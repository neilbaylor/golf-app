// node tools/dom.js <wrapped.html> <outJson> [keepGL]
// Section A: HTML/CSS/DOM cost per view. WebGL draws are stubbed (matrices still updated) so the page runs at real 60 Hz game
// speed on this CPU and the CDP timeline shows only JS + style/layout/paint/composite/raster work. Real-time clock (no __VT).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [,, page, out, keepGL] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.route('**/three.min.js', r => r.fulfill({ path: '/home/claude/golf/node_modules/three/build/three.min.js', contentType: 'text/javascript' }));
  await pg.route('**/fonts.googleapis.com/**', r => r.fulfill({ body: '', contentType: 'text/css' }));
  await pg.goto('file://' + path.resolve(page));
  const until = async (fn, arg, t = 120000) => pg.waitForFunction(fn, arg, { timeout: t, polling: 50 });
  await until(() => window.__R && window.__fn > 3);
  if (!keepGL) await pg.evaluate(() => { __R.render = function (s, c) { if (s.autoUpdate !== false) s.updateMatrixWorld(); if (c.parent === null) c.updateMatrixWorld(); }; });
  await pg.waitForTimeout(3500); // greeting + dial bakes
  const cdp = await pg.context().newCDPSession(pg);
  // layer tree
  await cdp.send('LayerTree.enable'); let layers = [];
  cdp.on('LayerTree.layerTreeDidChange', e => { if (e.layers) layers = e.layers; });
  const layerSnap = async () => {
    await pg.waitForTimeout(300); const L = layers.filter(l => l.drawsContent || true), res = [];
    for (const l of L) { let why = []; try { why = (await cdp.send('LayerTree.compositingReasons', { layerId: l.layerId })).compositingReasonIds || []; } catch (e) {}
      let node = ''; if (l.backendNodeId) { try { const d = await cdp.send('DOM.describeNode', { backendNodeId: l.backendNodeId }); node = d.node.localName + (d.node.attributes ? (i => i >= 0 ? '#' + d.node.attributes[i + 1] : '')(d.node.attributes.indexOf('id')) : ''); } catch (e) {} }
      res.push({ node, w: Math.round(l.width), h: Math.round(l.height), draws: l.drawsContent, paints: l.paintCount, why: why.join(',') }); }
    return res;
  };
  await cdp.send('DOM.enable');
  const cats = ['devtools.timeline', 'disabled-by-default-devtools.timeline', 'disabled-by-default-devtools.timeline.frame', 'blink.user_timing', 'disabled-by-default-devtools.timeline.stack'].join(',');
  const trace = async (name, act) => {
    const ev = []; const h = e => { for (const x of e.value) ev.push(x); }; cdp.on('Tracing.dataCollected', h);
    await cdp.send('Tracing.start', { categories: cats, transferMode: 'ReportEvents' });
    const fn0 = await pg.evaluate(() => window.__fn);
    await act();
    const fn1 = await pg.evaluate(() => window.__fn);
    const done = new Promise(r => cdp.once('Tracing.tracingComplete', r)); await cdp.send('Tracing.end'); await done; cdp.off('Tracing.dataCollected', h);
    // main renderer thread
    const tn = {}; for (const e of ev) if (e.ph === 'M' && e.name === 'thread_name') tn[e.pid + ':' + e.tid] = e.args.name;
    const main = Object.keys(tn).find(k => tn[k] === 'CrRendererMain' && ev.some(e => e.pid + ':' + e.tid === k && e.name === 'FireAnimationFrame'));
    const S = {}, add = (k, d) => { const r = S[k] = S[k] || { n: 0, ms: 0, max: 0 }; r.n++; r.ms += d; if (d > r.max) r.max = d; };
    let paintArea = 0, forced = 0, forcedMs = 0; const stack = [], byNode = {}, forcedBy = {};
    const M = ev.filter(e => e.pid + ':' + e.tid === main && e.ph === 'X' && e.dur != null).sort((a, b) => a.ts - b.ts);
    for (const e of M) {
      while (stack.length && stack[stack.length - 1].ts + stack[stack.length - 1].dur <= e.ts) stack.pop();
      const d = e.dur / 1000, inJS = stack.some(s => s.name === 'FunctionCall' || s.name === 'FireAnimationFrame' || s.name === 'TimerFire' || s.name === 'EventDispatch');
      if (['UpdateLayoutTree', 'Layout', 'Paint', 'PrePaint', 'Layerize', 'UpdateLayer', 'CompositeLayers', 'Commit', 'FireAnimationFrame', 'FunctionCall', 'TimerFire', 'EventDispatch', 'ParseHTML', 'HitTest', 'IntersectionObserverController::computeIntersections', 'ScrollLayer', 'Decode Image', 'Decode LazyPixelRef', 'ImageDecodeTask', 'UpdateLayerTree', 'PaintImage', 'GPUTask', 'MajorGC', 'MinorGC', 'V8.GC_SCAVENGER', 'BlinkGC.AtomicPhase', 'V8.GCScavenger', 'V8.GCFinalizeMC'].includes(e.name) || /GC/.test(e.name)) {
        add(e.name, d); if ((e.name === 'Layout' || e.name === 'UpdateLayoutTree') && inJS) { forced++; forcedMs += d; add('forced:' + e.name, d); const bd = e.args && (e.args.beginData || e.args.data) || {}, st = bd.stackTrace || (e.args && e.args.data && e.args.data.stackTrace) || []; const fnm = st.slice(0, 3).map(f => f.functionName + ':' + f.lineNumber).join('<') || '?'; const r = forcedBy[fnm] = forcedBy[fnm] || { n: 0, ms: 0 }; r.n++; r.ms += d; }
        if (e.name === 'Paint' && e.args && e.args.data) { const k = e.args.data.nodeId || 0; const r = byNode[k] = byNode[k] || { n: 0, ms: 0 }; r.n++; r.ms += d; }
      }
      if (e.name === 'Paint' && e.args && e.args.data && e.args.data.clip) { const c = e.args.data.clip; const xs = [c[0], c[2], c[4], c[6]], ys = [c[1], c[3], c[5], c[7]]; paintArea += (Math.max(...xs) - Math.min(...xs)) * (Math.max(...ys) - Math.min(...ys)); }
      stack.push(e);
    }
    // main thread busy (top level)
    let busy = 0, lastEnd = 0; for (const e of M) { if (e.ts >= lastEnd) { busy += e.dur / 1000; lastEnd = e.ts + e.dur; } }
    // raster / gpu work on other threads of the renderer process
    const R = {}; for (const e of ev) if (e.ph === 'X' && e.dur != null && (e.name === 'RasterTask' || e.name === 'ImageDecodeTask' || e.name === 'Decode Image')) { const r = R[e.name] = R[e.name] || { n: 0, ms: 0 }; r.n++; r.ms += e.dur / 1000; }
    const nF = (S.FireAnimationFrame || { n: 1 }).n, per = {};
    const nodes = []; for (const [k, v] of Object.entries(byNode).sort((a, b) => b[1].ms - a[1].ms).slice(0, 8)) { let nm = '#' + k; try { const d = await cdp.send('DOM.describeNode', { backendNodeId: +k }); const a = d.node.attributes || [], i = a.indexOf('id'); nm = d.node.localName + (i >= 0 ? '#' + a[i + 1] : '') + (a.indexOf('class') >= 0 ? '.' + a[a.indexOf('class') + 1].split(' ')[0] : ''); } catch (e) {} nodes.push(`${nm}: ${(v.ms / nF).toFixed(3)}ms/f n=${v.n}`); } for (const [k, v] of Object.entries(S)) per[k] = { perFrame: +(v.ms / nF).toFixed(3), n: v.n, max: +v.max.toFixed(2) };
    const res = { name, paintBy: nodes, forcedBy, frames: nF, gameFrames: fn1 - fn0, busyPerFrame: +(busy / nF).toFixed(3), paintPxPerFrame: Math.round(paintArea / nF), forcedPerFrame: +(forced / nF).toFixed(2), forcedMsPerFrame: +(forcedMs / nF).toFixed(3), raster: Object.fromEntries(Object.entries(R).map(([k, v]) => [k, { perFrame: +(v.ms / nF).toFixed(3), n: v.n }])), per };
    console.log(`${name.padEnd(12)} frames=${nF} mainBusy/f=${res.busyPerFrame}ms  rAF(JS)/f=${(per.FireAnimationFrame || {}).perFrame} style/f=${(per.UpdateLayoutTree || {}).perFrame} layout/f=${(per.Layout || {}).perFrame} prepaint/f=${(per.PrePaint || {}).perFrame} paint/f=${(per.Paint || {}).perFrame} (${res.paintPxPerFrame}px²) layerize/f=${(per.Layerize || {}).perFrame} commit/f=${(per.Commit || {}).perFrame} forced=${res.forcedPerFrame}(${res.forcedMsPerFrame}ms) raster/f=${(R.RasterTask ? (R.RasterTask.ms / nF).toFixed(3) : 0)} timers=${(per.TimerFire || {}).n || 0}`);
    console.log('   paint by node:', nodes.join(' | ')); if (Object.keys(forcedBy).length) console.log('   forced by:', JSON.stringify(forcedBy));
    return res;
  };
  const res = { views: [], layers: {} };
  const swingDrag = async (stopBeforeFlick) => {
    const d = await pg.locator('#dial').boundingBox(); const x = d.x + d.width / 2, y = d.y + d.height * .3;
    const ps = await pg.evaluate(() => Math.min(1, __G.D / __G.Feff)); const tot = 150 * ps;
    await pg.mouse.move(x, y); await pg.mouse.down(); for (let i = 1; i <= 30; i++) { await pg.mouse.move(x, y + tot * i / 30); await pg.waitForTimeout(40); } await pg.waitForTimeout(300);
    if (stopBeforeFlick) return { x, y, tot };
    for (let i = 1; i <= 8; i++) { await pg.mouse.move(x, y + tot - (tot + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
  };
  res.layers.tee = await layerSnap();
  res.views.push(await trace('tee-idle', () => pg.waitForTimeout(3000)));
  // swing: the back-swing drag, then the flick + flight
  let sw; res.views.push(await trace('swinging', async () => { sw = await swingDrag(true); }));
  res.layers.swinging = await layerSnap().catch(() => []);
  for (let i = 1; i <= 8; i++) { await pg.mouse.move(sw.x, sw.y + sw.tot - (sw.tot + 6) * i / 8); await pg.waitForTimeout(15); } await pg.mouse.up();
  await until(() => __G.view === 'flight');
  res.views.push(await trace('flight', async () => { await until(() => __G.view !== 'flight', null, 60000); }));
  res.views.push(await trace('result', async () => { await pg.waitForTimeout(1500); }));
  res.layers.result = await layerSnap();
  await until(() => document.querySelector('#result').hidden && __G.view === 'swing', null, 60000); await pg.waitForTimeout(4000);
  res.views.push(await trace('to-aim', async () => { await pg.mouse.click(195, 330); await until(() => __G.aimT >= 1); }));
  res.views.push(await trace('aim', () => pg.waitForTimeout(3000)));
  res.layers.aim = await layerSnap();
  res.views.push(await trace('from-aim', async () => { await pg.click('#ballView'); await until(() => __G.aimT <= 0); }));
  await pg.evaluate(() => __setup(-27, 388)); await until(() => __G.aimT >= 1 && !__G.camTween); await pg.waitForTimeout(1500);
  res.views.push(await trace('putting', () => pg.waitForTimeout(3000)));
  res.layers.putting = await layerSnap();
  await pg.evaluate(() => __setup(-20, 355)); await until(() => __G.aimT >= 1 && !__G.camTween); await pg.waitForTimeout(1500);
  res.views.push(await trace('shortgame', () => pg.waitForTimeout(3000)));
  res.errs = errs; fs.writeFileSync(out, JSON.stringify(res, null, 1));
  for (const [k, L] of Object.entries(res.layers)) console.log('layers', k, L.length, L.filter(l => l.draws).map(l => `${l.node || '?'} ${l.w}x${l.h} [${l.why}]`).join(' | '));
  console.log('errors', errs);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
