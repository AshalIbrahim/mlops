from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import pandas as pd
import mlflow
import mlflow.pyfunc
import json
from pydantic import BaseModel

# ---- Setup ----
app = FastAPI(title="Zameen MLOps API")

# Set MLflow tracking URI
mlflow.set_tracking_uri(
    "http://127.0.0.1:5000"
)  # Change to your MLflow tracking server

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Load model from MLflow ----
# Ensure MLflow tracking URI points to your server (change if needed)
mlflow.set_tracking_uri("http://127.0.0.1:5000")

model_name = "ZameenPriceModelV2"
model_version = "Production"

# Try loading from model registry (preferred). If that fails, try to locate
# the model artifacts from the registry entry and load directly from the
# artifact location (local mlruns or remote store).
model = None
try:
    model_uri = f"models:/{model_name}/{model_version}"
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"✅ Loaded MLflow model via URI: {model_uri}")
except Exception as e:
    print(f" Failed to load model via models:/ URI: {e}")
    try:
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(model_name)
        if not versions:
            raise Exception("No registered versions found")
        # Try each version's source path until one loads
        loaded = False
        for v in versions:
            try:
                src = v.source  # usually points to an artifact URI or mlruns path
                print(f"Trying to load model from source: {src}")
                # If source is an artifact:/ or runs:/ URI, mlflow can load it directly
                model = mlflow.pyfunc.load_model(src)
                print(f"Loaded model from source: {src}")
                loaded = True
                break
            except Exception as e2:
                print(f" - could not load from {v.version} source {v.source}: {e2}")
        if not loaded:
            model = None
            print("❌ Could not load any registered model sources.")
    except Exception as e3:
        model = None
        print(f"❌ Failed to load model from registry: {e3}")

# ---- Load feature schema and validation metadata from MLflow artifacts ----
sale_feature_columns = None
valid_metadata = None
locations = []
propertyTypes = []


def load_location_and_property_types():
    global locations
    global propertyTypes
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT prop_type, location FROM property_data")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Build sorted unique lists
        locations = sorted({r["location"] for r in rows if r.get("location")})
        propertyTypes = sorted({r["prop_type"] for r in rows if r.get("prop_type")})

        return {"locations": locations, "prop_type": propertyTypes}
    except Exception as e:
        print(f"⚠️ Failed to load locations/property types from DB: {e}")
        locations = []
        propertyTypes = []
        return {"locations": [], "prop_type": []}


load_location_and_property_types()
try:
    client = mlflow.tracking.MlflowClient()
    # Try to get production versions first; if none exist fall back to any latest version
    versions = client.get_latest_versions(model_name, stages=["Production"])
    if not versions:
        print(
            "⚠️ No Production-stage model found; falling back to latest registered version."
        )
        versions = client.get_latest_versions(model_name)
        if not versions:
            raise Exception("No registered versions found for model")

    # Choose the most recent version by numeric version ordering (highest number)
    try:
        chosen = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
    except Exception:
        chosen = versions[0]

    run_id = chosen.run_id

    # Download the feature_columns.json and valid_metadata.json artifacts
    feature_path = client.download_artifacts(run_id, "feature_columns.json")
    metadata_path = client.download_artifacts(run_id, "valid_metadata.json")

    with open(feature_path, "r") as f:
        feat = json.load(f)
    with open(metadata_path, "r") as f:
        valid_metadata = json.load(f)

    sale_feature_columns = feat.get("sale", [])
    print(
        f"✅ Loaded {len(sale_feature_columns)} sale feature columns from MLflow (run {run_id})."
    )
    print("✅ Loaded validation metadata from MLflow.")
except Exception as e:
    print(f"⚠️ Failed to load feature schema from MLflow: {e}")
    sale_feature_columns = None


# ---- Database connection ----
def get_connection():
    return mysql.connector.connect(
        host="zameen-db.c5ye0uuk68w0.eu-north-1.rds.amazonaws.com",
        port=3306,
        user="admin",
        password="Brianlara1",
    )


# ---- API Routes ----
@app.get("/")
def home():
    return {"message": "Zameen API is running"}


@app.get("/listings")
def get_listings(limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT prop_type, purpose, covered_area, price, location, beds, baths
        FROM property_data
        LIMIT %s
    """,
        (limit,),
    )
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data


@app.get("/locations")
def get_locations(purpose: str = "sale"):
    data = load_location_and_property_types()
    return {"locations": data["locations"]}


@app.get("/prop_type")
def get_prop_type(purpose: str = "sale"):
    data = load_location_and_property_types()
    return {"prop_type": data["prop_type"]}


# ---- Prediction Schema ----
class PredictionInput(BaseModel):
    coveredArea: float
    beds: int
    bathrooms: int
    location: str
    propType: str
    purpose: str = "sale"  # default to sale


@app.post("/predict")
async def predict_price(input_data: PredictionInput):
    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Check MLflow server and model registry.",
        )

    # Get current valid locations and property types from database
    valid_data = load_location_and_property_types()

    # Validate location
    if input_data.location not in valid_data["locations"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid location. Must be one of: {', '.join(valid_data['locations'])}",
        )

    # Validate property type
    if input_data.propType not in valid_data["prop_type"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid property type. Must be one of: {', '.join(valid_data['prop_type'])}",
        )
    try:
        # Numeric features
        base_df = pd.DataFrame(
            [[input_data.coveredArea, input_data.beds, input_data.bathrooms]],
            columns=["covered_area", "beds", "baths"],
        )

        # One-hot encode location
        loc_df = pd.get_dummies(pd.Series([input_data.location]), prefix="location")
        # One-hot encode property type (prop_type)
        prop_df = pd.get_dummies(pd.Series([input_data.propType]), prefix="prop_type")
        input_df = pd.concat([base_df, loc_df, prop_df], axis=1)

        # Align columns with training features
        if sale_feature_columns:
            for col in sale_feature_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            input_df = input_df[sale_feature_columns]
        else:
            input_df = input_df.fillna(0)

        # Predict
        predicted_price = float(model.predict(input_df)[0])
        return {
            "prediction": predicted_price,
            "formatted_price": f"PKR {predicted_price:,.2f}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/health")
def health_check():
    return {"status": "ok"}
