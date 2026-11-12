// node tools/physeq.js <wrapped.html>  -> hash of 400 seeded PHYS.fly+ground results and planShot() at 12 setups x clubs/aims,
// plus timing. Run on base and patched builds: identical hashes = bit-identical physics.
const { chromium } = require('playwright');
const path = require('path');
const [,, page] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => { window.__VT = true; });
  await pg.goto('file://' + path.resolve(page));
  await pg.waitForFunction(() => window.__G && window.__fn > 3, null, { timeout: 600000 });
  await pg.evaluate(() => { window.__pause = 1; });
  const r = await pg.evaluate(() => {
    const { PHYS, groundHW, lieAt, gradUV } = __ph; let sd = 99; const R = () => { sd = (sd * 16807) % 2147483647; return sd / 2147483647; };
    let h = 2166136261; const mix = v => { const s = typeof v === 'number' ? v.toString() : String(JSON.stringify(v)); for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } };
    const t0 = performance.now(); let n = 0;
    for (let i = 0; i < 400; i++) {
      const u = -60 + R() * 60, v = -5 + R() * 420; const p = { x: u, y: groundHW(u, -v) - .01, z: -v };
      const o = { p, yaw: (R() - .5) * .6, launch: 4 + R() * 50, spin: 1500 + R() * 9000, tilt: (R() - .5) * 60, speed: 8 + R() * 80, wind: R() < .5 ? null : { x: (R() - .5) * 8, z: (R() - .5) * 8 } };
      const f = PHYS.fly(o, groundHW, R() < .5 ? 1 / 120 : 1 / 240); n++;
      mix(f.pts.length); mix(f.t); mix(f.apex); mix(f.v); const L = f.pts[f.pts.length - 1]; mix(L); mix(f.pts[f.pts.length >> 1]);
      if (i % 4 === 0) { const g = PHYS.ground(f, lieAt, groundHW, gradUV, 1 / 120, true); mix(g.pts.length); mix(g.lie); mix(g.pts[g.pts.length - 1]); }
    }
    const tFly = performance.now() - t0;
    // planShot through the live game state, several setups / clubs / aim directions
    const t1 = performance.now(); let np = 0;
    for (const [u, v] of [[0, 0], [-5, 230], [4, 190], [30, 120], [-20, 355], [-12, 342], [10, 300], [-30, 80]]) {
      __setup(u, v);
      for (let k = 0; k < 6; k++) { __G.dir = { u: Math.sin((k - 2.5) * .05), v: Math.cos((k - 2.5) * .05) }; __G.D = Math.max(5, __G.Feff * (.55 + k * .08)); const pl = __ph.planShot(); np++;
        mix(pl.speed); mix(pl.yawc); mix(pl.f.pts.length); mix(pl.f.pts[pl.f.pts.length - 1]); mix(pl.track ? pl.track.length : 0); }
    }
    return { hash: (h >>> 0).toString(16), flies: n, msFly: +tFly.toFixed(1), plans: np, msPlan: +(performance.now() - t1).toFixed(1) };
  });
  console.log(path.basename(path.dirname(page)), JSON.stringify(r), 'errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
