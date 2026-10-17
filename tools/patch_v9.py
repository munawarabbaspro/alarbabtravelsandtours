# one-off patch: SEO round (unique region-visa pages, guides, html + image sitemap, WebPage schema, async fonts, Google Maps, llms.txt)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# ---------- async Google Fonts (no render blocking)
rep('''<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800;900&family=Inter:wght@400;600;700&display=swap">''',
    '''<link rel="preload" as="style" href="{FONTS}" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="{FONTS}"></noscript>''')
rep('''PAGES = {}   # url -> (html, priority, noindex)''', '''PAGES = {}   # url -> (html, priority, noindex)
FONTS = "https://fonts.googleapis.com/css2?family=Archivo:wght@700;800;900&family=Inter:wght@400;600;700&display=swap"''')

# ---------- WebPage schema on every indexable page
rep('''    lds = ([org_ld(), website_ld()] if home else [org_ld()]) + (ld or [])''',
    '''    lds = ([org_ld(), website_ld()] if home else [org_ld()]) + (ld or [])
    if not noindex:
        kind = "CollectionPage" if url in ("/countries", "/packages", "/guides", "/sitemap") else ("Article" if url.startswith("/guides/") else "WebPage")
        wp = {"@context": "https://schema.org", "@type": "WebPage" if kind == "Article" else kind, "@id": canon + "#webpage", "url": canon, "name": title, "description": fit_desc(desc),
              "inLanguage": "en-PK", "isPartOf": {"@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": NAME}, "about": {"@id": BASE + "/#org"},
              "dateModified": TODAY, "primaryImageOfPage": {"@type": "ImageObject", "url": img}}
        lds.append(wp)''')

# ---------- Google Maps embed instead of OpenStreetMap (both iframes)
OSM = 'src="https://www.openstreetmap.org/export/embed.html?bbox=73.0600%2C33.7090%2C73.0750%2C33.7180&amp;layer=mapnik&amp;marker=33.7135%2C73.0673"'
GMAP = 'src="https://www.google.com/maps?q=Eagle%20Plaza%2C%20Fazal-e-Haq%20Road%2C%20Blue%20Area%2C%20Islamabad&amp;output=embed"'
assert s.count(OSM) == 2
s = s.replace(OSM, GMAP)

# ---------- unique content for region visa pages
rep('''<div class="block"><h2>Expert tips</h2><ul class="tips">{tips}</ul></div>
<div class="block"><h2>What we do for you</h2>''', '''{region_extra}
<div class="block"><h2>Expert tips</h2><ul class="tips">{tips}</ul></div>
<div class="block"><h2>What we do for you</h2>''')
rep('''    lname = v["name"].lower()
    main = f\'\'\'<div class="stack">
<div class="block"><h2>Expert processing for {e(r["name"])} {e(lname)}s</h2>''', '''    lname = v["name"].lower()
    cs = [c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]]
    rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{e(c["fee"])}</td><td>{e(", ".join(c["popularPlaces"][:2]) or "—")}</td></tr>' for c in cs)
    table = (f'<div class="block"><h2>{e(r["name"])} {e(lname)} fees by country</h2><p>Embassy fees for Pakistani passport holders across {len(cs)} {e(r["name"])} destinations. Open a country for its full document list.</p>'
             f'<div style="overflow-x:auto;margin-top:12px"><table class="tbl"><thead><tr><th>Country</th><th>Visa fee</th><th>Popular places</th></tr></thead><tbody>{rows}</tbody></table></div></div>') if cs else ""
    gen = "".join(f"<li>{e(x)}</li>" for x in r["generalRequirements"])
    rfaq = [(f["q"], f["a"]) for f in r["faqs"]]
    region_extra = (f'<div class="block"><h2>About {e(r["name"])} visas from Pakistan</h2><p>{e(r["intro"])}</p><h3>General requirements in {e(r["name"])}</h3><ul class="checks">{gen}</ul></div>'
                    + table
                    + f'<div class="block"><h2>{e(r["name"])} application process</h2><ol class="steps">{steps_html([(st["title"], st["desc"]) for st in r["stepByStep"]])}</ol></div>'
                    + (f'<div class="block"><h2>{e(r["name"])} {e(lname)} FAQs</h2>{faq_html(rfaq)}</div>' if rfaq else ""))
    main = f\'\'\'<div class="stack">
<div class="block"><h2>Expert processing for {e(r["name"])} {e(lname)}s</h2>''')
rep('''          service_ld(f"{r['name']} {v['name']}", v["seoDescription"], url, {"serviceType": v["name"], "offers": {"@type": "Offer", "description": v["fees"]}})]
    t = v["seoTitle"]''', '''          service_ld(f"{r['name']} {v['name']}", v["seoDescription"], url, {"serviceType": v["name"], "offers": {"@type": "Offer", "description": v["fees"]}})]
    if rfaq:
        ld.append(faq_ld(rfaq))
    t = v["seoTitle"]''')

# ---------- links from country pages to the guides
rep('''<p style="margin-top:12px"><a class="btn wa" href="{wa("Hi, what is the total price for a " + c["name"] + " visa?")}" target="_blank" rel="noopener">💬 Ask today's price</a></p></div>''',
    '''<p style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap;align-items:center"><a class="btn wa" href="{wa("Hi, what is the total price for a " + c["name"] + " visa?")}" target="_blank" rel="noopener">💬 Ask today's price</a><a class="link" href="/guides/visa-fees-for-pakistani-passport">Compare visa fees for {len(COUNTRIES)} countries →</a></p></div>''')
rep('''<a class="link" href="/eligibility-check?d={c["slug"]}">Get your personal checklist →</a></p></div>''',
    '''<a class="link" href="/eligibility-check?d={c["slug"]}">Get your personal checklist →</a> · <a class="link" href="/guides/visa-documents-explained">What each document means →</a></p></div>''')

# ---------- footer: guides + sitemap
rep('''("/privacy", "Privacy Policy"), ("/terms", "Terms & Conditions")]''', '''("/guides", "Visa Guides"), ("/sitemap", "Sitemap"), ("/privacy", "Privacy Policy"), ("/terms", "Terms & Conditions")]''')

# ---------- hotel page: more substance
rep('''<p>Beyond visa compliance, we offer exceptional deals for holidaymakers and corporate travelers.''', '''<h3>What embassies check in a hotel booking</h3><ul class="checks"><li>Your name exactly as in the passport</li><li>Every night of the stay covered, city by city</li><li>Dates that match the flight reservation and cover letter</li><li>Hotel address and contact details the embassy can verify</li></ul>
<p>Need flights too? See our <a class="link" href="/flight-hotel-reservation-for-visa">flight &amp; hotel reservation for visa</a> service.</p>
<p>Beyond visa compliance, we offer exceptional deals for holidaymakers and corporate travelers.''')

# ---------- guides, html sitemap, image sitemap, llms.txt
NEW = r'''
# ================================================================== guides & sitemap (SEO round)
DOC_GUIDE = [
 ("passport", "Passport", ["passport"], "Valid for at least 6 months beyond your return date, with 2 or more blank pages. Embassies often ask for copies of old passports and previous visas too.", "Directorate General of Immigration & Passports"),
 ("cnic", "CNIC", ["cnic"], "A clear A4 copy of your computerised national identity card, front and back.", "NADRA"),
 ("frc", "Family Registration Certificate (FRC) / MRC", ["frc", "family registration", "mrc", "marriage certificate"], "Shows your family members and relationships. Asked for family trips, sponsored applicants and children. MRC is the marriage registration certificate.", "NADRA"),
 ("bank", "Bank statement & account maintenance certificate", ["bank statement", "maintenance certificate"], "Usually the last 6 months, signed and stamped by the bank. Embassies look for a steady balance and a clear source of funds, not sudden large deposits.", "Your bank"),
 ("tax", "NTN & income tax returns", ["ntn", "tax return", "fbr"], "Your National Tax Number certificate and filed returns for the last 2–3 years show taxable income in Pakistan.", "FBR (Federal Board of Revenue)"),
 ("job", "Employment letter & salary slips", ["employment", "salary slip", "job letter", "occupation"], "A letter on company letterhead with your designation, salary, joining date and approved leave, plus recent salary slips.", "Your employer"),
 ("business", "Business documents", ["business", "chamber of commerce", "secp"], "For owners: Chamber of Commerce membership, SECP or business registration, letterhead and business bank statement.", "Chamber of Commerce / SECP"),
 ("polio", "Polio vaccination certificate", ["polio"], "Many destinations ask Pakistani travellers for a valid polio vaccination certificate (the yellow card). Get it before you travel.", "Authorised vaccination centres"),
 ("insurance", "Travel medical insurance", ["insurance"], "Schengen states require at least €30,000 medical cover valid for the whole stay. Other countries may ask for it too.", "Licensed insurers (Jubilee, Adamjee, United, EFU…)"),
 ("bookings", "Flight reservation & hotel booking", ["flight", "hotel", "accommodation", "lodging", "itinerary"], "A return flight reservation and hotel bookings for every night, matching your dates. Many embassies prefer reservations over paid tickets.", "Your travel agent"),
 ("cover", "Cover letter", ["cover letter"], "Explains the purpose of the trip, the day-by-day plan, who pays, and your ties to Pakistan.", "You (we help draft it)"),
 ("photos", "Photographs", ["photo"], "Recent passport-size photos on a white background, usually 35×45 mm; some embassies need 50×50 mm.", "Any professional photo studio"),
 ("invite", "Invitation letter", ["invitation"], "For family or business visits: a letter from your host or the inviting company with their ID or registration details.", "Your host abroad"),
]

def doc_count(keys):
    return sum(1 for c in COUNTRIES.values() if any(any(k in d.lower() for k in keys) for d in c["docs"]))

def build_guides():
    guides = []
    # 1. visa fees table
    url = "/guides/visa-fees-for-pakistani-passport"
    blocks = ""
    for r in DATA["regions"]:
        cs = [c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]]
        if not cs:
            continue
        vv = visit_visa(r["slug"])
        rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{e(c["fee"])}</td><td>{e(short_time(vv["processingTime"]) if vv else "—")}</td></tr>' for c in cs)
        blocks += f'<div class="block" id="{r["slug"]}"><h2>{e(r["name"])} visa fees</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Country</th><th>Visa fee</th><th>Typical processing</th></tr></thead><tbody>{rows}</tbody></table></div></div>'
    special = "".join(f'<tr><td><a class="link" href="/countries/{rs}">{e(REGIONS[rs]["name"])}</a></td><td>{e(REGIONS[rs]["visas"][0]["fees"])}</td><td>{e(short_time(REGIONS[rs]["visas"][0]["processingTime"]))}</td></tr>' for rs in ("united-kingdom", "united-states", "canada", "australia"))
    faqs = [("Are these visa fees fixed?", "No. Embassy fees change with exchange rates and policy, and many are charged in EUR, USD or GBP and paid in PKR at the current rate. We confirm the current fee before you pay."),
            ("Do these fees include your service charges?", "No. The table shows embassy or visa fees. Our consultancy charges are quoted separately on WhatsApp before you start."),
            ("Which visas are cheapest for Pakistanis?", "Fees vary by country and change often. Use the table to compare, then ask us on WhatsApp for today's all-in price for the countries you are considering.")]
    toc = "".join(f'<a href="#{r["slug"]}">{e(r["name"])} <span>↓</span></a>' for r in DATA["regions"] if [c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]])
    main = f\'\'\'<div class="stack"><div class="block"><h2>How to use this list</h2><p>This page lists the visa fee for Pakistani passport holders for {len(COUNTRIES)} destinations we handle from Islamabad, grouped by region, with typical processing times. Fees are taken from each country's current checklist on our site; click a country for its full document list.</p><p class="note" style="margin-top:12px">Updated {UPDATED}. Fees change with exchange rates and embassy policy — confirm on WhatsApp before you pay.</p></div>
<div class="block"><h2>UK, USA, Canada &amp; Australia</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Destination</th><th>Visit visa fee</th><th>Typical processing</th></tr></thead><tbody>{special}</tbody></table></div></div>
{blocks}<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>\'\'\'
    guides.append((url, "Visa fees for Pakistani passport holders 2026", f"Visa fees for {len(COUNTRIES)} countries in one table, grouped by region, with typical processing times.",
                   f"Visa Fees for Pakistani Passport 2026 ({len(COUNTRIES)} Countries) | AL ARBAB",
                   f"Visa fees for Pakistani passport holders in 2026: one table for {len(COUNTRIES)} countries including Schengen, UK, USA, Dubai, Thailand and Malaysia, with processing times.",
                   main, toc, faqs, UNS["fr"], "visa fee pakistan, visa fees for pakistani passport, schengen visa fee pakistan, uk visa fee pakistan, dubai visa fee pakistan"))
    # 2. schengen requirements
    url = "/guides/schengen-visa-requirements-from-pakistan"
    sc = REGIONS["schengen"]
    route = {c: v for c, v, _ in APPOINTMENT_CENTRES}
    rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{e(short_fee(c["fee"]))}</td><td>{e(route.get(c["name"], "VFS / BLS / Gerry\'s (by embassy)"))}</td><td>{e(c["popularPlaces"][0] if c["popularPlaces"] else "—")}</td></tr>' for c in BY_REGION["schengen"])
    gen = "".join(f"<li>{e(x)}</li>" for x in sc["generalRequirements"])
    sfaq = [(f["q"], f["a"]) for f in sc["faqs"]] + [q for q in FAQ_GENERAL if "Schengen" in q[0] or "bank" in q[0].lower()][:2]
    main = f\'\'\'<div class="stack"><div class="block"><h2>Schengen visa from Pakistan in short</h2><p>{e(sc["intro"])}</p><p style="margin-top:10px">One Schengen visa lets you visit all 29 member states. Apply at the embassy of the country where you will spend the most nights, or the country you enter first if your stays are equal.</p></div>
<div class="block" id="requirements"><h2>Documents every Schengen embassy asks for</h2><ul class="checks">{gen}</ul><p style="margin-top:12px"><a class="link" href="/guides/visa-documents-explained">What each document means →</a></p></div>
<div class="block" id="countries"><h2>All 29 Schengen countries compared</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Country</th><th>Fee</th><th>Where you apply</th><th>Top attraction</th></tr></thead><tbody>{rows}</tbody></table></div></div>
<div class="block" id="process"><h2>Step-by-step process</h2><ol class="steps">{steps_html([(x["title"], x["desc"]) for x in sc["stepByStep"]])}</ol></div>
<div class="block" id="refusal"><h2>Why Schengen visas get refused</h2><ul class="refuse">{"".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in REFUSAL)}</ul></div>
<div class="block" id="faqs"><h2>FAQs</h2>{faq_html(sfaq)}</div></div>\'\'\'
    toc = "".join(f'<a href="#{i}">{n} <span>↓</span></a>' for i, n in [("requirements", "Documents"), ("countries", "29 countries"), ("process", "Process"), ("refusal", "Refusal reasons"), ("faqs", "FAQs")])
    guides.append((url, "Schengen visa requirements from Pakistan (2026)", "Documents, fees and the application route for all 29 Schengen countries, in one place.",
                   "Schengen Visa Requirements from Pakistan 2026 | AL ARBAB",
                   "Schengen visa requirements for Pakistanis in 2026: document checklist, €90 fee, where to apply (VFS, BLS, Gerry's) and a comparison of all 29 countries.",
                   main, toc, sfaq, UNS["it"], "schengen visa requirements pakistan, schengen visa documents pakistan, schengen visa from islamabad, easiest schengen visa pakistan"))
    # 3. documents explained
    url = "/guides/visa-documents-explained"
    items = ""
    for i, name, keys, what, issuer in DOC_GUIDE:
        n = doc_count(keys)
        items += f'<div class="block" id="{i}"><h2>{e(name)}</h2><p>{e(what)}</p><div class="feebox" style="margin-top:12px;grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Where to get it</small><b>{e(issuer)}</b></div><div><small>Asked by</small><b>{n} of {len(COUNTRIES)} country checklists</b></div></div></div>'
    dfaq = [("Which document causes the most refusals?", "Weak or unexplained bank statements are the most common problem, followed by missing proof of ties to Pakistan."),
            ("Do I need translations?", "Documents in Urdu usually need an English translation; some embassies also want attestation. We tell you exactly which ones for your case.")]
    main = f\'\'\'<div class="stack"><div class="block"><h2>Visa documents in plain words</h2><p>Every embassy checklist uses the same handful of documents. Here is what each one is, where Pakistani applicants get it, and how many of the {len(COUNTRIES)} country checklists on our site ask for it.</p></div>{items}<div class="block"><h2>FAQs</h2>{faq_html(dfaq)}</div></div>\'\'\'
    toc = "".join(f'<a href="#{i}">{e(n.split(" (")[0])} <span>↓</span></a>' for i, n, *_ in DOC_GUIDE)
    guides.append((url, "Visa documents explained for Pakistani applicants", "FRC, maintenance certificate, polio card, NTN, insurance and more: what each document is and where to get it.",
                   "Visa Documents Explained: FRC, Bank Statement, Polio | AL ARBAB",
                   "What FRC, bank maintenance certificate, NTN, polio certificate, travel insurance and cover letters mean for your visa from Pakistan, and where to get each one.",
                   main, toc, dfaq, UNS["cta"], "visa documents pakistan, frc for visa, bank maintenance certificate visa, polio certificate travel pakistan, ntn for visa"))
    for url, h1, lead, title, desc, main, toc, faqs, pid, kw in guides:
        aside = f'<aside class="aside"><nav class="mini toc" aria-label="On this page"><h3>On this page</h3>{toc}</nav>{ctacard("visa")}<nav class="mini"><h3>More guides</h3>' + "".join(f'<a href="{g[0]}">{e(g[1])} <span>→</span></a>' for g in guides if g[0] != url) + "</nav></aside>"
        ph = pagehead(f"Guide · Updated {UPDATED}", e(h1), e(lead), pid, alt=h1, actions=f'<a class="btn wa" href="{wa("Hi, I have a question about " + h1 + ".")}" target="_blank" rel="noopener">💬 Ask an adviser</a>')
        body = shell("/guides", [("Home", "/"), ("Guides", "/guides"), (h1, None)], ph, f'<div class="layout">{main}{aside}</div>{cta_band()}')
        art = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "image": U(pid, 1200), "datePublished": TODAY, "dateModified": TODAY,
               "author": {"@type": "Organization", "name": NAME, "url": BASE + "/"}, "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + url, "inLanguage": "en-PK"}
        page(url, title, desc, body, [crumbs_ld([("Home", "/"), ("Guides", "/guides"), (h1, url)]), art, faq_ld(faqs)], kw, image=U(pid, 1200), priority="0.8")
    cards = "".join(f'<a class="vt" href="{g[0]}"><h3>{e(g[1])}</h3><p>{e(g[2])}</p><span class="go">Read the guide →</span></a>' for g in guides)
    ph = pagehead("Visa guides", "Visa guides for<br>Pakistani travellers", "Plain-language guides built from the checklists we use every day in our Blue Area office: fees, documents and the Schengen process.", UNS["cta"], alt="Visa guides")
    body = shell("/guides", [("Home", "/"), ("Guides", None)], ph, f'<section class="sec"><div class="grid">{cards}</div></section>{cta_band()}')
    page("/guides", "Visa Guides for Pakistani Travellers 2026 | AL ARBAB",
         "Visa guides for Pakistani travellers: visa fees for 86 countries, Schengen requirements from Pakistan, and visa documents explained, from AL ARBAB in Islamabad.",
         body, [crumbs_ld([("Home", "/"), ("Guides", "/guides")])], priority="0.8")

SECTIONS = [("Main pages", lambda u: u.count("/") == 1 and not u.startswith("/guides")), ("Visa services", lambda u: u.startswith("/visa-services/")),
            ("Guides", lambda u: u.startswith("/guides")), ("Regions & visa types", lambda u: u.startswith("/countries/") and (u.count("/") == 2 or "/visa/" in u)),
            ("Countries", lambda u: u.startswith("/countries/") and u.count("/") == 3 and "/visa/" not in u), ("Flights", lambda u: u.startswith("/air-ticketing/")),
            ("Umrah & packages", lambda u: u.startswith("/umrah/") or u.startswith("/packages/"))]

def page_title(html):
    m = re.search(r"<title>([^<]*)</title>", html)
    return H.unescape(m.group(1)).replace(" | AL ARBAB TRAVEL AND TOURS", "").replace(" | AL ARBAB", "") if m else ""

def build_html_sitemap():
    groups = ""
    for name, test in SECTIONS:
        items = sorted((page_title(h), u) for u, (h, _, noi) in PAGES.items() if not noi and u != "/" and test(u))
        if items:
            groups += f'<div class="block"><h2>{e(name)} ({len(items)})</h2><ul class="smap">' + "".join(f'<li><a href="{u}">{e(t)}</a></li>' for t, u in items) + "</ul></div>"
    ph = pagehead("Sitemap", "All pages", f"Every page on the {NAME} website, grouped by section.")
    body = shell("/sitemap", [("Home", "/"), ("Sitemap", None)], ph, f'<div class="stack" style="margin-top:20px">{groups}</div>')
    page("/sitemap", "Sitemap | AL ARBAB TRAVEL AND TOURS", f"All pages on the {NAME} website: visa services, {len(COUNTRIES)} country visa guides, regions, flights, Umrah packages and travel guides.",
         body, [crumbs_ld([("Home", "/"), ("Sitemap", "/sitemap")])], priority="0.3")

# ================================================================== write'''
rep("\n# ================================================================== write", NEW)

# image sitemap + llms.txt
rep('''    urls = "".join(f'<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority></url>\\n'
                   for u, (_, p, noi) in sorted(PAGES.items(), key=lambda x: (-float(x[1][1]), x[0])) if not noi)
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(f'<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n{urls}</urlset>\\n')''',
    '''    def imgs(html):
        out = []
        for m in re.finditer(r'<img[^>]+src="(https://images\\.unsplash\\.com/photo-[^"?]+)[^"]*"[^>]*alt="([^"]+)"', html):
            if m.group(1) not in [o[0] for o in out]:
                out.append((m.group(1) + "?auto=format&amp;fit=crop&amp;q=70&amp;w=1200", m.group(2)))
        return out[:8]
    urls = ""
    for u, (h, p, noi) in sorted(PAGES.items(), key=lambda x: (-float(x[1][1]), x[0])):
        if noi:
            continue
        im = "".join(f"<image:image><image:loc>{src}</image:loc></image:image>" for src, _ in imgs(h))
        urls += f"<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority>{im}</url>\\n"
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\\n' + urls + "</urlset>\\n")
    llms = [f"# {NAME}", "", f"> IATA-authorized travel agency and visa consultancy in Blue Area, Islamabad, Pakistan (since 2009). Visas for {len(COUNTRIES)} countries, air tickets, Umrah packages, hotels and travel insurance.", "",
            f"- Address: {ADDR}", f"- Phone / WhatsApp: {PHONE}, landline {LAND}", f"- Email: {EMAIL}", f"- Hours: {HOURS}", "", "## Key pages"]
    for u in ["/visa-services", "/countries", "/guides/visa-fees-for-pakistani-passport", "/guides/schengen-visa-requirements-from-pakistan", "/guides/visa-documents-explained",
              "/umrah", "/air-ticketing", "/eligibility-check", "/contact"]:
        if u in PAGES:
            llms.append(f"- [{page_title(PAGES[u][0])}]({BASE}{u})")
    llms += ["", "## Countries"] + [f"- [{c['name']} visa]({BASE}{c['url']}): fee {c['fee']}" for c in COUNTRIES.values()]
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write("\\n".join(llms) + "\\n")''')

rep('''    build_eligibility(); build_cities(); build_appointments(); build_reservation(); build_routes(); build_umrah_packages()''',
    '''    build_eligibility(); build_cities(); build_appointments(); build_reservation(); build_routes(); build_umrah_packages(); build_guides()''')
rep('''    for c in COUNTRIES.values():
        build_country(c)
    write_all()''', '''    for c in COUNTRIES.values():
        build_country(c)
    build_html_sitemap()
    write_all()''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v9")
