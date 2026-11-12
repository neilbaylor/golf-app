// Hunter avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face: eyes 42/58 at y=51 (static #avEyes transform), mouth ~y67, chin ~y78; rest = closed-mouth smile, happy = open grin.
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('hunter', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M44.2 66.6 Q50 70.4 55.8 66.6 M43.1 65.8 Q43.7 66.8 44.8 67.3 M56.9 65.8 Q56.3 66.8 55.2 67.3', 'none'],
    closed: ['M44.6 67.4 Q50 69.6 55.4 67.4', 'none'],
    small: ['M45.8 67.4 Q50 72.4 54.2 67.4 Q50 68.4 45.8 67.4 Z', 'url(#avMo)'],
    wide: ['M42.9 66.6 Q50 77.8 57.1 66.6 Q50 68.6 42.9 66.6 Z', 'url(#avMo)'],
    o: ['M47.3 69.3 a2.7 3.4 0 1 0 5.4 0 a2.7 3.4 0 1 0 -5.4 0 Z', 'url(#avMo)'],
    ee: ['M43.3 66.8 Q50 72.8 56.7 66.8 Q50 68.3 43.3 66.8 Z', 'url(#avMo)'],
    grin: ['M41.8 65.8 Q50 68.6 58.2 65.8 Q56.6 74.8 50 75.0 Q43.4 74.8 41.8 65.8Z', 'url(#avGr)'],
    frown: ['M44.3 70.8 Q50 66.5 55.7 70.8', 'none'],
    shock: ['M46.3 70.2 a3.7 4.9 0 1 0 7.4 0 a3.7 4.9 0 1 0 -7.4 0 Z', 'url(#avMo)'],
    tight: ['M44.5 68.4 Q47.5 67.5 50 68.3 T55.5 67.9', 'none'],
    wobble: ['M43.3 68.6 q1.7 -1.8 3.4 0 t3.4 0 t3.4 0 t3.4 0', 'none']
  };
  let BROWS = {
    neutral: 'M36.2 46.8 Q41 45.4 46.0 46.0 M54.0 46.0 Q59 45.4 63.8 46.8',
    focus: 'M36.4 45.4 Q41.2 45.4 46.0 47.4 M54.0 47.4 Q58.8 45.4 63.6 45.4',
    up: 'M36.2 44.8 Q41 43.0 46.0 43.8 M54.0 43.8 Q59 43.0 63.8 44.8',
    sad: 'M36.4 47.0 Q41.2 46.8 46.0 44.4 M54.0 44.4 Q58.8 46.8 63.6 47.0',
    happy: 'M36.2 45.8 Q41 44.0 46.0 44.8 M54.0 44.8 Q59 44.0 63.8 45.8'
  };
