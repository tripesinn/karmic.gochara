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
    "tailwindcss": "latest",
    "typescript": "latest"
  },
  "devDependencies": {
    "@types/node": "latest",
    "typescript": "latest"
  }
}
```

```env
PUBLIC_API_URL=https://gochara-api-drln4gv4fa-ew.a.run.app
PUBLIC_CAPACITOR_API_URL=https://gochara-api-drln4gv4fa-ew.a.run.app

# Local dev default = /api (same origin)
```