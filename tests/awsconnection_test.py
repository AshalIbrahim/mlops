import mysql.connector
import pytest
from backend.app import get_connection


def test_database_connection_success():
    """
    Test that verifies the database connection can be established successfully.
    """

    try:
        conn = get_connection
        assert conn.is_connected(), "Database connection failed."
    except mysql.connector.Error as err:
        pytest.fail(f"Database connection failed: {err}")
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()
