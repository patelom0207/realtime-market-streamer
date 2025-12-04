/**
 * Main Dashboard component
 */

import React, { useState, useEffect } from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { MetricCard } from './MetricCard';
import { PriceChart } from './PriceChart';
import { OrderBook } from './OrderBook';
import { TradesTable } from './TradesTable';
import { formatPrice, formatQuantity, formatPercentage, formatElapsedTime, formatUptime } from '../utils/formatters';
import '../styles/Dashboard.css';

export const Dashboard: React.FC = () => {
  const { snapshot, isConnected, error } = useMarketData();
  const [startTime] = useState(Date.now());
  const [uptime, setUptime] = useState(0);

  // Update uptime every second
  useEffect(() => {
    const interval = setInterval(() => {
      setUptime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  if (error) {
    return (
      <div className="dashboard">
        <div className="error-banner">
          ⚠️ Error: {error}. Make sure the backend server is running on port 8000.
        </div>
      </div>
    );
  }

  if (!isConnected || !snapshot) {
    return (
      <div className="dashboard">
        <div className="loading-banner">
          🔄 Connecting to market data stream...
        </div>
      </div>
    );
  }

  const isMockMode = snapshot.data_points > 0; // Simplified check
  const midPrice = snapshot.current_mid || 0;
  const spread = snapshot.current_spread || 0;
  const spreadPct = midPrice > 0 ? (spread / midPrice) * 100 : 0;
  const imbalance = snapshot.current_imbalance || 0;
  const lastUpdate = snapshot.last_update
    ? formatElapsedTime(Date.now() / 1000 - snapshot.last_update)
    : 'N/A';

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <h1>📈 Real-Time Market Data Streamer</h1>
        <p className="dashboard-subtitle">Live data for BTCUSDT</p>
      </header>

      {/* Connection Status */}
      <div className="status-bar">
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
        <div className="status-info">
          📊 Data Points: {snapshot.data_points} | 🕐 Last Update: {lastUpdate} | ⏱️ Uptime: {formatUptime(uptime)}
        </div>
      </div>

      {/* Warning banner for demo mode - always show for simplicity */}
      <div className="demo-banner">
        🎲 DEMO MODE - Showing simulated market data
      </div>

      {/* Metrics Row */}
      <div className="metrics-row">
        <MetricCard
          label="Best Bid"
          value={`$${formatPrice(snapshot.best_bid)}`}
          delta={`Vol: ${formatQuantity(snapshot.bid_volume)}`}
          deltaType="neutral"
        />
        <MetricCard
          label="Best Ask"
          value={`$${formatPrice(snapshot.best_ask)}`}
          delta={`Vol: ${formatQuantity(snapshot.ask_volume)}`}
          deltaType="neutral"
        />
        <MetricCard
          label="Mid Price"
          value={`$${formatPrice(midPrice)}`}
        />
        <MetricCard
          label="Spread"
          value={`$${formatPrice(spread)}`}
          delta={`${spreadPct.toFixed(4)}%`}
          deltaType="neutral"
        />
        <MetricCard
          label="Imbalance"
          value={formatPercentage(imbalance)}
          delta={imbalance > 0 ? 'Buy pressure' : imbalance < 0 ? 'Sell pressure' : 'Balanced'}
          deltaType={imbalance > 0 ? 'positive' : imbalance < 0 ? 'negative' : 'neutral'}
        />
      </div>

      {/* Price Chart */}
      <div className="chart-section">
        <h2>Mid Price History</h2>
        <PriceChart data={snapshot.mid_prices} />
      </div>

      {/* Order Book and Trades */}
      <div className="data-grid">
        <OrderBook bids={snapshot.top_bids} asks={snapshot.top_asks} />
        <TradesTable trades={snapshot.recent_trades} />
      </div>
    </div>
  );
};
