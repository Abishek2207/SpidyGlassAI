import { create } from 'zustand';
import { getSettings, updateSettings } from '../services/api';
import type { UserSettings } from '../services/api';

interface SettingsState {
  settings: UserSettings | null;
  isLoading: boolean;
  error: string | null;
  fetchSettings: () => Promise<void>;
  updateSettings: (data: Partial<UserSettings>) => Promise<void>;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  settings: null,
  isLoading: false,
  error: null,
  fetchSettings: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await getSettings();
      set({ settings: data, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  },
  updateSettings: async (data: Partial<UserSettings>) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await updateSettings(data);
      set({ settings: updated, isLoading: false });
    } catch (err: any) {
      set({ error: err.message, isLoading: false });
    }
  }
}));
