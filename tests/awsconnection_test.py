import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np


@pytest.fixture(scope="session")
def is_ci():
    """Detect if running in CI environment."""
    return os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"


@pytest.fixture(scope="session", autouse=True)
def mock_model_for_ci(is_ci):
    """Mock the model loading in CI to avoid S3 dependency."""
    if not is_ci:
        # Local environment - use real model
        yield
        return

    print("🔧 CI Environment detected - using mocked model")

    # Create a mock model
    mock_model = Mock()
    mock_model.predict = Mock(return_value=np.array([50000000.0]))  # 50M PKR

    mock_sale_features = [
        "covered_area",
        "beds",
        "baths",
        "location_Cantt, Karachi, Sindh",
        "location_DHA Defence, Karachi, Sindh",
        "prop_type_House",
        "prop_type_Flat",
    ]

    mock_metadata = {
        "locations": ["Cantt, Karachi, Sindh", "DHA Defence, Karachi, Sindh"],
        "prop_types": ["House", "Flat", "Upper Portion"],
    }

    with patch("backend.app.load_model") as mock_load:
        mock_load.return_value = (mock_model, mock_sale_features, mock_metadata)

        # Also patch the module-level variables
        with patch("backend.app.model", mock_model):
            with patch("backend.app.sale_feature_columns", mock_sale_features):
                with patch("backend.app.valid_metadata", mock_metadata):
                    with patch("backend.app.locations", mock_metadata["locations"]):
                        with patch(
                            "backend.app.propertyTypes", mock_metadata["prop_types"]
                        ):
                            yield


@pytest.fixture(scope="session", autouse=True)
def mock_db_for_ci(is_ci):
    """Mock database connection in CI."""
    if not is_ci:
        # Local environment - use real DB
        yield
        return

    print("🔧 CI Environment detected - using mocked database")

    # Mock database responses
    mock_listings = [
        {
            "prop_type": "House",
            "purpose": "sale",
            "covered_area": 1000.0,
            "price": 50000000.0,
            "location": "Cantt, Karachi, Sindh",
            "beds": 3,
            "baths": 2,
        },
        {
            "prop_type": "Flat",
            "purpose": "sale",
            "covered_area": 800.0,
            "price": 30000000.0,
            "location": "DHA Defence, Karachi, Sindh",
            "beds": 2,
            "baths": 2,
        },
    ]

    def mock_get_connection():
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Mock cursor methods
        mock_cursor.fetchall.return_value = mock_listings
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=False)

        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)

        return mock_conn

    with patch("backend.app.get_connection", side_effect=mock_get_connection):
        yield


@pytest.fixture(scope="session", autouse=True)
def setup_ci_environment(is_ci):
    """Set up necessary environment variables for CI."""
    if is_ci:
        print("🔧 Setting up CI environment variables")
        # Ensure all required env vars have defaults
        os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-key")
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")
        os.environ.setdefault("AWS_DEFAULT_REGION", "eu-north-1")
        os.environ.setdefault("S3_BUCKET", "zameen-project")
        os.environ.setdefault("S3_MODELS_PREFIX", "zameen_models")
        os.environ.setdefault("HOST", "localhost")
        os.environ.setdefault("USER", "test")
        os.environ.setdefault("PASSWORD", "test")
        os.environ.setdefault("DB_NAME", "test_db")
        os.environ.setdefault("PORT", "3306")
    yield
