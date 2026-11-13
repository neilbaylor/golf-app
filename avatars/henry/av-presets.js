// Henry avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face: eyes 42/58 at y=51 (static #avEyes transform, open eyes, rx 3.1), brows ~y44-46.5, mouth ~y65-75, chin ~y77.4; rest = small warm smile showing a row of clean teeth (standard avTe), happy = open grin (avGr). Brows clear the cap brim in every preset.
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('henry', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M43.2 65.8 Q50 68.9 56.8 65.8 C56.0 69.8 53.4 71.4 50 71.4 C46.6 71.4 44.0 69.8 43.2 65.8Z', 'url(#avTe)'],
    closed: ['M44.6 67.2 Q50 69.6 55.4 67.2', 'none'],
    small: ['M45.8 67.3 Q50 72.3 54.2 67.3 Q50 68.3 45.8 67.3 Z', 'url(#avMo)'],
    wide: ['M42.9 66.5 Q50 77.7 57.1 66.5 Q50 68.5 42.9 66.5 Z', 'url(#avMo)'],
    o: ['M47.3 69.2 a2.7 3.4 0 1 0 5.4 0 a2.7 3.4 0 1 0 -5.4 0 Z', 'url(#avMo)'],
    ee: ['M43.3 66.7 Q50 72.7 56.7 66.7 Q50 68.2 43.3 66.7 Z', 'url(#avMo)'],
    grin: ['M42.2 65.8 Q50 68.4 57.8 65.6 Q56.2 74.0 50 74.2 Q43.8 74.0 42.2 65.8Z', 'url(#avGr)'],
    frown: ['M44.3 70.7 Q50 66.4 55.7 70.7', 'none'],
    shock: ['M46.3 70.1 a3.7 4.9 0 1 0 7.4 0 a3.7 4.9 0 1 0 -7.4 0 Z', 'url(#avMo)'],
    tight: ['M44.5 68.3 Q47.5 67.4 50 68.2 T55.5 67.8', 'none'],
    wobble: ['M43.3 68.5 q1.7 -1.8 3.4 0 t3.4 0 t3.4 0 t3.4 0', 'none']
  };
  let BROWS = {
    neutral: 'M36.1 46.2 Q40.8 44.8 45.8 45.4 M54.2 45.4 Q59.2 44.8 63.9 46.2',
    focus: 'M36.4 45 Q41 45 45.8 46.8 M54.2 46.8 Q59 45 63.6 45',
    up: 'M36.1 45 Q40.8 43.4 45.8 44.1 M54.2 44.1 Q59.2 43.4 63.9 45',
    sad: 'M36.4 46.4 Q41 46.2 45.8 44 M54.2 44 Q59 46.2 63.6 46.4',
    happy: 'M36.1 45.4 Q40.8 43.6 45.8 44.4 M54.2 44.4 Q59.2 43.6 63.9 45.4'
  };
