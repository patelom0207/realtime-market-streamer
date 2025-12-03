"""Unit tests for the MarketStore class."""

import time
import threading
import pytest
from backend.store import MarketStore


class TestMarketStore:
    """Test suite for MarketStore."""

    def test_initialization(self):
        """Test that MarketStore initializes correctly."""
        store = MarketStore(max_metrics=100, max_trades=50)

        assert len(store.mid_prices) == 0
        assert len(store.spreads) == 0
        assert len(store.imbalances) == 0
        assert len(store.timestamps) == 0
        assert len(store.recent_trades) == 0
        assert store.best_bid is None
        assert store.best_ask is None

    def test_update_book_metrics(self):
        """Test updating book metrics."""
        store = MarketStore()

        store.update_book_metrics(
            best_bid=50000.0,
            best_ask=50001.0,
            mid_price=50000.5,
            spread=1.0,
            imbalance=0.05,
            timestamp=time.time(),
            bid_volume=10.5,
            ask_volume=9.5,
        )

        assert store.best_bid == 50000.0
        assert store.best_ask == 50001.0
        assert len(store.mid_prices) == 1
        assert store.mid_prices[0] == 50000.5
        assert store.spreads[0] == 1.0
        assert store.imbalances[0] == 0.05

    def test_add_trade(self):
        """Test adding trades."""
        store = MarketStore()

        trade1 = {
            'price': 50000.0,
            'qty': 0.5,
            'time': time.time(),
            'is_buyer_maker': False,
            'side': 'BUY'
        }

        trade2 = {
            'price': 50001.0,
            'qty': 0.3,
            'time': time.time(),
            'is_buyer_maker': True,
            'side': 'SELL'
        }

        store.add_trade(trade1)
        store.add_trade(trade2)

        assert len(store.recent_trades) == 2
        assert store.recent_trades[0] == trade1
        assert store.recent_trades[1] == trade2

    def test_snapshot(self):
        """Test getting a snapshot of the store."""
        store = MarketStore()

        # Add some data
        ts = time.time()
        store.update_book_metrics(
            best_bid=50000.0,
            best_ask=50001.0,
            mid_price=50000.5,
            spread=1.0,
            imbalance=0.05,
            timestamp=ts,
        )

        trade = {
            'price': 50000.0,
            'qty': 0.5,
            'time': ts,
            'is_buyer_maker': False,
            'side': 'BUY'
        }
        store.add_trade(trade)

        # Get snapshot
        snapshot = store.snapshot()

        assert snapshot['best_bid'] == 50000.0
        assert snapshot['best_ask'] == 50001.0
        assert snapshot['current_mid'] == 50000.5
        assert snapshot['current_spread'] == 1.0
        assert snapshot['current_imbalance'] == 0.05
        assert len(snapshot['mid_prices']) == 1
        assert len(snapshot['recent_trades']) == 1
        assert snapshot['data_points'] == 1
        assert snapshot['last_update'] == ts

    def test_max_length_enforcement(self):
        """Test that deques respect max length."""
        store = MarketStore(max_metrics=3, max_trades=2)

        # Add more metrics than max
        for i in range(5):
            store.update_book_metrics(
                best_bid=50000.0 + i,
                best_ask=50001.0 + i,
                mid_price=50000.5 + i,
                spread=1.0,
                imbalance=0.05,
                timestamp=time.time() + i,
            )

        # Should only keep last 3
        assert len(store.mid_prices) == 3
        assert store.mid_prices[0] == 50002.5  # First kept value
        assert store.mid_prices[-1] == 50004.5  # Last value

        # Add more trades than max
        for i in range(4):
            store.add_trade({
                'price': 50000.0 + i,
                'qty': 0.5,
                'time': time.time() + i,
                'is_buyer_maker': False,
                'side': 'BUY'
            })

        # Should only keep last 2
        assert len(store.recent_trades) == 2

    def test_thread_safety(self):
        """Test that concurrent updates are thread-safe."""
        store = MarketStore()
        errors = []

        def update_metrics(thread_id: int):
            """Update metrics from a thread."""
            try:
                for i in range(100):
                    store.update_book_metrics(
                        best_bid=50000.0 + thread_id,
                        best_ask=50001.0 + thread_id,
                        mid_price=50000.5 + thread_id,
                        spread=1.0,
                        imbalance=0.05,
                        timestamp=time.time(),
                    )
                    time.sleep(0.001)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(e)

        def add_trades(thread_id: int):
            """Add trades from a thread."""
            try:
                for i in range(100):
                    store.add_trade({
                        'price': 50000.0 + thread_id,
                        'qty': 0.5,
                        'time': time.time(),
                        'is_buyer_maker': False,
                        'side': 'BUY'
                    })
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        def read_snapshot():
            """Read snapshots from a thread."""
            try:
                for i in range(100):
                    snapshot = store.snapshot()
                    assert isinstance(snapshot, dict)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Create multiple threads doing concurrent operations
        threads = []
        for i in range(3):
            threads.append(threading.Thread(target=update_metrics, args=(i,)))
            threads.append(threading.Thread(target=add_trades, args=(i,)))
        threads.append(threading.Thread(target=read_snapshot))

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Check no errors occurred
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Verify data integrity
        snapshot = store.snapshot()
        assert snapshot['data_points'] > 0
        assert len(snapshot['recent_trades']) > 0

    def test_clear(self):
        """Test clearing the store."""
        store = MarketStore()

        # Add some data
        store.update_book_metrics(
            best_bid=50000.0,
            best_ask=50001.0,
            mid_price=50000.5,
            spread=1.0,
            imbalance=0.05,
            timestamp=time.time(),
        )
        store.add_trade({
            'price': 50000.0,
            'qty': 0.5,
            'time': time.time(),
            'is_buyer_maker': False,
            'side': 'BUY'
        })

        # Clear
        store.clear()

        # Verify everything is cleared
        assert len(store.mid_prices) == 0
        assert len(store.recent_trades) == 0
        assert store.best_bid is None
        assert store.best_ask is None

        snapshot = store.snapshot()
        assert snapshot['data_points'] == 0
        assert snapshot['current_mid'] is None

    def test_snapshot_with_top_levels(self):
        """Test snapshot includes order book levels."""
        store = MarketStore()

        top_bids = [(50000.0, 1.5), (49999.0, 2.0), (49998.0, 1.0)]
        top_asks = [(50001.0, 1.2), (50002.0, 1.8), (50003.0, 0.9)]

        store.update_book_metrics(
            best_bid=50000.0,
            best_ask=50001.0,
            mid_price=50000.5,
            spread=1.0,
            imbalance=0.05,
            timestamp=time.time(),
            top_bids=top_bids,
            top_asks=top_asks,
        )

        snapshot = store.snapshot()

        assert snapshot['top_bids'] == top_bids
        assert snapshot['top_asks'] == top_asks
        assert len(snapshot['top_bids']) == 3
        assert len(snapshot['top_asks']) == 3
