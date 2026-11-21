# START HERE: bug/perf hunt hand-off (v496)

This replaces #16 (closed) as the entry point for the bug, perf and memory hunt on neilbaylor/golf-app (Tee Party). Current base: `main` @ 26836c8 (v496).

## Message for the main agent

**Where things stand**
- **#1–#13, #15, #17 and #18 are done.** They were ported into `sketchy-golf.html` and shipped in v473 (74c2a40); the server ones went in with 0b1b9a0. I checked again on v491 and v495, and all 18 fixes are in the live bundle (#12 with its `?shaders` switch). Nothing is left to do on them, and the decisions they needed (issue #14 and `DECISIONS.md` in #16) were settled when they merged.
- **New: #19 (Low).** Ghost line's see-through crown mesh had room for only 64 crowns. Any ghosted crown past the 64th vanished instead of going see-through, with no error. #19 sizes the mesh to what it has to draw. Today's courses don't reach 64 (the measured peak is 30, on Hunt 9), so this guards against bigger trees or denser woods.

**How to treat #19**
1. **Port it; don't merge the bundle edit.** It patches the built `game.7f098eaced.js`, because the real source, `sketchy-golf.html`, isn't in the repo. Redo the 2-line change in `sketchy-golf.html` (search for `GHOST_MAT, 64`) and rebuild with `tools/split_build.py`, which gives the file a new hashed name. Never edit a hashed file in place: it's cached forever, so phones would stay on the old code.
2. **One small decision** (below). The default is to take #19 as it is.
3. Like #1–#18, it has a description with proof, its test scripts, and a fresh-eyes review comment.

**Rounds on the merged build**
- **v491 (`main` @ 988472b), two rounds.** No new PRs:
  - All 18 ports were present.
  - Reviewed the tutorial (`TUTOR`), ghost line, `SHADER_WARM`, AIM_TILT, MODE_ON_DIAL / PUTT_TAB_OFF, MP_AUTO_VARY and the server's tee honours by score. No bugs:
    - The tutorial hole has no water or OB, so the gated drop screen can't come up.
    - MP_AUTO_VARY's randomness is sent with the shot, so replays still match.
    - `honourCmp` puts late joiners last and falls back to seat order.
  - Random play (`tests/randplay.js`): about 36 holes on Hunt 1–9, Augusta 1+ and Augusta 12, including 3 holes with water penalties. No page errors, no stuck states, and strokes = shots + penalties on every hole.
- **v492–v496 (`main` @ 26836c8).**
  - Read every changed line: the tutorial switches (TUT_READ, TUT_AIM_KEEP, TUT_PITCH_ONLY, TUT_FREE, TUT_NO_FRINGE, TUT_TO_COURSE, TUT_TG_TOP, TUT_ONE_TIP, the TUT_FADE sky dip) and the result card's DRIVE_TINT. No bugs:
    - The putt read's side vector and break direction are right.
    - TUT_TO_COURSE uses the existing `tp_round` `go` flag, which the boot already reads.
    - DRIVE_TINT only changes tee shots hit with less than a driver.
  - One edge case, dev-only and not a player bug: TUT_TO_COURSE sends someone whose saved course is the dev course `osler` to the Hunt. You can only get there through the secret dev hash.
  - Ghost-line overflow, found and fixed in #19. With every nearby crown forced to ghost, `main` drew 64 of 282 and 64 of 420 crowns; #19 draws all of them.
  - Random play on v496 + #19 (11 holes): clean.
- **Notes (not bugs):**
  - Ghost line costs about 0.44 ms per frame during an aim drag on Hunt 9.
  - Cold boot is still dominated by the swing-dial bake and the shader compiles that `renderer.compile` forces. Deferring either one just moves the cost into play as jank, so that's a product choice, left alone.
  - Every perf number comes from headless Chromium with SwiftShader. Confirm on real phones with `?prof`.

**If you find more:** add a PR, list it here, and record any decision on its PR and in the Decisions section below.

**Security:** the GitHub token used to open these PRs was pasted in chat. Revoke it.

## Decisions

### Open
- [ ] **#19 (ghost crowns):** grow the ghost mesh to fit (#19 as written, so every crown covering the tracer stays see-through), or keep a fixed budget of 64 and draw any overflow solid? Either way, crowns stop vanishing. Default: grow.

### Standing notes from earlier PRs
- **#17 (canvases freed after upload):** if a WebGL context-restore path is ever added, it has to repaint those canvases, or set `TEX_FREE = false`.
- **#8, #11, #12 (perf):** if they haven't been checked on an iPhone and an Android phone yet, compare `?prof` before and after.

### Settled
- #4, #6, #8, #12, #15/#18 and #17 were settled when they merged in v473 / 0b1b9a0.
