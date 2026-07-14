```typescript
// src/types.ts

export type User = {
  id: string;
  pseudo: string;
  plan: 'free' | 'pro';
  // Add other potential user fields here if known
};

export type SynthesisResponse = {
  ok: boolean;
  synthesis: string;
  fullText: string;
  // Add other potential response fields here
};

export type LoginResponse = {
  ok: boolean;
  access_token: string;
  refresh_token: string;
  // Add other potential login fields here
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
  transit_date: string; // e.g., ISO date string
  transit_time: string; // e.g., HH:mm
  transit_location: string;
};
```

```typescript
// src/env.d.ts

// Astro ambient declarations
declare module 'astro/types';

// Define the environment variable type
declare namespace App {
  /**
   * The public API URL for external services.
   */
  export const PUBLIC_API_URL: string;
}
```