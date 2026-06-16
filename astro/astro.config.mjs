import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  output: 'static',
  integrations: [tailwind()],
  vite: {
    define: {
      'import.meta.env.PUBLIC_API_URL': JSON.stringify(''),
    },
    server: {
      proxy: {
        '/api': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/login': { target: 'http://127.0.0.1:5001', changeOrigin: true, bypass: (req) => { if (req.method === 'GET') return req.url; } },
        '/register': { target: 'http://127.0.0.1:5001', changeOrigin: true, bypass: (req) => { if (req.method === 'GET') return req.url; } },
        '/logout': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/calculate': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/v2/calculate': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/hook': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/chart': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/stripe': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/geocode': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/sw.js': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/chat': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/calendar': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/set_lang': { target: 'http://127.0.0.1:5001', changeOrigin: true },
        '/health': { target: 'http://127.0.0.1:5001', changeOrigin: true },
      },
    },
  },
  build: {
    outDir: '../www',
  },
});
