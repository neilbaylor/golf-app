// node tools/ablate.js <wrapped.html> <view: putt|tee|aim|pitch> [rounds] [variantsCsv]
// GPU attribution with SwiftShader as a proxy: in a settled view, hide one thing at a time (measurement only) and take the
// median real frame interval over N frames. Rounds alternate the variants so background load (other processes) averages out.
const { chromium } = require('playwright');
const path = require('path');
const [,, page, view = 'putt', rounds = 3, only] = process.argv;
const V = {
  base: ['0', '0'],
  grain: ['window.__noGrain=1', 'window.__noGrain=0'],
  bg: ['window.__bg=__S.background; __S.background=null', '__S.background=window.__bg'],
  outer: ['__S.userData.outer.visible=false', '__S.userData.outer.visible=true'],
  tiles: ['__S.traverse(o=>{ if(o.userData.courseTile) o.visible=false; })', '__S.traverse(o=>{ if(o.userData.courseTile) o.visible=true; })'],
  detail: ['window.__dt=null; __S.traverse(o=>{ if(o.userData.courseTile){ const u=o.material.uniforms; if(!window.__dt){ window.__dt=u.detail.value; } u.detail.value=window.__white||(window.__white=new THREE.DataTexture(new Uint8Array([255,255,255]),1,1,THREE.RGBFormat)); window.__white.needsUpdate=true; } })', '__S.traverse(o=>{ if(o.userData.courseTile) o.material.uniforms.detail.value=window.__dt; })'],
  tufts: ['__S.traverse(o=>{ if(o.userData.tuft) { o.userData.__v=o.visible; o.visible=false; o.userData.__hid=1; } })', '0'],
  read: ['__S.traverse(o=>{ if((o.isLineSegments && o.material.opacity<.3) || (o.isInstancedMesh && o.renderOrder===3)) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  readGrid: ['__S.traverse(o=>{ if(o.isLineSegments && o.material.opacity<.3) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  readArrows: ['__S.traverse(o=>{ if(o.isInstancedMesh && o.renderOrder===3) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  trees: ['__S.traverse(o=>{ if(o.isInstancedMesh && !o.userData.tuft && o.renderOrder!==3) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  hulls: ['__S.traverse(o=>{ if(o.material && o.material.side===1 && !o.material.stencilWrite) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
  transp: ['__S.traverse(o=>{ if(o.material && o.material.transparent) o.layers.disable(0); })', '__S.traverse(o=>o.layers.enable(0))'],
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
  if (view === 'putt') await pg.evaluate(() => __setup(-27, 388)); else if (view === 'pitch') await pg.evaluate(() => __setup(-20, 355)); else if (view === 'aim') await pg.mouse.click(195, 330);
  await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(60);
  const meas = async (n = 24) => { const f0 = await pg.evaluate(() => window.__fn); await until(t => window.__fn >= t, f0 + n + 2); return pg.evaluate((f0) => { const L = window.__log.slice(f0 + 1); const d = []; for (let i = 1; i < L.length; i++) d.push(L[i][14] - L[i - 1][14]); d.sort((a, b) => a - b); return d[d.length >> 1]; }, f0); };
  const names = only ? only.split(',') : Object.keys(V); const R = {}; names.forEach(k => R[k] = []);
  for (let r = 0; r < +rounds; r++) for (const k of (r % 2 ? names.slice().reverse() : names)) { await pg.evaluate(V[k][0]); await frames(3); R[k].push(await meas()); await pg.evaluate(V[k][1]); if (k === 'tufts') await pg.evaluate(() => __S.traverse(o => { if (o.userData.__hid) { o.visible = o.userData.__v; o.userData.__hid = 0; } })); await frames(2); }
  const med = a => a.slice().sort((x, y) => x - y)[a.length >> 1];
  const base = med(R.base || [0]);
  for (const k of names) console.log(view.padEnd(6), k.padEnd(11), med(R[k]).toFixed(1).padStart(7), 'ms', base ? ('Δ ' + (med(R[k]) - base).toFixed(1)).padStart(9) : '', JSON.stringify(R[k].map(x => +x.toFixed(0))));
  console.log('calls', await pg.evaluate(() => __R.info.render.calls), 'errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
