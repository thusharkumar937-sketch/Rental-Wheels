# 🚗 Rental Wheels - Team Onboarding & Setup Guide

Welcome to the **Rental Wheels** car rental web application project. This guide contains everything you need to run, inspect, and test the full-stack system on your local machine.

---

## 📋 1. Prerequisites Checklist

Before running the project, make sure you have the following installed on your PC:

1. **Python 3.10+**: [Download Python](https://www.python.org/downloads/) *(Ensure "Add Python to PATH" is checked during installation)*
2. **Node.js (v18+) & npm**: [Download Node.js](https://nodejs.org/)
3. **MongoDB Community Server (v6 or v7)**: [Download MongoDB](https://www.mongodb.com/try/download/community) *(Ensure MongoDB service is running on `localhost:27017`)*
4. **Google Chrome Browser**: Required for running the automated Selenium test suites.

---

## ⚡ 2. Quick Setup (5 Minutes)

Open your terminal (PowerShell, Command Prompt, or VS Code Terminal) in the extracted project root directory (`rental_wheels/`):

### Step A: Set Up Python Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### Step B: Install Node Dependencies
```powershell
npm install
```

### Step C: Seed Local MongoDB Database
Populate your local MongoDB instance with initial mock vehicles, users, branches, and sample bookings:
```powershell
python backend/seed.py
```
*(Or run `npm run seed`)*

### Step D: Launch the Application
You can launch the full stack (Flask backend + Frontend HTTP server + Automatic browser launch) with a single command:
```powershell
# Method 1 (Recommended):
npm start

# Method 2 (Windows Shortcut):
# Double click on start.bat in the project root
```

* **Frontend URL**: [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)
* **Backend API URL**: [http://127.0.0.1:5000/api](http://127.0.0.1:5000/api)

---

## 🗄️ 3. How to View and Inspect the Database Files

You have **two easy ways** to view the database:

### Option 1: Direct File Inspection (No Database Client Needed!)
All MongoDB collections have been pre-exported as formatted, readable `.json` files in the `database_files/` folder. You can open and inspect them directly in VS Code, Notepad, or any editor:
* `database_files/vehicles.json`: 12 vehicle models with specs, rental pricing, mileage, and images.
* `database_files/users.json`: Customer, Staff, and Admin accounts with bcrypt-hashed passwords.
* `database_files/branches.json`: City pickup/return branches (Airport, Downtown, Tech Hub).
* `database_files/bookings.json`: Active, confirmed, and completed rental reservations.
* `database_files/payments.json`: Payment records, transaction IDs, and invoice summaries.
* `database_files/kyc_documents.json`: Driver license & identity verification documents.
* `database_files/promotions.json`: Active discount codes (`FIRST10`, `SUMMER25`).
* `database_files/vehicle_maintenance.json`: Service schedules and vehicle inspection logs.

> **Note**: To re-export live data from MongoDB into these JSON files at any time, run:
> ```powershell
> python database_files/export_db.py
> ```

### Option 2: Live Database GUI (MongoDB Compass)
1. Open **MongoDB Compass**.
2. Connect to the default URI: `mongodb://localhost:27017`.
3. Select database: `rental_wheels_app_db` to view real-time collections and documents.

---

## 🔑 4. Demo Login Credentials

You can log in and test different user roles using the following pre-seeded accounts:

| Role | Email Address | Password | Features / Dashboard |
| :--- | :--- | :--- | :--- |
| **Customer** | `john@example.com` | `password123` | Vehicle Catalog, Booking, Payments, KYC Upload, Booking History |
| **Branch Staff** | `staff@rentalwheels.com` | `password123` | Staff Desk, Vehicle Handover, Vehicle Return, Inspection Logs |
| **Administrator**| `admin@rentalwheels.com` | `admin123` | Fleet Management, Add/Edit Cars, User Control, System Analytics |

---

## 🧪 5. Running the 150 Automated Selenium Tests

The project includes an end-to-end automated testing suite consisting of **150 comprehensive test cases across 15 modular suites**.

### Run All 150 Tests:
Make sure the backend and frontend are running (`npm start`), then in another terminal run:
```powershell
python tests/selenium_suite/run_all_150_tests.py
```
*(Or run `npm test`)*

### Run Specific Test Suites:
You can also run any individual test suite independently:
* `python -m unittest tests/selenium_suite/test_suite_01_auth_kyc.py` (Auth & KYC flow)
* `python -m unittest tests/selenium_suite/test_suite_02_catalog_search.py` (Catalog & search)
* `python -m unittest tests/selenium_suite/test_suite_03_booking_payments.py` (Booking & payments)
* `python -m unittest tests/selenium_suite/test_suite_04_dashboards_operations.py` (Dashboards)
* `python -m unittest tests/selenium_suite/test_suite_05_advanced_workflows.py` (Workflows)
* `python -m unittest tests/selenium_suite/test_suite_06_validation_edge_cases.py` (Form validation)
* `python -m unittest tests/selenium_suite/test_suite_07_security_role_navigation.py` (Security & RBAC)
* `python -m unittest tests/selenium_suite/test_suite_08_operations_maintenance.py` (Maintenance)
* `python -m unittest tests/selenium_suite/test_suite_09_administration_fleet.py` (Admin fleet)
* `python -m unittest tests/selenium_suite/test_suite_10_cross_flow_journeys.py` (Cross-flow journeys)
* `python -m unittest tests/selenium_suite/test_suite_11_booking_lifecycle.py` (Lifecycle & cancellations)
* `python -m unittest tests/selenium_suite/test_suite_12_security_negative_access.py` (Penetration & tampering)
* `python -m unittest tests/selenium_suite/test_suite_13_staff_handovers_inspection.py` (Staff handovers)
* `python -m unittest tests/selenium_suite/test_suite_14_admin_fleet_controls.py` (Fleet CRUD & pricing)
* `python -m unittest tests/selenium_suite/test_suite_15_responsive_ui_integrity.py` (Mobile/desktop responsiveness)

---

## 📂 6. Project Architecture & Directory Layout

```text
RENTAL WHEELS/
├── .env                                 # Environment config (Mongo URI & JWT Secret)
├── start.bat                            # Windows one-click runner
├── package.json                         # npm run scripts (start, seed, test, export-db)
├── requirements.txt                     # Python packages (Flask, PyMongo, Selenium, etc.)
├── README.md                            # High-level project summary
├── TEAM_SETUP_GUIDE.md                  # This setup and onboarding guide
│
├── backend/                             # Flask REST API Backend
│   ├── .env                             # Backend copy of environment variables
│   ├── run.py                           # Flask server entrypoint (port 5000)
│   ├── seed.py                          # MongoDB seeder script (12 cars, 3 users, branches)
│   └── app/
│       ├── __init__.py                  # Flask app factory & CORS configuration
│       ├── config.py                    # App configuration loader
│       ├── database.py                  # PyMongo client & collection accessors
│       ├── middleware/                  # JWT auth guard & role-based middleware
│       ├── routes/                      # API endpoints (auth, vehicles, bookings, kyc, etc.)
│       └── uploads/                     # Upload storage for KYC and car images
│
├── frontend/                            # Frontend Web Application (Vanilla JS + Tailwind CSS)
│   ├── index.html                       # Landing page with hero banner & vehicle highlights
│   ├── catalog.html                     # Vehicle search, filter by branch/type, sort by price
│   ├── vehicle-detail.html              # Vehicle specifications, pricing, date picker
│   ├── booking.html                     # Reservation checkout, promo codes, insurance addons
│   ├── payment.html                     # Mock payment gateway (Card, UPI, NetBanking)
│   ├── confirmation.html                # Booking invoice, confirmation ticket, QR code
│   ├── kyc.html                         # Driver license & ID upload verification
│   ├── profile.html                     # Customer dashboard & past bookings
│   ├── staff-dashboard.html             # Staff vehicle check-in/check-out & inspection
│   ├── admin-dashboard.html             # Admin fleet management & revenue analytics
│   ├── js/                              # Client-side scripts (API client, Auth, UI handlers)
│   └── css/                             # Stylesheet overrides and Tailwind styling
│
├── database_files/                      # Readable JSON Database Dumps & Exporter
│   ├── export_db.py                     # Python script to dump MongoDB collections to JSON
│   ├── vehicles.json                    # Vehicles collection dump
│   ├── users.json                       # Users collection dump
│   ├── branches.json                   # Branches collection dump
│   ├── bookings.json                    # Bookings collection dump
│   ├── payments.json                    # Payments collection dump
│   ├── kyc_documents.json               # KYC documents collection dump
│   ├── promotions.json                  # Promotions & coupons collection dump
│   └── vehicle_maintenance.json         # Vehicle maintenance logs collection dump
│
└── tests/                               # Test Automation Suites
    ├── selenium_suite/                  # 15 modular suites (150 tests total)
    │   ├── run_all_150_tests.py         # Test runner for all 150 Selenium tests
    │   ├── test_suite_01_auth_kyc.py ... test_suite_15_responsive_ui_integrity.py
    │   └── README.md                    # Detailed documentation for all 150 test cases
    └── standalone_tests/                # Standalone component tests
```

---

## 🛠️ 7. Common Troubleshooting

* **Issue**: MongoDB Connection Error (`ServerSelectionTimeoutError`)
  * **Fix**: Verify your MongoDB service is running. On Windows, press `Win + R`, type `services.msc`, locate `MongoDB Server`, and click **Start**.
* **Issue**: Selenium Chrome Driver mismatch
  * **Fix**: Ensure your Google Chrome browser is updated. Selenium 4 automatically manages the matching ChromeDriver binary.
* **Issue**: Port 5000 or 8000 already in use
  * **Fix**: Close any existing Python processes running in the background via Task Manager or run:
    ```powershell
    Get-Process python* | Stop-Process
    ```

---
*Created for the Rental Wheels Development and QA Team.*
