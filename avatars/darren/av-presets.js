// Darren avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face: eyes 42/58 at y=51 (static #avEyes transform, open eyes), brows ~y45-47, mouth ~y68-78 tucked under the moustache overlay image, chin ~y84.8; rest = gentle smile (18 wide x ~5 deep), a little teeth below the drooping moustache (v2.3).
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('darren', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M41.0 69.2 Q50 71.2 59.0 69.0 Q57.2 74.2 50 74.4 Q42.8 74.2 41.0 69.2Z', 'url(#avTe)'],
    closed: ['M43.0 69.6 Q50 70.8 57.0 69.4 Q55.6 72.6 50 72.9 Q44.4 72.6 43.0 69.6Z', '#cf7f7a'],
    small: ['M45.6 69.8 Q50 75.1 54.4 69.8 Q50 70.9 45.6 69.8 Z', 'url(#avMo)'],
    wide: ['M42.6 69 Q50 80.8 57.4 69 Q50 71.1 42.6 69 Z', 'url(#avMo)'],
    o: ['M47.2 71.9 a2.8 3.6 0 1 0 5.6 0 a2.8 3.6 0 1 0 -5.6 0 Z', 'url(#avMo)'],
    ee: ['M43 69.2 Q50 75.5 57 69.2 Q50 70.8 43 69.2 Z', 'url(#avMo)'],
    grin: ['M40.4 68.0 Q50 69.8 59.6 67.8 Q58.0 77.6 50 78.0 Q42.0 77.6 40.4 68.0Z', 'url(#avGr)'],
    frown: ['M44 73.4 Q50 68.9 56 73.4', 'none'],
    shock: ['M46.1 72.8 a3.9 5.1 0 1 0 7.7 0 a3.9 5.1 0 1 0 -7.7 0 Z', 'url(#avMo)'],
    tight: ['M44.2 70.9 Q47.4 70 50 70.8 T55.8 70.4', 'none'],
    wobble: ['M43 71.1 q1.8 -1.9 3.5 0 t3.5 0 t3.5 0 t3.5 0', 'none']
  };
  let BROWS = {
    neutral: 'M35.8 46.8 Q40.2 44.2 45.8 46.0 M54.2 46.0 Q59.8 44.2 64.2 46.8',
    focus: 'M36.0 45.6 Q40.6 44.4 45.8 47.4 M54.2 47.4 Q59.4 44.4 64.0 45.6',
    up: 'M35.8 44.8 Q40.2 42.1 45.8 43.6 M54.2 43.6 Q59.8 42.1 64.2 44.8',
    sad: 'M36.0 47.4 Q40.8 46.4 45.8 44.0 M54.2 44.0 Q59.2 46.4 64.0 47.4',
    happy: 'M35.8 45.8 Q40.2 43.0 45.8 44.6 M54.2 44.6 Q59.8 43.0 64.2 45.8'
  };
