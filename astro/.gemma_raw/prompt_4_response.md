```typescript
// src/types.ts

export type User = {
  id: string;
  pseudo: string;
  plan: 'free' | 'pro';
  // Add other fields as necessary
};

export type SynthesisResponse = {
  ok: boolean;
  synthesis: string;
  fullText: string;
  // Add other fields as necessary
};

export type LoginResponse = {
  ok: boolean;
  access_token: string;
  refresh_token: string;
  // Add other fields as necessary
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
```

---

```typescript
// src/env.d.ts

/// <reference types="astro/client" />
/// <reference types="astro/build" />

declare namespace Environment {
  interface ProcessEnv {
    readonly PUBLIC_API_URL: string;
  }
}
```