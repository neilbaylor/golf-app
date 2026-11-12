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
  await until(() => !document.querySelector('#boot') && window.__G && __G.view === 'swing'); await pg.waitForTimeout(1000);
  const P = await pg.evaluate(() => __cup.PIN);
  for (const [tag, back, hold] of [['good', 300, 300], ['quick', 300, 40], ['slow', 300, 1400]]) {
    await pg.evaluate(P => { __setup(P.u + 2, P.v - 40); __setMode('flop'); }, P); await pg.waitForTimeout(2500);
    const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3, pull = 150;
    await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 20; i++) { await pg.mouse.move(x, y + pull * i / 20); await pg.waitForTimeout(back / 20); } await pg.waitForTimeout(hold);
    for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + pull - (pull + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
    await until(() => __G.view !== 'swing' || __SW.phase === 'idle'); const st = await pg.evaluate(() => __G.view === 'flight' ? [__G.mode, __G.lie, Math.round(__G.shot.carry), __G.shot.ratio.toFixed(2), document.querySelector('#stamp').textContent] : 'no launch');
    console.log(tag, JSON.stringify(st)); await until(() => __G.view !== 'flight'); await pg.waitForTimeout(800);
    await pg.evaluate(() => { const g = document.querySelector('#resBtns .btn.go'); if (g && !document.querySelector('#result').hidden) g.click(); }); await pg.waitForTimeout(800);
  }
  console.log('ERR', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
