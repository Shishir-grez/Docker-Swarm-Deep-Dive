let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname;
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  const ext = path.extname(p); const types = {'.js':'text/javascript','.woff2':'font/woff2','.css':'text/css','.html':'text/html'};
  res.writeHead(200, {'Content-Type': types[ext]||'application/octet-stream'}); fs.createReadStream(p).pipe(res);
}).listen(0);
(async () => {
  const port = srv.address().port;
  const specs = process.argv.slice(2);           // paths to spec .json files
  const outDir = process.env.OUT || path.join(root, 'out'); fs.mkdirSync(outDir, {recursive:true});
  const b = await chromium.launch(); const ctx = await b.newContext({deviceScaleFactor: 2}); const p = await ctx.newPage();
  p.on('pageerror', e => console.log('PAGEERROR', e.message)); p.on('console', m => { if (m.type()==='error') console.log('CONSOLE', m.text().slice(0,200)); });
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith(`http://localhost:${port}`)) return r.continue(); console.log('BLOCKED external', u.slice(0,100)); return r.abort(); });
  await p.goto(`http://localhost:${port}/page.html`);
  await p.waitForFunction('window.ready === true', null, {timeout: 60000});
  const fok = await p.evaluate(async () => { await Promise.all([document.fonts.load('20px Excalifont','Hello'), document.fonts.load('16px Cascadia','Hello')]); return [document.fonts.check('20px Excalifont'), document.fonts.check('16px Cascadia')]; });
  console.log('fonts loaded:', JSON.stringify(fok));
  for (const f of specs) {
    const name = path.basename(f, '.json');
    const spec = JSON.parse(fs.readFileSync(f, 'utf8'));
    const r = await p.evaluate(async (s) => { try { return await window.renderDiagram(s); } catch (e) { return {error: String(e && e.stack || e)}; } }, spec);
    if (r.error) { console.log(name, 'ERROR', r.error.slice(0,400)); continue; }
    fs.writeFileSync(path.join(outDir, name + '.excalidraw'), r.json);
    fs.writeFileSync(path.join(outDir, name + '.svg'), r.svg);
    if (process.env.PNG !== '0') { // preview PNG (not published)
      const pg = await ctx.newPage();
      await pg.setContent(`<html><body style="margin:0;background:#fff">${r.svg}</body></html>`);
      const el = await pg.$('svg'); await el.screenshot({path: path.join(outDir, name + '.png')}); await pg.close();
    }
    console.log(name, 'ok elements=' + r.count, 'svg=' + r.svg.length + 'B');
  }
  await b.close(); srv.close();
})();
