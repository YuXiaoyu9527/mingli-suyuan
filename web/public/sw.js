/**
 * 命理溯源 — Service Worker
 * ==========================
 * PWA 离线支持：缓存静态资源 + API 响应，断网也能用。
 *
 * 策略：
 * - 静态资源（JS/CSS/字体）：Cache First（优先缓存，快）
 * - 页面（HTML）：Network First（优先网络，离线时用缓存）
 * - API：Network First（保证数据最新，离线时用缓存兜底）
 */

// 版本号 — 每次部署改这里，浏览器自动刷新缓存
const SW_VERSION = "v3";
const CACHE_STATIC = `mingli-static-${SW_VERSION}`;
const CACHE_PAGES = `mingli-pages-${SW_VERSION}`;
const CACHE_API = `mingli-api-${SW_VERSION}`;

const STATIC_ASSETS = [
  "/",
  "/paipan",
  "/yiji",
  "/fengshui",
  "/zhouyi",
  "/dianji",
  "/mingli",
  "/manifest.json",
  "/icon.svg",
];

// ===== 安装：预缓存静态资源 =====
self.addEventListener("install", (event) => {
  console.log("[SW] 安装中...");
  event.waitUntil(
    caches.open(CACHE_STATIC).then((cache) => {
      console.log("[SW] 预缓存静态资源");
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// ===== 激活：清理旧缓存 =====
self.addEventListener("activate", (event) => {
  console.log("[SW] 激活");
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== CACHE_STATIC && key !== CACHE_PAGES && key !== CACHE_API)
          .map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// ===== 拦截请求 =====
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 跳过非 GET 请求
  if (request.method !== "GET") return;

  // 跳过 Chrome DevTools 请求
  if (url.pathname.startsWith("/__")) return;

  // API 请求：Network First
  if (url.pathname.startsWith("/api/") || url.port === "8000") {
    event.respondWith(networkFirst(request, CACHE_API));
    return;
  }

  // 页面请求（Next.js HTML）：Network First
  if (request.mode === "navigate" || request.headers.get("Accept")?.includes("text/html")) {
    event.respondWith(networkFirst(request, CACHE_PAGES));
    return;
  }

  // 静态资源：Cache First
  event.respondWith(cacheFirst(request, CACHE_STATIC));
});

// ===== 策略函数 =====

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (e) {
    // 离线且无缓存 → 返回离线页
    if (request.mode === "navigate") {
      return caches.match("/");
    }
    return new Response("离线", { status: 503 });
  }
}

async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (e) {
    const cached = await caches.match(request);
    if (cached) return cached;

    // 离线 + 无缓存
    return new Response(
      JSON.stringify({ error: "离线", message: "请连接网络后重试" }),
      { status: 503, headers: { "Content-Type": "application/json" } }
    );
  }
}