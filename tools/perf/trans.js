// node tools/trans.js <wrapped.html> <out.json>
// Drives every camera transition at the virtual 60 Hz clock and records the per-frame camera (pos, look, fov):
//  swing->aim crane, aim->swing, reversal mid-crane, club change in aim view (aimFrame recomputed + camTween), putting setup
//  (overhead frame), putt launch (overhead -> putt chase), putt finish (chase -> overhead), short-game frame, full shot
//  launch (chase -> broadcast), landing -> result -> green preview flyover -> settle, preview cancelled by a tap.
// Analyse with tools/transan.js.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [,, page, out] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => { window.__VT = true; window.__logOn = true; let sd = 4242; Math.random = () => { sd |= 0; sd = sd + 0x6D2B79F5 | 0; let t = Math.imul(sd ^ sd >>> 15, 1 | sd); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; });
  await pg.goto('file://' + path.resolve(page));
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 900000, polling: 50 });
  const frames = async (n) => { const t = await pg.evaluate(() => window.__fn) + n; await until(t => window.__fn >= t, t); };
  const marks = []; const mark = async (n) => marks.push([n, await pg.evaluate(() => window.__fn)]);
  const settle = async () => { await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(10); };
  const swing = async (tag, frac = 1) => {
    const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3;
    const pull = await pg.evaluate(() => { const r = document.querySelector('#app').getBoundingClientRect(), q = document.querySelector('#dial').getBoundingClientRect(); return Math.min(Math.max(r.bottom - (q.top + q.height * .3) - 14, 105), 190); });
    const ps = await pg.evaluate(() => __G.D / __G.Feff); const tot = pull * Math.min(1, ps) * frac;
    await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 30; i++) { await pg.mouse.move(x, y + tot * i / 30); await pg.waitForTimeout(40); } await pg.waitForTimeout(300);
    for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + tot - (tot + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
    await until(() => __G.view === 'flight' || __SW.phase === 'idle');
    if (!(await pg.evaluate(() => __G.view === 'flight'))) { errs.push('no launch ' + tag); return false; }
    await mark('launch-' + tag); return true;
  };
  await until(() => window.__fn > 5); await frames(120); await settle();
  // 1. swing -> aim -> swing
  await mark('to-aim'); await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await frames(10);
  await mark('from-aim'); await pg.click('#ballView'); await until(() => __G.aimT <= 0); await frames(10);
  // 2. reversal mid-crane
  await mark('to-aim-reverse'); await pg.mouse.click(195, 330); await until(() => __G.aimT >= .45); await pg.click('#ballView'); await until(() => __G.aimT <= 0); await frames(10);
  // 3. club change while in aim view (aim frame recomputed, camTween .7)
  await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); await frames(10);
  await mark('aim-club'); await pg.evaluate(() => { const b = document.querySelector('#clubBtn'); b && b.click(); }); await frames(4);
  const picked = await pg.evaluate(() => { const c = [...document.querySelectorAll('#clubGrid .ct:not(.sel):not([disabled])')]; const t = c[Math.max(0, c.length - 3)]; if (t) { t.click(); return true; } return false; });
  if (!picked) await pg.evaluate(() => { document.querySelectorAll('.sheet').forEach(s => s.hidden = true); const sc = document.querySelector('#scrim'); if (sc) sc.hidden = true; });
  await settle(); await frames(10);
  await pg.click('#ballView'); await until(() => __G.aimT <= 0); await frames(10);
  // 4. full shot from the fairway: launch -> chase -> broadcast -> landing -> result -> preview flyover
  await mark('setup-fairway'); await pg.evaluate(() => __setup(-5, 230)); await settle();
  if (await swing('fairway')) { await until(() => __G.view !== 'flight'); await mark('land-fairway'); await until(() => !__G.preview && !__G.camTween); await frames(10); }
  await pg.evaluate(() => { const r = document.querySelector('#result'); if (!r.hidden) { const g = r.querySelector('#resBtns .btn.go'); g && g.click(); } }); await settle();
  // 5. short game frame + pitch
  await mark('setup-pitch'); await pg.evaluate(() => __setup(-20, 355)); await settle();
  if (await swing('pitch')) { await until(() => __G.view !== 'flight'); await mark('land-pitch'); await until(() => !__G.camTween && !__G.preview); await frames(20); }
  await pg.evaluate(() => { const r = document.querySelector('#result'); if (!r.hidden) { const g = r.querySelector('#resBtns .btn.go'); g && g.click(); } }); await settle();
  // 6. putting: overhead frame, putt launch (overhead -> chase), finish (back overhead)
  await mark('setup-putt'); await pg.evaluate(() => __setup(-27, 388)); await settle();
  if (await swing('putt', .8)) { await until(() => __G.view !== 'flight'); await mark('land-putt'); await until(() => !__G.camTween && !__G.preview); await frames(20); }
  // 7. preview cancelled by a tap: tee shot, tap during flyover
  await mark('setup-tee'); await pg.evaluate(() => { const r = document.querySelector('#result'); if (!r.hidden) { const g = r.querySelector('#resBtns .btn.go'); g && g.click(); } __setup(0, 0); }); await settle();
  if (await swing('tee')) { await until(() => __G.view !== 'flight'); await mark('land-tee'); await until(() => __G.preview && __G.preview.t > 1.0); await mark('preview-cancel'); await pg.mouse.click(60, 200); await until(() => !__G.preview && !__G.camTween); await frames(10); }
  await mark('end');
  const res = await pg.evaluate(() => ({ log: window.__log, T: window.__T, newProg: window.__newProg }));
  res.marks = marks; res.errs = errs; fs.writeFileSync(out, JSON.stringify(res));
  console.log('frames', res.log.length, 'marks', marks.map(m => m.join('@')).join(' '), 'errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
