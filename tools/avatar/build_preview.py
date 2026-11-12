"""Build crew/<who>/preview.html: likeness row, every AV state at 228 px + 76 px for both versions (no hat / hat),
and a game-frame mock running the game's real AV module (extracted read-only from sketchy-golf.html) with
this character's MOUTH/BROWS tables and the game's two-SVG split.  usage: python3 build_preview.py hunter|sean [live=hat]"""
import re, os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from avlib import CREW, T, split_svg
who = sys.argv[1]; live_hat = len(sys.argv) > 2 and sys.argv[2] == 'hat'
NAME = who.capitalize()
D = CREW + who + '/'
svg0 = open(D + 'avatar.svg').read().strip(); svg1 = open(D + 'avatar-hat.svg').read().strip()
neil = open('/home/claude/golf/avatar/v2/avatar.svg').read().strip()
P = json.load(open(T + f'{who}_presets.json'))
game = open('/home/claude/golf/sketchy-golf.html').read()
a = game.index('const AV = (() => {'); b = game.index('})();', a) + 5
av = game[a:b]
mo = 'let MOUTH = {\n' + ',\n'.join(f"    {k}: ['{d}', '{f}']" for k, (d, f) in P['MOUTH'].items()) + '\n  };'
br = 'let BROWS = {\n' + ',\n'.join(f"    {k}: '{d}'" for k, d in P['BROWS'].items()) + '\n  };'
av2, n1 = re.subn(r'let MOUTH = \{.*?\n  \};', lambda m: mo, av, count=1, flags=re.S)
av2, n2 = re.subn(r'let BROWS = \{.*?\n  \};', lambda m: br, av2, count=1, flags=re.S)
assert n1 == 1 and n2 == 1, 'table swap failed'

def static(s, pre):  # copies for the grid: ids -> data-av, gradient ids made unique per copy family
    s = re.sub(r'id="av(Head|Body|Eyes|EyeL|EyeR|Brows|Mouth|Sweat)"', r'data-av="\1"', s)
    return s.replace('id="av', f'id="{pre}av').replace('url(#av', f'url(#{pre}av')
S0, S1, SN = static(svg0, 'x'), static(svg1, 'y'), static(neil, 'n')
states = [
    ('Neutral (rest)', dict()),
    ('Talk: closed', dict(m='closed')), ('Talk: small', dict(m='small')), ('Talk: wide', dict(m='wide')),
    ('Talk: o', dict(m='o')), ('Talk: ee', dict(m='ee')),
    ('Blink (half)', dict(lid=.5)), ('Blink (shut)', dict(lid=0)),
    ('Glance left', dict(lx=-.9)), ('Glance right', dict(lx=.9)), ('Look up (ball in air)', dict(ly=-1)), ('Look down', dict(ly=1)),
    ('Mood: happy / proud', dict(m='grin', b='happy', lid=.55, ty=-2)),
    ('Mood: focus (swing)', dict(m='tight', b='focus', lid=.7, lx=.15, ly=1, ty=2)),
    ('Mood: watch', dict(m='o', b='up', big=1, ly=-1)),
    ('Mood: oops', dict(m='shock', b='up', big=1)),
    ('Mood: sad', dict(m='frown', b='sad', rot=-4)),
    ('Mood: nervous', dict(m='wobble', b='sad', sweat=1)),
]
cards = ''.join(f'''<figure class="st" data-s='{json.dumps(o)}'><div class="pair"><div class="c228 slot" data-t="0"></div><div class="c228 slot" data-t="1"></div></div>
<div class="pair"><div class="c76 slot" data-t="0"></div><div class="c76 slot" data-t="1"></div></div><figcaption>{t}</figcaption></figure>''' for t, o in states)
refs = {'hunter': [('h_cap.jpg', 'cap close-up'), ('h_front.jpg', 'front'), ('h_group.jpg', 'group photo')],
        'sean': [('s_group.jpg', 'group photo'), ('s_cap.jpg', 'cap selfie')]}[who]
refhtml = ''.join(f'<figure class="ref"><img src="../work/prevref/{f}" alt="{c}"><figcaption>{c}</figcaption></figure>' for f, c in refs)
livesvg = split_svg(svg1 if live_hat else svg0)

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{NAME} avatar</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Luckiest+Guy&family=Patrick+Hand&display=swap">
<style>
:root{{--ink:#1d2a1a;--paper:#fffaf0;--paper-2:#f1e7cc;--sun:#ffd23f;--wob2:14px 22px 12px 25px / 22px 13px 24px 15px}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper-2);color:var(--ink);font:16px/1.4 "Patrick Hand",system-ui,sans-serif;padding:16px}}
h1,h2{{font-family:"Luckiest Guy",system-ui,sans-serif;font-weight:400;letter-spacing:.5px;margin:.2em 0 .4em}}
h1{{font-size:30px}} h2{{font-size:21px;margin-top:22px}}
.row{{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end}}
.ref img{{height:228px;width:auto;border:3px solid var(--ink);border-radius:10px;display:block}}
figcaption{{font-size:14px;text-align:center;margin-top:4px}}
figure{{margin:0}}
.c228,.c76{{border-radius:50%;overflow:hidden;border:3px solid var(--ink);background:var(--sun);flex:none}}
.c228{{width:228px;height:228px}} .c76{{width:76px;height:76px}}
.c228 svg,.c76 svg{{width:100%;height:100%;display:block}}
.pair{{display:flex;gap:10px;justify-content:center;margin-top:6px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(484px,1fr));gap:16px}}
.st{{background:var(--paper);border:2.5px solid var(--ink);border-radius:var(--wob2);padding:6px 6px 8px}}
.hud{{position:relative;background:linear-gradient(#8fd3ff 0 55%,#6cbf4a 55%);border:3px solid var(--ink);border-radius:16px;padding:18px 20px 34px;display:flex;gap:26px;align-items:flex-start;max-width:100%;min-height:300px}}
.player{{position:relative;flex:none;width:76px;height:76px;border-radius:50%;border:3.5px solid var(--ink);background:var(--sun);box-shadow:3px 4px 0 var(--ink);padding:0}}
.player svg{{width:100%;height:100%;border-radius:50%;display:block}}
#player svg.avHeadL{{position:absolute;inset:0;border-radius:0;overflow:visible;pointer-events:none;transform-origin:50% 78%;will-change:transform}}
.nametag{{position:absolute;left:50%;bottom:-13px;transform:translateX(-50%) rotate(-3deg);background:var(--paper);border:2.5px solid var(--ink);border-radius:var(--wob2);padding:0 10px;font:17px/21px "Luckiest Guy",system-ui,sans-serif;box-shadow:2px 2px 0 var(--ink);white-space:nowrap}}
#say{{position:absolute;left:112px;top:110px;z-index:2;background:var(--paper);border:2.5px solid var(--ink);border-radius:var(--wob2);padding:4px 10px;font:17px "Patrick Hand",sans-serif;max-width:220px}}
.note{{max-width:80ch}}
code{{font:13px ui-monospace,monospace;background:#fff6;padding:0 3px}}
</style></head><body>
<template id="tpl0">{S0}</template><template id="tpl1">{S1}</template><template id="tplN">{SN}</template>
<h1>{NAME} avatar</h1>
<p class="note">Sticker-book caricature in Neil's style, traced over {NAME}'s photos warped into the game's 100-unit frame. Two versions share one <code>MOUTH</code>/<code>BROWS</code> table: no hat (left of each pair) and cap (right). One embedded WebP texture under vector ink; every feature is driven by the game's own <code>AV</code> module.</p>
<h2>Likeness check</h2>
<div class="row">
 <figure><div class="c228 slot" data-t="0"></div><figcaption>no hat · 228px</figcaption></figure>
 <figure><div class="c228 slot" data-t="1"></div><figcaption>cap · 228px</figcaption></figure>
 <figure><div class="pair" style="flex-direction:column;align-items:center"><div class="c76 slot" data-t="0"></div><div class="c76 slot" data-t="1"></div></div><figcaption>76px</figcaption></figure>
 {refhtml}
 <figure><div class="c228 slot" data-t="N"></div><figcaption>Neil (for scale/style)</figcaption></figure>
</div>
<h2>Every state AV can show (228px + 76px, no hat | cap)</h2>
<div class="grid">{cards}</div>
<h2>In the game frame</h2><p class="note">Left: live, running the game's real <code>AV</code> code with {NAME}'s tables and the game's two-SVG split ({'cap' if live_hat else 'no hat'}). Then static neutral at true 76px (no hat, cap), and the cap version scaled 3x (happy) to show what the name tag hides.</p>
<div id="app" class="hud">
 <button class="player" id="player" aria-label="Player {NAME}">{livesvg}<span class="nametag">{NAME}</span></button>
 <div id="say" hidden></div>
 <div class="player" aria-hidden="true"><div class="slot" data-t="0" style="width:100%;height:100%;border-radius:50%;overflow:hidden"></div><span class="nametag">{NAME}</span></div>
 <div class="player" aria-hidden="true"><div class="slot" data-t="1" style="width:100%;height:100%;border-radius:50%;overflow:hidden"></div><span class="nametag">{NAME}</span></div>
 <div class="player" aria-hidden="true" style="transform:scale(3);transform-origin:0 0"><div class="slot" data-t="1" data-o='{{"m":"grin","b":"happy","lid":0.55}}' style="width:100%;height:100%;border-radius:50%;overflow:hidden"></div><span class="nametag">{NAME}</span></div>
</div>
<script>
const P = {json.dumps(P)};
const PN = {json.dumps({'MOUTH': {k: list(v) for k, v in __import__('avlib').NEIL_MOUTH.items()}})};
function apply(root, o, neil) {{
  const q = k => root.querySelector('[data-av="' + k + '"]');
  const lid = o.lid ?? 1, ry = Math.max(.25, 2.9 * lid) * (o.big ? 1.25 : 1), ex = (o.lx || 0) * 2.2, ey = (o.ly || 0) * 1.8;
  for (const [k, cx] of [['EyeL', 42], ['EyeR', 58]]) {{ const e = q(k); e.setAttribute('cx', (cx + ex).toFixed(1)); e.setAttribute('cy', (54 + ey).toFixed(1)); e.setAttribute('ry', ry.toFixed(1)); }}
  if (!neil) {{ q('Brows').setAttribute('d', P.BROWS[o.b || 'neutral']);
    const m = P.MOUTH[o.m || 'rest']; q('Mouth').setAttribute('d', m[0]); q('Mouth').setAttribute('fill', m[1].replace('url(#', 'url(#' + root.dataset.pre)); }}
  q('Sweat').setAttribute('opacity', o.sweat ? 1 : 0);
  q('Head').setAttribute('transform', `translate(${{((o.lx || 0) * 1.2).toFixed(1)}} ${{((o.ty || 0) + (o.ly || 0) * 1.2).toFixed(1)}}) rotate(${{o.rot || 0}} 50 78)`);
}}
const T = {{ '0': document.getElementById('tpl0').content.firstElementChild, '1': document.getElementById('tpl1').content.firstElementChild, N: document.getElementById('tplN').content.firstElementChild }};
const PRE = {{ '0': 'x', '1': 'y', N: 'n' }};
document.querySelectorAll('.slot').forEach(d => {{ const t = d.dataset.t; const s = T[t].cloneNode(true); s.dataset.pre = PRE[t]; d.appendChild(s); const f = d.closest('.st'); apply(s, f ? JSON.parse(f.dataset.s) : d.dataset.o ? JSON.parse(d.dataset.o) : {{}}, t === 'N'); }});
// ---- live: the game's AV module, verbatim apart from the swapped MOUTH/BROWS tables ----
const $ = s => document.querySelector(s); const app = $('#app'); const INK = '#1d2a1a'; const RM = false;
const G = {{ view: 'idle', shot: null }}; const SW = {{ vis: 0, tilt: 0 }}; const CHARS = {{ neil: {{ name: 'Neil' }}, {who}: {{ name: '{NAME}' }} }};
function setA(el, k, v) {{ v = String(v); if (el.getAttribute(k) !== v) el.setAttribute(k, v); }}
{av2}
window.__AV = () => AV;
const lines = [['Hey! Let\\'s tee it up.', 'happy'], ['165 yards. 7 Iron. Smooth tempo.'], ['Nooo. Not the pond.', 'sad'], ['Timber! Who planted that?', 'oops'], ['Pured it.', 'proud']];
let li = 0, last = performance.now(), t0 = last; window.__errs = [];
function cue() {{ const [tx, m] = lines[li++ % lines.length]; AV.say(tx, m ? {{ mood: m, force: true }} : {{ force: true }}); }}
setTimeout(cue, 300); setInterval(cue, 3600);
setInterval(() => AV.setMood('nervous', 1.2), 9100);
(function loop(now) {{ const dt = Math.min(.05, (now - last) / 1000); last = now; AV.update(dt, (now - t0) / 1000); requestAnimationFrame(loop); }})(last);
</script>
</body></html>'''
fn = D + ('preview-live-hat.html' if live_hat else 'preview.html')
open(fn, 'w').write(html)
print('wrote', fn, len(html))
