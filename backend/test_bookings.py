import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from bson import ObjectId

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app


def setup_test_app():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


# Test 1: Check vehicle availability successfully
def test_check_availability_success():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = None

    with patch("app.routes.bookings.get_db", return_value=mock_db):
        response = client.post(
            "/api/bookings/check-availability",
            json={
                "vehicle_id": str(ObjectId()),
                "start_date": "2026-11-01",
                "end_date": "2026-11-04"
            }
        )

    assert response.status_code == 200
    data = response.get_json()
    assert data["available"] is True
    assert data["days"] == 3


# Test 2: Reject availability request with missing fields
def test_check_availability_missing_fields():
    client = setup_test_app()

    response = client.post(
        "/api/bookings/check-availability",
        json={"vehicle_id": str(ObjectId())}
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Vehicle ID, start date, and end date are required"
    )


# Test 3: Reject invalid date range
def test_check_availability_invalid_dates():
    client = setup_test_app()

    response = client.post(
        "/api/bookings/check-availability",
        json={
            "vehicle_id": str(ObjectId()),
            "start_date": "2026-11-05",
            "end_date": "2026-11-03"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "End date must be strictly after pickup date"
    )


# Test 4: Report that the vehicle is already reserved
def test_check_availability_vehicle_reserved():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = {
        "vehicle_id": str(ObjectId()),
        "status": "confirmed"
    }

    with patch("app.routes.bookings.get_db", return_value=mock_db):
        response = client.post(
            "/api/bookings/check-availability",
            json={
                "vehicle_id": str(ObjectId()),
                "start_date": "2026-11-01",
                "end_date": "2026-11-04"
            }
        )

    assert response.status_code == 200
    assert response.get_json()["available"] is False


# Test 5: Reject booking creation without authentication
def test_create_booking_without_authentication():
    client = setup_test_app()

    response = client.post(
        "/api/bookings/create",
        json={
            "vehicle_id": str(ObjectId()),
            "start_date": "2026-11-01",
            "end_date": "2026-11-04"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == (
        "Authentication token is missing"
    )


# Test 6: Reject booking creation with missing fields
def test_create_booking_missing_fields():
    client = setup_test_app()

    # The endpoint requires authentication, so without a token
    # the request should be rejected before field validation.
    response = client.post(
        "/api/bookings/create",
        json={}
    )

    assert response.status_code == 401


# Test 7: Reject an invalid booking date range
def test_create_booking_invalid_dates():
    client = setup_test_app()

    # Authentication is required before date validation.
    response = client.post(
        "/api/bookings/create",
        json={
            "vehicle_id": str(ObjectId()),
            "start_date": "2026-11-05",
            "end_date": "2026-11-03"
        }
    )

    assert response.status_code == 401


# Test 8: Reject booking detail request without authentication
def test_get_booking_detail_without_authentication():
    client = setup_test_app()

    response = client.get(
        f"/api/bookings/{ObjectId()}"
    )

    assert response.status_code == 401


# Test 9: Reject my-bookings request without authentication
def test_get_my_bookings_without_authentication():
    client = setup_test_app()

    response = client.get("/api/bookings/my-bookings")

    assert response.status_code == 401


# Test 10: Handle database failure during availability check
def test_check_availability_database_error():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.bookings.find_one.side_effect = Exception(
        "Simulated database failure"
    )

    with patch("app.routes.bookings.get_db", return_value=mock_db):
        response = client.post(
            "/api/bookings/check-availability",
            json={
                "vehicle_id": str(ObjectId()),
                "start_date": "2026-11-01",
                "end_date": "2026-11-04"
            }
        )

    assert response.status_code == 500
    assert response.get_json()["message"] == (
        "Failed to verify availability"
    )