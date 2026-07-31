import React from 'react';
import { Network, Server, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

const AgentMesh: React.FC = () => {
  const agents = [
    { name: 'Vision Agent', status: 'Active', load: '45%' },
    { name: 'Speech Agent', status: 'Idle', load: '5%' },
    { name: 'Translation Agent', status: 'Active', load: '23%' },
    { name: 'LLM Orchestrator', status: 'Active', load: '67%' }
  ];

  return (
    <div className="h-full flex flex-col space-y-6">
      <header>
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">Agent Mesh</h2>
        <p className="text-white/50 mt-1">Distributed neural orchestration</p>
      </header>

      <div className="flex-1 glass-panel rounded-3xl p-8 relative overflow-hidden flex items-center justify-center">
        {/* Mock network visualization */}
        <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
          <Network className="w-96 h-96 text-blue-500 animate-pulse" />
        </div>
        
        <div className="z-10 w-full max-w-2xl space-y-4">
          {agents.map((agent, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-black/40 backdrop-blur-md border border-white/10 rounded-2xl p-4 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <div className={`p-2 rounded-lg ${agent.status === 'Active' ? 'bg-blue-500/20 text-blue-400' : 'bg-white/5 text-white/50'}`}>
                  {agent.status === 'Active' ? <Zap className="w-5 h-5" /> : <Server className="w-5 h-5" />}
                </div>
                <div>
                  <h4 className="font-semibold text-lg">{agent.name}</h4>
                  <p className="text-xs text-white/50">Node ID: {Math.random().toString(36).substring(7).toUpperCase()}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`font-mono ${agent.status === 'Active' ? 'text-green-400' : 'text-gray-400'}`}>{agent.status}</p>
                <div className="w-24 h-1.5 bg-white/10 rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-blue-500" style={{ width: agent.load }}></div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AgentMesh;
