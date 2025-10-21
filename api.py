from flask import Flask, request, jsonify
import pandas as pd
import re
import pickle

# === Load model and encoders ===
with open("trained_model.pkl", "rb") as f:
    model, le_location = pickle.load(f)

app = Flask(__name__)

# === Helper functions (same logic as training) ===
def clean_price(text):
    if not text:
        return 0.0
    match = re.search(r"(\d+(\.\d+)?)", str(text))
    return float(match.group(1)) if match else 0.0

def clean_area(area_str):
    text = str(area_str).replace(",", "").strip()
    match = re.match(r"(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else 0.0

def extract_num(value):
    match = re.search(r"(\d+)", str(value))
    return int(match.group(1)) if match else None

def extract_feature(amenities, key):
    match = re.search(rf"{key}:\s*(\d+)", str(amenities))
    return int(match.group(1)) if match else 0

def extract_from_amenities(amenities, key):
    match = re.search(rf"{key}:\s*(\d+)", str(amenities))
    return int(match.group(1)) if match else None

# === Prediction endpoint ===
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Convert to DataFrame for easier handling
        df = pd.DataFrame([data])

        # Clean and transform features just like training
        df["Price"] = df["price_text"].apply(clean_price)
        df["CoveredArea"] = df["covered_area"].apply(clean_area)
        df["PropertyType"] = df["prop_type"].apply(lambda x: 1 if str(x).strip().lower() == "house" else 0)
        df["Beds"] = df["beds"].apply(extract_num)
        df["Baths"] = df["baths"].apply(extract_num)

        # Fill missing Beds/Baths from amenities
        for i, row in df.iterrows():
            if pd.isna(row["Beds"]):
                val = extract_from_amenities(row["amenities"], "Bedrooms")
                if val: df.at[i, "Beds"] = val
            if pd.isna(row["Baths"]):
                val = extract_from_amenities(row["amenities"], "Bathrooms")
                if val: df.at[i, "Baths"] = val

        # Extract more features
        df["Floors"] = df["amenities"].apply(lambda x: extract_feature(x, "Floors"))
        df["Kitchens"] = df["amenities"].apply(lambda x: extract_feature(x, "Kitchens"))
        df["ServantQuarters"] = df["amenities"].apply(lambda x: extract_feature(x, "Servant Quarters"))

        # Encode location using the fitted label encoder
        df["LocationEncoded"] = le_location.transform(df["location"].astype(str))

        # Drop unnecessary columns
        df = df.drop(columns=["price_text", "covered_area", "prop_type", "purpose", "location", "amenities", "beds", "baths"])

        # Handle missing values
        df.fillna(0, inplace=True)

        # Predict price
        prediction = model.predict(df.drop(columns=["Price"]))[0]

        return jsonify({
            "predicted_price_crore": round(prediction, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True,port=5000)
