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
