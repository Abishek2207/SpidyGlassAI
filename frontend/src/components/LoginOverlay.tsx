import { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Fingerprint, Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export const LoginOverlay = () => {
  const { setToken, setUser } = useAuthStore();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const API_URL = `${BASE_URL}/api/v1`;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isLogin) {
        // Login
        const response = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
          throw new Error('Authentication failed');
        }

        const data = await response.json();
        setToken(data.access_token);
        
        // Fetch user data
        const userResponse = await fetch(`${API_URL}/auth/me`, {
          headers: { 'Authorization': `Bearer ${data.access_token}` },
        });
        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUser(userData);
        }

      } else {
        // Register
        const response = await fetch(`${API_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, username, password }),
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => null);
          throw new Error(errData?.detail || 'Registration failed');
        }

        // Auto-login after registration
        setIsLogin(true);
        setError('Registration successful. Please login.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md p-8 rounded-3xl glass-panel relative overflow-hidden"
      >
        {/* Glow Effects */}
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl"></div>
        
        <div className="relative z-10 flex flex-col items-center">
          <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(6,182,212,0.3)]">
            <Shield className="w-8 h-8 text-cyan-400" />
          </div>
          
          <h2 className="text-2xl font-light text-white mb-2 tracking-wide">
            {isLogin ? 'SYSTEM ACCESS' : 'INITIALIZE AGENT'}
          </h2>
          <p className="text-sm text-neutral-400 font-mono mb-8 tracking-widest text-center">
            {isLogin ? 'SECURE IDENTITY VERIFICATION' : 'CREATE BIOMETRIC PROFILE'}
          </p>

          <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
            {!isLogin && (
              <div className="relative">
                <input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="AGENT ALIAS"
                  required
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-neutral-500 focus:outline-none focus:border-cyan-500/50 transition-colors font-mono text-sm"
                />
              </div>
            )}
            <div className="relative">
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="IDENTITY STREAM (EMAIL)"
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-neutral-500 focus:outline-none focus:border-cyan-500/50 transition-colors font-mono text-sm"
              />
            </div>
            <div className="relative">
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="ACCESS KEY (PASSWORD)"
                required
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-neutral-500 focus:outline-none focus:border-cyan-500/50 transition-colors font-mono text-sm"
              />
            </div>

            {error && (
              <div className="text-red-400 text-xs font-mono text-center bg-red-500/10 py-2 rounded-lg border border-red-500/20">
                {error}
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="mt-4 w-full relative group overflow-hidden rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 transition-all duration-300 py-3 flex items-center justify-center gap-3"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
              ) : (
                <>
                  <Fingerprint className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
                  <span className="text-cyan-400 font-mono tracking-widest text-sm">
                    {isLogin ? 'AUTHENTICATE' : 'INITIALIZE'}
                  </span>
                </>
              )}
            </button>
          </form>

          <button 
            onClick={() => { setIsLogin(!isLogin); setError(null); }}
            className="mt-6 text-xs text-neutral-500 hover:text-cyan-400 transition-colors font-mono uppercase tracking-wider"
          >
            {isLogin ? 'Request Agent Provisioning (Register)' : 'Return to Authorization (Login)'}
          </button>
        </div>
      </motion.div>
    </div>
  );
};
