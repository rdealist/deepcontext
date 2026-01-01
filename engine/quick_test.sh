#!/bin/bash

# Quick test script for RAG system
# This script runs all tests and demonstrates the system

set -e

echo "========================================"
echo "  🧪 RAG System Quick Test"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import lancedb" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "   Please run: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Environment ready"
echo ""

# Run test suite
echo "========================================"
echo "  Running Test Suite"
echo "========================================"
echo ""
python test_rag.py

# Check if tests passed
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Tests failed! Please check the output above."
    exit 1
fi

echo ""
echo "========================================"
echo "  Running Demo Example"
echo "========================================"
echo ""
python example.py

echo ""
echo "========================================"
echo "  ✅ All Tests Complete!"
echo "========================================"
echo ""
echo "To start the FastAPI server:"
echo "  uvicorn main:app --reload --host 127.0.0.1 --port 8000"
echo ""
echo "Then test the API:"
echo "  curl http://localhost:8000/health"
echo ""
