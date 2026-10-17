// internal-link audit for dist/: inbound links per page (excluding header/footer), click depth from home, orphans
const fs = require('fs'), path = require('path');
const D = path.join(__dirname, '..', 'dist');
const files = [];
(function w(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) w(p); else if (f === 'index.html') files.push(p) } })(D);
const url = f => { const r = '/' + path.relative(D, path.dirname(f)).split(path.sep).join('/'); return r === '/' ? '/' : r };
const norm = h => { h = h.split('#')[0].split('?')[0]; if (h.length > 1) h = h.replace(/\/$/, ''); return h };
const pages = Object.fromEntries(files.map(f => [url(f), fs.readFileSync(f, 'utf8')]));
const inb = {}, out = {};
for (const u in pages) { inb[u] = new Set(); }
for (const [u, h] of Object.entries(pages)) {
  const body = h.replace(/<header[\s\S]*?<\/header>/, '').replace(/<footer[\s\S]*?<\/footer>/, '');   // contextual links only
  const links = new Set([...body.matchAll(/href="(\/[^"]*)"/g)].map(m => norm(m[1])).filter(l => l in pages && l !== u));
  out[u] = links; for (const l of links) inb[l].add(u);
}
// click depth via BFS using ALL links (incl. nav/footer)
const all = {}; for (const [u, h] of Object.entries(pages)) all[u] = new Set([...h.matchAll(/href="(\/[^"]*)"/g)].map(m => norm(m[1])).filter(l => l in pages));
const depth = { '/': 0 }, q = ['/'];
while (q.length) { const u = q.shift(); for (const l of all[u]) if (!(l in depth)) { depth[l] = depth[u] + 1; q.push(l) } }
const rows = Object.keys(pages).map(u => [u, inb[u].size, depth[u] ?? 'unreachable']).sort((a, b) => a[1] - b[1]);
const hist = {}; for (const r of rows) hist[r[2]] = (hist[r[2]] || 0) + 1;
console.log(JSON.stringify({ pages: rows.length, depthHistogram: hist, fewestContextualInlinks: rows.slice(0, 15), zeroContextual: rows.filter(r => r[1] === 0).map(r => r[0]) }, null, 1));
