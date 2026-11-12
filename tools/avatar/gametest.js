// node gametest.js <game copy.html> <tag> [pick]  -- loads a scratch copy headless (swiftshader), plays through the home
// screen, then drives talking, blinking and every mood, checking the DOM follows the character's tables. Zero-JS-error check.
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const fs = require('fs');
const [file, tag, pick] = process.argv.slice(2); const T = '/home/claude/golf/avatar/crew/work/gametest/';
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const errs = []; pg.on('pageerror', e => errs.push('pageerror: ' + e.message)); pg.on('console', m => m.type() === 'error' && errs.push('console: ' + m.text()));
  await pg.route('**/three.min.js', r => r.fulfill({ body: fs.readFileSync('/home/claude/golf/node_modules/three/build/three.min.js'), contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: fs.readFileSync('/home/claude/golf/fonts.css'), contentType: 'text/css' }));
  await pg.route('**/fonts.gstatic.com/**', r => r.abort());
  const t0 = Date.now();
  await pg.goto('file://' + file);
  await pg.waitForSelector('#boot.home', { timeout: 180000 });
  const faces = await pg.$$eval('#bunch .face', f => f.map(x => x.dataset.who));
  await pg.screenshot({ path: T + `${tag}-home.png` });
  if (pick) { await pg.click(`#bunch .face[data-who="${pick}"]`); await pg.waitForTimeout(300); }
  await pg.click('#playBtn');
  await pg.waitForFunction(() => !document.querySelector('#boot'), null, { timeout: 180000 });
  const tBoot = ((Date.now() - t0) / 1000).toFixed(1);
  const res = await pg.evaluate(async () => {
    const AV = window.__AV(), q = s => document.querySelector(s), sleep = ms => new Promise(r => setTimeout(r, ms));
    const out = { name: q('#player .nametag').textContent, svgs: q('#player').querySelectorAll('svg').length, headL: !!q('#player svg.avHeadL #avHead') };
    // talking: sample mouth shapes while the bubble types
    AV.say('Hey! Let\'s tee it up, big swing coming.', { mood: 'happy', force: true });
    const shapes = new Set(), fills = new Set(), ry = new Set(), tf = new Set();
    for (let i = 0; i < 40; i++) { await sleep(50); shapes.add(q('#avMouth').getAttribute('d')); fills.add(q('#avMouth').getAttribute('fill')); tf.add(q('svg.avHeadL').style.transform); }
    out.talkShapes = shapes.size; out.talkFills = [...fills]; out.headMoves = tf.size; out.talking = q('#app').classList.contains('talking');
    // blinking: watch eye ry for a few seconds
    let minRy = 9; for (let i = 0; i < 120; i++) { await sleep(50); const r = +q('#avEyeL').getAttribute('ry'); minRy = Math.min(minRy, r); ry.add(r); }
    out.blinkMinRy = minRy; out.ryValues = ry.size;
    // moods
    out.moods = {};
    for (const m of ['happy', 'focus', 'watch', 'oops', 'sad', 'nervous', 'proud']) {
      AV.say('', { force: true }); AV.setMood(m, 3); await sleep(700);
      out.moods[m] = { mouth: q('#avMouth').getAttribute('d').slice(0, 24), fill: q('#avMouth').getAttribute('fill'), brows: q('#avBrows').getAttribute('d').slice(0, 18), sweat: q('#avSweat').getAttribute('opacity') };
    }
    return out;
  });
  await pg.evaluate(() => window.__AV().say('Pured it! Right down the middle.', { mood: 'happy', force: true }));
  await pg.waitForTimeout(500);
  await pg.screenshot({ path: T + `${tag}-play.png`, clip: { x: 0, y: 0, width: 390, height: 220 } });
  console.log(JSON.stringify({ tag, bootSeconds: tBoot, roster: faces, ...res, errors: errs }));
  await b.close();
})().catch(e => { console.log(JSON.stringify({ tag, fatal: String(e) })); process.exit(1); });
