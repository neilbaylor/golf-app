// node tools/drawlist.js <wrapped.html> <view: putt|tee|aim|pitch>
// Dumps every draw call of one settled frame: object, material, transparency, blending, renderOrder, instances,
// vertices, and the approximate on-screen area (projected bounding sphere, clipped to the viewport) -> fill-rate suspects.
const { chromium } = require('playwright');
const path = require('path');
const [,, page, view = 'putt'] = process.argv;
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
  await until(() => !__G.camTween && !__G.preview && (__G.aimT === 0 || __G.aimT === 1)); await frames(30);
  await pg.evaluate(() => {
    const R = __R, orig = R.renderBufferDirect.bind(R), T = __THREE, v = new T.Vector3(), W = R.domElement.width, H = R.domElement.height;
    window.__dl = [];
    R.renderBufferDirect = function (camera, scene, geo, mat, obj, group) {
      if (window.__dlOn) {
        let area = -1;
        if (!obj.isInstancedMesh && geo.boundingSphere !== undefined) {
          if (!geo.boundingSphere) geo.computeBoundingSphere();
          const s = geo.boundingSphere, c = v.copy(s.center).applyMatrix4(obj.matrixWorld), r = s.radius * obj.matrixWorld.getMaxScaleOnAxis();
          const pv = c.clone().applyMatrix4(camera.matrixWorldInverse), d = -pv.z;
          if (d > r) { const p = c.clone().project(camera), pr = r / d / Math.tan(camera.fov * Math.PI / 360) * H / 2, x = (p.x * .5 + .5) * W, y = (-p.y * .5 + .5) * H;
            area = Math.max(0, Math.min(W, x + pr) - Math.max(0, x - pr)) * Math.max(0, Math.min(H, y + pr) - Math.max(0, y - pr)) / (W * H); } else area = 1;
        }
        __dl.push({ type: obj.type + (obj.name ? ':' + obj.name : ''), mat: mat.type, tr: mat.transparent, blend: mat.blending, at: mat.alphaTest, a2c: !!mat.alphaToCoverage, side: mat.side, ro: obj.renderOrder, inst: obj.isInstancedMesh ? obj.count : 0,
          verts: geo.index ? geo.index.count : (geo.attributes.position ? geo.attributes.position.count : 0), area: +area.toFixed(3), ud: Object.keys(obj.userData).join(','), depthTest: mat.depthTest, stencil: mat.stencilWrite, map: !!(mat.map || (mat.uniforms && mat.uniforms.map)) });
      }
      return orig(camera, scene, geo, mat, obj, group);
    };
    window.__dlOn = true; setTimeout(() => { window.__dlOn = false; }, 0);
  });
  await frames(2);
  const dl = await pg.evaluate(() => { const f = __dl.slice(); return { dl: f, fn: __fn, cam: __C.position.toArray(), gl: __R.domElement.width + 'x' + __R.domElement.height, calls: __R.info.render.calls }; });
  console.log(view, 'canvas', dl.gl, 'cam', dl.cam.map(x => x.toFixed(1)).join(','), 'calls(info)', dl.calls, 'listed', dl.dl.length);
  for (const d of dl.dl) console.log(`${String(d.ro).padStart(4)} ${(d.tr ? 'T' : 'O')} ${d.type.padEnd(22)} ${d.mat.padEnd(20)} area=${String(d.area).padEnd(6)} inst=${String(d.inst).padEnd(5)} verts=${String(d.verts).padEnd(7)} blend=${d.blend} at=${d.at} a2c=${d.a2c} side=${d.side} dT=${d.depthTest} st=${d.stencil} ${d.ud}`);
  console.log('errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
