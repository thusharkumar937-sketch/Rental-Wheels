from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.database import get_db
from app.middleware.auth_middleware import token_required, role_required

vehicles_bp = Blueprint("vehicles", __name__)

@vehicles_bp.route("/api/vehicles", methods=["GET"])
def get_vehicles():
    try:
        db = get_db()
        category = request.args.get("category")
        branch_id = request.args.get("branch_id")
        fuel_type = request.args.get("fuel_type")
        transmission = request.args.get("transmission")
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)
        status = request.args.get("status", "available")

        query = {}
        if status and status != "all":
            query["status"] = status
        if category and category != "all":
            query["category_name"] = category
        if branch_id and branch_id != "all":
            query["branch_id"] = branch_id
        if fuel_type and fuel_type != "all":
            query["fuel_type"] = fuel_type
        if transmission and transmission != "all":
            query["transmission"] = transmission
        
        if min_price is not None or max_price is not None:
            query["price_per_day"] = {}
            if min_price is not None:
                query["price_per_day"]["$gte"] = min_price
            if max_price is not None:
                query["price_per_day"]["$lte"] = max_price

        vehicles = list(db.vehicles.find(query))
        for v in vehicles:
            v["id"] = str(v.pop("_id"))

        return jsonify({
            "count": len(vehicles),
            "vehicles": vehicles
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch vehicles", "error": str(e)}), 500


@vehicles_bp.route("/api/vehicles/<vehicle_id>", methods=["GET"])
def get_vehicle_by_id(vehicle_id):
    try:
        db = get_db()
        if not ObjectId.is_valid(vehicle_id):
            return jsonify({"message": "Invalid vehicle ID format"}), 400

        vehicle = db.vehicles.find_one({"_id": ObjectId(vehicle_id)})
        if not vehicle:
            return jsonify({"message": "Vehicle not found"}), 404

        vehicle["id"] = str(vehicle.pop("_id"))
        return jsonify({"vehicle": vehicle}), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving vehicle", "error": str(e)}), 500


@vehicles_bp.route("/api/branches", methods=["GET"])
def get_branches():
    try:
        db = get_db()
        branches = list(db.branches.find())
        for b in branches:
            b["id"] = str(b.pop("_id"))
            if "created_at" in b:
                b["created_at"] = b["created_at"].isoformat()
        return jsonify({"branches": branches}), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch branches", "error": str(e)}), 500


@vehicles_bp.route("/api/categories", methods=["GET"])
def get_categories():
    try:
        db = get_db()
        categories = list(db.vehicle_categories.find())
        for c in categories:
            c["id"] = str(c.pop("_id"))
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch categories", "error": str(e)}), 500


@vehicles_bp.route("/api/vehicles", methods=["POST"])
@token_required
@role_required(["admin", "staff"])
def create_vehicle():
    try:
        data = request.get_json() or {}
        make = data.get("make")
        model = data.get("model")
        category_name = data.get("category_name")
        price_per_day = data.get("price_per_day")
        branch_id = data.get("branch_id")

        if not make or not model or not category_name or not price_per_day:
            return jsonify({"message": "Make, model, category, and price per day are required"}), 400

        db = get_db()
        branch_name = "Central Outlet"
        if branch_id and ObjectId.is_valid(branch_id):
            b_doc = db.branches.find_one({"_id": ObjectId(branch_id)})
            if b_doc:
                branch_name = b_doc.get("branch_name", "Central Outlet")

        vehicle_doc = {
            "make": make,
            "model": model,
            "category_name": category_name,
            "branch_id": str(branch_id) if branch_id else "",
            "branch_name": branch_name,
            "year": int(data.get("year", 2024)),
            "license_plate": data.get("license_plate", "RW-NEW-000"),
            "color": data.get("color", "Black"),
            "seating_capacity": int(data.get("seating_capacity", 5)),
            "fuel_type": data.get("fuel_type", "Petrol"),
            "transmission": data.get("transmission", "Automatic"),
            "price_per_day": float(price_per_day),
            "mileage": data.get("mileage", "15 km/l"),
            "status": data.get("status", "available"),
            "image_url": data.get("image_url", "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&q=80"),
            "created_at": datetime.now(timezone.utc)
        }

        res = db.vehicles.insert_one(vehicle_doc)
        vehicle_doc["id"] = str(res.inserted_id)
        vehicle_doc.pop("_id", None)

        return jsonify({"message": "Vehicle added successfully", "vehicle": vehicle_doc}), 201
    except Exception as e:
        return jsonify({"message": "Failed to create vehicle", "error": str(e)}), 500
