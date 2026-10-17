import os
import sys

# Ensure backend directory is in sys.path regardless of execution CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import get_db

app = create_app()

if __name__ == "__main__":
    # Test DB connection on startup
    try:
        db = get_db()
        print(f"[INIT] Connected to MongoDB database: '{db.name}'")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")

    print("[SERVER] Starting Rental Wheels API Server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
