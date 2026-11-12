// node tools/flow.js <wrapped.html> <outJson>
// Full play flow at a virtual 60 Hz clock: idle swing -> aim -> back -> tee swing -> flight -> result -> next shot ->
// pitch near green -> sand -> putting overhead -> hole-out. Records per-frame logs + function timers + page errors.
const { chromium } = require('playwright');
const fs = require('fs');
const [,, page, out] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => { window.__VT = true; window.__logOn = true; window.__LT = []; try { new PerformanceObserver(l => { for (const e of l.getEntries()) window.__LT.push([+e.startTime.toFixed(0), +e.duration.toFixed(0), window.__fn || 0]); }).observe({ entryTypes: ['longtask'] }); } catch (e) {} });
  await pg.goto('file://' + require('path').resolve(page));
  const marks = [];
  const mark = async (name) => marks.push([name, await pg.evaluate(() => window.__fn)]);
  const frames = async (n) => { const t = await pg.evaluate(() => window.__fn) + n; await pg.waitForFunction(t => window.__fn >= t, t, { timeout: 600000, polling: 50 }); };
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 600000, polling: 100 });
  await until(() => window.__fn > 5); await frames(90); await mark('idle-swing');
  await frames(40);
  await mark('tap-aim'); await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await frames(30);
  await mark('aim-back'); await pg.click('#ballView'); await until(() => __G.aimT <= 0); await frames(20);
  const swing = async (tag) => {
    await mark('swing-' + tag);
    const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3;
    const pull = await pg.evaluate(() => { const r = document.querySelector('#app').getBoundingClientRect(), q = document.querySelector('#dial').getBoundingClientRect(); return Math.min(Math.max(r.bottom - (q.top + q.height * .3) - 14, 105), 190); });
    const ps = await pg.evaluate(() => __G.D / __G.Feff); const tot = pull * Math.min(1, ps);
    await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 30; i++) { await pg.mouse.move(x, y + tot * i / 30); await pg.waitForTimeout(40); } await pg.waitForTimeout(300);
    for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + tot - (tot + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
    await until(() => __G.view === 'flight' || __SW.phase === 'idle');
    const flew = await pg.evaluate(() => __G.view === 'flight'); if (!flew) { errs.push('swing did not launch: ' + tag); return; }
    await mark('flight-' + tag);
    await until(() => __G.view !== 'flight'); await mark('result-' + tag);
  };
  await swing('tee');
  await until(() => __G.view !== 'result' && document.querySelector('#result').hidden); await mark('next-1'); await frames(200);
  // aim view on the second shot
  if (await pg.evaluate(() => __G.view === 'swing' && __G.aimGoal === 0)) { await mark('tap-aim2'); await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await frames(20); await pg.click('#ballView'); await until(() => __G.aimT <= 0); await frames(10); }
  // pitch near the green
  await mark('setup-pitch'); await pg.evaluate(() => __setup(-20, 355)); await frames(120);
  await swing('pitch'); await until(() => document.querySelector('#result').hidden && __G.view !== 'flight'); await frames(60);
  // sand
  await mark('setup-sand'); await pg.evaluate(() => __setup(-12, 342)); await frames(120);
  await swing('sand'); await until(() => document.querySelector('#result').hidden && __G.view !== 'flight'); await frames(60);
  // putting, overhead
  await mark('setup-putt'); await pg.evaluate(() => __setup(-27, 388)); await until(() => __G.aimT >= 1); await frames(60); await mark('putt-idle'); await frames(60);
  await swing('putt'); await frames(60);
  // hole-out: a short straight putt
  await mark('setup-hole'); await pg.evaluate(() => __setup(-25, 391.2)); await until(() => __G.aimT >= 1); await frames(30);
  await swing('hole'); await frames(80); await mark('end');
  const res = await pg.evaluate(() => ({ log: window.__log, T: window.__T, newProg: window.__newProg, progs: __R.info.programs.length, t1: window.__t1, LT: window.__LT, holed: !document.querySelector('#result').hidden && document.querySelector('#resWord').textContent }));
  res.marks = marks; res.errs = errs;
  fs.writeFileSync(out, JSON.stringify(res));
  console.log('firstFrameAt', res.t1 && res.t1.toFixed(0), 'ms', 'frames', res.log.length, 'errors', errs.length, errs.slice(0, 5), 'holed', res.holed, 'programs', res.progs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
