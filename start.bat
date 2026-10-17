@echo off
echo ===================================================
echo Starting Rental Wheels Car Rental Web Application
echo ===================================================
echo Backend API:  http://127.0.0.1:5000/api
echo Frontend Web: http://127.0.0.1:8000/index.html
echo ===================================================

if exist venv\Scripts\python.exe (
    set PY=venv\Scripts\python.exe
) else (
    set PY=python
)

start "Rental Wheels Backend" cmd /k "%PY% backend/run.py"
start "Rental Wheels Frontend" cmd /k "%PY% -m http.server 8000 --directory frontend"

timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000/index.html

echo Application successfully launched!
