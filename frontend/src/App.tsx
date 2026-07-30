import { useState, useEffect, useRef, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { ConversationHistory } from './components/ConversationHistory';
import { CenterDashboard } from './components/CenterDashboard';
import { RightPanel } from './components/RightPanel';
import { BottomPanel } from './components/BottomPanel';
import { ParticleBackground } from './components/ParticleBackground';
import { LoginOverlay } from './components/LoginOverlay';
import { SettingsModal } from './components/SettingsModal';
import { AnalyticsOverlay } from './components/AnalyticsOverlay';
import { useAuthStore } from './store/authStore';
import type { TelemetryPayload, FrameResult } from './types';
export interface AgentResponse {
  transcript?: string;
  translated_text?: string;
  ai_reply?: string;
  tts_audio_base64?: string;
  gesture_detected?: string;
  pipeline_stages: string[];
  total_processing_time_ms: number;
  error?: string;
}

function App() {
  const { token } = useAuthStore();
  const [telemetry, setTelemetry] = useState<TelemetryPayload | null>(null);
  const [frameResult, setFrameResult] = useState<FrameResult | null>(null);
  const [agentResponse, setAgentResponse] = useState<AgentResponse | null>(null);
  const [history, setHistory] = useState<AgentResponse[]>([]);
  const [cameraActive, setCameraActive] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState(false);

  const ws = useRef<WebSocket | null>(null);
  const pingInterval = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!token) return;

    const connect = () => {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
      ws.current = new WebSocket(`${wsUrl}?token=${token}`);

      ws.current.onopen = () => {
        console.log('[SpiderGlass] Neural link established');
        setWsConnected(true);
        // Send ping every 30s to keep alive
        pingInterval.current = setInterval(() => {
          ws.current?.send(JSON.stringify({ type: 'ping' }));
        }, 30000);
      };

      ws.current.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'telemetry') {
            setTelemetry(payload.data);
          } else if (payload.type === 'frame_result') {
            // New protocol: gestures is an array; pick first for display
            const data = payload.data;
            const topGesture = data.gestures?.[0] ?? null;
            
            // If a sentence is generated, treat it as an agent input equivalent
            if (data.sentence && data.sentence.trim() !== '') {
               // We will just show it in the frame for now
            }
            
            setFrameResult({
              image: data.image ?? null,
              gesture: topGesture
                ? { gesture: topGesture.gesture, confidence: topGesture.confidence }
                : null,
              objects: data.objects ?? [],
              faces: data.faces ?? [],
              process_time_ms: data.process_time_ms ?? 0,
            });
          } else if (payload.type === 'agent_response') {
            setAgentResponse(payload.data);
            setHistory(prev => [payload.data, ...prev].slice(0, 50));
          } else if (payload.type === 'pong') {
            // keepalive acknowledged
          }
        } catch (e) {
          console.error('[SpiderGlass] Link corruption', e);
        }
      };

      ws.current.onclose = () => {
        setWsConnected(false);
        if (pingInterval.current) clearInterval(pingInterval.current);
        console.log('[SpiderGlass] Neural link severed — reconnecting in 3s');
        setTimeout(connect, 3000);
      };

      ws.current.onerror = (e) => {
        console.error('[SpiderGlass] WebSocket error', e);
      };
    };

    connect();
    return () => {
      if (pingInterval.current) clearInterval(pingInterval.current);
      ws.current?.close();
    };
  }, [token]);

  const sendFrameToBackend = useCallback((base64Img: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'frame', data: base64Img }));
    }
  }, []);

  if (!token) {
    return (
      <div className="h-screen w-full bg-[#050505] text-white p-4 lg:p-6 overflow-hidden flex gap-6">
        <ParticleBackground />
        <LoginOverlay />
      </div>
    );
  }

  return (
    <div className="h-screen w-full bg-[#050505] text-white p-4 lg:p-6 overflow-hidden flex gap-6">
      <ParticleBackground />

      {/* Overlays */}
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <AnalyticsOverlay isOpen={isAnalyticsOpen} onClose={() => setIsAnalyticsOpen(false)} />

      {/* Main Layout */}
      <Sidebar 
        wsConnected={wsConnected} 
        onSettingsClick={() => setIsSettingsOpen(true)}
        onAnalyticsClick={() => setIsAnalyticsOpen(true)}
      />
      <ConversationHistory history={history} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full min-w-0">

        {/* Top/Center Dashboard (Video & Telemetry) */}
        <div className="flex-1 flex gap-6 min-h-0">
          <CenterDashboard
            cameraActive={cameraActive}
            frameResult={frameResult}
            onToggleCamera={() => setCameraActive(!cameraActive)}
            sendFrameToBackend={sendFrameToBackend}
          />
          <RightPanel telemetry={telemetry} />
        </div>

        {/* Bottom Panel (Audio/Context/Translation) */}
        <BottomPanel
          transcript={agentResponse?.transcript}
          translatedText={agentResponse?.translated_text}
          aiReply={agentResponse?.ai_reply}
          pipelineStages={agentResponse?.pipeline_stages}
        />

      </div>
    </div>
  );
}

export default App;
