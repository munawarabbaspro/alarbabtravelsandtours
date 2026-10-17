// One-off: pulls the content data out of the old site's JS bundle into data/site-data.json
// usage: node tools/extract.js <path-to-bundle.js>
const fs = require('fs'), path = require('path');
const t = fs.readFileSync(process.argv[2], 'utf8');

function grabAt(i) {
  const open = t[i], close = open === '[' ? ']' : '}';
  let d = 0, s = null;
  for (let j = i; j < t.length; j++) {
    const c = t[j];
    if (s) { if (c === '\\') { j++; continue } if (c === s) s = null; continue }
    if (c === '"' || c === "'" || c === '`') { s = c; continue }
    if (c === open) d++; else if (c === close) { d--; if (d === 0) return t.slice(i, j + 1) }
  }
}
const at = (decl) => { const i = t.indexOf(decl); if (i < 0) throw new Error('missing ' + decl); return i + decl.indexOf('=') + 1 };
const mk = k => { const f = function () { return f }; f.toJSON = () => '$' + String(k); return f };
const vars = {};
const scope = new Proxy(vars, {
  has: (o, k) => typeof k === 'string',
  get: (o, k) => k === Symbol.unscopables ? undefined : (k in o ? o[k] : (['Math', 'JSON', 'String', 'Number', 'Array', 'Object'].includes(k) ? globalThis[k] : mk(k)))
});
const ev = src => new Function('s', 'with(s){return (' + src + ')}')(scope);
const arr = (name, firstKey, extra = '') => ev(grabAt(at(`${name}=[{${firstKey}:${extra}`)));

const map = {
  pg: ['schengen', 'slug'], fg: ['south-asia', 'slug'], hg: ['central-asia', 'slug'], gg: ['north-africa', 'slug'],
  xg: ['southern-africa', 'slug'], bg: ['middle-east', 'slug'], vg: ['east-asia', 'slug'], vw: ['mexico', 'slug'],
  yw: ['ireland', 'slug'], yg: ['south-america', 'slug'], wg: ['oceania', 'slug']
};
const countries = {};
for (const [v, [name, k]] of Object.entries(map)) { vars[v] = arr(v, k); countries[name] = vars[v] }
vars.Ha = ev('n=>' + grabAt(t.indexOf('Ha=n=>') + 6));
const regions = arr('Zd', 'slug');

const out = {
  brand: ev(grabAt(at('F={name:"AL ARBAB'))),
  services: arr('ow', 'title'),
  countries, regions,
  visaTypeTemplate: vars.Ha('{{C}}'),
  umrah: arr('bh', 'title'),
  insurance: arr('n', 'name', '"Jubilee'),
  airlines: arr('yd', 'name'),
  faqSchengenGeneral: arr('Xh', 'q'),
  faqAir: arr('Zh', 'q'),
  heroDest: arr('at', 'id'),
  packages: arr('Vi', 'id'),
  visaDest: arr('Xj', 'id'),
};
const dst = path.join(__dirname, '..', 'data', 'site-data.json');
fs.mkdirSync(path.dirname(dst), { recursive: true });
fs.writeFileSync(dst, JSON.stringify(out, null, 1));
const sz = {}; for (const k in out) sz[k] = JSON.stringify(out[k]).length;
console.log(sz, Object.fromEntries(Object.entries(countries).map(([k, v]) => [k, v.length])));
