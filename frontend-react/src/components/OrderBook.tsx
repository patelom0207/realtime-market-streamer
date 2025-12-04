/**
 * OrderBook component for displaying bid/ask levels
 */

import React from 'react';
import { formatPrice, formatQuantity } from '../utils/formatters';
import '../styles/OrderBook.css';

interface OrderBookProps {
  bids: [number, number][];
  asks: [number, number][];
}

export const OrderBook: React.FC<OrderBookProps> = ({ bids, asks }) => {
  if (bids.length === 0 && asks.length === 0) {
    return (
      <div className="order-book">
        <h3>Order Book Snapshot</h3>
        <div className="order-book-empty">Waiting for order book data...</div>
      </div>
    );
  }

  return (
    <div className="order-book">
      <h3>Order Book Snapshot</h3>
      <table className="order-book-table">
        <thead>
          <tr>
            <th>Side</th>
            <th>Price</th>
            <th>Quantity</th>
          </tr>
        </thead>
        <tbody>
          {/* Asks in reverse order (highest to lowest) */}
          {[...asks].reverse().map(([price, qty], index) => (
            <tr key={`ask-${index}`} className="order-book-ask">
              <td>ASK</td>
              <td>${formatPrice(price)}</td>
              <td>{formatQuantity(qty)}</td>
            </tr>
          ))}

          {/* Separator */}
          <tr className="order-book-separator">
            <td colSpan={3}>
              <div className="separator-line"></div>
            </td>
          </tr>

          {/* Bids (highest to lowest) */}
          {bids.map(([price, qty], index) => (
            <tr key={`bid-${index}`} className="order-book-bid">
              <td>BID</td>
              <td>${formatPrice(price)}</td>
              <td>{formatQuantity(qty)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
