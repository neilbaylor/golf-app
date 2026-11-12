const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/wrapped.html');
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 900000, polling: 100 });
  await until(() => { const i = document.querySelector('#intro'); return i && !i.hidden; }); await pg.click('#introSkip');
  await until(() => document.querySelector('#boot.home') && !document.querySelector('#intro')); await pg.click('#playBtn');
  await until(() => !document.querySelector('#boot')); await until(() => window.__G && __G.view === 'swing'); await pg.waitForTimeout(3000);
  await until(() => !__G.camTween && !__G.preview); await pg.waitForTimeout(500);
  await pg.screenshot({ path: 'out/lift_swing.png' });
  await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await pg.waitForTimeout(800); await pg.screenshot({ path: 'out/lift_aim.png' });
  await pg.click('#ballView'); await until(() => __G.aimT <= 0); await pg.waitForTimeout(500);
  const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3;
  const pull = await pg.evaluate(() => { const r = document.querySelector('#app').getBoundingClientRect(), q = document.querySelector('#dial').getBoundingClientRect(); return Math.min(Math.max(r.bottom - (q.top + q.height * .3) - 14, 105), 190); });
  await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 30; i++) { await pg.mouse.move(x, y + pull * i / 30); await pg.waitForTimeout(40); } await pg.waitForTimeout(300);
  for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + pull - (pull + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
  await until(() => __G.view === 'flight');
  const info = await pg.evaluate(() => ({ apex: __G.shot.apex, carry: __G.shot.carry, dur: __G.shot.dur }));
  console.log(JSON.stringify(info));
  for (const f of [.25, .45, .65, .85]) { await until(f => !__G.shot || __G.shot.phase !== 'air' || __G.shot.t >= f, f); await pg.screenshot({ path: `out/lift_fl${Math.round(f * 100)}.png` }); console.log('t', await pg.evaluate(() => __G.shot && [__G.shot.t.toFixed(2), __G.ball && 0])); }
  await until(() => __G.view !== 'flight'); await pg.waitForTimeout(600); await pg.screenshot({ path: 'out/lift_after.png' });
  console.log('ERR', errs.length, JSON.stringify(errs.slice(0, 5)));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
