// usage: node shoot.js <who> [dpr] -> crew/<who>/preview.png (full page) + live HUD frames in work/tmp
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const who = process.argv[2], dpr = +(process.argv[3] || 1), page = process.argv[4] || 'preview.html';
const D = '/home/claude/golf/avatar/crew/' + who + '/', T = '/home/claude/golf/avatar/crew/work/tmp/';
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: dpr });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => m.type() === 'error' && !/fonts|ERR_/.test(m.text()) && errs.push(m.text()));
  await pg.route(/fonts\.(googleapis|gstatic)/, r => r.abort());
  await pg.goto('file://' + D + page); await pg.waitForTimeout(1200);
  if (page === 'preview.html') await pg.screenshot({ path: D + 'preview.png', fullPage: true });
  const hud = await pg.$('#app');
  for (let i = 0; i < 6; i++) { await pg.waitForTimeout(450); await hud.screenshot({ path: T + `live_${who}${page === 'preview.html' ? '' : '_hat'}${i}.png` }); }
  const perf = await pg.evaluate(() => { const t = performance.now(); for (let i = 0; i < 2000; i++) AV.update(1 / 60, i / 60); return (performance.now() - t) / 2000; });
  const st = await pg.evaluate(() => ({ mouth: document.querySelector('#avMouth').getAttribute('d').slice(0, 20), fill: document.querySelector('#avMouth').getAttribute('fill'), brows: document.querySelector('#avBrows').getAttribute('d').slice(0, 14) }));
  console.log(who, page, 'errors:', errs.length ? errs : 'none', '| AV.update ms/frame', perf.toFixed(4), JSON.stringify(st));
  await b.close();
})();
