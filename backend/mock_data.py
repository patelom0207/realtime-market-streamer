"""Mock data generator for testing when Binance API is unavailable."""

import random
import time
import threading
import logging
from typing import Optional

from backend.store import MarketStore


logger = logging.getLogger(__name__)


class MockDataGenerator:
    """Generates realistic mock market data for testing."""

    def __init__(self, store: MarketStore, base_price: float = 96000.0):
        """Initialize the mock data generator.

        Args:
            store: MarketStore instance to update.
            base_price: Starting price for BTCUSDT.
        """
        self.store = store
        self.base_price = base_price
        self.current_price = base_price
        self.running = False
        self._thread: Optional[threading.Thread] = None

    def _generate_depth_update(self) -> None:
        """Generate a realistic order book depth update."""
        # Random walk for price movement
        price_change = random.uniform(-5, 5)
        self.current_price += price_change

        # Generate bids (below current price)
        bids = []
        for i in range(10):
            price = self.current_price - (i * random.uniform(0.5, 2.0))
            qty = random.uniform(0.1, 5.0)
            bids.append((round(price, 2), round(qty, 4)))

        # Generate asks (above current price)
        asks = []
        for i in range(10):
            price = self.current_price + (i * random.uniform(0.5, 2.0))
            qty = random.uniform(0.1, 5.0)
            asks.append((round(price, 2), round(qty, 4)))

        # Sort
        bids.sort(reverse=True, key=lambda x: x[0])
        asks.sort(key=lambda x: x[0])

        # Calculate metrics
        best_bid, bid_qty = bids[0]
        best_ask, ask_qty = asks[0]
        mid_price = (best_bid + best_ask) / 2.0
        spread = best_ask - best_bid

        # Top-5 imbalance
        top_bids = bids[:5]
        top_asks = asks[:5]
        bid_volume = sum(qty for _, qty in top_bids)
        ask_volume = sum(qty for _, qty in top_asks)
        total_volume = bid_volume + ask_volume
        imbalance = (bid_volume - ask_volume) / total_volume if total_volume > 0 else 0.0

        timestamp = time.time()

        # Update store
        self.store.update_book_metrics(
            best_bid=best_bid,
            best_ask=best_ask,
            mid_price=mid_price,
            spread=spread,
            imbalance=imbalance,
            timestamp=timestamp,
            bid_volume=bid_qty,
            ask_volume=ask_qty,
            top_bids=top_bids,
            top_asks=top_asks,
        )

    def _generate_trade(self) -> None:
        """Generate a realistic trade."""
        is_buy = random.choice([True, False])
        price = self.current_price + random.uniform(-2, 2)
        qty = random.uniform(0.01, 1.0)

        trade = {
            'price': round(price, 2),
            'qty': round(qty, 4),
            'time': time.time(),
            'is_buyer_maker': not is_buy,
            'side': 'BUY' if is_buy else 'SELL',
        }
        self.store.add_trade(trade)

    def _run(self) -> None:
        """Main loop for generating mock data."""
        logger.info("Mock data generator started")

        while self.running:
            try:
                # Generate depth update (every 100ms like Binance)
                self._generate_depth_update()

                # Generate trade (randomly, ~30% chance)
                if random.random() < 0.3:
                    self._generate_trade()

                time.sleep(0.1)  # 100ms updates

            except Exception as e:
                logger.error(f"Error generating mock data: {e}")
                time.sleep(1)

        logger.info("Mock data generator stopped")

    def start(self) -> None:
        """Start generating mock data in a background thread."""
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop generating mock data."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)


def start_mock_worker(store: MarketStore) -> MockDataGenerator:
    """Start the mock data generator.

    Args:
        store: MarketStore instance to update.

    Returns:
        MockDataGenerator instance.
    """
    generator = MockDataGenerator(store)
    generator.start()
    return generator
