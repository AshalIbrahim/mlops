import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd
import json

# ----------------------
# MLflow setup
# ----------------------
mlflow.set_tracking_uri("http://127.0.0.1:5000")  # Your MLflow tracking server
mlflow.set_experiment("Zameen-Price-Prediction")

# ----------------------
# Load and preprocess data
# ----------------------
df = pd.read_csv("zameen_cleaned.csv")

# Clean and split data
sale_data = df[df["purpose"].str.strip().str.lower() == "for sale"]
rent_data = df[df["purpose"].str.strip().str.lower() == "for rent"]

# Save valid locations and property types for validation
valid_metadata = {
    "sale": {
        "locations": sorted(sale_data["location"].unique().tolist()),
        "prop_types": sorted(sale_data["prop_type"].unique().tolist())
    },
    "rent": {
        "locations": sorted(rent_data["location"].unique().tolist()),
        "prop_types": sorted(rent_data["prop_type"].unique().tolist())
    }
}

with open("valid_metadata.json", "w") as f:
    json.dump(valid_metadata, f, indent=4)

print("✅ Saved valid_metadata.json with validation data")

# One-hot encode locations and property types for each dataset
locations_sale = pd.get_dummies(sale_data["location"], prefix="location")
prop_types_sale = pd.get_dummies(sale_data["prop_type"], prefix="prop_type")
Xsale = pd.concat([sale_data[["covered_area", "beds", "baths"]], locations_sale, prop_types_sale], axis=1)
y_sale = sale_data["price"]

locations_rent = pd.get_dummies(rent_data["location"], prefix="location")
prop_types_rent = pd.get_dummies(rent_data["prop_type"], prefix="prop_type")
Xrent = pd.concat([rent_data[["covered_area", "beds", "baths"]], locations_rent, prop_types_rent], axis=1)
y_rent = rent_data["price"]

# Split into train/test sets
X_train_sale, X_test_sale, y_train_sale, y_test_sale = train_test_split(Xsale, y_sale, test_size=0.3, random_state=42)
X_train_rent, X_test_rent, y_train_rent, y_test_rent = train_test_split(Xrent, y_rent, test_size=0.3, random_state=42)

# ----------------------
# Save feature schema
# ----------------------
feature_columns = {
    "sale": list(Xsale.columns),
    "rent": list(Xrent.columns)
}

with open("feature_columns.json", "w") as f:
    json.dump(feature_columns, f, indent=4)

print(f"✅ Saved feature_columns.json with {len(Xsale.columns)} sale and {len(Xrent.columns)} rent features.")

# ----------------------
# Train and log Sale model
# ----------------------
with mlflow.start_run(run_name="Sale_Model") as run:
    model_sale = LinearRegression()
    model_sale.fit(X_train_sale, y_train_sale)

    y_pred_sale = model_sale.predict(X_test_sale)
    mae_sale = mean_absolute_error(y_test_sale, y_pred_sale)
    r2_sale = r2_score(y_test_sale, y_pred_sale)

    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_param("dataset", "For Sale")
    mlflow.log_metric("MAE", mae_sale)
    mlflow.log_metric("R2", r2_sale)

    # Log feature schema and validation metadata as artifacts
    mlflow.log_artifact("feature_columns.json")
    mlflow.log_artifact("valid_metadata.json")

    # Register model in MLflow
    mlflow.sklearn.log_model(
        sk_model=model_sale,
        artifact_path="ZameenPriceModelSale",
        registered_model_name="ZameenPriceModelV2"
    )

    print(f"✅ Sale model logged. Run ID: {run.info.run_id}")
    print(f"   MAE: {mae_sale:.2f}, R²: {r2_sale:.4f}")

# ----------------------
# Train and log Rent model
# ----------------------
with mlflow.start_run(run_name="Rent_Model") as run:
    model_rent = LinearRegression()
    model_rent.fit(X_train_rent, y_train_rent)

    y_pred_rent = model_rent.predict(X_test_rent)
    mae_rent = mean_absolute_error(y_test_rent, y_pred_rent)
    r2_rent = r2_score(y_test_rent, y_pred_rent)

    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_param("dataset", "For Rent")
    mlflow.log_metric("MAE", mae_rent)
    mlflow.log_metric("R2", r2_rent)

    # Log feature schema and validation metadata as artifacts
    mlflow.log_artifact("feature_columns.json")
    mlflow.log_artifact("valid_metadata.json")

    # Register model in MLflow
    mlflow.sklearn.log_model(
        sk_model=model_rent,
        artifact_path="ZameenRentModel",
        registered_model_name="ZameenPriceModelRentModel"
    )

    print(f"✅ Rent model logged. Run ID: {run.info.run_id}")
    print(f"   MAE: {mae_rent:.2f}, R²: {r2_rent:.4f}")
