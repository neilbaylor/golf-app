// node tools/glcalls.js <wrapped.html> [views csv]
// Counts every WebGL call per frame in each settled view (and 2D-canvas readbacks), with bytes uploaded per frame and the GL usage
// of every buffer that gets re-uploaded. Finds per-frame uploads into STATIC_DRAW buffers (ANGLE-Metal keeps a single buffer for
// static usage, so updating one the GPU is still reading forces a CPU/GPU sync) and synchronous get*/readback calls.
const { chromium } = require('playwright');
const path = require('path');
const [,, page, viewsCsv = 'tee,tee-aim,fairway,putt,pitch,sand'] = process.argv;
const SETUP = { flight: null, tee: null, fairway: [4, 190], putt: [-27, 388], pitch: [-20, 355], sand: [-12, 342] };
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => {
    window.__VT = true; window.__logOn = true;
    const C = window.__glc = { on: false, n: {}, bytes: 0, staticUp: {}, usage: new WeakMap(), bound: {}, sync: {} };
    const SYNC = /^(get|is|readPixels|finish|checkFramebufferStatus|clientWaitSync)/;
    for (const P of [WebGL2RenderingContext.prototype, WebGLRenderingContext.prototype]) {
      for (const k of Object.getOwnPropertyNames(P)) {
        const d = Object.getOwnPropertyDescriptor(P, k); if (!d || typeof d.value !== 'function') continue; const f = d.value;
        P[k] = function (...a) {
          if (k === 'bindBuffer') C.bound[a[0]] = a[1];
          if (k === 'bufferData' && a[0] !== undefined) { const buf = C.bound[a[0]]; if (buf) C.usage.set(buf, a[2]); }
          if (C.on) {
            C.n[k] = (C.n[k] || 0) + 1; if (SYNC.test(k) && k !== 'getExtension') C.sync[k] = (C.sync[k] || 0) + 1;
            if (k === 'bufferSubData' || k === 'bufferData') { const len = a[2] && a[2].byteLength || (a[1] && a[1].byteLength) || 0; C.bytes += len; const buf = C.bound[a[0]], u = buf && C.usage.get(buf);
              if (k === 'bufferSubData') { const key2 = (u === 35044 ? 'S' : u === 35048 ? 'D' : String(u)) + ':' + len; (C.all = C.all || {})[key2] = (C.all[key2] || 0) + 1; }
              if (k === 'bufferSubData' && u === 35044 /* STATIC_DRAW */) { const key = (buf.__id || (buf.__id = Math.random().toString(36).slice(2, 7))) + ':' + len; C.staticUp[key] = (C.staticUp[key] || 0) + 1; } }
            if (k === 'texImage2D' || k === 'texSubImage2D') C.n[k + '_tex'] = (C.n[k + '_tex'] || 0) + 1;
          }
          return f.apply(this, a);
        };
      }
    }
    for (const [P, k] of [[CanvasRenderingContext2D.prototype, 'getImageData'], [HTMLCanvasElement.prototype, 'toDataURL'], [Element.prototype, 'getBoundingClientRect'], [window, 'getComputedStyle']]) {
      const f = P[k]; P[k] = function (...a) { if (C.on) C.sync['dom:' + k] = (C.sync['dom:' + k] || 0) + 1; return f.apply(this, a); };
    }
  });
  await pg.goto('file://' + path.resolve(page));
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 600000, polling: 100 });
  const frames = async (n) => { const t = await pg.evaluate(() => window.__fn) + n; await until(t => window.__fn >= t, t); };
  await until(() => window.__fn > 5); await frames(150);
  for (const v of viewsCsv.split(',')) {
    const base = v.replace('-aim', '');
    if (SETUP[base]) await pg.evaluate(([u, w]) => __setup(u, w), SETUP[base]);
    else if (base === 'tee') await pg.evaluate(() => __setup(0, 0));
    await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(60);
    if (v.endsWith('-aim')) { await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await frames(60); }
    if (v === 'flight') { await pg.evaluate(() => __setup(0, 0)); await until(() => !__G.camTween && !__G.preview && __G.aimT === 0); await frames(20);
      const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3, tot = 150;
      await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 30; i++) { await pg.mouse.move(x, y + tot * i / 30); await pg.waitForTimeout(40); } await pg.waitForTimeout(300);
      for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + tot - (tot + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
      await until(() => __G.view === 'flight'); await frames(10); }
    const f0 = await pg.evaluate(() => { const C = __glc; C.n = {}; C.all = {}; C.bytes = 0; C.staticUp = {}; C.sync = {}; C.on = true; return __fn; });
    await frames(30);
    const r = await pg.evaluate((f0) => { const C = __glc; C.on = false; const nf = __fn - f0; return { nf, all: C.all, n: C.n, bytes: C.bytes, staticUp: C.staticUp, sync: C.sync }; }, f0);
    const per = o => Object.fromEntries(Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, x]) => [k, +(x / r.nf).toFixed(2)]));
    const tot = Object.values(r.n).reduce((a, b) => a + b, 0);
    console.log(`\n== ${v}  frames=${r.nf}  glCalls/f=${(tot / r.nf).toFixed(0)}  uploadBytes/f=${(r.bytes / r.nf).toFixed(0)}`);
    console.log('   static-usage buffers re-uploaded (id:bytes -> per frame):', JSON.stringify(per(r.staticUp)));
    console.log('   all bufferSubData (usage:bytes -> per frame):', JSON.stringify(per(r.all || {})));
    console.log('   sync/readback calls per frame:', JSON.stringify(per(r.sync)));
    const top = Object.entries(per(r.n)).slice(0, 14).map(([k, x]) => `${k}=${x}`).join(' ');
    console.log('   top:', top);
    if (v.endsWith('-aim')) { await pg.click('#ballView'); await until(() => __G.aimT <= 0); }
  }
  console.log('\nerrors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
