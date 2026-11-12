// node tools/plainflow.js <plain wrapped.html>
// The shipped code exactly as patched (no instrumentation, real clock): tee shot -> flight -> result card -> next shot ->
// aim view -> pitch near the green -> sand -> putt -> hole-out putt. Reports every page error and console error.
const { chromium } = require('playwright');
const path = require('path');
const [,, page] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.goto('file://' + path.resolve(page));
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 900000, polling: 100 });
  const steps = [];
  const step = (s) => { steps.push(s); console.log('  ok:', s); };
  const settle = async () => { await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await pg.waitForTimeout(500); };
  const swing = async (tag) => {
    const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3;
    const pull = await pg.evaluate(() => { const r = document.querySelector('#app').getBoundingClientRect(), q = document.querySelector('#dial').getBoundingClientRect(); return Math.min(Math.max(r.bottom - (q.top + q.height * .3) - 14, 105), 190); });
    const ps = await pg.evaluate(() => __G.D / __G.Feff); const tot = pull * Math.min(1, ps);
    await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 30; i++) { await pg.mouse.move(x, y + tot * i / 30); await pg.waitForTimeout(40); } await pg.waitForTimeout(300);
    for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + tot - (tot + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
    await until(() => __G.view === 'flight' || __SW.phase === 'idle');
    if (!(await pg.evaluate(() => __G.view === 'flight'))) { errs.push('swing did not launch: ' + tag); return; }
    step('launch ' + tag); await until(() => __G.view !== 'flight'); step('landed ' + tag + ' -> ' + await pg.evaluate(() => __G.view + ' ' + document.querySelector('#resWord').textContent));
  };
  const clearResult = async () => { await pg.evaluate(() => { const r = document.querySelector('#result'); if (!r.hidden) { const g = r.querySelector('#resBtns .btn.go'); g && g.click(); } }); await until(() => document.querySelector('#result').hidden && __G.view !== 'flight'); };
  await until(() => window.__G && __G.view === 'swing'); await pg.waitForTimeout(3000); await settle(); step('loaded, tee');
  await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); step('aim view'); await pg.click('#ballView'); await until(() => __G.aimT <= 0); step('back to swing view');
  await swing('tee'); await until(() => !document.querySelector('#result').hidden || __G.view === 'swing'); step('result card shown: ' + !(await pg.evaluate(() => document.querySelector('#result').hidden)));
  await clearResult(); await settle(); step('next shot at ' + JSON.stringify(await pg.evaluate(() => [__G.ball.u.toFixed(1), __G.ball.v.toFixed(1), __G.lie, __G.mode])));
  if (await pg.evaluate(() => __G.view === 'swing' && __G.aimGoal === 0)) { await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); step('aim view 2'); await pg.click('#ballView'); await until(() => __G.aimT <= 0); }
  await pg.evaluate(() => __setup(-20, 355)); await settle(); step('pitch setup ' + await pg.evaluate(() => __G.mode));
  await swing('pitch'); await clearResult(); await settle();
  await pg.evaluate(() => __setup(-12, 342)); await settle(); step('sand setup ' + await pg.evaluate(() => __G.lie + '/' + __G.mode));
  await swing('sand'); await clearResult(); await settle();
  await pg.evaluate(() => __setup(-27, 388)); await settle(); step('putt setup ' + await pg.evaluate(() => __G.mode + ' aimT=' + __G.aimT));
  await swing('putt'); await pg.waitForTimeout(1500); await clearResult().catch(() => {}); await settle();
  await pg.evaluate(() => __setup(-25, 391.2)); await settle(); await swing('hole-out'); await pg.waitForTimeout(3000);
  step('final: ' + await pg.evaluate(() => document.querySelector('#resWord').textContent + ' · ' + document.querySelector('#perf').textContent));
  console.log('PAGE ERRORS:', errs.length, JSON.stringify(errs));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
