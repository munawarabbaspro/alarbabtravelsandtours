"""v29 - add country guides for the Philippines and Tajikistan to data/site-data.json.
Every fact comes from official government pages read in October 2026 (sources are stored with each fact and shown on the page):
  Philippines: consular.dfa.gov.ph (visa general info, visa FAQs), evisa.gov.ph (eVisaPH country check, policy page)
  Tajikistan : www.evisa.tj (Ministry of Foreign Affairs e-Visa portal: Get informed, FAQ, application form)
No fees, processing times, approval chances or other numbers are included, except the six-month passport rule both governments state.

  py tools/patch_v29.py --dry | py tools/patch_v29.py   (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "site-data.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)

DFA_INFO = ("Philippine DFA: visa general information", "https://consular.dfa.gov.ph/visa-general-info/")
DFA_FAQ = ("Philippine DFA: visa FAQs", "https://consular.dfa.gov.ph/visa-faqs/")
EVISA_PH = ("eVisaPH: check if you need a visa", "https://evisa.gov.ph/")
EVISA_PH_POLICY = ("eVisaPH: Philippine visa policy", "https://evisa.gov.ph/page/policy")
TJ_INFO = ("Tajikistan e-Visa: Get informed", "https://www.evisa.tj/#/getinformed")
TJ_FAQ = ("Tajikistan e-Visa: FAQ", "https://www.evisa.tj/#/help")
TJ_APPLY = ("Tajikistan e-Visa: application form", "https://www.evisa.tj/#/apply")

def f(text, src):
    return [text, src[0], src[1]]

PH = {
    "slug": "philippines", "name": "Philippines", "code": "ph", "image": "https://images.unsplash.com/photo-1531761535209-180857e963b9?auto=format&fit=crop&q=80&w=800",
    "title": "Philippines Visa Consultant in Islamabad",
    "description": "Pakistani passport holders need a visa for the Philippines. The Philippine Department of Foreign Affairs says to apply at the Philippine Embassy in Islamabad, in person.",
    "keywords": "Philippines visa from Pakistan, Philippines visit visa Islamabad, Philippine Embassy Islamabad visa, Philippines tourist visa Pakistan",
    "intro": ("The Philippine government lists Pakistan as a visa-required country, so Pakistani passport holders need a visa before they travel. The application is made at the Philippine Embassy in Islamabad. "
              "The checklist on this page is the minimum requirement published by the Department of Foreign Affairs; the visa officer may ask for more documents depending on your purpose of visit. "
              "AL ARBAB TRAVEL AND TOURS prepares your file and follows it up from Blue Area, Islamabad. Always check the official sites linked below, because rules change."),
    "docs": [
        "Passport or travel document valid for at least six (6) months beyond the intended period of stay in the Philippines",
        "Electronic or machine-readable passport (non-machine-readable and hand-scripted passports are not accepted)",
        "Duly accomplished visa application form",
        "Two (2) passport-sized photos",
        "Proof of bona fide status as a tourist or businessman (for example a company letter or a bank statement)",
        "Confirmed ticket for the return or onward journey to the next port of destination",
        "Any other documents the visa officer requests, depending on your purpose of visit or visa subtype",
    ],
    "popularPlaces": [],
    "official_only": True,
    "lead": "Pakistani passport holders need a visa for the Philippines. According to the Philippine Department of Foreign Affairs, you apply at the Philippine Embassy in Islamabad, and the application is made in person.",
    "tier_note": "The Philippine DFA states that a temporary visitor's visa application is made in person, so you attend the Philippine Embassy yourself. We prepare your file and follow it up with you.",
    "facts": [
        f("Pakistan is on the list of countries whose passport holders need a visa for the Philippines. It is not on the visa-free list.", DFA_INFO),
        f("For Pakistan, the official eVisaPH check says: visa required, and the traveller may apply at the Philippine Embassy in Islamabad, Pakistan, or at the embassy of their place of legal residence.", EVISA_PH),
        f("A temporary visitor's visa application must be made in person, normally at the embassy or consulate that covers your place of residence.", DFA_INFO),
        f("Embassy address listed by eVisaPH: Plot Nos. 3, 4 and 5, Khayaban-e-Suhrwardy, Diplomatic Enclave, Sector G-5, Islamabad, Pakistan.", EVISA_PH),
        f("Core requirements: passport valid at least six months beyond the stay, application form, two passport photos, proof of bona fide status as tourist or businessman, confirmed return or onward ticket, and payment of the visa fee. Other documents may be requested.", DFA_FAQ),
        f("Embassies accept only electronic and machine-readable passports. Non-machine-readable or hand-scripted passports are not accepted.", EVISA_PH_POLICY),
        f("Online e-Visa applications are open to eligible foreign nationals only. Others are told to lodge the application at the nearest Philippine Embassy or Consulate.", DFA_FAQ),
        f("A visa does not ensure entry: admission is decided by the immigration authorities at the port of entry.", DFA_INFO),
    ],
    "faq_extra": [
        ["Is a visa required for Pakistani passport holders to visit the Philippines?", "Yes. The Philippine Department of Foreign Affairs lists Pakistan as visa required, and the eVisaPH check says the same. Always confirm on the official sites linked on this page before you travel."],
        ["Where do I apply for a Philippines visa from Pakistan?", "The official eVisaPH check says Pakistani travellers may apply at the Philippine Embassy in Islamabad, or at the embassy where they legally reside. The DFA says a temporary visitor's visa application is made in person."],
    ],
}

TJ = {
    "slug": "tajikistan", "name": "Tajikistan", "code": "tj", "image": "https://images.unsplash.com/photo-1726547507141-524321eb781f?auto=format&fit=crop&q=80&w=800",
    "title": "Tajikistan Visa Consultant in Islamabad",
    "description": "Tajikistan issues e-Visas for short visits through its official portal, evisa.tj. Pakistan appears in the portal's list of nationalities.",
    "keywords": "Tajikistan visa from Pakistan, Tajikistan e-visa Pakistan, evisa.tj Pakistan, Tajikistan tourist visa Islamabad",
    "intro": ("Tajikistan issues e-Visas for short-stay visits through its official government portal, evisa.tj, run by the Main Consulate Department of the Ministry of Foreign Affairs. "
              "Pakistan is on the portal's list of countries of citizenship. The checklist on this page comes from the portal's own information pages and application form. "
              "AL ARBAB TRAVEL AND TOURS processes and follows up your visit visa file from Blue Area, Islamabad. Always check the official portal, because rules change."),
    "docs": [
        "Passport or travel document valid for at least six (6) months after the validity of the requested e-Visa",
        "Online e-Visa application on evisa.tj, filled in exactly as the passport shows",
        "Personal and passport details as the form asks: name, date and place of birth, phone number, address, passport number, date of issue and date of expiry",
        "An email address, because the e-Visa download link is sent by email after approval",
        "A credit or debit card to pay the consular fee online (Visa, Mastercard and American Express are accepted)",
        "Any extra requirement for your nationality, which the portal shows after you choose your nationality and travel dates",
        "A separate permit for GBAO (Gorno-Badakhshan region) in addition to the e-Visa, if you plan to visit that region",
    ],
    "popularPlaces": [],
    "official_only": True,
    "lead": "Tajikistan issues e-Visas for short visits through its official portal, evisa.tj, and Pakistan appears in the portal's list of nationalities.",
    "facts": [
        f("The official e-Visa portal, evisa.tj, is run by the Main Consulate Department of the Ministry of Foreign Affairs of Tajikistan, for short-term visitors.", TJ_INFO),
        f("Pakistan is in the portal's list of countries of citizenship on the application form. The portal says extra requirements may apply depending on nationality and shows them after you choose your nationality and travel dates.", TJ_APPLY),
        f("You can apply for the e-Visa only while you are outside Tajikistan.", TJ_INFO),
        f("Your passport must be valid for at least six months after the validity of the requested e-Visa.", TJ_INFO),
        f("The details you enter must match your travel document exactly. If they do not, the e-Visa is invalid.", TJ_INFO),
        f("The consular fee is paid online by credit or debit card. If an e-Visa application is denied, the fee is not refunded.", TJ_FAQ),
        f("After approval the e-Visa is sent to you by email. The portal advises keeping a copy on your phone or on paper.", TJ_INFO),
        f("Visiting the Gorno-Badakhshan region (GBAO) needs a special permit in addition to the e-Visa.", TJ_FAQ),
        f("The portal's FAQ says an e-Visa is granted for tourism and business, for short stays only.", TJ_FAQ),
    ],
    "faq_extra": [
        ["Can Pakistani citizens apply for a Tajikistan e-Visa?", "Pakistan appears in the list of nationalities on the official portal, evisa.tj. Apply only through that portal and check it for any extra requirement for your nationality and travel dates."],
        ["Do I need a separate permit to visit the Pamir (GBAO) region?", "Yes. The official e-Visa FAQ says Gorno-Badakhshan (GBAO) needs a special permit in addition to the e-Visa."],
    ],
}

changes = []
for region, rec in (("south-asia", PH), ("central-asia", TJ)):
    lst = d["countries"][region]
    lst[:] = [c for c in lst if c["slug"] != rec["slug"]]
    lst.append(rec); changes.append(f"added/updated {rec['name']} in {region}")
print("\n".join(changes) or "nothing to do (already present)")
if "--dry" in sys.argv:
    print("DRY RUN"); sys.exit()
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
print("written")
