#!/bin/bash

# Kill any existing Streamlit processes
pkill -9 streamlit 2>/dev/null
sleep 2

# Navigate to project directory
cd /Users/patelom0207/Projects/realtime-market-streamer

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="$(pwd)"
export USE_MOCK_DATA=true

# Clear the terminal
clear

echo "============================================================"
echo "  REAL-TIME MARKET STREAMER - STARTING..."
echo "============================================================"
echo ""
echo "Starting Streamlit dashboard with mock data..."
echo ""

# Run Streamlit
streamlit run frontend/dashboard.py --server.port 8501

# This will show you the URL when it starts:
# Local URL: http://localhost:8501
