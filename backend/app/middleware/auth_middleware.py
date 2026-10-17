from functools import wraps
from flask import request, jsonify
import jwt
from bson import ObjectId
from app.config import Config
from app.database import get_db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({"message": "Authentication token is missing"}), 401

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            db = get_db()
            user = db.users.find_one({"_id": ObjectId(data["user_id"])})
            if not user:
                return jsonify({"message": "User not found or account deactivated"}), 401
            
            user_id_str = str(user["_id"])
            user["_id"] = user_id_str
            user["id"] = user_id_str
            user.pop("password_hash", None)
            request.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired. Please login again."}), 401
        except Exception as e:
            return jsonify({"message": "Invalid authentication token", "error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, "current_user"):
                return jsonify({"message": "User context not found"}), 401
            
            user_role = request.current_user.get("role", "customer")
            if user_role not in allowed_roles:
                return jsonify({
                    "message": f"Access denied. Requires one of the following roles: {', '.join(allowed_roles)}"
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
