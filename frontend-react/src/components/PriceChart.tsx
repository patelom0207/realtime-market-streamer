/**
 * PriceChart component for visualizing mid-price history
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ChartDataPoint } from '../types';
import '../styles/PriceChart.css';

interface PriceChartProps {
  data: number[];
}

export const PriceChart: React.FC<PriceChartProps> = ({ data }) => {
  // Transform data for Recharts
  const chartData: ChartDataPoint[] = data.map((price, index) => ({
    index,
    price,
  }));

  if (data.length === 0) {
    return (
      <div className="chart-container">
        <div className="chart-empty">
          Building chart... waiting for more data points.
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="index"
            label={{ value: 'Data Points', position: 'insideBottom', offset: -5 }}
            stroke="#666"
          />
          <YAxis
            label={{ value: 'Mid Price ($)', angle: -90, position: 'insideLeft' }}
            stroke="#666"
            domain={['auto', 'auto']}
          />
          <Tooltip
            formatter={(value: number) => [`$${value.toFixed(2)}`, 'Mid Price']}
            labelFormatter={(label) => `Point ${label}`}
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#1f77b4"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
