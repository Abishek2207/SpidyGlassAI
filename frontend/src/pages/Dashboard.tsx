import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { rootApi, api } from '../App';
import { useStore } from '../store/useStore';
import { Activity, Cpu, Wifi, Eye, Server, Database, CloudOff } from 'lucide-react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard: React.FC = () => {
  const { latency, fps, latencyHistory } = useStore();

  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await rootApi.get('/health');
      return res.data;
    },
    refetchInterval: 5000,
  });

  useQuery({
    queryKey: ['ws-stats'],
    queryFn: async () => {
      const res = await api.get('/ws/stats');
      return res.data;
    },
    refetchInterval: 10000,
  });

  const { data: systemData } = useQuery({
    queryKey: ['system-stats'],
    queryFn: async () => {
      const res = await api.get('/system');
      return res.data;
    },
    refetchInterval: 10000,
  });

  const { data: ollamaData } = useQuery({
    queryKey: ['ollama-stats'],
    queryFn: async () => {
      const res = await api.get('/ollama');
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
    { label: 'Network Mode', value: systemData?.mode === 'offline' ? 'Offline (Local AI)' : 'Online (Cloud AI)', icon: systemData?.mode === 'offline' ? CloudOff : Activity, color: systemData?.mode === 'offline' ? 'text-orange-400' : 'text-emerald-400' },
    { label: 'PyTorch Model', value: healthData?.model || 'missing', icon: Activity, color: healthData?.model === 'loaded' ? 'text-emerald-400' : 'text-orange-400' },
    { label: 'Sarvam AI', value: healthData?.sarvam || 'missing', icon: Cpu, color: healthData?.sarvam === 'connected' ? 'text-blue-400' : 'text-yellow-400' },
    { label: 'Database Status', value: healthData?.database || 'disconnected', icon: Database, color: healthData?.database === 'connected' ? 'text-green-400' : 'text-red-400' },
    { label: 'Ollama Status', value: ollamaData?.status || 'unknown', icon: Server, color: ollamaData?.status === 'online' ? 'text-green-400' : 'text-red-400' },
    { label: 'WS Latency', value: `${latency}ms`, icon: Wifi, color: 'text-purple-400' },
    { label: 'Vision FPS', value: String(fps), icon: Eye, color: 'text-pink-400' },
  ];

  const demoModeActive = healthData?.model !== 'loaded' || healthData?.sarvam !== 'connected';

  return (
    <div className="h-full flex flex-col space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {stats.map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-gray-800/50 border border-gray-700/50 backdrop-blur-xl rounded-2xl p-4 flex flex-col justify-between"
          >
            <div className="flex justify-between items-start mb-4">
              <span className="text-gray-400 text-sm font-medium">{stat.label}</span>
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <div className="flex items-end space-x-2">
              <span className="text-2xl font-bold text-white tracking-tight">
                {stat.value}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
      
      {demoModeActive && (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4 flex items-center space-x-4">
           <CloudOff className="w-6 h-6 text-orange-400" />
           <div>
             <h4 className="text-orange-400 font-semibold">Demo Mode / Offline Fallback Active</h4>
             <p className="text-sm text-orange-300/80">Running using local resources. If PyTorch is missing, gesture uses heuristics. If Sarvam is missing, LLM uses Ollama.</p>
           </div>
        </div>
      )}
      
      <div className="flex-1 bg-gray-800/50 border border-gray-700/50 backdrop-blur-xl rounded-2xl p-6 min-h-[300px] flex flex-col">
        <h3 className="text-lg font-semibold text-white mb-6">Real-time Latency (ms)</h3>
        <div className="flex-1 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis dataKey="time" stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                itemStyle={{ color: '#F3F4F6' }}
              />
              <Line 
                type="monotone" 
                dataKey="load" 
                stroke="#8B5CF6" 
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: '#8B5CF6', stroke: '#1F2937', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
