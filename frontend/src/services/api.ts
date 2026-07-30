import { useAuthStore } from '../store/authStore';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = useAuthStore.getState().token;
  if (!token) {
    throw new Error('Not authenticated');
  }

  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${token}`);
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      useAuthStore.getState().logout();
    }
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'API Request failed');
  }

  return response.json();
}

// ── Settings API ───────────────────────────────────────────────────────────
export interface UserSettings {
  preferred_language: string;
  tts_speaker: string;
  tts_speed: string;
  gesture_sensitivity: string;
  extra?: Record<string, any>;
}

export const getSettings = (): Promise<UserSettings> => {
  return fetchWithAuth('/settings/');
};

export const updateSettings = (data: Partial<UserSettings>): Promise<UserSettings> => {
  return fetchWithAuth('/settings/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
};

// ── Analytics API ──────────────────────────────────────────────────────────
export interface AnalyticsSummary {
  user_id: number;
  total_events: number;
  events_by_type: Record<string, number>;
  average_processing_time_ms: number;
}

export const getAnalyticsSummary = (): Promise<AnalyticsSummary> => {
  return fetchWithAuth('/analytics/summary');
};
