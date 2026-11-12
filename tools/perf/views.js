// node tools/views.js <wrapped.html> <outPrefix> [ablate]
// Settles each static view, reseeds Math.random, renders exactly N frames at the virtual 60 Hz clock, grabs the WebGL canvas
// (deterministic) + a page screenshot, and measures the real time per frame (SwiftShader GPU proxy) and JS ms.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [,, page, prefix, ablate] = process.argv;
const VIEWS = [
  ['tee', null], ['tee-aim', 'aim'], ['fairway', [4, 190]], ['fairway-aim', 'aim'], ['rough', [30, 120]], ['pitch', [-20, 355]], ['sand', [-12, 342]], ['putt', [-27, 388]], ['putt-far', [-36, 374]]];
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => { window.__VT = true; window.__logOn = true; });
  await pg.goto('file://' + path.resolve(page));
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 600000, polling: 100 });
  const frames = async (n) => { const t = await pg.evaluate(() => window.__fn) + n; await until(t => window.__fn >= t, t); };
  await until(() => window.__fn > 5); await frames(200); // avatar greeting + bakes done
  const out = {};
  for (const [name, how] of VIEWS) {
    if (how === 'aim') { await pg.mouse.click(195, 330); }
    else if (how) { await pg.evaluate(([u, v]) => __setup(u, v), how); }
    await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(140);
    if (ablate) await pg.evaluate(ablate);
    const f0 = await pg.evaluate(() => { window.__reseedAt = window.__fn + 2; window.__grabAt = window.__fn + 32; return window.__fn; });
    await until(t => window.__fn >= t + 40, f0);
    const r = await pg.evaluate((f0) => { const L = window.__log.slice(f0 + 2, f0 + 40); const real = []; for (let i = 1; i < L.length; i++) real.push(L[i][14] - L[i - 1][14]); real.sort((a, b) => a - b);
      return { realMs: real[real.length >> 1], js: +(L.reduce((s, r) => s + r[1], 0) / L.length).toFixed(2), calls: L[L.length - 1][12], tris: L[L.length - 1][13], aimT: __G.aimT, mode: __G.mode, lie: __G.lie, img: window.__grabbed }; }, f0);
    fs.writeFileSync(`${prefix}_${name}.png`, Buffer.from(r.img.split(',')[1], 'base64')); delete r.img;
    await pg.screenshot({ path: `${prefix}_${name}_page.png` });
    out[name] = r; console.log(name.padEnd(12), JSON.stringify(r));
    if (how === 'aim') { await pg.click('#ballView'); await until(() => __G.aimT <= 0); }
  }
  fs.writeFileSync(`${prefix}_views.json`, JSON.stringify(out, null, 1));
  console.log('errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
