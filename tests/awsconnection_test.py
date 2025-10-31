from backend.app import get_connection
import warnings
import mysql.connector
import sys
import os
import pytest

# Ignore all warnings coming from mlflow
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
warnings.filterwarnings("ignore", category=Warning, module="mlflow")


def test_database_connection_success():
    """
    Test that verifies the database connection can be established successfully.
    """

    try:
        conn = get_connection()
        assert conn.is_connected(), "Database connection failed."
    except mysql.connector.Error as err:
        pytest.fail(f"Database connection failed: {err}")
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()


def test_getlistings_endpoint():
    """
    Test the /listings endpoint to ensure it returns data correctly.
    """
    from fastapi.testclient import TestClient
    from backend.app import app

    client = TestClient(app)

    response = client.get("/listings?limit=5")
    assert response.status_code == 200, "Failed to get listings."
    data = response.json()
    assert isinstance(data, list), "Response is not a list."
    assert len(data) <= 5, "Returned more listings than the limit."


def test_getlocations_endpoint():
    """
    Test the /locations endpoint to ensure it returns location data correctly.
    """
    from fastapi.testclient import TestClient
    from backend.app import app

    client = TestClient(app)

    response = client.get("/locations?purpose=sale")
    assert response.status_code == 200, "Failed to get locations."
    data = response.json()
    assert "locations" in data, "Response does not contain 'locations' key."
    assert isinstance(data["locations"], list), "'locations' is not a list."


def test_getproptype_endpoint():
    """
    Test the /prop_type endpoint to ensure it returns property type data correctly.
    """
    from fastapi.testclient import TestClient
    from backend.app import app

    client = TestClient(app)

    response = client.get("/prop_type?purpose=rent")
    assert response.status_code == 200, "Failed to get property types."
    data = response.json()
    assert "prop_types" in data, "Response does not contain 'prop_types' key."
    assert isinstance(data["prop_types"], list), "'prop_types' is not a list."
