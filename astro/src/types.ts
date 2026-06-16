// src/types.ts

export type User = {
  id: string;
  pseudo: string;
  plan: 'free' | 'pro';
};

export type SynthesisResponse = {
  ok: boolean;
  synthesis: string;
  fullText: string;
};

export type LoginResponse = {
  ok: boolean;
  pseudo?: string;
  profile?: any;
  hook_natal?: string;
  hook_engine?: string;
};

export type RegisterData = {
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
};

export type CalculateBody = {
  pseudo: string;
  transit_date: string;
  transit_time: string;
  transit_location: string;
};
