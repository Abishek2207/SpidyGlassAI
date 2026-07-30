import { create } from 'zustand';

interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('spiderglass_token') || null,
  user: null,
  setToken: (token) => {
    if (token) {
      localStorage.setItem('spiderglass_token', token);
    } else {
      localStorage.removeItem('spiderglass_token');
    }
    set({ token });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('spiderglass_token');
    set({ token: null, user: null });
  },
}));
