# Message for the main agent

You're picking up the results of a bug and perf hunt on neilbaylor/golf-app (Tee Party), based on `main` @ 59cb62a (v472).

**What exists**
- **PRs #1–#13, #15 and #17** on GitHub, stacked in order. #14 is the decisions issue, not a PR. #16 is this hand-off. #8 is a draft.
  - Each PR applies cleanly to `main` on its own; the stack is only for review order, so merge any subset.
  - Every PR has: a description with a reproduction or measurement, the test script that proves it (`tests/` in the hand-off folder), and a fresh-eyes review comment.
- **Decisions waiting on you or Neil:** `DECISIONS.md`. The live list is the latest decisions comment on PR #1. Issue #14 holds rounds 1–5 only, because the token lost write access to issues.

**How to treat them**
1. **Porting comes first.** The repo holds only the built bundle `game.8381d52b01.js`; the real source is `sketchy-golf.html`, which isn't in the repo. The game PRs (#1, #2, #5, #6, #8, #9, #11, #12, #13, #15, #17) patch the built file to prove the fix. Redo each change in `sketchy-golf.html` and rebuild with `tools/split_build.py`, which gives the file a new hashed name. Never edit the hashed file in place: it's cached forever, so phones would stay on old code.
2. **Server-only, mergeable as is:** #3, #4, #7, #10 (`server.js`).
3. **Suggested order by value:**
   - #2: High — a reload mid-round loses the scorecard.
   - #8: hole builds about 30× less CPU; needs Neil's sign-off on tiny anti-aliasing changes and a phone check.
   - #15: MP replays drift up to 2.5 yd; one cause fixed, a second still open.
   - #9: MP golfer hand wrong after picking on the board.
   - #3: removed golfers come back after a server restart.
   - #1: GIR ignores penalties.
   - #12: cold boot about 18% faster.
   - #11: warm boot about 2× faster.
   - #17: frees about 26–33 MB of memory per built hole.
   - The rest are small.
4. **Needs Neil before merging:**
   - #8: graphics sign-off.
   - #6: even-par voice lines.
   - #4: should leavers also lose their turn after the tee?
   - #12: OK to drop shader error logging in production?
   - #15: merge now, or wait for the second drift cause?
5. **Check perf on real phones.** Every number comes from headless Chromium with SwiftShader (software GL) on 4 cores, so treat them as before/after comparisons. Confirm #8, #11 and #12 on an iPhone and an Android phone with the game's `?prof` panel.

**Open item worth a follow-up:** a second MP replay-drift source, still not root-caused. Full shots occasionally replay with a 1–1.7 yd difference in landing (`tests/mpsmoke.js` reproduces it in about 2 of 15 replays, intermittently).
- **Narrowed down so far:** a diagnostic build diffed every launch input between shooter and watcher for each mismatching shot. All recorded inputs match: golfer, lie, club, mode, ball, wind, curve, height, the speed table's key, its build aim, and its build start height and ball. Only `planShot`'s `speed` differs (and what follows from it: `speedMul`, `yawc`, `speedA`). So the two phones' speed tables hold different rows despite matching keys.
- **Ruled out:**
  - the mesh-based start height (`restYAt` idea: build heights matched, change dropped)
  - wind, `dOfP`/`pStar`, the lie/mode ranges, hand and golfer
- **Next step:** record the table's build-time `launch2`/`spin` and its rows on both phones (the instrumented diagnostic is described in the #15 comments) and diff them for one mismatching shot.

**Later passes (memory and perf) found:**
- **#17:** free the course and green canvases after GPU upload. No functionality lost.
- **No leaks:** home↔play cycles and hole loads keep GPU object counts and the JS heap steady.
- **Per-shot `launch`:** about 19 ms of one frame in software rendering. It's the physics; not changed, because changing the timestep would break MP replays between versions.

**If you find more:** add the PR to the stack and to this list, and post any decision on its PR and in `DECISIONS.md` here.

**Security:** the GitHub token used here was pasted in chat. Revoke it.
