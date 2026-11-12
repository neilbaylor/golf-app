const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/wrapped_t.html');
  const until = async (fn) => pg.waitForFunction(fn, null, { timeout: 900000, polling: 100 });
  await until(() => { const i = document.querySelector('#intro'); return i && !i.hidden; }); await pg.click('#introSkip');
  await until(() => document.querySelector('#boot.home') && !document.querySelector('#intro')); await pg.click('#playBtn');
  await until(() => !document.querySelector('#boot') && window.__G && __G.view === 'swing'); await pg.waitForTimeout(1500);
  await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await pg.waitForTimeout(1200);
  const c0 = await pg.evaluate(() => [__cam.position.x, __cam.position.z, __G.dir.u, __G.D]);
  await pg.mouse.move(300, 560); await pg.mouse.down(); await pg.waitForTimeout(120); for (let i = 1; i <= 10; i++) { await pg.mouse.move(300 - 29 * i, 560); await pg.waitForTimeout(30); }
  const tr = []; for (let k = 0; k < 6; k++) { await pg.waitForTimeout(250); tr.push(await pg.evaluate(() => { const A = __aimF(); return [Math.round(__cam.position.x), Math.round(__cam.position.z), A ? [Math.round(A.pan.x), Math.round(A.pan.z), +A.zoom.toFixed(2)] : null, __EDGE.kind, __G.club, __G.aimT]; })); } console.log(JSON.stringify(tr)); const c1 = await pg.evaluate(() => [__cam.position.x, __cam.position.z, __G.dir.u, __G.D]); await pg.mouse.up();
  console.log(JSON.stringify({ c0, c1 }), 'ERR', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
