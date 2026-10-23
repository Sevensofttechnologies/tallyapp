const CACHE_NAME = 'appkit-v2';
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
  '/frontend/favicon.svg',
  '/frontend/assets/icons/icon-192.png'
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
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
