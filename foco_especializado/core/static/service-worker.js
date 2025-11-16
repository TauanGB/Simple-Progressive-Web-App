/**
 * Service Worker do PWA "3 Coisas de Hoje".
 * Estratégia híbrida:
 * - Cache first para assets estáticos
 * - Network first para HTML e APIs (JSON)
 * - Fallback offline para navegação
 * - Push Notifications (quando suportado)
 */

const CACHE_VERSION = '3coisas-pwa-v20251115';
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const RUNTIME_CACHE = `runtime-${CACHE_VERSION}`;
const OFFLINE_FALLBACK_URL = '/offline/';

const STATIC_CACHE_URLS = [
  '/',
  OFFLINE_FALLBACK_URL,
  '/static/css/app.css',
  '/static/js/pwa-install.js',
  '/static/icon-192.png',
  '/static/icon-384.png',
  '/static/icon-512.png',
  '/static/icons/apple-touch-icon.png',
  '/static/manifest.json',
];

const STATIC_PATH_HINTS = [
  '/static/css/',
  '/static/js/',
  '/static/icon-',
  '/static/fonts/',
  '/static/manifest.json',
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_CACHE_URLS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) =>
        Promise.all(
          cacheNames
            .filter((cacheName) => !cacheName.includes(CACHE_VERSION))
            .map((cacheName) => caches.delete(cacheName))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);

  if (!url.protocol.startsWith('http')) {
    return;
  }

  if (url.origin !== self.location.origin) {
    return;
  }

  if (isStaticAsset(request)) {
    event.respondWith(cacheFirstStrategy(request));
    return;
  }

  if (isApiRequest(request)) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  if (request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(networkFirstStrategy(request, { offlineFallback: true }));
  }
});

function isStaticAsset(request) {
  const url = request.url;
  return STATIC_PATH_HINTS.some((path) => url.includes(path));
}

function isApiRequest(request) {
  const acceptHeader = request.headers.get('accept') || '';
  return (
    request.url.includes('/api/') ||
    acceptHeader.includes('application/json')
  );
}

async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const response = await fetch(request);
    if (response && response.status === 200) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    return new Response('offline', { status: 503 });
  }
}

async function networkFirstStrategy(request, options = {}) {
  try {
    const response = await fetch(request);
    if (response && response.status === 200) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    if (options.offlineFallback) {
      return caches.match(OFFLINE_FALLBACK_URL) || getInlineOfflinePage();
    }
    return new Response('offline', { status: 503 });
  }
}

async function getInlineOfflinePage() {
  return new Response(
    `
    <!DOCTYPE html>
    <html lang="pt-BR">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Sem conexão - 3 Coisas de Hoje</title>
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 24px;
            background: #0f172a;
            color: #fff;
            text-align: center;
          }
          button {
            margin-top: 16px;
            padding: 12px 20px;
            border-radius: 999px;
            border: none;
            background: #38bdf8;
            color: #0f172a;
            font-weight: 600;
          }
        </style>
      </head>
      <body>
        <h1>Sem conexão 😴</h1>
        <p>Assim que voltar para o online, suas tarefas serão sincronizadas.</p>
        <button onclick="window.location.reload()">Tentar novamente</button>
      </body>
    </html>
  `,
    {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      },
    }
  );
}

self.addEventListener('message', (event) => {
  const data = event.data || {};
  if (data.type === 'CACHE_URLS' && Array.isArray(data.urls)) {
    event.waitUntil(cacheUrls(data.urls));
  }
});

async function cacheUrls(urls) {
  const cache = await caches.open(RUNTIME_CACHE);
  await cache.addAll(urls);
}

// ---------------------------------------------
// Push Notifications
// ---------------------------------------------
const DEFAULT_PUSH_TITLE = '3 Coisas de Hoje';

self.addEventListener('push', (event) => {
  if (!event.data) {
    return;
  }

  let payload = {};
  try {
    payload = event.data.json();
  } catch (err) {
    payload = { body: event.data.text() };
  }

  const title = payload.title || DEFAULT_PUSH_TITLE;
  const options = {
    body: payload.body || 'Nova atualização disponível.',
    icon: payload.icon || '/static/icon-192.png',
    badge: payload.badge || '/static/icon-192.png',
    data: {
      url: payload.url || '/',
      ...payload.data,
    },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(self.location.origin)) {
          client.navigate(targetUrl);
          client.focus();
          return;
        }
      }
      clients.openWindow(targetUrl);
    })
  );
});

self.addEventListener('pushsubscriptionchange', (event) => {
  event.waitUntil(
    (async () => {
      try {
        const applicationServerKey =
          event.oldSubscription?.options?.applicationServerKey || null;
        if (!applicationServerKey) {
          return;
        }
        const newSubscription = await self.registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey,
        });
        const clientsList = await clients.matchAll({ includeUncontrolled: true });
        clientsList.forEach((client) =>
          client.postMessage({
            type: 'PUSH_SUBSCRIPTION_CHANGED',
            subscription: newSubscription,
          })
        );
      } catch (err) {
        console.error('[Service Worker] Falha ao renovar push subscription', err);
      }
    })()
  );
});
