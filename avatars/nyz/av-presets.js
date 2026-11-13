// Nyz avatar — expression tables for the AV module in sketchy-golf.html (same format as Neil's av-presets.js).
// Face (v6, face-mesh likeness pass): eyes 42/58 at y=51 (static #avEyes transform, small almond smiling eyes, rx 2.25), brows ~y44-48.6 (thin, low), mouth ~y65-75, chin ~y80.2; rest = wide crescent smile showing the upper teeth (standard avTe), happy = open grin (avGr). Brows clear the cap brim in every preset.
// Shared by avatar.svg (no hat) and avatar-hat.svg.
//
// INTEGRATION: pass these to AV.addArt('nyz', html, MOUTH, BROWS), or, to replace the active
// tables, swap them for `let MOUTH = { ... };` / `let BROWS = { ... };` inside `const AV = (() => {`.
  let MOUTH = {
    rest: ['M41.2 65.4 Q50 67.0 58.8 65.4 Q57.0 71.6 50 71.8 Q43.0 71.6 41.2 65.4Z', 'url(#avTe)'],
    closed: ['M42.4 66.6 Q50 69.8 57.6 66.6', 'none'],
    small: ['M45.2 68.1 Q50 73.2 54.8 68.1 Q50 69.2 45.2 68.1 Z', 'url(#avMo)'],
    wide: ['M42 67.4 Q50 78.5 58 67.4 Q50 69.4 42 67.4 Z', 'url(#avMo)'],
    o: ['M47 70.1 a3 3.4 0 1 0 6.1 0 a3 3.4 0 1 0 -6.1 0 Z', 'url(#avMo)'],
    ee: ['M42.4 67.6 Q50 73.5 57.6 67.6 Q50 69 42.4 67.6 Z', 'url(#avMo)'],
    grin: ['M40.4 65.0 Q50 67.4 59.6 65.0 Q58.0 74.2 50 74.6 Q42.0 74.2 40.4 65.0Z', 'url(#avGr)'],
    frown: ['M43.5 71.5 Q50 67.2 56.5 71.5', 'none'],
    shock: ['M45.8 71 a4.2 4.9 0 1 0 8.4 0 a4.2 4.9 0 1 0 -8.4 0 Z', 'url(#avMo)'],
    tight: ['M43.7 69.2 Q47.1 68.3 50 69 T56.3 68.7', 'none'],
    wobble: ['M42.4 69.4 q1.9 -1.8 3.8 0 t3.8 0 t3.8 0 t3.8 0', 'none']
  };
  let BROWS = {
    neutral: 'M36.2 48.4 Q40.6 46.0 46.8 47.6 M53.2 47.6 Q59.4 46.0 63.8 48.4',
    focus: 'M36.4 47.4 Q40.8 46.2 46.8 48.4 M53.2 48.4 Q59.2 46.2 63.6 47.4',
    up: 'M36.2 46.0 Q40.6 43.4 46.8 44.8 M53.2 44.8 Q59.4 43.4 63.8 46.0',
    sad: 'M36.4 48.6 Q41.0 47.6 46.8 45.4 M53.2 45.4 Q59.0 47.6 63.6 48.6',
    happy: 'M36.2 47.6 Q40.6 45.0 46.8 46.6 M53.2 46.6 Q59.4 45.0 63.8 47.6'
  };
