// Marsh avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face: eyes 42/58 at y=51 (static #avEyes transform), heavy straight brows ~y42-47, mouth ~y68-77 over a short salt-and-pepper beard, chin ~y82.6; rest = modest warm smile (16.8 wide x 5 deep, upper teeth). Brows clear the cap brim in every preset.
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('marsh', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M41.9 68.7 Q50 70.4 58.1 68.5 Q56.6 73.6 50 73.8 Q43.4 73.6 41.9 68.7Z', 'url(#avTe)'],
    closed: ['M43.0 69.4 Q50 71.6 57.0 69.2', 'none'],
    small: ['M45.6 69.8 Q50 75.1 54.4 69.8 Q50 70.9 45.6 69.8 Z', 'url(#avMo)'],
    wide: ['M42.6 69 Q50 80.8 57.4 69 Q50 71.1 42.6 69 Z', 'url(#avMo)'],
    o: ['M47.2 71.9 a2.8 3.6 0 1 0 5.6 0 a2.8 3.6 0 1 0 -5.6 0 Z', 'url(#avMo)'],
    ee: ['M43 69.2 Q50 75.5 57 69.2 Q50 70.8 43 69.2 Z', 'url(#avMo)'],
    grin: ['M40.6 67.8 Q50 69.8 59.4 67.6 Q57.8 76.8 50 77.2 Q42.2 76.8 40.6 67.8Z', 'url(#avGr)'],
    frown: ['M44 73.4 Q50 68.9 56 73.4', 'none'],
    shock: ['M46.1 72.8 a3.9 5.1 0 1 0 7.7 0 a3.9 5.1 0 1 0 -7.7 0 Z', 'url(#avMo)'],
    tight: ['M44.2 70.9 Q47.4 70 50 70.8 T55.8 70.4', 'none'],
    wobble: ['M43 71.1 q1.8 -1.9 3.5 0 t3.5 0 t3.5 0 t3.5 0', 'none']
  };
  let BROWS = {
    neutral: 'M35.4 46.6 Q40.0 44.0 46.6 45.2 M53.4 45.2 Q60.0 44.0 64.6 46.6',
    focus: 'M35.6 45.4 Q40.4 44.4 46.6 46.6 M53.4 46.6 Q59.6 44.4 64.4 45.4',
    up: 'M35.4 45.2 Q40.0 42.8 46.6 43.8 M53.4 43.8 Q60.0 42.8 64.6 45.2',
    sad: 'M35.6 46.8 Q40.6 45.8 46.6 43.4 M53.4 43.4 Q59.4 45.8 64.4 46.8',
    happy: 'M35.4 45.8 Q40.0 43.0 46.6 44.2 M53.4 44.2 Q60.0 43.0 64.6 45.8'
  };
