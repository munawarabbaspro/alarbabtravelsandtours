"""v33 - Thailand and Italy: more official facts and FAQs (read on the official sites on 11 Nov 2026).

Why: Search Console (Sep-Nov 2026) shows Thailand at position 28 and Italy at position 27. Competing pages
answer more questions but mix up fees and rules and link no official source. These pages stay strictly sourced.

Sources read:
  - Royal Thai Embassy Islamabad, home page (visa section phone, hours, Diplomatic Shuttle):
    https://islamabad.thaiembassy.org/en/index
    (the embassy's fee table and tourist-visa checklist are an image and a PDF: not read, so no fees or amounts are added)
  - Embassy of Italy Islamabad, "Where to apply for a visa" (updated 16 Jun 2026): https://ambislamabad.esteri.it/en/?p=2974
  - Embassy of Italy Islamabad, notice of 29 May 2026 (study visas, appointment fraud warning): https://ambislamabad.esteri.it/en/?p=3034

  py tools/patch_v33.py --dry | py tools/patch_v33.py   (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "src", "data", "site-data.json")
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

TH_EMB = ("Royal Thai Embassy, Islamabad", "https://islamabad.thaiembassy.org/en/index")
IT_WHERE = ("Embassy of Italy, Islamabad: Where to apply for a visa (updated 16 June 2026)", "https://ambislamabad.esteri.it/en/?p=2974")
IT_FRAUD = ("Embassy of Italy, Islamabad: notice of 29 May 2026", "https://ambislamabad.esteri.it/en/?p=3034")

# ---------------------------------------------------------------- Thailand
th = C["thailand"]
facts = list(th.get("facts") or [])
for t, src in [
    ("The Royal Thai Embassy in Islamabad lists its visa section on (+92-51) 8431270-80, extensions 1122 and 1166. Visa section hours: Monday to Friday, 9:00-13:00 and 14:00-17:00.", TH_EMB),
    ("To visit the visa section you must take the Diplomatic Shuttle; the embassy lists a fee of 2,000 rupees for it and asks visitors to bring identification, preferably the passport.", TH_EMB),
]:
    if t not in [x[0] for x in facts]:
        facts.append([t, src[0], src[1]])
setv(th, "facts", facts, "thailand.facts")
setv(th, "faq_extra", [
    ["Can I apply for the Thailand visa online from Pakistan?",
     "Yes. Thai visas are applied for on the official Thai e-Visa website: you create an account, fill in the form, upload your documents and pay the fee, and the e-Visa confirmation comes by email. We prepare your documents and fill the form with you."],
    ["Do I have to visit the Thai Embassy in Islamabad?",
     "Usually not. The official e-Visa website says passports and supporting documents no longer have to be submitted in person. The embassy can still ask for an interview or more documents. Its visa section is in the Diplomatic Enclave and is reached by the Diplomatic Shuttle."],
    ["Is there a Thailand visa on arrival for Pakistani passport holders?",
     "Plan to get your visa before you travel. We apply for Pakistani passport holders through the official e-Visa website, and you show the printed approval to the airline and to Thai immigration. Rules can change, so confirm with us before you book flights."],
    ["Can I apply for the Thai e-Visa while I am in Thailand?",
     "No. The official e-Visa website says you can apply only while you are not in Thailand."],
], "thailand.faq_extra")

# ---------------------------------------------------------------- Italy
it = C["italy"]
setv(it, "facts", [
    ["Visa applications are submitted at BLS-Intiana centres, and only at the centre for the consular area where you permanently live.", IT_WHERE[0], IT_WHERE[1]],
    ["The Embassy of Italy in Islamabad covers the BLS-Intiana centres in Islamabad, Lahore, Multan and Faisalabad. The centres in Karachi and Quetta come under the Consulate General of Italy in Karachi.", IT_WHERE[0], IT_WHERE[1]],
    ["Appointments are booked on the Intiana Italy Visa Application Centre website linked from the embassy page.", IT_WHERE[0], IT_WHERE[1]],
    ["The embassy states that it and BLS-Intiana have no official WhatsApp or mobile number for contacting applicants, and warns against anyone asking for money to book an appointment (notice written for 2026/27 study-visa applicants).", IT_FRAUD[0], IT_FRAUD[1]],
], "italy.facts")
setv(it, "faq_extra", [
    ["Where do I submit an Italy visa application in Pakistan?",
     "At a BLS-Intiana centre, and only at the centre for the area where you permanently live. The Embassy of Italy in Islamabad covers Islamabad, Lahore, Multan and Faisalabad; Karachi and Quetta come under the Consulate General in Karachi."],
    ["Can someone sell me an Italy visa appointment?",
     "Be careful. The Embassy of Italy says it and BLS-Intiana have no official WhatsApp or mobile number for applicants, and it warns against anyone asking for money to book an appointment. We prepare your file and help you book through the official system; we do not sell appointment slots."],
], "italy.faq_extra")

if "--dry" in sys.argv:
    for w, old, new in log:
        print(w, "->", json.dumps(new, ensure_ascii=False)[:160])
    print(len(log), "changes")
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(len(log), "changes written")
