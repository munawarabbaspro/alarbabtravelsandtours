# one-off patch: replace glass gcard with the dark "collectible" card from the client's reference image
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new):
    global s
    assert old in s, "missing: " + old[:80]
    s = s.replace(old, new, 1)

a = s.index("def gcard(")
b = s.index("def region_card(r):")
s = s[:a] + '''def short_fee(f):
    """'Approx 15,000 - 20,000 PKR (eVisa)' -> 'PKR 15,000+', '90 EUR (...)' -> 'EUR 90', '£135 ...' -> '£135'."""
    m = re.search(r"(\\d[\\d,]*)\\s*-\\s*\\d[\\d,]*\\s*(PKR|EUR|USD|GBP)", f)
    if m:
        return f"{m.group(2)} {m.group(1)}+"
    m = re.search(r"(\\d[\\d,]*)\\s*(PKR|EUR|USD|GBP)", f) or re.search(r"(PKR|EUR|USD|GBP)\\s*(\\d[\\d,]*)", f)
    if m:
        g = m.groups()
        return f"{g[1]} {g[0]}" if g[0][0].isdigit() else f"{g[0]} {g[1]}"
    m = re.search(r"([£$€])\\s?(\\d[\\d,]*)", f)
    return f"{m.group(1)}{m.group(2)}" if m else "On request"

def short_time(t):
    m = re.search(r"(\\d+)\\s*(?:to|-|–)\\s*(\\d+)\\s*(working days|weeks|days)", t or "")
    return f"{m.group(1)}–{m.group(2)} {m.group(3).replace('working days', 'days')}" if m else "Ask us"

def ncard(href, pid, alt, pill, notch, icon, title, sub, s1l, s1v, s2l, s2v, flagcode=None):
    """Dark collectible card: framed photo with pill on top and a notch tab at the bottom, icon tile, title, two stats."""
    if pid:
        media = picture(pid, alt, 600, 600, "(max-width:600px) 90vw, 280px", widths=(400, 600, 900))
    elif flagcode:
        media = f'<span class="n-flag">{flag(flagcode, alt, 110)}</span>'
    else:
        media = '<span class="n-orb"></span>'
    return (f'<a class="ncard" href="{href}"><span class="n-media">{media}<span class="n-pill">{e(pill)}</span><span class="n-notch">{e(notch)}</span></span>'
            f'<span class="n-head"><span class="n-ico">{icon}</span><span class="n-name"><b>{e(title)}</b><small>{e(sub)}</small></span></span>'
            f'<span class="n-stats"><span><small>{e(s1l)}</small><b>{e(s1v)}</b></span><span><small>{e(s2l)}</small><b>{e(s2v)}</b></span></span></a>')

LOGO_ICON = f'<img src="{LOGO}" alt="" width="40" height="40" loading="lazy">'

''' + s[b:]

rep('''    return gcard(f"/countries/{r['slug']}", r["img"], r["name"] + " visa from Pakistan", r["name"], r["shortDesc"], cnt, "AL ARBAB", "visa", r["flag"])''',
    '''    vv = r["visas"][0] if r["visas"] else None
    icon = flag(r["flag"], "", 40) if r["flag"] else LOGO_ICON
    sub = r["shortDesc"].split(".")[0]
    return ncard(f"/countries/{r['slug']}", r["img"], r["name"] + " visa from Pakistan", cnt, "Visa guide →", icon, r["name"], sub,
                 "Processing", short_time(vv["processingTime"]) if vv else "Ask us", "Visa types", str(len(r["visas"])), r["flag"])''')

rep('''        vd_cards += gcard(link, pid, v["country"].title() + " – " + v["landmark"], v["country"].title(), v["landmark"], v["tag"], v["flag"], "visa")''',
    '''        cc = COUNTRIES.get(link.rstrip("/").split("/")[-1])
        vv = visit_visa(cc["region"]) if cc else None
        vd_cards += ncard(link, pid, v["country"].title() + " – " + v["landmark"], v["tag"], short_fee(cc["fee"]) if cc else "Ask us",
                          flag(cc["code"], "", 40) if cc else LOGO_ICON, v["country"].title(), v["landmark"],
                          "Processing", short_time(vv["processingTime"]) if vv else "Ask us", "Approval", "98%")''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v8")
