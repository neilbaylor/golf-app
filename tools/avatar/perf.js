// Per-frame cost: 60 animated copies at 3x DPR, driven the way AV drives them (head transform, eye ry, mouth d),
// Neil (current v2 art) vs each crew SVG, interleaved, 3 rounds. Software raster, so only relative numbers matter.
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const fs = require('fs'); const C = '/home/claude/golf/avatar/crew/';
const svgs = { neil: '/home/claude/golf/avatar/v2/avatar.svg', hunter: C + 'hunter/avatar.svg', 'hunter-hat': C + 'hunter/avatar-hat.svg', sean: C + 'sean/avatar.svg', 'sean-hat': C + 'sean/avatar-hat.svg' };
const page = (svg, n) => `<html><body style="margin:0;display:flex;flex-wrap:wrap">${Array.from({ length: n }, () => `<div style="width:76px;height:76px;border-radius:50%;overflow:hidden">${svg.replace(/id="av(\w+)"/g, 'data-av="$1"')}</div>`).join('')}
<script>
const H=[...document.querySelectorAll('[data-av=Head]')], E=[...document.querySelectorAll('[data-av=EyeL]')], M=[...document.querySelectorAll('[data-av=Mouth]')];
const D=['M43 67 Q50 71 57 67','M45 68.4 Q50 74 55 68.4 Q50 69.6 45 68.4Z'];
let f=0; const times=[]; let last=performance.now();
function loop(now){ times.push(now-last); last=now; f++;
  H.forEach((h,i)=>h.setAttribute('transform','translate(0 '+Math.sin(now/300+i).toFixed(1)+') rotate('+(Math.sin(now/500+i)*3).toFixed(1)+' 50 78)'));
  E.forEach((e,i)=>e.setAttribute('ry',(1+Math.abs(Math.sin(now/200+i))*1.9).toFixed(1))); M.forEach((m,i)=>m.setAttribute('d',D[(f>>2)&1]));
  if(f<160) requestAnimationFrame(loop); else window.done=times.slice(20);
} requestAnimationFrame(loop);
</script></body></html>`;
(async () => {
  const b = await chromium.launch({ args: ['--disable-gpu-vsync', '--disable-frame-rate-limit'] });
  const acc = {};
  for (let r = 0; r < 3; r++) for (const [name, f] of Object.entries(svgs)) {
    const pg = await b.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 3 });
    await pg.setContent(page(fs.readFileSync(f, 'utf8'), 60)); await pg.waitForFunction(() => window.done, null, { timeout: 120000 });
    const t = await pg.evaluate(() => { const a = window.done.slice().sort((x, y) => x - y); return { med: a[a.length >> 1], min: a[0] }; });
    (acc[name] = acc[name] || []).push(t); await pg.close();
  }
  for (const [n, a] of Object.entries(acc)) console.log(n.padEnd(11), 'median ms/frame', a.map(t => t.med.toFixed(1)).join(' / '), '| best', Math.min(...a.map(t => t.min)).toFixed(1));
  await b.close();
})();
