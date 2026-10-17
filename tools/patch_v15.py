# one-off patch: fix keyword cannibalisation, align H1 with title, CTR descriptions, editorial policy page, richer entity schema
import io, re
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# ---- one page per head term
rep('''    page("/", "Visa Consultant & Travel Agency Islamabad | AL ARBAB",''', '''    page("/", "AL ARBAB Travel & Tours | Travel Agency in Islamabad",''')
rep('''    page("/visa-services", "Best Visa Consultant in Islamabad 2026 | AL ARBAB",''', '''    page("/visa-services", "Visa Services: Tourist, Family, Business & Student | AL ARBAB",''')
rep('''    page(url, f"{name} Consultant in Islamabad | AL ARBAB", f"{desc} Expert''', '''    page(url, (f"{name} from Pakistan: Documents & Process | AL ARBAB" if slug != "schengen-visa" else "Schengen Visa Service: Documents & Appointments | AL ARBAB"), f"{desc} Expert''')

# region visa pages: "from Pakistan" intent instead of another "consultant" page
rep('''    t = v["seoTitle"].replace(" | AL ARBAB TRAVEL AND TOURS", " | AL ARBAB")''', '''    t = f"{r['name']} {v['name']} from Pakistan: Documents | AL ARBAB"
    if len(t) > 65:
        t = f"{r['name']} {v['name']} from Pakistan | AL ARBAB"''')

# region pages: H1 = consultant intent, matching the title
rep('''    ph = pagehead("Destination guide", f'{e(r["name"])} visa services',''', '''    ph = pagehead("Destination guide", f'{e(r["name"])} visa consultant in Islamabad',''')

# country pages: H1 = "X visa from Pakistan" (matches title + the searches people type)
rep('''    ph = pagehead(f'{e(r["name"])} · Updated {UPDATED}', e(c["title"]), e(c["description"]),''',
    '''    ph = pagehead(f'{e(r["name"])} · Updated {UPDATED}', f'{e(c["name"])} visa from Pakistan', e(c["description"]) + f' Prepared by our visa consultants in Blue Area, Islamabad.',''')

# country pages: CTR-focused meta description
rep('''    desc = c["description"]
    if len(desc) < 120:
        desc = f"{desc} Free assessment in Blue Area, Islamabad."''', '''    desc = (f"{c['name']} visa from Pakistan 2026: {len(c['docs_clean'])}-document checklist, how to apply, what the embassy checks and refusal reasons. "
            f"Free file check in Blue Area, Islamabad.")''')

# Australia: country page points to the dedicated Australia guide
rep('''    sibnav = f'<nav class="mini" aria-label="Nearby countries"><h3>More in {e(r["name"])}</h3>{sib}</nav>' if sib else ""''',
    '''    sibnav = f'<nav class="mini" aria-label="Nearby countries"><h3>More in {e(r["name"])}</h3>{sib}</nav>' if sib else ""
    if c["slug"] in REGIONS and c["slug"] != c["region"]:
        sibnav = f'<nav class="mini"><h3>Full guide</h3><a href="/countries/{c["slug"]}">{e(c["name"])} visa types &amp; process <span>→</span></a></nav>' + sibnav''')

# ---- entity schema: what the business knows about + region ItemLists
rep('''            "hasCredential": {''', '''            "knowsAbout": ["Schengen visa", "UK Standard Visitor visa", "USA B1/B2 visa", "Canada visitor visa", "Australia visitor visa", "Dubai visit visa",
                           "Umrah packages", "Air ticketing", "Travel insurance", "Visa appointments (VFS Global, BLS, Gerry's)"],
            "hasCredential": {''')
rep('''    if faqs:
        ld.append(faq_ld(faqs))
    title = r["seoTitle"]''', '''    if faqs:
        ld.append(faq_ld(faqs))
    if cs:
        ld.append({"@context": "https://schema.org", "@type": "ItemList", "name": f"{r['name']} visa destinations",
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + c["url"], "name": f"{c['name']} visa"} for i, c in enumerate(cs)]})
    title = r["seoTitle"]''')

# ---- editorial policy (E-E-A-T): how the information is kept accurate
rep('''def build_html_sitemap():''', '''def build_editorial():
    main = f\'\'\'<div class="stack">
<div class="block"><h2>Where our visa information comes from</h2><p>Every country page is built from the document checklists our consultants use for real applications in our Blue Area office. Where a government publishes its rules online, we link that official source on the page so you can check it yourself.</p></div>
<div class="block"><h2>How we keep it current</h2><ul class="checks"><li>Pages show the month they were last updated.</li><li>When an embassy or visa centre changes a requirement, we update the checklist and the date.</li><li>We don't publish embassy fees or package prices, because they change too often to stay accurate online. We confirm the current cost on WhatsApp before you pay.</li><li>Processing times are shown as typical ranges, never promises.</li></ul></div>
<div class="block"><h2>What we never do</h2><ul class="refuse"><li><b>Guarantee a visa</b><span>The decision always belongs to the embassy, high commission or consulate.</span></li><li><b>Invent reviews or success numbers</b><span>Reviews on this site come from real clients.</span></li><li><b>Ask for false documents</b><span>We only work with genuine, verifiable documents.</span></li></ul></div>
<div class="block"><h2>Found something out of date?</h2><p>Tell us on WhatsApp at <a class="link" href="{WA}" target="_blank" rel="noopener">{PHONE}</a> or email <a class="link" href="mailto:{EMAIL}">{EMAIL}</a> and we will check and correct it.</p></div>
</div>\'\'\'
    ph = pagehead("Trust", "How we keep our<br>visa information accurate", f"Sources, update process and the promises we don't make at {NAME}.")
    body = shell("/editorial-policy", [("Home", "/"), ("Editorial Policy", None)], ph, f'<div style="margin-top:20px">{main}</div>')
    page("/editorial-policy", "Editorial Policy: How We Keep Visa Info Accurate | AL ARBAB",
         f"Where AL ARBAB's visa checklists come from, how often they are updated, why we don't publish fees, and what we never promise.",
         body, [crumbs_ld([("Home", "/"), ("Editorial Policy", "/editorial-policy")])], priority="0.4")

def build_html_sitemap():''')
rep('''    build_html_sitemap()
    write_all()''', '''    build_editorial()
    build_html_sitemap()
    write_all()''')
rep('''("/guides", "Visa Guides"), ("/sitemap", "Sitemap"),''', '''("/guides", "Visa Guides"), ("/editorial-policy", "Editorial Policy"), ("/sitemap", "Sitemap"),''')
rep('''<h2>Official sources</h2><p>Always confirm the latest rules on the official portal. We check every file against these requirements before submission.</p>''',
    '''<h2>Official sources</h2><p>Always confirm the latest rules on the official portal. We check every file against these requirements before submission. <a class="link" href="/editorial-policy">How we keep this page accurate →</a></p>''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v15")
