const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => { const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1340, height: 600 }, deviceScaleFactor: +(process.argv[2] || 1) });
  await pg.goto('file:///home/claude/golf/avatar/crew/crew_preview.html'); await pg.waitForTimeout(500);
  const h = await pg.evaluate(() => document.body.scrollHeight);
  await pg.screenshot({ path: process.argv[3] || '/home/claude/golf/avatar/crew/crew_preview.png', clip: { x: 0, y: 0, width: 1340, height: h } }); await b.close(); })();
