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
  const pingInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  // Use a ref (not a variable) so the closure always sees the latest value
  const isDestroyed = useRef(false);
  const reconnectDelay = useRef(2000);

  const connectWs = useCallback(() => {
    if (isDestroyed.current) return;

    const state = ws.current?.readyState;
    if (state === WebSocket.OPEN || state === WebSocket.CONNECTING) return;

    try {
      const socket = new WebSocket(`${wsUrl}?demoMode=${demoMode}`);
      ws.current = socket;

      socket.onopen = () => {
        if (isDestroyed.current) { socket.close(); return; }
        reconnectDelay.current = 2000; // reset backoff on success
        setConnectionState({ status: 'connected', wsConnected: true, lastPing: Date.now() });

        if (pingInterval.current) clearInterval(pingInterval.current);
        pingInterval.current = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 5000);
      };

      socket.onmessage = (event) => {
        if (isDestroyed.current) return;
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'pong') {
            setConnectionState(prev => ({ ...prev, lastPing: Date.now() }));
            return;
          }
          onMessage(payload);
        } catch (e) {
          console.error('[ConnectionManager] Message parse error:', e);
        }
      };

      socket.onclose = () => {
        if (isDestroyed.current) return;
        setConnectionState(prev => ({ ...prev, status: 'reconnecting', wsConnected: false }));
        if (pingInterval.current) clearInterval(pingInterval.current);

        // Exponential backoff capped at 10s
        const delay = Math.min(reconnectDelay.current, 10000);
        reconnectDelay.current = delay * 1.5;

        if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = setTimeout(connectWs, delay);
      };

      socket.onerror = (err) => {
        console.error('[ConnectionManager] WebSocket error:', err);
        // onclose fires automatically after onerror — no need to act here
      };
    } catch (e) {
      console.error('[ConnectionManager] Failed to create WebSocket:', e);
      // Schedule retry even if construction failed
      reconnectTimeout.current = setTimeout(connectWs, reconnectDelay.current);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [wsUrl, demoMode]);

  const checkHealth = useCallback(async () => {
    if (isDestroyed.current) return;
    try {
      const data = await fetchWithRetry('/health', { retries: 0, timeout: 2000 });
      if (data?.status === 'online') {
        if (ws.current?.readyState === WebSocket.OPEN) {
          setConnectionState(prev => ({ ...prev, status: 'connected', lastPing: Date.now() }));
        } else {
          // Backend is alive, but WS is dead — force a new connection
          setConnectionState(prev => ({ ...prev, status: 'reconnecting' }));
          connectWs();
        }
      }
    } catch {
      // Backend unreachable — UI will show reconnecting
      setConnectionState(prev => ({ ...prev, status: 'reconnecting', wsConnected: false }));
    }
  }, [connectWs]);

  useEffect(() => {
    isDestroyed.current = false;
    connectWs();

    // Poll REST health every 2 seconds as belt-and-suspenders
    healthPollInterval.current = setInterval(checkHealth, 2000);

    return () => {
      isDestroyed.current = true;
      if (healthPollInterval.current) clearInterval(healthPollInterval.current);
      if (reconnectTimeout.current)   clearTimeout(reconnectTimeout.current);
      if (pingInterval.current)       clearInterval(pingInterval.current);
      ws.current?.close();
    };
  }, [connectWs, checkHealth]);

  const sendMessage = useCallback((type: string, data: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, data }));
    } else {
      console.warn('[ConnectionManager] Cannot send — WebSocket not open. State:', ws.current?.readyState);
      // Attempt reconnect if user is actively trying to send
      if (ws.current?.readyState !== WebSocket.CONNECTING) {
        connectWs();
      }
    }
  }, [connectWs]);

  return { connectionState, sendMessage };
};
