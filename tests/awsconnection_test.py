import pytest
from fastapi.testclient import TestClient
from backend.app import app, load_model, model as m

client = TestClient(app)


# ---- Home & Health ----
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Zameen API is running"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---- Listings ----
def test_get_listings():
    response = client.get("/listings?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5
    if data:
        for item in data:
            assert "prop_type" in item
            assert "location" in item
            assert "price" in item


def test_get_locations():
    response = client.get("/locations")
    assert response.status_code == 200
    data = response.json()
    assert "locations" in data
    assert isinstance(data["locations"], list)


def test_get_prop_type():
    response = client.get("/prop_type")
    assert response.status_code == 200
    data = response.json()
    assert "prop_type" in data
    assert isinstance(data["prop_type"], list)


# ---- Prediction Tests ----


@pytest.fixture(scope="session")
def model_resources():
    """Load model once per session to avoid repeated S3 calls."""
    m, sale_feature_columns, valid_metadata = load_model()
    return m, sale_feature_columns, valid_metadata


skip_if_no_model = pytest.mark.skipif(m is None, reason="MLflow model not loaded")


@skip_if_no_model
def test_predict_price_valid():
    response = client.post(
        "/predict",
        json={
            "coveredArea": 1000,
            "beds": 3,
            "bathrooms": 2,
            "location": "Cantt, Karachi, Sindh",
            "propType": "House",
            "purpose": "sale",
        },
    )
    assert response.status_code == 200
    json_resp = response.json()
    assert "prediction" in json_resp
    assert "formatted_price" in json_resp


@skip_if_no_model
def test_predict_invalid_location():
    response = client.post(
        "/predict",
        json={
            "coveredArea": 1000,
            "beds": 3,
            "bathrooms": 2,
            "location": "InvalidLocation",
            "propType": "House",
            "purpose": "sale",
        },
    )
    assert response.status_code == 400
    assert "Invalid location" in response.json()["detail"]


@skip_if_no_model
def test_predict_invalid_prop_type():
    response = client.post(
        "/predict",
        json={
            "coveredArea": 1000,
            "beds": 3,
            "bathrooms": 2,
            "location": "Cantt, Karachi, Sindh",
            "propType": "InvalidType",
            "purpose": "sale",
        },
    )
    assert response.status_code == 400
    assert "Invalid property type" in response.json()["detail"]
