// Piggy avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face: eyes 42/58 at y=51 (static #avEyes transform: small, narrow, light blue/hazel), straight brows ~y44-48.6, mouth ~y64-72, soft short chin ~y78.9; rest = his modest smile, upper teeth showing (14 wide x ~4 deep), closed = a cocky lop-sided smirk. Brows clear the cap bill in every preset.
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('piggy', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M43.0 65.0 Q45.3 66.1 50 66.2 Q54.7 66.1 57.0 65.0 Q55.6 69.7 50 70.0 Q44.4 69.7 43.0 65.0Z', 'url(#avTe)'],
    closed: ['M43.4 66.6 Q49.2 68.8 56.8 65.4', 'none'],
    small: ['M46 67.2 Q50 71.9 54 67.2 Q50 68.2 46 67.2 Z', 'url(#avMo)'],
    wide: ['M43.3 66.5 Q50 77 56.7 66.5 Q50 68.4 43.3 66.5 Z', 'url(#avMo)'],
    o: ['M47.4 69.1 a2.6 3.2 0 1 0 5.1 0 a2.6 3.2 0 1 0 -5.1 0 Z', 'url(#avMo)'],
    ee: ['M43.6 66.7 Q50 72.3 56.4 66.7 Q50 68.1 43.6 66.7 Z', 'url(#avMo)'],
    grin: ['M41.6 64.6 Q50 66.4 58.4 64.4 Q56.8 71.4 50 71.8 Q43.2 71.4 41.6 64.6Z', 'url(#avGr)'],
    frown: ['M44.6 70.4 Q50 66.4 55.4 70.4', 'none'],
    shock: ['M46.5 69.9 a3.5 4.5 0 1 0 7 0 a3.5 4.5 0 1 0 -7 0 Z', 'url(#avMo)'],
    tight: ['M44.7 68.2 Q47.6 67.4 50 68.1 T55.3 67.7', 'none'],
    wobble: ['M43.6 68.4 q1.6 -1.7 3.2 0 t3.2 0 t3.2 0 t3.2 0', 'none']
  };
  let BROWS = {
    neutral: 'M35.2 48.1 Q39.8 46.8 46.6 47.4 M53.4 47.4 Q60.2 46.8 64.8 48.1',
    focus: 'M35.2 47.4 Q40.2 46.6 46.6 48.6 M53.4 48.6 Q59.8 46.6 64.8 47.4',
    up: 'M35.0 46.4 Q39.8 44.2 46.6 45.4 M53.4 45.4 Q60.2 44.2 65.0 46.4',
    sad: 'M35.2 48.6 Q40.4 47.8 46.6 45.6 M53.4 45.6 Q59.6 47.8 64.8 48.6',
    happy: 'M35.2 47.4 Q39.8 45.9 46.6 46.6 M53.4 46.6 Q60.2 45.9 64.8 47.4'
  };
