import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { VideoOff, Fingerprint } from 'lucide-react';
import type { FrameResult } from '../types';

interface CenterDashboardProps {
  cameraActive: boolean;
  frameResult: FrameResult | null;
  onToggleCamera: () => void;
  sendFrameToBackend: (frame: string) => void;
}

export const CenterDashboard = ({ cameraActive, frameResult, onToggleCamera, sendFrameToBackend }: CenterDashboardProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    let animationId: number;
    
    const captureLoop = () => {
      if (cameraActive && videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const base64Img = canvas.toDataURL('image/jpeg', 0.5);
            sendFrameToBackend(base64Img);
          }
        }
      }
      
      // Target ~15 FPS for the backend feed
      setTimeout(() => {
        animationId = requestAnimationFrame(captureLoop);
      }, 66);
    };

    if (cameraActive) {
      // Start camera
      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
        .then(stream => {
          streamRef.current = stream;
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
          }
          animationId = requestAnimationFrame(captureLoop);
        })
        .catch(err => console.error("Camera error:", err));
    } else {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
        streamRef.current = null;
      }
    }

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
      }
    };
  }, [cameraActive]);

  return (
    <div className="flex-1 flex flex-col relative min-h-[400px]">
      
      {/* Hidden canvas for frame capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Main Vision Display */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative flex-1 rounded-3xl overflow-hidden glass-panel flex items-center justify-center group"
      >
        {/* Glow behind the video */}
        <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 via-transparent to-blue-500/10"></div>
        
        {cameraActive ? (
          <div className="w-full h-full relative z-10">
            {/* Live video feed — always shown when camera is active */}
            <video
              ref={videoRef}
              playsInline
              muted
              autoPlay
              className="w-full h-full object-cover"
            />

            {/* AI-annotated overlay on top of live feed */}
            {frameResult?.objects?.map((obj, i) => (
              <div 
                key={`obj-${i}`} 
                className="absolute border-2 border-yellow-400/80 bg-yellow-400/10 pointer-events-none shadow-[0_0_15px_rgba(250,204,21,0.3)]"
                style={{
                  left: `${obj.bbox[0] * 100}%`,
                  top: `${obj.bbox[1] * 100}%`,
                  width: `${(obj.bbox[2] - obj.bbox[0]) * 100}%`,
                  height: `${(obj.bbox[3] - obj.bbox[1]) * 100}%`
                }}
              >
                <span className="absolute -top-6 left-[-2px] bg-yellow-400/90 text-black text-[10px] font-mono font-bold px-2 py-0.5 tracking-wider backdrop-blur-sm">
                  {obj.label.toUpperCase()} {Math.round(obj.confidence * 100)}%
                </span>
              </div>
            ))}
            {frameResult?.faces?.map((face, i) => (
              <div 
                key={`face-${i}`} 
                className="absolute border-2 border-fuchsia-500/80 bg-fuchsia-500/10 pointer-events-none flex items-center justify-center shadow-[0_0_15px_rgba(217,70,239,0.3)]"
                style={{
                  left: `${face.bbox[0] * 100}%`,
                  top: `${face.bbox[1] * 100}%`,
                  width: `${(face.bbox[2] - face.bbox[0]) * 100}%`,
                  height: `${(face.bbox[3] - face.bbox[1]) * 100}%`
                }}
              >
                 <span className="absolute -top-6 left-[-2px] bg-fuchsia-500/90 text-white text-[10px] font-mono font-bold px-2 py-0.5 tracking-wider backdrop-blur-sm">
                  FACE {Math.round(face.confidence * 100)}%
                </span>
                <div className="w-6 h-6 border-t border-l border-fuchsia-500/50 absolute top-2 left-2"></div>
                <div className="w-6 h-6 border-t border-r border-fuchsia-500/50 absolute top-2 right-2"></div>
                <div className="w-6 h-6 border-b border-l border-fuchsia-500/50 absolute bottom-2 left-2"></div>
                <div className="w-6 h-6 border-b border-r border-fuchsia-500/50 absolute bottom-2 right-2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="relative z-10 flex flex-col items-center text-neutral-500">
            <VideoOff className="w-16 h-16 mb-6 opacity-30" />
            <button 
              onClick={onToggleCamera}
              className="px-8 py-3 glass-pill hover:bg-white/20 transition-all font-medium text-white tracking-wide"
            >
              ENGAGE OPTICS
            </button>
          </div>
        )}

        {/* Floating overlays for Gesture */}
        {cameraActive && frameResult?.gesture && (
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="absolute bottom-6 left-6 z-20 glass-pill px-6 py-4 flex items-center gap-4 shadow-lg border-cyan-500/30"
          >
            <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center">
              <Fingerprint className="w-5 h-5 text-cyan-300" />
            </div>
            <div>
              <p className="text-[10px] text-cyan-400 font-mono tracking-widest uppercase mb-1">Detected Gesture</p>
              <p className="text-xl font-light text-white">{frameResult.gesture.gesture}</p>
            </div>
            <div className="ml-4 pl-4 border-l border-white/10 flex flex-col items-end">
              <p className="text-[10px] text-neutral-400 font-mono">CONFIDENCE</p>
              <p className="text-lg text-cyan-400 font-mono">{(frameResult.gesture.confidence * 100).toFixed(0)}%</p>
            </div>
          </motion.div>
        )}
        
        {/* Processing Latency Badge */}
        {cameraActive && frameResult && (
          <div className="absolute top-6 right-6 z-20 glass-pill px-3 py-1 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-xs font-mono text-neutral-300">{frameResult.process_time_ms}ms processing</span>
          </div>
        )}
      </motion.div>
      
      {/* Controls */}
      {cameraActive && (
        <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 z-30">
          <button 
            onClick={onToggleCamera}
            className="glass-pill px-6 py-2 bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20 transition-all text-sm font-medium tracking-wide"
          >
            DISENGAGE OPTICS
          </button>
        </div>
      )}
    </div>
  );
};
