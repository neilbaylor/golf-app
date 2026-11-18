// Tiny zero-dependency web server for Railway. Serves the single-file game inside a proper page shell
// (doctype, viewport, app-icon and home-screen tags), plus the manifest and icons. Compressed when the browser accepts it.
// Multiplayer: a WebSocket endpoint at /mp on the same port (a minimal hand-rolled RFC 6455, no packages), rooms in memory.
const http = require('http'), fs = require('fs'), path = require('path'), zlib = require('zlib'), crypto = require('crypto');
const ELD = require('perf_hooks').monitorEventLoopDelay({ resolution: 10 }); ELD.enable(); /* /mp/stats: event-loop delay (how late the server answers), for load profiling */
const HEAD = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<title>Tee Party</title>
<meta name="theme-color" content="#1d2a1a">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="Tee Party">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=2"><link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=2">
<style>html,body{margin:0;height:100%;background:#1d2a1a;overscroll-behavior:none}[hidden]{display:none!important}</style>
</head><body>`;
const page = Buffer.from(HEAD + fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8') + '</body></html>');
const TYPES = { '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const files = { '/': [page, 'text/html; charset=utf-8'] };
const icons = fs.existsSync(path.join(__dirname, 'icons')) ? fs.readdirSync(path.join(__dirname, 'icons')).map(n => 'icons/' + n) : []; // missing extras never stop the game from serving
for (const f of ['manifest.webmanifest', ...icons]) if (fs.existsSync(path.join(__dirname, f)))
  files['/' + f] = [fs.readFileSync(path.join(__dirname, f)), TYPES[path.extname(f)] || 'application/octet-stream'];
files['/index.html'] = files['/'];
if (fs.existsSync(path.join(__dirname, 'sw.js'))) files['/sw.js'] = [fs.readFileSync(path.join(__dirname, 'sw.js')), 'text/javascript; charset=utf-8']; /* SW_ON (v406): the service worker; served no-cache so a new one is picked up at once */
/* SPLIT_FILES (perf2, Neil 16 Nov): tools/split_build.py writes the page as index.html plus content-hashed scripts (game/crew/hunt/aug.<hash>.js). They are served with
   a cache-forever header (a new build means new names), compressed like the page (gzip at start, brotli off the main thread). ROLLBACK: false (or a --single build) -> as before. */
const SPLIT_FILES = true, HASHED = /^\/(game|crew|hunt|aug)\.[0-9a-f]{10}\.js$/;
if (SPLIT_FILES) for (const n of fs.readdirSync(__dirname)) if (HASHED.test('/' + n)) files['/' + n] = [fs.readFileSync(path.join(__dirname, n)), 'text/javascript; charset=utf-8'];
/* BR_ASYNC (Neil 11-16 14:12, "can't load the page" after a deploy): the 4 MB page's brotli (quality 11) ran synchronously before listen(), tens of seconds of CPU on a small box, so a new
   deploy started slowly. Now gzip is made at start (well under a second) and the server listens straight away; brotli is made off the main thread and served once it's ready (gzip until then).
   ROLLBACK: BR_ASYNC = false -> both made synchronously before listening, as before. */
const BR_ASYNC = true, BR_OPTS = process.env.TP_FAST_BR ? { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 4 } } : undefined; /* TP_FAST_BR: quick local test starts only */
const cache = {}; for (const [k, [buf, type]] of Object.entries(files)) {
  const c = cache[k] = { buf, type, gz: zlib.gzipSync(buf, { level: 9 }), br: BR_ASYNC ? null : zlib.brotliCompressSync(buf, BR_OPTS), etag: '"' + crypto.createHash('sha1').update(buf).digest('hex').slice(0, 16) + '"' };
  if (BR_ASYNC && type !== 'image/png') zlib.brotliCompress(buf, BR_OPTS || {}, (e, out) => { if (!e) c.br = out; else console.error('[br]', k, e.message); }); }
const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  if (url === '/healthz') { res.writeHead(200, { 'Content-Type': 'text/plain' }); return res.end('ok'); }
  if (url === '/mp/stats') { res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }); return res.end(JSON.stringify(MP.stats())); } /* rooms, sockets, message and byte counts (for profiling) */
  const f = cache[url]; if (!f) { res.writeHead(404, { 'Content-Type': 'text/plain' }); return res.end('Not found'); }
  const h = { 'Content-Type': f.type, 'Cache-Control': f.type.startsWith('text/html') || url === '/sw.js' ? 'no-cache' : SPLIT_FILES && HASHED.test(url) ? 'public, max-age=31536000, immutable' : 'public, max-age=86400', ETag: f.etag, Vary: 'Accept-Encoding' };
  if (req.headers['if-none-match'] === f.etag) { res.writeHead(304, h); return res.end(); }
  const ae = req.headers['accept-encoding'] || '', pngish = f.type === 'image/png';
  const [body, enc] = !pngish && f.br && /\bbr\b/.test(ae) ? [f.br, 'br'] : !pngish && /\bgzip\b/.test(ae) ? [f.gz, 'gzip'] : [f.buf, null];
  if (enc) h['Content-Encoding'] = enc;
  res.writeHead(200, h); res.end(req.method === 'HEAD' ? undefined : body);
});

/* ================= MULTIPLAYER =================
   Rooms by code (1-10 letters or digits, case-insensitive), max 4 golfers, no host. The server holds the authoritative state (players, course, hole, turn, balls,
   scores, seeds) and relays aim / shot / chat / typing / reaction events. Shots are computed on the shooter's phone and replayed
   from their inputs + seed everywhere else; the shooter's own result is what the server keeps. Timings below are the knobs. */
const MP = (() => {
  const T = {
    MAX: 4,                 // golfers per room
    EMPTY_GRACE: 120000,    // an empty room lives this long (refresh / flaky network), then it's deleted
    EMPTY_END: 45000,       // MP_EMPTY_END (Neil, v362: "when there are no active players in the game, let's just end it"): a round with nobody connected ends after this (a phone reload or a server restart with MP_RESTORE fits in it); a phone back later is told 'ended'; a newcomer to such a round gets a fresh lobby at once. 0 = off
    LOBBY_DROP: 20000,      // a golfer gone this long from the lobby gives up their seat
    IDLE: 30000,            // no input on your turn this long: the countdown ring appears...
    RING: 15000,            // ...for this long, then the game auto-hits for you
    HOLD_CAP: 45000,        // the chat composer pauses your turn timer, up to this long
    RECONNECT: 20000,       // a dropped golfer's turn waits this long for them, then their shots are auto-played
    AUTO_NUDGE: 6000,       // an auto-hit the active phone hasn't sent by now is played by another phone (the proxy)
    NEXT_WAIT: 45000,       // after a shot, the shooter reports where the ball ended up; failing that, the server uses the shot's own result
    CARD_AUTO: 30000,       // the end-of-hole group card moves on by itself after this long
    PU_OVER: 3,             // picked up: scored as par + this
    MAX_OVER: 3,            // MAX_TRIPLE: a shot that leaves you at par + this without holing out ends your hole there, picked up (0 = off: the old par + 7 cap)
    CHAT_MAX: 40,           // characters
    KICK: 1,                // MP_KICK (Neil 12:39-12:40): a golfer who hasn't played for IDLE on their turn (or is gone that long on it) is "away": the others get PLAY FOR / REMOVE / WAIT.
                            //   No timed auto-hit any more (the idle ring is a "hurry" nudge, a dropped golfer's turn waits): the room waits for someone to choose. 0 = the old IDLE + RING auto-hit and RECONNECT auto-play
    PF_WAIT: 20000,         // MP_KICK: a PLAY FOR not played by then is stale: the modal comes back and someone else may take over (the first phone's shot is still taken if it comes)
    MIN_PLAYERS: 2,         // MP_MIN2 (Neil 12:24): a round starts only with this many golfers in the room (1 = off: anyone can tee off alone, as before). Only starting is gated: a round carries on if golfers leave
    FRAME_MAX: 16384,       // bytes per message
    HOLD_MAX: 3000,         // NEXT_HOLD: the most a 'next' may hold off the next golfer's idle clock (the result card is 2.75 s)
    AIM_MAX: 1024,         // MP_AIMCAP: bytes per aim message (a real one is ~150): bigger ones are dropped, not relayed to three phones 20 times a second
    BP_SOFT: 65536,         // MP_BP: a socket with this much unsent: aim updates to it are skipped (the next one supersedes them anyway)
    BP_HARD: 1048576,       // MP_BP: ...and with this much it is cut (a phone that hasn't read 1 MB isn't reading): it reconnects and resyncs from the welcome
  };
  const MP_BP = true;       /* ROLLBACK: false -> every message is queued for every socket however far behind it is (before perf2) */
  const MP_RESTORE = true;  /* ROLLBACK: false -> a server restart (every deploy) loses every room: a phone coming back gets a new, empty lobby under the same code (before perf2).
    true: a phone reconnecting to a room the server doesn't have sends its last copy of the room (snap: the 'room' state it was sent, plus its own player id); the server rebuilds the room from it
    (course, phase, hole, pars, the pins seed, turn, balls, scores, seats), the phone takes its old seat back, and the others take theirs back by id when they return (meanwhile they are 'dropped', as after any blip).
    A shot in the air at the restart is lost (its turn goes back to aiming from the ball's last spot). */
  const NEXT_HOLD = true;   /* mplag (MP_EARLY_NEXT on the phones): a 'next' sent while its result card is still up says how long (hold, ms, at most HOLD_MAX); the next golfer's idle / away clock starts when the card goes, as it did when 'next' came after the card.
    ROLLBACK: false -> the clock starts at the 'next' (an early one would start it up to 2.75 s before the turn shows). An old phone sends no hold: as before */
  const FLY_SKIP_ALL = true; /* Neil (11-16): a Skip on the hole's fly-over on any phone skips it for everyone: its 'flyskip' (for this hole) is relayed once per hole to the others; a second press anywhere is dropped. ROLLBACK: false -> not relayed (each phone's own fly-over) */
  const MP_AIMCAP = true;   /* ROLLBACK: false -> aim messages of any size up to FRAME_MAX are relayed (before perf2) */
  for (const k in T) if (process.env['MP_' + k]) T[k] = +process.env['MP_' + k]; /* e.g. MP_IDLE=3000 for quick tests */
  const EMO = ['❤️', '😂', '🔥', '👏', '😮', '🙈'];
  const COURSES = { hunt: 'Toronto Hunt', augusta: 'Augusta National' };
  const RATE = { aim: [20, 30], chat: [1.2, 3], react: [5, 8], typing: [2, 4], ff: [6, 10], act: [2, 4], who: [2, 4], course: [2, 4], hello: [1, 3], '*': [60, 90] }; /* per second, burst */
  const ENDED = new Map(); let endedN = 0; /* MP_EMPTY_END: code -> the ended round's sids and ids (15 min), so its phones are told rather than seated in a ghost room */
  const rooms = new Map(), socks = new Set(); let msgsIn = 0, msgsOut = 0, bytesIn = 0, bytesOut = 0, bpSkip = 0, bpCut = 0, restoredN = 0;
  const now = () => Date.now();
  const rid = n => crypto.randomBytes(n).toString('base64').replace(/[^A-Za-z0-9]/g, '').slice(0, n);

  /* ---------- RFC 6455: handshake, frames (text, close, ping/pong, continuation), masked from clients, unmasked from us ---------- */
  function upgrade(req, sock) {
    const url = (req.url || '').split('?')[0], key = req.headers['sec-websocket-key'];
    if (url !== '/mp' || !key || String(req.headers.upgrade || '').toLowerCase() !== 'websocket') { sock.end('HTTP/1.1 400 Bad Request\r\n\r\n'); return; }
    const acc = crypto.createHash('sha1').update(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest('base64');
    sock.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ' + acc + '\r\n\r\n');
    sock.setNoDelay(true); sock.setKeepAlive(true, 20000);
    const c = { sock, buf: Buffer.alloc(0), frag: null, room: null, pid: null, alive: true, bucket: {}, closed: false };
    socks.add(c);
    sock.on('data', d => { c.buf = c.buf.length ? Buffer.concat([c.buf, d]) : d; try { parse(c); } catch (e) { kill(c, 1002); } });
    sock.on('close', () => gone(c)); sock.on('error', () => gone(c)); sock.on('end', () => gone(c));
  }
  function parse(c) {
    for (;;) {
      const b = c.buf; if (b.length < 2) return;
      const fin = b[0] & 0x80, op = b[0] & 0x0f, masked = b[1] & 0x80; let len = b[1] & 0x7f, o = 2;
      if (!masked) return kill(c, 1002);
      if (len === 126) { if (b.length < 4) return; len = b.readUInt16BE(2); o = 4; }
      else if (len === 127) { if (b.length < 10) return; if (b.readUInt32BE(2) !== 0) return kill(c, 1009); len = b.readUInt32BE(6); o = 10; }
      if (len > T.FRAME_MAX) return kill(c, 1009);
      if (b.length < o + 4 + len) return;
      const mask = b.slice(o, o + 4), data = Buffer.allocUnsafe(len); for (let i = 0; i < len; i++) data[i] = b[o + 4 + i] ^ mask[i & 3];
      c.buf = b.slice(o + 4 + len);
      if (op === 0x8) { kill(c, 1000); return; }
      if (op === 0x9) { frame(c, 0xA, data); continue; }
      if (op === 0xA) { c.alive = true; continue; }
      if (op === 0x1 || op === 0x2) { if (fin) message(c, data); else c.frag = [data]; continue; }
      if (op === 0x0 && c.frag) { c.frag.push(data); if (c.frag.reduce((a, x) => a + x.length, 0) > T.FRAME_MAX) return kill(c, 1009); if (fin) { const d = Buffer.concat(c.frag); c.frag = null; message(c, d); } continue; }
      return kill(c, 1002);
    }
  }
  function frame(c, op, data) {
    if (c.closed || c.sock.destroyed) return; const n = data.length; let h;
    if (n < 126) { h = Buffer.from([0x80 | op, n]); } else if (n < 65536) { h = Buffer.alloc(4); h[0] = 0x80 | op; h[1] = 126; h.writeUInt16BE(n, 2); } else { h = Buffer.alloc(10); h[0] = 0x80 | op; h[1] = 127; h.writeUInt32BE(0, 2); h.writeUInt32BE(n, 6); }
    try { c.sock.write(Buffer.concat([h, data])); } catch (e) {}
    if (MP_BP && c.sock.writableLength > T.BP_HARD) { bpCut++; c.closed = true; try { c.sock.destroy(); } catch (e) {} } /* MP_BP: not reading at all: cut (its 'close' event runs gone(), as for any drop) */
  }
  function send(c, o) { if (!c || c.closed) return; if (MP_BP && o.t === 'aim' && c.sock.writableLength > T.BP_SOFT) { bpSkip++; return; } /* MP_BP: behind: skip aim frames */ const s = Buffer.from(JSON.stringify(o)); msgsOut++; bytesOut += s.length; frame(c, 0x1, s); }
  function kill(c, code = 1000) { if (c.closed) return; const d = Buffer.alloc(2); d.writeUInt16BE(code, 0); frame(c, 0x8, d); c.closed = true; try { c.sock.end(); } catch (e) {} setTimeout(() => { try { c.sock.destroy(); } catch (e) {} }, 1000); gone(c); }
  setInterval(() => { for (const c of socks) { if (!c.alive) { kill(c, 1001); continue; } c.alive = false; frame(c, 0x9, Buffer.alloc(0)); } }, 25000).unref(); /* dead sockets: no pong within 25 s */
  function rate(c, t) { /* token buckets: one per message type and one overall */
    const ok = k => { const [r, burst] = RATE[k] || RATE['*'], B = c.bucket[k] || (c.bucket[k] = { n: burst, t: now() }); B.n = Math.min(burst, B.n + (now() - B.t) / 1000 * r); B.t = now(); if (B.n < 1) return false; B.n--; return true; };
    return ok('*') && (!RATE[t] || ok(t)); }

  /* ---------- rooms ---------- */
  const pub = R => ({ code: R.code, course: R.course, phase: R.phase, hole: R.hole, nHoles: R.pars.length || 0, pars: R.pars, seed: R.seed, turn: R.turn, tstate: R.tstate, shotN: R.shotN, auto: R.autoFor || null, away: R.away || null,
    players: R.players.map(p => ({ id: p.id, seat: p.seat, name: p.name, who: p.who, conn: !!p.c, pu: !!p.pu, wait: !!p.wait, ball: p.ball, scores: p.scores, lefty: !!p.lefty, ...(p.out ? { out: true } : {}) })), cardAt: R.cardAt ? Math.max(0, R.cardAt - now()) : null });
  const broadcast = (R, o, except) => { for (const p of R.players) if (p.c && p !== except) send(p.c, o); };
  const sync = R => broadcast(R, { t: 'room', room: pubN(R) });
  const NINES_PICK = true, NINES = ['18', 'f9', 'b9']; /* undo switch (Neil 11-16): the room's F9 / B9 / 18 pick (R.nine; the client sends that nine's pars at TEE OFF, so R.hole / R.pars are the round's own 1..9). false = no 'nine' in the room, as before */
  const pubN = R => NINES_PICK ? { ...pub(R), nine: R.nine || '18' } : pub(R);
  const P = (R, id) => R.players.find(p => p.id === id);
  function room(code) { let R = rooms.get(code); if (!R) { R = { code, players: [], course: 'hunt', phase: 'lobby', hole: 0, pars: [], seed: crypto.randomBytes(4).readUInt32BE(0), turn: null, tstate: null, shotN: 0, timers: {}, made: now() }; rooms.set(code, R); } return R; }
  function clearT(R, k) { if (R.timers[k]) { clearTimeout(R.timers[k]); delete R.timers[k]; } }
  function setT(R, k, ms, fn) { clearT(R, k); R.timers[k] = setTimeout(() => { delete R.timers[k]; fn(); }, Math.max(0, ms)); }
  function nameFor(R, p, who, name) { let n = String(name || who || 'Golfer').replace(/[^\p{L}\p{N} .'-]/gu, '').slice(0, 14) || 'Golfer'; const same = R.players.filter(q => q !== p && q.name.replace(/ \d$/, '') === n).length; return same ? n + ' ' + (same + 1) : n; }

  const int = (x, lo, hi, d) => typeof x === 'number' && isFinite(x) ? Math.max(lo, Math.min(hi, Math.round(x))) : d;
  function endRoom(R) { for (const k in R.timers) clearT(R, k); ENDED.set(R.code, { at: now(), sids: new Set(R.players.map(p => p.sid).filter(Boolean)), ids: new Set(R.players.map(p => p.id)) }); if (rooms.get(R.code) === R) rooms.delete(R.code); endedN++;
    for (const p of R.players) if (p.c) { const o = p.c; p.c = null; o.room = null; o.pid = null; send(o, { t: 'ended', msg: 'This round ended' }); } }
  const wasEnded = (code, m) => { const e = ENDED.get(code); if (!e) return false; if (now() - e.at > 900000) { ENDED.delete(code); return false; } return !!((m.sid && e.sids.has(String(m.sid))) || (typeof m.you === 'string' && e.ids.has(m.you))); };
  function restore(code, m) { /* MP_RESTORE: a room rebuilt from a returning phone's last copy of it, every field checked */
    const s = m.snap, you = typeof m.you === 'string' ? m.you : null;
    if (!s || typeof s !== 'object' || String(s.code || '').toUpperCase() !== code || !['play', 'hole', 'done'].includes(s.phase) || !Array.isArray(s.players) || !s.players.length || s.players.length > T.MAX) return null;
    if (!Array.isArray(s.pars) || !s.pars.length || s.pars.length > 36 || !s.pars.every(x => num(x, 2, 7)) || !you || !s.players.some(q => q && q.id === you)) return null;
    const R = room(code), np = s.pars.length; R.restored = now(); R.course = COURSES[s.course] ? s.course : 'hunt'; R.phase = s.phase; R.pars = s.pars.map(x => Math.round(x)); R.hole = int(s.hole, 1, np, 1); if (num(s.seed, 0, 4294967295)) R.seed = s.seed >>> 0; R.shotN = int(s.shotN, 0, 1e6, 0);
    if (NINES_PICK) R.nine = NINES.includes(s.nine) ? s.nine : '18'; /* NINES_PICK: the round's nine comes back with the room */
    const sc = A => Array.isArray(A) ? A.slice(0, np).map(x => x && typeof x === 'object' && num(x.s, 1, 99) ? { s: Math.round(x.s), par: int(x.par, 2, 7, 4), ...(x.pu ? { pu: true } : {}), ...(x.max ? { max: true } : {}) } : null) : [];
    const ball = b => b && typeof b === 'object' ? { u: num(b.u, -2000, 2000) ? b.u : 0, v: num(b.v, -2000, 2000) ? b.v : 0, lie: String(b.lie || 'tee').slice(0, 12), stroke: int(b.stroke, 1, 40, 1), toPin: num(b.toPin, 0, 1e4) ? b.toPin : 1e4, done: !!b.done, holed: !!b.holed, ...(b.wait ? { wait: true } : {}), ...(b.puNow ? { puNow: true } : {}), ...(b.left ? { left: true } : {}) } : null;
    const seen = new Set(); R.players = [];
    for (const q of s.players) { if (!q || typeof q.id !== 'string' || !/^[A-Za-z0-9]{1,12}$/.test(q.id) || seen.has(q.id)) continue; seen.add(q.id);
      R.players.push({ id: q.id, sid: null, seat: int(q.seat, 0, T.MAX - 1, R.players.length), name: String(q.name || 'Golfer').replace(/[^\p{L}\p{N} .'-]/gu, '').slice(0, 14) || 'Golfer', who: /^[a-z]{2,16}$/.test(q.who || '') ? q.who : 'neil', lefty: !!q.lefty, c: null, discAt: now(), scores: sc(q.scores), ball: ball(q.ball), pu: !!q.pu, wait: !!q.wait }); }
    R.players.sort((a, b) => a.seat - b.seat);
    R.turn = R.phase === 'play' && R.players.some(p => p.id === s.turn) ? s.turn : null; R.tstate = R.turn ? 'aim' : null; R.shot = null; R.autoFor = null; R.idle = { start: now(), held: 0, holdAt: null };
    if (R.phase === 'play' && !R.turn) { const live = R.players.filter(p => p.ball && !p.ball.done); if (!live.length) R.phase = 'hole'; }
    if (R.phase === 'hole') { R.cardAt = now() + T.CARD_AUTO; setT(R, 'card', T.CARD_AUTO, () => { if (R.phase === 'hole') startHole(R, R.hole + 1); }); }
    restoredN++; return R; }
  function hello(c, m) {
    const code = String(m.code || '').toUpperCase(); if (!/^[A-Z0-9]{1,10}$/.test(code)) return send(c, { t: 'err', code: 'code', msg: 'Room codes are 1 to 10 letters or numbers' });
    if (c.room && c.room.code === code) leave(c, true); /* the same room again: a plain rejoin */
    let R0 = rooms.get(code); const seat = R => (m.sid && R.players.some(q => q.sid === String(m.sid))) || (MP_RESTORE && typeof m.you === 'string' && R.players.some(q => q.sid === null && q.id === m.you));
    if (T.EMPTY_END && R0 && (R0.phase === 'play' || R0.phase === 'hole') && !R0.players.some(q => q.c) && !seat(R0)) { endRoom(R0); R0 = null; } /* MP_EMPTY_END: a newcomer to a round nobody is in: it ends, a fresh lobby under the code */
    if (!R0 && MP_RESTORE && !(T.EMPTY_END && wasEnded(code, m))) R0 = restore(code, m); /* (never rebuild a round that ended for want of players) */
    const want = /^[a-z]{2,16}$/.test(m.who || '') ? m.who : 'neil', p0 = R0 && ((m.sid && R0.players.find(q => q.sid === String(m.sid))) || (MP_RESTORE && typeof m.you === 'string' && R0.players.find(q => q.sid === null && q.id === m.you)));
    if (T.EMPTY_END && !p0 && wasEnded(code, m)) return send(c, { t: 'ended', msg: 'This round ended' }); /* one of the ended round's phones, back */
    if (p0 && p0.sid === null) p0.sid = m.sid ? String(m.sid).slice(0, 32) : rid(16); /* MP_RESTORE: a seat from a rebuilt room, taken back by its own player */
    if (R0 && !p0) { const t = R0.players.find(q => q.who === want && !q.out); if (t) return send(c, { t: 'err', code: 'taken', who: want, by: t.name, taken: R0.players.map(q => ({ who: q.who, name: q.name })), msg: 'That golfer is taken' }); } /* golfers are unique per room: first come, first served */
    if (R0 && !p0 && R0.players.filter(q => !q.out).length >= T.MAX) return send(c, { t: 'err', code: 'full', msg: 'That room is full (4 players)' });
    if (c.room) leave(c, true); /* switching rooms from the lobby: the old seat is only given up once the new room has said yes */
    const R = room(code); clearT(R, 'empty'); clearT(R, 'end');
    let p = p0;
    if (!p && T.KICK && R0) { const q = R0.players.find(x => x.out && x.who === want); /* MP_KICK (Neil): a removed golfer back with the code or link: their own row again, as a late joiner (in from the next hole; holes missed stay blank, so they can't win) */
      if (q) { p = q; p.out = false; p.sid = rid(16); p.pu = false; if (R.phase === 'play' || R.phase === 'hole') { p.wait = true; p.ball = { u: 0, v: 0, lie: 'tee', stroke: 1, done: true, holed: false, wait: true }; }
        if (R.players.some(x => x !== p && !x.out && x.seat === p.seat)) { const seats = R.players.filter(x => x !== p && !x.out).map(x => x.seat); let seat = 0; while (seats.includes(seat)) seat++; p.seat = seat; R.players.sort((a, b) => a.seat - b.seat); } } }
    if (p) { if (p.c && p.c !== c) { const o = p.c; o.room = null; o.pid = null; send(o, { t: 'err', code: 'moved', msg: 'Opened somewhere else' }); kill(o, 4000); } } /* a refresh (or a second tab) takes the seat back */
    else {
      if (R.players.filter(q => !q.out).length >= T.MAX) return send(c, { t: 'err', code: 'full', msg: 'That room is full (4 players)' });
      const seats = R.players.filter(q => !q.out).map(q => q.seat); /* (MP_KICK: a removed golfer's seat is free) */ let seat = 0; while (seats.includes(seat)) seat++;
      p = { id: rid(6), sid: rid(16), seat, name: '', who: 'neil', c: null, scores: [], ball: null, pu: false, wait: false };
      R.players.push(p); R.players.sort((a, b) => a.seat - b.seat);
      if (R.phase === 'play' || R.phase === 'hole') { p.scores = new Array(R.phase === 'play' ? R.hole - 1 : R.hole).fill(null); p.wait = true; p.ball = { u: 0, v: 0, lie: 'tee', stroke: 1, done: true, holed: false, wait: true }; } /* a late joiner: in the game now, tees off on the next hole that starts; the holes before are blank (no penalty) */
      else if (R.phase === 'done') p.scores = new Array(R.pars.length).fill(null);
    }
    if (R.players.length === 1 && R.phase === 'lobby' && COURSES[m.course]) R.course = m.course; /* a new room starts on the course its first golfer had picked */
    if (!R.players.some(q => q !== p && q.who === want && !q.out)) { p.who = want; p.name = nameFor(R, p, p.who, m.name); p.lefty = !!m.lefty; } else if (!p.name) p.name = nameFor(R, p, p.who, m.name); /* a rejoin keeps its golfer if the one asked for is now someone else's */
    p.c = c; p.discAt = null; c.room = R; c.pid = p.id;
    if (T.KICK) back(R, p, true); /* MP_KICK: a reconnect is coming back */
    if (p.pu && R.phase === 'play') { p.pu = false; if (p.ball && p.ball.done && p.ball.puNow) joinHole(R, p); } /* back from a drop: in from the next turn */
    send(c, { t: 'welcome', you: p.id, sid: p.sid, room: pubN(R), T: { IDLE: T.IDLE, RING: T.RING, HOLD_CAP: T.HOLD_CAP, RECONNECT: T.RECONNECT, CHAT_MAX: T.CHAT_MAX, CARD_AUTO: T.CARD_AUTO } });
    sync(R); if (R.phase === 'play' && (R.turn === p.id || (MP_RESTORE && R.restored && !R.timers.auto && !R.timers.ring && !R.timers.idle))) timers(R);
  }
  function joinHole(R, p) { p.ball = { u: 0, v: 0, lie: 'tee', stroke: 1, toPin: 1e4, done: false, holed: false }; const sc = p.scores[R.hole - 1]; if (sc && sc.pu) p.scores.length = R.hole - 1; }
  function leave(c, quiet) { const R = c.room; if (!R) return; const p = P(R, c.pid); c.room = null; c.pid = null; if (!p) return;
    if (R.phase === 'lobby' || R.phase === 'done') R.players = R.players.filter(q => q !== p); else { p.c = null; p.discAt = now(); p.left = true; }
    if (!quiet) send(c, { t: 'left' }); after(R); }
  function gone(c) { socks.delete(c); if (c.closed !== true) c.closed = true; const R = c.room; if (!R) return; const p = P(R, c.pid); c.room = null; if (!p || p.c !== c) return;
    p.c = null; p.discAt = now(); if (R.phase === 'lobby' || R.phase === 'done') setT(R, 'drop:' + p.id, T.LOBBY_DROP, () => { if (!p.c) { R.players = R.players.filter(q => q !== p); after(R); } }); after(R); }
  function after(R) { /* someone left or dropped */
    if (!R.players.some(p => p.c)) { setT(R, 'empty', T.EMPTY_GRACE, () => { for (const k in R.timers) clearT(R, k); rooms.delete(R.code); });
      if (T.EMPTY_END && (R.phase === 'play' || R.phase === 'hole')) setT(R, 'end', T.EMPTY_END, () => { if (!R.players.some(p => p.c) && rooms.get(R.code) === R) endRoom(R); }); } /* MP_EMPTY_END: nobody left in the round */
    if (!R.players.length) { for (const k in R.timers) clearT(R, k); rooms.delete(R.code); return; }
    sync(R); if (R.phase === 'play') timers(R); }

  /* ---------- the round ---------- */
  function teeoff(R, m) {
    const pars = Array.isArray(m.pars) ? m.pars.slice(0, 18).map(x => Math.round(+x)).filter(x => x >= 3 && x <= 6) : [];
    if (!pars.length || (R.phase !== 'lobby' && R.phase !== 'done')) return;
    R.pars = pars; R.phase = 'play'; R.hole = 0; R.seed = crypto.randomBytes(4).readUInt32BE(0); for (const p of R.players) { p.scores = []; p.pu = false; p.wait = false; }
    R.players = R.players.filter(p => !p.out && (p.c || now() - (p.discAt || 0) < T.LOBBY_DROP)); R.away = null; startHole(R, 1); }
  const unout = R => { R.players = R.players.filter(p => !p.out); }; /* MP_KICK: back to the lobby: removed golfers' rows go */
  function startHole(R, n) {
    R.hole = n; R.phase = 'play'; R.cardAt = null; clearT(R, 'card'); R.flyskip = 0; /* (FLY_SKIP_ALL: a new hole, a new fly-over) */
    for (const p of R.players) { p.wait = false; /* late joiners are in from this hole */ if (p.out) { p.ball = { u: 0, v: 0, lie: 'tee', stroke: 1, done: true, holed: false, out: true }; continue; } /* MP_KICK: removed: no more holes (blank on the card) */ if (!p.c && p.discAt && R.hole > 1) p.pu = true; /* still gone at the end of the last hole: picked up from here on */
      p.ball = p.pu ? { u: 0, v: 0, lie: 'tee', stroke: 1, done: true, holed: false, puNow: true } : { u: 0, v: 0, lie: 'tee', stroke: 1, toPin: 1e4, done: false, holed: false };
      if (p.pu) p.scores[n - 1] = { s: R.pars[n - 1] + T.PU_OVER, par: R.pars[n - 1], pu: true }; }
    R.turn = null; nextTurn(R); }
  function nextTurn(R) {
    const live = R.players.filter(p => p.ball && !p.ball.done && !p.out); R.shot = null; R.autoFor = null; R.away = null; clearT(R, 'pf'); clearT(R, 'away');
    if (!live.length) return endHole(R);
    const tee = live.filter(p => p.ball.stroke === 1 && p.ball.lie === 'tee' && !p.ball.left);
    const pick = tee.length ? tee[0] : live.slice().sort((a, b) => (b.ball.toPin - a.ball.toPin) || (a.seat - b.seat))[0]; /* tee shots in seat order, then farthest from the hole */
    R.turn = pick.id; R.tstate = 'aim'; R.shotN++; R.idle = { start: now() + (NEXT_HOLD ? R.hold || 0 : 0), held: 0, holdAt: null }; R.hold = 0; sync(R); timers(R); }
  function timers(R) { /* the active golfer's clock: idle ring, auto-hit, or a dropped golfer's reconnect wait */
    clearT(R, 'idle'); clearT(R, 'ring'); clearT(R, 'auto'); clearT(R, 'nudge');
    const p = P(R, R.turn); if (!p || R.phase !== 'play') return;
    if (R.tstate === 'flight') { setT(R, 'next', T.NEXT_WAIT, () => fallbackNext(R)); return; }
    if (T.KICK && !p.c) { broadcast(R, { t: 'timer', pid: p.id, ms: null }); const I = R.idle || {}; setT(R, 'away', Math.max(0, Math.max(I.start || 0, p.discAt || now()) + T.IDLE - now()), () => away(R, p)); return; } /* MP_KICK: gone on their turn: no auto-play; away after IDLE */
    if (!p.c) { const wait = Math.max(1500, (p.discAt || now()) + T.RECONNECT - now()); broadcast(R, { t: 'timer', pid: p.id, ms: wait, total: T.RECONNECT, why: 'reconnect' }); setT(R, 'auto', wait, () => autoHit(R, true)); return; }
    const I = R.idle; if (I.holdAt) { const cap = Math.max(0, T.HOLD_CAP - (now() - I.holdAt)); setT(R, 'idle', cap, () => { I.held += now() - I.holdAt; I.holdAt = null; I.capped = true; timers(R); }); broadcast(R, { t: 'timer', pid: p.id, ms: null }); return; }
    if (T.KICK) { const idleIn = T.IDLE - (now() - I.start); /* MP_KICK: no auto-hit; at IDLE a "hurry" nudge ring (no countdown) and the others are told (away) */
      if (idleIn > 0) { if (I.ring !== false) broadcast(R, { t: 'timer', pid: p.id, ms: null }); I.ring = false; setT(R, 'ring', idleIn, () => timers(R)); }
      else { if (!I.ring) broadcast(R, { t: 'timer', pid: p.id, ms: null, nudge: true, why: 'nudge' }); I.ring = true; away(R, p); } return; }
    const left = T.IDLE + T.RING - (now() - I.start), ringIn = left - T.RING;
    if (ringIn > 0) { if (I.ring !== false) broadcast(R, { t: 'timer', pid: p.id, ms: null }); I.ring = false; setT(R, 'ring', ringIn, () => timers(R)); }
    else { broadcast(R, { t: 'timer', pid: p.id, ms: Math.max(0, left), total: T.RING, why: 'idle' }); I.ring = true; }
    setT(R, 'auto', Math.max(0, left), () => { if (now() - I.start < T.IDLE + T.RING - 50) return timers(R); autoHit(R, false); }); } /* (aim input moves I.start without rescheduling: checked when the timer fires) */
  function autoHit(R, proxyOnly) { const p = P(R, R.turn); if (!p || R.tstate !== 'aim') return;
    const proxy = () => { const q = R.players.find(x => x.c && x !== p); if (!q) return; R.autoFor = { pid: p.id, by: q.id }; send(q.c, { t: 'auto', pid: p.id }); };
    if (!proxyOnly && p.c) { R.autoFor = { pid: p.id, by: p.id }; send(p.c, { t: 'auto', pid: p.id }); setT(R, 'nudge', T.AUTO_NUDGE, () => { if (R.tstate === 'aim' && R.turn === p.id) proxy(); }); }
    else proxy(); }
  function away(R, p) { if (!T.KICK || R.phase !== 'play' || R.tstate !== 'aim' || R.turn !== p.id || R.away === p.id || p.out) return; R.away = p.id; sync(R); } /* MP_KICK: the others' modal */
  function back(R, p, quiet) { if (!T.KICK) return; let ch = false; if (R.away === p.id) { R.away = null; ch = true; } /* MP_KICK: they're back: the modal goes everywhere */
    if (R.phase === 'play' && R.turn === p.id && R.tstate === 'aim' && R.idle) { R.idle.start = now(); if (R.idle.ring || ch) timers(R); } if (ch && !quiet) sync(R); }
  function playFor(R, p, m) { const X = P(R, m.pid); /* MP_KICK: PLAY FOR <NAME>: this phone plays the away golfer's shot now (the proxy auto-hit) */
    if (!T.KICK || !X || X === p || R.phase !== 'play' || R.tstate !== 'aim' || R.turn !== X.id || R.away !== X.id || (R.autoFor && !R.autoFor.stale)) return;
    const was = (R.autoFor && R.autoFor.bys) || []; for (const id of was) { const q = P(R, id); if (q && q.c && q !== p) send(q.c, { t: 'auto-cancel', pid: X.id }); } /* a takeover: the earlier phone drops an AUTO HIT it hasn't played (if it already has, its shot still counts: first one wins) */
    R.autoFor = { pid: X.id, by: p.id, bys: [...was, p.id] }; send(p.c, { t: 'auto', pid: X.id }); sync(R);
    setT(R, 'pf', T.PF_WAIT, () => { if (R.autoFor && R.autoFor.pid === X.id && R.tstate === 'aim' && R.turn === X.id) { R.autoFor.stale = true; sync(R); } }); } /* (not played yet: someone else may take over; any phone that tapped it can still play it, the first shot counts) */
  function remove(R, p, m) { const X = P(R, m.pid); /* MP_KICK: REMOVE <NAME>: out of the room (their card stays, marked as left); the round carries on */
    if (!T.KICK || !X || X === p || X.out || (R.phase !== 'play' && R.phase !== 'hole') || R.away !== X.id) return;
    X.out = true; X.pu = false; X.wait = false; X.sid = null; X.discAt = now(); X.ball = { ...(X.ball || { u: 0, v: 0, lie: 'tee', stroke: 1, holed: false }), done: true, out: true }; R.away = null;
    if (X.c) { const o = X.c; X.c = null; o.room = null; o.pid = null; send(o, { t: 'removed', by: p.name, msg: 'You were removed from the room' }); }
    if (R.turn === X.id && R.tstate === 'aim') nextTurn(R); else sync(R); }
  function act(R, p, m) { if (R.turn !== p.id || R.tstate !== 'aim' || !R.idle) return; const I = R.idle;
    if (m.hold === true && !I.holdAt && !I.capped) I.holdAt = now(); else if (m.hold === false && I.holdAt) { I.held += now() - I.holdAt; I.holdAt = null; I.start = now(); } else if (m.hold == null) I.start = now(); timers(R); }
  const num = (x, lo, hi) => typeof x === 'number' && isFinite(x) && x >= lo && x <= hi;
  function shot(R, p, m) { /* from the active golfer, or the proxy playing for them */
    const as = m.as || p.id; if (R.phase !== 'play' || R.tstate !== 'aim' || R.turn !== as) return;
    if (as !== p.id && !(R.autoFor && R.autoFor.pid === as && (R.autoFor.by === p.id || (R.autoFor.bys || []).includes(p.id)))) return; /* (MP_KICK: any phone that tapped PLAY FOR this turn) */
    const r = m.res || {}; if (!num(r.u, -2000, 2000) || !num(r.v, -2000, 2000)) return;
    R.tstate = 'flight'; R.shot = { by: p.id, as, res: { u: r.u, v: r.v, lie: String(r.lie || 'rough').slice(0, 12), holed: !!r.holed, water: !!r.water, toPin: num(r.toPin, 0, 5000) ? r.toPin : 999 } };
    broadcast(R, { t: 'shot', from: as, by: p.id, n: R.shotN, auto: !!m.auto, d: m.d }, p); timers(R); }
  function next(R, p, m) { const as = m.as || p.id, q = P(R, as); if (!q || R.turn !== as || R.tstate !== 'flight' || !R.shot || R.shot.by !== p.id) return; /* only from the phone that played the shot */
    if (!num(m.stroke, 1, 40)) return; const b = m.ball || {}; if (!num(b.u, -2000, 2000) || !num(b.v, -2000, 2000)) return;
    if (NEXT_HOLD) { R.hold = num(m.hold, 0, T.HOLD_MAX) ? m.hold : 0; R.go = R.hold ? { by: p.id, n: R.shotN } : null; } /* NEXT_HOLD: the result card is still up for this long on the phones: the next golfer's idle clock starts after it (or at the hitter's 'go') */
    apply(R, q, { u: b.u, v: b.v, lie: String(m.lie || 'rough').slice(0, 12), stroke: Math.round(m.stroke), toPin: num(m.toPin, 0, 5000) ? m.toPin : 999, holed: !!m.holed, strokes: Math.round(m.strokes || m.stroke) }); }
  function fallbackNext(R) { const S = R.shot, q = S && P(R, S.as); if (!q || R.tstate !== 'flight') return; const b = q.ball, r = S.res;
    if (r.water) apply(R, q, { u: b.u, v: b.v, lie: b.lie, stroke: b.stroke + 2, toPin: b.toPin, holed: false });
    else apply(R, q, { u: r.u, v: r.v, lie: r.lie, stroke: b.stroke + 1, toPin: r.toPin, holed: r.holed, strokes: b.stroke }); }
  function apply(R, q, b) { clearT(R, 'next');
    const par = R.pars[R.hole - 1], MAXS = T.MAX_OVER > 0 ? par + T.MAX_OVER : par + 7; /* strokes taken (b.stroke is the next one to play): at par + 3 without holing out, the hole ends there (MAX_TRIPLE, as in single player) */
    if (b.holed) { q.ball = { ...q.ball, u: b.u, v: b.v, lie: 'green', toPin: 0, done: true, holed: true }; q.scores[R.hole - 1] = { s: b.strokes, par }; }
    else if (b.stroke - 1 >= MAXS) { q.ball = { ...q.ball, u: b.u, v: b.v, lie: b.lie, done: true }; q.scores[R.hole - 1] = { s: T.MAX_OVER > 0 ? MAXS : par + T.PU_OVER, par, pu: true, max: T.MAX_OVER > 0 }; } /* max: picked up at the triple-bogey cap (the card says "Picked up") */
    else q.ball = { u: b.u, v: b.v, lie: b.lie, stroke: b.stroke, toPin: b.toPin, done: !!q.out, holed: false }; /* (MP_KICK: a removed golfer's last shot lands, then they're done) */
    nextTurn(R); }
  function endHole(R) { R.turn = null; R.tstate = null; R.away = null; for (const p of R.players) if (!p.scores[R.hole - 1] && !p.wait && !p.out) p.scores[R.hole - 1] = { s: R.pars[R.hole - 1] + T.PU_OVER, par: R.pars[R.hole - 1], pu: true }; else if (p.wait) p.scores[R.hole - 1] = null; /* a late joiner's waiting hole stays blank */
    if (R.hole >= R.pars.length) { R.phase = 'done'; R.cardAt = null; sync(R); return; }
    R.phase = 'hole'; R.cardAt = now() + T.CARD_AUTO; sync(R); setT(R, 'card', T.CARD_AUTO, () => { if (R.phase === 'hole') startHole(R, R.hole + 1); }); }

  function message(c, data) {
    msgsIn++; bytesIn += data.length; let m; try { m = JSON.parse(data.toString('utf8')); } catch (e) { return; }
    if (!m || typeof m !== 'object' || typeof m.t !== 'string') return;
    if (!rate(c, m.t)) { if (m.t !== 'aim' && m.t !== 'typing' && m.t !== 'react' && m.t !== 'ff') send(c, { t: 'err', code: 'rate', msg: 'Slow down a little' }); return; }
    if (m.t === 'ping') return send(c, { t: 'pong', at: m.at });
    if (m.t === 'hello') return hello(c, m);
    const R = c.room, p = R && P(R, c.pid); if (!p) return send(c, { t: 'err', code: 'noroom', msg: 'Not in a room' });
    if (T.KICK && (m.t === 'act' || m.t === 'chat' || m.t === 'react' || (m.t === 'typing' && m.on) || (m.t === 'aim' && m.in) || (m.t === 'shot' && !m.auto && !m.as))) back(R, p); /* MP_KICK: coming back: their own input (aim only when flagged as the player's own: in:1, not a wind update) */
    if ((m.t === 'shot' || m.t === 'next') && typeof m.id === 'string') { const seen = R.seen || (R.seen = []); if (seen.includes(m.id)) return; seen.push(m.id.slice(0, 40)); if (seen.length > 64) seen.shift(); } /* a shot (or its result) resent after a reconnect counts once */
    switch (m.t) {
      case 'leave': return leave(c);
      case 'nine': if (NINES_PICK && NINES.includes(m.v) && (R.phase === 'lobby' || R.phase === 'done')) { R.nine = m.v; if (R.phase === 'done') { R.phase = 'lobby'; unout(R); } sync(R); } /* (MP_KICK: back in the lobby, removed golfers' rows go, as for 'lobby' / 'course') */ return; /* NINES_PICK: F9 / B9 / 18 on an 18-hole course, for the whole room (like 'course': anyone in the room, between rounds) */
      case 'who': if (/^[a-z]{2,16}$/.test(m.who || '') && (R.phase === 'lobby' || R.phase === 'done')) { const t = R.players.find(q => q !== p && q.who === m.who); if (t) return send(c, { t: 'err', code: 'taken', who: m.who, by: t.name, taken: R.players.filter(q => q !== p).map(q => ({ who: q.who, name: q.name })), msg: 'That golfer is taken' });
        p.who = m.who; p.name = nameFor(R, p, m.who, m.name); p.lefty = !!m.lefty; sync(R); } return;
      case 'course': if (COURSES[m.id] && (R.phase === 'lobby' || R.phase === 'done')) { R.course = m.id; if (R.phase === 'done') { R.phase = 'lobby'; unout(R); } sync(R); } return;
      case 'lobby': if (R.phase === 'done') { R.phase = 'lobby'; unout(R); sync(R); } return;
      case 'teeoff': if (R.players.filter(q => !q.out).length < T.MIN_PLAYERS && (R.phase === 'lobby' || R.phase === 'done')) return send(c, { t: 'err', code: 'min2', msg: 'Waiting for a friend to join' }); /* MP_MIN2 (an older phone just sees the message) */ return teeoff(R, m);
      case 'nexthole': if (R.phase === 'hole') startHole(R, R.hole + 1); return;
      case 'aim': if (R.turn === p.id && R.tstate === 'aim' && m.d && typeof m.d === 'object' && (!MP_AIMCAP || data.length <= T.AIM_MAX)) { broadcast(R, { t: 'aim', from: p.id, n: R.shotN, d: m.d }, p); if (R.idle && !R.idle.holdAt && (!T.KICK || m.in)) { R.idle.start = now(); if (R.idle.ring) timers(R); } } return; /* aiming is input: it holds off the idle clock (MP_KICK: only the player's own aim, in:1; wind updates don't) */
      case 'act': return act(R, p, m);
      case 'flyskip': if (FLY_SKIP_ALL && R.phase === 'play' && m.hole === R.hole && R.flyskip !== R.hole) { R.flyskip = R.hole; broadcast(R, { t: 'flyskip', hole: R.hole, from: p.id }, p); } return; /* FLY_SKIP_ALL: once per hole */
      case 'go': if (NEXT_HOLD && R.go && R.go.by === p.id && m.n === R.go.n) { R.go = null; broadcast(R, { t: 'go', n: m.n, from: p.id }, p); if (R.phase === 'play' && R.tstate === 'aim' && R.idle && R.idle.start > now()) { R.idle.start = now(); timers(R); } } return; /* NEXT_HOLD: the hitter tapped their result card away early (only that phone, once): the others may move on after 1.7 s, and the next golfer's clock starts now, as when that tap sent 'next' */
      case 'playfor': return playFor(R, p, m);
      case 'kick': return remove(R, p, m);
      case 'shot': return shot(R, p, m);
      case 'next': return next(R, p, m);
      case 'chat': { const s = typeof m.text === 'string' ? m.text.replace(/[\u0000-\u001f\u007f\u2028\u2029]/g, ' ').replace(/\s+/g, ' ').trim() : ''; if (!s || [...s].length > T.CHAT_MAX) return send(c, { t: 'err', code: 'chat', msg: 'Messages are 1 to 40 characters' });
        return broadcast(R, { t: 'chat', from: p.id, text: s, id: rid(6) }); }
      case 'typing': return broadcast(R, { t: 'typing', from: p.id, on: !!m.on }, p);
      case 'ff': if (R.tstate === 'flight' && R.shot && R.shot.by === p.id) broadcast(R, { t: 'ff', from: R.shot.as, n: R.shotN, on: !!m.on }, p); return; /* MP_FF_SHARE (Neil 11-17): the shooter holding fast-forward: the others' replay speeds up too */
      case 'react': if (EMO.includes(m.e)) broadcast(R, { t: 'react', from: p.id, e: m.e }); return;
    }
  }
  function stats() { let players = 0, conn = 0; for (const R of rooms.values()) { players += R.players.length; conn += R.players.filter(p => p.c).length; }
    const cpu = process.cpuUsage(), mu = process.memoryUsage(); setImmediate(() => ELD.reset());
    return { rooms: rooms.size, sockets: socks.size, players, connected: conn, bpSkip, bpCut, restored: restoredN, ended: endedN, msgsIn, msgsOut, bytesIn, bytesOut, mem: mu.rss, heap: mu.heapUsed, cpuMs: Math.round((cpu.user + cpu.system) / 1000), lag: { p50: +(ELD.percentile(50) / 1e6).toFixed(2), p99: +(ELD.percentile(99) / 1e6).toFixed(2), max: +(ELD.max / 1e6).toFixed(2) }, up: Math.round(process.uptime()) }; } /* lag: since the previous stats read (it resets) */
  function drain() { for (const c of [...socks]) kill(c, 1012); } /* MP_DRAIN: 1012 'service restart' to every phone: they reconnect (with their sid) to the new instance */
  return { upgrade, stats, T, rooms, drain };
})();
server.on('upgrade', (req, sock) => MP.upgrade(req, sock));
const MP_DRAIN = true; /* ROLLBACK: false -> SIGTERM (a Railway redeploy) kills the process at once: every phone sees an abrupt drop (1006) and buffered messages are lost (before perf2) */
if (MP_DRAIN) process.on('SIGTERM', () => { console.log('SIGTERM: closing sockets (1012) and exiting'); try { server.close(); } catch (e) {} try { MP.drain(); } catch (e) {} setTimeout(() => process.exit(0), 1500); });
server.listen(process.env.PORT || 3000, '0.0.0.0', () => console.log('Tee Party on port ' + (process.env.PORT || 3000)));
