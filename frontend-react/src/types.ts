/**
 * TypeScript type definitions for real-time market data
 */

export interface Trade {
  time: number;
  price: number;
  qty: number;
  side: 'BUY' | 'SELL';
}

export interface OrderBookLevel {
  price: number;
  quantity: number;
}

export interface MarketSnapshot {
  // Current metrics
  best_bid: number | null;
  best_ask: number | null;
  bid_volume: number | null;
  ask_volume: number | null;
  current_mid: number | null;
  current_spread: number | null;
  current_imbalance: number | null;

  // Time series data
  mid_prices: number[];
  spreads: number[];
  imbalances: number[];
  timestamps: number[];

  // Recent trades
  recent_trades: Trade[];

  // Order book snapshot
  top_bids: [number, number][]; // [price, quantity][]
  top_asks: [number, number][]; // [price, quantity][]

  // Metadata
  data_points: number;
  last_update: number | null;
}

export interface ChartDataPoint {
  index: number;
  price: number;
}

export interface OrderBookDisplayLevel {
  side: 'BID' | 'ASK' | 'SEPARATOR';
  price: string;
  quantity: string;
}

export interface TradeDisplay {
  time: string;
  side: 'BUY' | 'SELL';
  price: string;
  quantity: string;
}
