# Tee Party: working notes

- The game source is the single file `/home/claude/golf/sketchy-golf.html` (Three.js r128 from cdnjs, everything else inline). Deploy with `python3 /home/claude/golf/tools/split_build.py sketchy-golf.html <golf-app>`: it writes `index.html` + content-hashed `game/crew/hunt/aug.<hash>.js` (plus `osler`/`tut`, loaded on demand: osler when picked, tut on `#tutorial-hole` or, for a first-time player, in the background on the home screen (`__tutLoad`, TUT_INPLACE: the tutorial starts and ends in place, no reload); the tutorial's TUTOR module (`TUTOR_MK`) and hole are cut out of game.js and eval'd in place) (cached forever; server.js SPLIT_FILES). `--single` = the old one-file page (rollback). Top-level code that patches AUG_HOLES must be a one-line `{ ... }` block (the split runs it once aug.js has loaded); the build stops on any other top-level AUG_HOLES read.
- Before dropping or downgrading any draw mode, effect or graphics feature, ask Neil first. Effects stay. Perf work must not reduce graphics or gameplay.
- Audio (Neil 16 Nov): only the ball strike, the ball landing, and subtle nature birds. No UI sounds. Sound must be togglable and default on.
- Target high fps (120 where the device allows). Check perf after visual changes (`tools/perf/bench.js`).
- In one-line JS inside the HTML, never use `//` comments where code follows on the same line. Use `/* */`.
- The menu state is `MENU` (not `HOME`, which is the dial constant).
- Golfer art goes in `avatars/<who>/` and is embedded with `tools/crew_integrate.py`. Home screen uses the no-hat art; in-game uses the hat version where a golfer has one.
- Ball flight is shown 1.35× taller than the physics (`SHOT_LIFT`). Tree hits and the tracer use the lifted path; stats use the real one.
