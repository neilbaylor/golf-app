#!/bin/bash
# tools/build.sh <name> [only=patch1,patch2]  -> out/<name>/sg.html (patched fresh copy of base.html) + out/<name>/w.html (instrumented)
set -e
cd /home/claude/golf/perfwork
mkdir -p out/$1
cp base.html out/$1/sg.html
python3 apply_perf.py out/$1/sg.html $2
python3 -c "
import re,sys;s=open('out/$1/sg.html').read();open('out/$1/chk.js','w').write(re.search(r'<script>(.*)</script>',s,re.S).group(1))"
node --check out/$1/chk.js && echo "syntax OK ($1)"
python3 tools/mkw.py out/$1/sg.html out/$1/w.html "$(cat tools/fns.txt),updateCull"
