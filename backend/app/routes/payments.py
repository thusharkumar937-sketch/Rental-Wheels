from datetime import datetime, timezone
import random
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.database import get_db
from app.middleware.auth_middleware import token_required

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/api/payments/process", methods=["POST"])
@token_required
def process_payment():
    try:
        data = request.get_json() or {}
        booking_id = data.get("booking_id")
        payment_method = data.get("payment_method", "Card")
        card_number = data.get("card_number", "")

        if not booking_id:
            return jsonify({"message": "Booking ID is required"}), 400

        db = get_db()
        booking = None
        if ObjectId.is_valid(booking_id):
            booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        elif booking_id == "demo_001":
            booking = db.bookings.find_one({})

        if not booking:
            # Fallback for demo reservations
            booking = db.bookings.find_one() or {
                "_id": ObjectId(),
                "booking_reference": "RW-2026-DEMO",
                "total_price": 249.00
            }

        # Generate unique transaction ID
        txn_id = f"TXN-{random.randint(10000000, 99999999)}"

        # Save Payment record
        payment_doc = {
            "booking_id": booking_id,
            "booking_reference": booking.get("booking_reference"),
            "user_id": request.current_user["id"],
            "user_email": request.current_user.get("email"),
            "transaction_id": txn_id,
            "payment_method": payment_method,
            "amount": booking.get("total_price", 0.0),
            "status": "success",
            "payment_date": datetime.now(timezone.utc)
        }

        db.payments.insert_one(payment_doc)

        # Update Booking status to 'confirmed'
        db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {
                "status": "confirmed",
                "payment_transaction_id": txn_id,
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        return jsonify({
            "message": "Payment processed successfully!",
            "transaction_id": txn_id,
            "status": "success",
            "booking_reference": booking.get("booking_reference")
        }), 200
    except Exception as e:
        return jsonify({"message": "Payment processing failed", "error": str(e)}), 500


@payments_bp.route("/api/payments/invoice/<booking_id>", methods=["GET"])
@token_required
def get_invoice(booking_id):
    try:
        db = get_db()
        booking = None
        if ObjectId.is_valid(booking_id):
            booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        elif booking_id == "demo_001":
            booking = db.bookings.find_one({})

        if not booking:
            return jsonify({"message": "Booking record not found"}), 404

        payment = db.payments.find_one({"booking_id": booking_id})

        booking["id"] = str(booking.pop("_id"))
        booking["start_date"] = booking["start_date"].strftime("%Y-%m-%d")
        booking["end_date"] = booking["end_date"].strftime("%Y-%m-%d")

        return jsonify({
            "invoice": {
                "booking": booking,
                "payment": {
                    "transaction_id": payment.get("transaction_id") if payment else "N/A",
                    "payment_method": payment.get("payment_method") if payment else "Pay at Branch",
                    "amount": payment.get("amount") if payment else booking.get("total_price"),
                    "date": payment["payment_date"].strftime("%Y-%m-%d %H:%M:%S") if payment else "Pending"
                }
            }
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to generate invoice", "error": str(e)}), 500
