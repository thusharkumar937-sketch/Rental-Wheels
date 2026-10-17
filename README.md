# Rental Wheels - Complete Car Rental Web Application

An end-to-end full-stack car rental platform connecting Customers, Branch Staff Agents, Fleet Managers, and Administrators.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14 + Flask REST API
- **Database**: MongoDB (`mongodb://localhost:27017/rental_wheels_app_db`)
- **Frontend**: HTML5 + CSS3 (Tailwind CSS) + Vanilla JavaScript (Fetch API)
- **Authentication**: JWT Tokens + Bcrypt Password Hashing + OTP Verification

---

## 🚀 How to Run the Application

### 1. Prerequisites
- Python 3.10+ installed
- MongoDB installed and running on `localhost:27017`

### 2. Install Dependencies
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install required Python packages
pip install -r backend/requirements.txt
```

### 3. Seed Database
```bash
python backend/seed.py
```

### 4. Start Backend REST Server
```bash
python backend/run.py
```
*Backend API server will run on http://127.0.0.1:5000*

### 5. Start Frontend HTTP Server
```bash
python -m http.server 8000 --directory frontend
```
*Frontend application will run on http://127.0.0.1:8000/index.html*

---

## 🔑 Pre-Configured Demo Accounts

| Role | Email | Password | OTP Code | Dashboard Page |
|---|---|---|---|---|
| **Customer** | `customer@gmail.com` | `customer123` | `123456` | [customer-dashboard.html](http://127.0.0.1:8000/customer-dashboard.html) |
| **Branch Staff** | `staff@rentalwheels.com` | `staff123` | `123456` | [staff-dashboard.html](http://127.0.0.1:8000/staff-dashboard.html) |
| **Fleet Admin** | `admin@rentalwheels.com` | `admin123` | `123456` | [admin-dashboard.html](http://127.0.0.1:8000/admin-dashboard.html) |

---

## 📂 Project Directory Structure

```
RENTAL WHEELS/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask App Factory & Blueprint Registrations
│   │   ├── config.py            # Environment Configuration
│   │   ├── database.py          # MongoDB Client & Index Management
│   │   ├── middleware/          # JWT & Role Authentication Middleware
│   │   └── routes/              # Auth, Vehicles, Bookings, Payments, KYC, Staff, Admin
│   ├── uploads/                 # Customer Driving License & Vehicle Uploads
│   ├── run.py                   # Flask Server Entry Point
│   ├── seed.py                  # Seed Data Script
│   ├── .env                     # Mongo URI & Secret Configuration
│   └── requirements.txt         # Dependencies
│
├── frontend/
│   ├── js/                      # API Helper Client (api.js)
│   ├── index.html               # Home Page & Search
│   ├── login.html               # Sign In, Registration & OTP Modal
│   ├── kyc.html                 # Profile & Driving License Upload
│   ├── vehicles.html            # Vehicle Catalog & Search Filters
│   ├── booking.html             # Reservation Stepper & Price Breakdown
│   ├── checkout.html            # Payment Gateway
│   ├── confirmation.html        # Booking Confirmation & Digital Invoice
│   ├── customer-dashboard.html  # Customer Dashboard with Profile Sidebar
│   ├── admin-dashboard.html     # Fleet & Admin Control Panel with Navigation Sidebar
│   └── staff-dashboard.html     # Branch Staff Desk with Handover & Return Modals
│
├── tests/
│   └── selenium_suite/          # 100 Selenium Automated UI Test Cases (10 Suites x 10 Tests)
│       ├── test_suite_01_auth_kyc.py
│       ├── test_suite_02_catalog_search.py
│       ├── test_suite_03_booking_payments.py
│       ├── test_suite_04_dashboards_operations.py
│       ├── test_suite_05_advanced_workflows.py
│       ├── test_suite_06_validation_edge_cases.py
│       ├── test_suite_07_security_role_navigation.py
│       ├── test_suite_08_operations_maintenance.py
│       ├── test_suite_09_administration_fleet.py
│       ├── test_suite_10_cross_flow_journeys.py
│       └── run_all_100_tests.py
│
├── requirements.txt             # Root requirements
├── start.bat                    # One-click start script
└── README.md                    # Project Setup Guide
```

---

## 🧪 Automated Testing (100 Selenium Test Cases)

To execute all 100 UI test cases:
```powershell
.\venv\Scripts\python tests/selenium_suite/run_all_100_tests.py
```
Or run any individual suite of 10 test cases:
```powershell
.\venv\Scripts\python -m unittest tests/selenium_suite/test_suite_01_auth_kyc.py -v
```

