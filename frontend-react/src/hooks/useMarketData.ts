/**
 * Custom React hook for WebSocket connection to market data API
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { MarketSnapshot } from '../types';

const WS_URL = 'ws://localhost:8000/ws/market-data';
const RECONNECT_DELAY = 3000; // 3 seconds

export const useMarketData = () => {
  const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        if (isMountedRef.current) {
          setIsConnected(true);
          setError(null);
        }
      };

      ws.onmessage = (event) => {
        try {
          const data: MarketSnapshot = JSON.parse(event.data);
          if (isMountedRef.current) {
            setSnapshot(data);
          }
        } catch (err) {
          console.error('Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        if (isMountedRef.current) {
          setError('WebSocket connection error');
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        if (isMountedRef.current) {
          setIsConnected(false);

          // Attempt to reconnect after delay
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              console.log('Attempting to reconnect...');
              connect();
            }
          }, RECONNECT_DELAY);
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      if (isMountedRef.current) {
        setError('Failed to connect to server');
      }
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    // Cleanup function
    return () => {
      isMountedRef.current = false;

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    snapshot,
    isConnected,
    error,
  };
};
