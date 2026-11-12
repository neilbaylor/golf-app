// node tools/transan.js <trans.json> [verbose]
// Per transition segment: peak camera speed, peak per-frame velocity change (|Δv|, yd/frame²) for position and look target,
// and velocity "steps": frames where the velocity changes by a large fraction of itself in one frame (a start/stop jolt or a
// target swapped mid-move). Smooth eased motion at 60 Hz changes velocity by a few % per frame.
const fs = require('fs');
const R = JSON.parse(fs.readFileSync(process.argv[2])); const verbose = process.argv[3];
const L = R.log, marks = R.marks; // [vt, ms, view, aimT, px,py,pz, lx,ly,lz, fov, ...]
const seg = marks.map((m, i) => [m[0], m[1], i + 1 < marks.length ? marks[i + 1][1] : L.length]);
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], len = a => Math.hypot(a[0], a[1], a[2]);
const v3 = (r, o) => [r[o], r[o + 1], r[o + 2]];
let total = 0;
for (const [name, a, b] of seg) {
  const out = { name, frames: b - a };
  const steps = [];
  for (const [nm, o] of [['pos', 4], ['look', 7]]) {
    let vmax = 0, dvmax = 0, at = 0;
    for (let i = Math.max(a, 2); i < b; i++) {
      const p0 = v3(L[i - 2], o), p1 = v3(L[i - 1], o), p2 = v3(L[i], o), v1 = sub(p1, p0), v2 = sub(p2, p1), dv = len(sub(v2, v1)), sp = Math.max(len(v1), len(v2));
      vmax = Math.max(vmax, len(v2)); if (dv > dvmax) { dvmax = dv; at = i; }
      if (dv > .04 && dv / (sp + 1e-9) > .35) steps.push(`${nm}@f${i + 1}(+${i - a}) |Δv|=${dv.toFixed(3)} v ${len(v1).toFixed(3)}→${len(v2).toFixed(3)} view=${L[i][2]} aimT=${L[i][3]} prev=${L[i][15]} tw=${L[i][16]}`);
    }
    out[nm] = `vmax ${vmax.toFixed(3)} yd/f, max|Δv| ${dvmax.toFixed(3)} @+${at - a}`;
  }
  let fovStep = 0; for (let i = Math.max(a, 2); i < b; i++) { const d1 = L[i][10] - L[i - 1][10], d0 = L[i - 1][10] - L[i - 2][10]; fovStep = Math.max(fovStep, Math.abs(d1 - d0)); }
  out.fov = `max Δ(fov rate) ${fovStep.toFixed(3)}°/f²`;
  total += steps.length;
  console.log(`${name.padEnd(16)} ${String(out.frames).padStart(4)}f  pos: ${out.pos}  | look: ${out.look} | ${out.fov}  | steps: ${steps.length}`);
  for (const s of steps.slice(0, verbose ? 50 : 4)) console.log('      ' + s);
}
console.log('TOTAL velocity steps:', total, ' errors:', R.errs);
