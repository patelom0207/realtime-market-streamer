/**
 * Utility functions for formatting data
 */

export const formatNumber = (value: number | null, decimals: number = 2): string => {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return value.toFixed(decimals);
};

export const formatPrice = (value: number | null): string => {
  return formatNumber(value, 2);
};

export const formatQuantity = (value: number | null): string => {
  return formatNumber(value, 4);
};

export const formatPercentage = (value: number | null): string => {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  return `${(value * 100).toFixed(2)}%`;
};

export const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp * 1000);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export const formatElapsedTime = (seconds: number): string => {
  if (seconds < 60) {
    return `${Math.floor(seconds)}s ago`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}m ${remainingSeconds}s ago`;
};

export const formatUptime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
};
