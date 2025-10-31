import mysql.connector
import pytest


def test_database_connection_success():
    """
    Test that verifies the database connection can be established successfully.
    """

    try:
        conn = mysql.connector.connect(
            host="zameen-db.c5ye0uuk68w0.eu-north-1.rds.amazonaws.com",
            port=3306,
            user="admin",
            password="Brianlara1",  # your DB name
        )

        assert conn.is_connected(), "Database connection failed."
    except mysql.connector.Error as err:
        pytest.fail(f"Database connection failed: {err}")
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()
