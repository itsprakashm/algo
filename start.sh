#!/bin/bash

echo "Starting Algo Trading Platform..."
echo

echo "Starting Backend..."
cd backend
gnome-terminal --title="Backend" -- bash -c "python app.py; exec bash" &
cd ..

echo
echo "Starting Frontend..."
cd frontend
gnome-terminal --title="Frontend" -- bash -c "npm start; exec bash" &
cd ..

echo
echo "Platform is starting up..."
echo "Backend will be available at: http://localhost:5000"
echo "Frontend will be available at: http://localhost:3000"
echo
echo "Press Ctrl+C to stop all services"
echo

# Wait for user to stop
wait 