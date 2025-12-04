/**
 * MetricCard component for displaying individual metrics
 */

import React from 'react';
import '../styles/MetricCard.css';

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  delta,
  deltaType = 'neutral',
}) => {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {delta && (
        <div className={`metric-delta metric-delta-${deltaType}`}>
          {delta}
        </div>
      )}
    </div>
  );
};
