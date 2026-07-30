import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, X, Save } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';
import type { UserSettings } from '../services/api';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal = ({ isOpen, onClose }: SettingsModalProps) => {
  const { settings, isLoading, fetchSettings, updateSettings } = useSettingsStore();

  useEffect(() => {
    if (isOpen && !settings) {
      fetchSettings();
    }
  }, [isOpen, settings, fetchSettings]);

  const handleChange = (key: keyof UserSettings, value: string) => {
    updateSettings({ [key]: value });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="w-full max-w-lg glass-panel p-8 relative shadow-[0_0_50px_rgba(34,211,238,0.15)]"
          >
            <button
              onClick={onClose}
              className="absolute top-6 right-6 text-neutral-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="flex items-center gap-4 mb-8">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 flex items-center justify-center border border-cyan-500/30">
                <Settings className="w-6 h-6 text-cyan-400" />
              </div>
              <div>
                <h2 className="text-2xl font-light tracking-wide text-white">System Settings</h2>
                <p className="text-sm font-mono text-cyan-500/70">NEURAL LINK PREFERENCES</p>
              </div>
            </div>

            {isLoading && !settings ? (
              <div className="flex flex-col items-center justify-center py-12 text-cyan-400">
                <div className="w-8 h-8 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin mb-4"></div>
                <p className="font-mono text-sm tracking-widest">LOADING PREFERENCES...</p>
              </div>
            ) : settings ? (
              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-mono text-neutral-400 mb-2">PREFERRED LANGUAGE</label>
                  <select 
                    value={settings.preferred_language}
                    onChange={(e) => handleChange('preferred_language', e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500/50 appearance-none font-light"
                  >
                    <option value="en-US">English (US)</option>
                    <option value="hi-IN">Hindi (India)</option>
                    <option value="es-ES">Spanish (Spain)</option>
                    <option value="fr-FR">French (France)</option>
                    <option value="ja-JP">Japanese (Japan)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-mono text-neutral-400 mb-2">TTS SPEAKER VOICE</label>
                  <select 
                    value={settings.tts_speaker}
                    onChange={(e) => handleChange('tts_speaker', e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500/50 appearance-none font-light"
                  >
                    <option value="meera">Meera (Female, IN)</option>
                    <option value="arjun">Arjun (Male, IN)</option>
                    <option value="sarah">Sarah (Female, US)</option>
                    <option value="michael">Michael (Male, US)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-mono text-neutral-400 mb-2">TTS SPEED ({settings.tts_speed}x)</label>
                  <input 
                    type="range" 
                    min="0.5" max="2.0" step="0.1"
                    value={settings.tts_speed}
                    onChange={(e) => handleChange('tts_speed', e.target.value)}
                    className="w-full accent-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-mono text-neutral-400 mb-2">GESTURE SENSITIVITY ({settings.gesture_sensitivity})</label>
                  <input 
                    type="range" 
                    min="0.1" max="1.0" step="0.1"
                    value={settings.gesture_sensitivity}
                    onChange={(e) => handleChange('gesture_sensitivity', e.target.value)}
                    className="w-full accent-cyan-500"
                  />
                </div>

              </div>
            ) : (
              <div className="text-red-400 font-mono py-8 text-center">Failed to load settings</div>
            )}
            
            <div className="mt-8 flex justify-end">
              <button 
                onClick={onClose}
                className="px-6 py-2 glass-pill bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 transition-all font-medium flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Done
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
