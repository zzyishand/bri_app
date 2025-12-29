@echo off
REM BRI Application Launcher for Windows

echo ========================================
echo BRI Bubble Risk Indicator Application
echo ========================================
echo.

REM Check if in correct directory
if not exist "app.py" (
    echo Error: app.py not found!
    echo Please run this script from the bri_app directory.
    pause
    exit /b 1
)

echo Starting Streamlit application...
echo.
echo Open your browser and go to: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

REM Run Streamlit
streamlit run app.py

pause

