# Wrap a sketchy-golf.html for headless testing + instrumentation (test-only; never shipped).
#  - virtual 60 Hz clock (window.__VT=true): every rendered frame advances game time by exactly 1/60 s
#  - per-frame log: real JS ms, view, aimT, camera pos/look/fov, program count, draw calls
#  - timers around named functions (max/total/count), and a deterministic canvas grab (__grabAt)
import sys, re
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()

def once(old, new):
    global s
    n = s.count(old)
    assert n == 1, (old, n)
    s = s.replace(old, new)

# virtual clock rAF
s = s.replace("requestAnimationFrame(frame);", "__RAF(frame);")
# deterministic READ streaks (own seeded RNG, re-seeded + respawned at __reseedAt) so screenshots compare pixel-exactly
once("const spawn = q => { for (let k = 0; k < 20; k++) { const u = U0 + Math.random() * (U1 - U0), v = V0 + Math.random() * (V1 - V0);", "const spawn = q => { for (let k = 0; k < 20; k++) { const u = U0 + __rr() * (U1 - U0), v = V0 + __rr() * (V1 - V0);")
once("q.life = 0; q.max = 1.2 + Math.random() * 1.4; };", "q.life = 0; q.max = 1.2 + __rr() * 1.4; }; window.__READrespawn = () => P.forEach(q => { spawn(q); q.life = __rr() * q.max; });")
once("P.forEach(q => { spawn(q); q.life = Math.random() * q.max; });", "P.forEach(q => { spawn(q); q.life = __rr() * q.max; });")
once("/* ================= GREEN READING", "function __mkRng(sd) { return () => { sd |= 0; sd = sd + 0x6D2B79F5 | 0; let t = Math.imul(sd ^ sd >>> 15, 1 | sd); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }\nlet __rr = __mkRng(777);\n/* ================= GREEN READING")
once("function frame(now) {", r"""function __RAF(f) { requestAnimationFrame(ts => { window.__realNow = ts; if (window.__pause) { __RAF(f); return; } if (window.__VT) { if (window.__reseedAt === (window.__fn || 0) + 1) window.__vtNow = 1e7; window.__vtNow = (window.__vtNow || 1e6) + 1000 / 60; f(window.__vtNow); } else f(ts); }); }
function frame(now) { const __t0 = performance.now(); if (!window.__t1) window.__t1 = __t0; const __p0 = renderer.info.programs.length; window.__fn = (window.__fn || 0) + 1;
  if (window.__reseedAt === window.__fn) { __rr = __mkRng(777); window.__READrespawn(); let sd = 12345; Math.random = () => { sd |= 0; sd = sd + 0x6D2B79F5 | 0; let t = Math.imul(sd ^ sd >>> 15, 1 | sd); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  try { return frame_(now); } finally {
    const ms = performance.now() - __t0, P = renderer.info.programs.length;
    if (window.__logOn) (window.__log = window.__log || []).push([+(now).toFixed(2), +ms.toFixed(3), G.view, +G.aimT.toFixed(4), +camera.position.x.toFixed(4), +camera.position.y.toFixed(4), +camera.position.z.toFixed(4), +camLook.x.toFixed(4), +camLook.y.toFixed(4), +camLook.z.toFixed(4), +camera.fov.toFixed(3), P, renderer.info.render.calls, renderer.info.render.triangles, +(window.__realNow||0).toFixed(1), G.preview ? 1 : 0, G.camTween ? 1 : 0, SW.phase]);
    if (P !== __p0) (window.__newProg = window.__newProg || []).push({ fn: window.__fn, view: G.view, mode: G.mode, n: P - __p0, ms: +ms.toFixed(1) });
    window.__R = renderer; window.__S = scene; window.__C = camera; } }
function frame_(now) {""")

# grab the WebGL canvas right after drawing (same task, so the drawing buffer is still valid)
once("  updateOverlays(); drawTrTop();\n", "  if (window.__grabAt === window.__fn) { window.__grabbed = canvas.toDataURL('image/png'); window.__grabAt = -1; }\n  updateOverlays(); drawTrTop();\n")

# measurement-only hooks
once("renderer.clear(); renderer.render(scene, camera); renderer.render(grain.sc, grain.cam); }", "renderer.clear(); renderer.render(scene, camera); if (!window.__noGrain) renderer.render(grain.sc, grain.cam); }")
s = s.replace("window.__G = G;", "window.__THREE = THREE; window.__grain = grain; window.__G = G;", 1)

# timers
names = sys.argv[3].split(',') if len(sys.argv) > 3 else []
for nm in names:
    pat = re.compile(r"^(\s*)function " + re.escape(nm) + r"\(([^)]*)\) \{", re.M)
    m = list(pat.finditer(s))
    assert len(m) == 1, (nm, len(m))
    m = m[0]
    ind, args = m.group(1), m.group(2)
    rep = f"{ind}function {nm}(...__a) {{ const __t = performance.now(); try {{ return {nm}__i.apply(this, __a); }} finally {{ const d = performance.now() - __t, T = (window.__T = window.__T || {{}}), r = (T['{nm}'] = T['{nm}'] || [0, 0, 0, []]); r[0]++; r[1] += d; if (d > r[2]) r[2] = d; if (d > 4) r[3].push([window.__fn, +d.toFixed(1)]); }} }}\n{ind}function {nm}__i({args}) {{"
    s = s[:m.start()] + rep + s[m.end():]

open(dst, 'w').write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>' + s + '</body></html>')
