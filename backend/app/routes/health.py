from flask import Blueprint, jsonify
from app.database import get_db

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    try:
        db = get_db()
        # Test command to verify database connectivity
        server_status = db.command("ping")
        
        # Count collections
        collections = db.list_collection_names()
        
        return jsonify({
            "status": "online",
            "message": "Rental Wheels API Service is healthy and connected to MongoDB",
            "database": {
                "name": db.name,
                "connected": True,
                "ping": server_status.get("ok", 0) == 1.0,
                "collections_count": len(collections),
                "collections": collections
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "message": "API server running but database connection issue",
            "error": str(e)
        }), 500
