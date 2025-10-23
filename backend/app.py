from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import pandas as pd
import numpy as np
import os
import mlflow.pyfunc
from typing import List


# ---- Setup ----
app = FastAPI(title="Zameen MLOps API")

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://127.0.0.1:5000")  # Your MLflow server

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load MLflow model
try:
    model_name = "ZameenPriceModel"
    model_version = "latest"
    model_uri = f"models:/{model_name}/{model_version}"
    model = mlflow.pyfunc.load_model(model_uri)
    
except Exception as e:
    
    model = None
    print(str(e))

# ---- MySQL Connection ----
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="zameen"
    )


# ---- Routes ----
@app.get("/")
def home():
    return {"message": "Zameen API is running"}

@app.get("/listings")
def get_listings(limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT prop_type, purpose , covered_area, price, location,beds,baths FROM property_data LIMIT {limit}")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/locations")
def get_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT location FROM property_data WHERE purpose LIKE '%sale%' ORDER BY location")
    locations = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"locations": locations}

from pydantic import BaseModel

class PredictionInput(BaseModel):
    coveredArea: float
    beds: int
    bathrooms: int
    location: str

@app.post("/predict")
async def predict_price(input_data: PredictionInput):
    if model is None:
        return {"error": "Model not loaded. Please ensure MLflow server is running and model is registered."}
    
    print(input_data)
    try:
        # First create DataFrame with numeric features
        base_df = pd.DataFrame([[
            input_data.coveredArea,
            input_data.beds,
            input_data.bathrooms,
        ]], columns=["covered_area", "beds", "baths"])
        
        # Create one-hot encoded location
        location_df = pd.DataFrame([[input_data.location]], columns=['location'])
        location_encoded = pd.get_dummies(location_df['location'], prefix='location')
        
        # Combine numeric features with encoded location
        input_df = pd.concat([base_df, location_encoded], axis=1)
        
        # Make prediction using MLflow model
        predicted_price = float(model.predict(input_df)[0])  # Convert numpy float to Python float
        print(f"Predicted Price: {predicted_price}")    
        return {
            "prediction": predicted_price,
            "formatted_price": f"PKR{predicted_price:,.2f}"
            
        }
        
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}