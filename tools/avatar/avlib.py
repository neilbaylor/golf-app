"""Shared helpers for the crew avatars (Hunter, Sean). Derived from Neil's gen3.py:
geometry is traced in the avatar's 100-unit frame over a warped reference photo (cwarp.py),
a baked skin/hair(/cap) texture WebP sits under vector ink lines, and the game's AV module
drives #avEyeL/#avEyeR/#avBrows/#avMouth/#avSweat/#avHead exactly as for Neil."""
import math, random, json, subprocess, base64, io, os, sys, re
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import cwarp

W = '/home/claude/golf/avatar/crew/work/'
T = W + 'tmp/'
CREW = '/home/claude/golf/avatar/crew/'
INK = '#1d2a1a'
os.makedirs(T, exist_ok=True)

# ------------------------------------------------------------------ path helpers
def cr(pts, closed=False, t=1.0):
    """Catmull-Rom through pts -> (svg path d, dense polyline)"""
    P = [np.array(p, float) for p in pts]; n = len(P)
    segs = range(n if closed else n - 1)
    get = (lambda i: P[i % n]) if closed else (lambda i: P[min(max(i, 0), n - 1)])
    d = f'M{P[0][0]:.1f} {P[0][1]:.1f}'; poly = []
    for i in segs:
        p0, p1, p2, p3 = get(i - 1), get(i), get(i + 1), get(i + 2)
        c1 = p1 + (p2 - p0) / 6 * t; c2 = p2 - (p3 - p1) / 6 * t
        d += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
        for s in np.linspace(0, 1, 24, endpoint=False):
            poly.append(((1 - s) ** 3) * p1 + 3 * s * (1 - s) ** 2 * c1 + 3 * s * s * (1 - s) * c2 + s ** 3 * p2)
    if closed: d += 'Z'
    else: poly.append(P[-1])
    return d, np.array(poly)

def mirror(pts): return [(round(100 - x, 2), y) for x, y in pts]
def rev(pts): return list(pts)[::-1]
def mirror_d(d):
    """mirror an absolute/relative path left<->right (x -> 100-x for absolute, dx -> -dx relative)"""
    return ptrans(d, lambda x, y: (100 - x, y), lambda dx, dy: (-dx, dy), arcflip=True)

_tok = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e-?\d+)?')
_NARGS = dict(M=2, L=2, H=1, V=1, C=6, S=4, Q=4, T=2, A=7, Z=0)
def ptrans(d, fa, fr=None, arcflip=False, nd=2):
    """transform path data: fa(x,y) for absolute points, fr(dx,dy) for relative ones (default: linear part of fa)."""
    if fr is None:
        ox, oy = fa(0, 0); fr = lambda dx, dy: (fa(dx, dy)[0] - ox, fa(dx, dy)[1] - oy)
    toks = _tok.findall(d); out = []; i = 0; cmd = None
    fmt = lambda v: (f'{v:.{nd}f}').rstrip('0').rstrip('.') if abs(v) >= 1e-9 else '0'
    while i < len(toks):
        t = toks[i]
        if re.match(r'[A-Za-z]', t): cmd = t; out.append(t); i += 1
        if cmd in 'Zz': continue
        n = _NARGS[cmd.upper()]; a = [float(v) for v in toks[i:i + n]]; i += n
        rel = cmd.islower(); f = fr if rel else fa
        if cmd.upper() == 'A':
            ox, oy = fr(1, 0); oy2 = fr(0, 1)
            sx = math.hypot(*fr(1, 0)); sy = math.hypot(*fr(0, 1))
            x, y = f(a[5], a[6]); sweep = int(a[4])
            if arcflip: sweep = 1 - sweep
            out += [fmt(a[0] * sx), fmt(a[1] * sy), fmt(a[2]), str(int(a[3])), str(sweep), fmt(x), fmt(y)]
        elif cmd.upper() == 'H':
            out.append(fmt(f(a[0], 0)[0]))
        elif cmd.upper() == 'V':
            out.append(fmt(f(0, a[0])[1]))
        else:
            for k in range(0, n, 2):
                x, y = f(a[k], a[k + 1]); out += [fmt(x), fmt(y)]
    s = ' '.join(out)
    return re.sub(r' ?([A-Za-z]) ', r' \1', s).strip()

# ------------------------------------------------------------------ raster helpers
PPU = 8
def mask(polys, ppu=PPU, blur=0):
    im = Image.new('L', (100 * ppu, 100 * ppu), 0); d = ImageDraw.Draw(im)
    for p in polys: d.polygon([(x * ppu, y * ppu) for x, y in p], fill=255)
    m = np.asarray(im).astype(np.float32) / 255
    if blur: m = cv2.GaussianBlur(m, (0, 0), blur * ppu)
    return m
def ell(cx, cy, rx, ry, n=40): return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
def sstep(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def inside(poly, x, y):
    return cv2.pointPolygonTest(np.asarray(poly, np.float32).reshape(-1, 1, 2), (float(x), float(y)), False) > 0
def du(f, mime='image/png'):
    return f'data:{mime};base64,' + base64.b64encode(open(f, 'rb').read()).decode()
def rgb(c): return 'rgb(%d,%d,%d)' % tuple(c)

def photo_skin(name, cx, face_poly, ear_polys, feat, keep, SKIN, FLUSH, out_png, lowk=.7, detk=.5, flushk=.5,
               region=((34, 42), (66, 42), (64, 76), (36, 76)), flush_excl=None):
    """toon skin: flat SKIN modulated by the warped photo's low-frequency light/shade, a band-passed
    fine texture and its natural redness (Lab a*). Features drawn as vectors are inpainted first."""
    ref, L = cwarp.warp(name, PPU=PPU, CX=cx)
    ref = ref.astype(np.uint8)
    fm_ = mask([ell(*e) for e in feat])
    ref = cv2.inpaint(ref, (fm_ > .3).astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA)
    cv2.imwrite(T + 'ref_' + os.path.basename(out_png), ref)
    lab = cv2.cvtColor(ref, cv2.COLOR_BGR2LAB).astype(np.float32)
    L0 = lab[:, :, 0]
    fm = mask([face_poly]); em = mask(ear_polys)
    reg = mask([list(region)]) > .5
    med = np.median(L0[reg])
    kp = np.minimum(1 - mask([ell(*e) for e in keep], blur=1.4), 1)
    low = cv2.GaussianBlur(L0, (0, 0), 1.6 * PPU) / med - 1
    mod = np.clip(low, -.12, .07) * kp * lowk
    det = (cv2.GaussianBlur(L0, (0, 0), .12 * PPU) - cv2.GaussianBlur(L0, (0, 0), .7 * PPU)) / med
    det = np.clip(det, -.12, .12) * detk * kp
    col = np.zeros(L0.shape + (3,), np.float32) + SKIN
    col = np.clip(col * (1 + mod + det)[..., None], 0, 255)
    a = cv2.GaussianBlur(lab[:, :, 1], (0, 0), 1.6 * PPU)
    amed = np.median(a[reg]); fl = sstep(0, 10, a - amed)
    if flush_excl: fl = fl * (1 - mask([ell(*e) for e in flush_excl], blur=1))
    col = col * (1 - fl[..., None] * flushk) + np.array(FLUSH, np.float32) * fl[..., None] * flushk
    alpha = np.maximum(fm, em)
    Image.fromarray(np.dstack([col, alpha * 255]).astype(np.uint8), 'RGBA').save(out_png)
    return ref, L

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    return r.stdout

def render(svg_path, png, w, h, transparent=False):
    run(['node', W + 'gen/render.js', svg_path, png, str(w), str(h)] + (['1'] if transparent else []))

def bake(svg_text, tag, box, tppu=4, q=80, sup=3, alpha_q=50):
    BX, BY, BW, BH = box
    open(T + f'bake_{tag}.svg', 'w').write(svg_text)
    render(T + f'bake_{tag}.svg', T + f'bake_{tag}_big.png', BW * tppu * sup, BH * tppu * sup, True)
    im = Image.open(T + f'bake_{tag}_big.png').convert('RGBA').resize((BW * tppu, BH * tppu), Image.LANCZOS)
    im.save(T + f'bake_{tag}.png')
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=q, method=6, alpha_quality=alpha_q)
    return buf.getvalue()

def lens(rnd, flow, x, y, ln, w, jitter=.2, bend=.35):
    ux, uy = flow(x, y); a = math.atan2(uy, ux) + rnd.gauss(0, jitter)
    ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    x2, y2 = x + ux * ln, y + uy * ln
    b = rnd.gauss(0, bend)
    mx, my = (x + x2) / 2 + nx * b, (y + y2) / 2 + ny * b
    return (f'M{x:.2f} {y:.2f} Q{mx + nx * w:.2f} {my + ny * w:.2f} {x2:.2f} {y2:.2f} '
            f'Q{mx - nx * w:.2f} {my - ny * w:.2f} {x:.2f} {y:.2f}Z')

def strands(rnd, poly, flow, layers, fine, bbox, accept=None):
    """layers: [(colour, opacity, n, (len range), (width range), bias)], fine: [(colour, opacity, width, n)]"""
    out = []
    x0, y0, x1, y1 = bbox
    def pick():
        while True:
            x = rnd.uniform(x0, x1); y = rnd.uniform(y0, y1)
            if inside(poly, x, y): return x, y
    for col, op, n, lr, wr, bias in layers:
        k = 0; paths = []
        while k < n:
            x, y = pick()
            if accept and not accept(bias, x, y, rnd): continue
            k += 1
            paths.append(lens(rnd, flow, x, y, rnd.uniform(*lr), rnd.uniform(*wr)))
        out.append(f'<path d="{" ".join(paths)}" fill="{col}" fill-opacity="{op}"/>')
    for col, op, sw, n, lr in fine:
        fs = []
        for _ in range(n):
            x, y = pick(); ux, uy = flow(x, y); a = math.atan2(uy, ux) + rnd.gauss(0, .3); ln = rnd.uniform(*lr)
            fs.append(f'M{x:.2f} {y:.2f} l{math.cos(a) * ln:.2f} {math.sin(a) * ln:.2f}')
        out.append(f'<path d="{" ".join(fs)}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round"/>')
    return '\n'.join(out)

BAKE_DEFS = '''<filter id="b03" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation=".3"/></filter>
 <filter id="b05" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation=".5"/></filter>
 <filter id="b1" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1"/></filter>
 <filter id="b2" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2"/></filter>'''

HILL = f'<path d="M0 78 Q30 66 52 74 T100 70 V100 H0Z" fill="#5fae3c" stroke="{INK}" stroke-width="2.5"/>'

def avatar_svg(defs, body, head_inner, webp, box, head_dy=-1.5, href=None):
    BX, BY, BW, BH = box
    href = href or 'data:image/webp;base64,' + base64.b64encode(webp).decode()
    return f'''<svg viewBox="0 0 100 100" aria-hidden="true">
<defs>
{defs}
</defs>
<rect width="100" height="100" fill="#8fd3ff"/>
{HILL}
<g id="avBody">
{body}
</g>
<g id="avHead"><g transform="translate(0 {head_dy})">
<image href="{href}" x="{BX}" y="{BY}" width="{BW}" height="{BH}"/>
{head_inner}
</g></g>
</svg>'''

def presets_js(who, MOUTH, BROWS, note):
    mo = ',\n    '.join(f"{k}: ['{d}', '{f}']" for k, (d, f) in MOUTH.items())
    br = ',\n    '.join(f"{k}: '{d}'" for k, d in BROWS.items())
    return f'''// {who} avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// {note}
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('{who.lower()}', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = {{ ... }};` / `let BROWS = {{ ... }};` inside `const AV = (() => {{`.
  let MOUTH = {{
    {mo}
  }};
  let BROWS = {{
    {br}
  }};
'''

def stats(svg):
    return dict(bytes=len(svg.encode()), elements=len(re.findall(r'<[a-zA-Z]', svg)),
                forbidden=len(re.findall(r'<(filter|mask|clipPath)\b|filter=|mask=|clip-path=', svg)))

# Neil's tables (reference for the shapes the AV module expects)
NEIL_MOUTH = {
    'rest':   ('M40.2 66.4 Q50 69.4 59.8 66.4 Q57.6 73.6 50 73.8 Q42.4 73.6 40.2 66.4Z', 'url(#avTe)'),
    'closed': ('M42.2 68.2 Q50 71.4 57.8 68.0', 'none'),
    'small':  ('M45 68.4 Q50 74 55 68.4 Q50 69.6 45 68.4Z', 'url(#avMo)'),
    'wide':   ('M41.6 67.6 Q50 80 58.4 67.6 Q50 69.8 41.6 67.6Z', 'url(#avMo)'),
    'o':      ('M46.8 70.6 a3.2 3.8 0 1 0 6.4 0 a3.2 3.8 0 1 0 -6.4 0Z', 'url(#avMo)'),
    'ee':     ('M42 67.8 Q50 74.4 58 67.8 Q50 69.4 42 67.8Z', 'url(#avMo)'),
    'grin':   ('M38.6 65.8 Q50 69.2 61.4 65.4 Q59.2 77 50 77.4 Q40.8 77 38.6 65.8Z', 'url(#avGr)'),
    'frown':  ('M43.2 72.2 Q50 67.4 56.8 72.2', 'none'),
    'shock':  ('M45.6 71.6 a4.4 5.4 0 1 0 8.8 0 a4.4 5.4 0 1 0 -8.8 0Z', 'url(#avMo)'),
    'tight':  ('M43.4 69.6 Q47 68.6 50 69.4 T56.6 69', 'none'),
    'wobble': ('M42 69.8 q2 -2 4 0 t4 0 t4 0 t4 0', 'none'),
}
def scale_mouth(d, sx, sy, cy0=68.5, cy1=68.5):
    return ptrans(d, lambda x, y: (50 + (x - 50) * sx, cy1 + (y - cy0) * sy), lambda dx, dy: (dx * sx, dy * sy), nd=1)

def trace_overlay(svg, ref_png, out_svg):
    """vector art at 55% over the warped photo (to check the trace)"""
    s = re.sub(r'(<g id="avHead"><g transform="[^"]*">)', lambda m: m.group(1) + f'<image href="{du(ref_png)}" width="100" height="100"/><g opacity=".55">', svg, count=1)
    s = s.replace('</g></g>\n</svg>', '</g></g></g>\n</svg>')
    open(out_svg, 'w').write(s)

def split_svg(svg):
    """the game's split inside <button id="player">: a background SVG (rect, hill, #avBody) and a head
    layer SVG (class avHeadL) holding <defs> and the #avHead group."""
    defs = re.search(r'<defs>.*?</defs>', svg, re.S).group(0)
    a = svg.index('<rect width="100"'); b = svg.index('<g id="avHead">')
    bg = svg[a:b].strip()
    head = svg[b:svg.rindex('</svg>')].strip()
    return (f'<svg viewBox="0 0 100 100" aria-hidden="true">\n{bg}\n</svg>\n'
            f'<svg class="avHeadL" viewBox="0 0 100 100" aria-hidden="true">\n{defs}\n{head}\n</svg>')
