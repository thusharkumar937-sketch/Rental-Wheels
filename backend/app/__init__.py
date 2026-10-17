import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for frontend cross-origin access
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "kyc"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "vehicles"), exist_ok=True)

    # Serve uploaded static files
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Root route redirect to frontend web application
    @app.route("/")
    def root_redirect():
        from flask import redirect
        return redirect("http://127.0.0.1:8000/index.html")

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.kyc import kyc_bp
    from app.routes.bookings import bookings_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp
    from app.routes.staff import staff_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(kyc_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)

    return app
