#!/bin/bash
# Run the Real-Time Market Streamer dashboard

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# If Binance is blocked in your region, use mock data mode:
# export USE_MOCK_DATA=true

streamlit run frontend/dashboard.py --server.headless=true
