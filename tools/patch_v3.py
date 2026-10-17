# one-off patch: travelvisa.pk-style features (country page fee/toc/refusal/sources, open status, GA4)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new):
    global s
    assert old in s, "missing: " + old[:80]
    s = s.replace(old, new, 1)

rep('TODAY = "2026-10-05"', '''TODAY = "2026-10-05"
UPDATED = "October 2026"
GA_ID = ""            # Google Analytics 4 measurement ID, e.g. "G-XXXXXXX". Empty = no tracking script.''')

rep("# ------------------------------------------------------------------ page text", '''# official portals for the "Sources" box on country pages (only well-known government sites)
OFFICIAL = {
 "malaysia": [("Malaysia eVISA portal", "https://malaysiavisa.imi.gov.my/")],
 "turkey": [("Turkey e-Visa (official)", "https://www.evisa.gov.tr/")],
 "azerbaijan": [("Azerbaijan ASAN e-Visa", "https://evisa.gov.az/")],
 "sri-lanka": [("Sri Lanka ETA (official)", "https://www.eta.gov.lk/")],
 "singapore": [("Singapore ICA", "https://www.ica.gov.sg/")],
 "thailand": [("Thailand e-Visa (official)", "https://www.thaievisa.go.th/")],
 "indonesia": [("Indonesia e-Visa (Imigrasi)", "https://evisa.imigrasi.go.id/")],
 "cambodia": [("Cambodia e-Visa (official)", "https://www.evisa.gov.kh/")],
 "vietnam": [("Vietnam e-Visa (official)", "https://evisa.gov.vn/")],
 "egypt": [("Egypt e-Visa portal", "https://visa2egypt.gov.eg/")],
 "oman": [("Royal Oman Police e-Visa", "https://evisa.rop.gov.om/")],
 "bahrain": [("Bahrain e-Visa", "https://www.evisa.gov.bh/")],
 "uzbekistan": [("Uzbekistan e-Visa", "https://e-visa.gov.uz/")],
 "saudi-arabia": [("Saudi visa platform", "https://visa.visitsaudi.com/")],
 "kenya": [("Kenya eTA (official)", "https://www.etakenya.go.ke/")],
 "australia": [("Visitor visa subclass 600 (Home Affairs)", "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600")],
}
REGION_OFFICIAL = {
 "united-kingdom": [("UK Standard Visitor visa (GOV.UK)", "https://www.gov.uk/standard-visitor")],
 "united-states": [("US visitor visas (travel.state.gov)", "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html"), ("DS-160 online form (CEAC)", "https://ceac.state.gov/genniv/")],
 "canada": [("Visit Canada (IRCC)", "https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada.html")],
 "australia": [("Visitor visa subclass 600 (Home Affairs)", "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600")],
 "schengen": [("Schengen visa policy (European Commission)", "https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/visa-policy_en")],
}
REFUSAL = [("Weak financial proof", "Bank statements with sudden large deposits, a low closing balance or no maintenance certificate."),
           ("Unclear ties to Pakistan", "No proof of job, business, property or family that shows you will return."),
           ("Mismatched details", "Names, dates or salary figures that differ between the form, bank statement and letters."),
           ("Incomplete bookings", "Missing hotel or flight reservations for the full stay, or insurance below the required cover."),
           ("Weak cover letter", "No clear purpose of visit, itinerary or explanation of who pays for the trip.")]
APPOINTMENT_CENTRES = [("United Kingdom", "VFS Global (UK Visa Application Centre)", "/countries/united-kingdom"),
                       ("United States", "CGI Federal fee & appointment; interview at US Embassy Islamabad or Consulate Karachi", "/countries/united-states"),
                       ("Spain", "BLS International", "/countries/schengen/spain"), ("Netherlands", "VFS Global", "/countries/schengen/netherlands"),
                       ("Sweden", "VFS Global", "/countries/schengen/sweden"), ("Greece", "GVCW visa centre", "/countries/schengen/greece"),
                       ("France", "France-Visas online portal", "/countries/schengen/france"), ("Denmark", "ApplyVisa portal", "/countries/schengen/denmark"),
                       ("Norway", "UDI online portal", "/countries/schengen/norway"), ("Other Schengen states", "VFS Global / BLS / Gerry's, depending on the embassy", "/countries/schengen")]

# ------------------------------------------------------------------ page text''')

rep('("/packages", "Packages"), ("/about", "About"), ("/contact", "Contact")]', '("/packages", "Packages"), ("/eligibility-check", "Free Check"), ("/contact", "Contact")]')

rep('''    return f\'\'\'<div class="ctacard"><h2>Free assessment</h2>''', '''    return f\'\'\'<div class="ctacard"><p class="open" data-open-status>Office hours: Mon–Sat, 8 AM – 8 PM</p><h2>Free assessment</h2>''')

rep('''{extra_head}
<script>document.documentElement.classList.add('js')</script>''', '''{extra_head}
{GA_TAG}
<script>document.documentElement.classList.add('js')</script>''')
rep("PAGES = {}   # url -> (html, priority, noindex)", '''PAGES = {}   # url -> (html, priority, noindex)
GA_TAG = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{GA_ID}");</script>'
          if GA_ID else "")''')

# ---------------- country page
rep('''    siblings = [x for x in BY_REGION[c["region"]] if x["slug"] != c["slug"] and x["region"] == c["region"]]
    main = f\'\'\'<div class="stack">
<div class="block"><h2>{e(c["name"])} visa services in Islamabad</h2><p>{e(c["intro"])}</p></div>
<div class="block"><h2>Required documents for {e(c["name"])} visa</h2><ul class="docs">{docs}</ul><p class="note" style="margin-top:14px"><b>Visa fee:</b> {e(c["fee"])}. Requirements can change; we give you an updated checklist for your exact case.</p></div>
{places_block}
<div class="block"><h2>How we process your application</h2><ol class="steps">{steps_html(st)}</ol></div>
''', '''    siblings = [x for x in BY_REGION[c["region"]] if x["slug"] != c["slug"] and x["region"] == c["region"]]
    srcs = OFFICIAL.get(c["slug"], []) + REGION_OFFICIAL.get(c["region"], [])
    src_block = (f'<div class="block" id="sources"><h2>Official sources</h2><p>Always confirm the latest rules on the official portal. We check every file against these requirements before submission.</p><ul class="srcs">'
                 + "".join(f'<li><a href="{u}" target="_blank" rel="noopener nofollow">{e(n)} ↗</a></li>' for n, u in srcs) + "</ul></div>") if srcs else ""
    refusal = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in REFUSAL)
    toc_items = [("about", "Overview"), ("fee", "Visa fee"), ("documents", "Documents"), ("places", "Places to visit") if places_block else None,
                 ("process", "How to apply"), ("refusal", "Refusal reasons"), ("sources", "Official sources") if src_block else None, ("faqs", "FAQs")]
    toc = '<nav class="mini toc" aria-label="On this page"><h3>On this page</h3>' + "".join(f'<a href="#{i}">{n} <span>↓</span></a>' for i, n in filter(None, toc_items)) + "</nav>"
    places_block = places_block.replace('<div class="block">', '<div class="block" id="places">', 1)
    main = f\'\'\'<div class="stack">
<div class="block" id="about"><h2>{e(c["name"])} visa services in Islamabad</h2><p>{e(c["intro"])}</p></div>
<div class="block" id="fee"><h2>{e(c["name"])} visa fee in Pakistan</h2><div class="feebox"><div><small>Embassy / visa fee</small><b>{e(c["fee"])}</b></div><div><small>Processing time</small><b>{e(proc)}</b></div><div><small>Our service charges</small><b>Quoted on WhatsApp before you pay</b></div></div>
<p style="margin-top:12px">Embassy fees change with exchange rates and policy. Send us your travel dates and we confirm the current fee and our all-in price for your case. No payment until you agree.</p>
<p style="margin-top:12px"><a class="btn wa" href="{wa("Hi, what is the total price for a " + c["name"] + " visa?")}" target="_blank" rel="noopener">💬 Ask today's price</a></p></div>
<div class="block" id="documents"><h2>Required documents for {e(c["name"])} visa</h2><ul class="docs">{docs}</ul><p class="note" style="margin-top:14px">Requirements can change; we give you an updated checklist for your exact case. <a class="link" href="/eligibility-check?d={c["slug"]}">Get your personal checklist →</a></p></div>
{places_block}
<div class="block" id="process"><h2>How we process your application</h2><ol class="steps">{steps_html(st)}</ol></div>
<div class="block" id="refusal"><h2>Common reasons {e(c["name"])} visas get refused</h2><ul class="refuse">{refusal}</ul><p style="margin-top:12px">Our free file check looks for exactly these problems before you submit.</p></div>
{src_block}
''')
rep('''<div class="block"><h2>{e(c["name"])} visa FAQs</h2>{faq_html(faqs)}</div>''', '''<div class="block" id="faqs"><h2>{e(c["name"])} visa FAQs</h2>{faq_html(faqs)}</div>''')
rep('''    aside = f'<aside class="aside">{ctacard(c["name"] + " visa")}<nav class="mini" aria-label="Related">''', '''    aside = f'<aside class="aside">{toc}{ctacard(c["name"] + " visa")}<nav class="mini" aria-label="Related">''')
rep('''    ph = pagehead(e(r["name"]), e(c["title"]), e(c["description"]), c["img"], c["code"],''', '''    ph = pagehead(f'{e(r["name"])} · Updated {UPDATED}', e(c["title"]), e(c["description"]), c["img"], c["code"],''')
rep('''    title = f"{c['name']} Visa from Pakistan | Requirements & Fee | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa from Pakistan | AL ARBAB"''', '''    title = f"{c['name']} Visa Fee in Pakistan & Documents 2026 | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Fee in Pakistan & Documents | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Fee & Documents | AL ARBAB"''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched")
