/**
 * TallySync Service Worker
 * Provides offline support and caching for PWA
 */

const CACHE_NAME = 'tallysync-v2.0.0';
const STATIC_CACHE = 'tallysync-static-v2';
const DYNAMIC_CACHE = 'tallysync-dynamic-v2';

// Files to cache for offline use
const STATIC_FILES = [
    '/',
    '/index.html',
    '/sync.html',
    '/dashboard.html',
    '/audit.html',
    '/static/css/tally-theme.css',
    '/static/manifest.json'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('[SW] Installing Service Worker...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[SW] Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .catch((error) => {
                console.log('[SW] Cache failed:', error);
            })
    );
    self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating Service Worker...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== STATIC_CACHE && name !== DYNAMIC_CACHE && name !== CACHE_NAME)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - network-first for HTML/CSS, cache-first for other assets
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip API calls - always fetch from network
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .catch(() => {
                    return new Response(
                        JSON.stringify({ error: 'Offline - API not available' }),
                        {
                            status: 503,
                            headers: { 'Content-Type': 'application/json' }
                        }
                    );
                })
        );
        return;
    }

    // Network-first strategy for HTML and CSS (always get fresh UI)
    const isHtmlOrCss = url.pathname.endsWith('.html') || url.pathname.endsWith('.css') || url.pathname === '/';
    if (isHtmlOrCss) {
        event.respondWith(
            fetch(request)
                .then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const responseToCache = networkResponse.clone();
                        caches.open(STATIC_CACHE).then((cache) => {
                            cache.put(request, responseToCache);
                        });
                    }
                    return networkResponse;
                })
                .catch(() => caches.match(request))
        );
        return;
    }

    // Cache-first strategy for other static assets (images, fonts, etc.)
    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(request)
                    .then((networkResponse) => {
                        if (!networkResponse || networkResponse.status !== 200) {
                            return networkResponse;
                        }
                        const responseToCache = networkResponse.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then((cache) => {
                                cache.put(request, responseToCache);
                            });
                        return networkResponse;
                    })
                    .catch(() => {
                        if (request.headers.get('accept') && request.headers.get('accept').includes('text/html')) {
                            return caches.match('/index.html');
                        }
                    });
            })
    );
});

// Background sync for offline data
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);
    if (event.tag === 'sync-data') {
        event.waitUntil(syncData());
    }
});

async function syncData() {
    // Implement background sync logic here
    console.log('[SW] Syncing data in background...');
}

// Push notifications
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'New notification',
        icon: '/static/images/icon-192.png',
        badge: '/static/images/icon-72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        }
    };

    event.waitUntil(
        self.registration.showNotification('TallySync', options)
    );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/sync.html')
    );
});

console.log('[SW] Service Worker loaded');
