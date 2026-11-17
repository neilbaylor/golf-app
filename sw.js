/* Tee Party service worker (SW_ON in the page; Neil 17 Nov, v406).
   Online, nobody runs an old version: every open still asks the server for the page (it's served no-cache, so the HTTP cache revalidates with its
   ETag: a 304 when nothing changed) and the network's page is the one used. The copy kept here is only used when the network FAILS (offline,
   no signal), so the game still opens. The content-hashed scripts (game/crew/hunt/aug.<hash>.js) are cache-first: a new build has new names.
   three.js (cdnjs, versioned URL) and the fonts are kept after first use. A page is only kept once its scripts are kept too (never a page whose
   scripts are missing), and scripts no kept page names are dropped. Kill switch: SW_ON = false in the page unregisters this and deletes its caches. */
const CACHE = 'tp-1', HASHED = /^\/(game|crew|hunt|aug)\.[0-9a-f]{10}\.js$/, NAMES = /\b(?:game|crew|hunt|aug)\.[0-9a-f]{10}\.js\b/g;
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil((async () => { for (const k of await caches.keys()) if (k.startsWith('tp-') && k !== CACHE) await caches.delete(k); await self.clients.claim();
  try { const r = await fetch('/', { cache: 'no-cache' }); if (r.ok) await keepPage(r); } catch (er) {} })())); /* the first visit loaded before this existed: keep the page now (its scripts come from the browser's HTTP cache, no download) */

const IV = { ignoreVary: true }; /* (the server sends Vary: Accept-Encoding; a kept copy must match whatever asks) */
const inflight = new Map(); /* one download per script, shared by the page's own request and the keep step */
function keepFirst(url, opts) { /* cache-first, filled from the network */
  if (inflight.has(url)) return inflight.get(url).then(r => r.clone()); /* (each asker gets its own copy of the body) */
  const p = (async () => { const c = await caches.open(CACHE), hit = await c.match(url, IV); if (hit) return hit;
    const r = await fetch(url, opts); if (r.ok || r.type === 'opaque') await c.put(url, r.clone()); return r; })();
  inflight.set(url, p); p.then(() => inflight.delete(url), () => inflight.delete(url)); return p.then(r => r.clone());
}
async function keepPage(r) { /* after a good page from the network: keep its scripts, then the page, then drop scripts nothing names */
  const text = await r.clone().text(), want = [...new Set(text.match(NAMES) || [])];
  for (const n of want) { const res = await keepFirst(new URL('/' + n, self.location.origin).href); if (!res.ok) return; }
  for (const x of new Set(text.match(/https:\/\/cdnjs\.cloudflare\.com\/[^"'\s]+\.js/g) || [])) { try { await keepFirst(x, { mode: 'no-cors', credentials: 'omit' }); } catch (er) {} } /* three.js too, so the first visit is enough to open offline */
  const c = await caches.open(CACHE), old = await c.match('/', IV), oldNames = old ? (await old.text()).match(NAMES) || [] : [];
  await c.put('/', r);
  const keep = new Set([...want, ...oldNames]); /* (and the previous page's: a tab opened just before a deploy may still ask for them) */
  for (const q of await c.keys()) { const p = new URL(q.url).pathname; if (HASHED.test(p) && !keep.has(p.slice(1))) await c.delete(q); }
}
self.addEventListener('fetch', e => {
  const q = e.request; if (q.method !== 'GET') return; const u = new URL(q.url);
  if (u.origin === self.location.origin) {
    if (q.mode === 'navigate' || u.pathname === '/' || u.pathname === '/index.html') {
      e.respondWith((async () => { try { const r = await fetch(q); if (r.ok) e.waitUntil(keepPage(r.clone()).catch(() => {})); return r; }
        catch (er) { const hit = await caches.match('/', IV); if (hit) return hit; throw er; } })()); /* network first, always: the cached page only when it fails */
      return; }
    if (HASHED.test(u.pathname)) { e.respondWith(keepFirst(u.origin + u.pathname)); return; }
    if (u.pathname === '/manifest.webmanifest' || u.pathname.startsWith('/icons/')) { e.respondWith(fetch(q).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(k => k.put(q, c)); } return r; }).catch(() => caches.match(q, IV).then(h => h || Response.error()))); return; }
    return; /* anything else (healthz, /mp/stats, sw.js): straight to the network */
  }
  if (u.hostname === 'cdnjs.cloudflare.com' || u.hostname === 'fonts.gstatic.com') { e.respondWith(keepFirst(q.url, { mode: q.mode === 'cors' ? 'cors' : 'no-cors', credentials: 'omit' })); return; } /* versioned URLs: never change */
  if (u.hostname === 'fonts.googleapis.com') { e.respondWith(fetch(q).then(r => { const c = r.clone(); caches.open(CACHE).then(k => k.put(q, c)); return r; }).catch(() => caches.match(q, IV).then(h => h || Response.error()))); return; }
});
