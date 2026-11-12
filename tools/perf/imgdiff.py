#!/usr/bin/env python3
# python3 tools/imgdiff.py A_prefix B_prefix [diffDir]  -> per view: % pixels differing, max channel diff, mean abs diff
# Compares the deterministic WebGL canvas grabs (<prefix>_<view>.png) written by tools/views.js.
import sys, glob, os
import numpy as np
from PIL import Image
a, b = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else None
worst = 0
for fa in sorted(glob.glob(a + '_*.png')):
    v = fa[len(a) + 1:-4]
    if v.endswith('_page'): continue
    fb = b + '_' + v + '.png'
    if not os.path.exists(fb): print(f'{v:12s} missing in B'); continue
    A = np.asarray(Image.open(fa).convert('RGB')).astype(int); B = np.asarray(Image.open(fb).convert('RGB')).astype(int)
    if A.shape != B.shape: print(f'{v:12s} size differs {A.shape} {B.shape}'); worst = 999; continue
    d = np.abs(A - B); px = (d.max(axis=2) > 0).mean() * 100; mx = d.max(); worst = max(worst, mx)
    print(f'{v:12s} differing px {px:7.4f}%  max {mx:3d}  mean {d.mean():.5f}  >8: {(d.max(axis=2) > 8).mean() * 100:.4f}%')
    if out and mx:
        os.makedirs(out, exist_ok=True); Image.fromarray((np.clip(d.max(axis=2) * 16, 0, 255)).astype(np.uint8)).save(f'{out}/diff_{v}.png')
print('WORST max channel diff:', worst)
