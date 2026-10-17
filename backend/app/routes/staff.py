from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.database import get_db
from app.middleware.auth_middleware import token_required, role_required

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/api/staff/handover", methods=["POST"])
@token_required
@role_required(["staff", "admin"])
def process_handover():
    try:
        data = request.get_json() or {}
        booking_id = data.get("booking_id")
        start_odometer = int(data.get("start_odometer", 15000))
        start_fuel = data.get("start_fuel", "100%")
        notes = data.get("notes", "Vehicle in good condition at handover")

        if not booking_id:
            return jsonify({"message": "Booking ID is required"}), 400

        db = get_db()
        if not ObjectId.is_valid(booking_id):
            return jsonify({"message": "Invalid booking ID"}), 400

        booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            return jsonify({"message": "Booking not found"}), 404

        # Record Handover
        handover_doc = {
            "booking_id": booking_id,
            "booking_reference": booking.get("booking_reference"),
            "staff_id": request.current_user["id"],
            "staff_name": request.current_user.get("full_name"),
            "handover_time": datetime.now(timezone.utc),
            "start_odometer": start_odometer,
            "start_fuel": start_fuel,
            "handover_notes": notes
        }
        db.handover_records.insert_one(handover_doc)

        # Update Booking status to 'active'
        db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"status": "active", "updated_at": datetime.now(timezone.utc)}}
        )

        # Update Vehicle status to 'rented'
        if "vehicle_id" in booking and ObjectId.is_valid(booking["vehicle_id"]):
            db.vehicles.update_one(
                {"_id": ObjectId(booking["vehicle_id"])},
                {"$set": {"status": "rented"}}
            )

        return jsonify({"message": "Vehicle handover completed successfully! Key issued to customer."}), 200
    except Exception as e:
        return jsonify({"message": "Handover processing failed", "error": str(e)}), 500


@staff_bp.route("/api/staff/return", methods=["POST"])
@token_required
@role_required(["staff", "admin"])
def process_return():
    try:
        data = request.get_json() or {}
        booking_id = data.get("booking_id")
        return_odometer = int(data.get("return_odometer", 15500))
        return_fuel = data.get("return_fuel", "100%")
        extra_charges = float(data.get("extra_charges", 0.0))
        inspection_result = data.get("inspection_result", "passed")
        notes = data.get("notes", "Return inspection completed")

        if not booking_id:
            return jsonify({"message": "Booking ID is required"}), 400

        db = get_db()
        if not ObjectId.is_valid(booking_id):
            return jsonify({"message": "Invalid booking ID"}), 400

        booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            return jsonify({"message": "Booking not found"}), 404

        # Record Return Inspection
        return_doc = {
            "booking_id": booking_id,
            "booking_reference": booking.get("booking_reference"),
            "staff_id": request.current_user["id"],
            "staff_name": request.current_user.get("full_name"),
            "return_time": datetime.now(timezone.utc),
            "return_odometer": return_odometer,
            "return_fuel": return_fuel,
            "extra_charges": extra_charges,
            "inspection_result": inspection_result,
            "notes": notes
        }
        db.return_records.insert_one(return_doc)

        # Update Booking status to 'completed'
        db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc)}}
        )

        # Update Vehicle status to 'available' or 'servicing'
        new_v_status = "available" if inspection_result == "passed" else "servicing"
        if "vehicle_id" in booking and ObjectId.is_valid(booking["vehicle_id"]):
            db.vehicles.update_one(
                {"_id": ObjectId(booking["vehicle_id"])},
                {"$set": {"status": new_v_status}}
            )

        return jsonify({
            "message": f"Return inspection completed. Vehicle status set to '{new_v_status}'.",
            "extra_charges": extra_charges
        }), 200
    except Exception as e:
        return jsonify({"message": "Return inspection failed", "error": str(e)}), 500


@staff_bp.route("/api/staff/maintenance", methods=["POST"])
@token_required
@role_required(["staff", "admin"])
def log_maintenance():
    try:
        data = request.get_json() or {}
        vehicle_id = data.get("vehicle_id")
        service_type = data.get("service_type", "Regular Servicing & Inspection")
        cost = float(data.get("cost", 100.0))
        notes = data.get("notes", "Routine maintenance")

        if not vehicle_id:
            return jsonify({"message": "Vehicle ID is required"}), 400

        db = get_db()
        if not ObjectId.is_valid(vehicle_id):
            return jsonify({"message": "Invalid vehicle ID"}), 400

        vehicle = db.vehicles.find_one({"_id": ObjectId(vehicle_id)})
        if not vehicle:
            return jsonify({"message": "Vehicle not found"}), 404

        # Log maintenance record
        maint_doc = {
            "vehicle_id": vehicle_id,
            "vehicle_name": f"{vehicle.get('make')} {vehicle.get('model')}",
            "staff_id": request.current_user["id"],
            "service_type": service_type,
            "cost": cost,
            "notes": notes,
            "servicing_date": datetime.now(timezone.utc),
            "status": "in_progress"
        }
        db.maintenance_logs.insert_one(maint_doc)

        # Update Vehicle status to 'servicing'
        db.vehicles.update_one(
            {"_id": ObjectId(vehicle_id)},
            {"$set": {"status": "servicing"}}
        )

        return jsonify({
            "message": f"Maintenance logged for {vehicle.get('make')} {vehicle.get('model')}. Marked as servicing."
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to log maintenance", "error": str(e)}), 500
