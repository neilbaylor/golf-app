"""Hunter (13, blonde) — sticker-book avatar in Neil's style, two versions: no hat / floral cap.
Geometry traced over hunter_cap.jpg + the group photo warped into the 100-unit frame (eyes 42/58, y=51).
Writes ../../hunter/{avatar.svg, avatar-hat.svg, av-presets.js} and trace overlays in ../tmp/."""
import math, random, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from avlib import *

WHO = 'hunter'; OUTD = CREW + 'hunter/'; os.makedirs(OUTD, exist_ok=True)
BOX = (17, 12, 66, 72)
EYE_DY = -3; EYE_S = .88; HEAD_DY = -1.5

# ------------------------------------------------------------------ palette
SKIN = (247, 196, 167); SKIN_HI = (255, 224, 202); SKIN_S1 = (232, 166, 138); SKIN_S2 = (208, 136, 112)
FLUSH = (238, 122, 114)
H_BASE = ('#efdcaa', '#dcc189', '#b79a62')      # top -> bottom gradient
H_DD = '#7a5f36'; H_D = '#9c7d48'; H_M = '#c9ab6e'; H_L = '#f0dfae'; H_LL = '#fbf3d8'
BROW = '#a37b4a'; FRECK = '#cf8964'; LINE = '#b0644e'

# ------------------------------------------------------------------ geometry (head-local units)
_J = [(33.0, 54), (33.3, 60.6), (34.4, 66.4), (36.6, 71.2), (40.0, 75.2), (44.6, 77.8), (50, 78.5)]
JAW_PTS = _J + mirror(_J[-2::-1])
FACE_PTS = [(34.2, 40), (33.6, 47)] + _J[1:] + mirror(_J[-2:0:-1]) + [(66.4, 47), (65.8, 40), (64, 31.5), (50, 28), (36, 31.5)]
EAR_L_PTS = [(33.6, 50.6), (30.8, 48.9), (28.0, 48.7), (26.0, 49.9), (25.0, 52.4), (25.1, 55.6), (26.0, 58.6), (27.5, 61.0), (29.6, 62.6), (31.8, 62.6), (33.8, 61.0)]
EAR_R_PTS = mirror(EAR_L_PTS)
EAR_IN_L = [(28.6, 51.6), (27.4, 53.6), (27.6, 56.4), (28.8, 58.6), (30.4, 59.2)]
EAR_IN_L2 = [(26.6, 51.4), (28.2, 50.4), (30.2, 51.0)]

# messy, wavy, swept forward and to the viewer's right; flicks out at the sides
HAIR_OUT = [(33.4, 49.8), (31.8, 47.4), (30.0, 47.8), (30.6, 44.6), (29.0, 41.2), (29.4, 37.6), (27.8, 34.0), (29.0, 30.2), (29.2, 26.6),
            (31.6, 23.4), (34.6, 19.8), (38.8, 17.8), (42.6, 15.0), (47.0, 15.8), (51.0, 13.2), (55.6, 14.6), (59.8, 14.0), (63.6, 16.8),
            (67.2, 18.0), (69.6, 21.4), (72.8, 23.2), (72.6, 27.4), (74.6, 30.8), (73.8, 34.6), (76.2, 38.4), (73.4, 39.8), (74.4, 44.0),
            (71.4, 44.8), (69.6, 47.8), (66.8, 50.6)]
# fringe: four big locks swept down-right; traversal right -> left
_TUFTS = [(65.4, 37.6, 42.4, 6.0), (59.0, 35.6, 41.6, 7.0), (51.6, 34.8, 40.2, 7.0), (44.4, 34.6, 38.8, 6.6)]
HAIR_IN = [(66.8, 50.6), (66.6, 47.0), (66.2, 43.6), (66.0, 40.8)]
for i, (rx, ry, ty, w) in enumerate(_TUFTS):
    ny = _TUFTS[i + 1][1] if i + 1 < len(_TUFTS) else 36.4
    HAIR_IN += [(rx, ry), (rx - .7, ry + (ty - ry) * .55), (rx - 1.9, ty), (rx - 3.4, ty - 1.1), (rx - w * .74, (ty + ny) / 2 - .2)]
HAIR_IN += [(37.0, 36.4), (35.2, 39.6), (34.2, 44.0), (33.6, 47.6), (33.4, 49.8)]
HAIR_LINES = ('M44.6 17.6 C46.0 21.6 44.8 25.0 48.4 29.0 M52.4 15.8 C54.0 19.8 53.2 23.4 57.0 27.0 M37.6 20.6 C38.8 24.2 37.6 27.6 40.8 31.0 '
              'M60.6 17.2 C63.0 20.2 62.6 24.0 65.6 27.0 M67.6 26.4 C69.6 29.0 69.0 32.6 70.6 35.6 M31.4 29.6 C32.6 32.4 31.4 35.0 32.6 38.0 '
              'M54.0 30.0 Q56.6 32.0 57.4 34.6 M46.6 30.4 Q49.0 32.0 49.6 34.4')
FLY = 'M49.8 13.6 Q51.6 11.2 54.4 11.6 M41.8 15.4 Q43.0 13.2 45.4 13.0 M74.2 37.6 Q76.6 38.6 77.6 40.8'

# features
LIDS = 'M37.5 50.4 Q42 47.2 46.4 49.9 M53.6 49.9 Q58 47.2 62.5 50.4'
LOWLID = 'M39.4 53.9 Q42 54.9 44.6 53.9 M55.4 53.9 Q58 54.9 60.6 53.9'
NOSE = ('M52.4 57.0 Q52.9 58.6 53.0 59.8 '
        'M47.8 60.8 Q46.2 61.4 46.4 62.6 Q46.8 63.5 48.0 63.2 '
        'M52.2 60.8 Q53.8 61.4 53.6 62.6 Q53.2 63.5 52.0 63.2 '
        'M48.2 64.0 Q50 64.8 51.8 64.0')
CHEEKLINES = 'M41.2 64.0 Q40.2 65.8 40.9 67.6 M58.8 64.0 Q59.8 65.8 59.1 67.6'

BROWS = {
    'neutral': 'M36.2 46.8 Q41 45.4 46.0 46.0 M54.0 46.0 Q59 45.4 63.8 46.8',
    'focus':   'M36.4 45.4 Q41.2 45.4 46.0 47.4 M54.0 47.4 Q58.8 45.4 63.6 45.4',
    'up':      'M36.2 44.8 Q41 43.0 46.0 43.8 M54.0 43.8 Q59 43.0 63.8 44.8',
    'sad':     'M36.4 47.0 Q41.2 46.8 46.0 44.4 M54.0 44.4 Q58.8 46.8 63.6 47.0',
    'happy':   'M36.2 45.8 Q41 44.0 46.0 44.8 M54.0 44.8 Q59 44.0 63.8 45.8',
}
MOUTH = {k: (scale_mouth(d, .84, .9, 69.0, 67.9), f) for k, (d, f) in NEIL_MOUTH.items()}
MOUTH['rest'] = ('M44.2 66.6 Q50 70.4 55.8 66.6 M43.1 65.8 Q43.7 66.8 44.8 67.3 M56.9 65.8 Q56.3 66.8 55.2 67.3', 'none')
MOUTH['closed'] = ('M44.6 67.4 Q50 69.6 55.4 67.4', 'none')
MOUTH['grin'] = ('M41.8 65.8 Q50 68.6 58.2 65.8 Q56.6 74.8 50 75.0 Q43.4 74.8 41.8 65.8Z', 'url(#avGr)')
MOUTH = {k: MOUTH[k] for k in NEIL_MOUTH}

# ------------------------------------------------------------------ hat (floral cap, brim angled to the viewer's right)
CROWN = [(30.2, 39.4), (29.6, 32.0), (33.2, 25.2), (40.0, 21.0), (50.2, 19.6), (60.6, 20.6), (67.4, 24.6), (70.9, 31.0), (70.4, 37.6)]
SEAM_D = 'M30.2 39.4 Q50 32.6 70.4 37.6'
BRIM_OUT = 'M70.4 37.6 C76.0 36.2 82.4 38.0 81.8 41.4 C81.2 44.8 72.4 44.8 64.0 42.8 Q52.0 40.4 40.0 40.9 Q31.0 41.6 28.8 41.0 Q27.8 40.0 30.2 39.4'
BRIM_D = 'M30.2 39.4 Q50 32.6 70.4 37.6 ' + BRIM_OUT[1:].split(' ', 2)[2] + 'Z'
CAP_SEAMS = 'M50.2 20.2 Q51.2 27.4 50.8 35.6 M40.6 21.6 Q37.0 28.4 36.0 37.6 M60.2 21.4 Q64.4 27.8 65.2 36.6'
BUTTON = 'M48.7 19.9 Q50.2 17.8 51.7 19.9'
# hair under the cap: side tufts + a few fringe tufts peeking out under the brim
HL_OUT = [(30.4, 40.6), (28.6, 43.4), (29.6, 46.0), (29.2, 49.2), (31.6, 48.8), (33.6, 50.2)]
HL_IN = [(33.6, 50.2), (33.9, 46.6), (34.6, 43.0), (36.0, 41.4)]
HR_OUT = [(70.0, 39.6), (72.0, 41.8), (71.6, 44.0), (73.2, 46.4), (70.0, 46.2), (68.0, 48.6), (66.6, 50.6)]
HR_IN = [(66.6, 50.6), (66.4, 47.0), (66.0, 43.6), (64.6, 42.4)]
FR_TUFTS = [((35.4, 41.6), (42.4, 40.6), (41.2, 44.6)), ((43.6, 40.4), (48.6, 40.2), (47.8, 43.0)), ((56.4, 40.8), (64.0, 42.0), (62.8, 45.2))]

FACE_D, FACE_POLY = cr(FACE_PTS, True)
JAW_D, _ = cr(JAW_PTS)
EAR_L_D, EAR_L_POLY = cr(EAR_L_PTS); EAR_R_D, EAR_R_POLY = cr(EAR_R_PTS)
EAR_IN_D = ' '.join(cr(p)[0] for p in [EAR_IN_L, mirror(EAR_IN_L), EAR_IN_L2, mirror(EAR_IN_L2)])
HO_D, HO_POLY = cr(HAIR_OUT); HI_D, HI_POLY = cr(HAIR_IN, t=.9)
HAIR_D = HO_D + ' L' + HI_D[1:] + 'Z'; HAIR_POLY = np.vstack([HO_POLY, HI_POLY])
HAIRLINE_D = cr(HAIR_IN[2:-2], t=.9)[0]
CROWN_D = cr(CROWN)[0] + ' Q50 32.6 30.2 39.4Z'
CAP_POLY = np.vstack([cr(CROWN)[1], [(50, 36.4)]])

def hat_hair():
    """closed paths for the hair that shows under the cap + the open outer edges for ink"""
    lo, lop = cr(HL_OUT); li, lip = cr(HL_IN)
    ro, rop = cr(HR_OUT); ri, rip = cr(HR_IN)
    d = lo + ' L' + li[1:] + 'Z ' + ro + ' L' + ri[1:] + 'Z'
    polys = [np.vstack([lop, lip]), np.vstack([rop, rip])]
    # blonde fringe band under the brim: top edge hidden under the brim, locks hang down-right
    fb = [(68.6, 42.4), (66.8, 44.6), (64.6, 42.6), (62.2, 45.0), (59.6, 42.6), (57.0, 44.2), (54.4, 42.2), (51.0, 43.6), (48.2, 42.0),
          (45.2, 43.8), (42.4, 42.0), (39.8, 44.4), (37.2, 42.4), (34.8, 44.2), (32.8, 42.6), (31.0, 41.6)]
    fd, fp = cr(fb, t=.9)
    tufts = ' M30.4 40.2 L69.6 38.8 L' + fd[1:] + 'Z'
    polys.append(np.vstack([[(30.4, 40.2), (69.6, 38.8)], fp]))
    ink_in_extra = ' ' + fd
    ink_out = lo + ' ' + ro
    ink_in = li + ' ' + ri
    return d + tufts, polys, ink_out, ink_in, ink_in_extra

# ------------------------------------------------------------------ texture bake
rnd = random.Random(7)
def flow(x, y):
    if y > 37 and x < 35: dx, dy = -.25, 1
    elif y > 35 and x > 66: dx, dy = .4, 1
    elif y > 29 and 35 <= x <= 66: dx, dy = .5, 1
    else: dx, dy = x - 40, y - 3; dx += 7
    L = math.hypot(dx, dy); return dx / L, dy / L

def hair_strands(poly, n=1.0, bbox=(26, 12, 76, 52)):
    L = [(H_DD, .5, int(45 * n), (3, 6.5), (.5, 1.0), 0), (H_D, .55, int(50 * n), (3, 6), (.6, 1.1), 0),
         (H_M, .7, int(55 * n), (3, 6), (.6, 1.2), 0), (H_L, .85, int(60 * n), (2.6, 5.2), (.5, 1.0), 1),
         (H_LL, .85, int(34 * n), (1.8, 3.6), (.3, .6), 2)]
    F = [(H_DD, .35, .3, int(90 * n), (1.4, 3.2)), (H_LL, .5, .28, int(90 * n), (1.4, 3.2))]
    def acc(bias, x, y, r):
        if bias == 0: return True
        return r.random() > (.3 if bias == 1 else .55) * ((x - 26) / 50 + max(0, y - 28) / 18)
    return strands(rnd, poly, flow, L, F, bbox, acc)

def freckles():
    out = []
    areas = [(41.6, 57.8, 5.4, 2.6, 18), (58.4, 57.8, 5.4, 2.6, 18), (50.0, 57.6, 2.8, 2.0, 7)]
    for cx, cy, rx, ry, n in areas:
        k = 0
        while k < n:
            a = rnd.uniform(0, 2 * math.pi); r = math.sqrt(rnd.random())
            x, y = cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)
            if abs(x - 50) < 2.6 and y > 59.5: continue
            k += 1
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rnd.uniform(.2, .34):.2f}" fill-opacity="{rnd.uniform(.25, .5):.2f}"/>')
    return f'<g fill="{FRECK}">' + ''.join(out) + '</g>'

def face_shading(hairline_d, fringe_shadow=True):
    S1, S2, HI, FL = rgb(SKIN_S1), rgb(SKIN_S2), rgb(SKIN_HI), rgb(FLUSH)
    return f'''<g clip-path="url(#cf)">
 <path d="{JAW_D}" fill="none" stroke="{S2}" stroke-width="4.4" opacity=".34" filter="url(#b2)"/>
 <ellipse cx="66" cy="59" rx="3.2" ry="12" fill="{S1}" opacity=".32" filter="url(#b2)"/>
 {f'<path d="{hairline_d}" fill="none" stroke="#c07a5c" stroke-width="3" opacity=".45" filter="url(#b1)"/>' if fringe_shadow else ''}
 <ellipse cx="46.8" cy="50.4" rx="1.6" ry="1.3" fill="{S2}" opacity=".35" filter="url(#b05)"/>
 <ellipse cx="53.2" cy="50.4" rx="1.6" ry="1.3" fill="{S2}" opacity=".4" filter="url(#b05)"/>
 <ellipse cx="38.4" cy="58.2" rx="3.4" ry="1.8" fill="{HI}" opacity=".5" filter="url(#b1)"/>
 <ellipse cx="61.6" cy="58.4" rx="3.2" ry="1.7" fill="{HI}" opacity=".35" filter="url(#b1)"/>
 <ellipse cx="39" cy="61" rx="4.6" ry="3.2" fill="{FL}" opacity=".34" filter="url(#b2)"/>
 <ellipse cx="61" cy="61" rx="4.6" ry="3.2" fill="{FL}" opacity=".34" filter="url(#b2)"/>
 <ellipse cx="50" cy="61.4" rx="2.4" ry="1.6" fill="{FL}" opacity=".22" filter="url(#b1)"/>
 <path d="M52.4 55.6 Q53.2 58.2 53.4 60.4" stroke="{S1}" stroke-width="1.8" fill="none" opacity=".5" filter="url(#b05)"/>
 <path d="M50.2 54.6 Q50.4 57.6 50.4 60" stroke="{HI}" stroke-width="1.2" fill="none" opacity=".6" filter="url(#b05)"/>
 <ellipse cx="49.8" cy="61.6" rx="1.5" ry="1" fill="#fff4ea" opacity=".6" filter="url(#b05)"/>
 <ellipse cx="50" cy="64.6" rx="3" ry=".8" fill="{S2}" opacity=".45" filter="url(#b05)"/>
 <ellipse cx="50" cy="69.0" rx="3.4" ry=".9" fill="#e08884" opacity=".28" filter="url(#b05)"/>
 <ellipse cx="50" cy="75.4" rx="3.6" ry="1.4" fill="{HI}" opacity=".45" filter="url(#b05)"/>
 {freckles()}
</g>'''

def tropical_print():
    """simplified generic tropical print: palm fronds, blue hibiscus, pink blooms (no text / logo)"""
    out = []
    def frond(x, y, ang, ln, w, col):
        c, s = math.cos(ang), math.sin(ang); nx, ny = -s, c
        d = ''
        for k in range(5):  # leaflet pairs along a rib
            t = .15 + k * .19; px, py = x + c * ln * t, y + s * ln * t; L = w * (1.15 - .5 * abs(t - .45))
            for sg in (1, -1):
                ex, ey = px + (nx * sg * .9 + c * .45) * L, py + (ny * sg * .9 + s * .45) * L
                mx, my = (px + ex) / 2, (py + ey) / 2; qx, qy = -(ey - py) * .22, (ex - px) * .22
                d += f'M{px:.1f} {py:.1f} Q{mx + qx:.1f} {my + qy:.1f} {ex:.1f} {ey:.1f} Q{mx - qx:.1f} {my - qy:.1f} {px:.1f} {py:.1f}Z'
        out.append(f'<path d="{d}" fill="{col}"/><path d="M{x:.1f} {y:.1f} l{c * ln:.1f} {s * ln:.1f}" stroke="#a8e09a" stroke-width=".3" opacity=".8"/>')
    def hib(x, y, r, a0):
        d = ''
        for k in range(5):
            a = a0 + k * 2 * math.pi / 5; c, s = math.cos(a), math.sin(a); nx, ny = -s, c
            ex, ey = x + c * r, y + s * r
            d += (f'M{x:.1f} {y:.1f} C{x + (c * .5 + nx * .75) * r:.1f} {y + (s * .5 + ny * .75) * r:.1f} {ex + nx * .55 * r:.1f} {ey + ny * .55 * r:.1f} {ex:.1f} {ey:.1f} '
                  f'C{ex - nx * .55 * r:.1f} {ey - ny * .55 * r:.1f} {x + (c * .5 - nx * .75) * r:.1f} {y + (s * .5 - ny * .75) * r:.1f} {x:.1f} {y:.1f}Z')
        out.append(f'<path d="{d}" fill="#3a78cf"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .42:.2f}" fill="#7cc0f5"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .16:.2f}" fill="#f07ab0"/>')
    def bloom(x, y, r):
        for k in range(5):
            a = k * 2 * math.pi / 5 + .4
            out.append(f'<circle cx="{x + math.cos(a) * r * .55:.1f}" cy="{y + math.sin(a) * r * .55:.1f}" r="{r * .45:.2f}" fill="#e8559a"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .3:.2f}" fill="#ffc2dd"/>')
    for (x, y, a, ln) in [(28, 28, -.3, 9), (31, 38, -.9, 8), (40, 21, .5, 8), (53, 37, -1.2, 8), (61, 22, .9, 8.5), (72, 30, 2.6, 9),
                          (45, 31, -.2, 7), (66, 37, -2.2, 7.5), (35, 24, 1.3, 6.5), (57, 30, 2.2, 7), (48, 22, 2.8, 6.5), (70, 22, 2.0, 7)]:
        frond(x, y, a, ln * 1.25, rnd.uniform(2.2, 2.8), rnd.choice(['#2e7a44', '#3f9a52', '#5cb860', '#1f6f6a', '#47a35a']))
    for (x, y, r) in [(42.4, 27.0, 3.0), (59.2, 30.6, 3.2), (34.4, 33.6, 2.5), (51.4, 23.2, 2.5), (66.6, 26.4, 2.4), (47.8, 35.0, 2.3)]:
        hib(x, y, r * 1.2, rnd.uniform(0, 1.2))
    for (x, y) in [(37.0, 27.6), (55.8, 26.4), (63.6, 34.4), (45.4, 22.2), (40.6, 35.6), (69.0, 32.0), (32.0, 30.0), (53.6, 31.6)]:
        bloom(x, y, rnd.uniform(1.8, 2.3))
    return '\n'.join(out)

def bake_svg(hat):
    skin = du(T + 'h_skin.png')
    if not hat:
        hair = f'''<path d="{HAIR_D}" fill="url(#ghair)"/>
<g clip-path="url(#ch)" fill="none" stroke-linecap="round">
 <path d="{HAIRLINE_D}" stroke="{H_DD}" stroke-width="2.2" opacity=".45" filter="url(#b05)"/>
 <ellipse cx="45" cy="21" rx="13" ry="4" fill="#f6e8bb" opacity=".55" filter="url(#b2)"/>
 <ellipse cx="29.6" cy="40" rx="2.4" ry="8" fill="{H_D}" opacity=".4" filter="url(#b1)"/>
 <ellipse cx="72" cy="40" rx="2.6" ry="8" fill="{H_D}" opacity=".45" filter="url(#b1)"/>
 {hair_strands(HAIR_POLY)}
</g>'''
        clip_hair = f'<clipPath id="ch"><path d="{HAIR_D}"/></clipPath>'
        face = face_shading(HAIRLINE_D)
        cap = ''
    else:
        hd, hpolys, _, _, _ = hat_hair()
        clip_hair = f'<clipPath id="ch"><path d="{hd}"/></clipPath><clipPath id="cc"><path d="{CROWN_D}"/></clipPath>'
        face = face_shading(HAIRLINE_D, False).replace('</g>', '<path d="M30 41 Q50 37.6 72 40 Q60 47.4 50 47 Q38 47.2 30 41Z" fill="#9a4a36" opacity=".3" filter="url(#b1)"/></g>', 1)
        hair = f'''<path d="{hd}" fill="url(#ghair)"/>
<g clip-path="url(#ch)" fill="none" stroke-linecap="round">
 <ellipse cx="30" cy="44" rx="2.4" ry="5" fill="{H_D}" opacity=".35" filter="url(#b1)"/>
 <ellipse cx="71" cy="44" rx="2.4" ry="5" fill="{H_D}" opacity=".4" filter="url(#b1)"/>
 <path d="M30 40.4 Q50 37.2 70 39.0" stroke="{H_D}" stroke-width="1.6" opacity=".35" filter="url(#b05)"/>
 {hair_strands(np.vstack(hpolys), .55, (27, 38, 75, 51))}
</g>'''
        cap = f'''<path d="{CROWN_D}" fill="#1b2230"/>
<g clip-path="url(#cc)">
 {tropical_print()}
 <ellipse cx="44" cy="22" rx="10" ry="4" fill="#ffffff" opacity=".18" filter="url(#b2)"/>
 <path d="M29 30 Q30 40 33 39 M71 28 Q71 39 67 39" stroke="#0b0f18" stroke-width="5" fill="none" opacity=".45" filter="url(#b2)"/>
 <path d="{SEAM_D}" stroke="#0b0f18" stroke-width="2" fill="none" opacity=".5" filter="url(#b05)"/>
</g>
<path d="{BRIM_D}" fill="url(#gbrim)"/>
<path d="M31 39.8 Q50 33.6 70 38.2" stroke="#0d4f55" stroke-width="2" fill="none" opacity=".5" filter="url(#b05)"/>
<ellipse cx="62" cy="38.6" rx="9" ry="1.6" fill="#7fe0d6" opacity=".35" filter="url(#b1)"/>
<path d="M30.2 40.6 Q36 40.8 40 40.4 Q52 39.8 64 42.2 Q72.4 44.2 80.6 41.6" stroke="#e8559a" stroke-width=".8" fill="none" opacity=".85"/>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{' '.join(map(str, BOX))}">
<defs>
 {BAKE_DEFS}
 <clipPath id="cf"><path d="{FACE_D}"/></clipPath>
 {clip_hair}
 <linearGradient id="ghair" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{H_BASE[0]}"/><stop offset=".5" stop-color="{H_BASE[1]}"/><stop offset="1" stop-color="{H_BASE[2]}"/></linearGradient>
 <linearGradient id="gbrim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f7b80"/><stop offset=".55" stop-color="#2fa3a3"/><stop offset="1" stop-color="#46bdb8"/></linearGradient>
</defs>
<image href="{skin}" x="0" y="0" width="100" height="100"/>
<path d="M{EAR_L_D[1:]} M{EAR_R_D[1:]}" fill="none" stroke="{rgb(SKIN_S2)}" stroke-width="1.6" opacity=".4" filter="url(#b05)"/>
{face}
{hair}
{cap}
</svg>'''

# ------------------------------------------------------------------ final svg
DEFS = '''<radialGradient id="avIris" fx=".4" fy=".36"><stop offset=".08" stop-color="#fff"/><stop offset=".13" stop-color="#18222a"/><stop offset=".4" stop-color="#18222a"/><stop offset=".52" stop-color="#5b7d92"/><stop offset=".8" stop-color="#93afc0"/><stop offset="1" stop-color="#2a3a45"/></radialGradient>
<linearGradient id="avTe" x2="0" y2="1"><stop offset=".7" stop-color="#fffaf0"/><stop offset=".78" stop-color="#7a2e2a"/></linearGradient>
<linearGradient id="avGr" x2="0" y2="1"><stop offset=".4" stop-color="#fffaf0"/><stop offset=".48" stop-color="#4a1b1b"/><stop offset=".72" stop-color="#4a1b1b"/><stop offset=".86" stop-color="#d0605a"/></linearGradient>
<linearGradient id="avMo" x2="0" y2="1"><stop offset=".22" stop-color="#fffaf0"/><stop offset=".28" stop-color="#4a1b1b"/><stop offset=".7" stop-color="#4a1b1b"/><stop offset=".8" stop-color="#d0605a"/></linearGradient>'''
BODY = f'''<path d="M6 104 Q8 90 30 87 Q40 86 50 86 Q60 86 70 87 Q92 90 94 104Z" fill="#5fc4b0" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
<path d="M43.6 72 L43.3 86.4 L50 91.6 L56.7 86.4 L56.4 72Z" fill="#e6a888" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M42.2 84.8 L37.6 92.6 L45.8 95.4 L50 91.6Z M57.8 84.8 L62.4 92.6 L54.2 95.4 L50 91.6Z M50 91.6 V101" fill="#3a9b88" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'''

def head_inner(hat):
    m = MOUTH['rest']
    eyes = (f'<g id="avEyes" transform="translate(0 {EYE_DY}) translate(0 54) scale(1 {EYE_S}) translate(0 -54)">'
            f'<ellipse id="avEyeL" cx="42" cy="54" rx="2.7" ry="2.9" fill="url(#avIris)"/><ellipse id="avEyeR" cx="58" cy="54" rx="2.7" ry="2.9" fill="url(#avIris)"/></g>')
    feats = f'''<path d="{CHEEKLINES}" fill="none" stroke="{LINE}" stroke-width="1.1" stroke-linecap="round" opacity=".45"/>
<path d="{LOWLID}" fill="none" stroke="{LINE}" stroke-width=".9" stroke-linecap="round" opacity=".45"/>
{eyes}
<path d="{LIDS}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>
<path d="{NOSE}" fill="none" stroke="{INK}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
<path id="avBrows" d="{BROWS['neutral']}" fill="none" stroke="{BROW}" stroke-width="2.1" stroke-linecap="round"/>'''
    tail = f'''<path id="avMouth" d="{m[0]}" fill="{m[1]}" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path id="avSweat" d="{'M67.6 41.6 q2.6 4.4 0 6.2 q-2.6 -1.8 0 -6.2z' if hat else 'M66.8 38.6 q2.6 4.4 0 6.2 q-2.6 -1.8 0 -6.2z'}" fill="#8fd3ff" stroke="{INK}" stroke-width="1.4" opacity="0"/>'''
    ear_in = f'<path d="{EAR_IN_D}" fill="none" stroke="{INK}" stroke-width="1" stroke-linecap="round" opacity=".4"/>'
    if not hat:
        return f'''<path d="{EAR_L_D} {EAR_R_D} {JAW_D} {HO_D}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{HAIRLINE_D}" fill="none" stroke="{INK}" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"/>
{ear_in}
<path d="{HAIR_LINES}" fill="none" stroke="{H_DD}" stroke-width=".9" stroke-linecap="round" opacity=".7"/>
<path d="{FLY}" fill="none" stroke="{INK}" stroke-width="1.4" stroke-linecap="round"/>
{feats}
{tail}'''
    _, _, ink_out, ink_in, tufts = hat_hair()
    return f'''<path d="{EAR_L_D} {EAR_R_D} {JAW_D} {ink_out}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{ink_in}{tufts}" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>
{ear_in}
{feats}
<path d="{cr(CROWN)[0]} {BRIM_OUT} {BUTTON}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{SEAM_D} {CAP_SEAMS}" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round" opacity=".8"/>
{tail}'''

def build():
    w0, L = cwarp.warp('h_cap.jpg', PPU=8, CX=50); cv2.imwrite(T + 'warp_h.png', w0)
    mid = (L[1][0] + L[152][0]) / 2; cx = 50 - (mid - 50)
    feat = [(cx - 8, 51.2, 4.6, 2.4), (cx + 8, 51.2, 4.6, 2.4), (cx - 8.6, 47, 6.2, 2.0), (cx + 8.6, 47, 6.2, 2.0), (50, 68.6, 8.6, 3.2)]
    keep = [(42, 51.5, 6, 3.6), (58, 51.5, 6, 3.6), (50, 68, 10, 4.6)]
    ref, _ = photo_skin('h_cap.jpg', cx, FACE_POLY, [EAR_L_POLY, EAR_R_POLY], feat, keep, SKIN, FLUSH, T + 'h_skin.png',
                        lowk=.5, detk=.28, flushk=.4, flush_excl=[(50, 68.6, 9, 3.6)])
    res = {}
    for hat in (False, True):
        tag = 'h_hat' if hat else 'h'
        webp = bake(bake_svg(hat), tag, BOX, tppu=int(os.environ.get('TPPU', 5)), q=int(os.environ.get('Q', 78)))
        svg = avatar_svg(DEFS, BODY, head_inner(hat), webp, BOX, HEAD_DY)
        fn = OUTD + ('avatar-hat.svg' if hat else 'avatar.svg')
        open(fn, 'w').write(svg)
        trace_overlay(svg, T + 'warp_h.png', T + f'trace_{tag}.svg')
        res[tag] = dict(webp=len(webp), **stats(svg))
    open(OUTD + 'av-presets.js', 'w').write(presets_js('Hunter', MOUTH, BROWS,
        'Face: eyes 42/58 at y=51 (static #avEyes transform), mouth ~y67, chin ~y78; rest = closed-mouth smile, happy = open grin.'))
    json.dump({'MOUTH': MOUTH, 'BROWS': BROWS}, open(T + 'hunter_presets.json', 'w'))
    print(json.dumps(res))

if __name__ == '__main__':
    build()
