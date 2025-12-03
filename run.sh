#!/bin/bash
# Run the Real-Time Market Streamer dashboard

export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run frontend/dashboard.py --server.headless=true
