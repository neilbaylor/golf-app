# Warp a reference crop into avatar units: iris centres -> (50-IPD/2,EY),(50+IPD/2,EY). Optional side compression (K/SL).
import json, numpy as np, cv2, sys, os
from PIL import Image, ImageDraw
W = '/home/claude/golf/avatar/crew/work/'
def load(name):
    D = json.load(open(W + 'fm/landmarks.json'))[name]; lm = np.array(D['lm'])[:, :2]
    im = cv2.imread(W + 'fm/' + name)
    irR, irL = lm[468], lm[473]; c = (irR + irL) / 2; v = irL - irR; ipd = np.linalg.norm(v); u = v / ipd; n = np.array([-u[1], u[0]])
    return im, lm, c, u, n, ipd
def warp(name, PPU=8, EY=51.0, IPD=16.0, K=9, SL=1, VS=1.0, CX=50.0):
    gi = lambda xp: np.sign(xp) * np.where(np.abs(xp) < K, np.abs(xp), K + (np.abs(xp) - K) / SL)
    g = lambda x: np.sign(x) * np.where(np.abs(x) < K, np.abs(x), K + (np.abs(x) - K) * SL)
    im, lm, c, u, n, ipd = load(name)
    N = 100 * PPU; X, Y = np.meshgrid((np.arange(N) + .5) / PPU, (np.arange(N) + .5) / PPU)
    xn = gi((X - CX) / IPD); yn = (Y - EY) / IPD / VS
    sx = c[0] + (xn * u[0] + yn * n[0]) * ipd; sy = c[1] + (xn * u[1] + yn * n[1]) * ipd
    out = cv2.remap(im, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    d = lm - c; xn = d @ u / ipd; yn = d @ n / ipd
    L = np.stack([CX + g(xn) * IPD, EY + yn * VS * IPD], 1)
    return out, L
def grid(out, PPU, path, pts=None):
    im = Image.fromarray(out[:, :, ::-1]); d = ImageDraw.Draw(im)
    for i in range(0, 101, 5):
        col = (255, 255, 0) if i % 10 == 0 else (90, 90, 90)
        d.line([(i * PPU, 0), (i * PPU, 100 * PPU)], fill=col, width=1); d.line([(0, i * PPU), (100 * PPU, i * PPU)], fill=col, width=1)
    for i in range(0, 101, 10): d.text((i * PPU + 2, 2), str(i), fill=(255, 255, 255)); d.text((2, i * PPU + 2), str(i), fill=(255, 255, 255))
    if pts is not None:
        for x, y in pts: d.ellipse([x * PPU - 2, y * PPU - 2, x * PPU + 2, y * PPU + 2], fill=(255, 0, 255))
    im.save(path)
NAMES = {'chin': 152, 'noseTip': 1, 'subnasale': 2, 'mL': 61, 'mR': 291, 'upLip': 0, 'lowLip': 17, 'jawR': 172, 'jawL': 397, 'cheekR': 234, 'cheekL': 454,
         'fore': 10, 'browInR': 107, 'browOutR': 70, 'browTopR': 105, 'alaR': 98, 'alaL': 327, 'eyeOutR': 33, 'eyeInR': 133, 'eyeTopR': 159, 'eyeBotR': 145,
         'jawR2': 136, 'jawL2': 365, 'chinR': 148, 'chinL': 377, 'temR': 127, 'temL': 356}
if __name__ == '__main__':
    for name in sys.argv[1:]:
        out, L = warp(name)
        idx = list(NAMES.values())
        grid(out, 8, W + 'out/warp_' + name.replace('.jpg', '.png'), [L[i] for i in idx])
        print(name, ' '.join(f'{k}={L[i][0]:.1f},{L[i][1]:.1f}' for k, i in NAMES.items()))
