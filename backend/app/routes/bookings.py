from datetime import datetime, timezone
import random
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.database import get_db
from app.middleware.auth_middleware import token_required, role_required

bookings_bp = Blueprint("bookings", __name__)

def parse_date(date_str):
    try:
        # Accepts 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM'
        if "T" in date_str:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None

@bookings_bp.route("/api/bookings/check-availability", methods=["POST"])
def check_availability():
    try:
        data = request.get_json() or {}
        vehicle_id = data.get("vehicle_id")
        start_str = data.get("start_date")
        end_str = data.get("end_date")

        if not vehicle_id or not start_str or not end_str:
            return jsonify({"message": "Vehicle ID, start date, and end date are required"}), 400

        start_dt = parse_date(start_str)
        end_dt = parse_date(end_str)

        if not start_dt or not end_dt or end_dt <= start_dt:
            return jsonify({"message": "End date must be strictly after pickup date"}), 400

        db = get_db()
        # Query overlapping confirmed / active bookings
        overlapping = db.bookings.find_one({
            "vehicle_id": vehicle_id,
            "status": {"$in": ["confirmed", "active", "pending_payment"]},
            "$or": [
                {"start_date": {"$lt": end_dt}, "end_date": {"$gt": start_dt}}
            ]
        })

        if overlapping:
            return jsonify({
                "available": False,
                "message": "Vehicle is reserved for the selected date range. Please choose another date or vehicle."
            }), 200

        days = max(1, (end_dt - start_dt).days)
        return jsonify({
            "available": True,
            "days": days,
            "message": "Vehicle is available for your selected dates!"
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to verify availability", "error": str(e)}), 500


@bookings_bp.route("/api/bookings/create", methods=["POST"])
@token_required
def create_booking():
    try:
        data = request.get_json() or {}
        vehicle_id = data.get("vehicle_id")
        pickup_branch_id = data.get("pickup_branch_id")
        return_branch_id = data.get("return_branch_id")
        start_str = data.get("start_date")
        end_str = data.get("end_date")
        insurance_selected = data.get("insurance", False)
        gps_selected = data.get("gps", False)
        child_seat_selected = data.get("child_seat", False)
        promo_code = data.get("promo_code", "").strip().upper()

        if not vehicle_id or not start_str or not end_str:
            return jsonify({"message": "Vehicle, pickup date, and return date are required"}), 400

        start_dt = parse_date(start_str)
        end_dt = parse_date(end_str)
        if not start_dt or not end_dt or end_dt <= start_dt:
            return jsonify({"message": "Invalid date range"}), 400

        db = get_db()
        vehicle = db.vehicles.find_one({"_id": ObjectId(vehicle_id)})
        if not vehicle:
            return jsonify({"message": "Vehicle not found"}), 404

        # Verify no collision with confirmed or active bookings
        overlapping = db.bookings.find_one({
            "vehicle_id": vehicle_id,
            "status": {"$in": ["confirmed", "active"]},
            "$or": [
                {"start_date": {"$lt": end_dt}, "end_date": {"$gt": start_dt}}
            ]
        })
        if overlapping:
            return jsonify({"message": "Vehicle is already booked for these dates"}), 409

        days = max(1, (end_dt - start_dt).days)
        base_rate = float(vehicle.get("price_per_day", 50.0))
        base_price = base_rate * days

        # Calculate add-ons
        addons_price = 0.0
        if insurance_selected: addons_price += (15.0 * days)
        if gps_selected: addons_price += (5.0 * days)
        if child_seat_selected: addons_price += (8.0 * days)

        subtotal = base_price + addons_price

        # Calculate Promo Discount
        discount_amount = 0.0
        if promo_code:
            promo = db.promotions.find_one({"promo_code": promo_code, "is_active": True})
            if promo:
                pct = promo.get("discount_percent", 0)
                max_d = promo.get("max_discount", 100.0)
                discount_amount = min((subtotal * pct / 100.0), max_d)

        taxable_amount = max(0.0, subtotal - discount_amount)
        tax_amount = round(taxable_amount * 0.18, 2)  # 18% Tax
        total_price = round(taxable_amount + tax_amount, 2)

        # Generate unique booking reference RW-2026-XXXX
        ref_code = f"RW-2026-{random.randint(1000, 9999)}"
        u_id = request.current_user.get("id") or str(request.current_user.get("_id"))

        booking_doc = {
            "booking_reference": ref_code,
            "user_id": u_id,
            "user_name": request.current_user.get("full_name", "John Customer"),
            "user_email": request.current_user.get("email", "customer@gmail.com"),
            "vehicle_id": str(vehicle_id),
            "vehicle_name": f"{vehicle.get('make')} {vehicle.get('model')}",
            "vehicle_image": vehicle.get("image_url"),
            "pickup_branch_id": str(pickup_branch_id) if pickup_branch_id else str(vehicle.get("branch_id", "")),
            "pickup_branch_name": vehicle.get("branch_name", "Downtown Outlet"),
            "return_branch_id": str(return_branch_id) if return_branch_id else str(pickup_branch_id or vehicle.get("branch_id", "")),
            "start_date": start_dt,
            "end_date": end_dt,
            "rental_days": days,
            "price_per_day": base_rate,
            "base_price": base_price,
            "addons_price": addons_price,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "total_price": total_price,
            "status": "pending_payment",
            "created_at": datetime.now(timezone.utc)
        }

        res = db.bookings.insert_one(booking_doc)
        booking_id = str(res.inserted_id)

        return jsonify({
            "message": "Booking created successfully. Proceed to payment.",
            "booking_id": booking_id,
            "booking_reference": ref_code,
            "total_price": total_price
        }), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": "Failed to create booking", "error": str(e)}), 500


@bookings_bp.route("/api/bookings/my-bookings", methods=["GET"])
@token_required
def get_my_bookings():
    try:
        db = get_db()
        u_id = request.current_user.get("id") or str(request.current_user.get("_id"))
        bookings = list(db.bookings.find({"user_id": u_id}).sort("created_at", -1))
        for b in bookings:
            b["id"] = str(b.pop("_id"))
            b["start_date"] = b["start_date"].strftime("%Y-%m-%d")
            b["end_date"] = b["end_date"].strftime("%Y-%m-%d")
            b["created_at"] = b["created_at"].isoformat()

        return jsonify({"bookings": bookings}), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch bookings", "error": str(e)}), 500


@bookings_bp.route("/api/bookings/<booking_id>", methods=["GET"])
@token_required
def get_booking_detail(booking_id):
    try:
        db = get_db()
        if not ObjectId.is_valid(booking_id):
            return jsonify({"message": "Invalid booking ID"}), 400

        booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            return jsonify({"message": "Booking not found"}), 404

        booking["id"] = str(booking.pop("_id"))
        booking["start_date"] = booking["start_date"].strftime("%Y-%m-%d")
        booking["end_date"] = booking["end_date"].strftime("%Y-%m-%d")
        if "created_at" in booking:
            booking["created_at"] = booking["created_at"].isoformat()

        return jsonify({"booking": booking}), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch booking details", "error": str(e)}), 500
