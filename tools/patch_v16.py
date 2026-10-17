# one-off patch: drop the work-permit service; add international tour + honeymoon pages (no invented itineraries or prices)
import io, re
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# ---------- remove work permit everywhere
rep(''' ("work-permit", "Work Permit", "🛠", "Employment visa & work authorization for Gulf, Europe & beyond.", None),\n''', "")
rep(''' "work-permit": ["united-arab-emirates", "saudi-arabia", "qatar", "oman", "kuwait", "bahrain"],\n''', "")
rep(''', "work-permit": ["middle-east", "schengen"]''', "")
rep('''business, student visas and work permits for 50+ countries''', '''business and student visas for 50+ countries''')
rep('''"From tourist visas to work permits — one desk in Blue Area, Islamabad."''', '''"From tourist visas to student visas — one desk in Blue Area, Islamabad."''')
rep('''DATA["faqSchengenGeneral"] = clean_faqs(DATA["faqSchengenGeneral"])''', '''DATA["faqSchengenGeneral"] = clean_faqs(DATA["faqSchengenGeneral"])
# no work-permit / overseas-employment offers (needs a BEOE OEP licence)
DATA["services"] = [x for x in DATA["services"] if not re.search(r"work permit|employment visa", x["title"] + " " + x["desc"], re.I)]
for _r in DATA["regions"]:
    _r["shortDesc"] = re.sub(r",?\\s*(and\\s+)?work permits?", "", _r["shortDesc"], flags=re.I)''')

# ---------- tours & honeymoon
NEW = r'''
# ================================================================== international tours & honeymoon (confirmed service)
TOURS = [  # (url slug, country slug, display name, honeymoon-friendly, linked package id or None)
 ("maldives-tour-package-from-pakistan", "maldives", "Maldives", True, None),
 ("turkey-tour-package-from-pakistan", "turkey", "Turkey", True, None),
 ("baku-tour-package-from-islamabad", "azerbaijan", "Baku, Azerbaijan", True, None),
 ("thailand-tour-package-from-islamabad", "thailand", "Thailand", True, "thailand-phuket"),
 ("bali-tour-package-from-pakistan", "indonesia", "Bali, Indonesia", True, "indonesia-bali"),
 ("dubai-tour-package-from-pakistan", "united-arab-emirates", "Dubai", True, "dubai-desert-safari"),
 ("malaysia-tour-package-from-pakistan", "malaysia", "Malaysia", True, "malaysia-kl"),
 ("singapore-tour-package-from-pakistan", "singapore", "Singapore", False, "singapore-city"),
 ("nepal-tour-package-from-pakistan", "nepal", "Nepal", False, "nepal-himalayas"),
 ("europe-tour-package-from-pakistan", "italy", "Europe (Italy & Schengen)", True, "italy-schengen"),
]
ARRANGE = ["Return flights from Islamabad (or Lahore / Karachi on request)", "Visa file preparation and appointment where needed", "Hotels or resorts in the category you choose",
           "Airport transfers and sightseeing on request", "Travel insurance", "24/7 WhatsApp support during the trip"]

def tour_url(slug):
    return "/tours/" + slug

def build_tours():
    pk = {p["id"]: p for p in PACKAGES}
    cards = []
    for slug, cs, name, honey, pid in TOURS:
        c = COUNTRIES[cs]
        p = pk.get(pid)
        url = tour_url(slug)
        gal = "".join(f'<figure>{picture(g[1], f"{g[0]}, {c["name"]}", 800, 600, "(max-width:600px) 100vw, 300px")}<figcaption>📍 {e(g[0])}</figcaption></figure>' for g in c["gallery"])
        route = visa_route(c)
        if p:
            pkg_block = (f'<div class="block" id="package"><h2>Ready-made package: {e(p["title"])}</h2><div class="feebox" style="grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Duration</small><b>{e(p["duration"])}</b></div><div><small>Stay</small><b>{e(p["amenities"])}</b></div></div>'
                         f'<ul class="checks" style="margin-top:12px">' + "".join(f"<li>{e(h)}</li>" for h in p["highlights"]) + f'</ul><p style="margin-top:12px"><a class="link" href="{p["url"]}">Full package details →</a> Prefer different dates or hotels? We tailor it.</p></div>')
        else:
            pkg_block = (f'<div class="block" id="package"><h2>Your {e(name)} trip, planned around you</h2><p>We build each {e(name)} trip to your dates, budget and hotel category rather than selling one fixed itinerary. '
                         f'Tell us how many nights, who is travelling and the kind of stay you want, and we send a full plan with flights, hotels and visa on WhatsApp.</p></div>')
        honey_block = (f'<div class="block" id="honeymoon"><h2>{e(name)} honeymoon from Pakistan</h2><p>Planning a honeymoon? Tell us your wedding date and we plan the trip around it, with couple-friendly hotels, private transfers on request and the visa handled for both of you. '
                       f'Newly married couples usually need a <a class="link" href="/guides/visa-documents-explained#frc">marriage registration certificate (MRC)</a> for the visa file.</p></div>') if honey else ""
        faqs = [(f"Do Pakistanis need a visa for {c['name']}?", (f"Pakistani passport holders can get a visa on arrival in {c['name']} if they meet the entry conditions." if route.startswith("Visa on arrival") else f"Yes. You apply through {ROUTE_PHRASE.get(route, route.lower())}. We prepare the file as part of your tour.") + f" See the full {c['name']} checklist on our visa page."),
                (f"How much does a {name} tour package from Pakistan cost?", "Prices change with dates, airfare and hotel availability, so we quote on the day. Send your dates and number of travellers on WhatsApp for today's price."),
                (f"Can you plan a {name} trip from Lahore or Karachi?", "Yes. Flights can start from Islamabad, Lahore or Karachi; the visa file is prepared through our Islamabad office and documents can be shared on WhatsApp.")]
        main = f\'\'\'<div class="stack">
<div class="block answer" id="answer"><h2>{e(name)} tour from Pakistan: quick answer</h2><p>{e(f"AL ARBAB TRAVEL AND TOURS arranges {name} trips from Islamabad with flights, hotels and the visa in one booking. ")}{e("Pakistani travellers can get a visa on arrival if they meet the entry conditions. " if route.startswith("Visa on arrival") else f"The visa is {ROUTE_PHRASE.get(route, route.lower())}; we prepare the file for you. ")}Get today's price and a plan for your dates on <a class="link" href="{wa("Hi, I want a " + name + " tour package.")}" target="_blank" rel="noopener">WhatsApp</a>.</p></div>
{pkg_block}
{honey_block}
<div class="block" id="places"><h2>Places you can visit in {e(name)}</h2><div class="gallery">{gal}</div></div>
<div class="block" id="included"><h2>What we arrange</h2><ul class="checks">{"".join(f"<li>{e(x)}</li>" for x in ARRANGE)}</ul></div>
<div class="block" id="visa"><h2>{e(c["name"])} visa for this trip</h2><p>{e(c["name"])} checklist: {len(c["docs_clean"])} documents. How you apply: {e(route.lower())}. <a class="link" href="{c["url"]}">See the full {e(c["name"])} visa requirements →</a></p></div>
<div class="block" id="how"><h2>How booking works</h2><ol class="steps">{steps_html([("Share your plan", "Dates, number of travellers and budget on WhatsApp."), ("Get a quote", "Flights, hotels and visa costed for your dates."), ("Visa & bookings", "We prepare the visa file and confirm flights and hotels."), ("Travel", "Documents and 24/7 WhatsApp support for the trip.")])}</ol></div>
<div class="block" id="faqs"><h2>FAQs</h2>{faq_html(faqs)}</div>
</div>\'\'\'
        others = "".join(f'<a href="{tour_url(t[0])}">{e(t[2])} tour <span>→</span></a>' for t in TOURS if t[0] != slug)
        aside = f'<aside class="aside">{ctacard(name + " tour")}<nav class="mini"><h3>More tours</h3><a href="/honeymoon-packages">Honeymoon packages <span>→</span></a>{others}</nav></aside>'
        ph = pagehead(f"Tour package · {UPDATED}", f"{e(name)} tour package<br>from Pakistan", f"Flights, hotels and visa for {e(name)} in one booking, planned to your dates from Blue Area, Islamabad.", c["img"], c["code"], name,
                      actions=f'<a class="btn wa" href="{wa("Hi, I want a " + name + " tour package. My dates are: ")}" target="_blank" rel="noopener">💬 Plan my trip</a><a class="btn light" href="{c["url"]}">Visa requirements</a>')
        body = shell("/packages", [("Home", "/"), ("Packages", "/packages"), (f"{name} tour", None)], ph, f'<div class="layout">{main}{aside}</div>{cta_band()}')
        ld = [crumbs_ld([("Home", "/"), ("Packages", "/packages"), (f"{name} tour", url)]),
              {"@context": "https://schema.org", "@type": "TouristTrip", "name": f"{name} tour package from Pakistan", "description": f"Flights, hotels and visa for {name}, planned to your dates.",
               "touristType": ["Couples", "Families"] if honey else ["Families", "Groups"], "provider": {"@id": BASE + "/#org"}, "image": U(c["img"], 1200) if c["img"] else LOGO,
               "itinerary": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": g[0]} for i, g in enumerate(c["gallery"])]}}, faq_ld(faqs)]
        title = f"{name} Tour Package from Pakistan 2026 | AL ARBAB"
        if len(title) > 65:
            title = f"{name} Tour Package from Pakistan | AL ARBAB"
        page(url, title, f"{name} tour package from Pakistan 2026: flights, hotels and visa in one booking from Islamabad. Honeymoon and family trips planned to your dates. Price on WhatsApp.",
             body, ld, f"{name.lower()} tour package from pakistan, {name.lower()} honeymoon package, {name.lower()} tour from islamabad", image=U(c["img"], 1200) if c["img"] else None, priority="0.8")
        cards.append(ncard(url, c["img"], f"{name} tour package", "Honeymoon & family" if honey else "Family & groups", "Plan my trip →",
                           flag(c["code"], "", 40), f"{name}", ", ".join(g[0].split(",")[0] for g in c["gallery"][:2]), "Visa", ROUTE_PHRASE.get(route, route).replace("an ", "").replace("a ", "", 1).split(" at ")[0][:22], "Booking", "WhatsApp"))
    # honeymoon hub
    hon = [t for t in TOURS if t[3]]
    hcards = "".join(cards[i] for i, t in enumerate(TOURS) if t[3])
    faqs = [("Which honeymoon destinations are popular from Pakistan?", "Maldives, Turkey, Bali, Thailand, Dubai, Baku and Europe are the destinations couples ask us about most."),
            ("What documents do newly married couples need?", "Both passports, the marriage registration certificate (MRC) or updated FRC, bank statements and the usual visa documents for the destination."),
            ("How early should we book a honeymoon?", "Six to eight weeks before the wedding is comfortable for most visas; Schengen and UK need more time, especially in summer.")]
    content = f\'\'\'<section class="sec"><div class="rgrid">{hcards}</div></section>
<section class="sec reveal"><div class="prose"><h2>Honeymoon packages from Islamabad, planned to your wedding date</h2><p>We plan honeymoons from Pakistan to {", ".join(t[2] for t in hon)}. Each trip is built around your dates and budget, with flights, hotels or resorts, transfers on request and both visas prepared together.</p><h3>What we arrange</h3><ul class="checks">{"".join(f"<li>{e(x)}</li>" for x in ARRANGE)}</ul></div></section>
{sec("FAQs", "", faq_html(faqs))}{cta_band("Planning your honeymoon?", "Send your wedding date, preferred destination and budget on WhatsApp and we reply with options.")}\'\'\'
    ph = pagehead("Honeymoon", "Honeymoon packages<br>from Pakistan", "Maldives, Turkey, Bali, Thailand, Dubai, Baku and Europe — flights, hotels and visas for both of you, planned from Blue Area, Islamabad.", COUNTRIES["maldives"]["img"], alt="Maldives honeymoon",
                  actions=f'<a class="btn wa" href="{wa("Hi, we are planning our honeymoon. Wedding date: ")}" target="_blank" rel="noopener">💬 Plan our honeymoon</a>')
    body = shell("/packages", [("Home", "/"), ("Packages", "/packages"), ("Honeymoon packages", None)], ph, content)
    page("/honeymoon-packages", "Honeymoon Packages from Pakistan 2026 | AL ARBAB",
         "Honeymoon packages from Pakistan to Maldives, Turkey, Bali, Thailand, Dubai, Baku and Europe: flights, hotels and visas for both of you, planned from Islamabad.",
         body, [crumbs_ld([("Home", "/"), ("Packages", "/packages"), ("Honeymoon packages", "/honeymoon-packages")]), faq_ld(faqs)],
         "honeymoon package from pakistan, honeymoon packages from islamabad, maldives honeymoon package from pakistan, turkey honeymoon package", priority="0.8")
    return cards

# ================================================================== write'''
rep("\n# ================================================================== write", NEW)

# packages hub lists the tours too; build order: tours before packages hub
rep('''def build_packages():
    content = f\'\'\'{sec("Holiday packages",''', '''def build_packages():
    tour_cards = build_tours()
    content = f\'\'\'{sec("Tour packages by destination", "Honeymoon, family and group trips planned to your dates — flights, hotels and visa in one booking.", f'<div class="rgrid">{"".join(tour_cards)}</div><p style="margin-top:20px"><a class="btn light" href="/honeymoon-packages">Honeymoon packages</a></p>', "tours")}
{sec("Holiday packages",''')
rep('''("Umrah & packages", lambda u: u.startswith("/umrah/") or u.startswith("/packages/"))]''', '''("Umrah, packages & tours", lambda u: u.startswith("/umrah/") or u.startswith("/packages/") or u.startswith("/tours/") or u == "/honeymoon-packages")]''')
rep('''("/visa-appointments", "Visa Appointments"),''', '''("/honeymoon-packages", "Honeymoon Packages"), ("/visa-appointments", "Visa Appointments"),''')
io.open(P, "w", encoding="utf-8").write(s)
print("patched v16")
