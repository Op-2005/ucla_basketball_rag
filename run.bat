@echo off
REM UCLA Women's Basketball RAG Analytics - Quick Start Script (Windows)

echo 🏀 UCLA Women's Basketball RAG Analytics
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  Warning: .env file not found!
    echo 📝 Please create a .env file based on .env.example
    echo    Copy .env.example to .env and add your API keys
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

REM Check if database exists
if not exist data\ucla_wbb.db (
    echo ❌ Error: Database file not found at data\ucla_wbb.db
    echo    Please ensure the database file exists
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Virtual environment not found. Creating one...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
    echo ✅ Dependencies installed
)

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

echo.
echo 🚀 Starting Flask backend...
echo 📍 Backend will be available at: http://localhost:5001
echo.
echo 💡 To start the React frontend, open a new terminal and run:
echo    cd frontend ^&^& npm install ^&^& npm run dev
echo.

REM Run the application
python app.py

