import React from 'react';
import { Save } from 'lucide-react';
import { useStore } from '../store/useStore';

const Settings: React.FC = () => {
  const { isDemoMode, setDemoMode } = useStore();

  return (
    <div className="h-full flex flex-col space-y-6">
      <header>
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">Configuration</h2>
        <p className="text-white/50 mt-1">Platform settings and hardware preferences</p>
      </header>

      <div className="flex-1 glass-panel rounded-3xl p-8 max-w-2xl">
        <div className="space-y-8">
          <section>
            <h3 className="text-xl font-semibold mb-4 border-b border-white/10 pb-2">Global Settings</h3>
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
              <div>
                <h4 className="font-medium text-white">Demo Mode</h4>
                <p className="text-sm text-white/50 mt-1">Enable fallback simulations for API endpoints</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer" 
                  checked={isDemoMode}
                  onChange={(e) => setDemoMode(e.target.checked)}
                />
                <div className="w-11 h-6 bg-white/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
              </label>
            </div>
          </section>

          <section>
            <h3 className="text-xl font-semibold mb-4 border-b border-white/10 pb-2">Hardware</h3>
            <div className="space-y-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm text-white/70">Primary Camera Source</label>
                <select className="bg-black/40 border border-white/10 rounded-lg p-3 text-white outline-none focus:border-blue-500/50">
                  <option>Integrated Webcam</option>
                  <option>External Capture Card</option>
                </select>
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm text-white/70">Audio Input Device</label>
                <select className="bg-black/40 border border-white/10 rounded-lg p-3 text-white outline-none focus:border-blue-500/50">
                  <option>Default Microphone Array</option>
                  <option>External USB Mic</option>
                </select>
              </div>
            </div>
          </section>
        </div>
        
        <div className="mt-12 flex justify-end">
          <button className="flex items-center gap-2 px-6 py-3 bg-white text-black font-semibold rounded-full hover:bg-gray-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.2)]">
            <Save className="w-5 h-5" />
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
