# Quick Start Guide

## Prerequisites
- Python 3.10+ (Note: Python 3.14 may have issues with pyarrow. Use Python 3.11 or 3.12 if available)
- Internet connection for Binance WebSocket

## Installation (5 minutes)

```bash
# 1. Navigate to project directory
cd realtime-market-streamer

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install --upgrade pip
pip install websockets pytest
pip install --only-binary=:all: pandas  # Pre-built wheels only
pip install --no-deps streamlit
pip install altair blinker cachetools click packaging pillow protobuf requests rich tenacity toml tornado typing-extensions validators watchdog gitpython pydeck
pip install "altair<6,>=4.0"

# Note: pyarrow may fail on Python 3.14. Streamlit will work without it for this project.
```

## Run the Application

```bash
# Make sure you're in the project root with venv activated
./run.sh

# Or manually:
export PYTHONPATH="$(pwd)"
streamlit run frontend/dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`.

## What You Should See

Within 10-30 seconds, you should see:
- ✅ Real-time price updates for BTCUSDT
- ✅ Live metrics: Best Bid, Best Ask, Mid Price, Spread, Imbalance
- ✅ A growing line chart of mid prices
- ✅ Recent trades table with buy/sell indicators
- ✅ Order book snapshot showing top 5 bids and asks

## Run Tests

```bash
source venv/bin/activate
export PYTHONPATH="$(pwd)"
pytest -v
```

You should see:
```
14 passed in 0.14s
```

## Troubleshooting

### No data after 30+ seconds
- Check internet connection
- Verify Binance is accessible (not blocked by firewall/VPN)
- Look for error messages in terminal

### Import errors
- Ensure PYTHONPATH is set: `export PYTHONPATH="$(pwd)"`
- Verify venv is activated: `which python3` should show the venv path

### pyarrow installation fails
- This is expected on Python 3.14
- Streamlit will work without pyarrow for this project
- Alternatively, use Python 3.11 or 3.12

## Next Steps

Once running, explore:
- Watch the mid price chart grow over time
- Observe imbalance changes (positive = buy pressure, negative = sell pressure)
- See live trades appear in the table
- Note the automatic reconnection if you lose internet briefly

## Stopping the Application

Press `Ctrl+C` in the terminal to stop the Streamlit server.

## Architecture

```
Browser ←→ Streamlit Dashboard ←→ MarketStore ←→ WebSocket Client ←→ Binance API
```

The WebSocket client runs in a background thread, continuously updating the MarketStore, which the dashboard polls every 0.8 seconds for display.
