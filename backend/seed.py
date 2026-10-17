import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in sys.path regardless of execution CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from pymongo import MongoClient
from app.config import Config

def seed_database():
    client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[Config.DB_NAME]

    print("[SEED] Seeding Clean Data with Available Dates...")

    # 1. Seed Branches
    db.branches.delete_many({})
    branches = [
        {
            "branch_name": "Downtown Central Outlet",
            "address": "123 Main Commercial Street, City Center",
            "city": "Metropolis",
            "contact_phone": "+1 (555) 100-2001",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "branch_name": "International Airport Branch",
            "address": "Terminal 2 Pickup Hub, Airport Boulevard",
            "city": "Metropolis",
            "contact_phone": "+1 (555) 100-2002",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "branch_name": "Tech Park Station",
            "address": "Building 4, Silicon Avenue",
            "city": "Metropolis",
            "contact_phone": "+1 (555) 100-2003",
            "created_at": datetime.now(timezone.utc)
        }
    ]
    branch_ids = db.branches.insert_many(branches).inserted_ids
    print(f"  - Inserted {len(branch_ids)} Outlets")

    # 2. Seed Vehicle Categories
    db.vehicle_categories.delete_many({})
    categories = [
        {"category_name": "SUV", "description": "Spacious 7-seater & 4x4 off-road vehicles ideal for family trips", "icon": "suv"},
        {"category_name": "Sedan", "description": "Comfortable 5-seater premium sedans for business & city travel", "icon": "sedan"},
        {"category_name": "Hatchback", "description": "Compact fuel-efficient cars for easy parking & city commutes", "icon": "hatchback"},
        {"category_name": "Luxury", "description": "High-end luxury vehicles for special events & maximum comfort", "icon": "luxury"},
        {"category_name": "Electric", "description": "Zero-emission eco-friendly electric vehicles with long battery range", "icon": "ev"}
    ]
    db.vehicle_categories.insert_many(categories)
    print("  - Inserted Vehicle Categories")

    # 3. Seed Expanded Fleet (12 Vehicles)
    db.vehicles.delete_many({})
    vehicles = [
        # SUVs
        {
            "category_name": "SUV",
            "branch_id": str(branch_ids[0]),
            "branch_name": "Downtown Central Outlet",
            "make": "Toyota",
            "model": "Fortuner Legender",
            "year": 2024,
            "license_plate": "RW-SUV-101",
            "color": "Pearl White",
            "seating_capacity": 7,
            "fuel_type": "Diesel",
            "transmission": "Automatic",
            "price_per_day": 85.00,
            "mileage": "14 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&q=80"
        },
        {
            "category_name": "SUV",
            "branch_id": str(branch_ids[1]),
            "branch_name": "International Airport Branch",
            "make": "Mahindra",
            "model": "Thar 4x4 LX",
            "year": 2024,
            "license_plate": "RW-SUV-102",
            "color": "Napoli Black",
            "seating_capacity": 4,
            "fuel_type": "Diesel",
            "transmission": "Manual",
            "price_per_day": 70.00,
            "mileage": "12 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&q=80"
        },
        {
            "category_name": "SUV",
            "branch_id": str(branch_ids[2]),
            "branch_name": "Tech Park Station",
            "make": "Hyundai",
            "model": "Creta SX(O)",
            "year": 2023,
            "license_plate": "RW-SUV-103",
            "color": "Titan Grey",
            "seating_capacity": 5,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "price_per_day": 55.00,
            "mileage": "16 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=800&q=80"
        },

        # Sedans
        {
            "category_name": "Sedan",
            "branch_id": str(branch_ids[0]),
            "branch_name": "Downtown Central Outlet",
            "make": "Honda",
            "model": "City ZX",
            "year": 2023,
            "license_plate": "RW-SED-201",
            "color": "Meteoroid Grey",
            "seating_capacity": 5,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "price_per_day": 45.00,
            "mileage": "18 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800&q=80"
        },
        {
            "category_name": "Sedan",
            "branch_id": str(branch_ids[1]),
            "branch_name": "International Airport Branch",
            "make": "Hyundai",
            "model": "Verna Turbo DCT",
            "year": 2024,
            "license_plate": "RW-SED-202",
            "color": "Abyss Black",
            "seating_capacity": 5,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "price_per_day": 50.00,
            "mileage": "17 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=800&q=80"
        },

        # Luxury
        {
            "category_name": "Luxury",
            "branch_id": str(branch_ids[1]),
            "branch_name": "International Airport Branch",
            "make": "BMW",
            "model": "5 Series M Sport",
            "year": 2024,
            "license_plate": "RW-LUX-301",
            "color": "Phytonic Blue",
            "seating_capacity": 5,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "price_per_day": 140.00,
            "mileage": "12 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&q=80"
        },
        {
            "category_name": "Luxury",
            "branch_id": str(branch_ids[0]),
            "branch_name": "Downtown Central Outlet",
            "make": "Mercedes-Benz",
            "model": "C-Class C200",
            "year": 2024,
            "license_plate": "RW-LUX-302",
            "color": "Obsidian Black",
            "seating_capacity": 5,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "price_per_day": 155.00,
            "mileage": "13 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&q=80"
        },
        {
            "category_name": "Luxury",
            "branch_id": str(branch_ids[1]),
            "branch_name": "International Airport Branch",
            "make": "Audi",
            "model": "Q7 Quattro",
            "year": 2024,
            "license_plate": "RW-LUX-303",
            "color": "Navarra Blue",
            "seating_capacity": 7,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "price_per_day": 185.00,
            "mileage": "10 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=800&q=80"
        },

        # Electric
        {
            "category_name": "Electric",
            "branch_id": str(branch_ids[1]),
            "branch_name": "International Airport Branch",
            "make": "Tesla",
            "model": "Model 3 Long Range",
            "year": 2024,
            "license_plate": "RW-EV-401",
            "color": "Solid Black",
            "seating_capacity": 5,
            "fuel_type": "EV",
            "transmission": "Automatic",
            "price_per_day": 95.00,
            "mileage": "450 km range",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&q=80"
        },
        {
            "category_name": "Electric",
            "branch_id": str(branch_ids[2]),
            "branch_name": "Tech Park Station",
            "make": "Hyundai",
            "model": "Ioniq 5 AWD",
            "year": 2024,
            "license_plate": "RW-EV-402",
            "color": "Gravity Gold",
            "seating_capacity": 5,
            "fuel_type": "EV",
            "transmission": "Automatic",
            "price_per_day": 90.00,
            "mileage": "480 km range",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=800&q=80"
        },

        # Hatchbacks
        {
            "category_name": "Hatchback",
            "branch_id": str(branch_ids[2]),
            "branch_name": "Tech Park Station",
            "make": "Maruti Suzuki",
            "model": "Swift ZXi+",
            "year": 2023,
            "license_plate": "RW-HAT-501",
            "color": "Luster Blue",
            "seating_capacity": 5,
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "price_per_day": 30.00,
            "mileage": "22 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1590362891991-f776e747a588?w=800&q=80"
        },
        {
            "category_name": "Hatchback",
            "branch_id": str(branch_ids[0]),
            "branch_name": "Downtown Central Outlet",
            "make": "Hyundai",
            "model": "i20 N Line N8",
            "year": 2024,
            "license_plate": "RW-HAT-502",
            "color": "Thunder Blue",
            "seating_capacity": 5,
            "fuel_type": "Petrol",
            "transmission": "Automatic",
            "price_per_day": 38.00,
            "mileage": "20 km/l",
            "status": "available",
            "image_url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80"
        }
    ]
    veh_ids = db.vehicles.insert_many(vehicles).inserted_ids
    print(f"  - Inserted {len(veh_ids)} Fleet Vehicles across all categories")

    # 4. Seed Default Users
    db.users.delete_many({})
    def hash_pw(pw):
        return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    users = [
        {
            "full_name": "Admin User",
            "email": "admin@rentalwheels.com",
            "password_hash": hash_pw("admin123"),
            "phone": "+1 (555) 999-0001",
            "role": "admin",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "full_name": "Branch Staff Agent",
            "email": "staff@rentalwheels.com",
            "password_hash": hash_pw("staff123"),
            "phone": "+1 (555) 999-0002",
            "role": "staff",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "full_name": "John Customer",
            "email": "customer@gmail.com",
            "password_hash": hash_pw("customer123"),
            "phone": "+1 (555) 999-0003",
            "role": "customer",
            "created_at": datetime.now(timezone.utc)
        }
    ]
    user_ids = db.users.insert_many(users).inserted_ids
    cust_id = str(user_ids[2])
    print("  - Inserted Default Users (Admin, Staff, Customer)")

    # 5. Seed Customer KYC Document (Verified License)
    db.kyc_documents.delete_many({})
    kyc_data = {
        "user_id": cust_id,
        "user_name": "John Customer",
        "user_email": "customer@gmail.com",
        "license_number": "DL-1420110098765",
        "license_expiry": "2029-12-31",
        "license_front_url": "/uploads/kyc/sample_license_front.jpg",
        "license_back_url": "/uploads/kyc/sample_license_back.jpg",
        "status": "verified",
        "admin_notes": "Verified automatically for demo testing",
        "updated_at": datetime.now(timezone.utc)
    }
    db.kyc_documents.insert_one(kyc_data)

    # 6. Seed Past Completed Bookings
    db.bookings.delete_many({})
    db.payments.delete_many({})

    b1_start = datetime.now(timezone.utc) - timedelta(days=20)
    b1_end = datetime.now(timezone.utc) - timedelta(days=17)
    booking1 = {
        "booking_reference": "RW-2026-8891",
        "user_id": cust_id,
        "user_name": "John Customer",
        "user_email": "customer@gmail.com",
        "vehicle_id": str(veh_ids[0]),
        "vehicle_name": "Toyota Fortuner Legender",
        "vehicle_image": vehicles[0]["image_url"],
        "pickup_branch_id": str(branch_ids[0]),
        "pickup_branch_name": "Downtown Central Outlet",
        "return_branch_id": str(branch_ids[0]),
        "start_date": b1_start,
        "end_date": b1_end,
        "rental_days": 3,
        "price_per_day": 85.00,
        "base_price": 255.00,
        "addons_price": 45.00,
        "discount_amount": 38.25,
        "tax_amount": 47.12,
        "total_price": 308.87,
        "status": "completed",
        "created_at": datetime.now(timezone.utc) - timedelta(days=21)
    }
    res1 = db.bookings.insert_one(booking1)

    db.payments.insert_one({
        "booking_id": str(res1.inserted_id),
        "booking_reference": "RW-2026-8891",
        "user_id": cust_id,
        "user_email": "customer@gmail.com",
        "transaction_id": "TXN-88492019",
        "payment_method": "Card",
        "amount": 308.87,
        "status": "success",
        "payment_date": datetime.now(timezone.utc) - timedelta(days=21)
    })

    b2_start = datetime.now(timezone.utc) - timedelta(days=15)
    b2_end = datetime.now(timezone.utc) - timedelta(days=12)
    booking2 = {
        "booking_reference": "RW-2026-4412",
        "user_id": cust_id,
        "user_name": "John Customer",
        "user_email": "customer@gmail.com",
        "vehicle_id": str(veh_ids[8]),
        "vehicle_name": "Tesla Model 3 Long Range",
        "vehicle_image": vehicles[8]["image_url"],
        "pickup_branch_id": str(branch_ids[1]),
        "pickup_branch_name": "International Airport Branch",
        "return_branch_id": str(branch_ids[1]),
        "start_date": b2_start,
        "end_date": b2_end,
        "rental_days": 3,
        "price_per_day": 95.00,
        "base_price": 285.00,
        "addons_price": 15.00,
        "discount_amount": 0.0,
        "tax_amount": 54.00,
        "total_price": 354.00,
        "status": "completed",
        "created_at": datetime.now(timezone.utc) - timedelta(days=16)
    }
    res2 = db.bookings.insert_one(booking2)

    db.payments.insert_one({
        "booking_id": str(res2.inserted_id),
        "booking_reference": "RW-2026-4412",
        "user_id": cust_id,
        "user_email": "customer@gmail.com",
        "transaction_id": "TXN-77192088",
        "payment_method": "UPI",
        "amount": 354.00,
        "status": "success",
        "payment_date": datetime.now(timezone.utc) - timedelta(days=16)
    })

    print("  - Seeded past completed bookings. All 12 fleet cars are 100% unblocked & available for current dates!")

    # 7. Seed Promotions
    db.promotions.delete_many({})
    promos = [
        {"promo_code": "WHEELS2026", "discount_percent": 15, "max_discount": 50.00, "valid_until": "2026-12-31", "is_active": True},
        {"promo_code": "WELCOME10", "discount_percent": 10, "max_discount": 30.00, "valid_until": "2026-12-31", "is_active": True}
    ]
    db.promotions.insert_many(promos)

    print("[SUCCESS] Seed Completed Successfully!")

if __name__ == "__main__":
    seed_database()
