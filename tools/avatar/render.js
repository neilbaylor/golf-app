// usage: node render.js in.svg|in.html out.png W H [transparent]
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [inp, out, W, H, tr] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: +W, height: +H }, deviceScaleFactor: 1 });
  pg.on('pageerror', e => console.log('PAGEERR', e.message));
  if (inp.endsWith('.svg')) {
    const svg = fs.readFileSync(inp, 'utf8').replace(/<svg /, `<svg width="${W}" height="${H}" `);
    await pg.setContent(`<html><body style="margin:0;background:${tr ? 'transparent' : '#fff'}">${svg}</body></html>`);
  } else await pg.goto('file://' + path.resolve(inp));
  await pg.waitForTimeout(300);
  await pg.screenshot({ path: out, omitBackground: !!tr, clip: { x: 0, y: 0, width: +W, height: +H } });
  await b.close();
})();
