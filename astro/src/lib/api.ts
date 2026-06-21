// src/lib/api.ts — Client API avec sessions Flask (cookies)
// Auth gérée par le cookie de session Flask — pas de JWT localStorage
import { Capacitor } from '@capacitor/core';
import type { RegisterData } from './types';

class ApiError extends Error {
  public data: any = null;
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    try {
      this.data = JSON.parse(message);
    } catch {
      this.data = null;
    }
  }
}

function getBaseUrl(): string {
  if (typeof window === 'undefined') return '';
  const isCapacitor = Capacitor.isNativePlatform();
  return isCapacitor
    ? 'https://gochara-api-732214018947.europe-west1.run.app'
    : (import.meta.env.PUBLIC_API_URL || '');
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${getBaseUrl()}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    credentials: 'include',
    ...options,
  });

  if (!res.ok) {
    const msg = await res.text().catch(() => '');
    throw new ApiError(res.status, msg || 'Erreur serveur');
  }

  return res.json() as Promise<T>;
}

// Streaming via fetch + ReadableStream (remplace EventSource)
async function* streamingRequest(path: string, body: Record<string, unknown>) {
  const res = await fetch(`${getBaseUrl()}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new ApiError(res.status, await res.text().catch(() => ''));

  const reader = res.body?.getReader();
  if (!reader) throw new ApiError(0, 'No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          yield JSON.parse(line.slice(6));
        } catch {
          yield { text: line.slice(6) };
        }
      }
    }
  }
}

export const api = {
  login(pseudo: string) {
    return request<{ ok: boolean; pseudo?: string; profile?: any; hook_natal?: string; error?: string }>(
      '/login',
      { method: 'POST', body: JSON.stringify({ pseudo }) }
    );
  },

  loginFirebase(email: string, idToken: string) {
    return request<{ ok: boolean; needs_register?: boolean; pseudo?: string; profile?: any; error?: string }>(
      '/login_firebase',
      { method: 'POST', body: JSON.stringify({ email, idToken }) }
    );
  },

  register(data: RegisterData) {
    return request<{ ok: boolean; pseudo?: string; profile?: any; error?: string }>(
      '/register',
      { method: 'POST', body: JSON.stringify(data) }
    );
  },

  logout() {
    return request<{ ok: boolean }>('/logout', { method: 'POST' });
  },

  profile() {
    return request<{ ok: boolean; profile?: any }>('/api/profile');
  },

  calculate(body: { pseudo: string; transit_date: string; transit_time: string; transit_location?: string }) {
    return streamingRequest('/calculate', body);
  },

  stripeCheckout(product_type: string) {
    return request<{ ok: boolean; beta: boolean; checkout_url?: string }>('/stripe/checkout', {
      method: 'POST',
      body: JSON.stringify({ product_type }),
    });
  },

  geocode(query: string) {
    return request<Array<{ display_name: string; lat: string; lon: string }>>(`/geocode?q=${encodeURIComponent(query)}`);
  },
};

export { ApiError };
