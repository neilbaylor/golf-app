const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 393, height: 695 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  let slow = false; await pg.route('**/three.min.js', async r => { await new Promise(x => setTimeout(x, 1500)); r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }); });
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/wrapped.html', { waitUntil: 'commit' });
  const hs = []; for (let i = 0; i < 25; i++) { hs.push(await pg.evaluate(() => { const e = document.querySelector('#bunch'); if (!e) return null; const r = e.getBoundingClientRect(); return Math.round(r.width) + 'x' + Math.round(r.height); }).catch(() => 'nav')); await pg.waitForTimeout(250); }
  console.log(JSON.stringify(hs), 'ERR', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
