"""Sean (adult, salt-and-pepper) — sticker-book avatar in Neil's style, two versions: no hat / navy cap.
"Same as Neil but a bigger face and head (not crazy)": face ~6% broader, head ~5% taller, still clear of the name tag.
Geometry traced over sean_and_hunter.jpg (Sean) + sean_cap_selfie.jpg warped into the 100-unit frame (eyes 42/58, y=51)."""
import math, random, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from avlib import *

WHO = 'sean'; OUTD = CREW + 'sean/'; os.makedirs(OUTD, exist_ok=True)
BOX = (17, 12, 66, 72)
EYE_DY = -3; EYE_S = .62; HEAD_DY = -1.5

# ------------------------------------------------------------------ palette
SKIN = (237, 166, 134); SKIN_HI = (251, 204, 174); SKIN_S1 = (220, 140, 110); SKIN_S2 = (190, 108, 86)
FLUSH = (224, 92, 80)
H_BASE = ('#75695f', '#5f5349', '#4f453d')        # ash grey-brown top
H_DD = '#3a312a'; H_D = '#54483e'; H_M = '#776a5e'; H_G = '#aaa59e'; H_GL = '#cfcbc4'; H_W = '#ebe8e3'
BROW = '#35271e'; LINE = '#8e4936'; STUB_L = '#f4f0ea'; STUB_D = '#5e4d43'

# ------------------------------------------------------------------ geometry (head-local units)
# broad, full face: wide to ~y76, then a broad flat-ish chin (y83.2 local = 81.7 shown, clear of the name tag)
_J = [(29.8, 54), (29.8, 61.0), (30.4, 67.0), (31.8, 72.4), (34.6, 77.0), (39.2, 80.8), (44.6, 82.8), (50, 83.2)]
JAW_PTS = _J + mirror(_J[-2::-1])
FACE_PTS = [(30.4, 40), (29.8, 47)] + _J[1:] + mirror(_J[-2:0:-1]) + [(70.2, 47), (69.6, 40), (67.4, 31), (50, 27.4), (32.6, 31)]
# small ears, close to the head
EAR_L_PTS = [(30.0, 50.2), (28.2, 48.9), (26.3, 48.8), (25.0, 50.2), (24.6, 52.8), (24.8, 55.6), (25.6, 58.2), (26.8, 60.2), (28.4, 61.2), (30.0, 60.8)]
EAR_R_PTS = mirror(EAR_L_PTS)
EAR_IN_L = [(27.6, 51.6), (26.8, 53.6), (27.0, 56.2), (28.0, 58.0), (29.2, 58.4)]
EAR_IN_L2 = [(26.2, 51.0), (27.6, 50.4), (29.2, 51.0)]

# short, swept up and back, a messy peak at the back-right; ash brown on top, grey/white at the sides
HAIR_OUT = [(30.0, 52.0), (28.8, 48.0), (27.8, 43.0), (27.0, 37.6), (26.8, 32.6), (27.6, 28.2), (29.2, 24.6), (31.6, 21.6), (34.8, 19.4),
            (38.0, 18.2), (41.0, 16.4), (44.4, 16.2), (47.4, 14.8), (50.6, 15.4), (53.6, 14.0), (56.8, 14.6), (59.6, 12.8), (61.8, 15.6),
            (64.8, 16.4), (67.4, 18.8), (69.6, 21.6), (71.4, 25.2), (72.6, 29.4), (73.2, 34.0), (73.0, 39.0), (72.2, 44.0), (71.2, 48.4), (70.0, 52.0)]
def _hy(y): return round(y + (31 - y) * .2, 2) if y < 31 else y     # lower the crown: short hair, not tall
HAIR_OUT = [(x, _hy(y)) for x, y in HAIR_OUT]
HAIR_IN = [(70.0, 52.0), (69.8, 47.6), (69.2, 43.0), (68.2, 39.6), (66.6, 36.6), (64.6, 34.6), (62.4, 35.6), (60.6, 35.0), (58.4, 36.6),
           (56.0, 36.0), (53.4, 37.2), (50.8, 36.6), (48.4, 37.8), (46.2, 37.4), (44.0, 38.6), (42.4, 37.2), (40.6, 36.0), (38.4, 35.6),
           (36.2, 36.4), (34.0, 38.0), (32.2, 40.8), (31.0, 44.4), (30.4, 48.2), (30.0, 52.0)]
HAIR_LINES = ('M41.6 36.6 C40.2 31.4 42.0 25.6 46.4 21.4 M48.2 36.6 C47.2 30.6 49.4 24.4 54.0 19.4 M55.0 36.4 C54.6 30.8 57.0 25.4 61.0 21.4 '
              'M61.6 35.6 C61.8 31.4 63.6 28.0 66.8 25.6 M35.6 36.4 C34.2 32.0 35.4 27.6 38.6 24.4 M44.6 25.6 C45.6 22.4 47.6 20.0 50.4 18.4')
HAIR_LINES = re.sub(r'(-?\d+\.?\d*) (-?\d+\.?\d*)', lambda m: f'{float(m.group(1)):.1f} {_hy(float(m.group(2))):.1f}', HAIR_LINES)
FLY = 'M58.0 17.4 Q59.8 14.4 63.0 14.6 M53.0 17.8 Q54.4 15.8 56.6 15.6'

LIDS = 'M37.4 50.4 Q41.8 47.8 46.4 50.0 M53.6 50.0 Q58.2 47.8 62.6 50.4'
CROW = ('M36.0 51.0 q-1.6 -.4 -2.7 -1.3 M36.2 52.8 q-1.6 .3 -2.8 .1 '
        'M64.0 51.0 q1.6 -.4 2.7 -1.3 M63.8 52.8 q1.6 .3 2.8 .1')
UNDER = 'M38.4 53.0 Q42 55.2 45.6 53.0 M54.4 53.0 Q58 55.2 61.6 53.0'          # cheeks pushing up into the eyes
CHEEKS = 'M37.6 56.0 Q41.6 58.0 45.4 56.2 M54.6 56.2 Q58.4 58.0 62.4 56.0'
NOSE = ('M53.2 55.2 Q53.8 57.2 54.0 59.0 '
        'M46.6 59.2 Q43.2 59.8 43.2 62.2 Q43.6 64.2 46.6 63.8 '
        'M53.4 59.2 Q56.8 59.8 56.8 62.2 Q56.4 64.2 53.4 63.8 '
        'M47.2 64.6 Q50 66.0 52.8 64.6')
FOLDS = ('M43.2 63.8 Q38.2 65.0 37.2 69.0 Q36.8 72.0 38.6 74.4 '
         'M56.8 63.6 Q61.8 64.6 62.8 68.6 Q63.2 71.6 61.4 74.0 '
         'M45.6 78.6 Q50 79.8 54.4 78.6')
DCHIN = 'M42.0 84.6 Q50 87.6 58.0 84.6'                                        # soft double chin under the stubble

BROWS = {
    'neutral': 'M35.2 46.6 Q40.6 45.6 46.4 47.0 M53.6 47.0 Q59.4 45.6 64.8 46.6',
    'focus':   'M35.4 45.6 Q40.8 45.4 46.4 48.2 M53.6 48.2 Q59.2 45.4 64.6 45.6',
    'up':      'M35.2 44.6 Q40.6 43.4 46.4 44.6 M53.6 44.6 Q59.4 43.4 64.8 44.6',
    'sad':     'M35.4 47.6 Q40.8 47.2 46.4 45.0 M53.6 45.0 Q59.2 47.2 64.6 47.6',
    'happy':   'M35.2 45.8 Q40.6 44.6 46.4 45.8 M53.6 45.8 Q59.4 44.6 64.8 45.8',
}
MOUTH = {k: (scale_mouth(d, 1.0, 1.0, 69.0, 70.0), f) for k, (d, f) in NEIL_MOUTH.items()}
MOUTH['rest'] = ('M41.6 66.8 Q50 68.4 58.8 65.8 Q57.2 73.2 50 73.4 Q43.0 73.2 41.6 66.8Z', 'url(#avTe)')   # wide, upper teeth, right corner lifted
MOUTH['closed'] = ('M42.4 69.4 Q50 72.2 58.0 68.6', 'none')
MOUTH['grin'] = ('M38.8 65.8 Q50 68.6 61.4 64.8 Q59.6 77.6 50 78.0 Q40.6 77.6 38.8 65.8Z', 'url(#avGr)')
MOUTH = {k: MOUTH[k] for k in NEIL_MOUTH}

# ------------------------------------------------------------------ hat (navy cap, curved brim, red button + stitching, no text/logo)
CROWN = [(28.8, 39.6), (28.4, 31.6), (32.4, 24.2), (39.6, 19.6), (50.0, 18.2), (60.4, 19.4), (67.8, 24.0), (71.8, 31.0), (71.4, 39.2)]
SEAM_D = 'M28.8 39.6 Q50 34.4 71.4 39.2'
BRIM_D = 'M28.8 39.6 Q50 34.4 71.4 39.2 Q75.2 39.4 75.0 40.8 C68 41.4 58 41.6 50 41.7 C43 41.6 35 41.4 28.6 40.8 Q27.8 40.0 28.8 39.6Z'
STITCH = 'M30.8 40.2 C37 40.6 44 40.7 50 40.7 C57 40.7 65 40.5 72.8 40.3'
CAP_SEAMS = 'M50.0 18.6 Q50.8 27 50.4 36.8 M39.8 20.4 Q35.8 28 35.0 38.0 M60.2 20.2 Q64.4 27.8 65.0 37.8'
BUTTON = 'M48.5 18.4 Q50 16.2 51.5 18.4'
HL_OUT = [(28.8, 40.2), (27.6, 44.4), (28.6, 48.6), (30.0, 52.0)]
HL_IN = [(30.0, 52.0), (30.4, 48.2), (31.2, 44.4), (32.8, 41.8)]
HR_OUT = [(71.4, 39.8), (72.4, 44.4), (71.4, 48.6), (70.0, 52.0)]
HR_IN = [(70.0, 52.0), (69.6, 48.2), (68.8, 44.4), (67.2, 42.0)]

FACE_D, FACE_POLY = cr(FACE_PTS, True)
JAW_D, _ = cr(JAW_PTS)
EAR_L_D, EAR_L_POLY = cr(EAR_L_PTS); EAR_R_D, EAR_R_POLY = cr(EAR_R_PTS)
EAR_IN_D = ' '.join(cr(p)[0] for p in [EAR_IN_L, mirror(EAR_IN_L), EAR_IN_L2, mirror(EAR_IN_L2)])
HO_D, HO_POLY = cr(HAIR_OUT); HI_D, HI_POLY = cr(HAIR_IN, t=.8)
HAIR_D = HO_D + ' L' + HI_D[1:] + 'Z'; HAIR_POLY = np.vstack([HO_POLY, HI_POLY])
HAIRLINE_D = cr(HAIR_IN[2:-2], t=.8)[0]
CROWN_D = cr(CROWN)[0] + ' Q50 34.4 28.8 39.6Z'

def hat_hair():
    lo, lop = cr(HL_OUT); li, lip = cr(HL_IN); ro, rop = cr(HR_OUT); ri, rip = cr(HR_IN)
    d = lo + ' L' + li[1:] + 'Z ' + ro + ' L' + ri[1:] + 'Z'
    return d, [np.vstack([lop, lip]), np.vstack([rop, rip])], lo + ' ' + ro, li + ' ' + ri

# ------------------------------------------------------------------ texture bake
rnd = random.Random(23)
def flow(x, y):
    if y > 37 and (x < 33.5 or x > 66.5): dx, dy = (x - 50) * .015, -1     # short grey sides: combed up and back
    else: dx, dy = (x - 50) * .1 + .35, -1                                  # top: swept up from the hairline, back and to the right
    L = math.hypot(dx, dy); return dx / L, dy / L

def hair_strands(poly, n=1.0, bbox=(26, 12, 74, 53), grey_only=False):
    if grey_only:
        L = [(H_D, .4, int(30 * n), (2, 4), (.4, .8), 0), (H_G, .8, int(40 * n), (2, 4), (.4, .8), 0),
             (H_GL, .85, int(40 * n), (1.6, 3.4), (.3, .6), 0), (H_W, .8, int(25 * n), (1.4, 3), (.3, .5), 0)]
        F = [(H_W, .6, .28, int(60 * n), (1.2, 2.6)), (H_DD, .3, .28, int(40 * n), (1.2, 2.6))]
        return strands(rnd, poly, flow, L, F, bbox)
    L = [(H_DD, .5, 50, (3.5, 6.5), (.7, 1.3), 0), (H_D, .6, 50, (3.5, 6), (.8, 1.4), 0), (H_M, .75, 50, (3, 5.5), (.8, 1.3), 0),
         ('#8f8378', .75, 40, (3, 5), (.6, 1.1), 0),
         (H_G, .85, 55, (2.4, 4.6), (.5, 1.0), 3), (H_GL, .85, 50, (2, 4), (.4, .8), 3), (H_W, .85, 30, (1.6, 3.2), (.3, .6), 4)]
    F = [(H_DD, .3, .3, 60, (1.4, 3)), ('#a39689', .45, .28, 45, (1.4, 3))]
    def acc(bias, x, y, r):
        side = (x < 35 or x > 65) and y > 29
        if bias == 3: return side or r.random() < .3      # grey: sides/temples + salt through the top
        if bias == 4: return side or r.random() < .12
        return not side or r.random() < .25
    out = strands(rnd, poly, flow, L, F, bbox, acc)
    for bb in ((26, 30, 34.4, 53), (65.6, 30, 74, 53)):      # grey-white sides and temples
        out += '\n' + strands(rnd, poly, flow, [(H_GL, .9, 40, (1.8, 3.6), (.4, .8), 0), (H_W, .9, 30, (1.4, 3), (.3, .6), 0), (H_D, .35, 12, (2, 3.4), (.3, .6), 0)],
                               [(H_W, .7, .28, 40, (1.2, 2.4))], bb)
    return out

LIPCUT = 'M43.0 69.4 Q50 67.4 57.4 68.6 Q50 73.0 43.0 69.4Z'
def stubble():
    """light grey-white stubble, fairly dense: jaw, chin, under the chin edge and the moustache"""
    FP = FACE_POLY.astype(np.float32); out_l = []; out_d = []
    def dens(x, y):
        ax = abs(x - 50); d = 0
        top = 61.5 + max(0, 12 - ax) * .32            # beard line: high at the sides, dips around the nose/mouth
        if y > top: d = .62 + min(.3, (y - top) * .04)
        if 64.4 < y < 66.6 and ax < 10: d = .75       # moustache
        if 67.2 <= y < 72.4 and ax < 7.6 - max(0, y - 70.6) * 1.6: d = 0      # lips
        if 73.6 <= y < 76.0 and ax < 7: d = .45        # soul patch area, lighter
        return d
    for _ in range(24000):
        x = rnd.uniform(29, 71); y = rnd.uniform(58, 84)
        if rnd.random() > dens(x, y) or not inside(FP, x, y): continue
        r = rnd.uniform(.06, .12)
        (out_l if rnd.random() < .8 else out_d).append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill-opacity="{rnd.uniform(.35, .8):.2f}"/>')
    return f'<g fill="{STUB_L}">' + ''.join(out_l) + f'</g><g fill="{STUB_D}">' + ''.join(out_d) + '</g>'

# beard zone (haze): follows the new jaw; high at the sides, around the nose, lips cut out
BEARD_D = ('M28 61 Q33 62.4 37.4 64.2 Q42 66.0 44.4 64.4 Q50 63.2 55.6 64.4 Q58 66.0 62.6 64.2 Q67 62.4 72 61 L72 90 L28 90Z ' + LIPCUT)

def face_shading(fringe_shadow=True, brim_shadow=False):
    S1, S2, HI, FL = rgb(SKIN_S1), rgb(SKIN_S2), rgb(SKIN_HI), rgb(FLUSH)
    return f'''<g clip-path="url(#cf)">
 <path d="{JAW_D}" fill="none" stroke="{S2}" stroke-width="5" opacity=".34" filter="url(#b2)"/>
 <ellipse cx="68.4" cy="60" rx="3.6" ry="14" fill="{S1}" opacity=".3" filter="url(#b2)"/>
 {f'<path d="{HAIRLINE_D}" fill="none" stroke="#b86a50" stroke-width="2.6" opacity=".4" filter="url(#b1)"/>' if fringe_shadow else ''}
 {'<path d="M28 40 Q50 36 72 40 L72 44 Q50 45.6 28 44Z" fill="#6a2c22" opacity=".32" filter="url(#b1)"/>' if brim_shadow else ''}
 <ellipse cx="48" cy="41.4" rx="9" ry="2.4" fill="{HI}" opacity=".4" filter="url(#b1)"/>
 <ellipse cx="42" cy="50.4" rx="5.2" ry="2.4" fill="{S2}" opacity=".32" filter="url(#b1)"/>
 <ellipse cx="58" cy="50.4" rx="5.2" ry="2.4" fill="{S2}" opacity=".36" filter="url(#b1)"/>
 <ellipse cx="46.8" cy="50.4" rx="1.8" ry="1.5" fill="{S2}" opacity=".45" filter="url(#b05)"/>
 <ellipse cx="53.2" cy="50.4" rx="1.8" ry="1.5" fill="{S2}" opacity=".5" filter="url(#b05)"/>
 <ellipse cx="39" cy="58.6" rx="4.6" ry="2.6" fill="{HI}" opacity=".6" filter="url(#b1)"/>
 <ellipse cx="61" cy="58.6" rx="4.4" ry="2.5" fill="{HI}" opacity=".45" filter="url(#b1)"/>
 <ellipse cx="37.2" cy="60.2" rx="5.6" ry="3.8" fill="{FL}" opacity=".42" filter="url(#b2)"/>
 <ellipse cx="62.8" cy="60.2" rx="5.6" ry="3.8" fill="{FL}" opacity=".42" filter="url(#b2)"/>
 <ellipse cx="50" cy="61.6" rx="3.6" ry="2.4" fill="{FL}" opacity=".4" filter="url(#b1)"/>
 <path d="M53.4 54.4 Q54.2 57.6 54.4 60.4" stroke="{S1}" stroke-width="2.4" fill="none" opacity=".55" filter="url(#b05)"/>
 <path d="M50.4 53.4 Q50.6 57.6 50.6 60.4" stroke="{HI}" stroke-width="1.8" fill="none" opacity=".6" filter="url(#b05)"/>
 <ellipse cx="49.6" cy="61.6" rx="2.4" ry="1.5" fill="#fff4ea" opacity=".55" filter="url(#b05)"/>
 <ellipse cx="50" cy="65.4" rx="4.4" ry="1" fill="{S2}" opacity=".5" filter="url(#b05)"/>
 <path d="M44.2 64 Q39.4 65.4 38.6 69.4 M55.8 63.8 Q60.6 65 61.4 69" stroke="{S1}" stroke-width="2.6" fill="none" opacity=".45" filter="url(#b05)"/>
 <path d="M42.2 62.4 Q36.6 63.6 35.8 67.8 M57.8 62.2 Q63.4 63.4 64.2 67.6" stroke="{HI}" stroke-width="2" fill="none" opacity=".45" filter="url(#b05)"/>
 <path d="M31 73 Q34 79 40 81.6 M69 73 Q66 79 60 81.6" stroke="{S2}" stroke-width="2.4" fill="none" opacity=".35" filter="url(#b1)"/>
 <path d="{BEARD_D}" fill="#e9e3dc" opacity=".55" fill-rule="evenodd" filter="url(#b1)"/>
 <path d="{BEARD_D}" fill="#8a7a70" opacity=".1" fill-rule="evenodd" filter="url(#b05)"/>
 <path d="{LIPCUT}" fill="#c9726a" opacity=".3" filter="url(#b05)"/>
 <ellipse cx="50" cy="76.4" rx="5" ry="1" fill="{S2}" opacity=".35" filter="url(#b05)"/>
 <ellipse cx="50" cy="80.2" rx="5" ry="1.6" fill="#ffffff" opacity=".25" filter="url(#b05)"/>
 {stubble()}
</g>'''

def bake_svg(hat):
    skin = du(T + 's_skin.png')
    if not hat:
        clip_hair = f'<clipPath id="ch"><path d="{HAIR_D}"/></clipPath>'
        hair = f'''<path d="{HAIR_D}" fill="url(#ghair)"/>
<g clip-path="url(#ch)" fill="none" stroke-linecap="round">
 <path d="{HAIRLINE_D}" stroke="{H_DD}" stroke-width="2.2" opacity=".45" filter="url(#b05)"/>
 <ellipse cx="29.4" cy="43" rx="3.8" ry="11" fill="{H_GL}" opacity=".85" filter="url(#b1)"/>
 <ellipse cx="70.6" cy="43" rx="3.8" ry="11" fill="{H_G}" opacity=".85" filter="url(#b1)"/>
 <ellipse cx="49" cy="25" rx="13" ry="4.4" fill="#a3978c" opacity=".45" filter="url(#b2)"/>
 {hair_strands(HAIR_POLY)}
</g>'''
        return _bake_wrap(skin, clip_hair, face_shading(True), hair, '')
    hd, hpolys, _, _ = hat_hair()
    clip_hair = f'<clipPath id="ch"><path d="{hd}"/></clipPath><clipPath id="cc"><path d="{CROWN_D}"/></clipPath>'
    hair = f'''<path d="{hd}" fill="{H_G}"/>
<g clip-path="url(#ch)" fill="none" stroke-linecap="round">
 {hair_strands(np.vstack(hpolys), 1.0, (27, 39, 74, 54), grey_only=True)}
</g>'''
    cap = f'''<path d="{CROWN_D}" fill="#27324d"/>
<g clip-path="url(#cc)">
 <ellipse cx="43" cy="24" rx="11" ry="5" fill="#5a6a90" opacity=".45" filter="url(#b2)"/>
 <path d="M28 30 Q29 41 33 40 M72 28 Q72 41 67 40" stroke="#0e1424" stroke-width="5" fill="none" opacity=".5" filter="url(#b2)"/>
 <path d="{SEAM_D}" stroke="#0e1424" stroke-width="2" fill="none" opacity=".5" filter="url(#b05)"/>
 <circle cx="44.6" cy="26.4" r=".55" fill="#c8413a"/><circle cx="56.2" cy="26.6" r=".55" fill="#c8413a"/>
</g>
<path d="{BRIM_D}" fill="url(#gbrim)"/>
<ellipse cx="50" cy="17.6" rx="1.7" ry="1.2" fill="#c8413a"/>'''
    return _bake_wrap(skin, clip_hair, face_shading(False, True), hair, cap)

def _bake_wrap(skin, clip_hair, face, hair, cap):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{' '.join(map(str, BOX))}">
<defs>
 {BAKE_DEFS}
 <clipPath id="cf"><path d="{FACE_D}"/></clipPath>
 {clip_hair}
 <linearGradient id="ghair" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{H_BASE[0]}"/><stop offset=".5" stop-color="{H_BASE[1]}"/><stop offset="1" stop-color="{H_BASE[2]}"/></linearGradient>
 <linearGradient id="gbrim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34426a"/><stop offset=".55" stop-color="#3f4f7c"/><stop offset="1" stop-color="#2a3555"/></linearGradient>
</defs>
<image href="{skin}" x="0" y="0" width="100" height="100"/>
<path d="M{EAR_L_D[1:]} M{EAR_R_D[1:]}" fill="none" stroke="{rgb(SKIN_S2)}" stroke-width="1.6" opacity=".4" filter="url(#b05)"/>
{face}
{hair}
{cap}
</svg>'''

# ------------------------------------------------------------------ final svg
DEFS = '''<radialGradient id="avIris" fx=".4" fy=".36"><stop offset=".08" stop-color="#fff"/><stop offset=".13" stop-color="#1a120e"/><stop offset=".42" stop-color="#1a120e"/><stop offset=".56" stop-color="#6a4530"/><stop offset=".8" stop-color="#8d5f3e"/><stop offset="1" stop-color="#2a1a12"/></radialGradient>
<linearGradient id="avTe" x2="0" y2="1"><stop offset=".64" stop-color="#fffaf0"/><stop offset=".74" stop-color="#7a2e2a"/></linearGradient>
<linearGradient id="avGr" x2="0" y2="1"><stop offset=".42" stop-color="#fffaf0"/><stop offset=".5" stop-color="#4a1b1b"/><stop offset=".74" stop-color="#4a1b1b"/><stop offset=".86" stop-color="#c8564d"/></linearGradient>
<linearGradient id="avMo" x2="0" y2="1"><stop offset=".22" stop-color="#fffaf0"/><stop offset=".28" stop-color="#4a1b1b"/><stop offset=".7" stop-color="#4a1b1b"/><stop offset=".8" stop-color="#c8564d"/></linearGradient>'''
BODY = f'''<path d="M5 104 Q7 89.6 29 86.6 Q40 85.6 50 85.6 Q60 85.6 71 86.6 Q93 89.6 95 104Z" fill="#26324a" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
<path d="M40.4 72 L40.0 89.6 Q50 94 60.0 89.6 L59.6 72Z" fill="#d48a6a" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M39.8 87.6 Q50 93.6 60.2 87.6 L62.4 90.8 Q50 97.4 37.6 90.8Z" fill="#80858c" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>
<path d="M35.2 86.0 Q37.2 95.8 50 97.4 Q62.8 95.8 64.8 86.0 Q68.2 86.4 70 88.8 Q66 100.6 50 101.6 Q34 100.6 30 88.8 Q31.8 86.4 35.2 86.0Z" fill="#33405e" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'''

def head_inner(hat):
    m = MOUTH['rest']
    eyes = (f'<g id="avEyes" transform="translate(0 {EYE_DY}) translate(0 54) scale(1 {EYE_S}) translate(0 -54)">'
            f'<ellipse id="avEyeL" cx="42" cy="54" rx="2.2" ry="2.9" fill="url(#avIris)"/><ellipse id="avEyeR" cx="58" cy="54" rx="2.2" ry="2.9" fill="url(#avIris)"/></g>')
    feats = f'''<path d="{FOLDS} {DCHIN}" fill="none" stroke="{LINE}" stroke-width="1.3" stroke-linecap="round" opacity=".6"/>
<path d="{CROW}" fill="none" stroke="#7b3f30" stroke-width="1" stroke-linecap="round" opacity=".5"/>
<path d="{UNDER}" fill="none" stroke="#6e3428" stroke-width="1.1" stroke-linecap="round" opacity=".6"/>
{eyes}
<path d="{LIDS}" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>
<path d="{NOSE}" fill="none" stroke="{INK}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path id="avBrows" d="{BROWS['neutral']}" fill="none" stroke="{BROW}" stroke-width="3" stroke-linecap="round"/>'''
    tail = f'''<path id="avMouth" d="{m[0]}" fill="{m[1]}" stroke="{INK}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/>
<path id="avSweat" d="{'M66.8 43.4 q2.6 4.4 0 6.2 q-2.6 -1.8 0 -6.2z' if hat else 'M66.8 37.2 q2.6 4.4 0 6.2 q-2.6 -1.8 0 -6.2z'}" fill="#8fd3ff" stroke="{INK}" stroke-width="1.4" opacity="0"/>'''
    ear_in = f'<path d="{EAR_IN_D}" fill="none" stroke="{INK}" stroke-width="1" stroke-linecap="round" opacity=".4"/>'
    if not hat:
        return f'''<path d="{EAR_L_D} {EAR_R_D} {JAW_D} {HO_D}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{HAIRLINE_D}" fill="none" stroke="{INK}" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
{ear_in}
<path d="{HAIR_LINES}" fill="none" stroke="{H_DD}" stroke-width=".9" stroke-linecap="round" opacity=".7"/>
<path d="{FLY}" fill="none" stroke="{INK}" stroke-width="1.4" stroke-linecap="round"/>
{feats}
{tail}'''
    _, _, ink_out, ink_in = hat_hair()
    return f'''<path d="{EAR_L_D} {EAR_R_D} {JAW_D} {ink_out}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{ink_in}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
{ear_in}
{feats}
<path d="{cr(CROWN)[0]} {BRIM_D} {BUTTON}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{CAP_SEAMS}" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round" opacity=".75"/>
<path d="{STITCH}" fill="none" stroke="#d8433c" stroke-width=".7" stroke-dasharray="1 .8" stroke-linecap="round"/>
{tail}'''

def build():
    w0, L = cwarp.warp('s_group.jpg', PPU=8, CX=50); cv2.imwrite(T + 'warp_s.png', w0)
    mid = (L[1][0] + L[152][0]) / 2; cx = 50 - (mid - 50)
    feat = [(cx - 8, 51.4, 4.8, 2.4), (cx + 8, 51.4, 4.8, 2.4), (cx - 8.6, 47.2, 6.6, 2.0), (cx + 8.6, 47.2, 6.6, 2.0), (50, 69, 9.6, 3.6)]
    keep = [(42, 51.5, 6.2, 3.6), (58, 51.5, 6.2, 3.6), (50, 69, 12, 4.8)]
    photo_skin('s_group.jpg', cx, FACE_POLY, [EAR_L_POLY, EAR_R_POLY], feat, keep, SKIN, FLUSH, T + 's_skin.png',
               lowk=.55, detk=.35, flushk=.45, flush_excl=[(50, 69, 10, 4)])
    res = {}
    for hat in (False, True):
        tag = 's_hat' if hat else 's'
        webp = bake(bake_svg(hat), tag, BOX, tppu=int(os.environ.get('TPPU', 5)), q=int(os.environ.get('Q', 74)))
        svg = avatar_svg(DEFS, BODY, head_inner(hat), webp, BOX, HEAD_DY)
        open(OUTD + ('avatar-hat.svg' if hat else 'avatar.svg'), 'w').write(svg)
        trace_overlay(svg, T + 'warp_s.png', T + f'trace_{tag}.svg')
        res[tag] = dict(webp=len(webp), **stats(svg))
    open(OUTD + 'av-presets.js', 'w').write(presets_js('Sean', MOUTH, BROWS,
        'Face: eyes 42/58 at y=51 (static #avEyes transform, squinty smile), mouth ~y66-74, chin ~y82; rest = big toothy smile.'))
    json.dump({'MOUTH': MOUTH, 'BROWS': BROWS}, open(T + 'sean_presets.json', 'w'))
    print(json.dumps(res))

if __name__ == '__main__':
    build()
