import { motion } from 'framer-motion';
import { Cpu, Activity, Terminal } from 'lucide-react';
import type { TelemetryPayload } from '../types';

interface RightPanelProps {
  telemetry?: TelemetryPayload | null;
  logs?: any[];
}

export const RightPanel = ({ telemetry, logs = [] }: RightPanelProps) => {
  const agents = telemetry?.agents || {};
  const sys = telemetry?.system || { fps: 0, gpu_utilization: 0, battery: 0, latency_ms: 0 };

  return (
    <motion.div 
      initial={{ x: 50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-full lg:w-80 flex flex-col gap-4 h-full overflow-y-auto pr-2"
    >
      {/* System Status Widget */}
      <div className="glass-panel rounded-3xl p-5 border border-white/5 bg-gradient-to-br from-white/5 to-transparent">
        <h3 className="text-sm font-semibold tracking-widest text-neutral-400 uppercase mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4" /> Core Telemetry
        </h3>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-black/40 p-3 rounded-2xl border border-white/5">
            <p className="text-xs text-neutral-500 font-mono">CPU</p>
            <p className="text-xl font-light text-cyan-400">{sys.cpu_utilization?.toFixed(1) || 0}%</p>
          </div>
          <div className="bg-black/40 p-3 rounded-2xl border border-white/5">
            <p className="text-xs text-neutral-500 font-mono">FPS</p>
            <p className="text-xl font-light text-white">{sys.fps}</p>
          </div>
          <div className="bg-black/40 p-3 rounded-2xl border border-white/5">
            <p className="text-xs text-neutral-500 font-mono">RAM</p>
            <p className="text-xl font-light text-green-400">{sys.ram_utilization?.toFixed(1) || 0}%</p>
          </div>
          <div className="bg-black/40 p-3 rounded-2xl border border-white/5">
            <p className="text-xs text-neutral-500 font-mono">LATENCY</p>
            <p className="text-xl font-light text-yellow-400">{sys.latency_ms}ms</p>
          </div>
        </div>
      </div>

      {/* Agents Mesh Status */}
      <div className="glass-panel rounded-3xl p-5 flex-1 border border-white/5 relative">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-semibold tracking-widest text-neutral-400 uppercase flex items-center gap-2">
            <Cpu className="w-4 h-4" /> Agent Mesh
          </h3>
          <button 
            onClick={() => {
              const backendUrl = import.meta.env.VITE_API_URL || 'https://spidyglassai.onrender.com';
              fetch(`${backendUrl}/api/cron/cleanup`, { 
                method: 'POST', 
                headers: { 'Authorization': 'Bearer spiderglass-local-cron' }
              }).then(res => res.json()).then(data => alert(data.message)).catch(e => console.error(e));
            }}
            className="text-[10px] uppercase font-bold tracking-widest text-red-400 bg-red-400/10 hover:bg-red-400/20 px-3 py-1 rounded-full transition-colors border border-red-500/20"
          >
            Clear Cache
          </button>
        </div>
        
        <div className="flex flex-col gap-3">
          {Object.entries(agents).map(([name, data]) => (
            <motion.div 
              key={name}
              layout
              className="bg-white/5 rounded-2xl p-3 border border-white/5 relative overflow-hidden"
            >
              <div className="flex justify-between items-center mb-2">
                <span className="capitalize text-sm font-medium tracking-wide">{name} Agent</span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                  data.status === 'online' || data.status === 'active' || data.status === 'listening' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 
                  'bg-neutral-800 text-neutral-400 border border-neutral-700'
                }`}>
                  {data.status}
                </span>
              </div>
              
              <div className="flex justify-between items-end text-[10px] font-mono text-neutral-400 mt-2">
                <span>Task: <span className="text-white">{data.task || 'Idle'}</span></span>
                <span>Lat: {data.latency_ms || 0}ms</span>
              </div>
              
              <div className="flex justify-between items-end text-[9px] font-mono text-neutral-500 mt-1">
                <span>Conf: {((data.confidence || 0) * 100).toFixed(1)}%</span>
                <span>Update: {data.last_update ? new Date(data.last_update * 1000).toLocaleTimeString() : 'N/A'}</span>
              </div>

              {/* Animated progress bar for confidence */}
              <div className="absolute bottom-0 left-0 h-[2px] bg-cyan-500/50" style={{ width: `${data.confidence * 100}%` }}></div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* System Logs */}
      <div className="glass-panel rounded-3xl p-5 border border-white/5 relative mt-4 mb-4 flex-shrink-0 min-h-[200px]">
        <h3 className="text-sm font-semibold tracking-widest text-neutral-400 uppercase flex items-center gap-2 mb-4">
          <Terminal className="w-4 h-4" /> System Logs
        </h3>
        <div className="space-y-2 h-[150px] overflow-y-auto pr-2">
          {logs.length === 0 ? (
            <p className="text-neutral-500 font-mono text-xs text-center py-4">Waiting for system events...</p>
          ) : (
            logs.map((log, i) => {
              const level = log.level || 'info';
              const levelColor =
                level === 'warn'  ? 'text-yellow-400' :
                level === 'error' ? 'text-red-400'    :
                level === 'debug' ? 'text-neutral-500' :
                'text-cyan-400';
              const moduleColor =
                log.module === 'vision'       ? 'bg-cyan-900/40 text-cyan-300 border-cyan-500/20'   :
                log.module === 'speech'       ? 'bg-green-900/40 text-green-300 border-green-500/20' :
                log.module === 'translation'  ? 'bg-blue-900/40 text-blue-300 border-blue-500/20'   :
                log.module === 'conversation' ? 'bg-purple-900/40 text-purple-300 border-purple-500/20' :
                log.module === 'device'       ? 'bg-orange-900/40 text-orange-300 border-orange-500/20' :
                'bg-white/5 text-neutral-400 border-white/10';
              return (
                <div key={i} className="text-[10px] font-mono p-2 rounded-lg bg-black/40 border border-white/5 leading-relaxed">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-neutral-600">{new Date(log.timestamp * 1000).toLocaleTimeString()}</span>
                    {log.module && (
                      <span className={`px-1 py-0.5 rounded border text-[8px] uppercase tracking-widest ${moduleColor}`}>
                        {log.module}
                      </span>
                    )}
                    <span className={`text-[8px] uppercase tracking-widest ${levelColor}`}>{level}</span>
                  </div>
                  <span className="text-neutral-300">{log.message}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </motion.div>
  );
};
