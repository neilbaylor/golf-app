// Sean avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face: eyes 42/58 at y=51 (static #avEyes transform, squinty smile), mouth ~y66-74, chin ~y82; rest = big toothy smile.
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('sean', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M41.6 66.8 Q50 68.4 58.8 65.8 Q57.2 73.2 50 73.4 Q43.0 73.2 41.6 66.8Z', 'url(#avTe)'],
    closed: ['M42.4 69.4 Q50 72.2 58.0 68.6', 'none'],
    small: ['M45 69.4 Q50 75 55 69.4 Q50 70.6 45 69.4 Z', 'url(#avMo)'],
    wide: ['M41.6 68.6 Q50 81 58.4 68.6 Q50 70.8 41.6 68.6 Z', 'url(#avMo)'],
    o: ['M46.8 71.6 a3.2 3.8 0 1 0 6.4 0 a3.2 3.8 0 1 0 -6.4 0 Z', 'url(#avMo)'],
    ee: ['M42 68.8 Q50 75.4 58 68.8 Q50 70.4 42 68.8 Z', 'url(#avMo)'],
    grin: ['M38.8 65.8 Q50 68.6 61.4 64.8 Q59.6 77.6 50 78.0 Q40.6 77.6 38.8 65.8Z', 'url(#avGr)'],
    frown: ['M43.2 73.2 Q50 68.4 56.8 73.2', 'none'],
    shock: ['M45.6 72.6 a4.4 5.4 0 1 0 8.8 0 a4.4 5.4 0 1 0 -8.8 0 Z', 'url(#avMo)'],
    tight: ['M43.4 70.6 Q47 69.6 50 70.4 T56.6 70', 'none'],
    wobble: ['M42 70.8 q2 -2 4 0 t4 0 t4 0 t4 0', 'none']
  };
  let BROWS = {
    neutral: 'M35.2 46.6 Q40.6 45.6 46.4 47.0 M53.6 47.0 Q59.4 45.6 64.8 46.6',
    focus: 'M35.4 45.6 Q40.8 45.4 46.4 48.2 M53.6 48.2 Q59.2 45.4 64.6 45.6',
    up: 'M35.2 44.6 Q40.6 43.4 46.4 44.6 M53.6 44.6 Q59.4 43.4 64.8 44.6',
    sad: 'M35.4 47.6 Q40.8 47.2 46.4 45.0 M53.6 45.0 Q59.2 47.2 64.6 47.6',
    happy: 'M35.2 45.8 Q40.6 44.6 46.4 45.8 M53.6 45.8 Q59.4 44.6 64.8 45.8'
  };
