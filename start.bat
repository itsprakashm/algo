@echo off
echo Starting Algo Trading Platform...
echo.

echo Starting Backend...
cd backend
start "Backend" cmd /k "python app.py"
cd ..

echo.
echo Starting Frontend...
cd frontend
start "Frontend" cmd /k "npm start"
cd ..

echo.
echo Platform is starting up...
echo Backend will be available at: http://localhost:5000
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to exit this script...
pause > nul 