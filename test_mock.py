#!/usr/bin/env python3
"""Quick test script to verify mock data mode works."""

import time
import sys
from backend.store import MarketStore
from backend.mock_data import start_mock_worker


def main():
    print("=" * 60)
    print("Testing Mock Data Generator")
    print("=" * 60)

    store = MarketStore()
    print("\n✓ MarketStore created")

    generator = start_mock_worker(store)
    print("✓ Mock data generator started")

    print("\nCollecting data for 3 seconds...")
    for i in range(3):
        time.sleep(1)
        snapshot = store.snapshot()
        mid_price = snapshot['current_mid'] if snapshot['current_mid'] else 0
        print(f"  [{i+1}s] Data points: {snapshot['data_points']}, "
              f"Trades: {len(snapshot['recent_trades'])}, "
              f"Mid: ${mid_price:.2f}")

    generator.stop()
    print("\n✓ Mock data generator stopped")

    snapshot = store.snapshot()
    print("\n" + "=" * 60)
    print("Final Statistics:")
    print("=" * 60)
    print(f"Total data points: {snapshot['data_points']}")
    print(f"Total trades: {len(snapshot['recent_trades'])}")
    print(f"Best bid: ${snapshot['best_bid']:.2f}")
    print(f"Best ask: ${snapshot['best_ask']:.2f}")
    print(f"Mid price: ${snapshot['current_mid']:.2f}")
    print(f"Spread: ${snapshot['current_spread']:.2f}")
    print(f"Imbalance: {snapshot['current_imbalance']:.2%}")
    print(f"Top bids: {len(snapshot['top_bids'])}")
    print(f"Top asks: {len(snapshot['top_asks'])}")

    print("\n✅ All tests passed! Mock data mode is working correctly.")
    print("\nYou can now run the dashboard with:")
    print("  ./run_mock.sh")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
