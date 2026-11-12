const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 } });
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.goto('file://' + path.resolve('/home/claude/golf/perfwork/out/b2/w.html'));
  await pg.waitForFunction(() => window.__ph && window.__fn > 2, null, { timeout: 300000 }); await pg.evaluate(() => { window.__pause = 1; });
  console.log(await pg.evaluate(() => { const g = __ph.groundHW; let mx = -1e9, at = null, n = 0;
    for (let u = -1800; u <= 1800; u += (Math.abs(u) < 160 ? .25 : 5)) for (let v = -1600; v <= 2000; v += ((v > -60 && v < 470) ? .25 : 5)) { const h = g(u, -v); n++; if (h > mx) { mx = h; at = [u, v]; } }
    return JSON.stringify({ samples: n, max: mx, at }); }));
  await b.close();
})();
