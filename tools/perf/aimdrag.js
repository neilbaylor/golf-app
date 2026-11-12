// node tools/aimdrag.js <wrapped.html> [setup u,v | tee]
// Main-thread cost while dragging the aim target around (each move re-plans the shot: planShot -> PHYS.fly passes) and while
// stepping through clubs. Reports per-call ms for planShot / updateTracer / MINI etc. from the instrumented timers.
const { chromium } = require('playwright');
const path = require('path');
const [,, page, setup = 'tee'] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => { window.__VT = true; window.__logOn = true; });
  await pg.goto('file://' + path.resolve(page));
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 600000, polling: 50 });
  const frames = async (n) => { const t = await pg.evaluate(() => window.__fn) + n; await until(t => window.__fn >= t, t); };
  await until(() => window.__fn > 5); await frames(120);
  if (setup !== 'tee') await pg.evaluate(a => __setup(a[0], a[1]), setup.split(',').map(Number));
  await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(30);
  if (await pg.evaluate(() => __G.aimT === 0)) { await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await frames(30); }
  await pg.evaluate(() => { window.__T = {}; window.__dragF0 = __fn; });
  // drag the target in a slow arc: one move per frame
  await pg.mouse.move(195, 300); await pg.mouse.down(); await frames(6);
  for (let i = 0; i < 40; i++) { const a = i / 39 * Math.PI; await pg.mouse.move(195 + Math.cos(a) * 110, 300 - Math.sin(a) * 90 + i * 2); await frames(1); }
  await pg.mouse.up(); await frames(5);
  const r = await pg.evaluate(() => { const L = window.__log.slice(window.__dragF0), js = L.map(x => x[1]).sort((a, b) => a - b);
    return { frames: L.length, jsMed: js[js.length >> 1], jsP95: js[Math.floor(js.length * .95)], jsMax: js[js.length - 1], T: Object.fromEntries(Object.entries(window.__T).map(([k, v]) => [k, { n: v[0], mean: +(v[1] / v[0]).toFixed(3), max: +v[2].toFixed(2) }])) }; });
  console.log('drag', setup, JSON.stringify({ frames: r.frames, jsMed: r.jsMed, jsP95: r.jsP95, jsMax: r.jsMax }));
  for (const [k, v] of Object.entries(r.T).sort((a, b) => b[1].mean * b[1].n - a[1].mean * a[1].n)) console.log('  ', k.padEnd(14), JSON.stringify(v));
  console.log('errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
