// node tools/bench.js <wrapped.html> <view: putt|tee|aim|pitch|fairway> [reps] [variantsCsv]
// Precise GPU-proxy cost of one frame's draw, independent of vsync quantisation: in a settled view, synchronously render the
// frame (scene + grain) R times, forcing completion each time with a 1-px readPixels, and take the median ms. Variants hide one
// thing at a time (measurement only) so the cost can be attributed. Rounds interleave variants so background noise averages out.
const { chromium } = require('playwright');
const path = require('path');
const [,, page, view = 'putt', reps = 5, only] = process.argv;
const V = {
  base: ['0', '0'],
  critters: ['__S.traverse(o=>{ if(o.geometry && o.geometry.isInstancedBufferGeometry) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  green: ['__S.traverse(o=>{ if(o.userData.courseTile){ const u=o.material.uniforms; if(u.gbox && u.gbox.value.z>0){ u.__gz=u.gbox.value.z; u.gbox.value.z=0; } } })', '__S.traverse(o=>{ if(o.userData.courseTile){ const u=o.material.uniforms; if(u.gbox && u.__gz!==undefined) u.gbox.value.z=u.__gz; } })'],
  grain: ['window.__noGrain=1', 'window.__noGrain=0'],
  bg: ['window.__bg=__S.background; __S.background=null', '__S.background=window.__bg'],
  outer: ['__S.userData.outer.layers.disable(0)', '__S.userData.outer.layers.enable(0)'],
  tiles: ['__S.traverse(o=>{ if(o.userData.courseTile) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  detail: ['__S.traverse(o=>{ if(o.userData.courseTile || o===__S.userData.outer){ const u=o.material.uniforms; if(!u.__dt) u.__dt=u.detail.value; u.detail.value=window.__white||(window.__white=(()=>{const t=new __THREE.DataTexture(new Uint8Array([255,255,255]),1,1,__THREE.RGBFormat); t.needsUpdate=true; return t;})()); } })', '__S.traverse(o=>{ if(o.userData.courseTile || o===__S.userData.outer){ const u=o.material.uniforms; if(u.__dt) u.detail.value=u.__dt; } })'],
  tufts: ['__S.traverse(o=>{ if(o.userData.tuft) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  readGrid: ['__S.traverse(o=>{ if(o.isLineSegments && o.material.opacity<.3) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  readArrows: ['__S.traverse(o=>{ if(o.isInstancedMesh && o.renderOrder===3) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  trees: ['__S.traverse(o=>{ if(o.isInstancedMesh && !o.userData.tuft && o.renderOrder!==3) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  hulls: ['__S.traverse(o=>{ if(o.material && o.material.side===1 && !o.material.stencilWrite) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  transp: ['__S.traverse(o=>{ if(o.material && o.material.transparent) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  sprites: ['__S.traverse(o=>{ if(o.isSprite) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  cup: ['__S.traverse(o=>{ if(o.material && o.material.stencilWrite) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  all: ['__S.traverse(o=>{ if(o.isMesh||o.isSprite||o.isLine||o.isPoints) o.layers.disable(0); }); window.__noGrain=1; window.__bg=__S.background; __S.background=null', '__S.traverse(o=>o.layers.enable(0)); window.__noGrain=0; __S.background=window.__bg'],
};
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => { window.__VT = true; window.__logOn = true; });
  await pg.goto('file://' + path.resolve(page));
  const until = async (fn, arg) => pg.waitForFunction(fn, arg, { timeout: 600000, polling: 100 });
  const frames = async (n) => { const t = await pg.evaluate(() => window.__fn) + n; await until(t => window.__fn >= t, t); };
  await until(() => window.__fn > 5); await frames(150);
  if (view === 'putt') await pg.evaluate(() => __setup(-27, 388)); else if (view === 'pitch') await pg.evaluate(() => __setup(-20, 355));
  else if (view === 'fairway') await pg.evaluate(() => __setup(4, 190)); else if (view === 'sand') await pg.evaluate(() => __setup(-12, 342));
  else if (view === 'aim') await pg.mouse.click(195, 330);
  await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(60);
  const names = only ? only.split(',') : Object.keys(V); const R = {}; names.forEach(k => R[k] = []);
  const once = () => pg.evaluate((n) => { const gl = __R.getContext(), px = new Uint8Array(4), out = [];
    window.__frameHook && window.__frameHook();
    for (let i = 0; i < n; i++) { const t0 = performance.now(); __R.clear(); __R.render(__S, __C); if (!window.__noGrain) __R.render(__grain.sc, __grain.cam); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); out.push(performance.now() - t0); }
    out.sort((a, b) => a - b); return out[n >> 1]; }, 7);
  await pg.evaluate(() => { window.__pause = 1; }); await pg.waitForTimeout(500);
  await pg.evaluate(() => { const gl = __R.getContext(), px = new Uint8Array(4); for (let i = 0; i < 3; i++) { __R.clear(); __R.render(__S, __C); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); } });
  for (let r = 0; r < +reps; r++) for (const k of (r % 2 ? names.slice().reverse() : names)) { await pg.evaluate(V[k][0]); R[k].push(await once()); await pg.evaluate(V[k][1]); }
  const med = a => a.slice().sort((x, y) => x - y)[a.length >> 1];
  const base = med(R.base || [0]);
  const info = await pg.evaluate(() => ({ calls: __R.info.render.calls, tris: __R.info.render.triangles, size: __R.domElement.width + 'x' + __R.domElement.height }));
  for (const k of names) console.log(view.padEnd(7), k.padEnd(11), med(R[k]).toFixed(2).padStart(7), 'ms', base ? ('Δ ' + (med(R[k]) - base).toFixed(2)).padStart(9) : '', JSON.stringify(R[k].map(x => +x.toFixed(1))));
  console.log(JSON.stringify(info), 'errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
