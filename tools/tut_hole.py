#!/usr/bin/env python3
"""The tutorial hole: an invented par 4 (not a real course), written in the
Hunt builder's JSON shape so the game's data-hole code builds it like any other.

Short and wide, nothing in play: an open meadow with light rough either side
of the fairway, tall fescue and trees well back, one front bunker and a raised
green with a gentle tilt (so the tutorial putt breaks a little).

  python3 tools/tut_hole.py --no-h > /tmp/tut.json   (one line: {"1": {...}}; --no-h: leave the heights to the game)
Units are yards: u across (right +), v down the hole from the tee.
"""
import base64, json, math, random, struct, sys
NO_H = "--no-h" in sys.argv  # the game makes the heights itself (tutH, the same z() in JS): only the shapes go in the page

R = random.Random(20261121)
sm = lambda t: 0.0 if t <= 0 else 1.0 if t >= 1 else t * t * (3 - 2 * t)

# the hole line: a straight drive, then a gentle bend left to the green
CL = [[0.0, 0.0], [3.0, 190.0], [-9.0, 326.0]]
PIN = (-9.0, 326.0)


def cl_u(v):  # the line's u at v
    if v <= CL[1][1]:
        t = v / CL[1][1]; return CL[0][0] + (CL[1][0] - CL[0][0]) * t
    t = (v - CL[1][1]) / (CL[2][1] - CL[1][1]); return CL[1][0] + (CL[2][0] - CL[1][0]) * t


def wob(v, a, f, p):  # a slow organic wobble for an edge
    return a * math.sin(v / f + p) + a * .45 * math.sin(v / (f * .37) + p * 2.1)


# fairway: 50 to 300 yd, 36 wide in the landing zone, narrowing into the green
def fw_half(v):
    w = 18.0
    w -= 3.0 * sm((v - 245) / 50)  # in to the approach
    w -= 6.0 * (1 - sm((v - 50) / 30))  # rounded start
    return w


FV = [v for v in range(50, 303, 4)]
FWL = [[round(cl_u(v) - fw_half(v) + wob(v, 1.6, 23, .4), 1), v] for v in FV]
FWR = [[round(cl_u(v) + fw_half(v) + wob(v, 1.4, 19, 2.2), 1), v] for v in FV]
fair = FWL + FWR[::-1]

# green: an oval round the pin, a touch long front to back
GC = (PIN[0] - .6, PIN[1] + 1.5)
GRX, GRY, GROT = 13.5, 17.0, 0.12


def ell(cx, cy, rx, ry, rot, n, jit):
    out = []
    for i in range(n):
        a = i / n * 2 * math.pi; r = 1 + jit * math.sin(3 * a + .7) + jit * .6 * math.sin(5 * a + 2.0)
        x, y = rx * r * math.cos(a), ry * r * math.sin(a)
        out.append([round(cx + x * math.cos(rot) - y * math.sin(rot), 1), round(cy + x * math.sin(rot) + y * math.cos(rot), 1)])
    return out


green = ell(GC[0], GC[1], GRX, GRY, GROT, 36, .035)

# one front bunker, a kidney short-right of the green: the pitch goes over it
def kidney(cx, cy, w, h, rot, n=28):
    out = []
    for i in range(n):
        a = i / n * 2 * math.pi
        r = 1 - .22 * max(0, math.cos(a - math.pi / 2)) ** 2  # the dent on the green side
        x, y = w * r * math.cos(a), h * r * math.sin(a)
        out.append([round(cx + x * math.cos(rot) - y * math.sin(rot), 1), round(cy + x * math.sin(rot) + y * math.cos(rot), 1)])
    return out


BUNK_C = (-1.5, 304.5)
bunker = kidney(BUNK_C[0], BUNK_C[1], 9.5, 4.2, -.18)

# tee box
tee = [[-5.0, 6.0], [5.0, 6.0], [5.0, -6.0], [-5.0, -6.0]]

# a cart path down the right, well clear of play
def path_pts():
    pts = []
    for v in range(-14, 352, 8):
        u = 58 + 6 * math.sin(v / 70 + .5) - 14 * sm((v - 250) / 90)
        pts.append([round(u, 1), v])
    pts += [[30.0, 352.0], [12.0, 356.0]]
    return pts


paths = [path_pts()]

# fescue: tall meadow grass, well back from the fairway (out of play)
def blob(cx, cy, rx, ry, n=18):
    return [[round(cx + rx * (1 + .18 * math.sin(3 * a + cx)) * math.cos(a), 1), round(cy + ry * (1 + .14 * math.sin(4 * a + cy)) * math.sin(a), 1)]
            for a in [i / n * 2 * math.pi for i in range(n)]]


fescue = []  # long strips of tall grass along the corridor, 44+ yd out, broken into pieces
for side in (-1, 1):
    v = 30.0
    while v < 330:
        ln = R.uniform(30, 55); off = side * (46 + R.uniform(0, 8)); w = R.uniform(5, 8)
        pts = []
        for t in [i / 10 for i in range(11)]:
            vv = v + ln * t; pts.append([round(cl_u(vv) + off - side * w * .5 * math.sin(t * math.pi) + wob(vv, 1.2, 9, side), 1), round(vv, 1)])
        for t in [i / 10 for i in range(10, -1, -1)]:
            vv = v + ln * t; pts.append([round(cl_u(vv) + off + side * w * (.6 + .4 * math.sin(t * math.pi)) + wob(vv, 1.2, 11, side + 1), 1), round(vv, 1)])
        fescue.append(pts); v += ln + R.uniform(14, 30)
# trees: loose clumps far back (none in play), a few in blossom; a big pair behind the green frames it
TREES = []


def tree(u, v, r=None, h=None, bloom=None):
    t = {"u": round(u, 1), "v": round(v, 1), "r": round(r or R.uniform(4.2, 7.5), 1), "h": round(h or R.uniform(12, 19), 1),
         "lob": False, "lean": round(R.uniform(0, .035), 3), "leanA": round(R.uniform(0, 6.28), 2)}
    if bloom: t["bloom"] = bloom
    TREES.append(t)


for v in range(-34, 372, 8):  # a tree line both sides, 66+ yd out (a slice that far is a lost cause anyway), and a looser row behind it
    for side in (-1, 1):
        if R.random() < .22: continue
        tree(cl_u(v) + side * (66 + R.uniform(0, 14)), v + R.uniform(-3, 3), bloom=R.choice([None] * 6 + ["white", "yellow"]))
        if R.random() < .6: tree(cl_u(v) + side * (88 + R.uniform(0, 26)), v + R.uniform(-4, 4), r=R.uniform(5, 8.5), h=R.uniform(15, 22))
for u in range(-90, 80, 9):  # the backdrop behind the green
    tree(u + R.uniform(-3, 3), 370 + R.uniform(-4, 10) + .002 * u * u, r=R.uniform(5.5, 8.5), h=R.uniform(16, 23), bloom=R.choice([None] * 7 + ["white"]))
for (u, v, b) in [(-50, 118, "white"), (54, 206, None), (-52, 262, "yellow"), (50, 40, None)]:  # a few big specimen trees out in the meadow
    tree(u, v, r=R.uniform(8, 9.5), h=R.uniform(18, 22), bloom=b)
tree(-18, -26, 6.5, 15, "white"); tree(22, -30, 7, 16)  # behind the tee

# flowering bushes by the tee and round the back of the green
BC = ['pink', 'magenta', 'white', 'coral', 'blush', 'crimson']
BUSHES = [{"u": u, "v": v, "r": r, "c": c} for (u, v, r, c) in
          [(-12, -9, 1.8, 'pink'), (-15, -5, 1.4, 'coral'), (12, -10, 1.7, 'magenta'), (15, -6, 1.3, 'blush'),
           (-30, 345, 2.0, 'pink'), (-24, 349, 1.6, 'white'), (14, 346, 1.9, 'coral'), (20, 341, 1.5, 'crimson')]]

# heights (yards): a gentle valley, sides that rise into the meadow, a raised green
U0, V0, D, NU, NV = -150.0, -45.0, 2.0, 151, 226


def pip(x, y, P):
    c = False; j = len(P) - 1
    for i in range(len(P)):
        xi, yi = P[i]; xj, yj = P[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c


def ell_d(u, v):  # >1 outside the green's oval, <1 inside
    x, y = u - GC[0], v - GC[1]; c, s = math.cos(-GROT), math.sin(-GROT)
    xr, yr = x * c - y * s, x * s + y * c
    return math.hypot(xr / GRX, yr / GRY)


def z(u, v):
    off = u - cl_u(min(max(v, 0), 326))
    h = -1.3 * sm(v / 170) + 1.0 * sm((v - 190) / 130)  # down into the valley, up to the green
    h += min(4.0, .00055 * off * off)  # the meadow rises off the corridor
    k = .35 + .65 * sm((abs(off) - 22) / 25)  # calmer on the fairway
    h += k * (.42 * math.sin(u / 23 + v / 31) + .3 * math.sin(v / 17 - u / 41 + 1.1) + .18 * math.sin(u / 9.5 + v / 13))
    h += .7 * (1 - sm((math.hypot(u, v) - 8) / 7))  # the tee pad
    e = ell_d(u, v)
    lift = 1.15 * (1 - sm((e - 1.0) / .55))  # the raised green, falling away over ~7 yd
    h += lift
    if e < 1.3:  # its tilt: back-left high, so putts run toward the front right
        w = 1 - sm((e - 1.0) / .3)
        h += w * (-.018 * (u - GC[0]) + .016 * (v - GC[1]))
    # the bunker: a soft dish
    bx, by = u - BUNK_C[0], v - BUNK_C[1]
    bd = math.hypot(bx / 10.5, by / 5.2)
    h -= .55 * (1 - sm((bd - .6) / .6))
    return h


vals = []
for j in range(NV):
    for i in range(NU):
        vals.append(int(round(z(U0 + i * D, V0 + j * D) * 100)))
b64 = base64.b64encode(struct.pack('<%dh' % len(vals), *vals)).decode()

L = sum(math.hypot(CL[i][0] - CL[i - 1][0], CL[i][1] - CL[i - 1][1]) for i in range(1, len(CL)))
hole = {
    "HOLE": {"n": 1, "par": 4, "yds": int(L), "hcp": 1, "name": "Tutorial"},
    "CL": CL, "lenYds": round(L, 1), "PIN": {"u": PIN[0], "v": PIN[1]},
    "GREEN": {"c": [round(GC[0], 1), round(GC[1], 1)], "rx": GRX, "ry": GRY, "rot": GROT, "poly": green},
    "other_greens": [], "FWL": FWL, "FWR": FWR,
    "fairways": [{"own": True, "poly": fair}],
    "tees": [{"own": True, "used": True, "poly": tee}],
    "bunkers": [{"deep": False, "poly": bunker}],
    "water": [], "ob": [], "PINE": [], "BUSHES": BUSHES, "TREES": TREES, "paths": paths,
    "crop": {"U0": -120, "U1": 120, "V0": -20, "V1": 385},
    "H": {"u0": U0, "v0": V0, "d": D, "nu": NU, "nv": NV} if NO_H else {"u0": U0, "v0": V0, "d": D, "nu": NU, "nv": NV, "b64": b64},
    "FESCUE": fescue, "meta": {},
}
json.dump({"1": hole}, sys.stdout, separators=(',', ':'))
