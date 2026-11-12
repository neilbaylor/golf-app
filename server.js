// Tiny zero-dependency web server for Railway: serves the single-file game (gzip/brotli when the browser accepts it).
const http = require('http'), fs = require('fs'), path = require('path'), zlib = require('zlib');
const html = fs.readFileSync(path.join(__dirname, 'index.html'));
const gz = zlib.gzipSync(html, { level: 9 }), br = zlib.brotliCompressSync(html, { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 } });
const etag = '"' + require('crypto').createHash('sha1').update(html).digest('hex').slice(0, 16) + '"';
http.createServer((req, res) => {
  const url = req.url.split('?')[0];
  if (url === '/healthz') { res.writeHead(200, { 'Content-Type': 'text/plain' }); return res.end('ok'); }
  if (url !== '/' && url !== '/index.html') { res.writeHead(404, { 'Content-Type': 'text/plain' }); return res.end('Not found'); }
  const h = { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache', ETag: etag, Vary: 'Accept-Encoding' };
  if (req.headers['if-none-match'] === etag) { res.writeHead(304, h); return res.end(); }
  const ae = req.headers['accept-encoding'] || '';
  const [body, enc] = /\bbr\b/.test(ae) ? [br, 'br'] : /\bgzip\b/.test(ae) ? [gz, 'gzip'] : [html, null];
  if (enc) h['Content-Encoding'] = enc;
  res.writeHead(200, h); res.end(req.method === 'HEAD' ? undefined : body);
}).listen(process.env.PORT || 3000, '0.0.0.0', () => console.log('Tee Party on port ' + (process.env.PORT || 3000)));
