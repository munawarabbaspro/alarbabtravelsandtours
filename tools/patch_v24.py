# apply footer Design A (CTA band + dark columns) site-wide
import io, re
P = "build.py"; s = io.open(P, encoding="utf-8").read()

# 1. social buttons with brand colours (replaces the old soc line)
old_soc = [l for l in s.split("\n") if l.startswith("    soc = ") and "SOCIAL" in l][0]
new_soc = '''    SB = {"fb": "#1877F2", "ig": "linear-gradient(45deg,#f9ce34,#ee2a7b 55%,#6228d7)", "x": "#000", "in": "#0A66C2"}
    soc = "".join(f'<a class="sb" style="background:{SB[s_]}" href="{u}" target="_blank" rel="noopener me" aria-label="{n}">{ico(s_, 18, "#fff")}</a>' for s_, u, n in SOCIAL)
    regions = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in reg)
    company = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in co)'''
s = s.replace(old_soc, new_soc, 1)
# the line order matters: reg/co are defined after soc in the old code, so move our 2 lines after `li = ...`
s = s.replace('''    regions = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in reg)
    company = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in co)\n''', "", 1)
s = s.replace('''    li = lambda xs: "".join(f'<li><a href="{u}">{e(n)}</a></li>' for u, n in xs)
    return f\'\'\'<footer>''', '''    li = lambda xs: "".join(f'<li><a href="{u}">{e(n)}</a></li>' for u, n in xs)
    regions = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in reg)
    company = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in co)
    return f\'\'\'<footer>''', 1)

# 2. footer markup
a = s.index("<footer>\n  <div class=\"cols\">"); b = s.index("</footer>", a) + len("</footer>")
markup = '''<footer class="fA">
  <div class="fa-cta"><div><h2>Planning a visa or trip?</h2><p>Send your documents on WhatsApp. An adviser checks them for free and replies within one business hour.</p></div>
    <div class="fa-btns"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">💬 WhatsApp {PHONE_D}</a><a class="btn light" href="tel:{PHONE_I}">📞 Call now</a></div></div>
  <div class="fa-body">
    <div class="fa-grid">
      <div class="fa-brand"><span class="lgt"><img src="{LOGO_SRC}" alt="" width="34" height="27" loading="lazy"></span><h2 class="fh big">{NAME}</h2>
        <p>DTS-licensed travel agency and visa consultancy in Blue Area, Islamabad, serving travellers since 2009.</p>
        <div class="badges"><span>DTS Licensed</span><span>15+ Years</span><span>Blue Area, Islamabad</span></div><div class="fa-soc">{soc}</div></div>
      <div><h2 class="fh">Services</h2><ul>{li(svc)}</ul></div>
      <div><h2 class="fh">Popular visas &amp; trips</h2><ul>{li(POPULAR)}</ul></div>
      <div><h2 class="fh">Visit us</h2><ul class="fa-contact">
        <li>{ico("pin", 18, "#ff7a6b")}<a href="{MAP_URL}" target="_blank" rel="noopener">{ADDR}</a></li>
        <li>{ico("phone", 17, "#7fb3ff")}<span><a href="tel:{PHONE_I}">{PHONE_D}</a> · <a href="tel:{LAND_I}">{LAND}</a></span></li>
        <li>{ico("clock", 18, "#c9d2d0")}<span>{HOURS}</span></li>
        <li>{ico("gmail", 18, None)}<a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
    </div>
    <div class="fa-more"><div><h2 class="fh">Browse by region</h2><p class="fl">{regions}</p></div><div><h2 class="fh">Company &amp; guides</h2><p class="fl">{company}</p></div></div>
    <div class="fa-bottom"><span>© 2026 {NAME}. All rights reserved.</span><span class="fa-dts">DTS licensed travel agency · Islamabad, Pakistan</span></div>
  </div>
</footer>'''
s = s[:a] + markup + s[b:]
io.open(P, "w", encoding="utf-8").write(s)

# 3. CSS: drop the old footer rules, add Design A
c = io.open("assets/style.css", encoding="utf-8").read()
c = "\n".join(l for l in c.split("\n") if not re.match(r"^footer[ .{]", l))
c = c.replace("  footer .cols{grid-template-columns:1fr 1fr}\n", "")
c = c.replace(",footer .cols{grid-template-columns:1fr}", "")
c = c.replace("  footer{padding:34px 22px 22px}.band{padding:24px}", "  .band{padding:24px}")
c += '''
/* v10: footer design A */
footer.fA{margin:70px auto 0;width:min(1240px,100%);background:var(--ink);color:#d9ebe6;border-radius:38px 38px 0 0;overflow:hidden}
.fa-cta{margin:14px;border-radius:28px;background:linear-gradient(120deg,#2fd1b0,#1d8a73 55%,#255246);color:var(--ink);padding:30px 34px;display:flex;gap:22px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.fa-cta h2{font:900 clamp(24px,3vw,34px)/1.05 Archivo,sans-serif;text-transform:uppercase}
.fa-cta p{font-size:14px;max-width:520px;margin-top:8px;color:#06231d;line-height:1.6}
.fa-btns{display:flex;gap:10px;flex-wrap:wrap}.fa-btns .btn.light{background:#fff;color:var(--ink)}
.fa-body{padding:28px 40px 22px}
.fa-grid{display:grid;grid-template-columns:1.3fr 1fr 1fr 1.4fr;gap:34px}
.fA h2.fh{font:800 12px Archivo,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#fff;margin-bottom:14px}
.fA h2.fh.big{font:800 16px Archivo,sans-serif;letter-spacing:.02em;margin:14px 0 8px}
.fA p{font-size:13px;line-height:1.7}.fA ul{list-style:none;display:grid;gap:9px;font-size:13px}
.fA a:hover{color:var(--teal)}
.lgt{width:46px;height:46px;border-radius:14px;background:#fff;display:grid;place-items:center;box-shadow:0 2px 8px rgba(0,0,0,.2)}.lgt img{width:34px;height:auto}
.fA .badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.fA .badges span{font-size:11px;font-weight:700;letter-spacing:.06em;background:rgba(255,255,255,.1);padding:6px 12px;border-radius:999px}
.fa-soc{display:flex;gap:9px;margin-top:16px}
a.sb{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;transition:.2s;color:#fff}a.sb:hover{transform:translateY(-3px);color:#fff}
.fa-contact li{display:flex;gap:10px;align-items:flex-start;line-height:1.5}.fa-contact svg{margin-top:2px}
.fa-more{display:grid;grid-template-columns:1fr 1fr;gap:34px;margin-top:30px;padding-top:24px;border-top:1px solid rgba(255,255,255,.12)}
.fa-more .fl{display:flex;flex-wrap:wrap;gap:4px 18px;font-size:12.5px;line-height:1.5}.fa-more .fl a{padding-block:5px}
.fa-bottom{margin-top:22px;padding-top:18px;border-top:1px solid rgba(255,255,255,.12);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:12px;color:#9db3ae;align-items:center}
.fa-dts{background:rgba(47,209,176,.15);color:#7ff0d6;padding:5px 12px;border-radius:999px;font-weight:700}
@media(max-width:1000px){.fa-grid{grid-template-columns:1fr 1fr}}
@media(max-width:600px){.fa-grid,.fa-more{grid-template-columns:1fr}.fa-body{padding-inline:20px}.fa-cta{padding:24px 22px}}
'''
io.open("assets/style.css", "w", encoding="utf-8").write(c)
print("footer A applied")
