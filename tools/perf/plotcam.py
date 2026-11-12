#!/usr/bin/env python3
# python3 tools/plotcam.py out.png A/trans.json [B/trans.json]
# Camera speed (yd per 1/60 s) for position and look target across every transition segment, before (A) vs after (B).
# A velocity step shows up as a vertical jump in these curves; smooth eased moves are smooth humps.
import sys, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def load(p):
    R = json.load(open(p)); L = R['log']; marks = R['marks']
    segs = []
    for i, (name, a) in enumerate(marks):
        b = marks[i + 1][1] if i + 1 < len(marks) else len(L)
        if name == 'end' or b - a < 3: continue
        sp, lk = [], []
        for j in range(max(a, 1), b):
            p0, p1 = L[j - 1], L[j]
            sp.append(math.dist(p0[4:7], p1[4:7])); lk.append(math.dist(p0[7:10], p1[7:10]))
        segs.append((name, sp, lk))
    return segs

out = sys.argv[1]; A = load(sys.argv[2]); B = load(sys.argv[3]) if len(sys.argv) > 3 else None
bmap = {n: (s, l) for n, s, l in B} if B else {}
n = len(A); cols = 3; rows = math.ceil(n / cols)
fig, axs = plt.subplots(rows, cols, figsize=(cols * 4.2, rows * 2.4), squeeze=False)
for k, (name, sp, lk) in enumerate(A):
    ax = axs[k // cols][k % cols]
    ax.plot(sp, color='#2a6f97', lw=1.2, label='pos (before)'); ax.plot(lk, color='#c9a227', lw=1.0, label='look (before)')
    if name in bmap:
        s2, l2 = bmap[name]; ax.plot(s2, color='#2a6f97', lw=1.2, ls='--', label='pos (after)'); ax.plot(l2, color='#c9a227', lw=1.0, ls='--', label='look (after)')
    ax.set_title(name, fontsize=9); ax.tick_params(labelsize=7); ax.set_xlabel('frame (1/60 s)', fontsize=7); ax.set_ylabel('yd / frame', fontsize=7)
for k in range(n, rows * cols): axs[k // cols][k % cols].axis('off')
axs[0][0].legend(fontsize=6, loc='upper right')
fig.tight_layout(); fig.savefig(out, dpi=110)
print('wrote', out)
