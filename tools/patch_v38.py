"""v38 - Qatar official facts + FAQs; Saudi intro wording (read 11 Nov 2026).

Source: Visit Qatar (Qatar Tourism), Visas page and its "What visa do I need" check, answered for
nationality Pakistan / not a GCC, Schengen, UK, US, Australia, NZ or Canada resident / no valid visa from those:
https://www.visitqatar.com/intl-en/practical-info/visas
No fees or amounts are added.

  py tools/patch_v38.py --dry | py tools/patch_v38.py   (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "src", "data", "site-data.json")
d = json.loads(open(P, encoding="utf-8").read())
log = []
C = {}
for lst in d["countries"].values():
    for c in lst:
        C.setdefault(c["slug"], c)

def add_facts(slug, items):
    c = C[slug]
    cur = [list(x) for x in (c.get("facts") or [])]
    have = {x[0] for x in cur}
    new = cur + [[t, s[0], s[1]] for t, s in items if t not in have]
    if new != cur:
        log.append((slug + ".facts", len(new) - len(cur))); c["facts"] = new

def add_faqs(slug, items):
    c = C[slug]
    cur = [list(x) for x in (c.get("faq_extra") or [])]
    have = {q for q, _ in cur}
    new = cur + [[q, a] for q, a in items if q not in have]
    if new != cur:
        log.append((slug + ".faq", len(new) - len(cur))); c["faq_extra"] = new

QA = ("Visit Qatar (Qatar Tourism): Visas and visa check", "https://www.visitqatar.com/intl-en/practical-info/visas")
add_facts("qatar", [
    ("For a Pakistani passport holder who is not a GCC resident and has no valid Schengen, UK, US, Australia, New Zealand or Canada visa, the official visa check says: book Discover Qatar accommodation before you travel to get your Entry Visa on arrival, or apply in advance for a Hayya A1 Entry Visa.", QA),
    ("The Ministry of Interior requires nationals of the listed countries to hold a hotel booking made through the Discover Qatar website before travelling, to get a visa on arrival.", QA),
    ("Visas are applied for on the Hayya platform (website or the 'Hayya to Qatar' app), which handles the Tourist Visa (A1), GCC Resident Visa (A2) and other categories.", QA),
    ("For visa on arrival, the passport must be valid for at least three months from the date of arrival in Qatar.", QA),
    ("Qatar Tourism recommends that all visitors hold health insurance covering Qatar's medical facilities; it can also be bought on arrival.", QA),
])
add_faqs("qatar", [
    ("Can Pakistanis get a Qatar visa on arrival?",
     "Yes, with a condition. Qatar's official visa check says a Pakistani passport holder must book accommodation through the Discover Qatar website before travelling to get the Entry Visa on arrival. The alternative is to apply in advance for a Hayya A1 Entry Visa."),
    ("What is the Hayya A1 visa for Qatar?",
     "The Hayya A1 is Qatar's Tourist Visa, applied for online on the Hayya platform or the 'Hayya to Qatar' app. We fill the application with you and arrange the hotel booking it needs."),
    ("Do I need a Discover Qatar hotel booking?",
     "For a visa on arrival, yes. Qatar's Ministry of Interior requires nationals of the listed countries, including Pakistan, to book their hotel through Discover Qatar before travel. We can make this booking for you."),
    ("How long must my passport be valid for Qatar?",
     "At least three months from the date you arrive in Qatar, for a visa on arrival."),
])

# Saudi intro: the tourist eVisa line suggested Pakistanis can use it; Pakistan is not on the 72-country list (patch_v37)
sa = C["saudi-arabia"]
new_intro = ("We prepare Umrah, family visit and tourist visa files for Pakistani passport holders and arrange hotel bookings. "
             "The right visa depends on your purpose, so tell us why you are travelling and we confirm the route.")
if sa.get("intro") != new_intro:
    log.append(("saudi-arabia.intro", 1)); sa["intro"] = new_intro

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
