// ── RocketCanvas Service Worker ──────────────────────────────────────
// Bumped to purge per-user HTML pages cached by earlier versions.
const CACHE_VERSION = 'rc-v5';
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

  // Only handle same-origin requests; let the browser deal with CDNs.
  if (new URL(request.url).origin !== self.location.origin) return;

  // Navigation requests (HTML pages) → network only, offline page as fallback.
  // Pages are per-user (profile, match history), so they are never cached:
  // a cached copy would outlive logout and be visible to the next person
  // using the device.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match('/offline'))
    );
    return;
  }

  // Shared static assets → cache-first. User uploads are excluded so a
  // replaced/deleted avatar or design isn't served from cache forever.
  const path = new URL(request.url).pathname;
  if (path.startsWith('/static/') && !path.startsWith('/static/uploads/')) {
    event.respondWith(
      caches.match(request)
        .then((cached) => {
          if (cached) return cached;
          return fetch(request).then((response) => {
            // Don't cache 404s/500s or redirects as if they were the asset.
            if (response.ok) {
              const clone = response.clone();
              caches.open(CACHE_VERSION).then((cache) => cache.put(request, clone));
            }
            return response;
          });
        })
    );
    return;
  }

  // Everything else (API/JSON, uploads) → straight to the network.
});
