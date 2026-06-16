// src/lib/types.ts — Types partagés API

export interface User {
  id: string;
  pseudo: string;
  plan: 'free' | 'pro';
}

export interface RegisterData {
  pseudo: string;
  email: string;
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  city: string;
  lat: number;
  lon: number;
  tz: string;
}

export interface CalculateBody {
  pseudo: string;
  transit_date: string;
  transit_time: string;
  transit_location?: string;
}

export interface UserProfile {
  id: string;
  pseudo: string;
  plan: string;
  hook_natal?: string;
  hook_engine?: string;
}
