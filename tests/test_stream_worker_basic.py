"""Basic smoke tests for stream worker message parsing."""

import json
import pytest
from backend.store import MarketStore
from backend.stream_worker import BinanceStreamClient


class TestStreamWorkerBasic:
    """Basic tests for stream worker parsing logic."""

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        store = MarketStore()
        client = BinanceStreamClient(store, symbol="btcusdt")

        assert client.symbol == "btcusdt"
        assert client.store is store
        assert "btcusdt@depth" in client.ws_url
        assert "btcusdt@trade" in client.ws_url

    def test_process_depth_message(self):
        """Test processing a depth update message."""
        store = MarketStore()
        client = BinanceStreamClient(store)

        # Sample depth message (simplified Binance format)
        sample_message = {
            "stream": "btcusdt@depth@100ms",
            "data": {
                "bids": [
                    ["50000.00", "1.5"],
                    ["49999.00", "2.0"],
                    ["49998.00", "1.0"],
                    ["49997.00", "0.8"],
                    ["49996.00", "1.2"]
                ],
                "asks": [
                    ["50001.00", "1.2"],
                    ["50002.00", "1.8"],
                    ["50003.00", "0.9"],
                    ["50004.00", "1.5"],
                    ["50005.00", "2.0"]
                ]
            }
        }

        # Process the depth update
        client._process_depth_update(sample_message["data"])

        # Check that store was updated
        snapshot = store.snapshot()

        assert snapshot['best_bid'] == 50000.00
        assert snapshot['best_ask'] == 50001.00
        assert snapshot['current_mid'] == 50000.50
        assert snapshot['current_spread'] == 1.0
        assert snapshot['data_points'] == 1

        # Check top levels
        assert len(snapshot['top_bids']) == 5
        assert len(snapshot['top_asks']) == 5
        assert snapshot['top_bids'][0] == (50000.00, 1.5)
        assert snapshot['top_asks'][0] == (50001.00, 1.2)

    def test_process_trade_message(self):
        """Test processing a trade message."""
        store = MarketStore()
        client = BinanceStreamClient(store)

        # Sample trade message (Binance format)
        sample_message = {
            "stream": "btcusdt@trade",
            "data": {
                "p": "50000.50",  # Price
                "q": "0.5",       # Quantity
                "T": 1699999999000,  # Trade time in ms
                "m": False        # Is buyer maker (False = buy)
            }
        }

        # Process the trade
        client._process_trade_update(sample_message["data"])

        # Check that trade was added
        snapshot = store.snapshot()

        assert len(snapshot['recent_trades']) == 1
        trade = snapshot['recent_trades'][0]
        assert trade['price'] == 50000.50
        assert trade['qty'] == 0.5
        assert trade['side'] == 'BUY'
        assert trade['is_buyer_maker'] is False

    def test_imbalance_calculation(self):
        """Test that order book imbalance is calculated correctly."""
        store = MarketStore()
        client = BinanceStreamClient(store)

        # More bids than asks (buy pressure)
        sample_data = {
            "bids": [
                ["50000.00", "10.0"],
                ["49999.00", "8.0"],
                ["49998.00", "6.0"],
                ["49997.00", "4.0"],
                ["49996.00", "2.0"]
            ],
            "asks": [
                ["50001.00", "2.0"],
                ["50002.00", "2.0"],
                ["50003.00", "2.0"],
                ["50004.00", "2.0"],
                ["50005.00", "2.0"]
            ]
        }

        client._process_depth_update(sample_data)
        snapshot = store.snapshot()

        # Bid volume: 10+8+6+4+2 = 30
        # Ask volume: 2+2+2+2+2 = 10
        # Imbalance: (30-10)/(30+10) = 20/40 = 0.5
        assert abs(snapshot['current_imbalance'] - 0.5) < 0.01

    def test_empty_book_handling(self):
        """Test that empty order book is handled gracefully."""
        store = MarketStore()
        client = BinanceStreamClient(store)

        # Empty book
        sample_data = {
            "bids": [],
            "asks": []
        }

        # Should not crash
        client._process_depth_update(sample_data)

        snapshot = store.snapshot()
        assert snapshot['data_points'] == 0

    def test_url_construction(self):
        """Test WebSocket URL is constructed correctly."""
        store = MarketStore()
        client = BinanceStreamClient(store, symbol="ETHUSDT")

        assert client.symbol == "ethusdt"  # Should be lowercase
        assert "ethusdt@depth@100ms" in client.ws_url
        assert "ethusdt@trade" in client.ws_url
        assert client.ws_url.startswith("wss://stream.binance.com:9443/stream")
