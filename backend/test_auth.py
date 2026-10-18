import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend directory to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app


def setup_test_app():
    """Create Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_register_success():
    """Test registration with valid details."""

    mock_db = MagicMock()
    mock_db.users.find_one.return_value = None
    mock_db.users.insert_one.return_value.inserted_id = "user123"

    client = setup_test_app()

    with patch("app.routes.auth.get_db", return_value=mock_db):
        response = client.post(
            "/api/auth/register",
            json={
                "full_name": "Test User",
                "email": "test@example.com",
                "password": "Password123",
                "phone": "9876543210"
            }
        )

    assert response.status_code == 201

    data = response.get_json()
    assert data["message"] == "User registered successfully"
    assert data["user"]["email"] == "test@example.com"
    assert "token" in data

    # Verify that the password was stored as a hash
    inserted_user = mock_db.users.insert_one.call_args[0][0]
    assert inserted_user["password_hash"] != "Password123"


def test_register_missing_fields():
    """Test registration when required fields are missing."""

    client = setup_test_app()

    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Full name, email, and password are required"
    )


def test_register_duplicate_email():
    """Test registration using an existing email."""

    mock_db = MagicMock()
    mock_db.users.find_one.return_value = {
        "email": "test@example.com"
    }

    client = setup_test_app()

    with patch("app.routes.auth.get_db", return_value=mock_db):
        response = client.post(
            "/api/auth/register",
            json={
                "full_name": "Test User",
                "email": "test@example.com",
                "password": "Password123"
            }
        )

    assert response.status_code == 409
    assert "already exists" in response.get_json()["message"]


def test_login_missing_fields():
    """Test login without required credentials."""

    client = setup_test_app()

    response = client.post(
        "/api/auth/login",
        json={
            "email": "",
            "password": ""
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Email and password are required"
    )


def test_login_unknown_email():
    """Test login using an email that does not exist."""

    mock_db = MagicMock()
    mock_db.users.find_one.return_value = None

    client = setup_test_app()

    with patch("app.routes.auth.get_db", return_value=mock_db):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "Password123"
            }
        )

    assert response.status_code == 401
    assert response.get_json()["message"] == (
        "Invalid email or password"
    )


def test_verify_otp_success():
    """Test OTP verification with the accepted simulated OTP."""

    client = setup_test_app()

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "otp": "123456",
            "token": "test-token"
        }
    )

    assert response.status_code == 200

    data = response.get_json()
    assert data["verified"] is True
    assert data["message"] == (
        "OTP verified successfully. Login complete!"
    )


def test_verify_otp_missing():
    """Test OTP verification when OTP is missing."""

    client = setup_test_app()

    response = client.post(
        "/api/auth/verify-otp",
        json={
            "otp": "",
            "token": "test-token"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "OTP is required"