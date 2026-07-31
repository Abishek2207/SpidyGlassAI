import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { rootApi, api } from '../App';
import { useStore } from '../store/useStore';
import { Activity, Cpu, Wifi, Eye, Server, Database } from 'lucide-react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard: React.FC = () => {
  const { latency, fps, latencyHistory } = useStore();

  const { data: healthData, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await rootApi.get('/health');
      return res.data;
    },
    refetchInterval: 5000,
  });

  const { data: wsStatsData } = useQuery({
    queryKey: ['ws-stats'],
    queryFn: async () => {
      const res = await api.get('/ws/stats');
      return res.data;
    },
    refetchInterval: 10000,
  });

  // Rolling telemetry for the chart from real latency history
  const chartData = React.useMemo(() => {
    return latencyHistory.map((lat, i) => ({
      time: `T-${20 - i}`,
      load: lat,
    }));
  }, [latencyHistory]);

  const stats = [
    { label: 'PyTorch Model', value: healthData?.model || 'missing', icon: Activity, color: healthData?.model === 'loaded' ? 'text-emerald-400' : 'text-orange-400' },
    { label: 'Sarvam AI', value: healthData?.sarvam || 'missing', icon: Cpu, color: healthData?.sarvam === 'connected' ? 'text-blue-400' : 'text-yellow-400' },
    { label: 'Database Status', value: healthData?.database || 'disconnected', icon: Database, color: healthData?.database === 'connected' ? 'text-green-400' : 'text-red-400' },
    { label: 'WS Latency', value: `${latency}ms`, icon: Wifi, color: 'text-purple-400' },
    { label: 'Vision FPS', value: String(fps), icon: Eye, color: 'text-pink-400' },
    { label: 'GPU / Device', value: healthData?.gpu || 'CPU', icon: Server, color: healthData?.gpu?.includes('cuda') ? 'text-green-400' : 'text-blue-400' },
  ];

  const demoModeActive = healthData?.model !== 'loaded' || healthData?.sarvam !== 'connected';

  return (
    <div className="h-full flex flex-col space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">System Overview</h2>
          <p className="text-white/50 mt-1">Real-time production telemetry and database health</p>
        </div>
        <div className="flex items-center gap-3">
          {wsStatsData && (
            <span className="text-xs font-mono text-white/50">{wsStatsData.active_connections} WS connections</span>
          )}
          {demoModeActive && (
            <div className="px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-yellow-400 text-sm font-medium animate-pulse">
              Missing Dependencies (Degraded Mode)
            </div>
          )}
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="glass-panel p-6 rounded-2xl flex items-center justify-between group hover:bg-white/10 transition-colors"
          >
            <div>
              <p className="text-white/50 text-sm font-medium mb-1">{stat.label}</p>
              <h3 className="text-xl font-semibold capitalize">{isLoading ? '…' : stat.value}</h3>
            </div>
            <div className={`p-4 rounded-xl bg-white/5 border border-white/10 ${stat.color} group-hover:scale-110 transition-transform`}>
              <stat.icon className="w-6 h-6" />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="flex-1 glass-panel rounded-2xl p-6 mt-6 flex flex-col">
        <h3 className="text-xl font-semibold mb-4">System Load (Live Telemetry)</h3>
        <div className="flex-1 w-full relative -ml-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" tick={{ fill: 'rgba(255,255,255,0.5)' }} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fill: 'rgba(255,255,255,0.5)' }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                itemStyle={{ color: '#fff' }}
              />
              <Line type="monotone" dataKey="load" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6', strokeWidth: 0 }} activeDot={{ r: 6, fill: '#60a5fa' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
