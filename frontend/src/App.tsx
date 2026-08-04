import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import axios from 'axios';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import VisionProcessing from './pages/VisionProcessing';
import SpeechEngine from './pages/SpeechEngine';
import Translation from './pages/Translation';
import AIAssistant from './pages/AIAssistant';
import AgentMesh from './pages/AgentMesh';
import Logs from './pages/Logs';
import Settings from './pages/Settings';
import { useStore } from './store/useStore';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } }
});

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Root-level axios for /health (not prefixed)
export const rootApi = axios.create({ baseURL: BASE_URL });

// API client for /api/v1/* routes
export const api = axios.create({ baseURL: `${BASE_URL}/api/v1` });

export interface AgentResponse {
  response?: string;
  error?: string;
  transcript?: string;
  gesture_detected?: string;
  ai_reply?: string;
}

function App() {
  const { setConnectionStatus, updateStats, setServerCapabilities, authToken } = useStore();

  // Inject JWT token into every api request
  useEffect(() => {
    const interceptor = api.interceptors.request.use((config) => {
      const token = useStore.getState().authToken;
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    });
    return () => api.interceptors.request.eject(interceptor);
  }, [authToken]);

  useEffect(() => {
    // Health check on root endpoint
    rootApi.get('/health').then((res) => {
      setServerCapabilities(
        res.data.model_loaded ?? false,
        Boolean(res.data.sarvam_configured ?? res.data.demo_mode === false)
      );
    }).catch(err => console.warn('Backend health check failed:', err));

    let ws: WebSocket;
    let heartbeatInterval: number;

    const connectWebSocket = () => {
      const token = useStore.getState().authToken;
      const wsUrl = token
        ? `ws://localhost:8000/ws?token=${token}`
        : 'ws://localhost:8000/ws?demoMode=true';
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setConnectionStatus(true);
        heartbeatInterval = window.setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 5000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'pong') {
            updateStats(
              Math.floor(Math.random() * 30 + 10),
              Math.floor(Math.random() * 5 + 25)
            );
          }
        } catch (e) {
          console.error('Error parsing WS message', e);
        }
      };

      ws.onclose = () => {
        setConnectionStatus(false);
        clearInterval(heartbeatInterval);
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connectWebSocket();

    return () => {
      if (ws) ws.close();
      if (heartbeatInterval) clearInterval(heartbeatInterval);
    };
  }, [setConnectionStatus, updateStats, setServerCapabilities]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/vision" element={<VisionProcessing />} />
            <Route path="/speech" element={<SpeechEngine />} />
            <Route path="/translation" element={<Translation />} />
            <Route path="/assistant" element={<AIAssistant />} />
            <Route path="/mesh" element={<AgentMesh />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
