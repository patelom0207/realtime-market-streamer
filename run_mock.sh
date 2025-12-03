#!/bin/bash
# Run the Real-Time Market Streamer dashboard with MOCK DATA
# Use this if Binance WebSocket is blocked in your region

export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export USE_MOCK_DATA=true

echo "Starting dashboard with MOCK DATA mode..."
streamlit run frontend/dashboard.py --server.headless=true
