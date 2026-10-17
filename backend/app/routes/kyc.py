from datetime import datetime, timezone
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from bson import ObjectId
from app.database import get_db
from app.middleware.auth_middleware import token_required, role_required

kyc_bp = Blueprint("kyc", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@kyc_bp.route("/api/kyc/status", methods=["GET"])
@token_required
def get_kyc_status():
    try:
        db = get_db()
        user_id = request.current_user["id"]

        kyc_doc = db.kyc_documents.find_one({"user_id": user_id})
        if not kyc_doc:
            return jsonify({
                "status": "unsubmitted",
                "message": "No KYC document uploaded yet",
                "kyc": None
            }), 200

        kyc_doc["id"] = str(kyc_doc.pop("_id"))
        if "updated_at" in kyc_doc:
            kyc_doc["updated_at"] = kyc_doc["updated_at"].isoformat()

        return jsonify({
            "status": kyc_doc.get("status", "pending"),
            "kyc": kyc_doc
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch KYC status", "error": str(e)}), 500


@kyc_bp.route("/api/kyc/upload", methods=["POST"])
@token_required
def upload_kyc():
    try:
        db = get_db()
        user_id = request.current_user["id"]

        license_number = request.form.get("license_number", "").strip()
        license_expiry = request.form.get("license_expiry", "").strip()

        if not license_number or not license_expiry:
            return jsonify({"message": "Driving license number and expiry date are required"}), 400

        kyc_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "kyc")
        os.makedirs(kyc_folder, exist_ok=True)

        front_file = request.files.get("license_front")
        back_file = request.files.get("license_back")

        front_url = "/uploads/kyc/sample_license_front.jpg"
        back_url = "/uploads/kyc/sample_license_back.jpg"

        if front_file and allowed_file(front_file.filename):
            filename = secure_filename(f"front_{user_id}_{front_file.filename}")
            filepath = os.path.join(kyc_folder, filename)
            front_file.save(filepath)
            front_url = f"/uploads/kyc/{filename}"

        if back_file and allowed_file(back_file.filename):
            filename = secure_filename(f"back_{user_id}_{back_file.filename}")
            filepath = os.path.join(kyc_folder, filename)
            back_file.save(filepath)
            back_url = f"/uploads/kyc/{filename}"

        kyc_data = {
            "user_id": user_id,
            "user_name": request.current_user.get("full_name"),
            "user_email": request.current_user.get("email"),
            "license_number": license_number,
            "license_expiry": license_expiry,
            "license_front_url": front_url,
            "license_back_url": back_url,
            "status": "pending",
            "admin_notes": "Submitted by customer for verification",
            "updated_at": datetime.now(timezone.utc)
        }

        db.kyc_documents.update_one(
            {"user_id": user_id},
            {"$set": kyc_data},
            upsert=True
        )

        return jsonify({
            "message": "KYC documents submitted successfully. Verification pending approval.",
            "status": "pending"
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to upload KYC document", "error": str(e)}), 500


@kyc_bp.route("/api/kyc/admin/pending", methods=["GET"])
@token_required
@role_required(["admin", "staff"])
def get_pending_kyc():
    try:
        db = get_db()
        docs = list(db.kyc_documents.find())
        for d in docs:
            d["id"] = str(d.pop("_id"))
            if "updated_at" in d:
                d["updated_at"] = d["updated_at"].isoformat()
        return jsonify({"kyc_list": docs}), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch pending KYC list", "error": str(e)}), 500


@kyc_bp.route("/api/kyc/admin/verify/<kyc_id>", methods=["PUT"])
@token_required
@role_required(["admin", "staff"])
def update_kyc_status(kyc_id):
    try:
        data = request.get_json() or {}
        new_status = data.get("status", "verified").lower()
        admin_notes = data.get("admin_notes", "Verified by admin")

        if new_status not in ["verified", "rejected", "pending"]:
            return jsonify({"message": "Invalid status value"}), 400

        db = get_db()
        result = db.kyc_documents.update_one(
            {"_id": ObjectId(kyc_id)},
            {"$set": {
                "status": new_status,
                "admin_notes": admin_notes,
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        if result.matched_count == 0:
            return jsonify({"message": "KYC record not found"}), 404

        return jsonify({
            "message": f"KYC status updated to '{new_status}' successfully"
        }), 200
    except Exception as e:
        return jsonify({"message": "Failed to update KYC status", "error": str(e)}), 500
