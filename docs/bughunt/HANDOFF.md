# Message for the main agent

You're picking up the results of a bug and perf hunt on neilbaylor/golf-app (Tee Party), based on `main` @ 59cb62a (v472).

**What exists**
- **PRs #1–#13, #15, #17 and #18** on GitHub, stacked in order. #14 is the decisions issue, not a PR. #16 is this hand-off. #8 is a draft.
  - Each PR applies cleanly to `main` on its own, **except #18, which needs #5 and #15 first** (it edits the same lines). Otherwise the stack is only for review order, so merge any subset.
  - Every PR has: a description with a reproduction or measurement, the test script that proves it (`tests/` in the hand-off folder), and a fresh-eyes review comment.
- **Decisions waiting on you or Neil:** `DECISIONS.md`. The live list is the latest decisions comment on PR #1. Issue #14 holds rounds 1–5 only, because the token lost write access to issues.

**How to treat them**
1. **Porting comes first.** The repo holds only the built bundle `game.8381d52b01.js`; the real source is `sketchy-golf.html`, which isn't in the repo. The game PRs (#1, #2, #5, #6, #8, #9, #11, #12, #13, #15, #17, #18) patch the built file to prove the fix. Redo each change in `sketchy-golf.html` and rebuild with `tools/split_build.py`, which gives the file a new hashed name. Never edit the hashed file in place: it's cached forever, so phones would stay on old code.
2. **Server-only, mergeable as is:** #3, #4, #7, #10 (`server.js`).
3. **Suggested order by value:**
   - #2: High — a reload mid-round loses the scorecard.
   - #8: hole builds about 30× less CPU; needs Neil's sign-off on tiny anti-aliasing changes and a phone check.
   - #15 + #18: MP replays drifted up to 2.5 yd on other players' screens; fixed (0 of 30 replays off in two-player tests).
   - #9: MP golfer hand wrong after picking on the board.
   - #3: removed golfers come back after a server restart.
   - #1: GIR ignores penalties.
   - #12: cold boot about 18% faster.
   - #11: warm boot about 2× faster.
   - #17: frees about 26–33 MB of memory per built hole.
   - The rest are small.
4. **Needs Neil before merging:**
   - #18: none (merge after #5 and #15).
   - #8: graphics sign-off.
   - #6: even-par voice lines.
   - #4: should leavers also lose their turn after the tee?
   - #12: OK to drop shader error logging in production?
   - #15: merge now, or wait for the second drift cause?
5. **Check perf on real phones.** Every number comes from headless Chromium with SwiftShader (software GL) on 4 cores, so treat them as before/after comparisons. Confirm #8, #11 and #12 on an iPhone and an Android phone with the game's `?prof` panel.

**MP replay drift: fixed by #15 + #18.**
- #15 fixed the proven curve-bucket cause.
- #18 has watchers use the shooter's final launch speed, yaw correction and wind scale.
- Two randomised two-player games: 0 of 30 replays off (before: about 2 per game, 0.8–1.8 yd).
- Still unexplained, and now harmless: why the two phones' speed tables differ slightly with identical keys (details in #18).

**Later passes (memory and perf) found:**
- **#17:** free the course and green canvases after GPU upload. No functionality lost.
- **No leaks:** home↔play cycles and hole loads keep GPU object counts and the JS heap steady.
- **Per-shot `launch`:** about 19 ms of one frame in software rendering. It's the physics; not changed, because changing the timestep would break MP replays between versions.

**If you find more:** add the PR to the stack and to this list, and post any decision on its PR and in `DECISIONS.md` here.

**Security:** the GitHub token used here was pasted in chat. Revoke it.
