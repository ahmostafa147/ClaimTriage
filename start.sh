#!/bin/bash

# Claims Triage Pro - React Frontend + FastAPI Backend
echo "🎯 Starting Claims Triage Pro..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install fastapi uvicorn python-multipart

echo "🚀 Starting FastAPI backend..."
echo "📱 Open your browser to: http://localhost:8000"
echo "🎯 Claims Triage Pro is ready!"

# Start the FastAPI server
python3 api.py
