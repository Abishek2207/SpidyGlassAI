/**
 * Base API Client Wrapper
 * Implements exponential backoff, retry logic, timeout handling, and global error catching.
 */

const BACKEND_URL = import.meta.env.VITE_API_URL || 'https://spidyglassai.onrender.com';

interface RequestOptions extends RequestInit {
  timeout?: number;
  retries?: number;
  backoff?: number;
}

export const fetchWithRetry = async (
  endpoint: string,
  options: RequestOptions = {}
): Promise<any> => {
  const {
    timeout = 10000,
    retries = 3,
    backoff = 500,
    ...fetchOptions
  } = options;

  const url = `${BACKEND_URL}${endpoint}`;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...fetchOptions.headers,
        },
      });

      clearTimeout(id);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error: any) {
      if (attempt === retries) {
        console.error(`[API Client] Final attempt failed for ${endpoint}:`, error);
        throw error;
      }
      
      const delay = backoff * Math.pow(2, attempt);
      console.warn(`[API Client] Attempt ${attempt + 1} failed for ${endpoint}. Retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};
