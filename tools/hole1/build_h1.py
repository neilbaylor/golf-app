"""Toronto Hunt hole 1 (300 yd par 4, dogleg right along the Lake Ontario bluff).
Builds hole1/h1.html from sketchy-golf.html; the main file is never touched.
Geometry traced from the Google aerial (hole1/ref.png), see geo.py / geo2.py: tee at (0,0), the tee->green line is +v, 0.24 yd/px."""
import re
SRC = '/home/claude/golf/sketchy-golf.html'
s = open(SRC).read()
def R(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:100], s.count(a)); s = s.replace(a, b)
def RB(start, end, new):
    """replace from start (inclusive) through end (inclusive)"""
    global s
    i = s.index(start); j = s.index(end, i) + len(end); s = s[:i] + new + s[j:]

# ---------------------------------------------------------------- 1. hole geometry
RB("const CL = [[0, -10]", "const PIN = { u: -25, v: 393 };", r"""// Toronto Hunt #1, traced from the aerial: the fairway's left and right edges, the green, the deep bunker left of it, the practice area,
// the cart path (out of bounds beyond it), the tree line down the right and the Lake Ontario bluff past it
const FWL = [[-20.7, 92.9], [-26.5, 95.7], [-33.5, 105.4], [-37.5, 117.0], [-41.4, 128.6], [-45.4, 140.2], [-48.3, 152.4], [-49.2, 165.7], [-50.0, 179.1], [-48.8, 193.7], [-48.7, 200.7], [-46.5, 208.9], [-44.3, 217.1], [-42.2, 225.3], [-37.9, 234.7], [-33.7, 244.2], [-30.5, 253.0], [-26.2, 262.4], [-18.7, 270.9], [-10.9, 279.0]];
const FWR = [[-16.6, 95.3], [-11.9, 104.1], [-8.6, 119.9], [-10.5, 132.7], [-15.5, 143.7], [-22.6, 153.4], [-28.6, 163.8], [-30.5, 176.6], [-32.4, 189.4], [-24.9, 207.6], [-21.7, 216.4], [-19.5, 224.6], [-17.4, 232.8], [-15.2, 241.0], [-12.0, 249.8], [-12.9, 256.2], [-13.9, 262.6], [-10.7, 271.4], [-6.6, 278.8]];
const PATH = [[-22.4, 14.7], [-68.6, 98.9], [-114.1, 172.4], [-123.5, 236.3], [-112.2, 279.0], [-97.7, 320.8], [-84, 380]];   // cart path: out of bounds left of it
const PATH2 = [[-43.0, 255.4], [-49.7, 276.5], [-47.8, 297.0], [-37.5, 312.7], [-24.8, 324.3], [-0.0, 324.8], [26.5, 322.2]]; // the path round the back of the green
const TLINE = [[14, -30], [12.3, 26.6], [6.7, 64.9], [4.6, 97.1], [2.9, 123.9], [-4.6, 141.7], [-8.4, 167.2], [-7.7, 189.9], [-4.5, 208.4], [1.9, 226.0], [3.8, 246.5], [6.9, 265.0], [14.6, 280.5], [26.3, 298.5], [32.8, 316.1], [29.3, 336.3], [19.3, 358.3], [10, 400]]; // tree line down the right
const PRACTICE = [[-115.3, 267.5], [-110.9, 274.2], [-101.2, 274.3], [-88.2, 273.5], [-85.0, 265.6], [-88.7, 255.2], [-86.4, 244.1], [-76.7, 227.5], [-70.1, 216.0], [-69.8, 203.7], [-73.7, 195.9], [-82.6, 192.1], [-89.9, 197.6], [-95.5, 209.6], [-95.7, 222.0], [-99.7, 233.5], [-103.6, 245.1], [-110.7, 254.9], [-113.9, 262.8]];
const byV = (P, v) => { if (v <= P[0][1]) return P[0][0]; for (let i = 1; i < P.length; i++) if (v <= P[i][1]) { const a = P[i - 1], b = P[i]; return lerp(a[0], b[0], (v - a[1]) / (b[1] - a[1] || 1)); } return P[P.length - 1][0]; };
const pathU = v => byV(PATH, v), treeU = v => byV(TLINE, v), bluffU = v => treeU(v) + 2; // the edge of the bluff: the aerial's woods all grow on the slope below it
const FW_V0 = 92.9, FW_V1 = 279;
function centerU(v) {
  if (v < FW_V0) return lerp(0, (byV(FWL, FW_V0) + byV(FWR, FW_V0)) / 2, Math.max(0, v) / FW_V0);
  if (v > FW_V1) return lerp((byV(FWL, FW_V1) + byV(FWR, FW_V1)) / 2, 2, clamp((v - FW_V1) / 20, 0, 1));
  return (byV(FWL, v) + byV(FWR, v)) / 2;
}
function fwHalf(v) { if (v < FW_V0 || v > FW_V1) return 0; return Math.max(0, (byV(FWR, v) - byV(FWL, v)) / 2); }
const FW = FWL.concat(FWR.slice().reverse());
const GREEN = { c: [0.2, 296.6], rx: 7.6, ry: 19.4, rot: -0.49, s: 1.3 };
const FRINGE = { c: [0.2, 296.6], rx: 10.2, ry: 22, rot: -0.49, s: 1.3 };
const BUNKERS = [
  { deep: true, poly: [[-14.8, 302.9], [-15.8, 303.1], [-17.7, 302.1], [-18.0, 301.3], [-18.7, 300.9], [-19.0, 300.1], [-19.0, 299.1], [-18.6, 298.4], [-18.7, 297.3], [-19.7, 296.4], [-20.7, 296.4], [-21.4, 296.0], [-22.3, 293.3], [-22.8, 292.4], [-23.7, 291.9], [-25.0, 292.2], [-25.6, 293.3], [-26.5, 293.3], [-27.1, 294.4], [-26.5, 295.8], [-26.1, 296.0], [-24.9, 295.9], [-24.1, 296.4], [-24.0, 297.8], [-23.7, 298.6], [-24.7, 299.9], [-26.3, 300.7], [-27.4, 301.7], [-28.6, 301.8], [-29.8, 301.1], [-31.6, 297.8], [-32.2, 296.1], [-32.1, 294.5], [-30.5, 292.6], [-29.7, 292.3], [-28.8, 290.6], [-29.0, 289.6], [-29.8, 289.1], [-30.8, 289.4], [-31.4, 289.9], [-32.3, 289.9], [-32.8, 288.5], [-32.8, 287.4], [-30.6, 284.2], [-30.3, 282.8], [-30.7, 281.4], [-32.2, 280.3], [-34.0, 280.9], [-35.4, 280.9], [-36.0, 280.6], [-36.6, 279.7], [-36.9, 278.4], [-36.4, 277.5], [-34.6, 277.2], [-34.1, 276.4], [-34.3, 275.7], [-35.2, 275.5], [-35.7, 274.9], [-34.9, 273.4], [-34.2, 273.3], [-33.9, 272.6], [-33.0, 272.1], [-31.7, 271.7], [-29.7, 269.8], [-24.8, 269.9], [-21.7, 271.4], [-20.5, 271.6], [-19.7, 272.2], [-19.4, 273.6], [-17.7, 275.9], [-17.8, 278.9], [-19.4, 279.4], [-19.8, 280.0], [-19.7, 281.2], [-19.0, 281.5], [-18.3, 283.6], [-18.6, 284.6], [-20.4, 284.9], [-20.9, 284.6], [-21.7, 280.8], [-22.1, 280.6], [-24.3, 281.0], [-24.8, 282.4], [-24.5, 283.3], [-23.6, 284.1], [-23.9, 285.1], [-23.4, 287.1], [-22.8, 288.0], [-21.7, 288.6], [-18.9, 288.5], [-15.2, 290.7], [-14.8, 291.5], [-14.8, 292.9], [-14.0, 293.9], [-13.9, 295.6], [-12.2, 297.5], [-11.8, 298.2], [-11.6, 300.3], [-12.1, 301.1], [-12.8, 301.3], [-13.1, 301.9]] }, // the deep one left of the green, traced from the aerial
  { poly: [[-112.0, 250.0], [-113.7, 247.1], [-115.4, 246.3], [-116.3, 245.0], [-116.3, 243.6], [-115.6, 241.8], [-114.3, 240.6], [-112.9, 240.6], [-111.6, 241.1], [-109.1, 240.6], [-108.7, 240.0], [-105.6, 237.6], [-104.4, 237.8], [-104.3, 238.1], [-103.0, 238.8], [-102.9, 239.5], [-103.2, 241.5], [-102.6, 243.3], [-103.6, 245.1], [-105.1, 246.2], [-106.1, 248.4], [-107.0, 249.0], [-107.9, 249.0], [-108.4, 248.5], [-109.2, 248.5], [-109.9, 247.8], [-110.3, 247.9], [-111.3, 250.1]] }]; // the practice bunker
// traced bunkers: smoothed outline, centre and size for painting; "pad" grows or shrinks the outline about its centre
BUNKERS.forEach(b => { if (!b.poly) return; let P = b.poly; for (let k = 0; k < 1; k++) { const Q = []; P.forEach((a, i) => { const c = P[(i + 1) % P.length]; Q.push([a[0] * .75 + c[0] * .25, a[1] * .75 + c[1] * .25], [a[0] * .25 + c[0] * .75, a[1] * .25 + c[1] * .75]); }); P = Q; }
  b.sm = P; let su = 0, sv = 0; P.forEach(p => { su += p[0]; sv += p[1]; }); b.c = [su / P.length, sv / P.length]; let u0 = 1e9, u1 = -1e9, v0 = 1e9, v1 = -1e9; P.forEach(([u, v]) => { u0 = Math.min(u0, u); u1 = Math.max(u1, u); v0 = Math.min(v0, v); v1 = Math.max(v1, v); });
  b.rx = (u1 - u0) / 2; b.ry = (v1 - v0) / 2; b.rot = 0; b.s = 2; b.box = [u0, u1, v0, v1]; });
const WATER = { c: [-900, -900], rx: 1, ry: 1, rot: 0, s: 7 }; // no pond on this hole (the lake is off the bluff)
const PIN = { u: 0.6, v: 297.2 };""")

R("function inEl(u, v, e, pad = 1) {\n", "function inEl(u, v, e, pad = 1) {\n  if (e.sm) { if (u < e.box[0] - 12 || u > e.box[1] + 12 || v < e.box[2] - 12 || v > e.box[3] + 12) return false; return inPoly(e.c[0] + (u - e.c[0]) / pad, e.c[1] + (v - e.c[1]) / pad, e.sm); }\n")
R("function elPts(e, n = 72, pad = 1) {\n", "function elPts(e, n = 72, pad = 1) {\n  if (e.sm) return e.sm.map(([u, v]) => [e.c[0] + (u - e.c[0]) * pad, e.c[1] + (v - e.c[1]) * pad]);\n")
# ---------------------------------------------------------------- 2. lies: lake past the bluff, out of bounds past the path, practice green, long grass round the fairway trees
R("function lieAt(u, v) {\n  if (inEl(u, v, WATER)) return 'water';",
  """function lieAt(u, v) {
  if (u > bluffU(v)) return 'water';                 // from the lip of the bluff on it is a hazard: down the cliff to Lake Ontario
  if (u < pathU(v)) return 'ob';                     // left of the cart path: other holes""")
R("  if (Math.abs(u) <= 5 && v >= -7 && v <= 7) return 'tee';\n  if (inPoly(u, v, FW)) return 'fairway';",
  """  if (Math.abs(u) <= 5 && v >= -7 && v <= 7) return 'tee';
  if (TUFTED.some(t => Math.hypot(u - t[0], v - t[1]) < 2.6)) return 'rough';   // the long grass round the trunks of the fairway trees
  if (inPoly(u, v, PRACTICE)) return 'fringe';
  if (inPoly(u, v, FW)) return 'fairway';""")
R("sand: { name: 'Bunker', f: .7, r: .18 }, green: { name: 'Green', f: 1 }, water: { name: 'Water', f: 0 }, trees: { name: 'Trees', f: .8 }",
  "sand: { name: 'Bunker', f: .7, r: .18 }, green: { name: 'Green', f: 1 }, water: { name: 'Water', f: 0 }, trees: { name: 'Trees', f: .8 }, ob: { name: 'Out of bounds', f: .86 }")
R("const deepB = v => Math.max(fwHalf(v), 13) + 10 + 45 * (1 - _ss(62, 100, v)) + 45 * _ss(322, 358, v);\nconst isDeep = (u, v) => v > 62 && v < 358 && Math.abs(u - centerU(v)) > deepB(v);",
  "const deepB = v => Math.max(fwHalf(v), 13) + 9 + 45 * (1 - _ss(62, 96, v)) + 45 * _ss(262, 284, v);\nconst isDeep = (u, v) => v > 62 && v < 284 && Math.abs(u - centerU(v)) > deepB(v);\nconst inDeepBunker = (u, v) => BUNKERS.some(b => b.deep && inEl(u, v, b));")

# ---------------------------------------------------------------- 3. trees: the real ones by hand, the woods and the other holes filled in
RB("const TREES = (() => {\n  const R = rng(42), out = [];", "  return out;\n})();", r"""// the fairway trees whose trunks stand in the fairway, with a skirt of long grass round them (a Hunt feature)
const TUFTED = [[-46.0, 198.5], [-48.2, 210.0]]; // on the left edge of the fairway
const TREES = (() => {
  const R = rng(42), out = [], add = (u, v, r, h, o = {}) => out.push(Object.assign({ u, v, h: h * 1.15, r, pine: false, k: R() }, o));
  // by hand, from the aerial
  add(-11.5, 147.5, 7.2, 21);                                   // the big one down the right, at the front
  add(-20.0, 168.8, 4.4, 15); add(-20.5, 182.0, 4.8, 16); add(-13.4, 177.0, 4.2, 14); add(-16.5, 194.5, 4.6, 15); // the ones past it: annoying to be behind
  add(-46.0, 198.5, 4.6, 17, { tuft: true }); add(-48.2, 210.0, 5.0, 18, { tuft: true }); // trunks just inside the left edge of the fairway
  add(-61.4, 189.2, 5.2, 16); add(-59.0, 168.3, 4.0, 14); add(-64.4, 134.7, 5.4, 16);            // down the left
  add(-68.1, 210.3, 6.6, 19); add(-61.3, 239.2, 5.8, 18); add(-47.7, 244.3, 4.6, 16);            // between the hole and the practice green
  add(-104.2, 279.5, 5.4, 17); add(-118.0, 230.0, 4.0, 14);                                        // by the practice green and its bunker
  add(6.2, 268.0, 2.7, 10.5); add(9.0, 275.5, 2.4, 9.5);       // right of the approach
  add(-63.9, 301.0, 7, 19); add(-49.1, 318.5, 6.2, 18); add(14.2, 334.5, 5.4, 17); // the few left of and behind the green
  const ok = (u, v, gap) => !out.some(t => Math.hypot(t.u - u, t.v - v) < gap);
  // the woods along the right, from the tree line out toward the bluff
  for (let i = 0; i < 2500; i++) { const v = -35 + R() * 425, u = bluffU(v) + 3 + R() * 12.5; // trees growing down the face of the bluff: their tops sit below the edge
    if (ok(u, v, 6.2)) add(u, v, 3.2 + R() * 2.2, 13 + R() * 8, { pine: R() < .15, face: true }); }
  // the other holes left of the cart path, and the trees round the clubhouse
  [[-146.0, 251.1, 6], [-132.1, 243.9, 5], [-123.5, 150.3, 5.6], [-101.0, 135.6, 5], [-75.2, 100.7, 5.4], [-140, 300, 6], [-128, 330, 5.4], [-150, 190, 5.6]].forEach(([u, v, r]) => add(u, v, r, 15 + r)); // a few over on the other holes
  // behind the green, beyond the back path
  return out;
})();""")

# ---------------------------------------------------------------- 4. terrain: gentle rolls, the bluff dropping to the lake, the deep bunker dug in; the green's real slopes
R("const MAP = { U0: -140, U1: 140, V0: -40, V1: 450, W: 1536 };", "const MAP = { U0: -150, U1: 90, V0: -40, V1: 390, W: 1536 };")
RB("function terrainH(u, v) {", "  return edge * (TERRAIN_BASE + local * raw * TERRAIN_AMP);\n}", r"""const BLUFF_D = -66; // yards below the course
function bunkerD(u, v, e) { if (e.sm) { if (u < e.box[0] - 6 || u > e.box[1] + 6 || v < e.box[2] - 6 || v > e.box[3] + 6) return 9; let d2 = 1e9; const P = e.sm; for (let i = 0, j = P.length - 1; i < P.length; j = i++) { const ax = P[j][0], ay = P[j][1], bx = P[i][0] - ax, by = P[i][1] - ay, t = clamp(((u - ax) * bx + (v - ay) * by) / (bx * bx + by * by || 1), 0, 1), dx = u - ax - bx * t, dy = v - ay - by * t; d2 = Math.min(d2, dx * dx + dy * dy); }
  const d = Math.sqrt(d2) / 6; return inPoly(u, v, P) ? 1 - d : 1 + d; } /* traced shape: 1 at the edge, 0.83 two yards in, 1.17 one yard out */ const du = u - e.c[0], dv = v - e.c[1], cs = Math.cos(-e.rot), sn = Math.sin(-e.rot); const x = (du * cs - dv * sn) / e.rx, y = (du * sn + dv * cs) / e.ry; return Math.hypot(x, y) / shR(Math.atan2(y, x), e); }
/* the bank behind and right of the green sits above it (~6 ft), so a miss long-right leaves a downhill chip */
function greenBank(u, v) { const du = u - FRINGE.c[0], dv = v - FRINGE.c[1]; if (Math.abs(du) > 70 || Math.abs(dv) > 90) return 0; const fd = fringeD(u, v); if (fd < 1.02 || fd > 4.4) return 0;
  const cs = Math.cos(-FRINGE.rot), sn = Math.sin(-FRINGE.rot), b = (du * cs - dv * sn) / FRINGE.rx, a = (du * sn + dv * cs) / FRINGE.ry, dir = (b * .8 + a * .6) / (Math.hypot(b, a) || 1);
  return 3 * smooth(-.15, .55, dir) * smooth(1.0, 1.4, fd) * (1 - smooth(2.8, 4.2, fd)); }
function terrainH(u, v) {
  const raw = 1.5 * Math.sin(u * .045 + v * .012) + 1.15 * Math.sin(v * .031 + 1.3) * Math.cos(u * .052) + .55 * Math.sin(u * .12 - v * .075 + 2) + .35 * Math.sin(v * .11 + u * .03);
  const local = smooth(8, 24, Math.hypot(u, v)) * smooth(1.05, 1.9, fringeD(u, v)) * .8;
  const edge = (1 - smooth(-148, -128, -u) * 0 - smooth(128, 148, -u)) * smooth(-38, -18, v) * (1 - smooth(368, 388, v));
  let h = edge * (TERRAIN_BASE + local * raw * TERRAIN_AMP) + greenBank(u, v);
  const bu = bluffU(v); if (u > bu) { const t = clamp((u - bu) / 16, 0, 1), k = 1 - (1 - t) * (1 - t) * (1 - .35 * t); h = h * (1 - k) + BLUFF_D * k; if (u > bu + 22) h = BLUFF_D - 3 * smooth(bu + 22, bu + 26, u); } // the bluff: a sheer drop of ~200 ft to a strip of beach, then the lake
  for (const b of BUNKERS) if (b.deep) { const d = bunkerD(u, v, b); if (d < 1.6) h += (-.9 * (1 - smooth(.7, 1.0, d)) + .45 * Math.exp(-(((d - 1.14) / .13) ** 2))) * smooth(1.0, 1.25, fringeD(u, v)); } /* never digs into the green */ // dug in, with a raised lip
  return h;
}""")
RB("function greenH(u, v) {", "+ .03 * Math.cos((v - 380) * .25 - (u + 30) * .08));\n}", r"""// the green: about a third of the way on it tips downhill toward the back right, so balls in the middle run back-right;
// the back is flatter and breaks less to the right, least of all on the back-left
function greenH(u, v) {
  if (Math.abs(u - FRINGE.c[0]) > 34 || Math.abs(v - FRINGE.c[1]) > 34) return 0;
  const d = fringeD(u, v); if (d > 1.45) return 0;
  const m = 1 - smooth(.92, 1.45, d), du = u - GREEN.c[0], dv = v - GREEN.c[1], cs = Math.cos(-GREEN.rot), sn = Math.sin(-GREEN.rot);
  const b = (du * cs - dv * sn) / GREEN.rx, a = (du * sn + dv * cs) / GREEN.ry;   // a: front (-1) to back (+1) · b: left (-1) to right (+1)
  const back = smooth(.2, .85, a), front = 1 - smooth(-.6, .3, a), left = smooth(.35, -.75, b);
  const tilt = .1 + .07 * front * left - back * (.04 + .04 * left); // breaks right everywhere, most on the front-left, least on the back-left; never severe
  const crown = .06 * (1 - Math.min(1, d / .95) ** 2);
  const toSand = d > .74 ? .4 * smooth(.76, 1.08, d) * (1 - smooth(1.9, 3.0, bunkerD(u, v, BUNKERS[0]))) : 0; /* the fringe beside the deep bunker (front-left) falls away into it */
  return m * Math.max(0, 1.05 + crown - toSand + .06 * (1 - smooth(-1, -.45, a)) - .3 * smooth(-.4, .55, a) - tilt * b * (1 + .12 * Math.sin(a * 2.1)) + .025 * Math.sin(a * 4.3 + b * 2.2));
}""")
R("function fringeD(u, v) { const e = FRINGE,", "function fringeD(u, v) { const e = FRINGE,")
# green-reading grid bounds follow the green
R("  const U0 = -68, U1 = 12, V0 = 346, V1 = 430, step = 1.5,", "  const U0 = FRINGE.c[0] - 34, U1 = FRINGE.c[0] + 34, V0 = FRINGE.c[1] - 34, V1 = FRINGE.c[1] + 34, step = 1.5,")

R("    const bp = elPts(b, 180); path(elPts(b, 180, 1.3)); g.fillStyle = real ? '#5f9a3e' : 'rgba(46,96,34,.35)'; g.fill(); path(elPts(b, 180, 1.14)); g.fillStyle = real ? '#5f9a3e' : '#8fcf55'; g.fill();",
  "    const bp = elPts(b, 180); if (b.sm) { g.save(); g.lineJoin = 'round'; path(bp); g.lineWidth = 5.4 * ppy; g.strokeStyle = real ? '#5f9a3e' : 'rgba(46,96,34,.35)'; g.stroke(); path(bp); g.lineWidth = 2.6 * ppy; g.strokeStyle = real ? '#5f9a3e' : '#8fcf55'; g.stroke(); g.restore(); } else { path(elPts(b, 180, 1.3)); g.fillStyle = real ? '#5f9a3e' : 'rgba(46,96,34,.35)'; g.fill(); path(elPts(b, 180, 1.14)); g.fillStyle = real ? '#5f9a3e' : '#8fcf55'; g.fill(); }")
# ---------------------------------------------------------------- 5. painting: stripes, deep rough, the paths, the practice green, the bluff edge
R("for (let v = 60; v <= 360; v += 2) pts.push([centerU(v) + sd * (deepB(v) + inset), v]); pts.push([sd < 0 ? MAP.U0 : MAP.U1, 360]);", "for (let v = 60; v <= 290; v += 2) pts.push([centerU(v) + sd * (deepB(v) + inset), v]); pts.push([sd < 0 ? MAP.U0 : MAP.U1, 290]);")
R("for (let v = 60; v <= 360; v += 2) pts.push([centerU(v) + sd * (deepB(v) + 1.6), v]); pts.push([sd < 0 ? MAP.U0 : MAP.U1, 360]);", "for (let v = 60; v <= 290; v += 2) pts.push([centerU(v) + sd * (deepB(v) + 1.6), v]); pts.push([sd < 0 ? MAP.U0 : MAP.U1, 290]);")
R("y = Y(60 + R() * 300), a = -1.15", "y = Y(60 + R() * 230), a = -1.15")
# the deep rough only between the cart path and the bluff (no hard bands across the out-of-bounds or the lake)
R("  { const band = (inset, col) => {", "  { g.save(); { const pts = []; for (let v = -40; v <= 390; v += 4) pts.push([pathU(v), v]); for (let v = 390; v >= -40; v -= 4) pts.push([bluffU(v), v]); path(pts); g.clip(); }\n  { const band = (inset, col) => {")
R("g.lineWidth = 1.3; g.stroke(); g.restore(); } }", "g.lineWidth = 1.3; g.stroke(); g.restore(); } } g.restore(); }")
R("for (let v = 80, k = 0; v < 372; v += 7, k++)", "for (let v = 86, k = 0; v < 290; v += 7, k++)")
R("g.fillRect(R() * MAP.W, Y(90 + R() * 275), 1, 1); }", "g.fillRect(R() * MAP.W, Y(90 + R() * 195), 1, 1); }")
R("const x = R() * MAP.W, y = Y(90 + R() * 275), a = -1.05,", "const x = R() * MAP.W, y = Y(90 + R() * 195), a = -1.05,")
R("  // tee\n  const tee = [[-5, -7], [5, -7], [5, 7], [-5, 7]];", r"""  // the practice green (and the cart paths: out of bounds left of the main one)
  { path(PRACTICE); g.fillStyle = real ? '#6fae4a' : '#8fd255'; g.fill(); const pg = PRACTICE.map(([u, v]) => { const cx = -92, cy = 235; return [cx + (u - cx) * .9, cy + (v - cy) * .92]; });
    path(pg); g.fillStyle = real ? '#7dbd55' : '#a9ea6d'; g.fill(); sketch(PRACTICE, 2.2, .7); }
  const road = (P, w) => { g.save(); g.lineJoin = g.lineCap = 'round'; path(P, false); g.lineWidth = (w + .9) * ppy; g.strokeStyle = real ? 'rgba(60,60,55,.6)' : 'rgba(29,42,26,.85)'; g.stroke();
    path(P, false); g.lineWidth = w * ppy; g.strokeStyle = real ? '#a9a59a' : '#d9d3c4'; g.stroke(); path(P, false); g.lineWidth = w * .25 * ppy; g.strokeStyle = 'rgba(255,255,255,.35)'; g.setLineDash([3 * ppy, 4 * ppy]); g.stroke(); g.restore(); };
  road(PATH, 2.4); road(PATH2, 2.2);
  // the bluff: the grass breaks over the edge, then a scrubby face with clay showing through, down to a strip of beach
  { const band = (a, b) => { const A = [], B = []; for (let v = -40; v <= 390; v += 2) { A.push([bluffU(v) + a, v]); B.push([bluffU(v) + b, v]); } return A.concat(B.reverse()); };
    path(band(.4, 16.5)); g.fillStyle = real ? '#5d7a3e' : '#6f9f47'; g.fill();
    path(band(.4, 16.5)); g.save(); g.clip();
    for (let i = 0; i < 70; i++) { const v = -40 + R() * 430, u0 = bluffU(v) + 3 + R() * 6, len = 5 + R() * 7; g.beginPath(); g.moveTo(X(u0), Y(v)); g.quadraticCurveTo(X(u0 + len * .5), Y(v + (R() - .5) * 4), X(u0 + len), Y(v + (R() - .5) * 6)); g.lineWidth = (1.2 + R() * 1.6) * ppy; g.lineCap = 'round'; g.strokeStyle = 'rgba(176,132,84,.55)'; g.stroke(); } // clay gullies
    const clump = (u, v, r, c) => { const k = [[0, 0, 1], [.55, .25, .72], [-.5, .3, .68], [.1, -.5, .6]]; g.beginPath(); k.forEach(([a, b, s]) => { g.moveTo(X(u + a * r) + r * s * ppy, Y(v + b * r)); g.arc(X(u + a * r), Y(v + b * r), r * s * ppy, 0, 7); });
      g.fillStyle = 'rgba(29,42,26,.85)'; g.save(); g.translate(.9, 1.1); g.fill(); g.restore(); g.fillStyle = c; g.fill(); g.beginPath(); g.arc(X(u - r * .25), Y(v + r * .3), r * .38 * ppy, 0, 7); g.fillStyle = 'rgba(255,255,255,.14)'; g.fill(); };
    const cs = ['#4f8f36', '#5c9c3c', '#467f31', '#6aa846'];
    for (let i = 0; i < 520; i++) { const v = -40 + R() * 430, d = Math.pow(R(), 1.3) * 14, u = bluffU(v) + 1.2 + d; clump(u, v, (1 - d / 24) * (.8 + R() * 1.0), cs[(R() * cs.length) | 0]); } // scrub, thickest just under the edge
    g.restore();
    path(band(16, 23)); g.fillStyle = '#e4dccb'; g.fill(); path(band(21, 23)); g.fillStyle = 'rgba(79,159,208,.75)'; g.fill(); // the beach and the wet edge of the lake
    if (!real) for (let pass = 0; pass < 2; pass++) { g.beginPath(); for (let v = -40; v <= 390; v += 2) { const x = X(bluffU(v) + .4) + (R() - .5) * (pass ? 1.6 : .5), y = Y(v); v === -40 ? g.moveTo(x, y) : g.lineTo(x, y); } g.lineWidth = pass ? 1.4 : 2.6; g.strokeStyle = `rgba(29,42,26,${pass ? .38 : .85})`; g.lineJoin = 'round'; g.stroke(); } } // the edge of the bluff (an open line: no closing stroke across the map)
  // tee
  const tee = [[-5, -7], [5, -7], [5, 7], [-5, 7]];""")

# ---------------------------------------------------------------- 6. scenery: the lake off the bluff, hills on land only, tufts, clubhouse, practice flags, OB stakes
RB("/* ---- Lake Ontario past the bluff behind the green ---- */", "shore.userData.ink = false; scene.add(shore); })();", r"""/* ---- Lake Ontario off the bluff down the right ---- */
(() => { const lake = new THREE.Mesh(new THREE.PlaneGeometry(4000, 5200), new THREE.MeshBasicMaterial({ color: 0x5aa8d8, fog: false }));
  lake.rotation.x = -Math.PI / 2; lake.position.set(0 + 2000, BLUFF_D - .7, -200); lake.userData.ink = false; lake.renderOrder = -2; scene.add(lake); /* drawn first so the ground under it fails the depth test */
  const pts = []; for (let v = -60; v <= 420; v += 6) pts.push(new THREE.Vector3(bluffU(v) + 21.6, BLUFF_D - .55, -v)); // a pale line of beach at the foot of the bluff
  const g = new THREE.BufferGeometry().setFromPoints(pts); const beach = new THREE.Line(g, new THREE.LineBasicMaterial({ color: 0xece0c2, fog: true })); beach.userData.ink = false; scene.add(beach); })();""")
R("if (-200 + Math.sin(a) * d - r < -470) continue; hills.push(", "if (Math.cos(a) * d - r < 60 && false) continue; if (Math.cos(a) * d > 40) continue; hills.push(")
R("  [[-10, 432, 16], [-46, 425, 13], [-62, 380, 10]].forEach(([u, v, r]) => hills.push({ p: W(u, v, groundHeight(u, v) - .3), s: new THREE.Vector3(r, r * .28, r), c: '#5aa743', ink: false }));\n", "")
R("    const v = -20 + Rt() * 440, cu = centerU(clamp(v, 0, 430)), side = Rt() < .5 ? -1 : 1;", "    const v = -20 + Rt() * 330, cu = centerU(clamp(v, 0, 300)), side = Rt() < .5 ? -1 : 1;")
R("    const l = lieAt(u, v); if (l !== 'rough' && l !== 'deep') continue; list.push([u, v]);\n  }",
  "    const l = lieAt(u, v); if (l !== 'rough' && l !== 'deep') continue; list.push([u, v]);\n  }\n  for (const [tu, tv] of TUFTED) for (let k = 0; k < 26; k++) { const a = Rt() * 6.28, r = .7 + Rt() * 1.8; list.push([tu + Math.cos(a) * r, tv + Math.sin(a) * r]); } // the skirts of long grass round the fairway trees")
R("const v = 30 + Rc() * 420, u = centerU(clamp(v, 0, 430)) + (Rc() < .5 ? -1 : 1) * (45 + Rc() * 85), w = 30 + Rc() * 38;", "const v = 30 + Rc() * 330, u = centerU(clamp(v, 0, 300)) + (Rc() < .5 ? -1 : 1) * (45 + Rc() * 85), w = 30 + Rc() * 38;")
R("  // tee markers\n", r"""  // little flags on the practice green
  [[-80, 205], [-91, 236], [-104, 262]].forEach(([u, v], i) => { const y = groundHeight(u, v), pole = new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, 1.9, 6), toon(0xfffaf0)); pole.position.copy(W(u, v, y + .95)); scene.add(pole);
    const fl = new THREE.Mesh(new THREE.PlaneGeometry(.75, .45), new THREE.MeshBasicMaterial({ color: [0xff4f9a, 0xffd23f, 0x5fe0b5][i], side: THREE.DoubleSide })); fl.position.copy(W(u + .38, v, y + 1.65)); scene.add(fl); });
  // white out-of-bounds stakes along the cart path
  { const sg = new THREE.CylinderGeometry(.09, .09, 1.1, 6), sm = toon(0xffffff), list = []; for (let v = 20; v <= 330; v += 14) list.push([pathU(v) - 1.6, v]);
    const im = new THREE.InstancedMesh(sg, sm, list.length), M = new THREE.Matrix4(); list.forEach(([u, v], i) => im.setMatrixAt(i, M.makeTranslation(u, groundHeight(u, v) + .55, -v))); scene.add(im); }
  // tee markers
""")
R("  const flocks = [{ cu: 0, cv: 210, ru: 175, rv: 270, w: .045, ph: 0, h: 34 }, { cu: -20, cv: 160, ru: 130, rv: 200, w: -.06, ph: 2.6, h: 26 }];",
  "  const flocks = [{ cu: -20, cv: 170, ru: 120, rv: 190, w: .045, ph: 0, h: 34 }, { cu: -35, cv: 140, ru: 90, rv: 150, w: -.06, ph: 2.6, h: 26 }];")

R("const outer = new THREE.Mesh(new THREE.PlaneGeometry(3400, 3400), groundMat(t, 3400 / 36)); outer.rotation.x = -Math.PI / 2; outer.position.set(0, -0.8, -200);",
  "const osh = new THREE.Shape(); osh.moveTo(-1900, -1900); osh.lineTo(bluffU(-40) + .5, -1900); for (let v = -40; v <= 390; v += 5) osh.lineTo(bluffU(v) + .5, v); osh.lineTo(bluffU(390) + .5, 1600); osh.lineTo(-1900, 1600); osh.closePath(); /* the land: ends at the edge of the bluff */\n  const outer = new THREE.Mesh(new THREE.ShapeGeometry(osh), groundMat(t, 1 / 36)); outer.rotation.x = -Math.PI / 2; outer.position.set(0, -0.8, 0);")
# ---------------------------------------------------------------- 7. play: aiming down this hole, the deep bunker, out of bounds
R("for (let v = Math.max(b.v, 0); v <= 430; v += .25) { const u = centerU(v);", "for (let v = Math.max(b.v, 0); v <= PIN.v + 10; v += .25) { const u = centerU(v);")
R("  if (G.mode === 'sand' && G.lieRoll < 1) carry /= G.lieRoll; // explosion shot: the sand is already priced in",
  "  if (G.mode === 'sand' && G.lieRoll < 1) carry /= G.lieRoll; // explosion shot: the sand is already priced in\n  if (G.lie === 'sand' && inDeepBunker(G.ball.u, G.ball.v)) carry *= .8; // the deep bunker left of the green: a tall face eats some of it")
R("  const S = G.shot; const water = S.endLie === 'water' || S.lieLand === 'water';",
  "  const S = G.shot; const ob = S.endLie === 'ob' && S.lieLand !== 'water', water = S.endLie === 'water' || S.lieLand === 'water' || ob; // out of bounds plays like water, but only stroke and distance")
R("water ? 'SPLASH!' : S.putt ?", "water ? (ob ? 'OUT OF BOUNDS' : 'SPLASH!') : S.putt ?")
R("lie: water ? 'water' : S.lieLand === 'trees' ? 'trees' : lie,", "lie: ob ? 'ob' : water ? 'water' : S.lieLand === 'trees' ? 'trees' : lie,")
R("  if (water) { btns.push(['Replay +1', 'penalty', false]); btns.push(['Take a drop +1', 'drop', true]); }",
  "  if (ob) btns.push(['Replay +1', 'penalty', true]);\n  else if (water) { btns.push(['Replay +1', 'penalty', false]); btns.push(['Take a drop +1', 'drop', true]); }")
R("water: 'Water', trees: 'Trees', tee: 'Tee' };", "water: 'Water', trees: 'Trees', tee: 'Tee', ob: 'Out of bounds' };")
# home fly-over down this hole
R("  const cu = v => centerU(clamp(v, 0, 430)), P = [[14, -48, 24], [cu(55) + 30, 55, 38], [cu(160) + 40, 160, 52], [cu(262) - 34, 262, 52], [PIN.u + 44, PIN.v - 62, 38], [PIN.u + 34, PIN.v + 22, 30], [PIN.u - 22, PIN.v + 46, 32]],\n    L = [[cu(150), 150, 26], [cu(230), 230, 30], [cu(320), 320, 26], [PIN.u + 4, PIN.v - 10, 12], [PIN.u, PIN.v, 7], [PIN.u, PIN.v, 7], [PIN.u - 2, PIN.v - 6, 8]];",
  "  const cu = v => centerU(clamp(v, 0, 300)), P = [[-6, -46, 24], [cu(45) - 28, 45, 36], [cu(130) - 40, 130, 48], [cu(205) - 40, 205, 50], [PIN.u - 40, PIN.v - 52, 36], [PIN.u - 34, PIN.v + 18, 28], [PIN.u + 18, PIN.v + 40, 30]],\n    L = [[cu(130), 130, 20], [cu(200), 200, 24], [cu(260), 260, 20], [PIN.u - 2, PIN.v - 10, 10], [PIN.u, PIN.v, 6], [PIN.u, PIN.v, 6], [PIN.u + 2, PIN.v - 6, 7]];")

open('/home/claude/golf/hole1/h1.html', 'w').write(s)
print('h1 built', len(s))
