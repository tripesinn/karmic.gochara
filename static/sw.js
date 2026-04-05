const CACHE = 'gochara-v1';
const PRECACHE = ['/', '/static/icons/icon-192.png', '/static/icons/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', e => {
  // Réseau en priorité, cache en fallback (app dynamique)
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
