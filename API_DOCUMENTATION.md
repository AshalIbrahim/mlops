# Zameen MLOps API Documentation

## Overview

The Zameen MLOps API provides endpoints for property price prediction and property data retrieval. The API is built using FastAPI and provides auto-generated interactive documentation.

## API Base URLs

- Local Development: `http://localhost:8000`
- Swagger UI (Interactive Docs): `http://localhost:8000/docs`
- ReDoc (Alternative Docs): `http://localhost:8000/redoc`

## Authentication

Currently, the API is open and does not require authentication.

## Endpoints

### 1. Health Check

```http
GET /
```

Checks if the API is running.

**Example Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
    "message": "Zameen API is running"
}
```

### 2. Property Price Prediction

```http
POST /predict
```

Predicts property price based on given features.

**Request Schema:**
```json
{
    "coveredArea": float,
    "beds": integer,
    "bathrooms": integer,
    "location": string,
    "propType": string,
    "purpose": string (optional, defaults to "sale")
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
         "coveredArea": 1200,
         "beds": 3,
         "bathrooms": 2,
         "location": "Gulberg",
         "propType": "House",
         "purpose": "sale"
     }'
```

**Success Response:**
```json
{
    "prediction": 12500000.0,
    "formatted_price": "PKR 12,500,000.00"
}
```

**Error Responses:**

Invalid Location:
```json
{
    "detail": "Invalid location. Must be one of: DHA, Gulberg, ..."
}
```

Invalid Property Type:
```json
{
    "detail": "Invalid property type. Must be one of: House, Apartment, ..."
}
```

Model Loading Error:
```json
{
    "detail": "Model not loaded. Check MLflow server and model registry."
}
```

### 3. Property Listings

```http
GET /listings
```

Retrieves a list of property listings.

**Parameters:**
- `limit` (optional, integer): Number of listings to return (default: 20)

**Example Request:**
```bash
curl "http://localhost:8000/listings?limit=5"
```

**Response:**
```json
[
    {
        "prop_type": "House",
        "purpose": "sale",
        "covered_area": 1200.0,
        "price": 15000000,
        "location": "Gulberg",
        "beds": 3,
        "baths": 2
    },
    // ... more listings
]
```

### 4. Available Locations

```http
GET /locations
```

Retrieves list of available property locations.

**Parameters:**
- `purpose` (optional, string): Filter by purpose (default: "sale")

**Example Request:**
```bash
curl http://localhost:8000/locations
```

**Response:**
```json
{
    "locations": ["DHA", "Gulberg", "Johar Town", "...]
}
```

### 5. Property Types

```http
GET /prop_type
```

Retrieves list of available property types.

**Parameters:**
- `purpose` (optional, string): Filter by purpose (default: "sale")

**Example Request:**
```bash
curl http://localhost:8000/prop_type
```

**Response:**
```json
{
    "prop_type": ["House", "Apartment", "Plot", ...]
}
```

### 6. Health Check

```http
GET /health
```

Checks API health status.

**Example Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
    "status": "ok"
}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Successful request
- 400: Bad request (invalid input)
- 404: Not found
- 500: Server error

Error responses include a detail message:
```json
{
    "detail": "Error message here"
}
```

## Rate Limiting

Currently, no rate limiting is implemented.

## Dependencies

The API requires:
- MLflow server running at `http://127.0.0.1:5000`
- MySQL database connection
- Trained model "ZameenPriceModelV2" in MLflow registry

## Testing the API

You can test the API using:
1. Interactive Swagger UI at `/docs`
2. cURL commands as shown in examples
3. Any HTTP client (Postman, HTTPie, etc.)

Example Python client:
```python
import requests

# Predict price
response = requests.post(
    "http://localhost:8000/predict",
    json={
        "coveredArea": 1200,
        "beds": 3,
        "bathrooms": 2,
        "location": "Gulberg",
        "propType": "House",
        "purpose": "sale"
    }
)
print(response.json())
```

## Local Development

1. Start the API server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

2. Visit `http://localhost:8000/docs` for interactive documentation

3. Make sure MLflow server is running:
```bash
mlflow server --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root file:./mlruns \
    --host 0.0.0.0 \
    --port 5000
```
