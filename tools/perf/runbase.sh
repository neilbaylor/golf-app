#!/bin/bash
# sequential baseline runs (2 CPUs: never run two SwiftShader pages at once)
cd /home/claude/golf
while pgrep -f "tools/views.js perfwork/out/base" >/dev/null; do sleep 3; done
node perfwork/tools/dom.js perfwork/out/base/w.html perfwork/out/base/dom.json > perfwork/out/base/dom.log 2>&1
node perfwork/tools/ablate.js perfwork/out/base/w.html putt 3 > perfwork/out/base/ablate_putt.log 2>&1
node perfwork/tools/flow.js perfwork/out/base/w.html perfwork/out/base/flow.json > perfwork/out/base/flow.log 2>&1
node perfwork/tools/analyze.js perfwork/out/base/flow.json > perfwork/out/base/flow_an.log 2>&1
echo ALLDONE >> perfwork/out/base/dom.log
