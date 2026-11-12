// node tools/analyze.js out/x_flow.json  -> segment stats, camera discontinuities, late shader compiles, function timers
const fs = require('fs');
const R = JSON.parse(fs.readFileSync(process.argv[2]));
const L = R.log, marks = R.marks; // log row: [vt, ms, view, aimT, px,py,pz, lx,ly,lz, fov, progs, calls, tris, realNow, preview, tween, swPhase]
const fn0 = R.log.length ? null : 0;
// frame numbers: log index i corresponds to fn = i + 1 (logging on from the first frame)
const seg = [];
for (let i = 0; i < marks.length; i++) seg.push([marks[i][0], marks[i][1], i + 1 < marks.length ? marks[i + 1][1] : L.length]);
const pct = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(s.length * p))]; };
console.log('segment'.padEnd(16), 'frames  jsMean  jsP95  jsMax  realMs(GPU proxy)  calls  tris');
for (const [name, a, b] of seg) {
  const rows = L.slice(a, b); if (!rows.length) continue;
  const js = rows.map(r => r[1]); const real = []; for (let i = 1; i < rows.length; i++) real.push(rows[i][14] - rows[i - 1][14]);
  console.log(name.padEnd(16), String(rows.length).padStart(6), (js.reduce((x, y) => x + y, 0) / js.length).toFixed(2).padStart(7), pct(js, .95).toFixed(2).padStart(6), Math.max(...js).toFixed(1).padStart(6),
    (real.length ? pct(real, .5).toFixed(0) : '-').padStart(10), String(Math.round(rows.reduce((s, r) => s + r[12], 0) / rows.length)).padStart(12), String(Math.round(rows.reduce((s, r) => s + r[13], 0) / rows.length)).padStart(7));
}
// camera jerk: second difference of position / look (per 1/60 s step). Flag frames whose jerk is far above the local median
const jerks = [];
const v3 = (r, o) => [r[o], r[o + 1], r[o + 2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], len = a => Math.hypot(...a);
for (let i = 2; i < L.length; i++) {
  for (const [nm, o] of [['pos', 4], ['look', 7]]) {
    const p0 = v3(L[i - 2], o), p1 = v3(L[i - 1], o), p2 = v3(L[i], o);
    const v1 = sub(p1, p0), v2 = sub(p2, p1), acc = len(sub(v2, v1)), sp = Math.max(len(v1), len(v2));
    jerks.push({ i, nm, acc, sp, ratio: acc / (sp + .02), view: L[i][2], aimT: L[i][3], prev: L[i][15], tw: L[i][16], ph: L[i][17] });
  }
}
const segOf = i => { let s = '?'; for (const [n, a] of seg) if (i >= a) s = n; return s; };
const bad = jerks.filter(j => j.acc > .25 && j.ratio > .5).sort((a, b) => b.acc - a.acc);
console.log('\ncamera discontinuities (|Δv| per frame > .25 yd and > 50% of speed):', bad.length);
for (const j of bad.slice(0, 25)) console.log(`  f${j.i + 1} ${segOf(j.i).padEnd(13)} ${j.nm.padEnd(4)} |Δv|=${j.acc.toFixed(3)} speed=${j.sp.toFixed(3)} view=${j.view} aimT=${j.aimT} preview=${j.prev} tween=${j.tw} sw=${j.ph}`);
// fov steps
const fovJ = []; for (let i = 2; i < L.length; i++) { const a = L[i][10] - L[i - 1][10], b = L[i - 1][10] - L[i - 2][10]; if (Math.abs(a - b) > .6) fovJ.push(`f${i + 1} ${segOf(i)} Δfov ${b.toFixed(2)}→${a.toFixed(2)} view=${L[i][2]}`); }
console.log('fov velocity jumps (>0.6°/frame change):', fovJ.length); fovJ.slice(0, 10).forEach(x => console.log('  ' + x));
console.log('\nprograms at end:', R.progs, ' compiled after first 10 frames:');
for (const p of (R.newProg || []).filter(p => p.fn > 10)) console.log(`  f${p.fn} ${segOf(p.fn - 1).padEnd(13)} +${p.n} program(s) view=${p.view} mode=${p.mode} frameJS=${p.ms}ms`);
console.log('\nfunction timers (count, total ms, max ms, calls >4ms [frame,ms]):');
for (const [k, v] of Object.entries(R.T || {}).sort((a, b) => b[1][2] - a[1][2])) console.log('  ' + k.padEnd(15), String(v[0]).padStart(6), v[1].toFixed(1).padStart(9), v[2].toFixed(1).padStart(7), JSON.stringify(v[3].slice(0, 6)));
const big = L.map((r, i) => [i + 1, r[1], r[2], segOf(i)]).filter(r => r[1] > 12).sort((a, b) => b[1] - a[1]);
console.log('\nworst frames (JS ms):'); big.slice(0, 15).forEach(r => console.log(`  f${r[0]} ${r[1]}ms ${r[2]} ${r[3]}`));
console.log('\nlong tasks (startMs, durMs, frame#) >50ms:', JSON.stringify((R.LT || []).filter(x => x[1] > 50)));
console.log('first frame at', R.t1 && R.t1.toFixed(0), 'ms after navigation');
console.log('\nerrors:', R.errs);
