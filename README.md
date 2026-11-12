# Tee Party

A mobile-web golf game in a hand-drawn, sticker-book style. The whole game is one file, `index.html`, using Three.js r128 from cdnjs. Open it in a browser to play.

## Hosting

Railway runs `node server.js` (no dependencies). It serves `index.html` compressed, with a `/healthz` check. Railway redeploys on every push to `main`.

## Layout

| Path | What it is |
|---|---|
| `index.html` | The game. |
| `avatars/<who>/` | Golfer art: `avatar.svg` (home screen, no hat), `avatar-hat.svg` (on the course), `av-presets.js` (mouth and brow shapes). |
| `tools/crew_integrate.py` | Embeds the crew avatars into `index.html` between the `CREW_ART_BEGIN/END` markers. |
| `tools/avatar/` | Avatar generators (Python plus Playwright render and preview scripts). |
| `tools/perf/` | Perf benches and probes used to tune frame rate. |
| `tests/` | Playwright scripts that drive the game (intro, home, swings, drops, putting views, cards). |
| `assets/` | The Toronto Hunt crest (used with permission). |

## Testing

Tests use Playwright (`cd tests && npm install`) with headless Chromium on SwiftShader:

```js
chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] })
```

They route `**/three.min.js` to `node_modules/three/build/three.min.js` and Google Fonts to `tests/fonts.css`. The game boots to the intro (`#introSkip`), then the home screen (`#boot.home`), then `#playBtn`. Debug hooks on `window` include `__G` (game state), `__setup(u, v)` (place the ball), `__ph` (physics) and `__trees`.

The scripts still contain absolute paths from the machine they were written on (`/home/claude/golf/...`); point them at your checkout before running.
