// src/lib/api.ts — Client API avec gestion conditionnelle CapacitorHttp
import { Capacitor } from '@capacitor/core';
import { CapacitorHttp } from '@capacitor/core';
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

  // 🧪 Mode émulateur : Flask local via ADB reverse tcp:5001
  // Prérequis : adb reverse tcp:5001 tcp:5001 && FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
  const isEmulator = (import.meta as any).env?.PUBLIC_FIREBASE_EMULATOR === 'true';
  if (isEmulator) {
    return 'http://127.0.0.1:5001';
  }
  
  const isCapacitor = Capacitor.isNativePlatform();
  if (isCapacitor) {
    return 'https://gochara-api-drln4gv4fa-ew.a.run.app';
  }
  
  // Simplification pour le développement local web: 
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://127.0.0.1:5001';
  }

  return ((import.meta as any).env.PUBLIC_API_URL || '');
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  const isCapacitor = Capacitor.isNativePlatform();

  console.log(`📡 [API] Fetch: ${url} (isCapacitor: ${isCapacitor})`);

  // Récupérer le token et les paramètres IA locaux
  const token = typeof window !== 'undefined' ? localStorage.getItem('karmic_token') : null;
  let customBody = options?.body;
  
  if (typeof window !== 'undefined' && options?.body && typeof options.body === 'string') {
    try {
      const storedAI = localStorage.getItem('karmic_ai_settings');
      if (storedAI) {
        const settings = JSON.parse(storedAI);
        if (settings.useLocal) {
          const parsedBody = JSON.parse(options.body);
          parsedBody.user_provider = 'local';
          customBody = JSON.stringify(parsedBody);
        }
      }
    } catch (e) {
      // Ignorer si JSON invalide
    }
  }

  const headers = {
    'Content-Type': 'application/json',
    'Referer': 'https://karmic-gochara.app',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options?.headers
  } as any;

  // Utiliser CapacitorHttp pour tout (incluant REST Firestore)
  if (isCapacitor) {
    try {
      const response = await CapacitorHttp.request({
        method: (options?.method as any) || 'GET',
        url: url,
        headers: headers,
        data: customBody ? JSON.parse(customBody as string) : undefined,
        connectTimeout: 15000,
        readTimeout: 15000,
      });

      if (response.status < 200 || response.status >= 300) {
        console.warn(`📡 [API] HTTP ${response.status} sur ${path}:`, response.data);
        const errorData = typeof response.data === 'string' ? response.data : JSON.stringify(response.data);
        throw new ApiError(response.status, errorData || 'Erreur serveur');
      }

      // Si la réponse contient un nouveau token, on le stocke
      if (response.data && (response.data as any).access_token) {
        localStorage.setItem('karmic_token', (response.data as any).access_token);
      }

      console.log(`📡 [API] HTTP ${response.status} sur ${path} OK`);
      return response.data as T;
    } catch (err) {
      console.error('API FETCH ERROR:', err);
      throw err;
    }
  } else {
    // Fallback standard pour le web
    const res = await fetch(url, {
      headers: headers,
      credentials: 'include',
      ...options,
      body: customBody,
    });

    if (!res.ok) {
      const msg = await res.text().catch(() => '');
      throw new ApiError(res.status, msg || 'Erreur serveur');
    }

    const data = await res.json();
    if (data && data.access_token) {
      localStorage.setItem('karmic_token', data.access_token);
    }
    return data as T;
  }
}

// Streaming via fetch + ReadableStream (remplace EventSource)
async function* streamingRequest(path: string, body: Record<string, unknown>) {
  const url = `${getBaseUrl()}${path}`;
  
  if (typeof window !== 'undefined') {
    try {
      const storedAI = localStorage.getItem('karmic_ai_settings');
      if (storedAI) {
        const settings = JSON.parse(storedAI);
        if (settings.useLocal) {
          body.user_provider = 'local';
        }
      }
    } catch (e) {}
  }

  const res = await fetch(url, {
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
  setLang(lang: string) {
    return request<{ ok: boolean; lang: string }>('/set_lang', {
      method: 'POST',
      body: JSON.stringify({ lang }),
    });
  },

  login(pseudo: string) {
    return request<{ ok: boolean; pseudo?: string; profile?: any; hook_natal?: string; error?: string }>(
      '/login',
      { method: 'POST', body: JSON.stringify({ pseudo }) }
    );
  },

  loginFirebase(email: string, idToken: string) {
    return request<{ ok: boolean; needs_register?: boolean; pseudo?: string; profile?: any; error?: string }>(
      '/api/login_firebase',
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

  calculate(body: { pseudo: string; transit_date: string; transit_time: string; transit_location?: string; reading_type?: 'daily' | 'full' }) {
    return streamingRequest('/v2/calculate', body);
  },

  synthesisPrompt(body: { context: string; date?: string; hour?: number; minute?: number; reading_type?: 'daily' | 'full'; is_local?: boolean }) {
    return request<{ ok: boolean; system: string; user: string; error?: string }>('/synthesis/prompt', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  stripeCheckout(product_type: string) {
    return request<{ ok: boolean; beta: boolean; checkout_url?: string }>('/stripe/checkout', {
      method: 'POST',
      body: JSON.stringify({ product_type }),
    });
  },

  geocode(query: string) {
    return request<Array<{ display_name: string; lat: string; lon: string; tz: string }>>(`/geocode?q=${encodeURIComponent(query)}`);
  },

  getCalendarUrl(pseudo: string): string {
    return `${getBaseUrl()}/api/calendar/${encodeURIComponent(pseudo)}.ics`;
  },

  async getChartSvg(date?: string, hour?: number, minute?: number): Promise<string> {
    let query = '';
    if (date) {
      query = `?date=${date}&hour=${hour || 12}&minute=${minute || 0}`;
    }
    const url = `${getBaseUrl()}/chart/karmic.svg${query}`;
    const token = typeof window !== 'undefined' ? localStorage.getItem('karmic_token') : null;
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
    
    if (Capacitor.isNativePlatform()) {
      const response = await CapacitorHttp.request({
        method: 'GET',
        url: url,
        headers: headers,
        connectTimeout: 15000,
      });
      if (response.status < 200 || response.status >= 300) throw new Error('API Error fetch SVG');
      return response.data as string;
    } else {
      const res = await fetch(url, { headers, credentials: 'include' });
      if (!res.ok) throw new Error('API Error fetch SVG');
      return await res.text();
    }
  },
};

export { ApiError };
