"""v39 - Greece and Switzerland: official facts + FAQs; Greece intro (read 11 Nov 2026).

Sources read:
  - Embassy of Greece in Islamabad, General Schengen visa requirements:
    https://www.mfa.gr/missionsabroad/en/pakistan-en/visas/general-schengen-visa-requirements.html
  - Embassy of Switzerland in Pakistan, Where to apply for a Schengen visa? (published 27 Apr 2026):
    https://www.schweiz-pakistan.eda.admin.ch/en/where-to-apply-for-a-schengen-visa
No fees or amounts are added (the 30,000 euro insurance minimum is a cover requirement, not a fee).

  py tools/patch_v39.py --dry | py tools/patch_v39.py   (idempotent)
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

GR = ("Embassy of Greece in Islamabad: General Schengen visa requirements", "https://www.mfa.gr/missionsabroad/en/pakistan-en/visas/general-schengen-visa-requirements.html")
add_facts("greece", [
    ("To apply for a Schengen visa at the Greek Consular Office in Islamabad you book an appointment on the embassy's scheduling site, print the confirmation and bring it on the day.", GR),
    ("The passport must have at least two blank pages, have been issued within the previous ten years, and be valid at least three months after you leave the Schengen area.", GR),
    ("Fingerprints are collected unless they were registered in the VIS within the previous 59 months.", GR),
    ("Travel medical insurance must cover emergency medical care, hospitalisation and repatriation, with a minimum cover of 30,000 euros, for the whole stay.", GR),
    ("You cannot choose which Schengen country's mission to apply at: apply at the mission of the country of your longest stay, or of your first point of entry if that is hard to determine.", GR),
    ("The embassy lists, among other documents, the NADRA Family Registration Certificate, previous visas and passports, proof of employment or business, and bank statements. A personal interview may be requested.", GR),
])
add_faqs("greece", [
    ("Where do I apply for a Greece visa in Pakistan?",
     "At the Greek Consular Office in Islamabad, by appointment. The embassy says you book the appointment on its scheduling site, print the confirmation and bring it with you. We prepare the file before your appointment."),
    ("Can I apply for a Greece visa if I will spend more days in Italy?",
     "No. The Embassy of Greece says you must apply at the mission of the country where your longest stay will be, or your first point of entry if that is hard to determine. We check your itinerary and tell you which embassy is correct."),
    ("Is an old passport accepted for a Greece visa?",
     "Only if it was issued within the previous ten years, has two blank pages and is valid at least three months after you leave the Schengen area. The embassy also asks for your previous passports."),
])

CH = ("Embassy of Switzerland in Pakistan: Where to apply for a Schengen visa? (27 Apr 2026)", "https://www.schweiz-pakistan.eda.admin.ch/en/where-to-apply-for-a-schengen-visa")
add_facts("switzerland", [
    ("Residents of Pakistan and Afghanistan submit their Swiss Schengen visa application to Gerry's / VFS, at the Switzerland Visa Application Centres in Islamabad, Karachi and Lahore.", CH),
    ("The Islamabad centre is on Park Road, Chatta Bakhtawar, Chak Shahzad. Appointments are booked on the Gerry's / VFS website or by phone on +92 51 848 58 36.", CH),
    ("The embassy says the visa centre charges for its services; ask the agency for the amount.", CH),
])
add_faqs("switzerland", [
    ("Where do I apply for a Switzerland visa in Pakistan?",
     "At the Switzerland Visa Application Centre run by Gerry's / VFS in Islamabad (Chak Shahzad), Karachi or Lahore, according to the Embassy of Switzerland. We prepare your file; you attend the centre yourself."),
    ("How do I book a Switzerland visa appointment?",
     "On the Gerry's / VFS website, or by phone on +92 51 848 58 36, as listed by the Embassy of Switzerland in Pakistan."),
])

gr = C["greece"]
new_intro = gr["intro"].replace("for submission at GVCW centers", "for your appointment at the Greek Consular Office in Islamabad")
if new_intro != gr["intro"]:
    log.append(("greece.intro", 1)); gr["intro"] = new_intro

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
