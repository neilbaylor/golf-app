"""Write SCRATCH copies of the game with a crew avatar integrated (the real sketchy-golf.html is only read).
mode A (replace): the two SVGs inside <button id="player"> -> this avatar's split; `let MOUTH`/`let BROWS` -> its tables.
mode B (roster):  Neil untouched; AV.addArt('hunter'|'sean', split svg, MOUTH, BROWS) registered right after AV.
usage: python3 integrate.py"""
import re, os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from avlib import CREW, W, T, split_svg
G = open('/home/claude/golf/sketchy-golf.html').read()
OUT = W + 'gametest/'; os.makedirs(OUT, exist_ok=True)

def tables(who):
    P = json.load(open(T + f'{who}_presets.json'))
    mo = 'let MOUTH = {\n' + ',\n'.join(f"    {k}: ['{d}', '{f}']" for k, (d, f) in P['MOUTH'].items()) + '\n  };'
    br = 'let BROWS = {\n' + ',\n'.join(f"    {k}: '{d}'" for k, d in P['BROWS'].items()) + '\n  };'
    return P, mo, br

def replace(who, fn):
    P, mo, br = tables(who)
    svg = open(CREW + f'{who}/{fn}').read().strip()
    g = G
    a = g.index('<button id="player"'); s0 = g.index('<svg viewBox="0 0 100 100"', a); s1 = g.index('<span class="nametag">', a)
    old = g[s0:s1]; assert old.count('<svg') == 2 and 'avHeadL' in old
    g = g[:s0] + split_svg(svg) + '\n' + g[s1:]
    k = g.index('const AV = (() => {'); head, tail = g[:k], g[k:]
    tail, n1 = re.subn(r'let MOUTH = \{.*?\n  \};', lambda m: mo, tail, count=1, flags=re.S)
    tail, n2 = re.subn(r'let BROWS = \{.*?\n  \};', lambda m: br, tail, count=1, flags=re.S)
    assert n1 == 1 and n2 == 1
    out = OUT + f'game-{who}-{fn.replace(".svg", "")}.html'
    open(out, 'w').write(head + tail); return out

def roster(hat=False):
    g = G; add = ''
    for who in ('hunter', 'sean'):
        P, _, _ = tables(who)
        svg = split_svg(open(CREW + f'{who}/avatar{"-hat" if hat else ""}.svg').read().strip())
        add += f"AV.addArt('{who}', {json.dumps(svg)}, {json.dumps(P['MOUTH'])}, {json.dumps(P['BROWS'])});\n"
    k = g.index('const AV = (() => {'); e = g.index('})();', k) + 5
    g = g[:e] + '\n' + add + g[e:]
    out = OUT + f'game-roster{"-hat" if hat else ""}.html'; open(out, 'w').write(g); return out

if __name__ == '__main__':
    for who in ('hunter', 'sean'):
        for fn in ('avatar.svg', 'avatar-hat.svg'): print(replace(who, fn))
    print(roster(False)); print(roster(True))
