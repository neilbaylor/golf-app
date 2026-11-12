const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 393, height: 750 }, deviceScaleFactor: 2 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/' + (process.argv[2] || 'wrapped_t.html'));
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 900000, polling: 100 });
  await until(() => { const i = document.querySelector('#intro'); return i && !i.hidden; }); await pg.click('#introSkip');
  await until(() => document.querySelector('#boot.home') && !document.querySelector('#intro')); await pg.click('#playBtn');
  await until(() => !document.querySelector('#boot')); await until(() => window.__G && __G.view === 'swing'); await pg.waitForTimeout(1500);
  const P = await pg.evaluate(() => __cup.PIN);
  for (const [n, d] of [['long', 21], ['mid', 9], ['short', 1.4]]) {
    await pg.evaluate(([d, P]) => { __setup(P.u, P.v - d); }, [d, P]); await until(() => __G.aimT >= 1 && !__G.camTween); await pg.waitForTimeout(1200);
    await pg.screenshot({ path: `out/putt_${n}${process.argv[3] || ''}.png` }); console.log(n, await pg.evaluate(() => __G.lie + ' ' + __G.mode));
  }
  console.log('ERR', errs); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
