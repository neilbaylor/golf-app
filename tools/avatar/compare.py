"""side-by-side at the same scale (avatar units): warped photos | current avatar(s) | Neil, with a light 10-unit grid
usage: python3 compare.py out.png photo1.jpg[,CX] ... -- svg1 svg2 ..."""
import sys, os, cv2, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from avlib import render, T
import cwarp
args = sys.argv[2:]; k = args.index('--'); photos, svgs = args[:k], args[k + 1:]
PP = 8; X0, Y0, X1, Y1 = 18, 8, 82, 92
tiles = []
for p in photos:
    name, *cx = p.split(','); im, L = cwarp.warp(name, PPU=PP, CX=float(cx[0]) if cx else 50)
    tiles.append(Image.fromarray(im[:, :, ::-1]))
for i, s in enumerate(svgs):
    render(s, T + f'_c{i}.png', 100 * PP, 100 * PP); tiles.append(Image.open(T + f'_c{i}.png').convert('RGB'))
out = []
for t in tiles:
    t = t.crop((X0 * PP, Y0 * PP, X1 * PP, Y1 * PP)); d = ImageDraw.Draw(t)
    for v in range(20, 100, 10):
        d.line([((v - X0) * PP, 0), ((v - X0) * PP, t.height)], fill=(255, 255, 0), width=1)
        d.line([(0, (v - Y0) * PP), (t.width, (v - Y0) * PP)], fill=(255, 255, 0), width=1)
    out.append(t)
W = Image.new('RGB', (sum(t.width for t in out) + 6 * (len(out) - 1), out[0].height), 'white'); x = 0
for t in out: W.paste(t, (x, 0)); x += t.width + 6
W.thumbnail((2000, 2000)); W.save(sys.argv[1])
