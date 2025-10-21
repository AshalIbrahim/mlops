# mlops
mlops zameen.com chatbot repo

🏠 House Price Prediction API

Predict house prices in DHA Karachi using a trained machine learning model!
This project trains a regression model on real estate listings and exposes a REST API to predict prices from property details.

📦 Features

✅ Train a linear regression model on property data (dha.csv)
✅ Predict house price (in Crores) using an HTTP API
✅ Preprocessing includes cleaning, encoding, and feature extraction
✅ Flask-based API ready for Postman or frontend integration

⚙️ 1. Setup & Installation
🧰 Requirements

You’ll need Python 3.8+ and the following libraries:

pip install pandas scikit-learn flask


💡 If you plan to retrain the model, also make sure you have your dha.csv dataset in the same directory.

🧠 2. Train the Model
Step 1: Prepare Your Dataset

Make sure your dha.csv file has columns like:

prop_type, purpose, covered_area, price_text, location, beds, baths, amenities

Step 2: Run the Training Script

You already have a training script (model.py).
Simply run:

python train_model.py


This will:

Clean and preprocess data

Train a Linear Regression model

Save it as trained_model.pkl in the project directory

🧾 The .pkl file contains the trained model and label encoder for location.

🌐 3. Start the Flask API
Step 1: Install Flask (if not already)
pip install flask

Step 2: Run the API server

Make sure trained_model.pkl exists, then run:

python api.py


You’ll see output like:

 * Running on http://127.0.0.1:5000


🎯 That’s your API URL — keep it running while you test!

📡 4. Test Using Postman
Step 1: Create a POST request

URL:

http://127.0.0.1:5000/predict


Method: POST
Body → raw → JSON (application/json)

Step 2: Paste this example JSON
{
  "prop_type": "House",
  "purpose": "For Sale",
  "covered_area": "500 Sq. Yd.",
  "location": "DHA Defence, Karachi, Sindh",
  "beds": "5 Beds",
  "baths": "5 Baths",
  "amenities": "Built in year: 25\nParking Spaces: 5\nDouble Glazed Windows\nCentral Air Conditioning\nCentral Heating\nFlooring\nElectricity Backup\nWaste Disposal\nFloors: 2,Bedrooms: 5\nBathrooms: 5\nServant Quarters: 1\nDrawing Room\nDining Room\nKitchens: 2"
}

Step 3: Click Send

You’ll receive a response like:

{
  "predicted_price_crore": 13.28
}

🧩 5. Project Structure
├── dha.csv                 # Dataset
├── train_model.py          # Training script (you already wrote this logic)
├── trained_model.pkl       # Saved model and encoders
├── api.py                  # Flask API for prediction
└── README.md               # This guide

🚀 6. Future Upgrades

🔹 Add batch prediction support (multiple listings in one request)
🔹 Switch from Flask → FastAPI for faster async responses
🔹 Integrate with a web frontend or mobile app

💡 Notes

You don’t need to include the price_text column when making predictions — the model predicts it for you.

If you retrain the model with new data, remember to replace trained_model.pkl.

Use debug=False in production for security.
