// Tiny zero-dependency web server for Railway. Serves the single-file game inside a proper page shell
// (doctype, viewport, app-icon and home-screen tags), plus the manifest and icons. Compressed when the browser accepts it.
const http = require('http'), fs = require('fs'), path = require('path'), zlib = require('zlib'), crypto = require('crypto');
const HEAD = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<title>Tee Party</title>
<meta name="theme-color" content="#1d2a1a">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="Tee Party">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png?v=2"><link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png?v=2">
<style>html,body{margin:0;height:100%;background:#1d2a1a;overscroll-behavior:none}[hidden]{display:none!important}</style>
</head><body>`;
const page = Buffer.from(HEAD + fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8') + '</body></html>');
const TYPES = { '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const files = { '/': [page, 'text/html; charset=utf-8'] };
const icons = fs.existsSync(path.join(__dirname, 'icons')) ? fs.readdirSync(path.join(__dirname, 'icons')).map(n => 'icons/' + n) : []; // missing extras never stop the game from serving
for (const f of ['manifest.webmanifest', ...icons]) if (fs.existsSync(path.join(__dirname, f)))
  files['/' + f] = [fs.readFileSync(path.join(__dirname, f)), TYPES[path.extname(f)] || 'application/octet-stream'];
files['/index.html'] = files['/'];
const cache = {}; for (const [k, [buf, type]] of Object.entries(files)) cache[k] = { buf, type, gz: zlib.gzipSync(buf, { level: 9 }), br: zlib.brotliCompressSync(buf), etag: '"' + crypto.createHash('sha1').update(buf).digest('hex').slice(0, 16) + '"' };
http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  if (url === '/healthz') { res.writeHead(200, { 'Content-Type': 'text/plain' }); return res.end('ok'); }
  const f = cache[url]; if (!f) { res.writeHead(404, { 'Content-Type': 'text/plain' }); return res.end('Not found'); }
  const h = { 'Content-Type': f.type, 'Cache-Control': f.type.startsWith('text/html') ? 'no-cache' : 'public, max-age=86400', ETag: f.etag, Vary: 'Accept-Encoding' };
  if (req.headers['if-none-match'] === f.etag) { res.writeHead(304, h); return res.end(); }
  const ae = req.headers['accept-encoding'] || '', pngish = f.type === 'image/png';
  const [body, enc] = !pngish && /\bbr\b/.test(ae) ? [f.br, 'br'] : !pngish && /\bgzip\b/.test(ae) ? [f.gz, 'gzip'] : [f.buf, null];
  if (enc) h['Content-Encoding'] = enc;
  res.writeHead(200, h); res.end(req.method === 'HEAD' ? undefined : body);
}).listen(process.env.PORT || 3000, '0.0.0.0', () => console.log('Tee Party on port ' + (process.env.PORT || 3000)));
