import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd
from datetime import datetime

# ----------------------
# Load and preprocess data
# ----------------------
df = pd.read_csv('zameen_cleaned.csv')
sale_data = df[df["purpose"].str.strip().str.lower() == "for sale"]

locations = pd.get_dummies(sale_data['location'], prefix='location')
X = pd.concat([sale_data[["covered_area", "beds", "baths"]], locations], axis=1)
y = sale_data["price"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ----------------------
# Train model
# ----------------------


# ----------------------
# MLflow setup
# ----------------------
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("Zameen-Price-Prediction")


with mlflow.start_run() as run:
    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    # Log metrics & params
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_metric("MAE", mae)
    mlflow.log_metric("R2", r2)

    # Log and register model
    model_uri = mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="ZameenPriceModelTry",
        registered_model_name="ZameenPriceModel"  # <-- register at the same time
    )
    
    print(f"Run ID: {run.info.run_id}")
    print(f"Model URI: {model_uri}")
