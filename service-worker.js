// SMSS 가계부 서비스워커
// 전략: 앱 셸은 캐시 우선(stale-while-revalidate) → 즉시 렌더, 백그라운드 갱신
//       새 버전이 준비되면 페이지에 알려서 '새 버전' 토스트를 띄운다.
const CACHE_NAME = 'smss-accountbook-v22';   // v22: 중복 기록 방지 코드를 휴대폰에 확실히 내려보내기

// 앱 셸 (없으면 앱이 아예 안 뜨는 것들)
const SHELL_URLS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon.svg'
];

// 외부 CDN (실패해도 설치는 성공해야 함)
const CDN_URLS = [
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js',
  'https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css'
];

// 캐시하지 않는 호스트 (항상 네트워크)
function isApiRequest(url) {
    return url.includes('script.google.com') ||
           url.includes('sheets.googleapis.com') ||
           url.includes('docs.google.com');
}

// ===== 설치 =====
self.addEventListener('install', event => {
    event.waitUntil((async () => {
        const cache = await caches.open(CACHE_NAME);
        // 셸은 반드시 캐시 (하나라도 실패하면 설치 실패 → 이전 버전 유지)
        await cache.addAll(SHELL_URLS);
        // CDN은 개별 처리 (실패 허용) — addAll은 하나만 실패해도 전체가 롤백된다
        await Promise.all(CDN_URLS.map(u =>
            cache.add(new Request(u, { mode: 'cors' })).catch(() => {})
        ));
        // skipWaiting은 하지 않음 → 페이지가 사용자에게 물어본 뒤 SKIP_WAITING 메시지로 전환
    })());
});

// ===== 활성화 =====
self.addEventListener('activate', event => {
    event.waitUntil((async () => {
        const names = await caches.keys();
        await Promise.all(names.map(n => n !== CACHE_NAME ? caches.delete(n) : null));
        await self.clients.claim();
    })());
});

// 페이지가 "지금 갱신" 을 눌렀을 때
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// ===== fetch =====
self.addEventListener('fetch', event => {
    const req = event.request;

    // GET 이외 / API 요청은 그대로 통과
    if (req.method !== 'GET' || isApiRequest(req.url)) return;

    // 캐시 우선 + 백그라운드 갱신 (stale-while-revalidate)
    event.respondWith((async () => {
        const cache = await caches.open(CACHE_NAME);
        const cached = await cache.match(req, { ignoreSearch: false });

        // 백그라운드 갱신 (응답을 기다리지 않음)
        const revalidate = fetch(req).then(res => {
            if (res && res.status === 200 && res.type !== 'opaque') {
                cache.put(req, res.clone()).catch(() => {});
            }
            return res;
        }).catch(() => null);

        if (cached) {
            // 캐시된 내용을 즉시 반환 — 네트워크를 기다리지 않는다
            event.waitUntil(revalidate);
            return cached;
        }

        // 캐시에 없으면 네트워크 (그리고 실패 시 index.html 폴백)
        const fresh = await revalidate;
        if (fresh) return fresh;

        if (req.mode === 'navigate') {
            const shell = await cache.match('./index.html');
            if (shell) return shell;
        }
        return new Response('오프라인 상태입니다', {
            status: 503,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
    })());
});
