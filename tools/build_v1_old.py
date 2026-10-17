#!/usr/bin/env python3
"""Static site generator for AL ARBAB TRAVEL AND TOURS. Run: python build.py
Edit the CONFIG / content below, re-run, deploy the folder contents."""
import json, os, html as H

BASE = "https://www.alarbabtravel.com"
NAME = "AL ARBAB TRAVEL AND TOURS"
PHONE, PHONE_I = "03152323811", "+923152323811"
LAND, LAND_I = "051-2000066", "+92512000066"
EMAIL = "alarbabtravels@gmail.com"
WA = "https://wa.me/923152323811"
ADDR = "Eagle Plaza, Mezzanine No. 121, Fazal-e-Haq Road, Blue Area, Islamabad"
HOURS = "Monday – Saturday: 8:00 AM – 8:00 PM"
LOGO = "https://www.alarbabtravel.com/assets/logo-CLLKKa8a.png"
TODAY = "2026-10-05"
SOCIAL = [("FB", "https://www.facebook.com/alarbabtravels", "Facebook"),
          ("IG", "https://www.instagram.com/alarbabtravels/", "Instagram"),
          ("X", "https://twitter.com/alarbabtravels", "X (Twitter)"),
          ("in", "https://www.linkedin.com/company/alarbabtravels/", "LinkedIn")]

def U(i, w=800):
    return f"https://images.unsplash.com/photo-{i}?q=80&w={w}&auto=format&fit=crop"

IMG = dict(th="1528181304800-259b08848526", my="1596422846543-75c6fc197f07", id="1537996194471-e657df975ab4",
           sg="1525625293386-3f8f99389edd", umrah="1591604129939-f1efa4d9f7fa", np="1544735716-392fe2489ffa",
           ae="1518684079-3c830dcef090", pk="1589182373726-e4f658ab50f0", cta="1507608616759-54f48f0af0ee",
           hero="1502602898657-3e91760cbb34")

e = H.escape
def wa_link(msg):
    from urllib.parse import quote
    return f"{WA}?text={quote(msg)}"

# ---------------------------------------------------------------- data
DEST = [
 dict(k="thailand", n="Thailand", city="Bangkok & Phuket", lat=13.75, lon=100.5, code="BKK", rating=4.9, tag="Top Tourist Favorite", visa="Sticker & eVisa", x=600, y=230, flag="🇹🇭", sub="Top Tourist Pick", p="Bangkok & Phuket (Wat Arun)"),
 dict(k="malaysia", n="Malaysia", city="Kuala Lumpur (Petronas)", lat=3.14, lon=101.69, code="KUL", rating=4.9, tag="Fast 48h eVisa", visa="Instant 48h eVisa", x=660, y=320, flag="🇲🇾", sub="Instant 48h eVisa", p="Kuala Lumpur (Petronas Towers)"),
 dict(k="indonesia", n="Indonesia", city="Bali Island (Ulun Danu)", lat=-8.41, lon=115.19, code="DPS", rating=4.9, tag="Island Special", visa="Visa on Arrival / B211A", x=700, y=400, flag="🇮🇩", sub="Visa on Arrival / B211A", p="Bali Island & Jakarta"),
 dict(k="singapore", n="Singapore", city="Marina Bay & Sentosa", lat=1.29, lon=103.86, code="SIN", rating=5.0, tag="Futuristic Modern Wonder", visa="Instant e-Visa", x=640, y=360, flag="🇸🇬", sub="Instant Electronic Visa", p="Marina Bay Sands & Sentosa"),
 dict(k="nepal", n="Nepal", city="Kathmandu & Himalayas", lat=27.7, lon=85.32, code="KTM", rating=4.8, tag="Scenic Adventure", visa="Visa on Arrival", x=470, y=210, flag="🇳🇵", sub="Scenic Adventure", p="Kathmandu & Himalayas"),
 dict(k="uae", n="Dubai", city="Burj Khalifa & Marina", lat=25.2, lon=55.27, code="DXB", rating=4.9, tag="24-48h Express Visa", visa="24-48h Express", x=330, y=190, flag="🇦🇪", sub="24-48h Express", p="Dubai Burj Khalifa & Marina"),
]
for d in DEST:
    d["img"] = U(IMG[{"thailand": "th", "malaysia": "my", "indonesia": "id", "singapore": "sg", "nepal": "np", "uae": "ae"}[d["k"]]], 1400)

PACKAGES = [
 ("thailand", "🇹🇭 Popular Pick", "Top Choice", 4.9, "2.4k", "THAILAND", "Thailand Bangkok & Phuket Island", "6 Days / 5 Nights", "Beachfront Resort | Coral Island Speedboat", ["Wat Arun & Grand Palace", "Phuket Beachfront", "Sticker & eVisa"], "th"),
 ("malaysia", "🇲🇾 Fast Approval", "Family Special", 4.8, "1.6k", "MALAYSIA", "Malaysia Kuala Lumpur & Langkawi", "5 Days / 4 Nights", "4-Star Modern Hotel | City & Cable Car Tour", ["Petronas Twin Towers", "Genting Highlands", "48-Hour eVisa"], "my"),
 ("indonesia", "🇮🇩 Island Special", "Exotic Retreat", 4.9, "1.9k", "INDONESIA", "Indonesia Bali Tropical Paradise", "6 Days / 5 Nights", "Private Pool Villa | Nusa Penida Tour", ["Ubud Sacred Monkey Forest", "Ulun Danu Lake Temple", "Visa on Arrival"], "id"),
 ("singapore", "🇸🇬 Futuristic", "Modern Wonder", 5.0, "2.8k", "SINGAPORE", "Singapore Marina Bay & Sentosa", "4 Days / 3 Nights", "Luxury City Hotel | Universal Studios & Night Safari", ["Marina Bay Sands", "Gardens by the Bay", "Instant e-Visa"], "sg"),
]

SERVICES = [
 ("✈", "Airline Tickets", "IATA-authorized ticketing with real-time fares from 22+ global carriers. Best prices guaranteed."),
 ("🌴", "Tourist Visa", "Plan your dream vacation with hassle-free tourist visa processing for 50+ countries."),
 ("👨‍👩‍👧", "Family Visit Visa", "Reunite with family abroad through our reliable visit visa service."),
 ("🏠", "Family Reunification", "Long-term family reunion visas with documentation support."),
 ("🇪🇺", "Schengen Visa", "Single visa to explore 29 European countries seamlessly."),
 ("💼", "Business Visa", "Business and corporate travel visas, fast and reliable."),
 ("🎓", "Student Visa", "Study abroad support — UK, USA, Canada, Australia & more."),
 ("🛠", "Work Permit", "Employment visa & work authorization for Gulf, Europe & beyond."),
]

REGIONS = [
 ("Schengen Area", "Visit 29 European countries on a single visa. Expert documentation and appointments."),
 ("United States", "B1/B2 tourist and business visa processing and interview prep."),
 ("United Kingdom", "Standard Visitor and Business visa expertise."),
 ("Canada", "Visit visas and Tourist pathway guidance."),
 ("Middle East", "Dubai (UAE), Saudi Arabia (Umrah/Tourist), and Oman visas."),
 ("South Asia", "Sri Lanka, Maldives, and regional visas handled seamlessly."),
 ("Central Asia", "Azerbaijan, Uzbekistan, and Turkey eVisas."),
 ("North Africa", "Egypt and Morocco visa assistance."),
 ("Southern Africa", "Expert processing for South Africa, Mauritius, and Kenya."),
 ("East Asia", "China, Japan, and South Korea visa assistance."),
 ("South America", "Brazil, Argentina, Colombia & more."),
 ("Oceania", "Australia, New Zealand, Fiji & more."),
 ("Australia", "Subclass 600 visitor visa processing and expert documentation."),
]

UMRAH = [
 ("Economy Package", "185,000", "15 Days", ["Standard Hotels (1km+)", "Shared Transport", "Visa Processing", "Return Flights"]),
 ("3 Star Package", "225,000", "15 Days", ["3 Star Hotels (600m)", "Luxury Transport", "Visa Processing", "Breakfast Included"]),
 ("4 Star Package", "285,000", "10-15 Days", ["4 Star Hotels (Walking Distance)", "Private Transport", "Visa & Insurance", "Breakfast & Ziarat"]),
 ("5 Star Luxury", "395,000", "7-15 Days", ["Front-row 5 Star Hotels", "VIP Private Transport", "Full Board Options", "24/7 Ground Support"]),
]

AIRLINES = [
 ("pk", "🇵🇰 Pakistani", [("🇵🇰", "Pakistan International Airlines", "PK", "1955", "Islamabad / Karachi", ["Pakistan's national carrier", "Extensive domestic network"]),
   ("🇵🇰", "AirSial", "PF", "2020", "Sialkot", ["Modern fuel-efficient fleet", "Growing domestic operations"]),
   ("🇵🇰", "Fly Jinnah", "9P", "2022", "Karachi", ["Budget-friendly fares", "Air Arabia group expertise"]),
   ("🇵🇰", "SereneAir", "ER", "2017", "Islamabad / Lahore", ["Premium cabin comfort", "Strong domestic presence"])]),
 ("gulf", "🌙 Gulf & Middle East", [("🇦🇪", "Emirates", "EK", "1985", "Dubai (DXB)", ["World's largest A380 operator", "Connectivity via Dubai hub"]),
   ("🇶🇦", "Qatar Airways", "QR", "1993", "Doha (DOH)", ["World's Best Airline 2024", "Award-winning Business Class"]),
   ("🇦🇪", "Etihad Airways", "EY", "2003", "Abu Dhabi (AUH)", ["Luxurious The Residence suite", "Abu Dhabi hub connectivity"]),
   ("🇦🇪", "flydubai", "FZ", "2009", "Dubai (DWC)", ["Budget carrier from Dubai", "SKYWARDS mile accrual"]),
   ("🇦🇪", "Air Arabia", "G9", "2003", "Sharjah (SHJ)", ["GCC's first LCC", "Sharjah hub for easy access"]),
   ("🇸🇦", "Saudi Arabian Airlines", "SV", "1945", "Jeddah (JED) / Riyadh (RUH)", ["Largest Hajj flights operator", "Riyadh & Jeddah hubs"]),
   ("🇸🇦", "Flynas", "XY", "2007", "Riyadh (RUH)", ["Saudi LCC pioneer", "Affordable hajj transfers"]),
   ("🇰🇼", "Kuwait Airways", "KU", "1953", "Kuwait City (KWI)", ["Gulf's oldest carrier", "Strong Pakistan connections"]),
   ("🇧🇭", "Gulf Air", "GF", "1950", "Bahrain (BAH)", ["One of MENA's oldest airlines", "Bahrain hub connectivity"]),
   ("🇴🇲", "Oman Air", "WY", "1993", "Muscat (MCT)", ["Consistent quality rankings", "Muscat hub access"])]),
 ("eu", "🌍 Europe & Turkey", [("🇹🇷", "Turkish Airlines", "TK", "1933", "Istanbul (IST)", ["Flies to most countries globally", "Istanbul mega-hub connections"]),
   ("🇬🇧", "British Airways", "BA", "1974", "London Heathrow (LHR)", ["London direct from Pakistan", "BA Avios reward flights"])]),
 ("ea", "🏯 East Asia", [("🇨🇳", "Air China", "CA", "1988", "Beijing (PEK)", ["China's flag carrier", "Beijing Capital hub"]),
   ("🇨🇳", "China Southern", "CZ", "1988", "Guangzhou (CAN)", ["Asia's largest airline by fleet", "Guangzhou super-hub"])]),
 ("sea", "🌺 SE Asia", [("🇹🇭", "Thai Airways", "TG", "1960", "Bangkok (BKK)", ["Southeast Asia specialist", "Royal Orchid Plus miles"]),
   ("🇲🇾", "Batik Air Malaysia", "OD", "2013", "Kuala Lumpur (KUL)", ["Full-service at LCC prices", "KL hub connectivity"])]),
 ("ca", "🏔️ Central Asia", [("🇺🇿", "Uzbekistan Airways", "HY", "1992", "Tashkent (TAS)", ["Tashkent gateway to CIS", "Direct Islamabad connections"])]),
 ("af", "⭐ Africa", [("🇪🇹", "Ethiopian Airlines", "ET", "1945", "Addis Ababa (ADD)", ["Africa's largest airline", "ShebaMiles loyalty"])]),
]

ROUTES = [("London", "ISB → LHR", "PIA, EMIRATES, TURKISH"), ("Dubai", "ISB → DXB", "EMIRATES, FLYDUBAI, PIA"),
          ("Toronto", "ISB → YYZ", "TURKISH, EMIRATES, QATAR"), ("Jeddah", "ISB → JED", "PIA, SAUDI, FLYNAS"),
          ("New York", "ISB → JFK", "EMIRATES, TURKISH, QATAR"), ("Istanbul", "ISB → IST", "TURKISH AIRLINES"),
          ("Melbourne", "ISB → MEL", "EMIRATES, QATAR, THAI"), ("Doha", "ISB → DOH", "QATAR AIRWAYS, PIA")]

FAQ_HOME = [
 ("Is AL ARBAB TRAVEL AND TOURS an IATA-authorized travel agency?", "Yes. We are an IATA-accredited agency (certified in 2015) and can issue tickets directly, with instant e-ticket confirmation."),
 ("Which visas do you process from Islamabad?", "Tourist, family visit, family reunification, Schengen, business, student visas and work permits for 50+ countries, with special expertise in Schengen, USA, UK, Canada and Australia."),
 ("What is your visa approval rate?", "98% across Schengen, UK, USA, Canada and Australia categories combined, based on the last 24 months of completed cases."),
 ("Do you offer Umrah packages?", "Yes. Umrah packages start from PKR 185,000 (Economy) and go up to 5-Star Luxury from PKR 395,000, plus fully customizable options."),
 ("Where is your office and how do I contact you?", f"Our office is at {ADDR}. Call {PHONE} or {LAND}, email {EMAIL}, or message us on WhatsApp. Hours: {HOURS}."),
]
FAQ_AIR = [
 ("Is AL ARBAB TRAVEL AND TOURS an IATA-authorized travel agency?", "Yes. We hold full IATA accreditation, allowing us to issue tickets directly on 300+ airlines worldwide with guaranteed fare accuracy and instant e-ticket confirmation."),
 ("How do I get cheap flights from Islamabad to London?", "Our ticketing officers manually audit routes to find hidden savings such as split-ticketing or alternative hubs. Send us your dates on WhatsApp and we will quote the best fare within minutes."),
 ("Can I book group flights for Umrah or Hajj from Islamabad?", "Yes. We offer group flight booking that lets you block seats with minimal deposits and manage name changes flexibly — ideal for weddings, sports teams and religious groups."),
 ("Do you offer student discount flights from Pakistan?", "Yes. We help students secure discounted tickets with extra baggage allowances on carriers such as Virgin Atlantic, Etihad and British Airways. Bring your university offer letter."),
 ("What airlines can I book through AL ARBAB TRAVEL AND TOURS?", "We work with 22+ partner airlines including Emirates, Qatar Airways, Turkish Airlines, PIA, Saudia and British Airways, and as an IATA agent we can book 300+ airlines worldwide."),
 ("How fast can I get my e-ticket after booking?", "E-tickets are issued instantly once payment is confirmed. Our average response time is 15 minutes."),
 ("Do you handle flight cancellations and date changes?", "Yes. Our human-powered support team is available around the clock to handle cancellations, urgent date changes and other emergencies."),
 ("Where is your office located in Islamabad?", f"{ADDR}. Open {HOURS}."),
]
FAQ_UMRAH = [
 ("How much does an Umrah package from Pakistan cost in 2026?", "Packages start from PKR 185,000 for Economy (15 days), PKR 225,000 for 3 Star, PKR 285,000 for 4 Star and PKR 395,000 for 5 Star Luxury. Final price depends on hotels, dates and group size."),
 ("Are you an authorized Umrah agent?", "Yes. We are officially authorized by the Ministry of Hajj & Umrah and process visas directly in Blue Area, Islamabad via official Saudi portals."),
 ("Can I customize my Umrah itinerary?", "Yes. Choose from 300+ hotels in Makkah and Madinah, pick private GMC or luxury bus transport, and stay 7, 10, 15 or 30 days — as a group or private family package."),
]

# ---------------------------------------------------------------- schema
def org_ld():
    return {"@context": "https://schema.org", "@type": ["TravelAgency", "LocalBusiness"], "@id": BASE + "/#org",
            "name": NAME, "url": BASE + "/", "logo": LOGO, "image": U(IMG["hero"], 1600),
            "description": "IATA-authorized travel agency in Islamabad: visa consultancy for 50+ countries, cheap air ticketing, Umrah packages, hotel booking and holiday packages.",
            "slogan": "Pakistan's #1 IATA Authorized Agency — Explore Beautiful World With Us",
            "telephone": [PHONE_I, LAND_I], "email": EMAIL, "priceRange": "$$", "foundingDate": "2009",
            "currenciesAccepted": "PKR", "address": {"@type": "PostalAddress", "streetAddress": ADDR.replace(", Islamabad", ""), "addressLocality": "Islamabad", "addressRegion": "Islamabad Capital Territory", "postalCode": "44000", "addressCountry": "PK"},
            "geo": {"@type": "GeoCoordinates", "latitude": 33.7135, "longitude": 73.0673},
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "08:00", "closes": "20:00"}],
            "areaServed": [{"@type": "Country", "name": "Pakistan"}, {"@type": "City", "name": "Islamabad"}, {"@type": "City", "name": "Rawalpindi"}, {"@type": "City", "name": "Lahore"}, {"@type": "City", "name": "Karachi"}],
            "sameAs": [s[1] for s in SOCIAL],
            "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE_I, "contactType": "customer support", "areaServed": "PK", "availableLanguage": ["English", "Urdu"]}]}

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def website_ld():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": NAME, "inLanguage": "en-PK", "publisher": {"@id": BASE + "/#org"}}

# ---------------------------------------------------------------- shared chrome
NAV = [("", "Home"), ("visa-services", "Visa"), ("air-ticketing", "Flights"), ("umrah", "Umrah"),
       ("countries", "Destinations"), ("hotel-booking", "Hotels"), ("partner-airlines", "Airlines"), ("about", "About"), ("contact", "Contact")]

def href(root, p):
    return root if p == "" else f"{root}{p}/"

def header(root, cur):
    links = "".join(f'<a class="pill" href="{href(root, p)}"{" aria-current=\"page\"" if p == cur else ""}>{n}</a>' for p, n in NAV)
    return f'''<header class="nav" role="banner">
  <a class="brand" href="{href(root, "")}" aria-label="{NAME} home"><span class="lg"><img src="{LOGO}" alt="{NAME} logo" width="34" height="34" onerror="this.replaceWith('⛰')"></span><span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></a>
  <button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu">☰</button>
  <nav class="menu" id="menu" aria-label="Main navigation">{links}</nav>
  <a class="cta-dark" href="{WA}" target="_blank" rel="noopener">✦ WhatsApp Us</a>
</header>'''

def footer(root):
    soc = "".join(f'<a href="{u}" target="_blank" rel="noopener me" aria-label="{n}">{s}</a>' for s, u, n in SOCIAL)
    q = [("visa-services", "Visa Consultancy"), ("umrah", "Umrah Packages 2026"), ("air-ticketing", "Air Ticketing"), ("hotel-booking", "Hotel Bookings"), ("partner-airlines", "Partner Airlines"), ("about", "About Us"), ("contact", "Contact Us")]
    ql = "".join(f'<li><a href="{href(root, p)}">{n}</a></li>' for p, n in q)
    dl = "".join(f'<li><a href="{root}countries/#{d["k"]}">{d["flag"]} {d["n"]}</a></li>' for d in DEST[:5]) + f'<li><a href="{root}countries/#schengen">🇪🇺 Europe &amp; Schengen</a></li>'
    return f'''<footer>
  <div class="cols">
    <div><h4>{NAME}</h4><p>Pakistan's #1 travel agency &amp; world-class visa consultancy. IATA-accredited experts for Schengen, USA, UK, Canada, Australia visas &amp; Umrah packages.</p>
      <div class="badges"><span>IATA Authorized</span><span>15+ Years Trust</span><span>98% Approval Rate</span><span>Islamabad Blue Area</span></div>
      <div class="soc">{soc}</div></div>
    <div><h4>Quick Links</h4><ul>{ql}</ul></div>
    <div><h4>Top Destinations</h4><ul>{dl}</ul></div>
    <div><h4>Contact &amp; Head Office</h4>
      <address style="font-style:normal"><p><b>Helpline &amp; Landline</b><br><a href="tel:{PHONE_I}">{PHONE}</a> | <a href="tel:{LAND_I}">{LAND}</a></p>
      <p style="margin-top:10px"><b>Email</b><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p style="margin-top:10px"><b>Blue Area Office</b><br>{ADDR}</p>
      <p style="margin-top:10px"><b>Office Hours</b><br>{HOURS}</p></address>
      <p style="margin-top:14px"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">Instant WhatsApp Inquiry</a></p></div>
  </div>
  <div class="bottom"><span>© 2026 {NAME}. All Rights Reserved.</span><span>IATA Authorized Agent · Islamabad, Pakistan</span></div>
</footer>
<a class="fab" href="{WA}?text=Hi%20AL%20ARBAB%20TRAVEL%20AND%20TOURS%2C%20I%20need%20help%20with%20a%20visa%20enquiry." target="_blank" rel="noopener" aria-label="Chat on WhatsApp">💬 <span>Chat with us</span></a>
<div id="toast" role="status" aria-live="polite"></div>'''

def page(path, title, desc, body, ld=None, kw="", root="", image=None, extra_head="", extra_script="", home=False):
    canon = BASE + ("/" if path == "" else f"/{path}/")
    img = image or U(IMG["hero"], 1200)
    ld = [org_ld(), website_ld()] + (ld or []) if home else [org_ld()] + (ld or [])
    ldt = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f'''<!doctype html>
<html lang="en-PK">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(kw)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#A0B1AE">
<meta name="author" content="{NAME}">
<meta name="geo.region" content="PK-IS"><meta name="geo.placename" content="Islamabad"><meta name="geo.position" content="33.7135;73.0673">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en-pk" href="{canon}"><link rel="alternate" hreflang="x-default" href="{canon}">
<link rel="icon" href="{LOGO}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:locale" content="en_PK">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{img}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">
{extra_head}
{ldt}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{body}
<script>window.SITE={{wa:"{WA}",email:"{EMAIL}"}};</script>
{extra_script}
<script src="{root}assets/app.js" defer></script>
</body>
</html>'''

def faq_html(faq):
    return "".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faq)

def sec(h2, lead, inner, id_="", cta=""):
    return f'<section class="sec reveal"{f" id=\"{id_}\"" if id_ else ""}><div class="head"><div><h2>{h2}</h2></div>{f"<p class=\"lead\">{lead}</p>" if lead else ""}{cta}</div>{inner}</section>'

def inner_page(path, cur_title, h1, intro, content, title, desc, kw, ld=None, faq=None, image=None, extra_script="", extra_head=""):
    root = "../"
    crumbs = [("Home", "/"), (cur_title, f"/{path}/")]
    ldx = [crumbs_ld(crumbs)] + (ld or [])
    if faq:
        ldx.append(faq_ld(faq))
    faqs = sec("Frequently asked questions", "", faq_html(faq)) if faq else ""
    cta = f'''<section class="sec reveal"><div class="band"><div><h2>Ready to plan your trip?</h2><p>Send us your route, dates or visa question — our team replies within 1 business hour. {HOURS}.</p></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">💬 WhatsApp {PHONE}</a><a class="btn light" href="{root}contact/">Contact us</a></div></div></section>'''
    body = f'''<main id="main"><div class="wrap"><div class="shell"><div class="inner">
{header(root, path)}
<div class="pagehead"><nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a> / {e(cur_title)}</nav><h1>{h1}</h1><p>{intro}</p></div>
</div></div>
<div id="content">{content}{faqs}{cta}</div></div></main>
{footer(root)}'''
    return page(path, title, desc, body, ldx, kw, root, image, extra_head, extra_script)

# ---------------------------------------------------------------- pages
def pkg_cards(root):
    out = []
    for k, badge, tag, rate, rc, country, name, dur, stay, feats, im in PACKAGES:
        li = "".join(f"<li>{e(f)}</li>" for f in feats)
        msg = wa_link(f"Hi {NAME}, I am interested in the {name} package ({dur}). Please share details and price.")
        out.append(f'''<article class="card"><div class="im"><span class="badge">{badge}</span><span class="rate">★ {rate} ({rc})</span><img src="{U(IMG[im])}" alt="{e(name)} holiday package from Islamabad" loading="lazy" width="800" height="533"></div>
<div class="bd"><span class="tag">{tag} · {country}</span><h3>{e(name)}</h3><p><b>{dur}</b><br>{e(stay)}</p><ul>{li}</ul>
<a class="more" href="{root}countries/#{k}">View package details <span>→</span></a></div></article>''')
    return "".join(out)

def build_home():
    d0 = DEST[0]
    dest_js = [dict(n=d["n"], city=d["city"], lat=d["lat"], lon=d["lon"], code=d["code"], rating=d["rating"], tag=d["tag"], visa=d["visa"], x=d["x"], y=d["y"], img=d["img"], url=f"countries/#{d['k']}") for d in DEST]
    visa_cards = "".join(f'''<a class="dest" href="countries/#{d["k"]}"><img src="{U(IMG[{"thailand":"th","malaysia":"my","indonesia":"id","singapore":"sg","nepal":"np","uae":"ae"}[d["k"]]])}" alt="{d["n"]} visa and travel – {d["city"]}" loading="lazy" width="800" height="533"><div><small>{d["flag"]} {d["n"]} · {d["sub"]}</small><h3>{d["n"]}</h3><p>{d["p"]}</p></div></a>''' for d in DEST)
    visa_cards += f'''<a class="dest" href="countries/#pakistan"><img src="{U(IMG["pk"])}" alt="Pakistan inbound tourism – Hunza Valley" loading="lazy" width="800" height="533"><div><small>🇵🇰 Inbound Tourism</small><h3>Pakistan</h3><p>Hunza Valley &amp; Historic Heritage</p></div></a>'''
    why = [("💰", "Best Price Guarantee", "IATA-authorized airfares and transparent visa fees with no hidden charges."),
           ("🕑", "24/7 Customer Support", f"Direct phone &amp; WhatsApp support: {PHONE} available anytime."),
           ("⚡", "Easy &amp; Fast Booking", "Seamless document review, online appointments &amp; instant ticket issuance."),
           ("🏆", "98% Visa Success Rate", "Over 15 years of industry excellence and 20,000+ happy travelers.")]
    why_h = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p></div>' for a, b, c in why)
    svc = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p></div>' for a, b, c in SERVICES[:4])
    body = f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><clipPath id="blobclip" clipPathUnits="objectBoundingBox"><path d="M0,0.5 Q0,0.40 0.06,0.40 L0.20,0.40 Q0.27,0.40 0.27,0.30 L0.27,0.09 Q0.27,0 0.35,0 L0.93,0 Q1,0 1,0.07 L1,0.93 Q1,1 0.93,1 L0.07,1 Q0,1 0,0.93 Z"/></clipPath></defs></svg>
<main id="main"><div class="wrap"><div class="shell"><div class="inner">
{header("", "")}
<section class="hero" aria-labelledby="h1">
  <div class="left">
    <p class="eyebrow rise" style="animation-delay:.3s"><i></i>Pakistan's #1 IATA Authorized Agency | 98% Visa Approval</p>
    <h1 id="h1" class="rise" style="animation-delay:.45s">Explore<br>Beautiful World<br>With Us</h1>
    <p class="sub rise" style="animation-delay:.6s">{NAME} — expert visa consultancy for 50+ countries, cheap air ticketing, luxury stays &amp; Umrah packages from Blue Area, Islamabad.</p>
    <div class="actions rise" style="animation-delay:.75s"><a class="start" href="visa-services/"><i>»</i>Discover Now</a><a class="start" href="air-ticketing/"><i>✈</i>Book Flights</a></div>
    <p class="rise" style="animation-delay:.9s;margin-top:16px"><a class="link" id="hlink" href="countries/#thailand">Explore this destination →</a></p>
    <div class="weather rise" style="animation-delay:1s" aria-live="polite"><h6><span>LIVE WEATHER</span><span id="wplace">{d0["city"]}</span></h6>
      <div class="dial" id="dial"><div id="temp">--°C</div></div><div class="meta"><b>Destination weather now</b><span id="wdesc">Loading…</span></div></div>
  </div>
  <div class="visual">
    <div class="dests" id="dtabs" role="tablist" aria-label="Featured destinations"></div>
    <div class="blob" id="blob">
      <img class="photo on" id="photoA" src="{d0["img"]}" alt="{d0["n"]} – {d0["city"]} travel and visa packages from Islamabad" fetchpriority="high" width="1400" height="933">
      <img class="photo" id="photoB" alt="" width="1400" height="933">
      <svg class="flight" viewBox="0 0 800 560" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <path id="fpath" d="M150,470 Q375,230 600,230" fill="none" stroke="#fff" stroke-width="3.2" stroke-dasharray="9 7" stroke-linecap="round"/>
        <circle cx="150" cy="470" r="10" fill="#fff"/><circle cx="150" cy="470" r="4" fill="#091413"/><text x="150" y="502" fill="#fff" font-size="15" font-weight="700" text-anchor="middle" font-family="Inter">ISB</text>
        <circle id="pend" cx="600" cy="230" r="10" fill="#2fd1b0"/><circle cx="0" cy="0" r="0"/><text id="pendT" x="600" y="212" fill="#fff" font-size="15" font-weight="700" text-anchor="middle" font-family="Inter">{d0["code"]}</text>
        <g id="plane"><path d="M14,0 L-10,-10 L-5,0 L-10,10 Z" fill="#fff" stroke="#091413" stroke-width="1.5"/></g>
      </svg>
      <div class="float" style="left:56%;top:24%"><em style="background:var(--orange)">★</em><span>Top rated<b id="f1t">★ 4.9</b></span></div>
      <div class="float" style="left:66%;top:42%"><em style="background:#6c5a7a">🌍</em><span>Highlight<b id="f2t"></b></span></div>
      <div class="float" style="left:60%;top:62%"><em style="background:#1d8a5c">✓</em><span>Visa<b id="f3t"></b></span></div>
      <div class="social"><div class="faces" aria-hidden="true"><span style="background:#c9a98b">🧳</span><span style="background:#9fb7a5">✈️</span><span style="background:#b79c9c">🕋</span></div><div><strong><span data-count="20000" data-suffix="+">20,000+</span></strong><small>Happy travelers</small></div></div>
    </div>
  </div>
</section>
<div class="chips rise" style="animation-delay:1.2s">
  <a class="chip" href="visa-services/">◈ Visa Consultancy</a><a class="chip" href="air-ticketing/">✈ Air Ticketing</a><a class="chip" href="umrah/">🕋 Umrah Packages</a><a class="chip" href="hotel-booking/">🏨 Hotels</a>
  <div class="stats"><div><b data-count="15" data-suffix="+">15+</b><small>Years experience</small></div><div><b data-count="98" data-suffix="%">98%</b><small>Approval rate</small></div><div><b data-count="20000" data-suffix="+">20,000+</b><small>Happy travelers</small></div></div>
</div>
</div>
<form class="search" id="searchForm" aria-label="Plan your trip">
  <div><label for="to">Where to?</label><input id="to" name="to" placeholder="Thailand, Dubai, Europe…" required></div>
  <div><label for="in">Check in</label><input id="in" name="in" type="date"></div>
  <div><label for="out">Check out</label><input id="out" name="out" type="date"></div>
  <div><label for="pax">Travelers</label><select id="pax" name="pax"><option>1 Adult</option><option selected>2 Adults, 1 Child</option><option>2 Adults</option><option>Family (5+)</option><option>Group</option></select></div>
  <button class="btn" type="submit">Search</button>
</form></div>

{sec("Exclusive travel packages", "All-inclusive international packages curated for Pakistani travelers.", f'<div class="grid g4">{pkg_cards("")}</div>', "packages")}
{sec("Featured visit visa destinations", "Thailand, Malaysia, Indonesia, Umrah, Nepal &amp; Dubai — hassle-free visa processing with guaranteed documentation support.",
  f'''<div class="umrah"><div class="t"><span class="eyebrow">🕋 Sacred Journey · VIP Packages 2026</span><h3>Umrah Packages — Makkah &amp; Madinah Luxury Stays</h3><p>Complete Umrah visa processing, 5-star luxury hotels near Haram, VIP airport transfers, curated ziyarat tours &amp; dedicated 24/7 Nusuk platform assistance.</p><div><a class="btn" href="umrah/">Explore Umrah packages</a></div></div><div class="pic"><img src="{U(IMG["umrah"], 1000)}" alt="Umrah packages 2026 – Kaaba, Makkah" loading="lazy" width="1000" height="667"></div></div>
  <div class="grid g4">{visa_cards}</div>
  <p style="margin-top:20px"><a class="btn" href="countries/">View all destinations</a></p>''', "destinations")}
{sec("Why travel with us?", "", f'<div class="grid g4">{why_h}</div>')}
{sec("Our core services", "From visas to flights and hotels — one IATA-authorized desk in Blue Area, Islamabad.", f'<div class="grid g4">{svc}</div><p style="margin-top:20px"><a class="btn light" href="visa-services/">See all visa services</a></p>')}
{sec("Frequently asked questions", "", faq_html(FAQ_HOME))}
<section class="sec reveal"><div class="band"><div><h2>Subscribe to our newsletter</h2><p>Get the latest visa updates, flight discounts &amp; exclusive Umrah packages from {NAME}.</p></div>
<form class="nl" id="nlForm"><label for="nle" class="sr" style="position:absolute;left:-999px">Email</label><input id="nle" type="email" placeholder="Your email address" required><button type="submit">Subscribe</button></form></div></section>
</div></main>
{footer("")}'''
    ld = [faq_ld(FAQ_HOME), {"@context": "https://schema.org", "@type": "ItemList", "name": "Exclusive travel packages",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "TouristTrip", "name": p[6], "description": f"{p[7]} — {p[8]}. " + ", ".join(p[9]), "touristType": "Family, Couples"}} for i, p in enumerate(PACKAGES)]}]
    script = f'<script>window.DEST={json.dumps(dest_js, ensure_ascii=False)};</script>'
    return page("", "Visa Consultant & Travel Agency Islamabad | AL ARBAB",
                "Pakistan's #1 IATA authorized travel agency in Islamabad. Visa consultancy for 50+ countries, cheap flights, Umrah packages & holiday deals. 98% visa approval.",
                body, ld, "visa consultant islamabad, schengen visa pakistan, uk visa islamabad, usa visa pakistan, canada visa islamabad, travel agency islamabad, iata authorized travel agent pakistan, cheap flights islamabad, umrah packages 2026, air ticketing islamabad, hotel booking islamabad",
                "", None, "", script, home=True)

def build_visa():
    svc = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p><p style="margin-top:12px"><a class="link" href="{wa_link("Hi, I need help with " + b)}" target="_blank" rel="noopener">Learn more →</a></p></div>' for a, b, c in SERVICES)
    inc = ["End-to-end documentation & embassy support", "Personalized visa pathway assessment", "Document checklist tailored to your case", "Form filling & application review", "Embassy appointment booking", "Interview preparation & coaching", "Real-time application tracking"]
    c = f'''{sec("Visa services", "Whether you're visiting family, studying abroad or expanding your business — our expert team handles every detail.", f'<div class="grid g4">{svc}</div>', "services")}
<section class="sec reveal"><div class="split"><div class="prose"><h2>What's included</h2><ul class="checks">{"".join(f"<li>{x}</li>" for x in inc)}</ul><p><a class="btn" href="../contact/">Start your application</a></p></div>
<div class="prose" style="align-content:center"><span class="eyebrow">Approval rate</span><div class="big"><span data-count="98" data-suffix="%">98%</span></div><p>Across Schengen, UK, USA, Canada and Australia categories combined — based on the last 24 months of completed cases.</p></div></div></section>
<section class="sec reveal"><div class="prose"><h2>Expert visa consultants in Islamabad for global destinations</h2>
<p>As the best visa consultant in Islamabad (ISB), {NAME} provides end-to-end immigration and travel solutions. Whether you are seeking a top visa consultant in Islamabad, planning a European tour, or navigating complex family reunification processes, our certified experts ensure a smooth, transparent, and successful application journey.</p>
<div class="two"><div><h3>Schengen visa from Pakistan</h3><p>Applying for a Schengen visa in Islamabad can be complex due to stringent documentation requirements. As a top Europe visa consultant in Islamabad, we specialize in tourist, business, and family visit visas for all Schengen states, including Germany, France, Italy, and Spain. We handle your complete itinerary, hotel bookings, and travel insurance to maximize your approval chances.</p></div>
<div><h3>UK visa consultant Islamabad</h3><p>Whether you need a Business Visa, a Standard Visitor Visa, or a Tourist Visa, our top visa agents in ISB provide comprehensive guidance. We assist with UKVI requirements, financial proof compilation, and interview preparation, making us the most reliable visa consultant ISB for United Kingdom immigration.</p></div>
<div><h3>USA visa processing (B1/B2)</h3><p>Securing a US visa requires meticulous preparation. Our USA visa consultant ISB team offers specialized interview coaching and DS-160 form filling services. From B1/B2 tourist visas to business visas, we provide the best visa guidance to confidently face the US embassy consular officers.</p></div>
<div><h3>Canada &amp; Australia visas</h3><p>Looking for reliable visit visa pathways? We handle visitor applications for Canada (TRV) and Australia (Subclass 600) with the highest level of professionalism and accuracy. Let our international visa experts simplify the process for you.</p></div></div>
<h2>Why choose the top visa consultancy in ISB?</h2>
<p>Located conveniently in Blue Area, {NAME} is recognized as the best immigration agency in Islamabad. We don't just fill out forms; we provide strategic visa solutions ISB tailored to your specific profile.</p>
<div class="kw"><span>Authorized visa agent ISB</span><span>Fast visa processing Islamabad</span><span>Visa documentation Islamabad</span><span>Embassy visa support Islamabad</span></div></div></section>'''
    ld = [{"@context": "https://schema.org", "@type": "Service", "serviceType": "Visa consultancy", "name": "Visa consultancy in Islamabad", "provider": {"@id": BASE + "/#org"}, "areaServed": {"@type": "Country", "name": "Pakistan"},
           "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Visa services", "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": b, "description": cc}} for _, b, cc in SERVICES]}}]
    return inner_page("visa-services", "Visa Services", "Visas tailored<br>to your journey", "Expert visa consultancy in Islamabad for Schengen, UK, USA, Canada, Australia and 50+ countries — 98% approval rate.", c,
        "Best Visa Consultant in Islamabad 2026 | AL ARBAB TRAVEL",
        "Top visa consultant in Islamabad (Blue Area). Schengen, UK, USA, Canada & Australia visas with 98% approval. Documentation, appointments & interview coaching.",
        "visa consultant islamabad, schengen visa pakistan, uk visa islamabad, usa visa pakistan, canada visa islamabad, visa agent isb, immigration agency islamabad", ld)

def build_air():
    feats = [("✅", "IATA Authorized", "Officially accredited ticketing agency."), ("🌍", "International Routes", "All major airlines worldwide."), ("💸", "Best Fares", "Lowest available pricing, transparent fees."), ("🕑", "24/7 Support", "Booking changes anytime, anywhere.")]
    fh = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p></div>' for a, b, c in feats)
    rt = "".join(f'<div class="route"><span class="c">{c}</span><b>Islamabad → {n}</b><small>{al}</small><a href="{wa_link(f"Hi, I need a fare quote for Islamabad to {n} ({c}).")}" target="_blank" rel="noopener">Get fare quote →</a></div>' for n, c, al in ROUTES)
    chk = ["Passport validity must be at least 6 months.", "Check transit visa requirements for layovers.", "Ensure your name matches your passport exactly.", "Verify baggage allowance (2PC vs 30KG)."]
    c = f'''<section class="sec reveal"><div class="grid g4">{fh}</div></section>
<section class="sec reveal"><div class="split"><div class="prose"><span class="eyebrow">Global network</span><h2>Seamless connections to over 200+ destinations</h2><p>As an IATA-certified agency, we bridge the gap between you and the world's leading airlines. Our direct integration with global distribution systems (GDS) ensures that you see real-time availability and "web-only" fares that aren't available to the general public.</p><div class="kw"><span>Instant E-Tickets</span><span>Group Discounts</span><span>Student Fares</span><span>Multi-city Routes</span></div></div>
<div class="prose" style="align-content:center"><span class="eyebrow">Avg response time</span><div class="big">15<small style="font-size:.3em"> MINS</small></div><p>Ready to fly? Send us your route and dates — we'll quote the best fare within minutes.</p><p><a class="btn wa" href="{WA}" target="_blank" rel="noopener">Contact ticketing officer</a></p></div></div></section>
{sec("Popular flight routes from Islamabad", "Discover our most frequently booked international sectors and the top airlines servicing them.", f'<div class="grid g4">{rt}</div>')}
<section class="sec reveal"><div class="prose"><h2>Why choose {NAME} for your flight bookings?</h2>
<p>Finding the best air ticketing agency in Islamabad can be overwhelming with so many options in Blue Area. However, {NAME} stands out as a premier IATA-authorized travel agent. This status is not just a badge; it signifies our commitment to professional standards, financial security, and direct relationships with over 300 airlines worldwide.</p>
<div class="two"><div><h3>Cheap flights from Islamabad</h3><p>Our team specializes in finding cheap flights from Islamabad to major hubs including London, New York, Toronto, Dubai, and Melbourne. Our expert ticketing officers manually audit routes to find hidden savings, such as "split-ticketing" or alternative hubs that can save you thousands of rupees on international flight bookings.</p></div>
<div><h3>Global airline partnerships</h3><p>We are proud partners with the world's leading carriers. Whether you prefer the luxury of Emirates and Qatar Airways, the extensive network of Turkish Airlines, or the convenience of PIA, we provide seamless reservations. <a class="link" href="../partner-airlines/">See all partner airlines →</a></p></div>
<div><h3>Corporate &amp; group travel</h3><p>We offer specialized group flight booking in Islamabad, allowing you to block seats with minimal deposits and manage name changes flexibly. Perfect for weddings, sports teams, and religious groups.</p></div>
<div><h3>Special student discounts</h3><p>Traveling for studies? We assist students in securing discounted tickets from Islamabad with extra baggage allowances on major airlines like Virgin Atlantic, Etihad, and British Airways. Bring your university offer letter.</p></div></div>
<h3>Ticketing checklist</h3><ul class="checks">{"".join(f"<li>{x}</li>" for x in chk)}</ul>
<h3>24/7 urgent support</h3><p>Flight cancelled? Need an urgent date change? Our "Human-Powered" support is available around the clock to handle emergencies.</p></div></section>'''
    return inner_page("air-ticketing", "Air Ticketing", "IATA-authorized tickets<br>at the best fares", "Instant booking on every major airline — domestic and international — backed by 24/7 support.", c,
        "Air Ticketing Agency Islamabad | Cheap Flights IATA",
        "IATA-authorized air ticketing in Islamabad. Cheap flights to London, Dubai, Toronto, Jeddah & more on 300+ airlines. Instant e-tickets, group & student fares.",
        "air ticketing islamabad, cheap flights islamabad, iata travel agent pakistan, pia booking islamabad, emirates tickets islamabad, qatar airways pakistan", faq=FAQ_AIR)

def build_umrah():
    pk = "".join(f'''<article class="card"><div class="bd"><span class="tag">{d}</span><h3>{n}</h3><div class="price"><small>From</small>PKR {p}</div><ul>{"".join(f"<li>{x}</li>" for x in f)}</ul>
<a class="more" href="{wa_link(f"Hi, I want to book the {n} Umrah package (from PKR {p}).")}" target="_blank" rel="noopener">Book now <span>→</span></a></div></article>''' for n, p, d, f in UMRAH)
    partners = [("✈️", "Airlines", "Saudia, flynas, PIA"), ("🏨", "Hotels", "Clock Tower, Hilton, Pullman"), ("🚌", "Transport", "SAPCTO, Private GMCs"), ("🛂", "Visa Systems", "Direct Maqam Integration")]
    ph = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p></div>' for a, b, c in partners)
    why = [("Authorized Umrah visa agent", "Direct processing in Blue Area, ISB via official Saudi portals"), ("Confirmed hotel bookings", "Guaranteed Makkah & Madinah proximity before you pay"), ("Best Umrah airfares", "Exclusive blocked group rates from Islamabad & Lahore"), ("24/7 pilgrim support", "Dedicated Pakistani support team on the ground in KSA")]
    wh = "".join(f'<li><span><b>{a}</b><br>{b}</span></li>' for a, b in why)
    c = f'''<section class="sec reveal"><div class="umrah"><div class="t"><span class="eyebrow">Spiritual journey</span><h3>"Perform Umrah and Hajj, as they remove poverty and sins…"</h3><p>— Prophet Muhammad (PBUH). From budget-friendly economy stays to premium 5-star luxury experiences — we handle every detail of your sacred pilgrimage.</p></div><div class="pic"><img src="{U(IMG["umrah"], 1000)}" alt="Umrah packages from Pakistan 2026 – Makkah" width="1000" height="667"></div></div></section>
{sec("Choose the package that fits your journey", "We offer a variety of pre-designed packages and fully customizable options to suit your preferences.", f'<div class="grid g4">{pk}</div>', "packages")}
{sec("Direct deals &amp; global partnerships", f"{NAME} is officially authorized by the Ministry of Hajj &amp; Umrah. We cut out the middlemen to bring you direct contracts with top Saudi providers.", f'<div class="grid g4">{ph}</div>')}
<section class="sec reveal"><div class="band"><div><h2>Customized Umrah planning</h2><p>Can't find exactly what you're looking for? Build your own itinerary: choose from 300+ hotels in Makkah &amp; Madinah, private GMC or luxury bus transport, flexible stays of 7, 10, 15 or 30 days, as a group or private family package.</p></div><div><a class="btn wa" href="{wa_link("Hi, I would like a custom Umrah quote.")}" target="_blank" rel="noopener">Request custom quote</a></div></div></section>
<section class="sec reveal"><div class="prose"><h2>Expert Umrah travel agency in Islamabad</h2>
<p>Finding the best Umrah packages from Pakistan 2026 can be overwhelming. At {NAME}, we simplify your spiritual journey. As a leading Umrah travel agency in Islamabad, we provide verified cheap Umrah packages that don't compromise on quality or proximity to the holy sites.</p>
<div class="two"><div><h3>Economy &amp; budget Umrah 2026</h3><p>Our economy Umrah packages 2026 are perfect for families looking for affordability. We ensure clean, certified hotels with dedicated shuttle services to the Haram, making it the most reliable budget Umrah Islamabad option without hidden costs.</p></div>
<div><h3>Luxury 5-star experience</h3><p>For those seeking ultimate comfort, our luxury Umrah packages 2026 feature stays in the iconic Clock Tower or hotels directly facing the Haram courtyard. With private VIP transport and premium ground handling, your focus remains entirely on your prayers.</p></div></div>
<h2>Why book your Umrah with us?</h2><ul class="checks">{wh}</ul></div></section>'''
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "Umrah packages 2026", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Service", "name": f"Umrah {n}", "provider": {"@id": BASE + "/#org"}, "offers": {"@type": "Offer", "priceCurrency": "PKR", "price": p.replace(",", ""), "description": f"From PKR {p} · {d}"}}} for i, (n, p, d, f) in enumerate(UMRAH)]}]
    return inner_page("umrah", "Umrah Packages", "Umrah packages designed<br>for peace of mind", "Economy to 5-star Umrah packages 2026 from Islamabad — visa, flights, hotels and 24/7 ground support.", c,
        "Best Umrah Packages 2026 from Pakistan | AL ARBAB",
        "Book Umrah packages 2026 from Islamabad: Economy from PKR 185,000 to 5-Star Luxury. Ministry-authorized agent, visa, flights, hotels & 24/7 support.",
        "umrah packages 2026, umrah packages from pakistan, cheap umrah packages islamabad, luxury umrah packages, umrah visa agent islamabad", ld, FAQ_UMRAH, U(IMG["umrah"], 1200))

def build_countries():
    reg = "".join(f'<div class="feat"><div class="ic">🌐</div><h3>{n}</h3><p>{d}</p><p style="margin-top:12px"><a class="link" href="{wa_link(f"Hi, I need visa details for {n}.")}" target="_blank" rel="noopener">Explore →</a></p></div>' for n, d in REGIONS)
    popular = ""
    for d in DEST:
        pk = next((p for p in PACKAGES if p[0] == d["k"]), None)
        extra = f'<p><b>{pk[6]}</b> — {pk[7]}. {e(pk[8])}.</p><ul>{"".join(f"<li>{e(x)}</li>" for x in pk[9])}</ul>' if pk else f'<p>{d["p"]} — {d["sub"]}.</p>'
        popular += f'''<article class="card" id="{d["k"]}"><div class="im"><span class="badge">{d["flag"]} {d["sub"]}</span><img src="{d["img"].replace("w=1400","w=800")}" alt="{d["n"]} – {d["city"]}" loading="lazy" width="800" height="533"></div><div class="bd"><h3>{d["n"]}</h3>{extra}<a class="more" href="{wa_link(f"Hi, I want details and visa help for {d['n']}.")}" target="_blank" rel="noopener">Ask about {d["n"]} <span>→</span></a></div></article>'''
    popular += f'''<article class="card" id="pakistan"><div class="im"><span class="badge">🇵🇰 Inbound Tourism</span><img src="{U(IMG["pk"])}" alt="Pakistan – Hunza Valley" loading="lazy" width="800" height="533"></div><div class="bd"><h3>Pakistan</h3><p>Hunza Valley &amp; Historic Heritage — inbound tourism support.</p><a class="more" href="{wa_link("Hi, I want details about Pakistan inbound tourism.")}" target="_blank" rel="noopener">Ask about Pakistan <span>→</span></a></div></article>'''
    c = f'''{sec("Popular destinations", "Packages and visa support for the most requested countries from Islamabad.", f'<div class="grid">{popular}</div>', "popular")}
{sec("Explore our global destinations", "Select a region or country to view detailed visa requirements, processing times, and required documentation.", f'<div class="grid g4" id="schengen">{reg}</div>')}
<section class="sec reveal"><div class="prose"><h2>Your trusted partner for global destinations in Islamabad</h2><p>Choosing the right destination requires the right guidance. As the top visa consultancy in Islamabad, {NAME} simplifies the application process for over 50 countries.</p>
<div class="two"><div><h3>Schengen &amp; European visas</h3><p>Applying for a Schengen visa from Pakistan requires precision. We cover the Schengen member states, including popular destinations like France, Germany, Italy, and Spain. Our Islamabad-based experts handle your flight reservations, hotel bookings, and travel insurance to meet strict embassy standards.</p></div>
<div><h3>The Americas (USA &amp; Canada)</h3><p>Navigating the complex requirements for a USA visa from Islamabad (B1/B2, F1) or a Canadian study permit demands an experienced hand. We provide thorough DS-160 processing, interview coaching, and documentation review.</p></div>
<div><h3>Oceania (Australia &amp; New Zealand)</h3><p>From Sydney to Auckland, securing an Australia visit visa ISB or an NZeTA is seamless with our support. We assist students, tourists, and skilled workers with precise documentation alignment.</p></div>
<div><h3>Middle East &amp; Asia</h3><p>Looking for a reliable Dubai visit visa consultant in Islamabad? We offer rapid processing for UAE, Qatar, Bahrain, and Saudi Arabia, plus Malaysia, Thailand, and Singapore for holiday or business trips.</p></div></div></div></section>'''
    return inner_page("countries", "Destinations", "Visa support across<br>every continent", "From iconic European capitals to vibrant Middle Eastern hubs and Oceania's natural wonders — 50+ visa destinations from Islamabad.", c,
        "50+ Visa Destinations Worldwide | AL ARBAB TRAVEL",
        "Visa and holiday packages for 50+ destinations from Islamabad: Thailand, Malaysia, Bali, Singapore, Dubai, Nepal, Schengen, USA, UK, Canada & Australia.",
        "visa destinations, thailand visa pakistan, malaysia visa pakistan, dubai visa pakistan, schengen visa islamabad, bali visa pakistan")

def build_hotel():
    t = [("🏨", "Luxury Stays", "5-star resorts, suites and exclusive properties."), ("🛏", "Mid-range Comfort", "Trusted brands and great locations."), ("💡", "Budget Friendly", "Verified value stays for smart travelers."), ("🌐", "Global hotel partners", "Direct contracts with leading chains across Europe, the Americas, Middle East, and Asia.")]
    th = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p></div>' for a, b, c in t)
    c = f'''<section class="sec reveal"><div class="grid g4">{th}</div><p style="margin-top:20px"><a class="btn wa" href="{wa_link("Hi, I need a hotel booking.")}" target="_blank" rel="noopener">Book a hotel</a></p></section>
<section class="sec reveal"><div class="prose"><h2>Expert hotel booking agent in Islamabad</h2><p>Securing the right accommodation is critical, especially when applying for visas. As the premier hotel booking agent in Islamabad, {NAME} offers verifiable and cheap hotel reservations for visa applications. Embassies, particularly for Schengen and the US, require confirmed hotel bookings; we ensure your documentation is flawless to prevent visa rejections.</p>
<p>Beyond visa compliance, we offer exceptional deals for holidaymakers and corporate travelers. Whether you need a luxury 5-star resort in Dubai, a boutique hotel in Paris, or a budget-friendly stay in London, our international partnerships guarantee the best rates. Let the best travel agent for hotels in Blue Area handle your itinerary seamlessly.</p></div></section>'''
    return inner_page("hotel-booking", "Hotel Booking", "Stay where you love,<br>save where it matters", "From 5-star icons to boutique gems and value stays — we book it all.", c,
        "Hotel Booking Agent Islamabad | Visa Hotel Reservations",
        "Verifiable hotel reservations for visa applications and holidays. Luxury, mid-range and budget stays worldwide, booked by Islamabad's IATA-authorized agency.",
        "hotel booking islamabad, hotel reservation for visa, cheap international hotel booking, hotel booking agent pakistan")

def build_airlines():
    tabs = '<button type="button" data-r="all" aria-pressed="true">✈️ All (22)</button>' + "".join(f'<button type="button" data-r="{k}" aria-pressed="false">{n} ({len(a)})</button>' for k, n, a in AIRLINES)
    cards = ""
    for k, n, al in AIRLINES:
        for fl, nm, code, est, hub, f in al:
            cards += f'''<article class="air" data-region="{k}"><div class="top"><span style="font-size:26px">{fl}</span><span class="code">{code}</span></div><h3>{nm}</h3><small>Est. {est} · {hub}</small><ul>{"".join(f"<li>• {x}</li>" for x in f)}</ul><a href="{wa_link(f"Hi, I want a fare on {nm} ({code}).")}" target="_blank" rel="noopener">Enquire now →</a></article>'''
    wh = [("🎫", "Real-time fares", "Live pricing from all partner airlines — no markup, no middlemen"), ("📞", "Expert advice", "Our ticketing specialists find you the best route & cabin every time"), ("✅", "IATA authorized", "Fully licensed to issue tickets for all international carriers"), ("💬", "WhatsApp booking", "Book 24/7 via WhatsApp — instant confirmation, no paperwork")]
    wf = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p></div>' for a, b, c in wh)
    c = f'''<section class="sec reveal"><div class="stats" style="margin:0 0 24px"><div><b>22+</b><small>Partner airlines</small></div><div><b>140+</b><small>Destinations</small></div><div><b>IATA</b><small>Authorized agent</small></div></div>
<div class="tabs" id="airTabs" role="group" aria-label="Filter airlines by region">{tabs}</div><div class="grid g4">{cards}</div></section>
{sec("Direct access. Better prices.", "", f'<div class="grid g4">{wf}</div>')}'''
    return inner_page("partner-airlines", "Partner Airlines", "World-class airlines.<br>One agency.", f"{NAME} is an IATA-authorized travel partner with direct access to real-time fares from 22+ global carriers. From budget to luxury — we connect Pakistan to the world.", c,
        "Partner Airlines | Emirates, Qatar, PIA, Turkish | AL ARBAB",
        "IATA-authorized agent with 22+ partner airlines: PIA, Emirates, Qatar Airways, Etihad, Turkish, British Airways, Saudia & more. Real-time fares from Islamabad.",
        "partner airlines pakistan, emirates tickets islamabad, qatar airways pakistan, turkish airlines islamabad, pia booking islamabad, british airways islamabad")

def build_about():
    vals = [("🎯", "Our mission", "Empower every traveler with transparent, expert visa and travel guidance — no shortcuts, no false promises, no surprises."), ("🔭", "Our vision", "To be Pakistan's most universally trusted name in visa consultancy by continually setting new industry standards in service and integrity."), ("💎", "Our values", "Honesty in assessment, expertise in execution, accountability in results, and an obsessive focus on the client experience.")]
    vh = "".join(f'<div class="feat"><div class="ic">{a}</div><h3>{b}</h3><p>{c}</p></div>' for a, b, c in vals)
    tl = [("2009", "The Beginning", f"{NAME} opened its first small office, focusing on Umrah and basic ticketing services with a commitment to honest pricing."), ("2015", "IATA Accreditation", "Achieved full IATA certification, allowing us to issue global air tickets directly and solidifying our status as a premium travel agency."), ("2019", "Visa Consultancy Expansion", "Expanded our dedicated visa department to handle complex Schengen, UK, and USA cases, achieving an unprecedented 98% approval rate."), ("2026", "Leading the Industry", "Today, we operate from a state-of-the-art office in Blue Area, recognized as Islamabad's #1 trusted visa and travel partner.")]
    th = "".join(f"<div><b>{y}</b><h3>{t}</h3><p>{d}</p></div>" for y, t, d in tl)
    ex = [("Schengen Visas", "Expert profiling for Europe"), ("USA & UK Visas", "B1/B2 and Standard Visitor"), ("Umrah Packages", "Direct Ministry allocations"), ("Global Ticketing", "IATA direct lowest fares"), ("Travel Insurance", "Instant Schengen compliant"), ("Corporate Travel", "B2B travel management")]
    eh = "".join(f'<div class="feat"><h3>{a}</h3><p>{b}</p></div>' for a, b in ex)
    c = f'''<section class="sec reveal"><div class="split"><div class="prose"><span class="eyebrow">Established 2009</span><h2>Trusted advisors for life-changing journeys</h2><p>{NAME} began with a simple promise — make global travel accessible to every Pakistani family, student, and professional. Today, we are recognized as one of Islamabad's premier visa consultancies, with a reputation built on absolute transparency, deep expertise, and an unwavering commitment to client success.</p><p>From complex Schengen and US visitor visas to family reunification and IATA-authorized global ticketing, our dedicated team in Blue Area delivers premium, white-glove service at every step of your application.</p><p><a class="btn" href="../contact/">Book a free consultation</a></p></div>
<div class="prose" style="align-content:center"><div class="stats" style="margin:0;gap:34px"><div><b class="big" style="font-size:54px"><span data-count="15" data-suffix="+">15+</span></b><small>Years of experience</small></div><div><b class="big" style="font-size:54px"><span data-count="20" data-suffix="K+">20K+</span></b><small>Happy travelers</small></div><div><b class="big" style="font-size:54px"><span data-count="98" data-suffix="%">98%</span></b><small>Approval rate</small></div><div><b class="big" style="font-size:54px"><span data-count="50" data-suffix="+">50+</span></b><small>Countries covered</small></div></div></div></div></section>
{sec("The foundation of our success", "The core principles that drive every application we process and every ticket we book.", f'<div class="grid">{vh}</div>')}
{sec("A legacy of trust", "", f'<div class="timeline">{th}</div>')}
{sec("Comprehensive global expertise", "We don't just fill out forms. We strategically build your profile to ensure maximum approval chances across various travel sectors.", f'<div class="grid g4">{eh}</div>')}'''
    ld = [{"@context": "https://schema.org", "@type": "AboutPage", "name": f"About {NAME}", "url": BASE + "/about/", "about": {"@id": BASE + "/#org"}}]
    return inner_page("about", "About Us", "Premium visa consultancy<br>from the heart of Islamabad", f"Since 2009, {NAME} has helped over 20,000 travelers secure visas, flights and travel solutions to 50+ destinations worldwide.", c,
        "About Us | Visa & Travel Agency Since 2009 | AL ARBAB",
        "Since 2009, AL ARBAB TRAVEL AND TOURS has helped 20,000+ travelers with visas, IATA ticketing and Umrah. Blue Area, Islamabad. 98% approval rate.",
        "about al arbab travel, travel agency islamabad since 2009, iata accredited agency pakistan", ld)

def build_contact():
    info = [("📍", "Office", ADDR), ("📞", "Phone", f'<a href="tel:{PHONE_I}">{PHONE}</a> | <a href="tel:{LAND_I}">{LAND}</a>'), ("✉", "Email", f'<a href="mailto:{EMAIL}">{EMAIL}</a>'),
            ("🕑", "Hours", HOURS), ("💬", "WhatsApp", f'<a href="{WA}" target="_blank" rel="noopener">{PHONE}</a>'), ("👍", "Facebook", '<a href="https://www.facebook.com/alarbabtravels" target="_blank" rel="noopener me">Follow us on Facebook</a>')]
    ih = "".join(f'<div><span class="ic">{a}</span><span><small>{b.upper()}</small>{c}</span></div>' for a, b, c in info)
    opts = "".join(f"<option>{o}</option>" for o in ["Schengen / Europe", "USA", "UK", "Canada", "Australia", "Thailand", "Malaysia", "Indonesia (Bali)", "Singapore", "Dubai / UAE", "Nepal", "Umrah / Saudi Arabia", "Other"])
    c = f'''<section class="sec reveal" style="margin-top:20px"><div class="contactgrid"><div class="info">{ih}
<iframe class="map" title="Map: {NAME} office, Blue Area, Islamabad" loading="lazy" src="https://www.openstreetmap.org/export/embed.html?bbox=73.0600%2C33.7090%2C73.0750%2C33.7180&amp;layer=mapnik&amp;marker=33.7135%2C73.0673"></iframe></div>
<form class="f" id="contactForm"><h2 style="font-size:24px;text-transform:uppercase">Send a message</h2><p style="font-size:13px;color:#3a4d49">Fill out the form below and our visa experts will get back to you promptly. We typically reply within 1 business hour.</p>
<div class="row"><div><label for="name">Full name</label><input id="name" name="name" required autocomplete="name"></div><div><label for="email">Email address</label><input id="email" name="email" type="email" required autocomplete="email"></div></div>
<div class="row"><div><label for="phone">WhatsApp number</label><input id="phone" name="phone" type="tel" required autocomplete="tel"></div><div><label for="dest">Target destination</label><select id="dest" name="dest">{opts}</select></div></div>
<div><label for="msg">Travel plans &amp; details</label><textarea id="msg" name="msg" rows="4"></textarea></div>
<div><button class="btn wa" type="submit">Send your inquiry via WhatsApp</button></div></form></div></section>'''
    ld = [{"@context": "https://schema.org", "@type": "ContactPage", "name": f"Contact {NAME}", "url": BASE + "/contact/", "about": {"@id": BASE + "/#org"}}]
    return inner_page("contact", "Contact", "We'd love<br>to hear from you", "Walk in, call, email or message us on WhatsApp. We typically reply within 1 business hour.", c,
        "Contact Visa Consultant Islamabad | AL ARBAB Blue Area",
        f"Visit AL ARBAB TRAVEL AND TOURS at Eagle Plaza, Blue Area, Islamabad. Call {PHONE} / {LAND}, email or WhatsApp. {HOURS}.",
        "contact travel agency islamabad, visa office blue area islamabad, eagle plaza blue area travel agency", ld)

def build_404():
    body = f'''<div class="wrap"><div class="shell"><div class="inner">{header("/", "")}<main id="main"><div class="pagehead"><h1>Page not<br>found</h1><p>The page you are looking for does not exist. Try our visa services, flights or Umrah packages.</p><p style="margin-top:20px"><a class="btn" href="/">Back to home</a></p></div></main></div></div></div>{footer("/")}'''
    return page("404", "Page not found | " + NAME, "Page not found.", body, None, "", "/").replace('content="index,follow', 'content="noindex,follow')

# ---------------------------------------------------------------- write
def out(path, content):
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    open(d, "w", encoding="utf-8").write(content)

if __name__ == "__main__":
    pages = {"": build_home(), "visa-services": build_visa(), "air-ticketing": build_air(), "umrah": build_umrah(), "countries": build_countries(),
             "hotel-booking": build_hotel(), "partner-airlines": build_airlines(), "about": build_about(), "contact": build_contact()}
    for p, c in pages.items():
        out("index.html" if p == "" else f"{p}/index.html", c)
    out("404.html", build_404())
    urls = "".join(f'  <url><loc>{BASE}/{p + "/" if p else ""}</loc><lastmod>{TODAY}</lastmod><changefreq>{"weekly" if p == "" else "monthly"}</changefreq><priority>{"1.0" if p == "" else "0.8"}</priority></url>\n' for p in pages)
    out("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    out("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    print("built", len(pages) + 1, "pages")
