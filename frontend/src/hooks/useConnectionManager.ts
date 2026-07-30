import { useState, useEffect, useRef, useCallback } from 'react';
import { fetchWithRetry } from '../services/apiClient';

interface ConnectionState {
  status: 'connected' | 'reconnecting' | 'offline';
  lastPing: number | null;
  wsConnected: boolean;
}

export const useConnectionManager = (
  wsUrl: string,
  onMessage: (data: any) => void,
  demoMode: boolean = true
) => {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    status: 'reconnecting',
    lastPing: null,
    wsConnected: false,
  });

  const ws = useRef<WebSocket | null>(null);
  const healthPollInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  let isDestroyed = false;

  const connectWs = useCallback(() => {
    if (isDestroyed || ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) return;

    try {
      ws.current = new WebSocket(`${wsUrl}?demoMode=${demoMode}`);

      ws.current.onopen = () => {
        if (isDestroyed) { ws.current?.close(); return; }
        setConnectionState(prev => ({ ...prev, status: 'connected', wsConnected: true, lastPing: Date.now() }));
      };

      ws.current.onmessage = (event) => {
        if (isDestroyed) return;
        try {
          const payload = JSON.parse(event.data);
          onMessage(payload);
        } catch (e) {
          console.error('[ConnectionManager] Message parse error:', e);
        }
      };

      ws.current.onclose = () => {
        if (isDestroyed) return;
        setConnectionState(prev => ({ ...prev, status: 'reconnecting', wsConnected: false }));
        // Try to reconnect in 2 seconds
        if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = setTimeout(connectWs, 2000);
      };

      ws.current.onerror = () => {
        console.error('[ConnectionManager] WebSocket error');
      };
    } catch (e) {
      console.error('[ConnectionManager] Failed to create WebSocket');
    }
  }, [wsUrl, onMessage, demoMode]);

  const checkHealth = useCallback(async () => {
    if (isDestroyed) return;
    try {
      const data = await fetchWithRetry('/health', { retries: 0, timeout: 1500 });
      if (data.status === 'online') {
        // Backend is alive. If WS is dead, status is reconnecting. If WS is alive, status is connected.
        if (ws.current?.readyState === WebSocket.OPEN) {
          setConnectionState(prev => ({ ...prev, status: 'connected', lastPing: Date.now() }));
        } else {
          setConnectionState(prev => ({ ...prev, status: 'reconnecting' }));
          connectWs(); // Force reconnect attempt if we know it's online but WS is dead
        }
      }
    } catch (e) {
      setConnectionState(prev => ({ ...prev, status: 'reconnecting' }));
    }
  }, [connectWs]);

  useEffect(() => {
    isDestroyed = false;
    connectWs();
    
    // Poll health every 2 seconds
    healthPollInterval.current = setInterval(checkHealth, 2000);

    return () => {
      isDestroyed = true;
      if (healthPollInterval.current) clearInterval(healthPollInterval.current);
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      ws.current?.close();
    };
  }, [connectWs, checkHealth]);

  const sendMessage = useCallback((type: string, data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, data }));
    } else {
      console.warn('[ConnectionManager] Cannot send message, WebSocket not connected.');
      // REST Fallback could be implemented here for specific message types
    }
  }, []);

  return { connectionState, sendMessage };
};
