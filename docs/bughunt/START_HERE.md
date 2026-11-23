# START HERE: bug/perf hunt hand-off (v496, updated for v561 + perf round)

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


## Round on v561 (`main` @ f44ba59)
#19 is ported (v497, GHOST_GROW). I read v497–v561: the game bundle's changed code, `tut.js` against the old TUTOR, `index.html`, `server.js`, `sw.js` and `split_build.py`. Course data blobs were skimmed only.
- **#21 (Medium): Hunt pins never change between rounds.** Since v541, BOOT_ALL keeps Hunt 1 built, so the per-round pin seed never re-rolls: every Hunt round in a session has identical pins (v496 rolled a new seed each round). One-condition fix. **Decision for Neil:** Hunt 1 rebuilds behind the home screen after a Hunt round, as before v541.
- **#22 (Low): the home button still says "Tutorial" after the in-place tutorial's Tee off / Skip** (until a reload). Tapping it plays normally. One-line fix.
- **Checked and fine:**
  - TERRAIN_OCC really is pixel-identical: 0 pixels differ while it hides up to 106 instances, rendered with and without it in the same task (Hunt 1 and 9; `tests/occpix.js`).
  - PROG_PIN keeps GPU programs bounded at 37 over 34 hole loads on all three courses (`tests/progs2.js`).
  - Random play on OslerBrook (10 holes): clean.
  - KNOB_FAST's parser falls back safely on odd markup.
  - The boot's synchronous build can't stall on the hatch worker.
- **Unchecked / notes:**
  - With BOOT_ALL, osler.js is in every boot, but the service worker still skips it when pre-caching a page. Offline then relies on the HTTP cache for it.
  - SWING_EASE and ROUGH_LIFT change outcomes, so a mixed-version MP room (during a deploy) can classify the same swing differently.


## Perf round on v561
- **#23 (perf): keep the baked swing-dial frames across deploys.** The cache was named per BUILD, so every deploy re-baked identical art for every returning player: about 5–7 s of CPU at boot in test. After a simulated deploy, time to home went from 19.4 s to 13.6 s, with 0 bake. One-line change.
- **Measured and left alone:**
  - In play, the main thread is nearly idle. Tee view, aim drag, shot flight, next-hole build and the home screen all had **0 long tasks** (>50 ms) and only a few % of JS per frame; the frame time is the GPU (SwiftShader).
  - On the GPU side, trees (~40 ms) and ground tiles (~35 ms) dominate a ~110 ms SwiftShader frame. Cutting them means reducing graphics, which needs Neil.
  - Cold boot (~23 s in test) is the dial bake (#11/#23 cache it), shader compiles (SHADER_WARM, by design) and BOOT_ALL's three first holes (Neil's choice). None of it is waste I could remove without changing behaviour.
  - TERRAIN_OCC is pixel-identical, and the GPU program count stays bounded at 37 (see the v561 round above).

## Decisions

### Open
- [ ] **#21 (Hunt pins):** OK that Hunt 1 is built again behind the home screen after each Hunt round (as before v541), so every round gets new pins?
- [x] **#19:** ported in v497 (GHOST_GROW).

### Standing notes from earlier PRs
- **#17 (canvases freed after upload):** if a WebGL context-restore path is ever added, it has to repaint those canvases, or set `TEX_FREE = false`.
- **#8, #11, #12 (perf):** if they haven't been checked on an iPhone and an Android phone yet, compare `?prof` before and after.

### Settled
- #4, #6, #8, #12, #15/#18 and #17 were settled when they merged in v473 / 0b1b9a0.
