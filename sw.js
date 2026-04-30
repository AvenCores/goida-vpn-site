const CACHE_VERSION = 'goida-vpn-v2';
const APP_CACHE = `${CACHE_VERSION}-app`;
const RUNTIME_CACHE = `${CACHE_VERSION}-runtime`;

const QR_CODES = Array.from({ length: 26 }, (_, index) => `static/qr-codes/${index + 1}.png`);
const PRECACHE_URLS = [
  './',
  'index.html',
  'manifest.webmanifest',
  'static/css/tailwind.css',
  'static/images/favicon.png',
  'static/LICENSE',
  'static/i18n/translations.json',
  'static/js/i18n.js',
  'static/js/update-download-links.js',
  'static/js/statistics.js',
  'static/js/link-confirmation.js',
  'static/media/video.jpg',
  'static/media/bypass.png',
  'static/media/sber-icon.png',
  'static/media/dzen-white.png',
  'static/media/dzen-black.png',
  'api/download-links.json',
  'api/vc-runtime-link.json',
  'api/github-stats.json',
  ...QR_CODES
];

// Домены рекламных сетей и аналитики — не перехватываем их запросы
const IGNORED_HOSTS = [
  'yandex.ru',
  'yandex.net',
  'yastatic.net',
  'googletagmanager.com',
  'google-analytics.com',
  'doubleclick.net',
  'googleadservices.com',
  'google.com',
  'intent.ai',
  'temu.com',
  'shopnetic.com',
  'silvermob.com',
  'whiteboxdigital.ru',
  'vk.com',
  'facebook.com',
  'fbcdn.net'
];

function isIgnoredHost(hostname) {
  return IGNORED_HOSTS.some(host => hostname === host || hostname.endsWith('.' + host));
}

const scopeUrl = new URL(self.registration.scope);

function toScopedUrl(path) {
  return new URL(path, scopeUrl).toString();
}

async function precache() {
  const cache = await caches.open(APP_CACHE);
  const requests = PRECACHE_URLS.map((path) => new Request(toScopedUrl(path), { cache: 'reload' }));
  const results = await Promise.allSettled(
    requests.map(async (request) => {
      const response = await fetch(request);
      if (response.ok) {
        await cache.put(request, response);
      }
    })
  );

  const failed = results.filter((result) => result.status === 'rejected').length;
  if (failed > 0) {
    console.warn(`[ServiceWorker] ${failed} precache request(s) failed`);
  }
}

self.addEventListener('install', (event) => {
  event.waitUntil(precache().then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames
        .filter((cacheName) => cacheName.startsWith('goida-vpn-') && !cacheName.startsWith(CACHE_VERSION))
        .map((cacheName) => caches.delete(cacheName))
    );
    await self.clients.claim();
  })());
});

async function fromNetwork(request, cacheName = RUNTIME_CACHE) {
  const response = await fetch(request);
  if (response && (response.ok || response.type === 'opaque')) {
    const cache = await caches.open(cacheName);
    await cache.put(request, response.clone());
  }
  return response;
}

async function cacheFirst(request, fallbackToShell = true) {
  const cached = await caches.match(request, { ignoreSearch: true });
  if (cached) {
    return cached;
  }

  try {
    return await fromNetwork(request);
  } catch (error) {
    if (fallbackToShell) {
      return (await caches.match(toScopedUrl('index.html'))) || caches.match(toScopedUrl('./'));
    }
    return new Response('', { status: 504, statusText: 'Offline' });
  }
}

async function networkFirst(request, fallbackToJson = false) {
  try {
    return await fromNetwork(request);
  } catch (error) {
    const cached = await caches.match(request, { ignoreSearch: true });
    if (cached) {
      return cached;
    }
    if (fallbackToJson) {
      return new Response('{}', {
        headers: {
          'Content-Type': 'application/json; charset=utf-8'
        }
      });
    }
    return (await caches.match(toScopedUrl('index.html'))) || caches.match(toScopedUrl('./'));
  }
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);

  // 1. Игнорируем chrome-extension://, data:, blob: и т.д.
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // 2. Не перехватываем рекламные/аналитические запросы — пусть грузятся напрямую
  if (isIgnoredHost(url.hostname)) {
    return;
  }

  const sameOrigin = url.origin === self.location.origin;
  const isApi = sameOrigin && url.pathname.includes('/api/');
  const isQrCode = sameOrigin && url.pathname.includes('/static/qr-codes/');
  const isNavigation = request.mode === 'navigate';

  if (isNavigation) {
    event.respondWith(networkFirst(request));
    return;
  }

  if (isApi) {
    event.respondWith(networkFirst(request, true));
    return;
  }

  if (isQrCode || sameOrigin) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // 3. Для остальных cross-origin запросов тоже не мешаем
  // (например, CDN шрифтов, Alpine.js, FontAwesome)
  event.respondWith(cacheFirst(request, false));
});