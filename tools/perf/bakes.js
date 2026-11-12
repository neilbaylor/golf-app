// node tools/bakes.js <wrapped.html> [dpr]  -> every synchronous canvas.toDataURL / getImageData during the first 8 s (dial bakes etc.)
const { chromium } = require('playwright'); const path = require('path');
const [,, page, dpr = 3] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: +dpr });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.addInitScript(() => { window.__BK = []; const f = HTMLCanvasElement.prototype.toDataURL; HTMLCanvasElement.prototype.toDataURL = function (...a) { const t = performance.now(); const r = f.apply(this, a); window.__BK.push(['toDataURL', this.width + 'x' + this.height, +(performance.now() - t).toFixed(1), +t.toFixed(0)]); return r; };
    const d = CanvasRenderingContext2D.prototype.drawImage; CanvasRenderingContext2D.prototype.drawImage = function (...a) { const t = performance.now(); const r = d.apply(this, a); const ms = performance.now() - t; if (ms > 2) window.__BK.push(['drawImage', this.canvas.width + 'x' + this.canvas.height, +ms.toFixed(1), +t.toFixed(0)]); return r; }; });
  await pg.goto('file://' + path.resolve(page));
  await pg.waitForTimeout(9000);
  console.log('dpr', dpr, JSON.stringify(await pg.evaluate(() => window.__BK)), 'errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
