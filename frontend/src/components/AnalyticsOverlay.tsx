import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, X, Server, Zap, Cpu } from 'lucide-react';
import { getAnalyticsSummary } from '../services/api';
import type { AnalyticsSummary } from '../services/api';

interface AnalyticsOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AnalyticsOverlay = ({ isOpen, onClose }: AnalyticsOverlayProps) => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      getAnalyticsSummary()
        .then(data => {
          setSummary(data);
          setIsLoading(false);
        })
        .catch(err => {
          console.error(err);
          setIsLoading(false);
        });
    }
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="w-full max-w-2xl glass-panel p-8 relative shadow-[0_0_50px_rgba(217,70,239,0.15)]"
          >
            <button
              onClick={onClose}
              className="absolute top-6 right-6 text-neutral-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="flex items-center gap-4 mb-8">
              <div className="w-12 h-12 rounded-2xl bg-fuchsia-500/20 flex items-center justify-center border border-fuchsia-500/30">
                <Activity className="w-6 h-6 text-fuchsia-400" />
              </div>
              <div>
                <h2 className="text-2xl font-light tracking-wide text-white">System Analytics</h2>
                <p className="text-sm font-mono text-fuchsia-500/70">TELEMETRY & USAGE METRICS</p>
              </div>
            </div>

            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-20 text-fuchsia-400">
                <div className="w-8 h-8 border-2 border-fuchsia-500/30 border-t-fuchsia-400 rounded-full animate-spin mb-4"></div>
                <p className="font-mono text-sm tracking-widest">FETCHING TELEMETRY...</p>
              </div>
            ) : summary ? (
              <div className="space-y-6">
                
                {/* Top Metrics Row */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="glass-panel p-4 bg-white/5 border-white/10 flex flex-col items-center justify-center text-center">
                    <Server className="w-5 h-5 text-fuchsia-400 mb-2 opacity-70" />
                    <p className="text-[10px] font-mono text-neutral-400 tracking-wider mb-1">TOTAL EVENTS</p>
                    <p className="text-2xl font-light text-white">{summary.total_events}</p>
                  </div>
                  <div className="glass-panel p-4 bg-white/5 border-white/10 flex flex-col items-center justify-center text-center">
                    <Zap className="w-5 h-5 text-yellow-400 mb-2 opacity-70" />
                    <p className="text-[10px] font-mono text-neutral-400 tracking-wider mb-1">AVG LATENCY</p>
                    <p className="text-2xl font-light text-white">{summary.average_processing_time_ms.toFixed(1)}<span className="text-sm text-neutral-500 ml-1">ms</span></p>
                  </div>
                  <div className="glass-panel p-4 bg-white/5 border-white/10 flex flex-col items-center justify-center text-center">
                    <Cpu className="w-5 h-5 text-cyan-400 mb-2 opacity-70" />
                    <p className="text-[10px] font-mono text-neutral-400 tracking-wider mb-1">AI MODELS</p>
                    <p className="text-2xl font-light text-white">4<span className="text-sm text-neutral-500 ml-1">active</span></p>
                  </div>
                </div>

                {/* Event Breakdown */}
                <div className="mt-8">
                  <h3 className="text-xs font-mono text-neutral-400 mb-4 tracking-widest border-b border-white/10 pb-2">EVENT BREAKDOWN</h3>
                  <div className="space-y-3">
                    {Object.entries(summary.events_by_type).map(([eventType, count]) => {
                      const percentage = summary.total_events > 0 
                        ? (count / summary.total_events) * 100 
                        : 0;
                        
                      return (
                        <div key={eventType} className="flex items-center gap-4">
                          <div className="w-32 text-xs font-mono text-neutral-300 truncate" title={eventType}>
                            {eventType.replace('_', ' ').toUpperCase()}
                          </div>
                          <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${percentage}%` }}
                              transition={{ duration: 1, ease: "easeOut" }}
                              className="h-full bg-gradient-to-r from-fuchsia-500 to-cyan-400"
                            />
                          </div>
                          <div className="w-12 text-right text-xs font-mono text-fuchsia-300">
                            {count}
                          </div>
                        </div>
                      );
                    })}
                    
                    {Object.keys(summary.events_by_type).length === 0 && (
                      <div className="text-center text-neutral-500 font-mono text-sm py-4">
                        NO TELEMETRY RECORDED YET
                      </div>
                    )}
                  </div>
                </div>

              </div>
            ) : (
              <div className="text-red-400 font-mono py-8 text-center">Failed to load analytics</div>
            )}
            
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
