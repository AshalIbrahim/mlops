import pandas as pd
import re
import numpy as np
import mysql.connector
import time

# ---------- STEP 1: Load CSV ----------
df = pd.read_csv("mlops/dha.csv")

# ---------- STEP 2: Normalize Column Names ----------
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(' ', '_')
    .str.replace('\ufeff', '', regex=True)  # remove BOM if present
)

print("🧾 Columns found:", list(df.columns))

# ---------- STEP 3: Auto-fix Column Names ----------
rename_map = {}
for c in df.columns:
    if "price" in c and "text" in c:
        rename_map[c] = "price_text"
    if "prop" in c and "type" in c:
        rename_map[c] = "prop_type"
    if "covered" in c and "area" in c:
        rename_map[c] = "covered_area"
df.rename(columns=rename_map, inplace=True)

# Ensure all required columns exist
required_cols = ["prop_type", "purpose", "covered_area", "price_text", "location", "beds", "baths", "amenities"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"❌ Missing required columns in CSV: {missing}")

# ---------- STEP 4: Clean Price ----------
def clean_price(price):
    if isinstance(price, str):
        price = price.strip()
        match = re.search(r"([\d\.]+)\s*(Crore|Lakh)", price)
        if match:
            value, unit = float(match.group(1)), match.group(2)
            if unit == "Crore":
                return value * 10_000_000
            elif unit == "Lakh":
                return value * 100_000
        nums = re.findall(r"[\d\.]+", price)
        return float(nums[0]) if nums else np.nan
    return np.nan

df["price"] = df["price_text"].apply(clean_price)

# ---------- STEP 5: Clean Covered Area ----------
df["covered_area"] = df["covered_area"].astype(str).str.extract(r"([\d\.]+)").astype(float)

# ---------- STEP 6: Clean Beds & Baths ----------
df["beds"] = df["beds"].astype(str).str.extract(r"(\d+)").astype(float)
df["baths"] = df["baths"].astype(str).str.extract(r"(\d+)").astype(float)

# ---------- STEP 7: Impute Missing Values ----------
df["beds"].fillna(df["beds"].median(), inplace=True)
df["baths"].fillna(df["baths"].median(), inplace=True)

# ---------- STEP 8: Clean Text Fields ----------
for col in ["prop_type", "purpose", "location", "amenities"]:
    df[col] = df[col].astype(str).str.strip().replace({"nan": None})

# ---------- STEP 9: Save Cleaned CSV ----------
df.to_csv("zameen_cleaned.csv", index=False)
print("✅ Cleaned data saved to zameen_cleaned.csv")

# ---------- STEP 10: Connect to MySQL ----------
def connect_mysql(retries=3, delay=2):
    for i in range(retries):
        try:
            connection = mysql.connector.connect(
                host="localhost",      # change if needed
                user="root",           # your MySQL username
                password="1234",  # your MySQL password
                database="zameen"      # your database name
            )
            if connection.is_connected():
                print("✅ Connected to MySQL successfully.")
                return connection
        except mysql.connector.Error as e:
            print(f"⚠️ MySQL connection failed ({e}), retrying in {delay}s...")
            time.sleep(delay)
    raise ConnectionError("❌ Could not connect to MySQL after retries.")

connection = connect_mysql()
cursor = connection.cursor()


# ---------- STEP 12: Insert Data ----------
insert_query = """
    INSERT INTO property_data
    (prop_type, purpose, covered_area, price, location, beds, baths, amenities)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

data_tuples = [
    (
        row.prop_type, row.purpose, row.covered_area, row.price,
        row.location, int(row.beds), int(row.baths), row.amenities
    )
    for _, row in df.iterrows()
]

cursor.executemany(insert_query, data_tuples)
connection.commit()

print(f"✅ Successfully inserted {cursor.rowcount} rows into MySQL.")

# ---------- STEP 13: Close Connection ----------
cursor.close()
connection.close()
print("🔒 MySQL connection closed.")
