"""Sherbo (50s/60s, long silver-blonde hair, clear champagne glasses, white goatee) — sticker-book avatar in Neil's style,
two versions: no hat / brown woven-straw trilby. Geometry traced over sherbo_front_smile.jpg (+ the close-up and the
B&W hat photo) warped into the 100-unit frame (eyes 42/58, y=51).
Differences from Sean's structure: no ears (long hair covers them); glasses + a second, small baked WebP of the
moustache's lower edge drawn just after #avMouth so every mouth shape tucks under the moustache."""
import math, random, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from avlib import *

WHO = 'sherbo'; OUTD = CREW + 'sherbo/'; os.makedirs(OUTD, exist_ok=True)
BOX = (17, 12, 66, 80)
EYE_DY = -3; EYE_S = .7; HEAD_DY = -1.5
TPPU = int(os.environ.get('TPPU', 5))

# ------------------------------------------------------------------ palette
SKIN = (240, 172, 150); SKIN_HI = (253, 210, 190); SKIN_S1 = (224, 144, 122); SKIN_S2 = (194, 110, 94)
FLUSH = (228, 98, 96)
H_BASE = ('#cfc9be', '#dcd7cc', '#e6e1d4')        # silver -> pale silver-blonde ends
H_DD = '#5a5048'; H_D = '#81776c'; H_M = '#a59c90'; H_G = '#c6bfb3'; H_L = '#e4dfd3'; H_W = '#f7f5ef'; H_B = '#e6d9b8'
BROW = '#8d7d70'; LINE = '#9a4c3c'
B_W = '#f3f1ec'; B_L = '#dedad3'; B_G = '#b4aea6'; B_D = '#7d756d'; B_DD = '#4b433d'
FRAME = '#ecd3c2'; FRAME_HI = '#fff6ee'; FRAME_SH = '#c8988a'
STRAW = '#95643a'; STRAW_L = '#c39360'; STRAW_D = '#5f3c20'; BAND = '#3b2418'; STRIPE = '#dcc196'

# ------------------------------------------------------------------ geometry (head-local units)
# face skin (mostly hidden at the sides by hair, the chin by the beard)
_F = [(31.6, 47), (31.6, 54), (32.2, 61), (33.4, 67), (35.6, 72), (38.8, 76.6), (43.2, 79.6), (50, 80.6)]
FACE_PTS = [(32.2, 40)] + _F + mirror(_F[-2::-1]) + [(67.8, 40), (66.2, 31.4), (50, 26.2), (33.8, 31.4)]

# long straight hair: swept back off a high, receding forehead from a part at ~x40, falling to the jaw on both sides
_TL = [(37.4, 79.0), (35.8, 81.6), (33.8, 79.8), (31.8, 82.4), (29.6, 80.0), (27.4, 82.0), (25.2, 79.4), (23.2, 80.8)]     # left tips (inner -> outer)
_TR = [(77.0, 80.4), (75.0, 79.2), (72.8, 81.8), (70.6, 79.6), (68.4, 82.0), (66.4, 79.8), (64.4, 81.2), (62.8, 78.8)]       # right tips (outer -> inner)
HAIR_OUT = _TL + [(23.8, 76.4), (24.8, 71.2), (25.9, 65.2), (26.8, 58.8), (27.6, 52), (28.4, 46), (29.4, 40.4), (30.8, 35.2), (32.8, 30.4),
                  (35.6, 26.2), (39.0, 22.8), (43.0, 20.4), (47.4, 18.9), (52.2, 18.3), (56.6, 18.7), (60.8, 20.0), (64.6, 22.4),
                  (67.8, 25.8), (70.2, 30.2), (71.6, 35.6), (72.4, 41.6), (72.8, 48), (73.3, 55), (74.2, 61.6), (75.2, 68.0), (76.4, 74.4)] + _TR
HAIR_IN = [(62.8, 78.8), (64.6, 74.2), (64.8, 70.2), (66.4, 64.4), (67.4, 58), (67.9, 51), (67.7, 44.6), (66.8, 39.2), (65.0, 34.6), (62.4, 31.2),
           (58.8, 29.0), (54.6, 28.1), (50.2, 28.0), (46.2, 28.6), (42.8, 29.8), (40.4, 31.2), (38.2, 33.4), (36.0, 36.8), (34.4, 41.0),
           (33.4, 46), (32.9, 52), (33.0, 58), (33.6, 64), (34.8, 69.6), (36.2, 74.4), (37.4, 79.0)]
HAIR_LINES = ('M40.6 31.0 C41.0 26.4 44.0 22.6 48.6 20.4 M45.6 29.0 C46.6 25.0 50.0 21.6 55.0 19.8 M52.4 28.2 C53.8 24.8 57.2 22.2 61.4 21.6 '
              'M59.6 29.6 C61.6 27.0 64.6 25.6 67.4 26.4 M38.0 32.6 C36.0 30.6 35.6 28.0 37.0 25.6 '
              'M69.0 34.8 C70.2 38 70.6 40.4 70.4 43.6 ')
HAIR_LINES_SIDE = 'M30.8 44 C30.0 52 29.2 64 27.6 77.4 M70.0 42 C70.8 50 71.6 62 72.8 77.2 M33.4 60 C33.0 68 32.6 74 31.4 79.6 M66.8 60 C67.2 68 67.6 74 68.8 79.8'
_hy = lambda y: round(y + (30 - y) * .3, 2) if y < 30 else y        # a flatter crown: thin, swept-back hair on top, not a helmet
HAIR_OUT = [(x, _hy(y)) for x, y in HAIR_OUT]
HAIR_LINES = ptrans(HAIR_LINES, lambda x, y: (x, _hy(y)), lambda dx, dy: (dx, dy * .7))
HAIR_LINES += HAIR_LINES_SIDE
FLY_SIDE = 'M24.4 73.4 Q21.4 76.8 21.8 80.6 M76.0 70.8 Q79.0 74.4 78.2 78.4'
FLY = ptrans('M55.0 18.6 Q58.4 16.4 62.2 17.6 M64.6 22.4 Q67.4 21.0 69.6 22.6 ', lambda x, y: (x, _hy(y))) + FLY_SIDE

# glasses: thick, square-ish clear acetate (champagne-pink)
def _rrect(x0, y0, x1, y1, r, top_flat=0.0):
    """rounded-rect path, slightly upswept outer top corner handled by caller via mirror"""
    return (f'M{x0 + r:.2f} {y0:.2f} L{x1 - r:.2f} {y0 + top_flat:.2f} Q{x1:.2f} {y0 + top_flat:.2f} {x1:.2f} {y0 + r + top_flat:.2f} '
            f'L{x1 - .3:.2f} {y1 - r:.2f} Q{x1 - .3:.2f} {y1:.2f} {x1 - r - .3:.2f} {y1:.2f} L{x0 + r + .3:.2f} {y1:.2f} '
            f'Q{x0 + .3:.2f} {y1:.2f} {x0 + .3:.2f} {y1 - r:.2f} L{x0:.2f} {y0 + r:.2f} Q{x0:.2f} {y0:.2f} {x0 + r:.2f} {y0:.2f}Z')
G_OUT_L = 'M31.4 46.2 C36 45.6 43 45.6 47.8 46.4 Q48.6 46.6 48.6 47.6 L48.4 55.4 Q48.2 58.4 45.2 58.6 L35.2 58.6 Q32.2 58.4 31.8 55.4 L30.8 48.0 Q30.6 46.4 31.4 46.2Z'
G_IN_L = 'M33.6 48.0 C37.4 47.6 42.6 47.6 46.4 48.2 Q47.1 48.4 47.0 49.2 L46.8 55.0 Q46.6 57.0 44.6 57.1 L35.8 57.1 Q33.6 57.0 33.3 55.0 L32.7 49.4 Q32.6 48.1 33.6 48.0Z'
G_OUT_R = mirror_d(G_OUT_L); G_IN_R = mirror_d(G_IN_L)
G_BRIDGE = 'M48.4 48.2 Q50 47.0 51.6 48.2 L51.6 50.2 Q50 49.2 48.4 50.2Z'
G_TEMPLES = 'M30.9 47.0 L28.6 47.4 L28.6 49.0 L31.1 48.8Z M69.1 47.0 L71.4 47.4 L71.4 49.0 L68.9 48.8Z'
G_GLARE = 'M34.6 49.4 L36.6 48.6 L34.2 54.0 L33.8 53.2Z M37.6 48.6 L38.4 48.6 L35.6 55.6 L35.2 55.2Z M61.6 48.6 L63.6 48.6 L61.0 55.0 L60.2 54.6Z'
G_FRAME_D = f'{G_OUT_L} {G_IN_L} {G_OUT_R} {G_IN_R}'

LIDS = 'M37.6 50.0 Q42 47.8 46.2 49.8 M53.8 49.8 Q58 47.8 62.4 50.0'
UNDER = 'M38.8 53.6 Q42 55.4 45.2 53.6 M54.8 53.6 Q58 55.4 61.2 53.6'
CROW = 'M33.4 59.6 Q35.4 61.2 38.0 61.4 M66.6 59.6 Q64.6 61.2 62.0 61.4'
FORE = 'M40.4 34.8 Q45 33.6 49.6 34.4 Q54.4 33.4 59.6 34.6 M42.4 38.4 Q47 37.4 50.4 38.0 Q54 37.2 57.8 38.2 M45.6 41.4 Q49.6 40.8 53.6 41.4'
NOSE = ('M52.6 50.6 Q53.6 55.0 54.0 58.8 '
        'M46.6 59.2 Q43.0 59.8 43.0 62.2 Q43.4 64.0 46.4 63.8 '
        'M53.4 59.2 Q57.0 59.8 57.0 62.2 Q56.6 64.0 53.6 63.8 '
        'M47.0 64.2 Q50 65.4 53.0 64.2')
FOLDS = 'M42.2 61.8 Q38.4 63.0 37.2 66.4 M57.8 61.8 Q61.6 63.0 62.8 66.4'

# beard: moustache + goatee joined into a full chin beard that hangs below the jaw
BEARD_PTS = [(39.0, 66.4), (40.4, 64.4), (43.2, 63.5), (46.4, 63.3), (48.6, 63.8), (50, 63.5), (51.4, 63.8), (53.6, 63.3), (56.8, 63.5),
             (59.6, 64.4), (61.0, 66.4), (61.8, 69.2), (62.8, 72.0), (63.2, 75.0), (62.6, 79.0), (60.8, 83.0), (57.8, 86.8), (54.0, 89.6),
             (50, 90.6), (46.0, 89.6), (42.2, 86.8), (39.2, 83.0), (37.4, 79.0), (36.8, 75.0), (37.2, 72.0), (38.2, 69.2)]   # long white goatee down over the collar
LIP = 'M42.2 67.9 Q50 69.0 57.8 67.9 Q55.2 71.6 50 71.8 Q44.8 71.6 42.2 67.9Z'
MB = 'M39.6 67.8 Q50 68.8 60.4 67.8'                            # moustache's bottom edge (top of the lip)

BROWS = {
    'neutral': 'M34.8 43.8 Q40.4 42.2 46.0 43.4 M54.0 43.4 Q59.6 42.2 65.2 43.8',
    'focus':   'M35.0 42.6 Q40.6 42.4 46.0 44.2 M54.0 44.2 Q59.4 42.4 65.0 42.6',
    'up':      'M34.8 42.4 Q40.4 40.6 46.0 41.8 M54.0 41.8 Q59.6 40.6 65.2 42.4',
    'sad':     'M35.0 44.2 Q40.6 43.8 46.0 41.8 M54.0 41.8 Q59.4 43.8 65.0 44.2',
    'happy':   'M34.8 43.0 Q40.4 41.2 46.0 42.4 M54.0 42.4 Q59.6 41.2 65.2 43.0',
}
MOUTH = {k: (scale_mouth(d, .9, .95, 68.5, 68.9), f) for k, (d, f) in NEIL_MOUTH.items()}
MOUTH['rest'] = ('M40.8 66.8 Q50 70.6 59.2 66.6 Q57.2 71.6 50 72.0 Q42.8 71.6 40.8 66.8Z', '#d9786f')   # big closed-mouth smile: the lower lip shows under the moustache
MOUTH['closed'] = ('M42.2 67.6 Q50 70.0 57.8 67.4 Q55.8 70.6 50 70.9 Q44.2 70.6 42.2 67.6Z', '#d9786f')
MOUTH['grin'] = ('M40.4 66.8 Q50 68.6 59.6 66.6 Q58.0 76.8 50 77.2 Q42.0 76.8 40.4 66.8Z', 'url(#avGr)')
MOUTH = {k: MOUTH[k] for k in NEIL_MOUTH}

# ------------------------------------------------------------------ hat: brown woven-straw trilby, short snap brim, dark band + light stripe
CROWN = [(31.0, 36.6), (31.6, 31.0), (33.0, 25.4), (35.4, 21.6), (40.2, 19.4), (45.6, 19.2), (50.0, 20.6), (54.4, 19.2), (59.8, 19.4),
         (64.6, 21.6), (67.0, 25.4), (68.4, 31.0), (69.0, 36.6)]
BRIM_TOP = 'M22.4 34.6 Q26.4 34.0 31.0 36.0 Q50 38.6 69.0 36.0 Q73.6 34.0 77.6 34.6'
BRIM_BOT = 'M77.6 34.6 C77.4 37.6 70.4 39.0 62.0 39.8 Q50 41.0 38.0 39.8 C29.6 39.0 22.6 37.6 22.4 34.6'
BRIM_D = BRIM_TOP + ' ' + BRIM_BOT[BRIM_BOT.index('C'):] + 'Z'
BAND_D = 'M31.4 30.8 Q50 33.0 68.6 30.8 L69.0 36.2 Q50 38.6 31.0 36.2Z'
STRIPE_D = 'M31.4 32.2 Q50 34.4 68.6 32.2'
PINCH = 'M45.2 19.6 Q46.6 22.4 46.2 25.6 M54.8 19.6 Q53.4 22.4 53.8 25.6'
HAT_CUT_Y = 39.8                                                 # hair ink below this (the brim covers the rest)

FACE_D, FACE_POLY = cr(FACE_PTS, True)
HO_D, HO_POLY = cr(HAIR_OUT); HI_D, HI_POLY = cr(HAIR_IN, t=.85)
HAIR_D = HO_D + ' L' + HI_D[1:] + 'Z'; HAIR_POLY = np.vstack([HO_POLY, HI_POLY])
HAIRLINE_D = cr(HAIR_IN[1:-1], t=.85)[0]
BEARD_D, BEARD_POLY = cr(BEARD_PTS, True)
CROWN_D = cr(CROWN)[0] + ' Q50 38.6 31.0 36.6Z'

def cut_poly(pts, y0):
    """the open sub-paths of a point list that lie below y0 (for hair ink under the brim)"""
    _, poly = cr(pts, t=.85); segs = []; cur = []
    for x, y in poly:
        if y >= y0: cur.append((x, y))
        elif cur: segs.append(cur); cur = []
    if cur: segs.append(cur)
    return ' '.join('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in s[::3] + [s[-1]]) for s in segs if len(s) > 3)

# ------------------------------------------------------------------ texture bake
rnd = random.Random(31)
def flow(x, y):
    if y > 40 or (y > 34 and (x < 33 or x > 67)):
        dx, dy = (x - 50) * .006, 1                                  # long straight sides
    else:
        dx, dy = x - 45, y - 47                                      # swept back: fans from the hairline up over the crown
    L = math.hypot(dx, dy); return dx / L, dy / L

def hair_strands(poly, n=1.0, bbox=(26, 17, 75, 79)):
    L = [(H_D, .55, int(55 * n), (3.5, 7), (.6, 1.2), 1), (H_M, .7, int(70 * n), (3.5, 7), (.6, 1.2), 0),
         (H_G, .8, int(80 * n), (3, 6), (.5, 1.0), 0), (H_B, .55, int(40 * n), (3, 6), (.5, 1.0), 2),
         (H_L, .85, int(80 * n), (2.6, 5.4), (.4, .9), 0), (H_W, .9, int(60 * n), (2, 4.4), (.3, .6), 0)]
    F = [(H_DD, .35, .28, int(70 * n), (1.8, 3.6)), (H_W, .7, .26, int(90 * n), (1.8, 3.6)), (H_D, .4, .26, int(50 * n), (1.8, 3.6))]
    def acc(bias, x, y, r):
        if bias == 1: return (y < 31 and 46 < x < 66) or r.random() < .35    # darker grey-brown streaks toward the crown
        if bias == 2: return y > 46 or r.random() < .2                         # blonde tint in the lengths
        return True
    return strands(rnd, poly, flow, L, F, bbox, acc)

def bflow(x, y):
    if y < 68.4:
        dx, dy = (x - 50) * .25, 1 + abs(x - 50) * .02               # moustache: from the philtrum down and out
    else:
        dx, dy = (50 - x) * .05, 1                                   # chin beard: down, converging to the point
    L = math.hypot(dx, dy); return dx / L, dy / L

def beard_strands():
    def acc(bias, x, y, r):
        ax = abs(x - 50)
        if bias == 1: return y < 68.4 or (y < 75 and (ax > 7 or y < 73)) or r.random() < .08     # salt-and-pepper moustache + around the mouth
        if bias == 2: return y > 72 or r.random() < .25                                          # white chin
        return True
    L = [(B_G, .8, 120, (1.4, 3.2), (.35, .7), 0), (B_D, .7, 120, (1.2, 2.8), (.3, .6), 1), (B_DD, .55, 70, (1, 2.4), (.25, .5), 1),
         (B_L, .9, 130, (1.6, 3.6), (.35, .7), 2), (B_W, .95, 120, (1.4, 3.2), (.3, .6), 2)]
    F = [(B_DD, .45, .22, 110, (1, 2.2)), (B_W, .85, .24, 140, (1.2, 2.6))]
    s = strands(rnd, BEARD_POLY, bflow, L, F, (36.5, 63, 63.5, 86.4), acc)
    # wispy edge hairs along the chin outline
    E = []
    for i in range(70):
        t = rnd.uniform(.08, .92); idx = int(t * (len(BEARD_POLY) - 1)); x, y = BEARD_POLY[idx]
        if y < 70: continue
        ux, uy = bflow(x, y); a = math.atan2(uy, ux) + rnd.gauss(0, .3); ln = rnd.uniform(.8, 1.8)
        E.append(f'M{x - math.cos(a) * ln:.2f} {y - math.sin(a) * ln:.2f} l{math.cos(a) * ln * 1.6:.2f} {math.sin(a) * ln * 1.6:.2f}')
    s += f'\n<path d="{" ".join(E)}" stroke="{B_W}" stroke-width=".3" stroke-linecap="round" fill="none" opacity=".9"/>'
    return s

BEARD_STR = None
def beard_group():
    global BEARD_STR
    if BEARD_STR is None: BEARD_STR = beard_strands()
    return f'''<g>
 <path d="{BEARD_D}" fill="{B_L}"/>
 <g clip-path="url(#cb)">
  <path d="M36 64 Q50 61.6 64 64 L64 70 Q50 68 36 70Z" fill="{B_G}" opacity=".85" filter="url(#b05)"/>
  <ellipse cx="50" cy="80" rx="10" ry="5.4" fill="{B_W}" opacity=".9" filter="url(#b1)"/>
  <path d="M38.6 67 Q37.6 72 39.4 75.6 M61.4 67 Q62.4 72 60.6 75.6" stroke="{B_D}" stroke-width="2.2" fill="none" opacity=".55" filter="url(#b05)"/>
  <ellipse cx="50" cy="73.6" rx="3.2" ry="1.6" fill="{B_D}" opacity=".6" filter="url(#b05)"/>
  {BEARD_STR}
 </g>
 <path d="{LIP}" fill="#d0857c"/>
 <path d="M44 69.6 Q50 71.4 56 69.6" stroke="#e8a59a" stroke-width="1" fill="none" opacity=".7" filter="url(#b03)"/>
 <path d="{MB}" stroke="{B_DD}" stroke-width=".9" fill="none" opacity=".45" filter="url(#b03)"/>
</g>'''

def face_shading(hat=False):
    S1, S2, HI, FL = rgb(SKIN_S1), rgb(SKIN_S2), rgb(SKIN_HI), rgb(FLUSH)
    return f'''<g clip-path="url(#cf)">
 <path d="{cr(_F)[0]} M{100 - _F[0][0]} {_F[0][1]} {cr(mirror(_F))[0][1:]}" fill="none" stroke="{S2}" stroke-width="5" opacity=".3" filter="url(#b2)"/>
 {'' if hat else f'<path d="{HAIRLINE_D}" fill="none" stroke="#b9705a" stroke-width="2.6" opacity=".35" filter="url(#b1)"/>'}
 {'<path d="M28 36 Q50 39 72 36 L72 42 Q50 45.6 28 42Z" fill="#6a2c22" opacity=".34" filter="url(#b1)"/>' if hat else ''}
 <ellipse cx="50" cy="32" rx="9" ry="3.2" fill="{HI}" opacity=".45" filter="url(#b2)"/>
 <ellipse cx="42" cy="50.4" rx="5.2" ry="2.2" fill="{S2}" opacity=".3" filter="url(#b1)"/>
 <ellipse cx="58" cy="50.4" rx="5.2" ry="2.2" fill="{S2}" opacity=".32" filter="url(#b1)"/>
 <ellipse cx="47.6" cy="51" rx="1.6" ry="2.4" fill="{S2}" opacity=".4" filter="url(#b05)"/>
 <ellipse cx="52.4" cy="51" rx="1.6" ry="2.4" fill="{S2}" opacity=".45" filter="url(#b05)"/>
 <ellipse cx="38.6" cy="59.4" rx="4.6" ry="2.6" fill="{FL}" opacity=".5" filter="url(#b2)"/>
 <ellipse cx="61.4" cy="59.4" rx="4.6" ry="2.6" fill="{FL}" opacity=".5" filter="url(#b2)"/>
 <ellipse cx="38.4" cy="57.8" rx="3.2" ry="1.4" fill="{HI}" opacity=".45" filter="url(#b1)"/>
 <ellipse cx="50" cy="61" rx="4.4" ry="3" fill="{FL}" opacity=".55" filter="url(#b1)"/>
 <path d="M53.0 52 Q54.0 56.6 54.4 60" stroke="{S1}" stroke-width="2.2" fill="none" opacity=".5" filter="url(#b05)"/>
 <path d="M50.4 50.4 Q50.6 55.6 50.6 59.6" stroke="{HI}" stroke-width="1.8" fill="none" opacity=".55" filter="url(#b05)"/>
 <ellipse cx="49.4" cy="61" rx="2.2" ry="1.5" fill="#fff4ea" opacity=".6" filter="url(#b05)"/>
 <ellipse cx="50" cy="64.2" rx="4.6" ry="1" fill="{S2}" opacity=".5" filter="url(#b05)"/>
 <path d="M43.2 62.6 Q39 63.6 37.8 67.2 M56.8 62.6 Q61 63.6 62.2 67.2" stroke="{S1}" stroke-width="2.4" fill="none" opacity=".45" filter="url(#b05)"/>
 <path d="{BEARD_D}" fill="{S2}" opacity=".35" filter="url(#b1)" transform="translate(0 .6)"/>
</g>'''

def weave(clip_id, region, rows, rot=0.0):
    """woven straw: little alternating diagonal stitches in rows, light/dark"""
    x0, y0, x1, y1 = region; dl = []; dd = []; dm = []
    y = y0; r = 0
    while y < y1:
        x = x0 + (r % 2) * .55
        while x < x1:
            s = 1 if (r + int((x - x0) / 1.1)) % 2 else -1
            d = f'M{x:.2f} {y - s * .3:.2f} l.8 {s * .6:.2f}'
            k = rnd.random(); (dl if k < .42 else dd if k < .7 else dm).append(d)
            x += 1.1
        y += rows; r += 1
    return (f'<g clip-path="url(#{clip_id})" fill="none" stroke-linecap="round">'
            f'<path d="{" ".join(dl)}" stroke="{STRAW_L}" stroke-width=".55" opacity=".85"/>'
            f'<path d="{" ".join(dm)}" stroke="#b07c4a" stroke-width=".55" opacity=".8"/>'
            f'<path d="{" ".join(dd)}" stroke="{STRAW_D}" stroke-width=".45" opacity=".7"/></g>')

def hat_svg():
    return f'''<path d="{CROWN_D}" fill="{STRAW}"/>
{weave('cc', (30, 18, 70, 37), .85)}
<g clip-path="url(#cc)">
 <ellipse cx="43" cy="24" rx="9" ry="4.4" fill="#e2b98a" opacity=".35" filter="url(#b2)"/>
 <path d="M31 22 Q31.4 34 34 36 M69 22 Q68.6 34 66 36" stroke="#3a2010" stroke-width="4.4" fill="none" opacity=".45" filter="url(#b2)"/>
 <path d="{PINCH}" stroke="#3a2010" stroke-width="1.8" fill="none" opacity=".35" filter="url(#b05)"/>
 <path d="{BAND_D}" fill="{BAND}"/>
 <path d="{STRIPE_D}" stroke="{STRIPE}" stroke-width=".7" fill="none"/>
 <path d="M31.4 34.4 Q50 36.8 68.6 34.4" stroke="#5a3a26" stroke-width=".9" fill="none" opacity=".6"/>
</g>
<path d="{BRIM_D}" fill="{STRAW}"/>
<clipPath id="cbr"><path d="{BRIM_D}"/></clipPath>
{weave('cbr', (21, 33, 79, 42), .75)}
<g clip-path="url(#cbr)">
 <path d="M24 36.4 Q50 41.6 76 36.4 L78 42 L22 42Z" fill="#4a2a14" opacity=".35" filter="url(#b05)"/>
 <path d="{BRIM_TOP}" stroke="#3a2010" stroke-width="1.6" fill="none" opacity=".5" filter="url(#b05)"/>
 <ellipse cx="36" cy="36.4" rx="7" ry="1.2" fill="#e8c497" opacity=".35" filter="url(#b05)"/>
</g>'''

def bake_svg(hat):
    skin = du(T + 'sb_skin.png')
    hair = f'''<path d="{HAIR_D}" fill="url(#ghair)"/>
<g clip-path="url(#ch)" fill="none" stroke-linecap="round">
 <path d="{HAIRLINE_D}" stroke="{H_D}" stroke-width="2" opacity=".4" filter="url(#b05)"/>
 <ellipse cx="57" cy="24" rx="8" ry="4" fill="{H_D}" opacity=".35" filter="url(#b2)"/>
 <ellipse cx="44" cy="23" rx="7" ry="2.6" fill="{H_W}" opacity=".6" filter="url(#b2)"/>
 <path d="M30 42 Q29.4 58 31 74 M70 40 Q71.4 58 70 74" stroke="{H_W}" stroke-width="2.4" opacity=".55" filter="url(#b1)"/>
 <path d="M32.6 44 Q32 58 34 72 M67.6 42 Q68 58 66 72" stroke="{H_D}" stroke-width="1.6" opacity=".35" filter="url(#b1)"/>
 {HAIR_STR}
</g>'''
    if hat:
        hair = f'<g clip-path="url(#chat)">{hair}</g>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{' '.join(map(str, BOX))}">
<defs>
 {BAKE_DEFS}
 <clipPath id="cf"><path d="{FACE_D}"/></clipPath>
 <clipPath id="ch"><path d="{HAIR_D}"/></clipPath>
 <clipPath id="cb"><path d="{BEARD_D}"/></clipPath>
 <clipPath id="cc"><path d="{CROWN_D}"/></clipPath>
 <clipPath id="chat"><path d="M0 38.4 Q50 41 100 38.4 V100 H0Z"/></clipPath>
 <linearGradient id="ghair" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{H_BASE[0]}"/><stop offset=".5" stop-color="{H_BASE[1]}"/><stop offset="1" stop-color="{H_BASE[2]}"/></linearGradient>
</defs>
<image href="{skin}" x="0" y="0" width="100" height="100"/>
{face_shading(hat)}
{beard_group()}
{hair}
{hat_svg() if hat else ''}
</svg>'''

# moustache overlay: the moustache's lower part, baked on the same pixel grid, drawn after #avMouth
MO_BOX = (37, 64, 26, 7)
def moustache_svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{' '.join(map(str, MO_BOX))}">
<defs>
 {BAKE_DEFS}
 <clipPath id="cb"><path d="{BEARD_D}"/></clipPath>
 <clipPath id="cm"><path d="M30 60 H70 V69.6 L60.4 68.0 Q50 69.4 39.6 68.0 L30 69.6Z"/></clipPath>
 <linearGradient id="gm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".3" stop-color="#fff"/></linearGradient>
 <mask id="mm" maskUnits="userSpaceOnUse" x="37" y="64" width="26" height="7"><rect x="37" y="64" width="26" height="7" fill="url(#gm)"/></mask>
</defs>
<g mask="url(#mm)"><g clip-path="url(#cm)">{beard_group()}</g></g>
</svg>'''

# ------------------------------------------------------------------ final svg
DEFS = '''<radialGradient id="avIris" fx=".4" fy=".36"><stop offset=".08" stop-color="#fff"/><stop offset=".13" stop-color="#182019"/><stop offset=".4" stop-color="#182019"/><stop offset=".52" stop-color="#58775f"/><stop offset=".8" stop-color="#8ea894"/><stop offset="1" stop-color="#26352a"/></radialGradient>
<linearGradient id="avTe" x2="0" y2="1"><stop offset=".64" stop-color="#fffaf0"/><stop offset=".74" stop-color="#7a2e2a"/></linearGradient>
<linearGradient id="avGr" x2="0" y2="1"><stop offset=".4" stop-color="#fffaf0"/><stop offset=".48" stop-color="#4a1b1b"/><stop offset=".74" stop-color="#4a1b1b"/><stop offset=".86" stop-color="#c8564d"/></linearGradient>
<linearGradient id="avMo" x2="0" y2="1"><stop offset=".22" stop-color="#fffaf0"/><stop offset=".28" stop-color="#4a1b1b"/><stop offset=".7" stop-color="#4a1b1b"/><stop offset=".8" stop-color="#c8564d"/></linearGradient>'''
BODY = f'''<path d="M5 104 Q7 89.6 29 86.6 Q40 85.6 50 85.6 Q60 85.6 71 86.6 Q93 89.6 95 104Z" fill="#7d8087" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>
<path d="M40.6 72 L40.2 88.6 Q50 93 59.8 88.6 L59.4 72Z" fill="#d88d76" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M36.6 86.4 Q50 88.4 63.4 86.4 L55.2 104 L44.8 104Z" fill="#eef2f7" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M39.8 85.6 L34.2 88.4 L41.4 96.6 L46.4 89.8Z M60.2 85.6 L65.8 88.4 L58.6 96.6 L53.6 89.8Z" fill="#ffffff" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>
<path d="M33.4 88.6 L27.2 90.6 L38.6 104 M66.6 88.6 L72.8 90.6 L61.4 104" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
<path d="M20 95 l1.2 .8 M25 99 l1 -.6 M76 96 l-1 .8 M80 99.6 l1 .6 M14 99 l1.2 .4 M86 99 l-1 .6" stroke="#5c6067" stroke-width="1" stroke-linecap="round"/>'''

SWEAT = 'M64.2 58.6 q2.6 4.4 0 6.2 q-2.6 -1.8 0 -6.2z'
def head_inner(hat, mo_href):
    m = MOUTH['rest']
    eyes = (f'<g id="avEyes" transform="translate(0 {EYE_DY}) translate(0 54) scale(1 {EYE_S}) translate(0 -54)">'
            f'<ellipse id="avEyeL" cx="42" cy="54" rx="2.3" ry="2.9" fill="url(#avIris)"/><ellipse id="avEyeR" cx="58" cy="54" rx="2.3" ry="2.9" fill="url(#avIris)"/></g>')
    glasses = f'''<path d="{G_FRAME_D} {G_BRIDGE}" fill="{FRAME}" fill-rule="evenodd" opacity=".93"/>
<path d="M32.4 47.2 C37 46.6 43 46.6 47.4 47.3 M52.6 47.3 C57 46.6 63 46.6 67.6 47.2" fill="none" stroke="{FRAME_HI}" stroke-width=".7" stroke-linecap="round" opacity=".9"/>
<path d="M34.6 57.9 L45 57.9 M55 57.9 L65.4 57.9" fill="none" stroke="{FRAME_SH}" stroke-width=".8" stroke-linecap="round" opacity=".8"/>
<path d="{G_GLARE}" fill="#ffffff" opacity=".35"/>
<path d="{G_OUT_L} {G_OUT_R} {G_BRIDGE} {G_TEMPLES}" fill="none" stroke="{INK}" stroke-width="1.15" stroke-linejoin="round"/>
<path d="{G_IN_L} {G_IN_R}" fill="none" stroke="{INK}" stroke-width=".85" stroke-linejoin="round" opacity=".85"/>'''
    feats = f'''<path d="{FORE}" fill="none" stroke="{LINE}" stroke-width=".95" stroke-linecap="round" opacity="{'0' if hat else '.42'}"/>
<path d="{FOLDS}" fill="none" stroke="{LINE}" stroke-width="1.2" stroke-linecap="round" opacity=".55"/>
<path d="{CROW}" fill="none" stroke="#7b3f30" stroke-width=".9" stroke-linecap="round" opacity=".45"/>
<path d="{UNDER}" fill="none" stroke="#6e3428" stroke-width="1" stroke-linecap="round" opacity=".55"/>
{eyes}
<path d="{LIDS}" fill="none" stroke="{INK}" stroke-width="1.8" stroke-linecap="round"/>
<path d="{NOSE}" fill="none" stroke="{INK}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
{glasses}
<path id="avBrows" d="{BROWS['neutral']}" fill="none" stroke="{BROW}" stroke-width="2.1" stroke-linecap="round"/>'''
    beard_ink = cr(BEARD_PTS[11:-1])[0]
    tail = f'''<path id="avMouth" d="{m[0]}" fill="{m[1]}" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<image href="{mo_href}" x="{MO_BOX[0]}" y="{MO_BOX[1]}" width="{MO_BOX[2]}" height="{MO_BOX[3]}"/>
<path id="avSweat" d="{SWEAT}" fill="#8fd3ff" stroke="{INK}" stroke-width="1.4" opacity="0"/>'''
    beard = f'<path d="{beard_ink}" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    if not hat:
        return f'''<path d="{HO_D}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{HAIRLINE_D}" fill="none" stroke="{INK}" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{HAIR_LINES}" fill="none" stroke="{H_D}" stroke-width=".8" stroke-linecap="round" opacity=".75"/>
<path d="{FLY}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-linecap="round"/>
{beard}
{feats}
{tail}'''
    ink_out = cut_poly(HAIR_OUT, HAT_CUT_Y); ink_in = cut_poly(HAIR_IN, HAT_CUT_Y + 1.2)
    return f'''<path d="{ink_out}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{ink_in}" fill="none" stroke="{INK}" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{HAIR_LINES_SIDE}" fill="none" stroke="{H_D}" stroke-width=".8" stroke-linecap="round" opacity=".75"/>
<path d="{FLY_SIDE}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-linecap="round"/>
{beard}
{feats}
<path d="{cr(CROWN)[0]} {BRIM_D}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{BAND_D} {PINCH}" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>
{tail}'''

HAIR_STR = None
def build():
    global HAIR_STR
    w0, L = cwarp.warp('sb_front.jpg', PPU=8, CX=50); cv2.imwrite(T + 'warp_sb.png', w0)
    mid = (L[1][0] + L[152][0]) / 2; cx = 50 - (mid - 50)
    feat = [(cx - 8, 51.2, 5, 2.4), (cx + 8, 51.2, 5, 2.4), (cx - 8.6, 44, 6.6, 2.0), (cx + 8.6, 44, 6.6, 2.0), (50, 67.6, 10, 3.6)]
    keep = [(40, 52.4, 10.6, 7.4), (60, 52.4, 10.6, 7.4), (50, 70, 12, 6)]
    photo_skin('sb_front.jpg', cx, FACE_POLY, [], feat, keep, SKIN, FLUSH, T + 'sb_skin.png',
               lowk=.5, detk=.3, flushk=.45, flush_excl=[(40, 52.4, 9, 6), (60, 52.4, 9, 6), (50, 70, 10, 4)])
    HAIR_STR = hair_strands(HAIR_POLY)
    mo = bake(moustache_svg(), 'sb_mo', MO_BOX, tppu=TPPU * 2, q=82, alpha_q=70)
    mo_href = 'data:image/webp;base64,' + base64.b64encode(mo).decode()
    res = {'mo_webp': len(mo)}
    for hat in (False, True):
        tag = 'sb_hat' if hat else 'sb'
        webp = bake(bake_svg(hat), tag, BOX, tppu=TPPU, q=int(os.environ.get('Q', 74)))
        svg = avatar_svg(DEFS, BODY, head_inner(hat, mo_href), webp, BOX, HEAD_DY)
        open(OUTD + ('avatar-hat.svg' if hat else 'avatar.svg'), 'w').write(svg)
        trace_overlay(svg, T + 'warp_sb.png', T + f'trace_{tag}.svg')
        res[tag] = dict(webp=len(webp), **stats(svg))
    open(OUTD + 'av-presets.js', 'w').write(presets_js('Sherbo', MOUTH, BROWS,
        'Face: eyes 42/58 at y=51 (static #avEyes transform) behind clear glasses, brows above the frame (~y43), mouth ~y67-77 tucked '
        'under the moustache overlay image, beard to ~y86; rest = big closed-mouth smile.'))
    json.dump({'MOUTH': MOUTH, 'BROWS': BROWS}, open(T + 'sherbo_presets.json', 'w'))
    print(json.dumps(res))

if __name__ == '__main__':
    build()
