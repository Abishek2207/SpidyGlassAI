import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Eye, 
  Mic, 
  Languages, 
  Bot, 
  Network, 
  Terminal, 
  Settings 
} from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/vision', label: 'Vision Processing', icon: Eye },
  { path: '/speech', label: 'Speech Engine', icon: Mic },
  { path: '/translation', label: 'Translation', icon: Languages },
  { path: '/assistant', label: 'AI Assistant', icon: Bot },
  { path: '/mesh', label: 'Agent Mesh', icon: Network },
  { path: '/logs', label: 'Logs', icon: Terminal },
  { path: '/settings', label: 'Settings', icon: Settings },
];

const Sidebar: React.FC = () => {
  return (
    <div className="w-64 h-full p-6 flex flex-col border-r border-white/5 bg-black/40 backdrop-blur-3xl z-10">
      <div className="flex items-center gap-3 mb-10 mt-2 px-2">
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 shadow-[0_0_15px_rgba(59,130,246,0.5)] flex items-center justify-center">
          <span className="font-bold text-sm tracking-tighter">SG</span>
        </div>
        <h1 className="text-xl font-semibold tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
          SpidyGlass
        </h1>
      </div>

      <nav className="flex-1 space-y-2 relative">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 relative group ${
                  isActive 
                    ? 'text-white bg-white/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]' 
                    : 'text-white/50 hover:text-white/90 hover:bg-white/5'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={`w-5 h-5 transition-colors ${isActive ? 'text-blue-400' : 'text-white/40 group-hover:text-white/70'}`} />
                  <span className="font-medium text-sm">{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 border border-white/20 rounded-xl pointer-events-none"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>
      
      <div className="mt-auto pt-6 border-t border-white/10">
        <div className="px-4 py-3 rounded-xl bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/20">
          <p className="text-xs text-blue-200 font-medium">Demo Mode Active</p>
          <p className="text-[10px] text-blue-200/50 mt-1">Prototype V1.0</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
