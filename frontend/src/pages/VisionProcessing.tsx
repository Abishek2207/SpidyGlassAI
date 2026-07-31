import React, { useEffect, useRef, useState } from 'react';
import { Camera, AlertTriangle, Zap, Clock, Cpu, BarChart2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../App';
import { useStore } from '../store/useStore';

// MediaPipe is loaded via CDN script tags in index.html.
// We access it via the window globals it injects.
declare global {
  interface Window {
    Hands: new (config: { locateFile: (file: string) => string }) => {
      setOptions: (opts: object) => void;
      onResults: (cb: (results: MediaPipeResults) => void) => void;
      send: (data: { image: HTMLVideoElement }) => Promise<void>;
      close: () => void;
    };
    Camera: new (
      video: HTMLVideoElement,
      opts: { onFrame: () => Promise<void>; width: number; height: number }
    ) => { start: () => Promise<void>; stop: () => void };
    drawConnectors: (ctx: CanvasRenderingContext2D, landmarks: NormalizedLandmark[], connections: [number, number][], style: object) => void;
    drawLandmarks: (ctx: CanvasRenderingContext2D, landmarks: NormalizedLandmark[], style: object) => void;
    HAND_CONNECTIONS: [number, number][];
  }
}

interface NormalizedLandmark { x: number; y: number; z: number }
interface MediaPipeResults {
  multiHandLandmarks?: NormalizedLandmark[][];
}

interface GestureResult {
  gesture: string;
  confidence: number;
  latency: number;
  model_version: string;
  hand_index: number;
}

const VisionProcessing: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [gestureData, setGestureData] = useState<GestureResult | null>(null);
  const [modelError, setModelError] = useState<string | null>(null);
  const [mediapipeReady, setMediapipeReady] = useState(false);
  const [fps, setFps] = useState(0);
  const frameCountRef = useRef(0);
  const lastFpsTimeRef = useRef(Date.now());

  const { updateStats } = useStore();

  // Check if MediaPipe globals are available (loaded from CDN in index.html)
  useEffect(() => {
    const checkMediaPipe = setInterval(() => {
      if (Boolean(window.Hands) && Boolean(window.Camera) && Boolean(window.drawConnectors)) {
        setMediapipeReady(true);
        clearInterval(checkMediaPipe);
      }
    }, 200);
    return () => clearInterval(checkMediaPipe);
  }, []);

  useEffect(() => {
    if (!mediapipeReady) return;

    const videoEl = videoRef.current;
    const canvasEl = canvasRef.current;
    if (!videoEl || !canvasEl) return;

    let lastInference = 0;

    const hands = new window.Hands({
      locateFile: (file: string) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
    });

    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });

    hands.onResults(async (results: MediaPipeResults) => {
      setIsStreaming(true);
      const ctx = canvasEl.getContext('2d');
      if (!ctx) return;

      // FPS tracking
      frameCountRef.current += 1;
      const now = Date.now();
      if (now - lastFpsTimeRef.current >= 1000) {
        const currentFps = Math.round(frameCountRef.current * 1000 / (now - lastFpsTimeRef.current));
        setFps(currentFps);
        lastFpsTimeRef.current = now;
        frameCountRef.current = 0;
      }

      ctx.save();
      ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);

      if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
          window.drawConnectors(ctx, landmarks, window.HAND_CONNECTIONS, {
            color: '#00FF88',
            lineWidth: 2,
          });
          window.drawLandmarks(ctx, landmarks, {
            color: '#FF4444',
            lineWidth: 1,
            radius: 3,
          });
        }

        if (now - lastInference > 300 && results.multiHandLandmarks.length > 0) {
          lastInference = now;
          const payload = results.multiHandLandmarks[0].map((lm) => ({
            x: lm.x,
            y: lm.y,
            z: lm.z,
          }));
          try {
            const res = await api.post('/gesture/recognize', {
              landmarks: [payload],
            });
            if (res.data.error) {
              setModelError(res.data.error);
              setGestureData(null);
            } else if (res.data.results && res.data.results.length > 0) {
              setModelError(null);
              const result: GestureResult = res.data.results[0];
              setGestureData(result);
              updateStats(result.latency, fps);
            }
          } catch {
            setModelError('NETWORK_ERROR');
          }
        }
      }
      ctx.restore();
    });

    const camera = new window.Camera(videoEl, {
      onFrame: async () => {
        if (videoEl.readyState >= 2) {
          await hands.send({ image: videoEl });
        }
      },
      width: 640,
      height: 480,
    });

    camera.start().catch((err: Error) => console.error('Camera error:', err));

    return () => {
      camera.stop();
      hands.close();
    };
  }, [mediapipeReady]);

  const confidencePct = gestureData ? Math.round(gestureData.confidence * 100) : 0;

  return (
    <div className="h-full flex flex-col space-y-6">
      <header>
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">
          Vision Processing
        </h2>
        <p className="text-white/50 mt-1">Real-time MediaPipe + PyTorch gesture inference</p>
      </header>

      <div className="flex-1 grid grid-cols-3 gap-6">
        {/* Camera Feed */}
        <div className="col-span-2 glass-panel rounded-2xl overflow-hidden relative border border-white/10 shadow-[0_0_30px_rgba(59,130,246,0.15)] flex flex-col justify-center items-center bg-black/70">
          {!isStreaming && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-white/50 z-20">
              {!mediapipeReady ? (
                <>
                  <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mb-4" />
                  <p className="font-mono text-sm">Loading MediaPipe from CDN…</p>
                </>
              ) : (
                <>
                  <div className="w-8 h-8 border-2 border-green-400 border-t-transparent rounded-full animate-spin mb-4" />
                  <p className="font-mono text-sm">Initializing camera…</p>
                </>
              )}
            </div>
          )}
          {/* Hidden video source; canvas shows output */}
          <video ref={videoRef} playsInline muted className="hidden" />
          <canvas
            ref={canvasRef}
            width={640}
            height={480}
            className={`w-full h-full object-cover transition-opacity duration-1000 ${isStreaming ? 'opacity-100' : 'opacity-0'}`}
          />
          {/* Live badge */}
          <div className="absolute top-4 right-4 px-3 py-1 bg-black/60 backdrop-blur-md border border-white/10 rounded-full flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`} />
            <span className="text-xs font-mono">{isStreaming ? 'LIVE' : 'OFFLINE'}</span>
          </div>
          {/* FPS badge */}
          {isStreaming && (
            <div className="absolute top-4 left-4 px-3 py-1 bg-black/60 backdrop-blur-md border border-white/10 rounded-full flex items-center gap-2">
              <span className="text-xs font-mono text-green-400">{fps} FPS</span>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Detected Gesture */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-panel rounded-2xl p-5"
          >
            <h3 className="text-base font-semibold mb-3 flex items-center gap-2">
              <Camera className="w-4 h-4 text-blue-400" />
              Detected Gesture
            </h3>
            {modelError === 'MODEL_NOT_FOUND' ? (
              <div className="h-24 flex flex-col items-center justify-center bg-red-900/20 rounded-xl border border-red-500/20 text-red-400 p-4 text-center">
                <AlertTriangle className="w-7 h-7 mb-1" />
                <span className="font-semibold text-sm">MODEL_NOT_FOUND</span>
                <span className="text-xs mt-1 text-red-300/70">Train and place sign_language.pt in backend/models/</span>
              </div>
            ) : modelError ? (
              <div className="h-24 flex flex-col items-center justify-center bg-yellow-900/20 rounded-xl border border-yellow-500/20 text-yellow-400 p-4 text-center">
                <AlertTriangle className="w-7 h-7 mb-1" />
                <span className="font-semibold text-sm">{modelError}</span>
              </div>
            ) : (
              <div className="h-24 flex items-center justify-center bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-xl border border-white/5">
                <span className="text-2xl font-bold tracking-widest uppercase text-center px-2">
                  {gestureData ? gestureData.gesture : 'WAITING…'}
                </span>
              </div>
            )}
          </motion.div>

          {/* Confidence Bar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.05 }}
            className="glass-panel rounded-2xl p-5"
          >
            <h3 className="text-base font-semibold mb-3 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-emerald-400" />
              Confidence
            </h3>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-3 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-green-400"
                  animate={{ width: `${confidencePct}%` }}
                  transition={{ type: 'spring', stiffness: 80 }}
                />
              </div>
              <span className="font-mono text-sm text-emerald-400 w-12 text-right">{gestureData ? `${confidencePct}%` : '--'}</span>
            </div>
          </motion.div>

          {/* Inference Metrics */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-panel rounded-2xl p-5"
          >
            <h3 className="text-base font-semibold mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              Inference Metrics
            </h3>
            <ul className="space-y-2.5 font-mono text-sm text-white/70">
              <li className="flex justify-between items-center">
                <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" />Latency</span>
                <span className="text-yellow-400">{gestureData ? `${gestureData.latency}ms` : '--'}</span>
              </li>
              <li className="flex justify-between items-center">
                <span>FPS</span>
                <span className="text-green-400">{isStreaming ? fps : '--'}</span>
              </li>
              <li className="flex justify-between items-center">
                <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5" />Model</span>
                <span className={gestureData ? 'text-purple-400' : 'text-red-400'}>
                  {gestureData ? gestureData.model_version : 'Missing'}
                </span>
              </li>
              <li className="flex justify-between items-center">
                <span>Landmarks</span>
                <span className="text-blue-400">21 × (X, Y, Z)</span>
              </li>
            </ul>
          </motion.div>

          {/* Pipeline Status */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 }}
            className="glass-panel rounded-2xl p-5"
          >
            <h3 className="text-base font-semibold mb-3">Pipeline Status</h3>
            <ul className="space-y-2 font-mono text-sm text-white/70">
              <li className="flex justify-between">
                <span>MediaPipe</span>
                <span className={mediapipeReady ? 'text-green-400' : 'text-yellow-400'}>
                  {mediapipeReady ? 'Ready' : 'Loading…'}
                </span>
              </li>
              <li className="flex justify-between">
                <span>Camera</span>
                <span className={isStreaming ? 'text-green-400' : 'text-yellow-400'}>
                  {isStreaming ? 'Live' : 'Starting…'}
                </span>
              </li>
              <li className="flex justify-between">
                <span>PyTorch Model</span>
                <span className={gestureData && !modelError ? 'text-purple-400' : 'text-red-400'}>
                  {gestureData && !modelError ? 'Loaded' : 'Not Loaded'}
                </span>
              </li>
            </ul>
            {modelError === 'MODEL_NOT_FOUND' && (
              <div className="mt-3 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-200/80">
                Run <code className="bg-white/10 px-1 rounded">cd backend/ml && python train.py</code> to generate the model, then restart the backend.
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default VisionProcessing;
