"""Streamlit dashboard for real-time market data visualization."""

import os
import time
import streamlit as st
import pandas as pd
from datetime import datetime

from backend.store import MarketStore
from backend.stream_worker import start_worker


# Page configuration
st.set_page_config(
    page_title="Real-Time Market Streamer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'store' not in st.session_state:
    # Check if mock mode is requested via environment variable
    use_mock = os.getenv('USE_MOCK_DATA', 'false').lower() in ('true', '1', 'yes')

    st.session_state.store = MarketStore(max_metrics=1000, max_trades=50)
    st.session_state.worker_thread = start_worker(
        st.session_state.store,
        symbol="btcusdt",
        use_mock=use_mock
    )
    st.session_state.start_time = time.time()
    st.session_state.is_mock_mode = use_mock

store = st.session_state.store


def format_number(value, decimals=2):
    """Format number for display."""
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def render_dashboard():
    """Render the main dashboard."""

    st.title("📈 Real-Time Market Data Streamer")

    # Show data source
    if st.session_state.get('is_mock_mode', False):
        st.caption("🎲 DEMO MODE - Showing simulated market data for BTCUSDT")
        st.warning("⚠️ Binance WebSocket is not available in your region (HTTP 451). Using mock data for demonstration.", icon="⚠️")
    else:
        st.caption("Live data from Binance - BTCUSDT")

    # Get current snapshot
    snapshot = store.snapshot()

    # Check if we have data
    if snapshot['data_points'] == 0:
        st.info("🔄 Connecting to Binance WebSocket... Waiting for data...")
        st.caption("This usually takes 5-15 seconds. If no data appears after 30 seconds, check your internet connection.")
        time.sleep(2)
        st.rerun()
        return

    # Metrics row
    st.subheader("Current Market Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Best Bid",
            value=format_number(snapshot['best_bid'], 2),
            delta=f"Vol: {format_number(snapshot['bid_volume'], 4)}"
        )

    with col2:
        st.metric(
            label="Best Ask",
            value=format_number(snapshot['best_ask'], 2),
            delta=f"Vol: {format_number(snapshot['ask_volume'], 4)}"
        )

    with col3:
        st.metric(
            label="Mid Price",
            value=format_number(snapshot['current_mid'], 2)
        )

    with col4:
        st.metric(
            label="Spread",
            value=format_number(snapshot['current_spread'], 2),
            delta=f"{format_number(snapshot['current_spread'] / snapshot['current_mid'] * 100, 4)}%" if snapshot['current_mid'] else "N/A"
        )

    with col5:
        imbalance = snapshot['current_imbalance']
        imbalance_pct = imbalance * 100 if imbalance is not None else None
        st.metric(
            label="Imbalance",
            value=format_number(imbalance_pct, 2) + "%" if imbalance_pct is not None else "N/A",
            delta="Buy pressure" if imbalance and imbalance > 0 else "Sell pressure" if imbalance else None
        )

    # Mid price chart
    st.subheader("Mid Price History")

    if len(snapshot['mid_prices']) > 0:
        chart_df = pd.DataFrame({
            'Time': [datetime.fromtimestamp(ts) for ts in snapshot['timestamps']],
            'Mid Price': snapshot['mid_prices']
        })
        st.line_chart(chart_df.set_index('Time'), use_container_width=True)
    else:
        st.info("Building chart... waiting for more data points.")

    # Two column layout for order book and trades
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Order Book Snapshot")

        if snapshot['top_bids'] and snapshot['top_asks']:
            # Create order book table
            book_data = []

            # Show top asks in reverse order (highest to lowest)
            for price, qty in reversed(snapshot['top_asks']):
                book_data.append({
                    'Side': 'ASK',
                    'Price': format_number(price, 2),
                    'Quantity': format_number(qty, 4)
                })

            # Add a separator
            book_data.append({
                'Side': '---',
                'Price': '---',
                'Quantity': '---'
            })

            # Show top bids (highest to lowest)
            for price, qty in snapshot['top_bids']:
                book_data.append({
                    'Side': 'BID',
                    'Price': format_number(price, 2),
                    'Quantity': format_number(qty, 4)
                })

            book_df = pd.DataFrame(book_data)

            # Color code rows
            def highlight_side(row):
                if row['Side'] == 'ASK':
                    return ['background-color: #ffebee'] * len(row)
                elif row['Side'] == 'BID':
                    return ['background-color: #e8f5e9'] * len(row)
                else:
                    return ['background-color: white'] * len(row)

            st.dataframe(
                book_df.style.apply(highlight_side, axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Waiting for order book data...")

    with col_right:
        st.subheader("Recent Trades")

        if snapshot['recent_trades']:
            trades_data = []
            for trade in snapshot['recent_trades'][:20]:  # Show last 20 trades
                trades_data.append({
                    'Time': datetime.fromtimestamp(trade['time']).strftime('%H:%M:%S'),
                    'Side': trade['side'],
                    'Price': format_number(trade['price'], 2),
                    'Quantity': format_number(trade['qty'], 4)
                })

            trades_df = pd.DataFrame(trades_data)

            # Color code by side
            def highlight_trade_side(row):
                if row['Side'] == 'BUY':
                    return ['background-color: #e8f5e9'] * len(row)
                else:
                    return ['background-color: #ffebee'] * len(row)

            st.dataframe(
                trades_df.style.apply(highlight_trade_side, axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Waiting for trade data...")

    # Footer with stats
    st.divider()

    footer_col1, footer_col2, footer_col3 = st.columns(3)

    with footer_col1:
        st.caption(f"📊 Data Points: {snapshot['data_points']}")

    with footer_col2:
        if snapshot['last_update']:
            elapsed = time.time() - snapshot['last_update']
            st.caption(f"🕐 Last Update: {elapsed:.1f}s ago")
        else:
            st.caption("🕐 Last Update: N/A")

    with footer_col3:
        uptime = time.time() - st.session_state.start_time
        minutes = int(uptime // 60)
        seconds = int(uptime % 60)
        st.caption(f"⏱️ Uptime: {minutes}m {seconds}s")


# Main loop
def main():
    """Main application loop."""

    # Create placeholder for dynamic updates
    dashboard_placeholder = st.empty()

    # Update loop
    while True:
        with dashboard_placeholder.container():
            render_dashboard()

        # Wait before next update
        time.sleep(0.8)


if __name__ == "__main__":
    main()
