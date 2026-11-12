// node tools/probe.js <wrapped.html> <setupJSON|tee> <js expression evaluated each frame for N frames>
const { chromium } = require('playwright'); const path = require('path');
const [,, page, setup, expr, N = 6] = process.argv;
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
  await until(() => window.__fn > 5); await frames(150);
  if (setup !== 'tee') await pg.evaluate(a => __setup(a[0], a[1]), JSON.parse(setup));
  await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(60);
  for (let i = 0; i < +N; i++) { await frames(1); console.log(await pg.evaluate(expr)); }
  console.log('errors', errs); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
