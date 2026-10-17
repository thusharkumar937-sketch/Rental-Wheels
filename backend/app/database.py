from pymongo import MongoClient, ASCENDING, DESCENDING
from app.config import Config

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[Config.DB_NAME]
        init_indexes(_db)
    return _db

def init_indexes(db):
    """Ensure indexes exist for performance & uniqueness constraints."""
    try:
        # Users collection indexes
        db.users.create_index([("email", ASCENDING)], unique=True)

        # Vehicles collection indexes
        db.vehicles.create_index([("status", ASCENDING)])
        db.vehicles.create_index([("category_name", ASCENDING)])
        db.vehicles.create_index([("branch_id", ASCENDING)])

        # Bookings collection indexes
        db.bookings.create_index([("booking_reference", ASCENDING)], unique=True)
        db.bookings.create_index([("user_id", ASCENDING)])
        db.bookings.create_index([("vehicle_id", ASCENDING)])
        db.bookings.create_index([("start_date", ASCENDING), ("end_date", ASCENDING)])

        # KYC Documents indexes
        db.kyc_documents.create_index([("user_id", ASCENDING)], unique=True)

        # Payments collection indexes
        db.payments.create_index([("booking_id", ASCENDING)])
        db.payments.create_index([("transaction_id", ASCENDING)], unique=True)

        # Promotions index
        db.promotions.create_index([("promo_code", ASCENDING)], unique=True)

        print("[DB] MongoDB Indexes Initialized successfully!")
    except Exception as e:
        print(f"[DB] Index initialization notice: {e}")
