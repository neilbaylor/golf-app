// node zoomcard.js who idx out.png  -> screenshot of state card idx at 2x
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const [who, idx, out] = process.argv.slice(2);
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 2 });
  await pg.route(/fonts\.(googleapis|gstatic)/, r => r.abort());
  await pg.goto('file:///home/claude/golf/avatar/crew/' + who + '/preview.html'); await pg.waitForTimeout(500);
  const els = await pg.$$('.st'); await els[+idx].screenshot({ path: out }); await b.close(); })();
