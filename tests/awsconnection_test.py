# tests/test_app_real_db_extended.py
from fastapi.testclient import TestClient
from backend.app import app, get_connection, load_location_and_property_types
import mysql.connector

client = TestClient(app)


# --- Test database connection directly ---
def test_db_connection():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
    finally:
        if conn:
            conn.close()


# --- Test basic endpoints ---
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Zameen API is running"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Test /listings with edge cases ---
def test_get_listings_real_db():
    # Normal limit
    response = client.get("/listings?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        for item in data:
            assert "prop_type" in item
            assert "price" in item
            assert "location" in item

    # Edge case: limit=0
    response = client.get("/listings?limit=0")
    assert response.status_code == 200
    assert response.json() == []


# --- Test /locations and /prop_type endpoints ---
def test_get_locations_real_db():
    response = client.get("/locations")
    assert response.status_code == 200
    data = response.json()
    assert "locations" in data
    assert isinstance(data["locations"], list)


def test_get_prop_type_real_db():
    response = client.get("/prop_type")
    assert response.status_code == 200
    data = response.json()
    assert "prop_type" in data
    assert isinstance(data["prop_type"], list)


# --- Test the helper function with real DB ---
def test_load_location_and_property_types_direct():
    result = load_location_and_property_types()
    assert isinstance(result, dict)
    assert "locations" in result
    assert "prop_type" in result
    assert isinstance(result["locations"], list)
    assert isinstance(result["prop_type"], list)


# --- Force DB exception to hit except blocks ---
def test_load_location_and_property_types_error(monkeypatch):
    # Force get_connection() to raise an exception
    def fake_connection():
        raise mysql.connector.Error("Forced DB error")

    monkeypatch.setattr("backend.app.get_connection", fake_connection)

    result = load_location_and_property_types()
    assert result["locations"] == []
    assert result["prop_type"] == []
