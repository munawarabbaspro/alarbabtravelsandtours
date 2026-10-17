# Generates dist/_footer-preview.html: three footer designs stacked, using the site's real data, icons and CSS.
# usage: py tools/footer_preview.py   (run after build.py, then open /_footer-preview.html)
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build as B   # module-level code only loads data; nothing is written

ico, e = B.ico, B.e
SOC = {"fb": ("#1877F2", "Facebook"), "ig": ("linear-gradient(45deg,#f9ce34,#ee2a7b 55%,#6228d7)", "Instagram"), "x": ("#000", "X"), "in": ("#0A66C2", "LinkedIn")}
soc_urls = {k: u for k, u, n in B.SOCIAL}

def soc_buttons(cls):
    return "".join(f'<a class="{cls}" style="background:{SOC[k][0]}" href="{soc_urls[k]}" target="_blank" rel="noopener me" aria-label="{SOC[k][1]}">{ico(k, 18, "#fff")}</a>' for k in ("fb", "ig", "x", "in"))

SERV = [("/visa-services", "Visa Consultancy"), ("/air-ticketing", "Air Ticketing"), ("/umrah", "Umrah Packages"), ("/packages", "Holiday Packages"), ("/honeymoon-packages", "Honeymoon Packages"),
        ("/hotel-booking", "Hotel Bookings"), ("/travel-insurance", "Travel Insurance"), ("/visa-appointments", "Visa Appointments"), ("/eligibility-check", "Free Eligibility Check")]
DEST = [("/countries/schengen", "Schengen"), ("/countries/united-kingdom", "United Kingdom"), ("/countries/united-states", "United States"), ("/countries/canada", "Canada"),
        ("/countries/middle-east/united-arab-emirates", "Dubai"), ("/countries/central-asia/turkey", "Turkey"), ("/countries/south-asia/malaysia", "Malaysia"), ("/countries/south-asia/thailand", "Thailand"),
        ("/countries", "All 86 destinations")]
COMP = [("/about", "About us"), ("/contact", "Contact"), ("/guides", "Visa guides"), ("/editorial-policy", "Editorial policy"), ("/travel-agency-islamabad", "Travel agency Islamabad"),
        ("/travel-agency-rawalpindi", "Travel agency Rawalpindi"), ("/privacy", "Privacy"), ("/terms", "Terms")]
li = lambda xs: "".join(f'<li><a href="{u}">{e(n)}</a></li>' for u, n in xs)
logo = '<span class="lgt"><img src="/assets/logo-80.png" alt="" width="34" height="27"></span>'

def tile(cls, icon, label, value, href):
    return f'<a class="ct {cls}" href="{href}" target="_blank" rel="noopener"><span class="cti">{icon}</span><span><small>{label}</small><b>{value}</b></span></a>'

IC_MAP, IC_CALL, IC_MAIL, IC_WA, IC_FB = ico("pin", 24, "#EA4335"), ico("phone", 22, "#fff"), ico("gmail", 24, None), ico("wa", 24, "#fff"), ico("fb", 24, "#1877F2")

# ---------------------------------------------------------------- A: call-to-action band + dark columns
A = f'''<footer class="fA">
  <div class="fa-cta"><div><h2>Planning a visa or trip?</h2><p>Send your documents on WhatsApp. An adviser checks them for free and replies within one business hour.</p></div>
    <div class="fa-btns"><a class="btn wa" href="{B.WA}">{ico("wa", 18)} WhatsApp {e(B.PHONE_D)}</a><a class="btn light" href="tel:{B.PHONE_I}">{ico("phone", 17)} Call now</a></div></div>
  <div class="fa-body">
    <div class="fa-grid">
      <div class="fa-brand">{logo}<h3>{e(B.NAME)}</h3><p>DTS-licensed travel agency and visa consultancy in Blue Area, Islamabad, serving travellers since 2009.</p>
        <div class="fa-soc">{soc_buttons("sb")}</div></div>
      <div><h3>Services</h3><ul>{li(B.SERV if hasattr(B, "SERV") else SERV)}</ul></div>
      <div><h3>Destinations</h3><ul>{li(DEST)}</ul></div>
      <div><h3>Visit us</h3><ul class="fa-contact">
        <li>{ico("pin", 18, "#ff7a6b")}<a href="{B.MAP_URL}">{e(B.ADDR)}</a></li>
        <li>{ico("phone", 17, "#7fb3ff")}<span><a href="tel:{B.PHONE_I}">{e(B.PHONE_D)}</a> · <a href="tel:{B.LAND_I}">{e(B.LAND)}</a></span></li>
        <li>{ico("clock", 18, "#c9d2d0")}<span>{e(B.HOURS)}</span></li>
        <li>{ico("gmail", 18, None)}<a href="mailto:{B.EMAIL}">{e(B.EMAIL)}</a></li></ul></div>
    </div>
    <div class="fa-bottom"><span>© 2026 {e(B.NAME)}</span><span class="fa-links"><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="/sitemap">Sitemap</a></span><span class="fa-dts">DTS licensed</span></div>
  </div></footer>'''

# ---------------------------------------------------------------- B: light sage panel (matches the hero shell)
B_ = f'''<footer class="fB"><div class="fb-in">
  <div class="fb-top">
    <div class="fb-intro">{logo}<h3>{e(B.NAME)}</h3><p>Visas, air tickets, Umrah and tours from one office in Blue Area, Islamabad. Free file check before you pay anything.</p>
      <div class="fb-tiles">
        {tile("t-map", IC_MAP, "Office", "Eagle Plaza, Blue Area", B.MAP_URL)}
        {tile("t-call", IC_CALL, "Call", e(B.PHONE_D), "tel:" + B.PHONE_I)}
        {tile("t-wa", IC_WA, "WhatsApp", "Chat with an adviser", B.WA)}
        {tile("t-mail", IC_MAIL, "Email", "alarbabtravels@gmail.com", "mailto:" + B.EMAIL)}</div></div>
    <div class="fb-map"><div><small>OPEN {e(B.HOURS.split(": ")[0].upper())}</small><b>{e(B.HOURS.split(": ")[1])}</b><span>{e(B.ADDR)}</span></div><a class="btn" href="{B.MAP_URL}">{ico("pin", 16)} Open in Google Maps</a></div>
  </div>
  <div class="fb-cols"><div><h3>Services</h3><ul>{li(SERV)}</ul></div><div><h3>Destinations</h3><ul>{li(DEST)}</ul></div><div><h3>Company</h3><ul>{li(COMP)}</ul></div></div>
  <div class="fb-bottom"><span>© 2026 {e(B.NAME)} · DTS licensed</span><span class="fb-soc">{soc_buttons("sb")}</span></div>
</div></footer>'''

# ---------------------------------------------------------------- C: big headline, contact tiles, giant wordmark
C = f'''<footer class="fC">
  <div class="fc-head"><h2>Let's plan your<br>journey.</h2><a class="btn wa" href="{B.WA}">{ico("wa", 18)} Start on WhatsApp</a></div>
  <div class="fc-tiles">
    {tile("t-map", IC_MAP, "Office", "Eagle Plaza, Fazal-e-Haq Rd", B.MAP_URL)}{tile("t-call", IC_CALL, "Call", e(B.PHONE_D), "tel:" + B.PHONE_I)}
    {tile("t-wa", IC_WA, "WhatsApp", "Free file check", B.WA)}{tile("t-mail", IC_MAIL, "Email", "alarbabtravels@gmail.com", "mailto:" + B.EMAIL)}{tile("t-fb", IC_FB, "Facebook", "alarbabtravels", soc_urls["fb"])}</div>
  <div class="fc-cols"><div><h3>Services</h3><ul>{li(SERV)}</ul></div><div><h3>Destinations</h3><ul>{li(DEST)}</ul></div><div><h3>Company</h3><ul>{li(COMP)}</ul></div>
    <div><h3>Hours</h3><p>{e(B.HOURS)}</p><div class="fc-soc">{soc_buttons("sb")}</div></div></div>
  <div class="fc-word" aria-hidden="true">AL ARBAB</div>
  <div class="fc-bottom"><span>© 2026 {e(B.NAME)}</span><span>DTS licensed travel agency · Islamabad, Pakistan</span></div>
</footer>'''

CSS = open(os.path.join(ROOT, "assets", "style.css"), encoding="utf-8").read()
EXTRA = r'''
body{padding:20px 16px 60px}
.pv{max-width:1240px;margin:0 auto 70px}
.pv>h1{font-size:26px;text-transform:uppercase;margin:34px 0 6px}.pv>p.lead{margin-bottom:18px;color:#2c3d39;font-size:14px;max-width:640px}
.tag{display:inline-block;background:var(--ink);color:#fff;border-radius:999px;padding:6px 14px;font:700 12px Inter;letter-spacing:.08em;margin-bottom:10px}
.pv footer{margin:0;width:100%}
.lgt{width:46px;height:46px;border-radius:14px;background:#fff;display:grid;place-items:center;box-shadow:0 2px 8px rgba(0,0,0,.2)}.lgt img{width:34px;height:auto}
a.sb{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;transition:.2s}a.sb:hover{transform:translateY(-3px)}
.ct{display:flex;gap:12px;align-items:center;border-radius:18px;padding:12px 14px;min-width:0;transition:.2s}.ct:hover{transform:translateY(-3px)}
.ct small{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;opacity:.65}.ct b{font-size:14px;display:block;overflow-wrap:anywhere}
.cti{width:44px;height:44px;border-radius:14px;display:grid;place-items:center;flex:none;background:#fff;box-shadow:inset 0 0 0 1px rgba(80,102,97,.2)}
.t-call .cti{background:#1a73e8}.t-wa .cti{background:#25D366}

/* A */
.fA{background:var(--ink);color:#d9ebe6;border-radius:38px;overflow:hidden}
.fa-cta{margin:14px;border-radius:28px;background:linear-gradient(120deg,#2fd1b0,#1d8a73 55%,#255246);color:var(--ink);padding:30px 34px;display:flex;gap:22px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.fa-cta h2{font:900 clamp(24px,3vw,34px)/1.05 Archivo;text-transform:uppercase}.fa-cta p{font-size:14px;max-width:520px;margin-top:8px;color:#06231d}
.fa-btns{display:flex;gap:10px;flex-wrap:wrap}.fa-btns .btn.light{background:#fff}
.fa-body{padding:28px 40px 24px}
.fa-grid{display:grid;grid-template-columns:1.3fr 1fr 1fr 1.4fr;gap:34px}
.fA h3{font:800 12px Archivo;letter-spacing:.14em;text-transform:uppercase;color:#fff;margin-bottom:14px}
.fa-brand h3{font:800 16px Archivo;letter-spacing:.02em;margin:14px 0 8px}
.fA p{font-size:13px;line-height:1.7}.fA ul{list-style:none;display:grid;gap:9px;font-size:13px}.fA a:hover{color:var(--teal)}
.fa-soc{display:flex;gap:9px;margin-top:16px}
.fa-contact li{display:flex;gap:10px;align-items:flex-start;line-height:1.5}.fa-contact svg{margin-top:2px}
.fa-bottom{margin-top:28px;padding-top:18px;border-top:1px solid rgba(255,255,255,.12);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:12px;color:#9db3ae;align-items:center}
.fa-links{display:flex;gap:18px}.fa-dts{background:rgba(47,209,176,.15);color:#7ff0d6;padding:5px 12px;border-radius:999px;font-weight:700}

/* B */
.fB{background:var(--shell);border-radius:38px;padding:12px;box-shadow:0 30px 60px -20px rgba(9,20,19,.35);color:var(--ink)}
.fb-in{background:var(--panel);border-radius:28px;padding:30px 30px 22px}
.fb-top{display:grid;grid-template-columns:1.5fr 1fr;gap:20px}
.fb-intro h3{font:900 22px Archivo;text-transform:uppercase;margin:14px 0 6px}.fb-intro p{font-size:13.5px;color:#2c3d39;max-width:480px;line-height:1.65}
.fb-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr));gap:10px;margin-top:18px}
.fb-tiles .ct{background:var(--card);box-shadow:inset 0 0 0 1px rgba(80,102,97,.14)}.fb-tiles .ct:hover{background:#fff}
.fb-map{border-radius:24px;background:linear-gradient(145deg,var(--ink),var(--green));color:#fff;padding:24px;display:flex;flex-direction:column;justify-content:space-between;gap:16px;min-height:200px}
.fb-map small{letter-spacing:.12em;font-weight:700;font-size:11px;color:#7ff0d6}.fb-map b{display:block;font:800 22px/1.15 Archivo;margin:6px 0 8px}.fb-map span{font-size:13px;opacity:.85}
.fb-map .btn{background:#fff;color:var(--ink);align-self:flex-start}
.fb-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}
.fb-cols>div{background:var(--card);border-radius:22px;padding:20px 22px}
.fB h3{font:800 12px Archivo;letter-spacing:.14em;text-transform:uppercase;margin-bottom:12px;color:var(--green)}
.fB ul{list-style:none;display:grid;gap:8px;font-size:13px}.fB ul a:hover{color:var(--green);text-decoration:underline}
.fb-bottom{margin-top:20px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center;font-size:12px;color:var(--mid)}.fb-soc{display:flex;gap:8px}

/* C */
.fC{background:#0a1514;color:#d9ebe6;border-radius:38px;padding:46px 40px 0;overflow:hidden;position:relative}
.fc-head{display:flex;justify-content:space-between;align-items:end;gap:20px;flex-wrap:wrap}
.fc-head h2{font:900 clamp(34px,6vw,72px)/.95 Archivo;text-transform:uppercase;color:#fff}
.fc-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(230px,100%),1fr));gap:10px;margin-top:30px}
.fc-tiles .ct{background:rgba(255,255,255,.07);color:#fff}.fc-tiles .ct:hover{background:rgba(255,255,255,.14)}.fc-tiles .ct small{opacity:.6}
.fc-cols{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:30px;margin-top:40px}
.fC h3{font:800 12px Archivo;letter-spacing:.14em;text-transform:uppercase;color:#7ff0d6;margin-bottom:14px}
.fC ul{list-style:none;display:grid;gap:9px;font-size:13px}.fC a:hover{color:var(--teal)}.fC p{font-size:13px;line-height:1.7}
.fc-soc{display:flex;gap:9px;margin-top:16px}
.fc-word{font:900 clamp(70px,17vw,230px)/.8 Archivo;letter-spacing:-.02em;color:transparent;-webkit-text-stroke:1.5px rgba(255,255,255,.16);margin:34px 0 -.12em;white-space:nowrap;user-select:none}
.fc-bottom{position:relative;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:12px;color:#9db3ae;padding:16px 0 20px;border-top:1px solid rgba(255,255,255,.1);background:#0a1514}

@media(max-width:1000px){.fa-grid,.fc-cols{grid-template-columns:1fr 1fr}.fb-top{grid-template-columns:1fr}.fb-cols{grid-template-columns:1fr 1fr}}
@media(max-width:600px){.fa-grid,.fc-cols,.fb-cols{grid-template-columns:1fr}.fa-body,.fC{padding-inline:20px}.fa-cta{padding:24px 22px}.fb-in{padding:22px 18px}}
'''
OUT = os.path.join(ROOT, "dist", "_footer-preview.html")
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Footer designs</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800;900&family=Inter:wght@400;600;700&display=swap"><style>{CSS}{EXTRA}</style></head><body>
<div class="pv"><span class="tag">DESIGN A</span><h1>Call-to-action band + dark columns</h1><p class="lead">A big teal banner pushes visitors to WhatsApp or call first, then a dark footer with colored social buttons and contact details.</p>{A}</div>
<div class="pv"><span class="tag">DESIGN B</span><h1>Light panel, matches the hero</h1><p class="lead">Same rounded sage shell as the top of the site. Brand-colored contact tiles, an hours-and-map card and link groups in soft cards.</p>{B_}</div>
<div class="pv"><span class="tag">DESIGN C</span><h1>Big headline + giant wordmark</h1><p class="lead">A bold "Let's plan your journey" headline, five contact tiles, link columns and an outlined AL ARBAB wordmark at the bottom.</p>{C}</div>
</body></html>'''
html = B.finish_icons(html)
open(OUT, "w", encoding="utf-8").write(html)
print("written", OUT, len(html) // 1024, "KB")
