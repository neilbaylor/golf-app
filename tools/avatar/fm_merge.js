const { chromium } = require('/opt/npm-tools/node_modules/playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const S = '/home/claude/golf/avatar/crew/work'; const NP='/tmp/claude-0/-home-claude/f3913e02-f249-51e1-9b46-1ecd5cb64ada/scratchpad/npmdl/package';
const srv = http.createServer((q, r) => {
  let u = decodeURIComponent(q.url.split('?')[0]);
  let f = u.startsWith('/mp/') ? path.join(NP, u.slice(4)) : path.join(S, 'fm', u.slice(1));
  if (u === '/') { r.setHeader('content-type','text/html'); return r.end(`<script src="/mp/face_mesh.js"></script><body></body>`); }
  if (!fs.existsSync(f)) { r.statusCode = 404; return r.end(); }
  const ext = path.extname(f); r.setHeader('content-type', {'.js':'text/javascript','.wasm':'application/wasm','.png':'image/png','.jpg':'image/jpeg'}[ext] || 'application/octet-stream');
  fs.createReadStream(f).pipe(r);
}).listen(8771, async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  pg.on('console', m => console.error('C:', m.text().slice(0, 200)));
  await pg.goto('http://localhost:8771/');
  const out = {};
  for (const name of process.argv.slice(2)) {
    out[name] = await pg.evaluate(async (name) => {
      const img = new Image(); img.src = '/' + name; await img.decode();
      const fm = new FaceMesh({ locateFile: f => '/mp/' + f });
      fm.setOptions({ maxNumFaces: 1, refineLandmarks: true, minDetectionConfidence: .3 });
      let res = null; fm.onResults(r => res = r);
      await fm.initialize(); await fm.send({ image: img });
      const lm = res && res.multiFaceLandmarks && res.multiFaceLandmarks[0];
      return lm ? { w: img.width, h: img.height, lm: lm.map(p => [+(p.x * img.width).toFixed(1), +(p.y * img.height).toFixed(1), +(p.z*img.width).toFixed(1)]) } : null;
    }, name);
    console.error(name, out[name] ? out[name].lm.length : 'none');
  }
  const prev = JSON.parse(fs.readFileSync(path.join(S, 'fm/landmarks.json'))); Object.assign(prev, out); fs.writeFileSync(path.join(S, 'fm/landmarks.json'), JSON.stringify(prev));
  await b.close(); srv.close();
});
