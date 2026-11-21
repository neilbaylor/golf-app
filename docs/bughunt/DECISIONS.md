# Decisions needed for the bug/perf PRs (#1–#18)

Also tracked in https://github.com/neilbaylor/golf-app/issues/14 (rounds 1–5) and in a comment on PR #1 (rounds 6–8). The token couldn't edit the issue any more.

## Needs Neil
- [ ] **#8 (perf: CPU-backed helper canvases).** About 6.5% of course-texture pixels change slightly at the edges of the grass, needle and fescue strokes. It looks the same side by side, but CLAUDE.md says perf work must not reduce graphics, so it needs Neil's sign-off and a phone check.
- [ ] **#6 (round card voice).** Even par: should it get the good-round lines (drop #6 and reword the "Under par" lines), or the OK-round lines (merge #6)?
- [ ] **#4 (MP tee honour).** Should a golfer who leaves also lose their turn after the tee, not just the honour order on the tee?
- [ ] **#12 (async shader compile).** OK to turn off three.js shader error reporting in production? There's no `?debug` flag today; a `?shaders` switch could be added.
- [x] **#15 / #18 (MP replay drift):** resolved. #18 fixes the remaining drift (0 of 30 replays off). Merge #18 after #5 and #15. Optional: keep #15 (it's still correct) or drop it.

- [ ] **#17 (free uploaded canvases):** fine as long as no WebGL context-restore path is planned. If one is, it must repaint these canvases (or set `TEX_FREE = false`).

## Before merging
- [ ] Phone check for the perf PRs measured only in headless Chromium + SwiftShader: #8, #11, #12 (`?prof` before and after).

## Porting
- **Need redoing in `sketchy-golf.html` plus a rebuild (new file name; don't edit the hashed file in place):** #1, #2, #5, #6, #8, #9, #11, #12, #13, #15, #17, #18.
- **Server-only, mergeable as they are:** #3, #4, #7, #10.
- Every PR applies to `main` on its own except #18, which needs #5 and #15 first. Otherwise the stack is only for review order.
