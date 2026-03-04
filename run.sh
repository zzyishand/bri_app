#!/bin/bash
# BRI Application Launcher for Linux/Mac

echo "========================================"
echo "BRI Bubble Risk Indicator Application"
echo "========================================"
echo ""

# Check if in correct directory
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found!"
    echo "Please run this script from the bri_app directory."
    exit 1
fi

echo "Starting Streamlit application..."
echo ""
echo "Open your browser and go to: http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

# Run Streamlit
streamlit run app.py

