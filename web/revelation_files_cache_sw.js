const RUNTIME_IMAGE_CACHE = 'revelation-runtime-image-cache-v2';
const MAX_IMAGE_CACHE_ENTRIES = 512;
const ALLOWED_SUPABASE_HOST = 'adfdfxnzxmzyoioedwuy.supabase.co';
const SUPABASE_OBJECT_PATH_PREFIX = '/storage/v1/object/';
const ALLOWED_SUPABASE_FOLDERS = ['images/', 'primary_sources/'];

self.addEventListener('install', (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
      (async () => {
        const cacheNames = await caches.keys();
        await Promise.all(
            cacheNames
                .filter((name) => name !== RUNTIME_IMAGE_CACHE)
                .map((name) => caches.delete(name)),
        );
        await self.clients.claim();
      })(),
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);
  if (!shouldHandleRequest(url)) {
    return;
  }

  event.respondWith(cacheFirst(request));
});

function shouldHandleRequest(url) {
  if (!isHttp(url)) {
    return false;
  }

  return isAllowedSupabaseImageRequest(url);
}

function isHttp(url) {
  return url.protocol === 'http:' || url.protocol === 'https:';
}

function isAllowedSupabaseImageRequest(url) {
  if (url.hostname.toLowerCase() !== ALLOWED_SUPABASE_HOST) {
    return false;
  }

  if (!url.pathname.startsWith(SUPABASE_OBJECT_PATH_PREFIX)) {
    return false;
  }

  const objectPath = url.pathname.substring(SUPABASE_OBJECT_PATH_PREFIX.length);
  return ALLOWED_SUPABASE_FOLDERS.some(
    (folderPrefix) =>
      objectPath.startsWith(folderPrefix) ||
      objectPath.startsWith(`public/${folderPrefix}`),
  );
}

async function cacheFirst(request) {
  const cache = await caches.open(RUNTIME_IMAGE_CACHE);
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const response = await fetch(request);
    if (isCacheable(response)) {
      await cache.put(request, response.clone());
      await trimCache(cache, MAX_IMAGE_CACHE_ENTRIES);
    }
    return response;
  } catch (error) {
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

function isCacheable(response) {
  if (!response) {
    return false;
  }
  return response.ok || response.type === 'opaque';
}

async function trimCache(cache, maxEntries) {
  const keys = await cache.keys();
  if (keys.length <= maxEntries) {
    return;
  }

  const removeCount = keys.length - maxEntries;
  for (let i = 0; i < removeCount; i += 1) {
    await cache.delete(keys[i]);
  }
}
