#!/usr/bin/env python3
# python3 tools/montage.py BEFORE_prefix AFTER_prefix out.png
# Contact sheet: for each view, the WebGL frame before | after | |difference| x16 (black = identical), labelled.
import sys, glob, os
import numpy as np
from PIL import Image, ImageDraw
a, b, out = sys.argv[1], sys.argv[2], sys.argv[3]
views = [f[len(a) + 1:-4] for f in sorted(glob.glob(a + '_*.png')) if not f.endswith('_page.png')]
order = ['tee', 'tee-aim', 'fairway', 'fairway-aim', 'rough', 'pitch', 'sand', 'putt', 'putt-far']
views = [v for v in order if v in views] + [v for v in views if v not in order]
S = 0.5
rows = []
for v in views:
    A = Image.open(f'{a}_{v}.png').convert('RGB'); B = Image.open(f'{b}_{v}.png').convert('RGB')
    d = np.abs(np.asarray(A).astype(int) - np.asarray(B).astype(int)).max(axis=2)
    D = Image.fromarray(np.clip(d * 16, 0, 255).astype(np.uint8)).convert('RGB')
    w, h = int(A.width * S), int(A.height * S)
    row = Image.new('RGB', (w * 3 + 20, h + 28), 'white'); dr = ImageDraw.Draw(row)
    for i, im in enumerate([A, B, D]): row.paste(im.resize((w, h)), (i * (w + 10), 28))
    px = (d > 0).mean() * 100
    dr.text((4, 6), f'{v}: before | after | diff x16   differing pixels {px:.4f}%  max channel diff {d.max()}', fill='black')
    rows.append(row)
W = max(r.width for r in rows); H = sum(r.height for r in rows)
sheet = Image.new('RGB', (W, H), 'white'); y = 0
for r in rows: sheet.paste(r, (0, y)); y += r.height
sheet.save(out); print('wrote', out, sheet.size)
