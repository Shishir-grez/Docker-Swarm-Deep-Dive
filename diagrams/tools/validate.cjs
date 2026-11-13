let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname;
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  const types = {'.js':'text/javascript','.woff2':'font/woff2','.css':'text/css','.html':'text/html'};
  res.writeHead(200, {'Content-Type': types[path.extname(p)]||'application/octet-stream'}); fs.createReadStream(p).pipe(res);
}).listen(0);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(`http://localhost:${srv.address().port}/page.html`);
  await p.waitForFunction('window.ready === true');
  let bad = 0;
  for (const f of process.argv.slice(2)) {
    const r = await p.evaluate((j) => { try { return window.validateFile(j); } catch (e) { return { error: String(e) }; } }, fs.readFileSync(f, 'utf8'));
    if (r.error || r.type !== 'excalidraw') { bad++; console.log('INVALID', path.basename(f), r.error || r.type); }
    else console.log('valid', path.basename(f), 'elements=' + r.count, 'bound-arrows=' + r.bound);
  }
  console.log(bad ? `${bad} invalid` : 'all files load in Excalidraw'); await b.close(); srv.close(); process.exit(bad ? 1 : 0);
})();
