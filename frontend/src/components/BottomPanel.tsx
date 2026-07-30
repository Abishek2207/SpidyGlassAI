import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Globe2, Sparkles, CheckCircle2, Mic, MicOff } from 'lucide-react';

interface BottomPanelProps {
  transcript?: string;
  translatedText?: string;
  aiReply?: string;
  pipelineStages?: string[];
  micActive?: boolean;
  onMicToggle?: () => void;
}

const renderWithDemoBadge = (text?: string, fallback?: string) => {
  if (!text) return fallback;
  if (text.startsWith('[DEMO PROVIDER]') || text.startsWith('[DEMO RESPONSE]')) {
    const isProvider = text.startsWith('[DEMO PROVIDER]');
    const badgeText = isProvider ? 'DEMO PROVIDER' : 'DEMO RESPONSE';
    const cleanText = text.replace(/\[DEMO (PROVIDER|RESPONSE)\]\s*/, '');
    return (
      <span className="leading-relaxed">
        <span className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-bold tracking-widest uppercase mr-2 align-middle border ${isProvider ? 'bg-cyan-900/40 text-cyan-400 border-cyan-500/30' : 'bg-purple-900/40 text-purple-400 border-purple-500/30'}`}>
          {badgeText}
        </span>
        {cleanText}
      </span>
    );
  }
  return text;
};

export const BottomPanel = ({ transcript, translatedText, aiReply, pipelineStages, micActive, onMicToggle }: BottomPanelProps) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-48 mt-6">

      {/* Live Transcript */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="glass-panel rounded-3xl p-5 flex flex-col relative overflow-hidden group"
      >
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50 group-hover:opacity-100 transition-opacity duration-700"></div>
        <h3 className="text-xs font-mono text-cyan-400 mb-3 flex items-center justify-between uppercase tracking-widest">
          <span className="flex items-center gap-2"><MessageSquare className="w-4 h-4" /> Live Transcript (STT)</span>
          <button
            onClick={onMicToggle}
            className={`p-1.5 rounded-full transition-all ${
              micActive
                ? 'bg-red-500/20 text-red-400 animate-pulse'
                : 'bg-white/10 text-neutral-400 hover:text-white'
            }`}
            title={micActive ? 'Stop mic' : 'Start mic'}
          >
            {micActive ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
          </button>
        </h3>
        <AnimatePresence mode="wait">
          <motion.p
            key={transcript ?? 'empty'}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="text-base font-light italic text-neutral-300 flex-1"
          >
            {renderWithDemoBadge(transcript, 'Waiting for audio input...')}
          </motion.p>
        </AnimatePresence>
        {/* Waveform animation — only active when mic is live */}
        <div className="h-4 flex items-center gap-[2px] opacity-40 mt-2">
          {[...Array(22)].map((_, i) => (
            micActive ? (
              <motion.div
                key={i}
                animate={{ height: ['20%', '100%', '20%'] }}
                transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.06, ease: 'easeInOut' }}
                className="w-[2px] bg-cyan-500 rounded-full"
              />
            ) : (
              <div
                key={i}
                className="w-[2px] rounded-full bg-white/20"
                style={{ height: `${10 + (i % 5) * 8}%` }}
              />
            )
          ))}
        </div>
      </motion.div>

      {/* Translation */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="glass-panel rounded-3xl p-5 flex flex-col relative"
      >
        <h3 className="text-xs font-mono text-blue-400 mb-3 flex items-center justify-between uppercase tracking-widest">
          <span className="flex items-center gap-2"><Globe2 className="w-4 h-4" /> Translation</span>
          {pipelineStages?.includes('translation') && (
            <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
          )}
        </h3>
        <AnimatePresence mode="wait">
          <motion.p
            key={translatedText ?? 'empty'}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="text-xl font-medium text-white flex-1 flex items-center"
          >
            {renderWithDemoBadge(translatedText, 'ऑडियो इनपुट की प्रतीक्षा है...')}
          </motion.p>
        </AnimatePresence>
      </motion.div>

      {/* AI Response */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="glass-panel rounded-3xl p-5 flex flex-col relative overflow-hidden border-purple-500/20"
      >
        <div className="absolute -top-10 -right-10 w-32 h-32 bg-purple-500/20 blur-[50px] rounded-full pointer-events-none"></div>
        <h3 className="text-xs font-mono text-purple-400 mb-3 flex items-center justify-between uppercase tracking-widest relative z-10">
          <span className="flex items-center gap-2"><Sparkles className="w-4 h-4" /> AI Context Response</span>
          {pipelineStages?.includes('llm') && (
            <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
          )}
        </h3>
        <AnimatePresence mode="wait">
          <motion.p
            key={aiReply ?? 'empty'}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="text-sm text-neutral-300 font-light relative z-10 leading-relaxed overflow-y-auto"
          >
            {renderWithDemoBadge(aiReply, 'Perform a sign language gesture or speak to begin.')}
          </motion.p>
        </AnimatePresence>
      </motion.div>

    </div>
  );
};
