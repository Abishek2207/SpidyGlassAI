import { useState, useEffect, useRef, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { ConversationHistory } from './components/ConversationHistory';
import { CenterDashboard } from './components/CenterDashboard';
import { RightPanel } from './components/RightPanel';
import { BottomPanel } from './components/BottomPanel';
import { ParticleBackground } from './components/ParticleBackground';
import { SettingsModal } from './components/SettingsModal';
import { AnalyticsOverlay } from './components/AnalyticsOverlay';
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
  const [telemetry, setTelemetry] = useState<TelemetryPayload | null>(null);
  const [frameResult, setFrameResult] = useState<FrameResult | null>(null);
  const [agentResponse, setAgentResponse] = useState<AgentResponse | null>(null);
  const [history, setHistory] = useState<AgentResponse[]>([]);
  const [cameraActive, setCameraActive] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('Dashboard');
  
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState(false);

  const ws = useRef<WebSocket | null>(null);
  const pingInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const recognitionRef = useRef<any>(null);
  const [micActive, setMicActive] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState<string>('');

  useEffect(() => {
    let destroyed = false;

    const connect = () => {
      if (destroyed) return;
      const backendUrl = import.meta.env.VITE_API_URL || 'https://spidyglassai.onrender.com';
      const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
      const wsUrl = `${backendUrl.replace(/^https?:\/\//, `${wsProtocol}://`)}/ws`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        if (destroyed) { ws.current?.close(); return; }
        console.log('[SpiderGlass] Neural link established');
        setWsConnected(true);
        pingInterval.current = setInterval(() => {
          ws.current?.send(JSON.stringify({ type: 'ping' }));
        }, 30000);
      };

      ws.current.onmessage = (event) => {
        if (destroyed) return;
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'telemetry') {
            setTelemetry(payload.data);
          } else if (payload.type === 'frame_result') {
            const data = payload.data;
            const topGesture = data.gestures?.[0] ?? null;
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
            setLiveTranscript(payload.data.transcript || '');
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
        if (!destroyed) {
          console.log('[SpiderGlass] Neural link severed — reconnecting in 3s');
          setTimeout(connect, 3000);
        }
      };

      ws.current.onerror = (e) => {
        console.error('[SpiderGlass] WebSocket error', e);
      };
    };

    connect();
    return () => {
      destroyed = true;
      if (pingInterval.current) clearInterval(pingInterval.current);
      ws.current?.close();
    };
  }, []);

  const toggleMic = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Speech Recognition not supported in this browser.');
      return;
    }

    if (micActive) {
      recognitionRef.current?.stop();
      setMicActive(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      setLiveTranscript(interim || final);
      if (final.trim()) {
        // Send finalized transcript to backend for translation + AI
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: 'text_message', data: final.trim() }));
        }
      }
    };

    recognition.onerror = () => setMicActive(false);
    recognition.onend = () => { if (micActive) recognition.start(); };

    recognitionRef.current = recognition;
    recognition.start();
    setMicActive(true);
  }, [micActive]);

  const sendFrameToBackend = useCallback((base64Img: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'frame', data: base64Img }));
    }
  }, []);


  return (
    <div className="h-screen w-full bg-[#050505] text-white p-4 lg:p-6 overflow-hidden flex gap-6">
      <ParticleBackground />

      {/* Overlays */}
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <AnalyticsOverlay isOpen={isAnalyticsOpen} onClose={() => setIsAnalyticsOpen(false)} />

      {/* Main Layout */}
      <Sidebar 
        wsConnected={wsConnected} 
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onSettingsClick={() => setIsSettingsOpen(true)}
        onAnalyticsClick={() => setIsAnalyticsOpen(true)}
      />
      <ConversationHistory history={history} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full min-w-0">

        {/* Top/Center Dashboard (Video & Telemetry) */}
        <div className="flex-1 flex gap-6 min-h-0">
          {activeTab === 'Dashboard' ? (
            <>
              <CenterDashboard
                cameraActive={cameraActive}
                frameResult={frameResult}
                onToggleCamera={() => setCameraActive(!cameraActive)}
                sendFrameToBackend={sendFrameToBackend}
              />
              <RightPanel telemetry={telemetry} />
            </>
          ) : (
            <div className="flex-1 glass-panel rounded-3xl flex flex-col items-center justify-center border border-white/5 bg-gradient-to-br from-white/5 to-transparent relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50"></div>
              <h2 className="text-3xl font-light tracking-widest text-cyan-400 mb-4 uppercase">{activeTab}</h2>
              <p className="text-neutral-500 font-mono text-sm max-w-md text-center">
                Module isolated for Investor Demo Mode. Real-time {activeTab.toLowerCase()} data is being aggregated in the background.
              </p>
              <div className="mt-8 flex gap-2">
                {[1, 2, 3].map(i => (
                  <div key={i} className="w-2 h-2 rounded-full bg-cyan-500/50 animate-bounce" style={{ animationDelay: `${i * 0.2}s` }}></div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Bottom Panel (Audio/Context/Translation) */}
        <BottomPanel
          transcript={liveTranscript || agentResponse?.transcript}
          translatedText={agentResponse?.translated_text}
          aiReply={agentResponse?.ai_reply}
          pipelineStages={agentResponse?.pipeline_stages}
          micActive={micActive}
          onMicToggle={toggleMic}
        />

      </div>
    </div>
  );
}

export default App;
