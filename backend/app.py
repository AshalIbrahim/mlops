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
from contextlib import asynccontextmanager

# ---- Load environment variables ----
load_dotenv()

# ---- Setup ----
model = None
sale_feature_columns = None
valid_metadata = None
locations = []
propertyTypes = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, sale_feature_columns, valid_metadata
    print("🚀 Starting up: loading model and DB metadata...")
    model, sale_feature_columns, valid_metadata = load_model()
    load_location_and_property_types()  # load once
    # (cleanup logic could go here later)


app = FastAPI(title="Zameen MLOps API", lifespan=lifespan)

# ---- CORS ----
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

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)

mlflow.set_tracking_uri("http://127.0.0.1:5000")
model_name = "ZameenPriceModelV2"


# ---- DB Connection ----
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT", 3306)),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


# ---- Load model ----
def load_model(model_name="ZameenPriceModelSale"):
    model = None
    sale_feature_columns = None
    valid_metadata = None
    try:
        os.makedirs("model_cache", exist_ok=True)

        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=S3_BUCKET, Prefix=f"{S3_MODELS_PREFIX}/{model_name}"
        ):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                rel_path = os.path.relpath(key, f"{S3_MODELS_PREFIX}/{model_name}")
                local_path = os.path.join("model_cache", model_name, rel_path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                s3.download_file(S3_BUCKET, key, local_path)

        s3.download_file(
            S3_BUCKET,
            f"{S3_MODELS_PREFIX}/feature_columns.json",
            "model_cache/feature_columns.json",
        )
        s3.download_file(
            S3_BUCKET,
            f"{S3_MODELS_PREFIX}/valid_metadata.json",
            "model_cache/valid_metadata.json",
        )

        model = mlflow.sklearn.load_model(f"model_cache/{model_name}")

        with open("model_cache/feature_columns.json", "r") as f:
            feat = json.load(f)
        with open("model_cache/valid_metadata.json", "r") as f:
            valid_metadata = json.load(f)

        sale_feature_columns = feat.get("sale", [])
        print("✅ Model and artifacts loaded from S3 successfully!")

    except Exception as e:
        print(f"❌ Model load failed: {e}")

    return model, sale_feature_columns, valid_metadata


# ---- Load Locations & Property Types ----
def load_location_and_property_types():
    """Load data once into memory"""
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
        print(
            f"✅ Loaded {len(locations)} locations and {len(propertyTypes)} property types."
        )
    except Exception as e:
        print(f"⚠️ Failed to load locations/property types: {e}")
        locations, propertyTypes = [], []


# ---- Routes ----
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
def get_locations():
    return {"locations": locations}


@app.get("/prop_type")
def get_prop_type():
    return {"prop_type": propertyTypes}


# ---- Prediction ----
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
        raise HTTPException(status_code=500, detail="Model not loaded.")

    if input_data.location not in locations:
        raise HTTPException(
            status_code=400, detail=f"Invalid location: {input_data.location}"
        )

    if input_data.propType not in propertyTypes:
        raise HTTPException(
            status_code=400, detail=f"Invalid property type: {input_data.propType}"
        )

    try:
        base_df = pd.DataFrame(
            [[input_data.coveredArea, input_data.beds, input_data.bathrooms]],
            columns=["covered_area", "beds", "baths"],
        )

        loc_df = pd.get_dummies(pd.Series([input_data.location]), prefix="location")
        prop_df = pd.get_dummies(pd.Series([input_data.propType]), prefix="prop_type")
        input_df = pd.concat([base_df, loc_df, prop_df], axis=1)

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
