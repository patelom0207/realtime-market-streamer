# 🚀 Start Your Real-Time Market Streamer

## Quick Start (30 seconds)

### Option 1: One Command (Recommended)

Open your terminal and run:

```bash
cd /Users/patelom0207/Projects/realtime-market-streamer
./run_mock.sh
```

Then open your browser to: **http://localhost:8501**

### Option 2: Step by Step

```bash
# 1. Navigate to the project
cd /Users/patelom0207/Projects/realtime-market-streamer

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run the dashboard with mock data
export PYTHONPATH="$(pwd)"
export USE_MOCK_DATA=true
streamlit run frontend/dashboard.py
```

Your browser will automatically open to **http://localhost:8501**

---

## What You'll See

Within seconds, you'll see a live dashboard with:

✅ **Real-time price updates** - Mid price chart growing over time
✅ **Live metrics** - Best Bid, Ask, Spread, Imbalance
✅ **Recent trades** - Color-coded buy/sell orders
✅ **Order book** - Top 5 bids and asks
✅ **Demo banner** - Showing you're in mock data mode

---

## Why Mock Mode?

Binance WebSocket is blocked in your region (HTTP 451). Mock mode generates realistic simulated market data that behaves exactly like real Binance data - perfect for:
- 📊 Demonstrations
- 🎓 Learning
- 🧪 Testing
- 📸 Screenshots for portfolio

---

## Troubleshooting

### Browser doesn't open automatically?
Manually go to: **http://localhost:8501**

### Port already in use?
```bash
# Kill existing process
pkill streamlit

# Try again
./run_mock.sh
```

### Still not working?
Run the verification test:
```bash
python3 test_mock.py
```

If this passes (it should!), the dashboard will work too.

---

## Next Steps

Once the dashboard is running:

1. **Watch the chart grow** - Mid price updates in real-time
2. **Check the metrics** - Spread, imbalance changing dynamically
3. **View recent trades** - Green (buy) and red (sell) orders
4. **Take screenshots** - Perfect for your portfolio/resume!

---

## Stop the Dashboard

Press **Ctrl+C** in the terminal where Streamlit is running.

---

**Need help?** All documentation is in [README.md](README.md)
