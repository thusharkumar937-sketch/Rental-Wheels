from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from bson import ObjectId
from app.config import Config
from app.database import get_db
from app.middleware.auth_middleware import token_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()
    role = data.get("role", "customer").lower()

    if not full_name or not email or not password:
        return jsonify({"message": "Full name, email, and password are required"}), 400

    if role not in ["customer", "staff", "admin"]:
        role = "customer"

    db = get_db()
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"message": "An account with this email address already exists"}), 409

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_doc = {
        "full_name": full_name,
        "email": email,
        "password_hash": hashed_pw,
        "phone": phone,
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }

    result = db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Generate JWT Token
    token = jwt.encode(
        {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        },
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "role": role
        }
    }), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    db = get_db()
    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"message": "Invalid email or password"}), 401

    user_id = str(user["_id"])
    role = user.get("role", "customer")

    # Generate OTP simulation code (e.g. 6-digit code: 123456)
    simulated_otp = "123456"

    # Generate JWT token
    token = jwt.encode(
        {
            "user_id": user_id,
            "email": user["email"],
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        },
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "message": "Credentials verified. OTP sent successfully.",
        "otp_required": True,
        "simulated_otp": simulated_otp,
        "token": token,
        "user": {
            "id": user_id,
            "full_name": user.get("full_name"),
            "email": user["email"],
            "phone": user.get("phone", ""),
            "role": role
        }
    }), 200


@auth_bp.route("/api/auth/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json() or {}
    otp = data.get("otp", "").strip()
    token = data.get("token")

    if not otp:
        return jsonify({"message": "OTP is required"}), 400

    # Validate OTP (Accept simulated '123456' or any 6-digit code for testing)
    if otp != "123456" and len(otp) != 6:
        return jsonify({"message": "Invalid OTP code. Please try 123456"}), 400

    return jsonify({
        "message": "OTP verified successfully. Login complete!",
        "verified": True
    }), 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@token_required
def get_current_user():
    return jsonify({
        "user": request.current_user
    }), 200
