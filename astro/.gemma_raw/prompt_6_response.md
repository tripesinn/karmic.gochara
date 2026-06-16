astro/package.json
```json
{
  "name": "karmic-gochara-astro",
  "version": "0.1.0",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "sync:capacitor": "cp -r dist/* ../www/ && npx cap sync"
  },
  "dependencies": {
    "astro": "latest",
    "tailwindcss": "^3.0.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "astro-tailwind": "^1.0.0"
  }
}
```

astro/.env.example
```
PUBLIC_API_URL=https://gochara-api-drln4gv4fa-ew.a.run.app
PUBLIC_CAPACITOR_API_URL=https://gochara-api-drln4gv4fa-ew.a.run.app
# Local dev default = /api (same origin)
```