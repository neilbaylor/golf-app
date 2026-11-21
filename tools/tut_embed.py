#!/usr/bin/env python3
"""Puts the tutorial hole's shapes (tools/tut_hole.py --no-h) into tutHoles() in the game file.
  python3 tools/tut_embed.py sketchy-golf.html"""
import subprocess, sys, os
p = sys.argv[1]; s = open(p).read()
J = subprocess.check_output([sys.executable, os.path.join(os.path.dirname(__file__), 'tut_hole.py'), '--no-h']).decode()
a = s.index('function tutHoles() {'); a = s.index('const J = ', a) + len('const J = '); b = s.index(', h = J[1], H = h.H', a)
s = s[:a] + J + s[b:]; open(p, 'w').write(s); print('tut hole:', len(J), 'bytes')
