import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface StoreState {
  isConnected: boolean;
  isDemoMode: boolean;
  cameraActive: boolean;
  micActive: boolean;
  latency: number;
  fps: number;
  latencyHistory: number[];
  fpsHistory: number[];
  serverModelLoaded: boolean;
  sarvamConfigured: boolean;
  authToken: string | null;
  currentUser: { email: string; username: string } | null;
  setConnectionStatus: (status: boolean) => void;
  setDemoMode: (status: boolean) => void;
  setCameraActive: (status: boolean) => void;
  setMicActive: (status: boolean) => void;
  updateStats: (latency: number, fps: number) => void;
  setServerCapabilities: (model: boolean, sarvam: boolean) => void;
  setAuthToken: (token: string | null) => void;
  setCurrentUser: (user: { email: string; username: string } | null) => void;
  logout: () => void;
}

export const useStore = create<StoreState>()(
  persist(
    (set) => ({
      isConnected: false,
      isDemoMode: false,
      cameraActive: false,
      micActive: false,
      latency: 0,
      fps: 0,
      latencyHistory: Array(20).fill(0),
      fpsHistory: Array(20).fill(0),
      serverModelLoaded: false,
      sarvamConfigured: false,
      authToken: null,
      currentUser: null,
      setConnectionStatus: (status) => set({ isConnected: status }),
      setDemoMode: (status) => set({ isDemoMode: status }),
      setCameraActive: (status) => set({ cameraActive: status }),
      setMicActive: (status) => set({ micActive: status }),
      updateStats: (latency, fps) => set((state) => {
        const newLat = [...state.latencyHistory.slice(1), latency];
        const newFps = [...state.fpsHistory.slice(1), fps];
        return { latency, fps, latencyHistory: newLat, fpsHistory: newFps };
      }),
      setServerCapabilities: (model, sarvam) => set({ serverModelLoaded: model, sarvamConfigured: sarvam }),
      setAuthToken: (token) => set({ authToken: token }),
      setCurrentUser: (user) => set({ currentUser: user }),
      logout: () => set({ authToken: null, currentUser: null }),
    }),
    {
      name: 'spidyglass-store',
      partialize: (state) => ({ authToken: state.authToken, currentUser: state.currentUser }),
    }
  )
);
