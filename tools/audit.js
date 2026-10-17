// content audit for dist/: inline CSS size, word counts per page type, near-duplicate pages
const fs = require('fs'), path = require('path');
const D = path.join(__dirname, '..', 'dist');
const files = [];
(function w(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) w(p); else if (f.endsWith('.html')) files.push(p) } })(D);
const rel = f => '/' + path.relative(D, f).split(path.sep).join('/');
const text = f => { const h = fs.readFileSync(f, 'utf8'); const m = h.match(/<main[\s\S]*<\/main>/); return m ? m[0].replace(/<script[\s\S]*?<\/script>/g, '').replace(/<[^>]+>/g, ' ') : '' };
const words = f => text(f).split(/\s+/).filter(Boolean).length;
const css = fs.readFileSync(path.join(D, 'index.html'), 'utf8').match(/<style>([\s\S]*?)<\/style>/)[1].length;
const rows = files.map(f => [rel(f), words(f)]).sort((a, b) => a[1] - b[1]);
const avg = rs => Math.round(rs.reduce((a, b) => a + b[1], 0) / (rs.length || 1));
const vis = rows.filter(r => r[0].includes('/visa/'));
const ctry = rows.filter(r => /^\/countries\/[^/]+\/[^/]+\/index/.test(r[0]) && !r[0].includes('/visa/'));
// near-duplicates: shingle similarity between region visa pages
const sh = f => { const w = text(f).toLowerCase().split(/\s+/).filter(Boolean); const s = new Set(); for (let i = 0; i < w.length - 4; i++) s.add(w.slice(i, i + 5).join(' ')); return s };
const vf = files.filter(f => rel(f).includes('/visa/visit-visa'));
let maxSim = 0;
for (let i = 0; i < vf.length; i++) for (let j = i + 1; j < vf.length; j++) { const a = sh(vf[i]), b = sh(vf[j]); let n = 0; for (const x of a) if (b.has(x)) n++; maxSim = Math.max(maxSim, n / Math.min(a.size, b.size)) }
console.log(JSON.stringify({ pages: files.length, inlineCssKB: +(css / 1024).toFixed(1), lowest: rows.slice(0, 10), regionVisaPages: vis.length, regionVisaAvgWords: avg(vis),
  countryPages: ctry.length, countryAvgWords: avg(ctry), visitVisaPagesMaxSimilarity: +maxSim.toFixed(2) }, null, 1));
