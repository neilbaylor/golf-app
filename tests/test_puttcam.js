const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/wrapped.html');
  const until = async (fn) => pg.waitForFunction(fn, null, { timeout: 900000, polling: 50 });
  await until(() => { const i = document.querySelector('#intro'); return i && !i.hidden; }); await pg.click('#introSkip');
  await until(() => document.querySelector('#boot.home') && !document.querySelector('#intro')); await pg.click('#playBtn');
  await until(() => !document.querySelector('#boot') && window.__G && __G.view === 'swing'); await pg.waitForTimeout(1000);
  const P = await pg.evaluate(() => __cup.PIN); await pg.evaluate(P => __setup(P.u + .5, P.v - 6), P); await until(() => __G.aimT >= 1 && !__G.camTween); await pg.waitForTimeout(800);
  const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3;
  await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 15; i++) { await pg.mouse.move(x, y + 30 * i / 15); await pg.waitForTimeout(25); } await pg.waitForTimeout(250);
  for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + 30 - 36 * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
  await until(() => __G.view === 'flight'); await until(() => __G.view !== 'flight');
  const tr = []; for (let i = 0; i < 40; i++) { tr.push(await pg.evaluate(() => +( __cam.position.y).toFixed(1))); await pg.waitForTimeout(60); }
  console.log(await pg.evaluate(() => __G.mode + ' ' + __G.view), JSON.stringify(tr), 'ERR', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
