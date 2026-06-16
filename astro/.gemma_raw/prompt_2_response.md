```mjs
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        cosmic: {
          bg: '#0c0a08',
          gold: '#c9a84c',
          'gold-dim': '#8a6f30',
          text: '#f5f0e8',
          'text-dim': '#8a8678',
          border: '#2a2820',
          void: '#1a1410',
        },
      },
      fontFamily: {
        display: ['Cinzel', 'serif'],
        body: ['Cormorant Garamond', 'serif'],
        mono: ['DM Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
```

```mjs
import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  output: 'static',
  integrations: [tailwind()],
  vite: {
    define: {
      'import.meta.env.PUBLIC_API_URL': JSON.stringify('YOUR_API_URL_HERE'),
    },
  },
  build: {
    outDir: '../www',
  },
});
```