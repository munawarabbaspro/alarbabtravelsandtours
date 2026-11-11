"""v45 - Australia region page: FAQs from Home Affairs replace unsourced ones (read 11 Nov 2026).

Source read: Department of Home Affairs, Visitor visa (subclass 600) Tourist stream (apply outside Australia),
last updated 5 Nov 2026: https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/tourist-stream-overseas
Removed (no official source found): "valid typically up to 3 years", "medical only if over 75", and the fee FAQ.
No fees or amounts are added.

  py tools/patch_v45.py --dry | py tools/patch_v45.py   (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "src", "data", "site-data.json")
d = json.loads(open(P, encoding="utf-8").read())
log = []
R = {r["slug"]: r for r in d["regions"]}
au = R["australia"]

DROP = {"How long is an Australian visitor visa valid for?", "Is a medical checkup required?", "What is the subclass 600 visa fee?"}
NEW = [
    {"q": "How long can I stay in Australia on a visitor visa?",
     "a": "The Home Affairs page for the Visitor visa (subclass 600) Tourist stream lists a stay of up to 12 months. The period you get is set on your visa grant."},
    {"q": "Can I apply for an Australia tourist visa from Pakistan?",
     "a": "Yes. The Tourist stream (apply outside Australia) is for visiting as a tourist, for a cruise or to see family and friends. Home Affairs says you must be outside Australia when you apply and when the visa is decided."},
    {"q": "What does Australia check for a visitor visa?",
     "a": "Home Affairs says you must intend to visit only, have enough money for your stay, and not work in Australia. We prepare the file to show these clearly."},
    {"q": "How long does an Australia visitor visa take?",
     "a": "Home Affairs publishes a visa processing time guide based on recently decided applications. It is a guide only and not specific to your application."},
]
faqs = [f for f in au["faqs"] if f["q"] not in DROP]
have = {f["q"] for f in faqs}
faqs = [f for f in NEW if f["q"] not in have] + faqs
if faqs != au["faqs"]:
    log.append(("australia.faqs", len(au["faqs"]), len(faqs))); au["faqs"] = faqs
for v in au["visas"]:
    if v["slug"] == "visitor-visa":
        t = "Varies. Home Affairs publishes a processing time guide on its website."
        if v["processingTime"] != t:
            log.append(("australia.visitor-visa.processingTime", v["processingTime"], t)); v["processingTime"] = t

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
