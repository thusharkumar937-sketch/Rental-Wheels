import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the backend directory to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app


def test_health_check_success():
    """Test health endpoint when MongoDB is available."""

    mock_db = MagicMock()
    mock_db.name = "rental_wheels"
    mock_db.command.return_value = {"ok": 1.0}
    mock_db.list_collection_names.return_value = ["users", "vehicles"]

    app = create_app()
    app.config["TESTING"] = True

    with patch("app.routes.health.get_db", return_value=mock_db):
        client = app.test_client()
        response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "online"
    assert data["database"]["connected"] is True
    assert data["database"]["ping"] is True
    assert data["database"]["collections_count"] == 2


def test_health_check_database_failure():
    """Test health endpoint when MongoDB connection fails."""

    app = create_app()
    app.config["TESTING"] = True

    with patch(
        "app.routes.health.get_db",
        side_effect=Exception("Database unavailable")
    ):
        client = app.test_client()
        response = client.get("/api/health")

    assert response.status_code == 500

    data = response.get_json()

    assert data["status"] == "degraded"
    assert data["message"] == (
        "API server running but database connection issue"
    )
    assert data["error"] == "Database unavailable"