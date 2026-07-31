import React, { useEffect, useState, useRef } from 'react';
import { Terminal as TerminalIcon, RefreshCw } from 'lucide-react';
import { api } from '../App';

interface LogEntry {
  time: string;
  msg: string;
  level: string;
}

const Logs: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const endRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    try {
      // system_logs endpoint is under analytics module
      const res = await api.get('/analytics/system-logs?limit=100');
      if (res.data?.logs) {
        const mapped: LogEntry[] = res.data.logs.map((l: { created_at: string; level: string; message: string }) => ({
          time: l.created_at,
          msg: l.message,
          level: l.level,
        }));
        setLogs(mapped);
      }
    } catch {
      // If backend not authenticated or unavailable, show local events
      setLogs(prev => [
        ...prev,
        {
          time: new Date().toISOString(),
          msg: 'Backend log stream unavailable — showing local events only.',
          level: 'WARN',
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    // Poll every 10 seconds
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR': return 'text-red-400';
      case 'WARNING':
      case 'WARN': return 'text-yellow-400';
      case 'INFO': return 'text-blue-400';
      case 'DEBUG': return 'text-white/40';
      default: return 'text-white/60';
    }
  };

  return (
    <div className="h-full flex flex-col space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">System Logs</h2>
          <p className="text-white/50 mt-1">Live backend terminal output and diagnostics</p>
        </div>
        <button
          onClick={fetchLogs}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-white/70 hover:bg-white/10 transition-colors text-sm"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </header>

      <div className="flex-1 glass-panel rounded-3xl p-6 flex flex-col font-mono text-sm overflow-hidden border border-white/5">
        <div className="flex items-center gap-2 mb-4 text-white/50 border-b border-white/10 pb-4">
          <TerminalIcon className="w-5 h-5" />
          <span>spidyglass@core-node-01:~$</span>
          {isLoading && <RefreshCw className="w-3 h-3 animate-spin ml-auto" />}
        </div>
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {logs.length === 0 && !isLoading && (
            <p className="text-white/30 italic mt-6 text-center">No logs yet. Start the backend to see real-time events.</p>
          )}
          {logs.map((log, i) => (
            <div key={i} className="flex gap-4 hover:bg-white/5 px-2 py-0.5 rounded transition-colors">
              <span className="text-white/30 shrink-0">[{log.time.split('T')[1]?.split('.')[0] ?? log.time}]</span>
              <span className={`shrink-0 ${getLevelColor(log.level)}`}>[{log.level.toUpperCase()}]</span>
              <span className="text-white/80">{log.msg}</span>
            </div>
          ))}
          <div ref={endRef} />
        </div>
      </div>
    </div>
  );
};

export default Logs;
