// Sherbo avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face: eyes 42/58 at y=51 (static #avEyes transform) behind clear glasses, brows above the frame (~y43), mouth ~y67-77 tucked under the moustache overlay image, beard to ~y86; rest = big closed-mouth smile.
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('sherbo', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M40.8 66.8 Q50 70.6 59.2 66.6 Q57.2 71.6 50 72.0 Q42.8 71.6 40.8 66.8Z', '#d9786f'],
    closed: ['M42.2 67.6 Q50 70.0 57.8 67.4 Q55.8 70.6 50 70.9 Q44.2 70.6 42.2 67.6Z', '#d9786f'],
    small: ['M45.5 68.8 Q50 74.1 54.5 68.8 Q50 69.9 45.5 68.8 Z', 'url(#avMo)'],
    wide: ['M42.4 68 Q50 79.8 57.6 68 Q50 70.1 42.4 68 Z', 'url(#avMo)'],
    o: ['M47.1 70.9 a2.9 3.6 0 1 0 5.8 0 a2.9 3.6 0 1 0 -5.8 0 Z', 'url(#avMo)'],
    ee: ['M42.8 68.2 Q50 74.5 57.2 68.2 Q50 69.8 42.8 68.2 Z', 'url(#avMo)'],
    grin: ['M40.4 66.8 Q50 68.6 59.6 66.6 Q58.0 76.8 50 77.2 Q42.0 76.8 40.4 66.8Z', 'url(#avGr)'],
    frown: ['M43.9 72.4 Q50 67.9 56.1 72.4', 'none'],
    shock: ['M46 71.8 a4 5.1 0 1 0 7.9 0 a4 5.1 0 1 0 -7.9 0 Z', 'url(#avMo)'],
    tight: ['M44.1 69.9 Q47.3 69 50 69.8 T55.9 69.4', 'none'],
    wobble: ['M42.8 70.1 q1.8 -1.9 3.6 0 t3.6 0 t3.6 0 t3.6 0', 'none']
  };
  let BROWS = {
    neutral: 'M34.8 43.8 Q40.4 42.2 46.0 43.4 M54.0 43.4 Q59.6 42.2 65.2 43.8',
    focus: 'M35.0 42.6 Q40.6 42.4 46.0 44.2 M54.0 44.2 Q59.4 42.4 65.0 42.6',
    up: 'M34.8 42.4 Q40.4 40.6 46.0 41.8 M54.0 41.8 Q59.6 40.6 65.2 42.4',
    sad: 'M35.0 44.2 Q40.6 43.8 46.0 41.8 M54.0 41.8 Q59.4 43.8 65.0 44.2',
    happy: 'M34.8 43.0 Q40.4 41.2 46.0 42.4 M54.0 42.4 Q59.6 41.2 65.2 43.0'
  };
