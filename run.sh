#!/bin/bash
# UCLA Women's Basketball RAG Analytics - Quick Start Script

echo "🏀 UCLA Women's Basketball RAG Analytics"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create a .env file based on .env.example"
    echo "   Copy .env.example to .env and add your API keys"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if database exists
if [ ! -f data/ucla_wbb.db ]; then
    echo "❌ Error: Database file not found at data/ucla_wbb.db"
    echo "   Please ensure the database file exists"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "🚀 Starting Flask backend..."
echo "📍 Backend will be available at: http://localhost:5001"
echo ""
echo "💡 To start the React frontend, open a new terminal and run:"
echo "   cd frontend && npm install && npm run dev"
echo ""

# Run the application
python3 app.py

