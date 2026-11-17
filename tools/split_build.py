#!/usr/bin/env python3
"""Tee Party split build (perf2, Neil 16 Nov): sketchy-golf.html -> a small index.html plus content-hashed, cache-forever scripts.

  python3 tools/split_build.py sketchy-golf.html /home/claude/golf-app        # writes index.html + game/crew/hunt/aug.<hash>.js, removes stale ones (keeps the previous build's)
  python3 tools/split_build.py sketchy-golf.html OUTDIR --single               # rollback: today's one-file index.html (removes the hashed files)
  python3 tools/split_build.py sketchy-golf.html OUTDIR --artifact-files       # print the Artifact `files` map for the split output (after a build)

Files (each name = first 10 hex of the sha256 of its content, so the same input always gives the same names):
  index.html          the page: CSS, markup, boot scene, a tiny loader (served no-cache)
  game.<hash>.js      all the game code (changes every deploy)
  crew.<hash>.js      the golfers' art (the CREW_ART block, run as __CREW(AV) at its old place) and the two course crests
  hunt.<hash>.js      HUNT_HOLES and REAL_H (the Hunt's data)
  aug.<hash>.js       AUG_HOLES (Augusta's data, half the bytes): in the ordered chain only when the page boots on Augusta
                      (#augusta / #augusta-hole-N, also a hash HOLE_URL restores from tp_at, or the fresh load's 50% pick); otherwise fetched
                      as soon as a build needs it (the home screen's prebuild of Augusta's first hole, right after boot; holeAUGDg
                      waits, behind the existing pill), on the first pointerdown on Augusta's course card, or at idle after load.
                      HOLESYS.boot() then leaves Augusta's first hole to that prebuild instead of building it under the boot cover.
                      Top-level one-line { ... } blocks in the game code that patch AUG_HOLES (aug13's flowers/maple/bridge) run at once when the
                      data is there, else queued and run by aug.js right after its data; any other top-level read of AUG_HOLES stops the build
The game code stays in its strict IIFE; the data files are strict classic scripts whose top-level consts (HUNT_HOLES, REAL_H, AUG_HOLES,
HUNT_LOGO, AUG_LOGO) and window.__CREW are globals the IIFE reads by name (none of them clash with the page's other globals).
The scripts are parser-blocking classic scripts at the old inline script's place, in order (data, crew, game), so everything runs
exactly where and when it ran inline; <link rel=preload> in the head starts every download at once.
"""
import hashlib, os, re, sys, json

def die(m): sys.exit('split_build: ' + m)

def one(text, pat, what, flags=re.M):
    m = list(re.finditer(pat, text, flags))
    if len(m) != 1: die(f'{what}: expected 1 match, got {len(m)}')
    return m[0]

def build(src, single=False):
    s = open(src, encoding='utf-8').read()
    if single: return {'index.html': s}, {}
    # the game's own inline script: the last <script> ... </script> block (after three.min.js)
    t3 = one(s, r'^<script src="https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/r128/three\.min\.js"></script>\n', 'three.js tag')
    open_ = s.index('<script>\n', t3.end())
    if open_ != t3.end(): die('the game script does not follow three.js directly')
    close = s.rindex('</script>')
    code = s[open_ + len('<script>\n'):close]
    def cut(pat, what):
        nonlocal code
        m = one(code, pat, what); code = code[:m.start()] + code[m.end():]; return m.group(0)
    aug = cut(r'^const AUG_HOLES = \{.*\n', 'AUG_HOLES')
    hunt = cut(r'^const HUNT_HOLES = \{.*\n', 'HUNT_HOLES') + cut(r'^const REAL_H = \(\(\) => \{.*\n', 'REAL_H')
    logos = cut(r"^const HUNT_LOGO = 'data:image/[^']*';.*\n", 'HUNT_LOGO') + cut(r"^const AUG_LOGO = 'data:image/[^']*';.*\n", 'AUG_LOGO')
    a = one(code, r'^/\* CREW_ART_BEGIN[^\n]*\n', 'CREW_ART_BEGIN'); b = one(code, r'^/\* CREW_ART_END \*/\n', 'CREW_ART_END')
    if b.start() < a.end(): die('crew art markers out of order')
    art = code[a.end():b.start()]
    if re.search(r'^(?!AV\.addArt\(|\s|\}|"|\{)\S', art, re.M): die('crew art block holds something other than AV.addArt calls')
    code = code[:a.start()] + a.group(0) + "__CREW(AV); /* SPLIT: the golfers' art, from crew.<hash>.js */\n" + b.group(0) + code[b.end():]
    # Augusta on demand: the boot pick is made in the head (same rule as AUG_M), and a build of an Augusta hole waits for its data
    m = one(code, r"^const AUG_M = /\^#augusta\(\?:-hole-\(\\d\+\)\)\?\$/\.exec\(location\.hash\) \|\| \(!location\.hash && Math\.random\(\) < \.5 \? \['#augusta', undefined\] : null\);", 'AUG_M')
    code = code[:m.start()] + m.group(0).replace("Math.random() < .5", "window.__augPick") + code[m.end():]
    m = one(code, r"  if \(cid === 'augusta'\) return AUG_HOLES\[n\] \? yield\* buildDataHoleG\(", 'holeAUGDg augusta line')
    code = code[:m.start()] + "  if (cid === 'augusta') while (typeof AUG_HOLES === 'undefined') { window.__augLoad(); yield HATCH_WAIT; } /* SPLIT: Augusta's data on its way (an idle step: the frame's slice ends) */\n" + code[m.start():]
    # HOLESYS.boot() builds every other course's first hole synchronously under the boot cover; on a Hunt boot Augusta's data isn't there yet,
    # so that one is left to ahead()'s home-screen prebuild (a normal stepped job, which waits for the data above)
    m = one(code, r"if \(id !== CID && !jobs\.has\(keyOf\(id, NINE\.first\(id\)\)\)\) \{ const J = start\(id, NINE\.first\(id\)\); while \(!J\.ready\) step\(J\); \}", 'HOLESYS.boot other courses')
    code = code[:m.start()] + m.group(0).replace("if (id !== CID && ", "if (id !== CID && !(id === 'augusta' && typeof AUG_HOLES === 'undefined') /* SPLIT */ && ", 1) + code[m.end():]
    # Top-level code that patches Augusta's data as the game script loads (e.g. aug13's `{ const h = AUG_HOLES['13'], ... }`): on a Hunt boot AUG_HOLES isn't
    # there yet, so each such block runs as soon as it is: at once when the data came first (an Augusta boot: exactly as inline), else queued and run by aug.js
    # itself, right after its data and before any build can see it. Any OTHER top-level statement that reads AUG_HOLES stops the build (it would break a Hunt boot).
    out_lines, inc = [], False
    for l in code.splitlines(True):
        t, k = '', 0  # the line without its comments (block comments may span lines; good enough for this check)
        while k < len(l):
            if inc: e = l.find('*/', k); k, inc = (len(l), True) if e < 0 else (e + 2, False); continue
            if l.startswith('/*', k): inc = True; k += 2; continue
            if l.startswith('//', k) and (k == 0 or l[k - 1] in ' ;{}(,'): break
            t += l[k]; k += 1
        if 'AUG_HOLES' in t and not l[:1].isspace() and not re.match(r'(async\s+)?function\b|\}', l):
            m = re.match(r'(\{ .*\})(\s*/\*(?:(?!\*/).)*\*/)?\n$', l)  # a one-line block, maybe with a trailing /* comment */ (kept after the wrap)
            if not m: die('a top-level statement reads AUG_HOLES (undefined on a Hunt boot until aug.js arrives); make it a one-line { ... } block or move it into a function:\n  ' + l[:160])
            l = AUG_FIX_A + m.group(1) + AUG_FIX_B + (m.group(2) or '') + '\n'
        out_lines.append(l)
    code = ''.join(out_lines)
    files = {
        'hunt': "'use strict'; /* Tee Party: the Toronto Hunt data */\n" + hunt,
        'crew': "'use strict'; /* Tee Party: the golfers' art and the course crests */\n" + logos + 'window.__CREW = function (AV) {\n' + art + '};\n',
        'aug': "'use strict'; /* Tee Party: Augusta National data */\n" + aug + AUG_FIX_RUN,
        'game': code,
    }
    names = {k: f'{k}.{hashlib.sha256(v.encode()).hexdigest()[:10]}.js' for k, v in files.items()}
    head_js = ("<script>/* SPLIT loader: starts every download at once; Augusta's 1.9 MB of data is in the boot only when the page opens on Augusta */\n"
               "(function () { var h = location.hash, at = ''; try { at = !h && sessionStorage.getItem('tp_at') || ''; } catch (e) {} if (!/^#(augusta|augusta-hole-\\d+|hole-\\d+)$/.test(at)) at = '';\n"
               "  /* the head scripts below may still change the hash (HOLE_URL puts tp_at back, MP_REJOIN_HOLE / a room link take it off), so this is only the early guess for the preload;\n"
               "     the real decision is made at the scripts' place (the tail), on the hash AUG_M will read; the fresh load's 50% pick is made there too, at the same point of\n"
               "     Math.random's sequence as AUG_M's (after three.js), so on a fresh Augusta pick its data starts at the tail rather than here */\n"
               "  var guess = /^#augusta/.test(h || at);\n"
               "  var N = " + json.dumps(names) + ", pre = function (n) { var l = document.createElement('link'); l.rel = 'preload'; l.as = 'script'; l.href = n; document.head.appendChild(l); };\n"
               "  window.__splitN = N; if (guess) pre(N.aug); pre(N.hunt); pre(N.crew); pre(N.game);\n"
               "  var s = null, t0 = -1e9; window.__augLoad = function () { if (s || window.__augBoot || Date.now() - t0 < 3000) return; t0 = Date.now(); s = document.createElement('script'); s.src = N.aug; s.async = true;\n"
               "    s.onerror = function () { s.remove(); s = null; }; document.head.appendChild(s); }; /* a failed fetch is tried again (at most every 3 s) the next time it's wanted */\n"
               "  window.__splitFail = function () { try { var k = 'tp_split_retry', t = +sessionStorage.getItem(k) || 0; if (Date.now() - t < 60000) return; sessionStorage.setItem(k, Date.now()); } catch (e) { return; } location.reload(); }; /* a boot script that failed to load: one fresh reload (no loops) */\n"
               "  addEventListener('load', function () { (window.requestIdleCallback || setTimeout)(window.__augLoad, { timeout: 2000 }); }); /* (the home screen's prebuild of Augusta's first hole usually asks first) */\n"
               "  addEventListener('pointerdown', function (e) { var t = e.target; if (t && t.closest && t.closest('.course[data-id=\"augusta\"]')) window.__augLoad(); }, true);\n"
               "})();</script>\n")
    tail = ("<script>(function () { var h = location.hash; if (!h && window.__augPick === undefined) window.__augPick = Math.random() < .5; /* AUG_M's rule, on the hash it will see */\n"
            "  window.__augBoot = h ? /^#augusta(?:-hole-(\\d+))?$/.test(h) : window.__augPick; })();\n"
            "if (window.__augBoot) document.write('<script src=\"' + __splitN.aug + '\" onerror=\"__splitFail()\"><\\/script>');</script>\n"
            f'<script src="{names["hunt"]}" onerror="__splitFail()"></script>\n<script src="{names["crew"]}" onerror="__splitFail()"></script>\n<script src="{names["game"]}" onerror="__splitFail()"></script>\n')
    index = head_js + s[:open_] + tail + s[close + len('</script>'):]
    out = {'index.html': index}
    for k, v in files.items(): out[names[k]] = v
    return out, names

AUG_FIX_A = "(typeof AUG_HOLES !== 'undefined' ? f => f() : f => (window.__augQ = window.__augQ || []).push(f))(() => "
AUG_FIX_B = "); /* SPLIT: patches Augusta's data once it's here */"
AUG_FIX_RUN = "(window.__augQ || []).splice(0).forEach(f => f()); /* SPLIT: the game's patches to this data (queued on a Hunt boot) */\n"

HASHED = re.compile(r'^(game|crew|hunt|aug)\.[0-9a-f]{10}\.js$')

def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]; fl = [x for x in sys.argv[1:] if x.startswith('--')]
    if len(a) != 2: die(__doc__)
    src, out = a
    if '--artifact-files' in fl:
        m = re.search(r'var N = (\{[^}]*\})', open(os.path.join(out, 'index.html'), encoding='utf-8').read())  # only the files this index.html loads
        names = sorted(json.loads(m.group(1)).values()) if m else []
        print(json.dumps({n: os.path.join(os.path.abspath(out), n) for n in names}, indent=1)); print('# page: ' + os.path.join(os.path.abspath(out), 'index.html'), file=sys.stderr); return
    single = '--single' in fl
    files, names = build(src, single)
    os.makedirs(out, exist_ok=True)
    # keep the previous build's hashed files one deploy longer: a page opened just before the deploy can still fetch them (Augusta's data, lazily)
    prev = set()
    if os.path.exists(os.path.join(out, 'index.html')):
        m = re.search(r'var N = (\{[^}]*\})', open(os.path.join(out, 'index.html'), encoding='utf-8').read())
        if m: prev = set(json.loads(m.group(1)).values())
        if prev == set(names.values()): prev = set(n for n in os.listdir(out) if HASHED.match(n))  # the same build again: remove nothing
    for n, v in files.items():
        p = os.path.join(out, n)
        if n != 'index.html' and os.path.exists(p) and open(p, encoding='utf-8').read() == v: continue
        with open(p, 'w', encoding='utf-8') as f: f.write(v)
    stale = [n for n in os.listdir(out) if HASHED.match(n) and n not in files and n not in prev]
    for n in stale: os.remove(os.path.join(out, n))
    for n in sorted(files): print(f'{len(files[n].encode()):9d}  {n}')
    if stale: print('removed stale:', ' '.join(sorted(stale)))

if __name__ == '__main__': main()
