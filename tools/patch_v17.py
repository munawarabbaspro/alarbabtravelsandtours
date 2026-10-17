# one-off patch: speed – small logo/favicons, versioned assets with long caching, click-to-load map, lighter home page
import io, re
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# versioned asset URLs (hash of file content) so browsers can cache them for a year
rep('''LOGO_SRC = "/assets/logo.png"             # same file, relative for <img> and favicon''', '''import hashlib
def _v(name):
    return hashlib.md5(open(os.path.join(ROOT, "assets", name), "rb").read()).hexdigest()[:8]
LOGO_SRC = f"/assets/logo-80.png?v={_v('logo-80.png')}"   # 80px header logo (~3 KB)
ICON32 = f"/assets/icon-32.png?v={_v('icon-32.png')}"
ICON192 = f"/assets/icon-192.png?v={_v('icon-192.png')}"
APPJS = f"/assets/app.js?v={_v('app.js')}"''')
rep('''<link rel="icon" type="image/png" href="{LOGO_SRC}"><link rel="apple-touch-icon" href="{LOGO_SRC}">''',
    '''<link rel="icon" type="image/png" sizes="32x32" href="{ICON32}"><link rel="apple-touch-icon" href="{ICON192}">''')
rep('''<script src="/assets/app.js" defer></script>''', '''<script src="{APPJS}" defer></script>''')
rep('''    shutil.copy(os.path.join(ROOT, "assets", "logo.png"), os.path.join(OUT, "assets", "logo.png"))''',
    '''    for _f in ("logo.png", "logo-80.png", "icon-32.png", "icon-192.png"):
        shutil.copy(os.path.join(ROOT, "assets", _f), os.path.join(OUT, "assets", _f))''')

# long-lived caching for versioned assets (all hosts)
rep('''"/assets/*\\n  Cache-Control: public, max-age=604800\\n''', '''"/assets/*\\n  Cache-Control: public, max-age=31536000, immutable\\n''')
rep('''{"key": "Cache-Control", "value": "public, max-age=604800"}''', '''{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}''')
rep('''ExpiresByType application/javascript "access plus 7 days"''', '''ExpiresByType application/javascript "access plus 1 year"
ExpiresByType image/png "access plus 1 year"''')

# click-to-load map (Google Maps iframe is heavy; load it only when asked)
GM = 'https://www.google.com/maps?q=Eagle%20Plaza%2C%20Fazal-e-Haq%20Road%2C%20Blue%20Area%2C%20Islamabad&amp;output=embed'
n = 0
for m in list(re.finditer(r'<iframe class="map" title="([^"]*)" loading="lazy" src="' + re.escape(GM) + r'"></iframe>', s)):
    s = s.replace(m.group(0), f'<div class="map map-facade" data-src="{GM}" data-title="{m.group(1)}"><button type="button" class="btn light">📍 Show map</button><span>Eagle Plaza, Fazal-e-Haq Road, Blue Area, Islamabad</span></div>', 1)
    n += 1
assert n == 2, n

# home: build the destination suggestions in JS from window.FIND instead of repeating every name in HTML
rep('''<input id="to" name="to" list="destlist" placeholder="Thailand, Dubai, Germany…" required autocomplete="off"><datalist id="destlist">{datalist}</datalist>''',
    '''<input id="to" name="to" list="destlist" placeholder="Thailand, Dubai, Germany…" required autocomplete="off"><datalist id="destlist"></datalist>''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v17")
