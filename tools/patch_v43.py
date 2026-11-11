"""v43 - Egypt, Kenya, Maldives: official facts + FAQs (read 11 Nov 2026).

Sources read:
  - Egypt e-Visa Portal (Ministry of Interior), FAQ "Who requires a visa?": https://visa2egypt.gov.eg/eVisa/FAQ
    (the list of e-Visa nationalities does not include Pakistan)
  - Kenya eTA, General information: https://www.etakenya.go.ke/general-information
  - Maldives Immigration, Tourist visa: https://immigration.gov.mv/visa/tourist-visa/
No fees or amounts are added.

  py tools/patch_v43.py --dry | py tools/patch_v43.py   (idempotent)
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

EG = ("Egypt e-Visa Portal (Ministry of Interior): FAQ, who requires a visa", "https://visa2egypt.gov.eg/eVisa/FAQ")
add_facts("egypt", [
    ("The Egypt e-Visa Portal lists the nationalities that may be issued an e-Visa on application. Pakistan is not on that list.", EG),
    ("For listed nationalities, the e-Visa is applied for online, and a link to download it is sent by email. Passport authorities at the port of arrival check the e-Visa on their system.", EG),
])
add_faqs("egypt", [
    ("Can Pakistanis get an Egypt e-Visa online?",
     "Not on a Pakistani passport alone: Pakistan is not on the Egypt e-Visa Portal's list of nationalities that can be issued an e-Visa. Pakistani passport holders apply through the Egyptian embassy. We prepare the file and guide you through the submission."),
])

KE = ("Kenya eTA: General information", "https://www.etakenya.go.ke/general-information")
add_facts("kenya", [
    ("Pakistan is not on the Kenya eTA exemption lists, so Pakistani travellers apply for an Electronic Travel Authorisation (eTA) online before travel.", KE),
    ("The official site recommends applying at least 2 weeks before travel. Processing is typically three working days, but it may take longer in some cases.", KE),
])
add_faqs("kenya", [
    ("Do Pakistanis need an eTA for Kenya?",
     "Yes. Pakistan is not on Kenya's eTA exemption lists, so you apply for the eTA online on the official site before you travel."),
    ("How long does the Kenya eTA take?",
     "The official site says processing is typically three working days and recommends applying at least 2 weeks before travel."),
])

MV = ("Maldives Immigration: Tourist visa", "https://immigration.gov.mv/visa/tourist-visa/")
add_facts("maldives", [
    ("A tourist visa is granted on arrival in the Maldives; tourists do not need pre-approval.", MV),
    ("You need a machine-readable passport with at least 1 month's validity, a complete itinerary with a confirmed return ticket, a prepaid confirmed booking at a registered facility and enough funds for the stay. A complete itinerary does not guarantee entry.", MV),
    ("Every foreigner, including children, must submit an individual Traveller Declaration on the IMUGA portal within 96 hours before arrival.", MV),
])
add_faqs("maldives", [
    ("What do I need for a Maldives visa on arrival?",
     "Maldives Immigration asks for a machine-readable passport valid at least 1 month, a confirmed return ticket, a prepaid confirmed booking at a registered hotel or resort, and enough funds for your stay."),
    ("When do I fill the Maldives IMUGA Traveller Declaration?",
     "Within 96 hours before arrival. Each traveller, including children, submits an individual declaration on the IMUGA portal. We can fill it with you."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
