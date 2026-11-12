"""crew/crew_preview.html -> crew_preview.png: Neil, Hunter (no hat, cap), Sean (no hat, cap) at 228px and in the game's 76px button."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from avlib import CREW
items = [('Neil', '/home/claude/golf/avatar/v2/avatar.svg'), ('Hunter', CREW + 'hunter/avatar.svg'), ('Hunter', CREW + 'hunter/avatar-hat.svg'),
         ('Sean', CREW + 'sean/avatar.svg'), ('Sean', CREW + 'sean/avatar-hat.svg')]
caps = ['Neil', 'Hunter', 'Hunter · cap', 'Sean', 'Sean · cap']
def uniq(s, p): return s.replace('id="av', f'id="{p}av').replace('url(#av', f'url(#{p}av')
big = ''.join(f'<figure><div class="c228">{uniq(open(f).read(), f"a{i}")}</div><figcaption>{c} · 228px</figcaption></figure>' for i, ((n, f), c) in enumerate(zip(items, caps)))
small = ''.join(f'<figure class="sm"><div class="player">{uniq(open(f).read(), f"b{i}")}<span class="nametag">{n}</span></div><figcaption>{c} · 76px</figcaption></figure>' for i, ((n, f), c) in enumerate(zip(items, caps)))
html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Crew avatars</title><style>
:root{{--ink:#1d2a1a;--paper:#fffaf0;--sun:#ffd23f;--wob2:14px 22px 12px 25px / 22px 13px 24px 15px}}
body{{margin:0;padding:18px 20px 26px;background:#f1e7cc;color:var(--ink);font:15px system-ui,sans-serif;width:1300px}}
h1{{font:400 26px "Luckiest Guy",system-ui,sans-serif;margin:0 0 12px}}
.row{{display:flex;gap:22px;align-items:flex-start}} figure{{margin:0;text-align:center}} figcaption{{margin-top:6px}}
.c228{{width:228px;height:228px;border-radius:50%;overflow:hidden;border:3px solid var(--ink);background:var(--sun)}} .c228 svg{{width:100%;height:100%;display:block}}
.hud{{margin-top:18px;background:linear-gradient(#8fd3ff 0 60%,#6cbf4a 60%);border:3px solid var(--ink);border-radius:16px;padding:16px 26px 14px;display:flex;justify-content:space-around}}
.player{{position:relative;width:76px;height:76px;border-radius:50%;border:3.5px solid var(--ink);background:var(--sun);box-shadow:3px 4px 0 var(--ink);margin:0 auto}}
.player svg{{width:100%;height:100%;border-radius:50%;display:block}}
.nametag{{position:absolute;left:50%;bottom:-13px;transform:translateX(-50%) rotate(-3deg);background:var(--paper);border:2.5px solid var(--ink);border-radius:var(--wob2);padding:0 10px;font:700 15px/20px system-ui,sans-serif;box-shadow:2px 2px 0 var(--ink);white-space:nowrap}}
.sm figcaption{{margin-top:22px}}
</style></head><body><h1>The crew</h1><div class="row">{big}</div><div class="hud">{small}</div></body></html>'''
open(CREW + 'crew_preview.html', 'w').write(html)
