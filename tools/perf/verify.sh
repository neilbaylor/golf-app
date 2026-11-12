#!/bin/bash
# Final check: fresh copy of base.html -> apply_perf.py -> syntax check -> full play flow (page errors) + view grabs vs base.
cd /home/claude/golf/perfwork
mkdir -p out/final
cp base.html out/final/sketchy-golf.html
python3 apply_perf.py out/final/sketchy-golf.html || exit 1
python3 -c "
import re;s=open('out/final/sketchy-golf.html').read();open('out/final/chk.js','w').write(re.search(r'<script>(.*)</script>',s,re.S).group(1))"
node --check out/final/chk.js && echo "syntax OK"
# plain wrap (exactly the shipped code, no instrumentation) for the error check
python3 -c "s=open('out/final/sketchy-golf.html').read(); open('out/final/wrapped.html','w').write('<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>'+s+'</body></html>')"
python3 tools/mkw.py out/final/sketchy-golf.html out/final/w.html "$(cat tools/fns.txt),updateCull"
node tools/plainflow.js out/final/wrapped.html > out/final/plainflow.log 2>&1; cat out/final/plainflow.log
node tools/flow.js out/final/w.html out/final/flow.json > out/final/flow.log 2>&1; node tools/analyze.js out/final/flow.json > out/final/flow_an.log 2>&1; cat out/final/flow.log
node tools/views.js out/final/w.html out/final/v > out/final/views.log 2>&1; cat out/final/views.log
python3 tools/imgdiff.py out/b2/v out/final/v out/final/diff
mkdir -p screens
python3 tools/montage.py out/b2/v out/final/v screens/before_after_all_views.png
for v in tee tee-aim fairway-aim pitch sand putt putt-far; do cp out/b2/v_$v.png screens/before_$v.png; cp out/final/v_$v.png screens/after_$v.png; done
python3 tools/cmpviews.py out/b2/views.log out/final/views.log
