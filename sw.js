const CACHE = 'map2area-v2';
const URLS = [
  'index.html', 'manifest.json',
  'vendor/capacitor.js', 'vendor/filesystem.js', 'vendor/share.js',
  'vendor/html2canvas.min.js',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('unpkg.com') || e.request.url.includes('arcgisonline.com') || e.request.url.includes('basemaps.cartocdn.com')) {
    e.respondWith(fetch(e.request).catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request))
  );
});
