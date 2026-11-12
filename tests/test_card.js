const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/wrapped.html');
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 900000, polling: 100 });
  await until(() => { const i = document.querySelector('#intro'); return i && !i.hidden; }); await pg.click('#introSkip');
  await until(() => document.querySelector('#boot.home') && !document.querySelector('#intro')); await pg.click('#playBtn');
  await until(() => !document.querySelector('#boot')); await until(() => window.__G && __G.view === 'swing'); await pg.waitForTimeout(1500);
  for (const pen of [0, 1]) {
    await pg.evaluate(pen => { const G = __G; G.stroke = 4 + pen; G.log = [{ n: 1, club: 'Driver', mode: 'full', total: 252, lie: pen ? 'water' : 'fairway', pin: 140, pen }, { n: 2 + pen, club: '8 Iron', mode: 'full', total: 150, lie: 'green', pin: 6 }, { n: 3 + pen, club: 'Putter', putt: true, lie: 'green', pin: 1.2, gimme: true }, { n: 4 + pen, club: 'Putter', putt: true, gimme: true, conceded: true, lie: 'green', pin: 0, holed: true }];
      const r = document.querySelector('#result'); r.classList.add('final'); document.querySelector('#resCard').innerHTML = __holeCard(G.log); document.querySelector('#resWord').textContent = pen ? 'BOGEY' : 'PAR'; r.hidden = false; }, pen);
    await pg.waitForTimeout(900);
    const box = await pg.evaluate(() => { const e = document.querySelector('#result').getBoundingClientRect(); return { x: e.x - 8, y: e.y - 8, width: e.width + 16, height: e.height + 16 }; });
    await pg.screenshot({ path: `out/card${pen}.png`, clip: box });
    if (!pen) { const g = await pg.evaluate(() => { const b = [...document.querySelectorAll('.sc li.in b')].pop(); const r = b.getBoundingClientRect(), li = b.parentElement.getBoundingClientRect(); return { b: [r.top, r.bottom], li: [li.top, li.bottom], txt: b.textContent }; }); console.log(JSON.stringify(g)); await pg.screenshot({ path: 'out/gimme_zoom.png', clip: await pg.evaluate(() => { const e = [...document.querySelectorAll('.sc li.in')].pop().getBoundingClientRect(); return { x: e.x + e.width - 110, y: e.y - 4, width: 112, height: e.height + 8 }; }) }); }
  }
  console.log('ERR', errs); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
