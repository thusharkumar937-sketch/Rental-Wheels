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


# Test 1: Get all available vehicles
def test_get_vehicles_success():
    client = setup_test_app()

    vehicle_id = ObjectId()
    mock_db = MagicMock()
    mock_db.vehicles.find.return_value = [
        {
            "_id": vehicle_id,
            "make": "Toyota",
            "model": "Innova",
            "category_name": "SUV",
            "price_per_day": 2000,
            "status": "available"
        }
    ]

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get("/api/vehicles")

    assert response.status_code == 200

    data = response.get_json()
    assert data["count"] == 1
    assert data["vehicles"][0]["make"] == "Toyota"
    assert data["vehicles"][0]["id"] == str(vehicle_id)

    mock_db.vehicles.find.assert_called_once_with(
        {"status": "available"}
    )


# Test 2: Get vehicles with category filter
def test_get_vehicles_by_category():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.vehicles.find.return_value = [
        {
            "_id": ObjectId(),
            "make": "Honda",
            "model": "City",
            "category_name": "Sedan",
            "price_per_day": 1500
        }
    ]

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get("/api/vehicles?category=Sedan")

    assert response.status_code == 200

    query = mock_db.vehicles.find.call_args[0][0]
    assert query["category_name"] == "Sedan"
    assert query["status"] == "available"


# Test 3: Filter vehicles by minimum and maximum price
def test_get_vehicles_by_price_range():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.vehicles.find.return_value = []

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get(
            "/api/vehicles?min_price=1000&max_price=3000"
        )

    assert response.status_code == 200

    query = mock_db.vehicles.find.call_args[0][0]

    assert query["price_per_day"]["$gte"] == 1000
    assert query["price_per_day"]["$lte"] == 3000


# Test 4: Handle database error while fetching vehicles
def test_get_vehicles_database_error():
    client = setup_test_app()

    mock_db = MagicMock()
    mock_db.vehicles.find.side_effect = Exception("Database error")

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get("/api/vehicles")

    assert response.status_code == 500
    assert response.get_json()["message"] == "Failed to fetch vehicles"


# Test 5: Get vehicle by valid ID
def test_get_vehicle_by_id_success():
    client = setup_test_app()

    vehicle_id = ObjectId()

    mock_db = MagicMock()
    mock_db.vehicles.find_one.return_value = {
        "_id": vehicle_id,
        "make": "Hyundai",
        "model": "Creta",
        "price_per_day": 1800
    }

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get(f"/api/vehicles/{vehicle_id}")

    assert response.status_code == 200

    data = response.get_json()
    assert data["vehicle"]["id"] == str(vehicle_id)
    assert data["vehicle"]["make"] == "Hyundai"


# Test 6: Get vehicle using an invalid ID
def test_get_vehicle_invalid_id():
    client = setup_test_app()

    mock_db = MagicMock()

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get("/api/vehicles/invalid-id")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Invalid vehicle ID format"

    mock_db.vehicles.find_one.assert_not_called()


# Test 7: Return 404 when vehicle does not exist
def test_get_vehicle_not_found():
    client = setup_test_app()

    vehicle_id = ObjectId()

    mock_db = MagicMock()
    mock_db.vehicles.find_one.return_value = None

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get(f"/api/vehicles/{vehicle_id}")

    assert response.status_code == 404
    assert response.get_json()["message"] == "Vehicle not found"


# Test 8: Get branches successfully
def test_get_branches_success():
    client = setup_test_app()

    branch_id = ObjectId()
    created_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    mock_db = MagicMock()
    mock_db.branches.find.return_value = [
        {
            "_id": branch_id,
            "branch_name": "Central Outlet",
            "created_at": created_time
        }
    ]

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get("/api/branches")

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["branches"]) == 1
    assert data["branches"][0]["id"] == str(branch_id)
    assert data["branches"][0]["branch_name"] == "Central Outlet"
    assert isinstance(data["branches"][0]["created_at"], str)


# Test 9: Get vehicle categories successfully
def test_get_categories_success():
    client = setup_test_app()

    category_id = ObjectId()

    mock_db = MagicMock()
    mock_db.vehicle_categories.find.return_value = [
        {
            "_id": category_id,
            "category_name": "SUV"
        },
        {
            "_id": ObjectId(),
            "category_name": "Sedan"
        }
    ]

    with patch("app.routes.vehicles.get_db", return_value=mock_db):
        response = client.get("/api/categories")

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["categories"]) == 2
    assert data["categories"][0]["category_name"] == "SUV"
    assert data["categories"][0]["id"] == str(category_id)


# Test 10: Reject vehicle creation without an authentication token
def test_create_vehicle_missing_fields():
    client = setup_test_app()

    response = client.post(
        "/api/vehicles",
        json={
            "make": "Toyota",
            "model": "Innova"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Authentication token is missing"    
