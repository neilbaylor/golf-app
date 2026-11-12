#!/usr/bin/env python3
# python3 tools/cmpviews.py A/views.log B/views.log -> per view: JS ms/frame and real frame interval, before -> after
import sys, json
def load(p):
    d = {}
    for l in open(p):
        parts = l.split(None, 1)
        if len(parts) == 2 and parts[1].startswith('{'):
            d[parts[0]] = json.loads(parts[1])
    return d
A, B = load(sys.argv[1]), load(sys.argv[2])
print(f"{'view':12s} {'JS ms/frame':>22s} {'real frame ms (SwiftShader)':>30s}  calls")
for k in A:
    if k not in B: continue
    a, b = A[k], B[k]
    print(f"{k:12s} {a['js']:8.2f} -> {b['js']:6.2f} ({(b['js'] - a['js']) / a['js'] * 100:+5.0f}%)   {a['realMs']:8.0f} -> {b['realMs']:6.0f}            {a['calls']} -> {b['calls']}")
