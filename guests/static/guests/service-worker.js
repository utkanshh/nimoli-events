const CACHE_NAME = "nimoli-bhandari-events-shell-v1";
const OFFLINE_URL = "/offline/";
const SHELL_ASSETS = [
  OFFLINE_URL,
  "/static/guests/dashboard.css",
  "/static/guests/dashboard.js",
  "/static/guests/app-icon-192.png",
  "/static/guests/app-icon-512.png",
  "/app.webmanifest",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter(
            (key) =>
              (key.startsWith("gather-shell-") ||
                key.startsWith("nimoli-events-shell-") ||
                key.startsWith("nimoli-bhandari-events-shell-")) &&
              key !== CACHE_NAME,
          )
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(async () => {
        const cachedPage = await caches.match(OFFLINE_URL);
        return cachedPage || new Response("Reconnect to use Nimoli Bhandari Events.", { status: 503 });
      })
    );
    return;
  }

  if (
    url.pathname.startsWith("/static/guests/") ||
    url.pathname === "/app.webmanifest"
  ) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            if (response.ok) {
              const copy = response.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
            }
            return response;
          })
      )
    );
  }
});
