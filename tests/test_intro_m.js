const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/wrapped.html');
  const until = async (fn) => pg.waitForFunction(fn, null, { timeout: 900000, polling: 100 });
  await until(() => { const i = document.querySelector('#intro'); return i && !i.hidden; });
  for (const t of []) { await pg.waitForTimeout(t); const r = await pg.evaluate(() => { const e = document.querySelector('#introGrid').getBoundingClientRect(); return { x: e.x, y: e.y, width: e.width, height: e.height }; }); await pg.screenshot({ path: `out/im_${t}.png`, clip: r }); }
  await until(() => document.querySelector('#boot.home') && !document.querySelector('#intro')); await pg.click('#playBtn');
  await until(() => !document.querySelector('#boot') && window.__G && __G.view === 'swing');
  const r = await pg.evaluate(() => { const e = document.querySelector('#player').getBoundingClientRect(); return { x: e.x, y: e.y, width: e.width, height: e.height }; });
  for (let i = 0; i < 10; i++) { await pg.waitForTimeout(1500); await pg.screenshot({ path: `out/idle_${i}.png`, clip: r }); }
  console.log('ERR', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
