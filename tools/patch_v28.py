"""v28 - clean unverified claims out of data/site-data.json (rules agreed with the owner, Oct 2026):
badges and invented ratings, Umrah authorisation wording, 24/7, response times, airline counts, superlatives,
"cheap flights", and office hours made consistent (Mon-Sat 9am-8pm).

  py tools/patch_v28.py --dry    show every change, write nothing
  py tools/patch_v28.py          apply (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "site-data.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
print("round trip identical to the file on disk:", json.dumps(d, ensure_ascii=False, indent=1) in (raw, raw.rstrip("\n")))
log = []

def setp(obj, key, old, new, where):
    """Replace a substring inside obj[key]; old must be present unless already replaced."""
    s = obj[key]
    if old in s:
        obj[key] = s.replace(old, new); log.append((where, old, new))
    elif new not in s:
        raise SystemExit(f"NOT FOUND in {where}: {old!r}")

def drop(obj, key, where):
    if key in obj:
        log.append((where, f"{key} = {obj[key]!r}", "(field removed)")); del obj[key]

C = {c["slug"]: c for lst in d["countries"].values() for c in lst}
R = {r["slug"]: r for r in d["regions"]}

# Rule 1 - badges, tags and invented ratings
for p in d["packages"]:
    drop(p, "discountBadge", f"packages/{p['id']}"); drop(p, "tag", f"packages/{p['id']}")
    hl = p["highlights"]
    for i, h in enumerate(hl):
        new = {"Instant e-Visa": "e-Visa support", "Fast 24h E-Visa": "E-Visa support", "48-Hour eVisa": "eVisa support", "Nusuk Support": "Visa file preparation"}.get(h)
        if new: log.append((f"packages/{p['id']}/highlights", h, new)); hl[i] = new
for v in d["visaDest"]:
    drop(v, "tag", f"visaDest/{v['country']}")
for h in d["heroDest"]:
    drop(h, "rating", f"heroDest/{h.get('id')}"); drop(h, "visaTag", f"heroDest/{h.get('id')}")

# Rule 2 - Umrah: no authorisation claims, describe what we actually do
setp(d["faqSchengenGeneral"][2], "a", "Yes, we process standalone Umrah visas for clients who wish to book their own flights and accommodations. However, booking a complete Umrah package through us often results in better overall rates due to our direct B2B contracts with Saudi hotels and airlines.",
     "Yes. We can prepare a standalone Umrah visa file for clients who book their own flights and hotels. A complete package can be simpler, because we arrange the hotels, flights and visa file together.", "faqSchengenGeneral[2]")
setp(C["saudi-arabia"], "description", "Instant processing.", "We prepare your visa file.", "countries/saudi-arabia/description")
setp(C["saudi-arabia"], "intro", "We process both Tourist and Umrah visas instantly, providing complete support for Nusuk registration and hotel bookings.",
     "We prepare Tourist and Umrah visa files and arrange hotel bookings.", "countries/saudi-arabia/intro")

# Rule 3 - 24/7 -> Mon-Sat, 9am-8pm (and one set of office hours everywhere)
setp(d["umrah"][3]["features"], 4, "24/7 Ground Support", "WhatsApp support, Mon–Sat, 9am–8pm", "umrah[3]/features")
setp(d["faqAir"][6], "a", "Yes, our 24/7 support team handles all post-booking changes", "Yes. Mon–Sat, 9am–8pm, we handle post-booking changes", "faqAir[6]")
setp(d["faqAir"][7], "a", "We are open Monday to Saturday, 10 AM – 7 PM.", "We are open Monday to Saturday, 9 AM – 8 PM.", "faqAir[7]")
setp(d["faqSchengenGeneral"][7], "a", "Monday through Saturday from 10:00 AM to 7:00 PM.", "Monday through Saturday from 9:00 AM to 8:00 PM.", "faqSchengenGeneral[7]")

# Rule 4 - numbers and response times
setp(d["faqAir"][4], "a", ", and 290+ more.", " and other airlines.", "faqAir[4]")
setp(d["faqAir"][5], "a", "Instant. Once payment is confirmed, your e-ticket is issued within minutes and sent directly to your email and WhatsApp.",
     "Once payment is confirmed, we issue your e-ticket and send it to your email and WhatsApp. We reply during office hours.", "faqAir[5]")
setp(d["services"][0], "desc", "IATA-authorized ticketing with real-time fares from 22+ global carriers. Best prices guaranteed.", "Ticketing with real-time fares from major airlines.", "services[0]")
setp(d["services"][1], "desc", "processing for 50+ countries.", "processing, with 86 country guides.", "services[1]")

# Rule 6 - superlatives and "cheap flights"
setp(d["faqSchengenGeneral"][5], "q", "Do you provide cheap flights from Islamabad to London or USA?", "Do you book flights from Islamabad to London or USA?", "faqSchengenGeneral[5]/q")
setp(d["faqSchengenGeneral"][5], "a", "Absolutely. As direct ticketing agents, we offer exclusive discounted airfares from Islamabad (ISB) to major destinations like London (LHR), New York (JFK), and Toronto (YYZ) via Emirates, Qatar Airways, Turkish Airlines, and British Airways. We also offer special student baggage allowances.",
     "Yes. We book flights from Islamabad (ISB) to destinations like London (LHR), New York (JFK) and Toronto (YYZ) on Emirates, Qatar Airways, Turkish Airlines and British Airways, and we check student baggage allowances for you.", "faqSchengenGeneral[5]/a")
setp(d["faqAir"][1], "q", "How do I get cheap flights from Islamabad to London?", "How do I book flights from Islamabad to London?", "faqAir[1]/q")
setp(d["faqAir"][1], "a", "to find the lowest price with the best route for ISB to LHR flights.", "and send you the fare and route options for ISB to LHR flights.", "faqAir[1]/a")
setp(C["france"], "intro", "We are recognized as the top France visa consultant in Islamabad,", "As a France visa consultant in Islamabad, we provide", "countries/france/intro")
setp(C["france"], "intro", "we provide providing end-to-end services", "we provide end-to-end services", "countries/france/intro (grammar)")
setp(C["hong-kong"], "intro", "is a premier global financial hub", "is a major global financial hub", "countries/hong-kong/intro")
setp(C["netherlands"], "intro", "acts as your premier Netherlands visa consultant", "acts as your Netherlands visa consultant", "countries/netherlands/intro")
setp(C["switzerland"], "intro", "As the leading Switzerland visa consultant in Islamabad,", "As a Switzerland visa consultant in Islamabad,", "countries/switzerland/intro")
setp(C["austria"], "intro", "As Pakistan's leading Austria visa consultant,", "As an Austria visa consultant,", "countries/austria/intro")
setp(R["schengen"], "seoTitle", "Schengen Visa Consultant Islamabad | Top Europe Visa Agency", "Schengen Visa Consultant Islamabad | Europe Visas from Pakistan", "regions/schengen/seoTitle")
setp(R["schengen"], "keywords", "best visa consultant Islamabad", "visa consultant Islamabad", "regions/schengen/keywords")
setp(R["united-kingdom"], "seoTitle", "UK Visa Consultant Islamabad | Best Visa Consultancy ISB", "UK Visa Consultant Islamabad | UK Visitor Visa ISB", "regions/united-kingdom/seoTitle")
setp(R["canada"], "seoDescription", "Top Canada visa consultant in Islamabad.", "Canada visa consultant in Islamabad.", "regions/canada/seoDescription")
setp(R["canada"], "keywords", "IRCC authorized consultant", "Canada visa documents", "regions/canada/keywords")
setp(R["middle-east"], "seoDescription", "Top visa agency for Middle East travel in Islamabad. Fast Dubai visit visas, Saudi tourist visas, and Oman eVisas.",
     "Visa agency for Middle East travel in Islamabad: Dubai visit visas, Saudi tourist visas and Oman eVisas.", "regions/middle-east/seoDescription")
setp(R["middle-east"], "intro", "We are your premier partner for Middle Eastern travel. From instant Dubai (UAE) eVisas to the new Saudi Tourist visas and Oman applications, we provide rapid, reliable service with minimum documentation required.",
     "We help with Middle Eastern travel, from Dubai (UAE) eVisas to the new Saudi Tourist visas and Oman applications, with minimum documentation required.", "regions/middle-east/intro")
setp(R["middle-east"]["stepByStep"][0], "title", "Instant Processing", "Simple paperwork", "regions/middle-east/stepByStep[0]")
setp(R["middle-east"]["stepByStep"][1], "desc", "We submit via our authorized B2B portals.", "We submit your application through the official channel for your destination.", "regions/middle-east/stepByStep[1]")
setp(d["insurance"][1], "desc", "Trusted Embassy Approved", "Schengen-compliant policies", "insurance[1]")
setp(d["insurance"][2], "desc", "Best Value Packages", "Value packages", "insurance[2]")

for w, a, b in log:
    print("-", w); print("   BEFORE:", str(a)[:200]); print("   AFTER: ", str(b)[:200])
print("\nchanges:", len(log))
if "--dry" in sys.argv:
    print("DRY RUN - nothing written"); sys.exit()
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
print("written", P)
