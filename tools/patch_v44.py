"""v44 - UK and Canada region pages: FAQs from GOV.UK and IRCC; unsourced processing times replaced (read 11 Nov 2026).

Sources read:
  - GOV.UK, Visit the UK as a Standard Visitor: https://www.gov.uk/standard-visitor
  - GOV.UK, Standard Visitor: apply: https://www.gov.uk/standard-visitor/apply-standard-visitor-visa
  - IRCC, Apply for a visitor visa: https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada/apply-visitor-visa.html
No fees or amounts are added.

  py tools/patch_v44.py --dry | py tools/patch_v44.py   (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "src", "data", "site-data.json")
d = json.loads(open(P, encoding="utf-8").read())
log = []
R = {r["slug"]: r for r in d["regions"]}

def add_rfaqs(slug, items):
    r = R[slug]
    have = {f["q"] for f in r["faqs"]}
    add = [{"q": q, "a": a} for q, a in items if q not in have]
    if add:
        r["faqs"] = add + r["faqs"]
        log.append((slug + ".faqs", len(add)))

def set_proc(slug, vslug, text):
    for v in R[slug]["visas"]:
        if v["slug"] == vslug and v["processingTime"] != text:
            log.append((f"{slug}.{vslug}.processingTime", v["processingTime"], text)); v["processingTime"] = text

add_rfaqs("united-kingdom", [
    ("How long can I stay in the UK on a Standard Visitor visa?",
     "GOV.UK says you can usually stay for up to 6 months. You cannot live in the UK through frequent or successive visits, or claim public funds."),
    ("When can I apply for a UK visit visa?",
     "Online, before you travel. GOV.UK says the earliest you can apply is 3 months before your travel date."),
    ("How long does a UK visit visa take from Pakistan?",
     "GOV.UK says you will usually get a decision within 3 weeks of proving your identity at the visa application centre. You can check on GOV.UK whether a faster decision is available for you."),
    ("What happens at the UK visa application centre?",
     "You show your passport, and your fingerprints and photo are taken. GOV.UK says your passport is returned the same day, though the centre may keep some other documents while your application is processed."),
    ("I visit the UK often. Is there a longer visa?",
     "Yes. GOV.UK says regular visitors can apply for a long-term Standard Visitor visa instead of the 6-month visa. We check whether your travel history supports it."),
])
set_proc("united-kingdom", "standard-visitor-visa", "Usually within 3 weeks after your visa centre appointment (GOV.UK).")

add_rfaqs("canada", [
    ("How do I apply for a Canada visitor visa from Pakistan?",
     "Online, through the IRCC portal. You get a personalised document checklist in the portal. After you apply, wait for your biometrics instruction letter before booking the biometrics appointment."),
    ("How long must my passport be valid for a Canada visa?",
     "IRCC says it should be valid for at least 6 months from your planned travel date. A visa can be valid for up to 10 years, but not beyond your passport or biometrics expiry."),
    ("What bank statement does Canada need?",
     "IRCC says bank statements show whether you have enough money to support yourself during your stay, and asks for at least 6 months of account details."),
    ("What should my employer letter for a Canada visa say?",
     "IRCC says an employer letter can show you have a stable job and will return to it. It should be on official letterhead and dated no earlier than 3 months before you apply."),
])
set_proc("canada", "visitor-visa", "Varies by case. IRCC publishes current processing times on canada.ca.")

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
