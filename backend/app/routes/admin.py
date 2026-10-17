from datetime import datetime, timezone
from flask import Blueprint, jsonify
from bson import ObjectId
from app.database import get_db
from app.middleware.auth_middleware import token_required, role_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/api/admin/metrics", methods=["GET"])
@token_required
@role_required(["admin", "staff"])
def get_admin_metrics():
    try:
        db = get_db()
        total_vehicles = db.vehicles.count_documents({})
        available_vehicles = db.vehicles.count_documents({"status": "available"})
        rented_vehicles = db.vehicles.count_documents({"status": "rented"})
        servicing_vehicles = db.vehicles.count_documents({"status": "servicing"})

        total_users = db.users.count_documents({})
        total_bookings = db.bookings.count_documents({})
        pending_kyc = db.kyc_documents.count_documents({"status": "pending"})

        # Calculate Total Revenue from payments
        pipeline = [
            {"$match": {"status": "success"}},
            {"$group": {"_id": None, "total_revenue": {"$sum": "$amount"}}}
        ]
        rev_res = list(db.payments.aggregate(pipeline))
        total_revenue = rev_res[0]["total_revenue"] if rev_res else 0.0

        utilization_rate = round((rented_vehicles / total_vehicles * 100), 1) if total_vehicles > 0 else 0.0

        return jsonify({
            "metrics": {
                "total_vehicles": total_vehicles,
                "available_vehicles": available_vehicles,
                "rented_vehicles": rented_vehicles,
                "servicing_vehicles": servicing_vehicles,
                "total_users": total_users,
                "total_bookings": total_bookings,
                "pending_kyc": pending_kyc,
                "total_revenue": round(total_revenue, 2),
                "utilization_rate": utilization_rate
            }
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch admin metrics", "error": str(e)}), 500


@admin_bp.route("/api/admin/bookings", methods=["GET"])
@token_required
@role_required(["admin", "staff"])
def get_master_bookings():
    try:
        db = get_db()
        bookings = list(db.bookings.find().sort("created_at", -1))
        for b in bookings:
            b["id"] = str(b.pop("_id"))
            b["start_date"] = b["start_date"].strftime("%Y-%m-%d")
            b["end_date"] = b["end_date"].strftime("%Y-%m-%d")
            if "created_at" in b:
                b["created_at"] = b["created_at"].isoformat()

        return jsonify({"bookings": bookings}), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch master bookings", "error": str(e)}), 500
