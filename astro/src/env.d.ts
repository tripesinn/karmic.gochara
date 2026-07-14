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