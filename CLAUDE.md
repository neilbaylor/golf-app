# Tee Party: working notes

- The game is the single file `index.html`. Keep it one self-contained file (Three.js r128 from cdnjs, everything else inline).
- Before dropping or downgrading any draw mode, effect or graphics feature, ask Neil first. Effects stay. Perf work must not reduce graphics or gameplay.
- No audio.
- Target high fps (120 where the device allows). Check perf after visual changes (`tools/perf/bench.js`).
- In one-line JS inside the HTML, never use `//` comments where code follows on the same line. Use `/* */`.
- The menu state is `MENU` (not `HOME`, which is the dial constant).
- Golfer art goes in `avatars/<who>/` and is embedded with `tools/crew_integrate.py`. Home screen uses the no-hat art; in-game uses the hat version where a golfer has one.
- Ball flight is shown 1.35× taller than the physics (`SHOT_LIFT`). Tree hits and the tracer use the lifted path; stats use the real one.
