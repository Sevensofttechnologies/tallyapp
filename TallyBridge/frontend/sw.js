const CACHE_NAME = 'appkit-v4';
const urlsToCache = [
  '/frontend/',
  '/frontend/index.html',
  '/frontend/login.html',
  '/frontend/register.html',
  '/frontend/forgot-password.html',
  '/frontend/dashboard.html',
  '/frontend/users.html',
  '/frontend/companies.html',
  '/frontend/audit.html',
  '/frontend/profile.html',
  '/frontend/permissions.html',
  '/frontend/tally-sync.html',
  '/frontend/manifest.json',
  '/frontend/css/tokens.css',
  '/frontend/css/base.css',
  '/frontend/css/components.css',
  '/frontend/css/layout.css',
  '/frontend/css/admin-layout.css',
  '/frontend/css/pages/permissions.css',
  '/frontend/css/components/buttons.css',
  '/frontend/css/components/badges.css',
  '/frontend/js/config.js',
  '/frontend/js/api.js',
  '/frontend/js/auth.js',
  '/frontend/js/pwa-init.js',
  '/frontend/favicon.svg'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.filter((name) => name !== CACHE_NAME).map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Skip external URLs (fonts, CDNs, etc.) to avoid CSP issues
  const url = new URL(event.request.url);
  if (url.origin !== location.origin) {
    return; // Let browser handle external requests
  }
  
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
