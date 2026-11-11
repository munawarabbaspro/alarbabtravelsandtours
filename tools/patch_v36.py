"""v36 - Official facts + FAQs for Malaysia, Oman, Kuwait, Spain, Netherlands (read 11 Nov 2026).

Why: top Search Console pages with no sourced facts (Malaysia 174 impressions, Spain 171, Oman 169, Kuwait 143).
Competitor pages on these queries list fees and rules without official sources; ours cite the government page.
No fees or amounts are added.

Sources read:
  - Immigration Department of Malaysia, Visa requirement by country / Types of visas:
    https://www.imi.gov.my/index.php/en/main-services/visa/visa-requirement-by-country/
    https://www.imi.gov.my/index.php/en/main-services/visa/types-of-visas/
  - Ministry of Foreign Affairs Malaysia (mission notice, MDAC): https://www.kln.gov.my/web/aus_canberra/post/malaysia-digital-arrival-card-mdac--1
  - Oman Ministry of Foreign Affairs, Entry visas: https://www.fm.gov.om/en/visitors/entry-visas/
  - Kuwait Ministry of Interior visa portal (visa instructions + FAQ): https://kuwaitvisa.moi.gov.kw/
  - Embassy of Spain in Islamabad, Schengen visas: https://www.exteriores.gob.es/Embajadas/islamabad/en/ServiciosConsulares/Paginas/Consular/Visados-Schengen.aspx
  - Netherlands Worldwide, Applying for a Schengen visa for the Netherlands in Pakistan (updated 19 Oct 2026):
    https://www.netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-pakistan

  py tools/patch_v36.py --dry | py tools/patch_v36.py   (idempotent)
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

# ---------------------------------------------------------------- Malaysia
MY_REQ = ("Immigration Department of Malaysia: Visa requirement by country", "https://www.imi.gov.my/index.php/en/main-services/visa/visa-requirement-by-country/")
MY_TYPES = ("Immigration Department of Malaysia: Types of visas", "https://www.imi.gov.my/index.php/en/main-services/visa/types-of-visas/")
MY_MDAC = ("Ministry of Foreign Affairs Malaysia: Malaysia Digital Arrival Card (MDAC)", "https://www.kln.gov.my/web/aus_canberra/post/malaysia-digital-arrival-card-mdac--1")
add_facts("malaysia", [
    ("Pakistan is on the Immigration Department of Malaysia's list of countries whose citizens must have a visa to enter Malaysia.", MY_REQ),
    ("For eVISA applications, the Immigration Department points to its official portal, malaysiavisa.imi.gov.my.", MY_REQ),
    ("A Single Entry Visa is issued mainly for a social visit. It is normally valid for one entry within three months from the date of issue.", MY_TYPES),
    ("Travellers who stay inside the airport and continue on the same flight do not need a transit visa.", MY_TYPES),
    ("Since 1 January 2024 all foreign citizens travelling to Malaysia must complete the Malaysia Digital Arrival Card (MDAC) three days before arrival, with a few exceptions (such as Singapore citizens and diplomatic passport holders). It is submitted at imigresen-online.imi.gov.my.", MY_MDAC),
])
add_faqs("malaysia", [
    ("Do Pakistanis need a visa for Malaysia?",
     "Yes. Pakistan is on the Immigration Department of Malaysia's list of countries whose citizens need a visa to enter Malaysia."),
    ("Where do I apply for the Malaysia eVISA?",
     "On the Immigration Department's official eVISA portal, malaysiavisa.imi.gov.my. We prepare your documents and fill the application with you."),
    ("How long is a Malaysia single entry visa valid?",
     "The Immigration Department says a Single Entry Visa, issued mainly for social visits, is normally valid for one entry within three months from the date of issue."),
    ("What is the MDAC for Malaysia?",
     "The Malaysia Digital Arrival Card. Foreign visitors, including Pakistanis, must complete it online at imigresen-online.imi.gov.my three days before arrival. It does not replace your visa."),
])

# ---------------------------------------------------------------- Oman
OM = ("Ministry of Foreign Affairs of Oman: Entry visas", "https://www.fm.gov.om/en/visitors/entry-visas/")
add_facts("oman", [
    ("Visas for visitors to Oman are managed by the Royal Oman Police (ROP), and applications are made online on the ROP eVisa website.", OM),
    ("For tourists, the Ministry says the Tourist Visit Visa (Unsponsored) will usually be appropriate.", OM),
    ("Pakistan is not on the Ministry's lists of nationalities exempt from an entry visa for stays of up to 14 days.", OM),
    ("The ROP eVisa call centre: 80080011 (toll free inside Oman), +968 22848200 from outside Oman, email Info-OmaneVisa@rop.gov.om.", OM),
])
add_faqs("oman", [
    ("Do Pakistanis need a visa for Oman?",
     "Yes. Pakistan is not on the Oman Ministry of Foreign Affairs' lists of nationalities that can enter without a visa for up to 14 days."),
    ("Who issues the Oman visit visa?",
     "The Royal Oman Police (ROP). Applications are made online on the ROP eVisa website, and for tourists the Ministry says the Tourist Visit Visa (Unsponsored) will usually be appropriate. We check your eligibility and prepare the application with you."),
    ("How can I contact the Oman eVisa helpline from Pakistan?",
     "The ROP eVisa call centre is +968 22848200 from outside Oman, or email Info-OmaneVisa@rop.gov.om."),
])

# ---------------------------------------------------------------- Kuwait
KW = ("Kuwait Ministry of Interior: Kuwait Visa portal", "https://kuwaitvisa.moi.gov.kw/")
add_facts("kuwait", [
    ("Kuwait visas are applied for online on the Ministry of Interior's Kuwait Visa portal: create an account, complete your profile, submit the application and track it.", KW),
    ("Tourist visa (single visit): passport valid for at least 6 months; the entry permit is valid 30 days from issue; stay of no more than 90 days from entry; work is prohibited.", KW),
    ("Generally required: a valid passport (at least 6 months), a recent passport-size photo, a confirmed round-trip ticket and a hotel booking or proof of accommodation. More documents may be asked for depending on visa type and nationality.", KW),
    ("The portal says tourist visas typically take 1 to 2 business days, depending on visa type and nationality.", KW),
    ("Pakistan is not on the portal's list of countries whose citizens can get a tourist visa on arrival.", KW),
])
add_faqs("kuwait", [
    ("Can Pakistanis get a Kuwait visa on arrival?",
     "No. Pakistan is not on the Ministry of Interior's list of countries whose citizens can get a tourist visa on arrival. Apply online before you travel."),
    ("How long can I stay in Kuwait on a tourist visa?",
     "Up to 90 days from the date of entry. The entry permit itself is valid for 30 days from issue, so you must enter within that time."),
    ("What documents do I need for a Kuwait tourist visa?",
     "A passport valid at least 6 months, a recent passport-size photo, a confirmed round-trip ticket and a hotel booking or proof of accommodation. The Ministry may ask for more depending on your nationality."),
    ("How long does a Kuwait tourist visa take?",
     "The Ministry of Interior portal says tourist visas typically take 1 to 2 business days. We check your file before you submit so it is not held up."),
])

# ---------------------------------------------------------------- Spain
ES = ("Embassy of Spain in Islamabad: Schengen visas", "https://www.exteriores.gob.es/Embajadas/islamabad/en/ServiciosConsulares/Paginas/Consular/Visados-Schengen.aspx")
add_facts("spain", [
    ("Applications are submitted in person at the Consular Office or, when available, the Visa Application Centre. An appointment is needed in either case.", ES),
    ("Apply between 6 months and 15 days before your travel date (seafarers up to 9 months).", ES),
    ("The decision period is 15 calendar days from the day after submission, extendable to 45 days if an interview or more documents are needed.", ES),
    ("Your passport must be valid at least 3 months after your planned departure, have at least two blank pages and have been issued within the last 10 years.", ES),
    ("Travel medical insurance with cover of at least 30,000 euros is required.", ES),
    ("A refusal is notified in writing. You can ask for reconsideration within 1 month or seek judicial review within 2 months.", ES),
])
add_faqs("spain", [
    ("How early should I apply for a Spain visa from Pakistan?",
     "Between 6 months and 15 days before your travel date, according to the Embassy of Spain in Islamabad. Appointments fill up before summer, so start early."),
    ("How long does a Spain Schengen visa take?",
     "The embassy's legal decision period is 15 calendar days from the day after you submit. It can be extended to 45 days if an interview or more documents are needed."),
    ("Is an old passport accepted for a Spain visa?",
     "Only if it was issued within the last 10 years, is valid at least 3 months after you leave the Schengen area and has at least two blank pages."),
    ("What if my Spain visa is refused?",
     "The refusal is given in writing. You can ask the embassy to reconsider within 1 month, or seek judicial review within 2 months. We review the refusal reasons with you before you decide."),
])

# ---------------------------------------------------------------- Netherlands
NL = ("Netherlands Worldwide: Applying for a Schengen visa for the Netherlands in Pakistan (updated 19 Oct 2026)", "https://www.netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-pakistan")
add_facts("netherlands", [
    ("In Pakistan you apply at the VFS Global application centre in Islamabad, Karachi or Lahore. You must live in Pakistan or Afghanistan to apply there.", NL),
    ("Appointments can only be made through the VFS Global appointment system. The Dutch government advises against using intermediaries for appointments.", NL),
    ("You can apply up to 6 months before your trip, and at least 15 calendar days before you travel.", NL),
    ("Always submit all required documents: an application can be rejected if you do not.", NL),
    ("Fingerprints are taken, unless they were taken within the past 59 months. If a visa is refused, you receive a letter stating why.", NL),
])
add_faqs("netherlands", [
    ("Where do I apply for a Netherlands visa in Pakistan?",
     "At the VFS Global application centre in Islamabad, Karachi or Lahore. Appointments are booked only through the VFS Global appointment system. We prepare your file; you attend the appointment yourself."),
    ("How early can I apply for a Netherlands Schengen visa?",
     "Up to 6 months before your trip, and at least 15 calendar days before you travel."),
    ("Do I need to give fingerprints again for a Netherlands visa?",
     "Not if your fingerprints were taken for a Schengen visa within the past 59 months. Otherwise they are taken at VFS."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
