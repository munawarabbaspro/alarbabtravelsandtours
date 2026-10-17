"""v31 - official facts blocks for Sri Lanka, Vietnam and Singapore (read on the official sites on 7 Oct 2026),
and their "Fast …" descriptions made neutral. Malaysia is skipped: the official eVISA portal shows nothing without a login.

  py tools/patch_v31.py --dry | py tools/patch_v31.py   (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "site-data.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
log = []

def setv(obj, key, new, where):
    if obj.get(key) != new:
        log.append((where, obj.get(key), new)); obj[key] = new

C = {}
for lst in d["countries"].values():
    for c in lst:
        C.setdefault(c["slug"], c)

LK = ("Sri Lanka ETA official website (Department of Immigration & Emigration)", "https://www.eta.gov.lk/slvisa/")
VN = ("Viet Nam e-Visa official website (Immigration Department)", "https://evisa.gov.vn/")
VN_PRE = ("Viet Nam pre-arrival form (Immigration Department)", "https://prearrival.immigration.gov.vn/")
SG = ("ICA: Check if you need an entry visa", "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements")

lk = C["sri-lanka"]
setv(lk, "description", "Sri Lanka ETA for Pakistani tourists, applied for on the official portal. Minimum documentation.", "sri-lanka.description")
setv(lk, "facts", [
    ["From 25 May 2026, Pakistan is one of 40 countries whose nationals can get a tourist visa (ETA) free of charge for 30 days.", *LK],
    ["Every foreign national, including those 40 countries, must get an Electronic Travel Authorization (ETA) before arriving in Sri Lanka.", *LK],
    ["The free tourist visa is valid for 30 days, with double entry allowed within that 30-day validity from the date of first arrival.", *LK],
    ["To stay longer than 30 days, you apply for a visa extension and pay the visa fee that applies.", *LK],
], "sri-lanka.facts")

vn = C["vietnam"]
setv(vn, "description", "Vietnam e-visa for Pakistani citizens, applied for on the official Viet Nam e-Visa website.", "vietnam.description")
setv(vn, "facts", [
    ["Foreigners outside Viet Nam apply for the e-Visa on the official website: fill in the application form, pay online and receive the e-Visa online.", *VN],
    ["The e-Visa is valid for a maximum of 90 days, for single or multiple entry.", *VN],
    ["The fee is paid through the portal's payment gateway and is not refunded if the visa is not granted.", *VN],
    ["e-Visa holders must enter and leave Viet Nam through the international border gates the government designates.", *VN],
    ["The Immigration Department recommends completing the pre-arrival form before you travel.", *VN_PRE],
], "vietnam.facts")

sg = C["singapore"]
setv(sg, "description", "Singapore visa for Pakistani passport holders, prepared in Islamabad and submitted through the official channel.", "singapore.description")
setv(sg, "intro", "Singapore is a world-class hub of shopping, food and iconic attractions like Marina Bay Sands and Sentosa. Pakistani passport holders need a Singapore entry visa before they travel. We prepare your documents and the application.", "singapore.intro")
setv(sg, "facts", [
    ["Pakistan is on ICA's list of travel documents that need a valid Singapore entry visa.", *SG],
    ["Without a local contact who has a Singpass or Corppass account, you apply through an authorised visa agent appointed by the Singapore Overseas Missions, or at the nearest Singapore Overseas Mission.", *SG],
    ["ICA does not accept visa applications at the immigration counters.", *SG],
    ["A visa is permission to travel and seek entry. ICA officers at the checkpoint decide on entry and the length of stay, which is not tied to the visa's validity.", *SG],
    ["Visitors are told their Visit Pass (e-Pass) by email, with no stamp in the passport, so give a valid email address in the SG Arrival Card.", *SG],
], "singapore.facts")

for w, a, b in log:
    print("-", w); print("   BEFORE:", str(a)[:160]); print("   AFTER: ", str(b)[:160])
print("\nchanges:", len(log))
if "--dry" in sys.argv:
    print("DRY RUN - nothing written"); sys.exit()
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
print("written", P)
