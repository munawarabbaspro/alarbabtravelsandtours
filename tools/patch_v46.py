"""v46 - Nepal and Bangladesh facts/FAQs from official bodies (read 24 Nov 2026).

Sources read:
  - Nepal Tourism Board, Tourist visa: https://ntb.gov.np/en/plan-your-trip/before-you-come/tourist-visa
    (the Department of Immigration site, immigration.gov.np, could not be read: TLS certificate error)
  - High Commission of Bangladesh, Islamabad (Ministry of Foreign Affairs): http://islamabad.mofa.gov.bd/
    (dip.gov.bd and visa.gov.bd could not be read)
No fees or amounts are added.

  py tools/patch_v46.py --dry | py tools/patch_v46.py   (idempotent)
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
        log.append((slug + ".facts", len(new) - len(cur)))
        c["facts"] = new


def add_faqs(slug, items):
    c = C[slug]
    cur = [list(x) for x in (c.get("faq_extra") or [])]
    have = {q for q, _ in cur}
    new = cur + [[q, a] for q, a in items if q not in have]
    if new != cur:
        log.append((slug + ".faq", len(new) - len(cur)))
        c["faq_extra"] = new


NP = ("Nepal Tourism Board: Tourist visa", "https://ntb.gov.np/en/plan-your-trip/before-you-come/tourist-visa")
add_facts("nepal", [
    ("The Nepal Tourism Board lists the nationalities for which no visa on arrival is provided, who must get a visa from a Nepali mission before travel. Pakistan is not on that list.", NP),
    ("A tourist visa can be issued on arrival at Tribhuvan International Airport, Pokhara International Airport and Gautam Buddha International Airport in Lumbini, or before travel from Nepal's diplomatic missions abroad.", NP),
    ("You may fill the online visa application form on the Department of Immigration portal before you arrive in Nepal. A visa issued abroad must be used to enter Nepal within six months of the issue date.", NP),
    ("Tourist visas are listed as multiple entry for 15, 30 or 90 days. Extensions are handled by the Department of Immigration in Kathmandu or Pokhara.", NP),
    ("You need a valid passport and a passport-size photo with a light background. The Nepal Tourism Board also lists a free visa for up to 30 days for SAARC citizens (except Afghanistan) visiting for the first time in a visa year.", NP),
])
add_faqs("nepal", [
    ("Do Pakistanis need a visa for Nepal?",
     "Yes, a tourist visa is needed. The Nepal Tourism Board says all foreigners except Indians need one, and Pakistan is not on its list of nationalities for which no on-arrival visa is provided. We check the current Immigration Department rule for your passport before you travel."),
    ("Where can I get a Nepal tourist visa?",
     "The Nepal Tourism Board lists three ways: on arrival at Tribhuvan, Pokhara or Gautam Buddha (Lumbini) airport, before travel from a Nepali mission, or by filling the online form before you arrive. We help you fill the form and prepare your documents."),
    ("How long can I stay in Nepal on a tourist visa?",
     "Tourist visas are listed for 15, 30 or 90 days, multiple entry. You can ask the Department of Immigration in Kathmandu or Pokhara for an extension."),
])

BD = ("High Commission of Bangladesh, Islamabad", "http://islamabad.mofa.gov.bd/")
add_facts("bangladesh", [
    ("The High Commission of Bangladesh in Islamabad lists Tourist Visa and Business Visa among its visa categories, with a downloadable visa application form on its website.", BD),
    ("The High Commission's website offers e-Consular visa services, including booking an appointment and checking the status of an application.", BD),
])
add_faqs("bangladesh", [
    ("Where do Pakistanis apply for a Bangladesh visa?",
     "At the High Commission of Bangladesh in Islamabad. Its website lists the visa categories, a visa application form and an e-Consular service for booking an appointment and checking your application status. We prepare your documents and guide you through the submission."),
    ("What types of Bangladesh visa can I apply for?",
     "The High Commission lists categories such as Tourist Visa, Business Visa and Student Visa. We help you choose the one that matches your purpose of travel and check the requirements for it."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
