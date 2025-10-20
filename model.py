#%%
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import pickle

# === Load CSV ===
data = pd.read_csv("dha.csv")

#%%
# === Clean Price Column (remove "Crore" etc.) ===
data["Price"] = data["price_text"].str.replace("[^0-9.]", "", regex=True)
data["Price"] = pd.to_numeric(data["Price"], errors="coerce")
print("💰 Price cleaned (crore values converted to numbers only)")

# === Clean Covered Area (remove commas, keep numeric part only) ===
def clean_area(area_str):
    text = str(area_str).replace(",", "").strip()  # remove commas
    match = re.match(r"(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else 0.0

data["CoveredArea"] = data["covered_area"].apply(clean_area)
print("📏 Covered area cleaned (commas removed, numeric extracted)")


# === Property Type Encoding ===
data["PropertyType"] = data["prop_type"].apply(lambda x: 1 if str(x).strip().lower() == "house" else 0)

# === Extract Beds/Baths from text ===
def extract_num(value):
    match = re.search(r"(\d+)", str(value))
    return int(match.group(1)) if match else None

data["Beds"] = data["beds"].apply(extract_num)
data["Baths"] = data["baths"].apply(extract_num)

# === Fill missing Beds/Baths from Amenities ===
def extract_from_amenities(amenities, key):
    match = re.search(rf"{key}:\s*(\d+)", str(amenities))
    return int(match.group(1)) if match else None

for i, row in data.iterrows():
    if pd.isna(row["Beds"]):
        val = extract_from_amenities(row["amenities"], "Bedrooms")
        if val: data.at[i, "Beds"] = val
    if pd.isna(row["Baths"]):
        val = extract_from_amenities(row["amenities"], "Bathrooms")
        if val: data.at[i, "Baths"] = val

# === Extract additional info from amenities ===
def extract_feature(amenities, key):
    match = re.search(rf"{key}:\s*(\d+)", str(amenities))
    return int(match.group(1)) if match else 0

data["Floors"] = data["amenities"].apply(lambda x: extract_feature(x, "Floors"))
data["Kitchens"] = data["amenities"].apply(lambda x: extract_feature(x, "Kitchens"))
data["ServantQuarters"] = data["amenities"].apply(lambda x: extract_feature(x, "Servant Quarters"))

print("🧩 Extracted Floors, Kitchens, Servant Quarters from amenities")
print(data.head())

#%%
# === Encode Location Numerically ===
le_location = LabelEncoder()
data["LocationEncoded"] = le_location.fit_transform(data["location"].astype(str))
print(f"📍 {len(le_location.classes_)} unique locations encoded")

# === Drop unnecessary columns ===
data = data.drop(columns=["price_text", "covered_area", "prop_type", "purpose", "location", "amenities","beds","baths"])

# === Handle Missing Values ===
data.fillna(0, inplace=True)

print("✅ Missing values handled")
print(data.head())


#%%

# === Split ===
X = data.drop(columns=["Price"])
y = data["Price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📊 Train: {len(X_train)}, Test: {len(X_test)}")

# === Train Model ===
model = LinearRegression()
model.fit(X_train, y_train)
print("🚀 Model training complete")

# === Evaluate ===
y_pred = model.predict(X_test)
print(f"📈 MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"🎯 R²: {r2_score(y_test, y_pred):.2f}")

# === Save Model & LabelEncoder ===
with open("trained_model.pkl", "wb") as f:
    pickle.dump((model, le_location), f)
print("💾 Model and encoders saved to trained_model.pkl")
