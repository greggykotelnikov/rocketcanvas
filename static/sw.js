// ── RocketCanvas Service Worker ──────────────────────────────────────
const CACHE_VERSION = 'rc-v4';
const PRECACHE_URLS = [
  '/offline',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png',
  '/static/images/logo.png'
];

// ── Install: precache essential assets ──────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// ── Activate: clean up old caches ───────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) => key !== CACHE_VERSION)
          .map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

// ── Fetch: network-first for pages, cache-first for static assets ──
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Navigation requests (HTML pages) → network-first
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache a copy of successful responses
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() => {
          // Try cache, then fall back to offline page
          return caches.match(request, { ignoreSearch: true })
            .then((cached) => cached || caches.match('/offline', { ignoreSearch: true }));
        })
    );
    return;
  }

  // Static assets → cache-first
  if (request.url.includes('/static/')) {
    event.respondWith(
      caches.match(request, { ignoreSearch: true })
        .then((cached) => {
          if (cached) return cached;
          return fetch(request).then((response) => {
            const clone = response.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
            return response;
          }).catch(() => null);
        })
    );
    return;
  }

  // Everything else → network-first with cache fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        const clone = response.clone();
        caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
        return response;
      })
      .catch(() => caches.match(request, { ignoreSearch: true }))
  );
});
