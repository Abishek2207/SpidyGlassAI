import { motion } from 'framer-motion';
import { LayoutDashboard, Video, Mic, Globe, Settings, Cpu, Activity } from 'lucide-react';
import clsx from 'clsx';

interface SidebarProps {
  wsConnected?: boolean;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onSettingsClick?: () => void;
  onAnalyticsClick?: () => void;
}

export const Sidebar = ({ wsConnected = false, activeTab = 'Dashboard', onTabChange, onSettingsClick, onAnalyticsClick }: SidebarProps) => {
  const items = [
    { icon: LayoutDashboard, label: 'Dashboard' },
    { icon: Video, label: 'Vision Processing' },
    { icon: Mic, label: 'Audio Engine' },
    { icon: Globe, label: 'Translation' },
    { icon: Cpu, label: 'Agent Mesh' },
    { icon: Activity, label: 'Analytics', isAction: true, onClick: onAnalyticsClick },
    { icon: Settings, label: 'Preferences', isAction: true, onClick: onSettingsClick },
  ];

  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-20 lg:w-64 glass-panel rounded-3xl p-4 flex flex-col h-full gap-2 transition-all"
    >
      <div className="flex items-center gap-3 mb-4 px-2 mt-4">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-400 to-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(34,211,238,0.5)]">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <div className="hidden lg:block">
          <h1 className="text-xl font-medium tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-white to-white/50">
            SpidyGlass
          </h1>
          <span className="text-[9px] uppercase tracking-widest text-cyan-400 font-bold bg-cyan-900/30 px-2 py-0.5 rounded-full border border-cyan-500/30">
            Demo Mode
          </span>
        </div>
      </div>

      <div className="flex-1 flex flex-col gap-2">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <motion.button
              key={item.label}
              onClick={() => {
                if (item.isAction && item.onClick) {
                  item.onClick();
                } else if (onTabChange) {
                  onTabChange(item.label);
                }
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={clsx(
                "flex items-center gap-4 px-4 py-3 rounded-2xl transition-colors w-full",
                (!item.isAction && activeTab === item.label)
                  ? "bg-white/10 text-cyan-400 border border-white/10" 
                  : "hover:bg-white/5 text-neutral-400"
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium hidden lg:block tracking-wide">{item.label}</span>
            </motion.button>
          );
        })}
      </div>

      <div className="mt-auto px-2">
        <div className={`p-4 rounded-2xl border flex flex-col items-center lg:items-start gap-2 transition-all duration-500 ${
          wsConnected
            ? 'bg-gradient-to-br from-cyan-900/40 to-blue-900/40 border-cyan-500/20'
            : 'bg-gradient-to-br from-red-900/30 to-neutral-900/40 border-red-500/20'
        }`}>
          <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.8)]' : 'bg-red-400'}`}></div>
          <p className="text-xs text-cyan-200/80 hidden lg:block font-mono">
            {wsConnected ? <>System Online<br/>Neural Mesh Active</> : <>Connecting...<br/>Backend Offline</>}
          </p>
        </div>
      </div>
    </motion.div>
  );
};
