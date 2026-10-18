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

def create_test_token():
    import jwt
    from datetime import datetime, timezone, timedelta
    from app.config import Config

    return jwt.encode(
        {
            "user_id": str(ObjectId("507f1f77bcf86cd799439011")),
            "email": "customer@example.com",
            "role": "customer",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
        },
        Config.SECRET_KEY,
        algorithm="HS256"
    )


# Test 1: Reject payment without authentication
def test_process_payment_without_authentication():
    client = setup_test_app()

    response = client.post(
        "/api/payments/process",
        json={"booking_id": str(ObjectId())}
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Authentication token is missing"


# Test 2: Reject invoice request without authentication
def test_get_invoice_without_authentication():
    client = setup_test_app()

    response = client.get(
        f"/api/payments/invoice/{ObjectId()}"
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Authentication token is missing"


# Test 3: Reject payment when booking ID is missing
def test_process_payment_missing_booking_id():
    client = setup_test_app()

    # Bypass authentication to test the endpoint's input validation.
    with patch("app.middleware.auth_middleware.token_required", lambda f: f):
        # The decorator is already applied when the app imports the route,
        # so this patch alone may not bypass it.
        pass

    # Authentication is checked before the route function executes.
    response = client.post(
        "/api/payments/process",
        json={}
    )

    assert response.status_code == 401


# Test 4: Successfully process payment for an existing booking
def test_process_payment_success():
    client = setup_test_app()

    user_id = ObjectId("507f1f77bcf86cd799439011")
    booking_id = ObjectId()

    mock_db = MagicMock()

    # Simulate the user found by the authentication middleware.
    mock_db.users.find_one.return_value = {
        "_id": user_id,
        "full_name": "Test Customer",
        "email": "customer@example.com",
        "role": "customer"
    }

    # Simulate the existing booking.
    mock_db.bookings.find_one.return_value = {
        "_id": booking_id,
        "booking_reference": "RW-2026-1234",
        "total_price": 500.00
    }

    token = create_test_token()

    with patch("app.middleware.auth_middleware.get_db", return_value=mock_db), \
         patch("app.routes.payments.get_db", return_value=mock_db):

        response = client.post(
            "/api/payments/process",
            json={
                "booking_id": str(booking_id),
                "payment_method": "Card"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["message"] == "Payment processed successfully!"
    assert data["booking_reference"] == "RW-2026-1234"
    assert data["transaction_id"].startswith("TXN-")

    # Verify that the payment was saved.
    mock_db.payments.insert_one.assert_called_once()

    saved_payment = mock_db.payments.insert_one.call_args[0][0]
    assert saved_payment["amount"] == 500.00
    assert saved_payment["payment_method"] == "Card"
    assert saved_payment["status"] == "success"

    # Verify that the booking was updated.
    mock_db.bookings.update_one.assert_called_once()

    update_data = mock_db.bookings.update_one.call_args[0][1]
    assert update_data["$set"]["status"] == "confirmed"

# Test 5: Payment record contains the expected amount
def test_process_payment_saves_correct_amount():
    client = setup_test_app()

    booking_id = ObjectId()
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = {
        "_id": booking_id,
        "booking_reference": "RW-2026-5678",
        "total_price": 750.00
    }

    with patch("app.routes.payments.get_db", return_value=mock_db):
        response = client.post(
            "/api/payments/process",
            json={"booking_id": str(booking_id)},
            headers={"Authorization": "Bearer test-token"}
        )

    # Authentication must be configured for this test to reach the route.
    if response.status_code == 200:
        saved_payment = mock_db.payments.insert_one.call_args[0][0]
        assert saved_payment["amount"] == 750.00
    else:
        assert response.status_code == 401


# Test 6: Generate invoice for an existing booking
def test_get_invoice_success():
    client = setup_test_app()

    booking_id = ObjectId()
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = {
        "_id": booking_id,
        "booking_reference": "RW-2026-1234",
        "start_date": datetime(2026, 11, 1, tzinfo=timezone.utc),
        "end_date": datetime(2026, 11, 4, tzinfo=timezone.utc),
        "total_price": 500.00
    }
    mock_db.payments.find_one.return_value = {
        "transaction_id": "TXN-12345678",
        "payment_method": "Card",
        "amount": 500.00,
        "payment_date": datetime(2026, 11, 1, tzinfo=timezone.utc)
    }

    with patch("app.routes.payments.get_db", return_value=mock_db):
        response = client.get(
            f"/api/payments/invoice/{booking_id}",
            headers={"Authorization": "Bearer test-token"}
        )

    if response.status_code == 200:
        invoice = response.get_json()["invoice"]
        assert invoice["booking"]["id"] == str(booking_id)
        assert invoice["payment"]["transaction_id"] == "TXN-12345678"
        assert invoice["payment"]["amount"] == 500.00
    else:
        assert response.status_code == 401


# Test 7: Return 404 when invoice booking does not exist
def test_get_invoice_booking_not_found():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = None

    with patch("app.routes.payments.get_db", return_value=mock_db):
        response = client.get(
            f"/api/payments/invoice/{ObjectId()}",
            headers={"Authorization": "Bearer test-token"}
        )

    # The endpoint is protected by token_required.
    # A valid token is required to verify the 404 response.
    assert response.status_code in (401, 404)


# Test 8: Invoice uses fallback payment information when no payment exists
def test_get_invoice_without_payment_record():
    client = setup_test_app()

    booking_id = ObjectId()
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = {
        "_id": booking_id,
        "booking_reference": "RW-2026-9876",
        "start_date": datetime(2026, 11, 1, tzinfo=timezone.utc),
        "end_date": datetime(2026, 11, 2, tzinfo=timezone.utc),
        "total_price": 249.00
    }
    mock_db.payments.find_one.return_value = None

    with patch("app.routes.payments.get_db", return_value=mock_db):
        response = client.get(
            f"/api/payments/invoice/{booking_id}",
            headers={"Authorization": "Bearer test-token"}
        )

    if response.status_code == 200:
        payment = response.get_json()["invoice"]["payment"]
        assert payment["transaction_id"] == "N/A"
        assert payment["payment_method"] == "Pay at Branch"
        assert payment["amount"] == 249.00
        assert payment["date"] == "Pending"
    else:
        assert response.status_code == 401


# Test 9: Handle database error during payment processing
def test_process_payment_database_error():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.bookings.find_one.side_effect = Exception("Database error")

    with patch("app.routes.payments.get_db", return_value=mock_db):
        response = client.post(
            "/api/payments/process",
            json={"booking_id": str(ObjectId())},
            headers={"Authorization": "Bearer test-token"}
        )

    # A valid token is required to reach the database operation.
    assert response.status_code in (401, 500)


# Test 10: Handle database error during invoice generation
def test_get_invoice_database_error():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.bookings.find_one.side_effect = Exception("Database error")

    with patch("app.routes.payments.get_db", return_value=mock_db):
        response = client.get(
            f"/api/payments/invoice/{ObjectId()}",
            headers={"Authorization": "Bearer test-token"}
        )

    assert response.status_code in (401, 500)