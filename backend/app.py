from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import pandas as pd
import mlflow
import mlflow.pyfunc
import json
import os
import boto3
from dotenv import load_dotenv
from pydantic import BaseModel

# ---- Load environment variables ----
load_dotenv()

# ---- Setup ----
app = FastAPI(title="Zameen MLOps API")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- AWS + MLflow Config ----
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-north-1")
S3_BUCKET = os.getenv("S3_BUCKET", "zameen-project")
S3_MODELS_PREFIX = os.getenv("S3_MODELS_PREFIX", "zameen_models")

# Initialize S3 client (will use env creds)
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)

# MLflow setup
mlflow.set_tracking_uri("http://127.0.0.1:5000")
model_name = "ZameenPriceModelV2"
stage = "Production"


# ---- DB Connection ----
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("host"),
        port=int(os.getenv("port", 3306)),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("db_name"),
    )


# ---- Load model ----
def load_model(model_name="ZameenPriceModelV2", stage="Production"):
    model = None
    sale_feature_columns = None
    valid_metadata = None

    try:
        client = mlflow.tracking.MlflowClient()

        # Try stage first, fallback to latest
        versions = client.get_latest_versions(
            model_name, stages=[stage]
        ) or client.get_latest_versions(model_name)
        if not versions:
            raise Exception("No registered versions found for model")

        chosen = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
        run_id = chosen.run_id

        try:
            model_uri = f"models:/{model_name}/{stage}"
            model = mlflow.pyfunc.load_model(model_uri)
            print(f"✅ Loaded model via URI: {model_uri}")
        except Exception as e_uri:
            print(f"⚠ Failed via URI: {e_uri}, trying source...")
            model = mlflow.pyfunc.load_model(chosen.source)
            print(f"✅ Loaded model from source path: {chosen.source}")

        # Download artifacts
        feature_path = client.download_artifacts(run_id, "feature_columns.json")
        metadata_path = client.download_artifacts(run_id, "valid_metadata.json")

        with open(feature_path, "r") as f:
            feat = json.load(f)
        with open(metadata_path, "r") as f:
            valid_metadata = json.load(f)

        sale_feature_columns = feat.get("sale", [])
        print(f"Loaded {len(sale_feature_columns)} features from run {run_id}")
    except Exception as e:
        print(f"❌ Model/artifact load failed: {e}")

    return model, sale_feature_columns, valid_metadata


model, sale_feature_columns, valid_metadata = load_model()

# ---- Load location/property types ----
locations = []
propertyTypes = []


def load_location_and_property_types():
    global locations, propertyTypes
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT prop_type, location FROM property_data")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        locations = sorted({r["location"] for r in rows if r.get("location")})
        propertyTypes = sorted({r["prop_type"] for r in rows if r.get("prop_type")})

        return {"locations": locations, "prop_type": propertyTypes}
    except Exception as e:
        print(f"⚠ Failed to load locations/property types from DB: {e}")
        return {"locations": [], "prop_type": []}


load_location_and_property_types()


# ---- Routes ----
@app.get("/")
def home():
    return {"message": "Zameen API is running 🚀"}


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
    purpose: str = "sale"


@app.post("/predict")
async def predict_price(input_data: PredictionInput):
    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Check MLflow server and registry.",
        )

    valid_data = load_location_and_property_types()

    if input_data.location not in valid_data["locations"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid location. Must be one of: {', '.join(valid_data['locations'])}",
        )

    if input_data.propType not in valid_data["prop_type"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid property type. Must be one of: {', '.join(valid_data['prop_type'])}",
        )

    try:
        base_df = pd.DataFrame(
            [[input_data.coveredArea, input_data.beds, input_data.bathrooms]],
            columns=["covered_area", "beds", "baths"],
        )

        loc_df = pd.get_dummies(pd.Series([input_data.location]), prefix="location")
        prop_df = pd.get_dummies(pd.Series([input_data.propType]), prefix="prop_type")
        input_df = pd.concat([base_df, loc_df, prop_df], axis=1)

        # Align columns
        if sale_feature_columns:
            for col in sale_feature_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            input_df = input_df[sale_feature_columns]
        else:
            input_df = input_df.fillna(0)

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
