```javascript
// tailwind.config.mjs
import { defineConfig } from 'tailwindcss';

export default defineConfig({
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
});
```

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  output: 'static',
  integrations: [tailwind()],
  vite: {
    define: {
      'import.meta.env.PUBLIC_API_URL': 'https://api.example.com', // Placeholder for actual environment variable
    },
  },
  build: {
    outDir: '../www', // For Capacitor sync
  },
});
```