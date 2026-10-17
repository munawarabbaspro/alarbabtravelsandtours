# one-off patch: remove every visa fee / package price from the site (they change too often)
import io, re
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# ---------- 1. sanitize data on load: strip fee amounts from document lists / FAQs
rep('''B = DATA["brand"]
''', '''B = DATA["brand"]

MONEY = r"(?:PKR|Rs\\.?|EUR|USD|GBP|AUD|CAD|€|£|\\$)\\s?\\d[\\d,.]*\\+?|\\d[\\d,.]*\\+?\\s?(?:PKR|EUR|USD|GBP|AUD|CAD)\\b"
FEE_WORD = re.compile(r"\\bfees?\\b|\\bcharges?\\b|\\bcost\\b|\\bprice\\b", re.I)

def no_fee(text):
    """Remove fee amounts from a requirement line; returns None if the whole line is about the fee."""
    if re.match(r"\\s*(visa\\s+)?fees?\\s*:", text, re.I):
        return None
    if not (FEE_WORD.search(text) and re.search(MONEY, text)):
        return text
    t = re.sub(r"\\s*\\([^)]*(?:" + MONEY + r")[^)]*\\)", "", text)
    t = re.sub(r"(?:approx\\.?\\s*)?(?:" + MONEY + r")(?:\\s*[-–/]\\s*(?:approx\\.?\\s*)?(?:" + MONEY + r"|\\d[\\d,.]*))?", "", t, flags=re.I)
    t = re.sub(r"\\s{2,}", " ", t).strip(" -–:,;/")
    return t if len(t) > 3 and not re.fullmatch(r"(visa\\s+)?fees?.*", t, re.I) else None

def clean_list(xs):
    return [y for y in (no_fee(x) for x in xs) if y]

def clean_faqs(fs):
    return [f for f in fs if not (FEE_WORD.search(f["q"]) and re.search(MONEY, f["a"])) and not re.search(r"\\bfees?\\b", f["q"], re.I)]

for _lst in DATA["countries"].values():
    for _c in _lst:
        _c["docs"] = clean_list(_c["docs"])
for _r in DATA["regions"]:
    _r["generalRequirements"] = clean_list(_r["generalRequirements"])
    _r["faqs"] = clean_faqs(_r["faqs"])
    if isinstance(_r["visas"], list):
        for _v in _r["visas"]:
            _v["requirements"] = clean_list(_v["requirements"])
for _v in DATA["visaTypeTemplate"]:
    _v["requirements"] = clean_list(_v["requirements"])
DATA["faqSchengenGeneral"] = clean_faqs(DATA["faqSchengenGeneral"])
DATA["faqAir"] = clean_faqs(DATA["faqAir"])
''')
rep('''        fee = [d for d in c["docs"] if d.lower().startswith("visa fee")]
        c["fee"] = fee[0].split(":", 1)[1].strip() if fee else "Varies — ask for a quote"
        c["docs_clean"] = [d for d in c["docs"] if not d.lower().startswith("visa fee")]''', '''        c["docs_clean"] = c["docs"]''')

# ---------- 2. home cards: notch shows processing time instead of fee
rep('''        vd_cards += ncard(link, pid, v["country"].title() + " – " + v["landmark"], v["tag"], short_fee(cc["fee"]) if cc else "Ask us",''',
    '''        vd_cards += ncard(link, pid, v["country"].title() + " – " + v["landmark"], v["tag"], "Visa guide →",''')
rep('''"Choose a region to see country-by-country requirements, fees and documents."''', '''"Choose a region to see country-by-country requirements, documents and processing times."''')
rep('''f"Visa requirements, fees and documents for {len(COUNTRIES)} countries''', '''f"Visa requirements, documents and processing times for {len(COUNTRIES)} countries''')

# ---------- 3. region visa pages
rep('''<div class="block"><h2>Fees &amp; processing time</h2><div class="facts" style="margin-top:0;grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Estimated fees</small><b>{e(v["fees"])}</b></div><div><small>Processing time</small><b>{e(v["processingTime"])}</b></div></div><p class="note" style="margin-top:12px">Embassy fees change with exchange rates and embassy policy. We confirm the current fee before you pay.</p></div>''',
    '''<div class="block"><h2>Processing time &amp; cost</h2><div class="facts" style="margin-top:0;grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Processing time</small><b>{e(v["processingTime"])}</b></div><div><small>Cost</small><b>Today's price on WhatsApp</b></div></div><p class="note" style="margin-top:12px">Embassy charges change often, so we don't publish them. Message us for the current all-in cost for your case.</p></div>''')
rep('''    rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{e(c["fee"])}</td><td>{e(", ".join(c["popularPlaces"][:2]) or "—")}</td></tr>' for c in cs)
    table = (f'<div class="block"><h2>{e(r["name"])} {e(lname)} fees by country</h2><p>Embassy fees for Pakistani passport holders across {len(cs)} {e(r["name"])} destinations. Open a country for its full document list.</p>'
             f'<div style="overflow-x:auto;margin-top:12px"><table class="tbl"><thead><tr><th>Country</th><th>Visa fee</th><th>Popular places</th></tr></thead><tbody>{rows}</tbody></table></div></div>') if cs else ""''',
    '''    rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{len(c["docs_clean"])} documents</td><td>{e(", ".join(c["popularPlaces"][:2]) or "—")}</td></tr>' for c in cs)
    table = (f'<div class="block"><h2>{e(r["name"])} {e(lname)}: countries we handle</h2><p>Document checklists for Pakistani passport holders across {len(cs)} {e(r["name"])} destinations. Open a country for its full list.</p>'
             f'<div style="overflow-x:auto;margin-top:12px"><table class="tbl"><thead><tr><th>Country</th><th>Checklist</th><th>Popular places</th></tr></thead><tbody>{rows}</tbody></table></div></div>') if cs else ""''')
rep('''{"serviceType": v["name"], "offers": {"@type": "Offer", "description": v["fees"]}}''', '''{"serviceType": v["name"]}''')

# ---------- 4. country pages
rep('''            (f"How much is the {c['name']} visa fee for Pakistani passport holders?", f"{c['fee']}. Our service charges are quoted separately, and we confirm the current embassy fee before you pay."),''',
    '''            (f"How much does a {c['name']} visa cost from Pakistan?", "Embassy charges change often, so we don't publish them. Message us on WhatsApp and we confirm the current all-in cost for your case before you pay anything."),''')
rep('''("fee", "Visa fee")''', '''("fee", "Cost & processing")''')
a = s.index('<div class="block" id="fee"><h2>{e(c["name"])} visa fee in Pakistan</h2>')
b = s.index('<div class="block" id="documents">', a)
s = s[:a] + '''<div class="block" id="fee"><h2>{e(c["name"])} visa cost &amp; processing time</h2><div class="feebox" style="grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Processing time</small><b>{e(proc)}</b></div><div><small>Cost</small><b>Today's price on WhatsApp</b></div></div>
<p style="margin-top:12px">Embassy charges change with exchange rates and policy, so we don't publish them. Send us your travel dates and we confirm the current all-in cost for your case. No payment until you agree.</p>
<p style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap;align-items:center"><a class="btn wa" href="{wa("Hi, what is the total cost for a " + c["name"] + " visa?")}" target="_blank" rel="noopener">💬 Ask today's price</a><a class="link" href="/guides/visa-requirements-for-pakistani-passport">Compare {len(COUNTRIES)} countries →</a></p></div>
''' + s[b:]
rep('''    facts = f'<div class="facts"><div><small>Visa fee</small><b>{e(c["fee"])}</b></div>''', '''    facts = f'<div class="facts"><div><small>Documents</small><b>{len(c["docs_clean"])} on the checklist</b></div>''')
rep('''{"serviceType": "Visa consultancy", "offers": {"@type": "Offer", "description": "Visa fee: " + c["fee"]}}''', '''{"serviceType": "Visa consultancy"}''')
rep('''    title = f"{c['name']} Visa Fee in Pakistan & Documents 2026 | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Fee in Pakistan & Documents | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Fee & Documents | AL ARBAB"''', '''    title = f"{c['name']} Visa from Pakistan: Requirements 2026 | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Requirements from Pakistan | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Requirements | AL ARBAB"''')

# ---------- 5. Umrah: no prices
rep(''' ("How much does an Umrah package from Pakistan cost in 2026?", "Packages start from PKR 185,000 for Economy (15 days), PKR 225,000 for 3 Star, PKR 285,000 for 4 Star and PKR 395,000 for 5 Star Luxury. Final price depends on hotels, dates and group size."),''',
    ''' ("How much does an Umrah package from Pakistan cost in 2026?", "Prices change with the season, airfare and hotel availability, so we quote on the day. Choose Economy, 3 Star, 4 Star or 5 Star and send your dates on WhatsApp for today's price."),''')
rep('''<h3>{e(u["title"])}</h3><div class="price"><small>From</small>{e(price)}</div><ul>{f}</ul>''', '''<h3>{e(u["title"])}</h3><ul>{f}</ul>''')
rep('''"Economy to 5-star Umrah packages 2026 from Islamabad — visa, flights, hotels and 24/7 ground support. From PKR 185,000."''', '''"Economy to 5-star Umrah packages 2026 from Islamabad — visa, flights, hotels and 24/7 ground support."''')
rep('''            "offers": {"@type": "Offer", "priceCurrency": "PKR", "price": re.sub(r"[^\\d]", "", u["price"]), "description": u["price"]}}} for i, u in enumerate(DATA["umrah"])]}]''',
    '''            }} for i, u in enumerate(DATA["umrah"])]}]''')
rep('''"Book Umrah packages 2026 from Islamabad: Economy from PKR 185,000 to 5-Star Luxury. Ministry-authorized agent, visa, flights, hotels & 24/7 support."''',
    '''"Book Umrah packages 2026 from Islamabad: Economy, 3 Star, 4 Star and 5-Star Luxury. Ministry-authorized agent, visa, flights, hotels & 24/7 support."''')
rep('''("🕋", "Umrah packages", "Economy to 5-star packages from PKR 185,000 with visa, flights and hotels.", "/umrah"),''', '''("🕋", "Umrah packages", "Economy to 5-star packages with visa, flights and hotels.", "/umrah"),''')
rep('''                (f"How much does the {u['title']} cost?", f"{u['price']} per person. The final price depends on dates, hotel availability and group size; we confirm it before you pay."),''',
    '''                (f"How much does the {u['title']} cost?", "Prices change with dates, airfare and hotel availability, so we quote on the day. Send your dates and family size on WhatsApp for today's price."),''')
rep('''<div class="feebox"><div><small>Price</small><b>{e(u["price"])}</b></div><div><small>Duration</small>''', '''<div class="feebox"><div><small>Price</small><b>Today's price on WhatsApp</b></div><div><small>Duration</small>''')
rep('''f"Hi, I want to book the {u['title']} Umrah package ({u['price']}).")''', '''f"Hi, I want to book the {u['title']} Umrah package. Please send today's price.")''')
rep('''{e(o["title"])} · {e(o["price"].replace("From ", ""))} <span>→</span>''', '''{e(o["title"])} <span>→</span>''')
rep('''pagehead(f"Umrah 2026 · {e(price)}", f"Umrah {e(u['title'])}", f"{e(u['price'])} — " + e(", ".join(u["features"][:3]))''', '''pagehead("Umrah 2026", f"Umrah {e(u['title'])}", e(", ".join(u["features"][:3]))''')
rep('''{"serviceType": "Umrah package", "offers": {"@type": "Offer", "priceCurrency": "PKR", "price": re.sub(r"[^\\d]", "", u["price"]), "description": u["price"]}}''', '''{"serviceType": "Umrah package"}''')
rep('''        page(url, f"Umrah {u['title']} 2026 {price} | AL ARBAB"[:65], f"Umrah {u['title']} from Islamabad: {u['price']}. " + ", ".join(u["features"]) + ". Book on WhatsApp.",
             body, ld, f"umrah {u['title'].lower()}, umrah package {price.lower()}, umrah package islamabad 2026",''',
    '''        page(url, f"Umrah {u['title']} 2026 from Islamabad | AL ARBAB", f"Umrah {u['title']} from Islamabad: " + ", ".join(u["features"]) + ". Get today's price on WhatsApp.",
             body, ld, f"umrah {u['title'].lower()}, umrah package islamabad 2026, umrah package from pakistan",''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v10 (part 1)")
