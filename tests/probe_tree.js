const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ path: '/home/claude/golf/fonts.css', contentType: 'text/css' }));
  await pg.goto('file:///home/claude/golf/wrapped.html');
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 900000, polling: 100 });
  await until(() => { const i = document.querySelector('#intro'); return i && !i.hidden; }); await pg.click('#introSkip');
  await until(() => document.querySelector('#boot.home') && !document.querySelector('#intro')); await pg.click('#playBtn');
  await until(() => !document.querySelector('#boot')); await until(() => window.__G && __G.view === 'swing'); await pg.waitForTimeout(2000);
  const res = await pg.evaluate(() => {
    const out = []; const T = __trees.filter(t => !t.pine && t.blobs);
    for (const t of T) for (const back of [5, 7, 9, 12]) for (const side of [-3, -1.5, 0, 1.5, 3]) {
      // ball 'back' yd before the tree toward the tee (tee ~ v=0)
      const L = Math.hypot(t.u, t.v) || 1, du = -t.u / L, dv = -t.v / L, u = t.u + du * back + dv * side, v = t.v + dv * back - du * side;
      if (__ph.lieAt(u, v) !== 'rough') continue;
      __setup(u, v); __G.club = 1; const plan = __ph.planShot(); const P = plan.f.pts;
      let minHit = 1e9, minVis = 1e9;
      for (let i = 1; i < P.length; i++) { const a = P[i - 1], c = P[i]; for (let j = 0; j < 6; j++) { const k = j / 6, x = a.x + (c.x - a.x) * k, y = a.y + (c.y - a.y) * k, z = a.z + (c.z - a.z) * k;
        const rel = y - t.gy; for (const [bx, by, bv, br] of t.blobs) { const d = Math.hypot(x - (t.u + bx), -z - (t.v + bv), rel - by); minHit = Math.min(minHit, d - br * .97); minVis = Math.min(minVis, d - (br * 1.12 + .3)); } } }
      out.push({ u: +u.toFixed(1), v: +v.toFixed(1), back, side, tree: !!plan.tree, minHit: +minHit.toFixed(2), minVis: +minVis.toFixed(2), h: +t.h.toFixed(1), r: +t.r.toFixed(1) });
    }
    return out; });
  const vis = res.filter(r => !r.tree && r.minVis < 0);
  console.log('total', res.length, 'treeHit', res.filter(r => r.tree).length, 'visual-overlap-but-no-hit', vis.length);
  console.log(JSON.stringify(vis.slice(0, 12)));
  console.log('ERR', errs.length, errs.slice(0,3)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
