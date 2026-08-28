// Service worker minimal : met en cache la coquille statique de l'appli
// (HTML/CSS/JS/icônes) pour permettre l'ouverture hors ligne. Les appels
// aux API en direct (Vélo'v, météo, itinéraire, géocodage) ne sont JAMAIS
// mis en cache ici : c'est index.html (localStorage) qui gère leur repli
// hors ligne avec les dernières données connues.
const CACHE_NAME = 'velov-tabareau-shell-v1';
const SHELL_URLS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-180.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(SHELL_URLS))
      .catch(() => {}) // pas grave si un asset externe échoue au premier install
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = event.request.url;
  const isShellAsset = SHELL_URLS.some((u) => url.endsWith(u.replace('./', '')));
  if (!isShellAsset || event.request.method !== 'GET') return; // laisse passer le reste au réseau

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const network = fetch(event.request)
        .then((res) => {
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return res;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
