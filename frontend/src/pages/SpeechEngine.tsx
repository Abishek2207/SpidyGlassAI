import React, { useState, useRef } from 'react';
import { Mic, MicOff, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../App';
import { useStore } from '../store/useStore';

const SpeechEngine: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [sarvamError, setSarvamError] = useState<string | null>(null);
  
  const { sarvamConfigured } = useStore();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const toggleListening = async () => {
    if (isListening) {
      if (mediaRecorderRef.current) {
         mediaRecorderRef.current.stop();
      }
      setIsListening(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        
        mediaRecorder.ondataavailable = (e) => {
           chunksRef.current.push(e.data);
        };
        
        mediaRecorder.onstop = async () => {
           const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
           chunksRef.current = [];
           
           // Convert blob to base64
           const reader = new FileReader();
           reader.readAsDataURL(blob);
           reader.onloadend = async () => {
             const base64data = (reader.result as string).split(',')[1];
             try {
                const res = await api.post('/speech/transcribe', { audio_base64: base64data });
                if (res.data.error) {
                  setSarvamError(res.data.error);
                } else {
                  setSarvamError(null);
                  setTranscript(prev => prev + " " + res.data.transcript);
                }
             } catch (err) {
                setSarvamError("NETWORK_ERROR");
             }
           };
           
           // Release microphone
           stream.getTracks().forEach(t => t.stop());
        };
        
        mediaRecorder.start();
        setIsListening(true);
      } catch (err) {
        console.error("Mic access denied", err);
      }
    }
  };

  return (
    <div className="h-full flex flex-col space-y-6">
      <header>
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">Speech Engine</h2>
        <p className="text-white/50 mt-1">Real-time Sarvam AI speech synthesis and recognition</p>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 flex flex-col relative overflow-hidden">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold">Live Transcript</h3>
            <button 
              onClick={toggleListening}
              className={`flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all duration-300 ${
                isListening 
                  ? 'bg-red-500/20 text-red-400 border border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.3)]' 
                  : 'bg-blue-500/20 text-blue-400 border border-blue-500/50 hover:bg-blue-500/30'
              }`}
            >
              {isListening ? (
                <><MicOff className="w-5 h-5" /> Stop Listening</>
              ) : (
                <><Mic className="w-5 h-5" /> Start Listening</>
              )}
            </button>
          </div>
          
          <div className="flex-1 bg-black/40 rounded-xl border border-white/5 p-6 overflow-y-auto font-mono text-lg leading-relaxed text-white/80 shadow-[inset_0_0_20px_rgba(0,0,0,0.5)] relative">
            {sarvamError === 'SERVICE_NOT_CONFIGURED' ? (
               <div className="absolute inset-0 flex flex-col items-center justify-center text-red-400 bg-red-900/10">
                 <AlertTriangle className="w-12 h-12 mb-4" />
                 <span className="font-semibold text-xl">SERVICE_NOT_CONFIGURED</span>
                 <span className="text-sm mt-2 text-white/50">SARVAM_API_KEY environment variable is missing.</span>
               </div>
            ) : (
              <>
                {transcript || <span className="text-white/30 italic">Waiting for speech input...</span>}
                {isListening && (
                  <motion.span 
                    animate={{ opacity: [0, 1, 0] }} 
                    transition={{ repeat: Infinity, duration: 1 }}
                    className="inline-block w-2 h-5 bg-white/70 ml-1 align-middle"
                  />
                )}
              </>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-panel rounded-2xl p-6 h-48 flex flex-col justify-center items-center relative overflow-hidden">
             <h3 className="absolute top-4 left-4 text-sm font-medium text-white/50">Audio Visualization</h3>
             
             <div className="flex items-center gap-1 mt-6">
               {[...Array(20)].map((_, i) => (
                 <motion.div
                   key={i}
                   animate={{ 
                     height: isListening ? [10, Math.random() * 80 + 20, 10] : 4,
                   }}
                   transition={{ 
                     repeat: Infinity, 
                     duration: 0.5 + Math.random() * 0.5,
                     ease: "easeInOut"
                   }}
                   className="w-2 rounded-full bg-gradient-to-t from-blue-500 to-purple-500"
                 />
               ))}
             </div>
          </div>
          
          <div className="glass-panel rounded-2xl p-6 flex-1">
             <h3 className="text-lg font-semibold mb-4">Engine Metrics</h3>
             <ul className="space-y-4 font-mono text-sm text-white/70">
                <li className="flex justify-between items-center">
                  <span>Provider:</span>
                  <span className="px-2 py-1 bg-white/5 rounded text-white">Sarvam AI</span>
                </li>
                <li className="flex justify-between items-center">
                  <span>Configuration:</span>
                  <span className={sarvamConfigured ? "text-green-400" : "text-red-400"}>{sarvamConfigured ? "Valid Key" : "Missing"}</span>
                </li>
             </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpeechEngine;
