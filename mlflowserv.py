import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd
import json
import os
import boto3
from dotenv import load_dotenv
load_dotenv()
print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))
print("AWS_SECRET_ACCESS_KEY:", os.getenv("AWS_SECRET_ACCESS_KEY"))
session = boto3.Session()
credentials = session.get_credentials()
print(credentials.get_frozen_credentials())


# ----------------------
# S3 Setup
# ----------------------
S3_BUCKET = "zameen-project"
S3_MODELS_PREFIX = "zameen_models"
s3 = boto3.client("s3")  # credentials from environment or IAM role

def upload_to_s3(local_path, s3_bucket, s3_key):
    """Upload a file or directory to S3"""
    if os.path.isdir(local_path):
        for root, dirs, files in os.walk(local_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, local_path)
                s3_path = os.path.join(s3_key, relative_path)
                s3.upload_file(full_path, s3_bucket, s3_path)
    else:
        s3.upload_file(local_path, s3_bucket, s3_key)
    print(f"✅ Uploaded {local_path} to s3://{s3_bucket}/{s3_key}")

# ----------------------
# Load and preprocess data
# ----------------------
df = pd.read_csv("zameen_cleaned.csv")

# Filter only "for sale" data
sale_data = df[df["purpose"].str.strip().str.lower() == "for sale"]

# Save valid metadata
valid_metadata = {
    "sale": {
        "locations": sorted(sale_data["location"].dropna().unique().tolist()),
        "prop_types": sorted(sale_data["prop_type"].dropna().unique().tolist()),
    }
}

with open("valid_metadata.json", "w") as f:
    json.dump(valid_metadata, f, indent=4)

# One-hot encode locations and property types
locations_sale = pd.get_dummies(sale_data["location"], prefix="location")
prop_types_sale = pd.get_dummies(sale_data["prop_type"], prefix="prop_type")
X_sale = pd.concat([sale_data[["covered_area", "beds", "baths"]], locations_sale, prop_types_sale], axis=1)
y_sale = sale_data["price"]

# Train/test split
X_train_sale, X_test_sale, y_train_sale, y_test_sale = train_test_split(X_sale, y_sale, test_size=0.3, random_state=42)

# Save feature columns
feature_columns = {"sale": list(X_sale.columns)}
with open("feature_columns.json", "w") as f:
    json.dump(feature_columns, f, indent=4)

# ----------------------
# Train Sale Model
# ----------------------
model_sale = LinearRegression()
model_sale.fit(X_train_sale, y_train_sale)
y_pred_sale = model_sale.predict(X_test_sale)

mae_sale = mean_absolute_error(y_test_sale, y_pred_sale)
r2_sale = r2_score(y_test_sale, y_pred_sale)

# Save model locally
mlflow.sklearn.save_model(model_sale, "ZameenPriceModelSale")

# Upload model and artifacts to S3
upload_to_s3("ZameenPriceModelSale", S3_BUCKET, f"{S3_MODELS_PREFIX}/ZameenPriceModelSale")
upload_to_s3("feature_columns.json", S3_BUCKET, f"{S3_MODELS_PREFIX}/feature_columns.json")
upload_to_s3("valid_metadata.json", S3_BUCKET, f"{S3_MODELS_PREFIX}/valid_metadata.json")

print(f"✅ Sale model trained and uploaded. MAE: {mae_sale:.2f}, R²: {r2_sale:.4f}")