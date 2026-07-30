import { useState, useRef, useCallback } from 'react';
import { useConnectionManager } from './hooks/useConnectionManager';
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
  const [systemLogs, setSystemLogs] = useState<any[]>([]);
  const [cameraActive, setCameraActive] = useState(false);
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState(false);
  const recognitionRef = useRef<any>(null);
  const [micActive, setMicActive] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState<string>('');
  const backendUrl = import.meta.env.VITE_API_URL || 'https://spidyglassai.onrender.com';
  const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
  const wsUrl = `${backendUrl.replace(/^https?:\/\//, `${wsProtocol}://`)}/ws`;

  const [demoMode, setDemoMode] = useState(true);

  const handleMessage = useCallback((payload: any) => {
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
      // Show confirmed gesture sentence in the live transcript
      if (data.sentence && data.sentence.trim()) {
        setLiveTranscript(`✋ ${data.sentence}`);
      }
    } else if (payload.type === 'agent_response') {
      setAgentResponse(payload.data);
      if (payload.data.transcript) {
        setLiveTranscript(payload.data.transcript);
      }
      setHistory(prev => [payload.data, ...prev].slice(0, 50));
    } else if (payload.type === 'system_log') {
      setSystemLogs(prev => [payload.data, ...prev].slice(0, 50));
    }
  }, []);

  const { connectionState, sendMessage } = useConnectionManager(wsUrl, handleMessage, demoMode);

  const toggleMic = useCallback(async () => {
    if (micActive) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current.stream.getTracks().forEach((track: any) => track.stop());
        recognitionRef.current = null;
      }
      setMicActive(false);
      sendMessage('audio_end', '');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64data = (reader.result as string).split(',')[1];
            sendMessage('audio_chunk', base64data);
          };
          reader.readAsDataURL(e.data);
        }
      };

      mediaRecorder.start(250); // Capture chunk every 250ms
      // Store custom object in ref to hold both recorder and stream
      recognitionRef.current = {
        stop: () => mediaRecorder.stop(),
        stream: stream
      };
      
      setMicActive(true);
      setLiveTranscript(''); // Clear previous transcript on new recording
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setMicActive(false);
    }
  }, [micActive, sendMessage]);

  const sendFrameToBackend = useCallback((base64Img: string) => {
    sendMessage('frame', base64Img);
  }, [sendMessage]);


  return (
    <div className="h-screen w-full bg-[#050505] text-white p-4 lg:p-6 overflow-hidden flex gap-6">
      <ParticleBackground />

      {/* Overlays */}
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <AnalyticsOverlay isOpen={isAnalyticsOpen} onClose={() => setIsAnalyticsOpen(false)} />

      {/* Main Layout */}
      <Sidebar 
        wsConnected={connectionState.status === 'connected'} 
        activeTab={activeTab}
        demoMode={demoMode}
        onDemoToggle={() => setDemoMode(!demoMode)}
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
              <RightPanel telemetry={telemetry} logs={systemLogs} />
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
