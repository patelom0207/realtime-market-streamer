"""Thread-safe in-memory store for market data."""

import threading
from collections import deque
from typing import Dict, List, Any, Optional
import time


class MarketStore:
    """Thread-safe in-memory store for live market data.

    Maintains rolling windows of metrics and recent trades.
    All public methods are thread-safe.
    """

    def __init__(self, max_metrics: int = 1000, max_trades: int = 100):
        """Initialize the market store.

        Args:
            max_metrics: Maximum number of metric data points to keep.
            max_trades: Maximum number of recent trades to keep.
        """
        self._lock = threading.Lock()

        # Time series data (deques for efficient append/pop)
        self.mid_prices: deque = deque(maxlen=max_metrics)
        self.spreads: deque = deque(maxlen=max_metrics)
        self.imbalances: deque = deque(maxlen=max_metrics)
        self.timestamps: deque = deque(maxlen=max_metrics)

        # Recent trades
        self.recent_trades: deque = deque(maxlen=max_trades)

        # Current book snapshot
        self.best_bid: Optional[float] = None
        self.best_ask: Optional[float] = None
        self.bid_volume: Optional[float] = None
        self.ask_volume: Optional[float] = None
        self.top_bids: List[tuple] = []  # [(price, qty), ...]
        self.top_asks: List[tuple] = []  # [(price, qty), ...]

    def update_book_metrics(
        self,
        best_bid: float,
        best_ask: float,
        mid_price: float,
        spread: float,
        imbalance: float,
        timestamp: float,
        bid_volume: float = 0.0,
        ask_volume: float = 0.0,
        top_bids: Optional[List[tuple]] = None,
        top_asks: Optional[List[tuple]] = None,
    ) -> None:
        """Update order book metrics.

        Args:
            best_bid: Best bid price.
            best_ask: Best ask price.
            mid_price: Mid price.
            spread: Bid-ask spread.
            imbalance: Order book imbalance ratio.
            timestamp: Event timestamp.
            bid_volume: Total bid volume at best level.
            ask_volume: Total ask volume at best level.
            top_bids: List of (price, qty) tuples for top bid levels.
            top_asks: List of (price, qty) tuples for top ask levels.
        """
        with self._lock:
            self.best_bid = best_bid
            self.best_ask = best_ask
            self.bid_volume = bid_volume
            self.ask_volume = ask_volume

            if top_bids is not None:
                self.top_bids = top_bids
            if top_asks is not None:
                self.top_asks = top_asks

            self.mid_prices.append(mid_price)
            self.spreads.append(spread)
            self.imbalances.append(imbalance)
            self.timestamps.append(timestamp)

    def add_trade(self, trade_data: Dict[str, Any]) -> None:
        """Add a new trade to recent trades.

        Args:
            trade_data: Dictionary containing trade information.
                Expected keys: price, qty, time, is_buyer_maker.
        """
        with self._lock:
            self.recent_trades.append(trade_data)

    def snapshot(self) -> Dict[str, Any]:
        """Get a thread-safe snapshot of current market state.

        Returns:
            Dictionary containing all market data as plain Python lists/dicts.
            Safe to use across threads and from Streamlit.
        """
        with self._lock:
            return {
                # Current metrics
                'best_bid': self.best_bid,
                'best_ask': self.best_ask,
                'bid_volume': self.bid_volume,
                'ask_volume': self.ask_volume,
                'current_mid': self.mid_prices[-1] if self.mid_prices else None,
                'current_spread': self.spreads[-1] if self.spreads else None,
                'current_imbalance': self.imbalances[-1] if self.imbalances else None,

                # Time series (convert deque to list for safety)
                'mid_prices': list(self.mid_prices),
                'spreads': list(self.spreads),
                'imbalances': list(self.imbalances),
                'timestamps': list(self.timestamps),

                # Order book levels
                'top_bids': list(self.top_bids),
                'top_asks': list(self.top_asks),

                # Recent trades (most recent first)
                'recent_trades': list(reversed(self.recent_trades)),

                # Metadata
                'data_points': len(self.mid_prices),
                'last_update': self.timestamps[-1] if self.timestamps else None,
            }

    def clear(self) -> None:
        """Clear all stored data (useful for testing)."""
        with self._lock:
            self.mid_prices.clear()
            self.spreads.clear()
            self.imbalances.clear()
            self.timestamps.clear()
            self.recent_trades.clear()
            self.best_bid = None
            self.best_ask = None
            self.bid_volume = None
            self.ask_volume = None
            self.top_bids = []
            self.top_asks = []
