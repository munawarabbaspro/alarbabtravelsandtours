// Full content/markup QA over every page in dist/
const fs = require('fs'), path = require('path');
const D = path.join(__dirname, '..', 'dist');
const files = [];
(function w(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) w(p); else if (f.endsWith('.html')) files.push(p) } })(D);
const issues = {}; const add = (k, where, ex) => { (issues[k] = issues[k] || { count: 0, examples: [] }).count++; if (issues[k].examples.length < 4) issues[k].examples.push(where + (ex ? ' :: ' + ex : '')) };
for (const f of files) {
  const rel = '/' + path.relative(D, f).split(path.sep).join('/');
  const h = fs.readFileSync(f, 'utf8');
  const body = h.replace(/<script[\s\S]*?<\/script>/g, '').replace(/<style[\s\S]*?<\/style>/g, '');
  const text = body.replace(/<[^>]+>/g, '\n').replace(/&amp;/g, '&').replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"');
  // template / data leftovers
  for (const [k, re] of [['empty parentheses', /\(\s*\)/], ['space before punctuation', /\w \s*[,.;:](?=\s|$)/m], ['double space in text', /\S  +\S/],
    ['"undefined"/"None"/"null"', /\b(undefined|None|null|NaN)\b/], ['template braces', /\{\{|\}\}|\{[a-z_]+\}/], ['double-escaped entity', /&amp;(amp|quot|#)/],
    ['dangling connector', /\b(and|or|with|for|of|the)\s*[.,]/i], ['lowercase sentence start', /[.!?]\s+[a-z]{3,}/]]) {
    const src = k === 'double-escaped entity' ? body : text;
    const m = src.match(re); if (m) add(k, rel, src.slice(Math.max(0, m.index - 40), m.index + 40).replace(/\s+/g, ' '));
  }
  // duplicate ids
  const ids = [...body.matchAll(/\sid="([^"]+)"/g)].map(m => m[1]); const dup = ids.filter((x, i) => ids.indexOf(x) !== i); if (dup.length) add('duplicate id', rel, [...new Set(dup)].join(','));
  // headings
  const hs = [...body.matchAll(/<h([1-6])[^>]*>([\s\S]*?)<\/h\1>/g)].map(m => [+m[1], m[2].replace(/<[^>]+>/g, '').trim()]);
  hs.forEach(([l, t]) => { if (!t) add('empty heading', rel, 'h' + l) });
  for (let i = 1; i < hs.length; i++) if (hs[i][0] > hs[i - 1][0] + 1) { add('heading level skipped', rel, `h${hs[i - 1][0]} → h${hs[i][0]} "${hs[i][1].slice(0, 30)}"`); break }
  const h2 = hs.filter(x => x[0] === 2).map(x => x[1].toLowerCase()); const d2 = h2.filter((x, i) => h2.indexOf(x) !== i); if (d2.length) add('duplicate h2 text', rel, d2[0]);
  // images
  for (const m of body.matchAll(/<img\b[^>]*>/g)) { const t = m[0];
    if (!/\swidth="\d+"/.test(t) || !/\sheight="\d+"/.test(t)) add('img without width/height (CLS)', rel, t.slice(0, 90));
    if (!/\salt="/.test(t)) add('img without alt', rel, t.slice(0, 90)); }
  const firstImg = (body.match(/<div class="(?:pic|blob)[^"]*"[^>]*>\s*<img\b[^>]*>/) || [''])[0];
  if (/loading="lazy"/.test(firstImg)) add('hero image lazy-loaded (hurts LCP)', rel);
  // links
  for (const m of body.matchAll(/<a\b[^>]*>/g)) { const t = m[0];
    if (/target="_blank"/.test(t) && !/rel="[^"]*noopener/.test(t)) add('target=_blank without noopener', rel, t.slice(0, 80));
    if (/href=""/.test(t) || /href="#"/.test(t)) add('empty href', rel, t.slice(0, 80)); }
  const anchors = [...body.matchAll(/<a\b[^>]*>([\s\S]*?)<\/a>/g)].filter(m => !m[1].replace(/<[^>]+>/g, '').trim() && !/aria-label=/.test(m[0]) && !/<img[^>]+alt="[^"]+"/.test(m[1]));
  if (anchors.length) add('link with no accessible name', rel, anchors[0][0].slice(0, 80));
  // forms
  for (const m of body.matchAll(/<(input|select|textarea)\b[^>]*id="([^"]+)"[^>]*>/g)) if (!new RegExp(`for="${m[2]}"`).test(body) && !/aria-label=/.test(m[0]) && !/type="hidden"/.test(m[0])) add('form field without label', rel, m[2]);
  // fees / IATA policy guards
  if (/\bIATA\b/.test(text)) add('IATA mentioned', rel);
  const fee = text.match(/(?:visa\s+fee|embassy\s+fee)[^\n]{0,20}?\d/i) || text.match(/PKR\s?\d{2,3},\d{3}/); if (fee) add('fee/price amount', rel, fee[0]);
  if (/work permit/i.test(text)) add('work permit mentioned', rel);
}
const out = Object.fromEntries(Object.entries(issues).sort((a, b) => b[1].count - a[1].count));
console.log(JSON.stringify({ pages: files.length, issueTypes: Object.keys(out).length, issues: out }, null, 1));
