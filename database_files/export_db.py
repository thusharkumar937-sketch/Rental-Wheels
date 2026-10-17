import json
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient

def default_json_converter(o):
    if isinstance(o, ObjectId):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o)} is not JSON serializable")

def export_all():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["rental_wheels_app_db"]
    collections = [
        "vehicles",
        "users",
        "branches",
        "bookings",
        "payments",
        "kyc_documents",
        "promotions",
        "vehicle_maintenance"
    ]
    
    for coll_name in collections:
        coll = db[coll_name]
        docs = list(coll.find({}))
        out_path = f"database_files/{coll_name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2, default=default_json_converter)
        print(f"Exported {len(docs)} documents to {out_path}")

if __name__ == "__main__":
    export_all()
