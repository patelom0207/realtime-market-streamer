/**
 * TradesTable component for displaying recent trades
 */

import React from 'react';
import { Trade } from '../types';
import { formatPrice, formatQuantity, formatTime } from '../utils/formatters';
import '../styles/TradesTable.css';

interface TradesTableProps {
  trades: Trade[];
  maxTrades?: number;
}

export const TradesTable: React.FC<TradesTableProps> = ({ trades, maxTrades = 20 }) => {
  if (trades.length === 0) {
    return (
      <div className="trades-table">
        <h3>Recent Trades</h3>
        <div className="trades-empty">Waiting for trade data...</div>
      </div>
    );
  }

  const displayTrades = trades.slice(0, maxTrades);

  return (
    <div className="trades-table">
      <h3>Recent Trades</h3>
      <table className="trades-table-content">
        <thead>
          <tr>
            <th>Time</th>
            <th>Side</th>
            <th>Price</th>
            <th>Quantity</th>
          </tr>
        </thead>
        <tbody>
          {displayTrades.map((trade, index) => (
            <tr
              key={`${trade.time}-${index}`}
              className={trade.side === 'BUY' ? 'trade-buy' : 'trade-sell'}
            >
              <td>{formatTime(trade.time)}</td>
              <td>{trade.side}</td>
              <td>${formatPrice(trade.price)}</td>
              <td>{formatQuantity(trade.qty)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
