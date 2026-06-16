// src/env.d.ts

/// <reference types="astro/client" />
/// <reference types="astro/build" />

declare namespace Environment {
  interface ProcessEnv {
    readonly PUBLIC_API_URL: string;
  }
}