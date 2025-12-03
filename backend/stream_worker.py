"""WebSocket client for streaming live market data from Binance."""

import asyncio
import json
import logging
import threading
import time
from typing import Optional, Dict, Any, List
import websockets

from backend.store import MarketStore


# Configuration
SYMBOL = "btcusdt"  # Lowercase for Binance streams
TOP_N = 5  # Number of top levels to track
RECONNECT_BASE_DELAY = 1.0  # Initial reconnect delay in seconds
RECONNECT_MAX_DELAY = 30.0  # Maximum reconnect delay in seconds
RECONNECT_MULTIPLIER = 2.0  # Exponential backoff multiplier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BinanceStreamClient:
    """Async WebSocket client for Binance public market data streams."""

    def __init__(self, store: MarketStore, symbol: str = SYMBOL):
        """Initialize the stream client.

        Args:
            store: MarketStore instance to update with incoming data.
            symbol: Trading symbol (lowercase, e.g., 'btcusdt').
        """
        self.store = store
        self.symbol = symbol.lower()
        self.ws_url = self._build_stream_url()
        self.running = False
        self._reconnect_delay = RECONNECT_BASE_DELAY

    def _build_stream_url(self) -> str:
        """Build the combined WebSocket stream URL.

        Returns:
            WebSocket URL for depth and trade streams.
        """
        base_url = "wss://stream.binance.com:9443/stream"
        streams = f"{self.symbol}@depth@100ms/{self.symbol}@trade"
        return f"{base_url}?streams={streams}"

    async def connect_and_stream(self) -> None:
        """Connect to Binance WebSocket and process messages.

        Implements automatic reconnection with exponential backoff.
        """
        self.running = True

        while self.running:
            try:
                logger.info(f"Connecting to Binance WebSocket: {self.ws_url}")
                async with websockets.connect(self.ws_url) as websocket:
                    logger.info("Connected successfully")
                    self._reconnect_delay = RECONNECT_BASE_DELAY  # Reset delay on success

                    while self.running:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=60.0  # Timeout to detect stale connections
                            )
                            await self._process_message(message)

                        except asyncio.TimeoutError:
                            logger.warning("No message received in 60s, checking connection...")
                            # Send a ping to check if connection is alive
                            try:
                                pong = await websocket.ping()
                                await asyncio.wait_for(pong, timeout=10)
                            except Exception:
                                logger.error("Connection appears dead, reconnecting...")
                                break

                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            break

            except Exception as e:
                if self.running:
                    logger.error(f"Connection error: {e}")
                    logger.info(f"Reconnecting in {self._reconnect_delay:.1f} seconds...")
                    await asyncio.sleep(self._reconnect_delay)

                    # Exponential backoff
                    self._reconnect_delay = min(
                        self._reconnect_delay * RECONNECT_MULTIPLIER,
                        RECONNECT_MAX_DELAY
                    )
                else:
                    break

        logger.info("Stream worker stopped")

    async def _process_message(self, message: str) -> None:
        """Process a WebSocket message.

        Args:
            message: Raw JSON message from WebSocket.
        """
        try:
            data = json.loads(message)

            # Binance combined stream format: {"stream": "...", "data": {...}}
            if 'stream' not in data or 'data' not in data:
                return

            stream_name = data['stream']
            stream_data = data['data']

            if 'depth' in stream_name:
                self._process_depth_update(stream_data)
            elif 'trade' in stream_name:
                self._process_trade_update(stream_data)

        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {message[:100]}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _process_depth_update(self, data: Dict[str, Any]) -> None:
        """Process order book depth update.

        Args:
            data: Depth update data from Binance.
        """
        try:
            # Extract bids and asks
            # Format: [["price", "qty"], ...]
            bids = [(float(p), float(q)) for p, q in data.get('bids', [])]
            asks = [(float(p), float(q)) for p, q in data.get('asks', [])]

            if not bids or not asks:
                return

            # Sort to ensure best prices
            bids.sort(reverse=True, key=lambda x: x[0])  # Highest bid first
            asks.sort(key=lambda x: x[0])  # Lowest ask first

            # Calculate metrics
            best_bid, bid_qty = bids[0]
            best_ask, ask_qty = asks[0]
            mid_price = (best_bid + best_ask) / 2.0
            spread = best_ask - best_bid

            # Calculate top-N imbalance
            top_bids = bids[:TOP_N]
            top_asks = asks[:TOP_N]

            bid_volume = sum(qty for _, qty in top_bids)
            ask_volume = sum(qty for _, qty in top_asks)

            # Imbalance ratio: (bid_vol - ask_vol) / (bid_vol + ask_vol)
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

        except (KeyError, ValueError, IndexError) as e:
            logger.error(f"Error processing depth data: {e}")

    def _process_trade_update(self, data: Dict[str, Any]) -> None:
        """Process trade update.

        Args:
            data: Trade data from Binance.
        """
        try:
            trade = {
                'price': float(data['p']),
                'qty': float(data['q']),
                'time': data['T'] / 1000.0,  # Convert ms to seconds
                'is_buyer_maker': data['m'],  # True if buyer is maker (sell)
                'side': 'SELL' if data['m'] else 'BUY',
            }
            self.store.add_trade(trade)

        except (KeyError, ValueError) as e:
            logger.error(f"Error processing trade data: {e}")

    def stop(self) -> None:
        """Stop the stream worker."""
        self.running = False


def start_worker(store: MarketStore, symbol: str = SYMBOL, use_mock: bool = False) -> threading.Thread:
    """Start the WebSocket stream worker in a background thread.

    Args:
        store: MarketStore instance to update.
        symbol: Trading symbol to stream.
        use_mock: If True, use mock data instead of real WebSocket.

    Returns:
        Thread object running the worker.
    """
    # Check if mock mode is requested or auto-detect HTTP 451
    if use_mock:
        from backend.mock_data import start_mock_worker
        logger.warning("Using MOCK DATA mode - generating simulated market data")
        start_mock_worker(store)
        return threading.Thread(target=lambda: None, daemon=True)

    client = BinanceStreamClient(store, symbol)

    def run_async_loop():
        """Run the async event loop in a separate thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        http_451_count = 0

        try:
            # Try to connect
            async def try_connect():
                nonlocal http_451_count
                try:
                    await client.connect_and_stream()
                except Exception as e:
                    # Detect HTTP 451 (geo-blocking)
                    if "451" in str(e):
                        http_451_count += 1
                        if http_451_count >= 3:
                            logger.error("Binance WebSocket blocked (HTTP 451) - switching to MOCK DATA mode")
                            from backend.mock_data import start_mock_worker
                            start_mock_worker(store)
                            return
                    raise

            loop.run_until_complete(try_connect())
        finally:
            loop.close()

    thread = threading.Thread(target=run_async_loop, daemon=True)
    thread.start()
    logger.info(f"Stream worker started for {symbol.upper()}")

    return thread
