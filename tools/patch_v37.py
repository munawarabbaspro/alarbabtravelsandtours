"""v37 - Official facts + FAQs for Germany, France and Saudi Arabia (read 11 Nov 2026).

Sources read:
  - German Missions in Pakistan, Visa: Short-term-stay / Schengen (article of 19 Feb 2026):
    https://pakistan.diplo.de/pk-en/service/visa-shortterm-1673126
  - Embassy of France in Pakistan, "Prendre rendez-vous pour deposer une demande de visa avec TLSContact" (published 10 Nov 2026):
    https://pk.diplomatie.gouv.fr/fr/aller-en-france/prendre-rendez-vous-pour-deposer-une-demande-de-visa-avec-tlscontact
  - Saudi eVisa portal (official tourist visa site): https://visa.visitsaudi.com/
No fees or amounts are added.

  py tools/patch_v37.py --dry | py tools/patch_v37.py   (idempotent)
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

# ---------------------------------------------------------------- Germany
DE = ("German Missions in Pakistan: Visa short-term stay / Schengen", "https://pakistan.diplo.de/pk-en/service/visa-shortterm-1673126")
add_facts("germany", [
    ("Appointments are registered online. The German Embassy Islamabad runs a waiting list: you register, receive a waiting-list number by email, and are told once your appointment is set.", DE),
    ("The Embassy in Islamabad takes applicants from Islamabad Capital Territory, Khyber Pakhtunkhwa, Azad Jammu & Kashmir and Punjab. The Consulate General in Karachi takes applicants from Sindh and Balochistan.", DE),
    ("Registration on the waiting list is free of charge. The mission warns that anyone asking for money at this stage is a fraudster and should be reported to the Pakistani police.", DE),
    ("Only one appointment per person is needed. Multiple registrations for the same applicant are cancelled or refused at the appointment.", DE),
    ("A short-term visa usually takes about 14 calendar days from the day of application, longer in some cases and in peak travel season. You can apply up to six months before your journey.", DE),
    ("The mission asks applicants to fill the online VIDEX application form and bring the printout with its barcode.", DE),
    ("Pakistani nationals in many cases need a visa even for the international transit area of a German airport.", DE),
])
add_faqs("germany", [
    ("How do I get a Germany visa appointment in Islamabad?",
     "You register online on the German Embassy Islamabad's waiting list. You get a waiting-list number by email and are told when your appointment is set. Registration is free; register only once per person."),
    ("Should I pay someone for a German visa appointment?",
     "No. The German mission says registration on the waiting list is free, and anyone asking for money at this stage is a fraudster. We prepare your file and documents; we do not sell appointments."),
    ("Which German office handles my visa: Islamabad or Karachi?",
     "Islamabad handles applicants from ICT, Khyber Pakhtunkhwa, AJK and Punjab. Karachi handles Sindh and Balochistan."),
    ("How long does a Germany Schengen visa take from Pakistan?",
     "The German mission says about 14 calendar days from the day you apply, sometimes longer, especially in peak season. You can apply up to six months before you travel."),
    ("Do I need a visa to transit through a German airport?",
     "Often yes. The German mission says Pakistani nationals in many cases need a visa even for the international transit area of a German airport. Tell us your route and we check."),
])

# ---------------------------------------------------------------- France
FR = ("Embassy of France in Pakistan: visa appointments with TLScontact (published 10 Nov 2026)",
      "https://pk.diplomatie.gouv.fr/fr/aller-en-france/prendre-rendez-vous-pour-deposer-une-demande-de-visa-avec-tlscontact")
add_facts("france", [
    ("From 16 November 2026, appointments to apply for a France visa are booked only online through TLScontact, which replaces AEG. Appointments are not given by phone.", FR),
    ("First fill the visa application form online on France-Visas and print the form, the receipt and the list of supporting documents.", FR),
    ("After an appointment is allotted you are asked to pay the TLScontact service charge online within the stated time. If it is not paid in time, the appointment is cancelled.", FR),
    ("On the appointment day you go in person to the Embassy of France in Islamabad with the printed confirmation, the signed France-Visas form, your passport and all supporting documents in original and copy.", FR),
    ("You must print the 'Receipt for Appointment and Passport Collection' from TLScontact: it is needed to pass security into the Diplomatic Enclave.", FR),
    ("Passports are returned at the TLScontact centre in Islamabad, not at the embassy, in person, through an authorised representative, or by optional courier.", FR),
])
add_faqs("france", [
    ("How do I book a France visa appointment in Pakistan from November 2026?",
     "From 16 November 2026, only online through TLScontact, the embassy's new partner in place of AEG. First complete the France-Visas form, then register on TLScontact. Appointments are not given by phone."),
    ("Where do I submit my France visa application in Pakistan?",
     "In person at the Embassy of France in Islamabad, on your TLScontact appointment date. Bring the printed confirmation, the signed France-Visas form, your passport and all documents in original and copy."),
    ("What happens if I do not pay the TLScontact service charge in time?",
     "Your appointment is cancelled. The embassy says the charge must be paid online within the time given in the notification."),
    ("Where do I collect my passport after a France visa decision?",
     "At the TLScontact centre in Islamabad, not at the embassy. You can collect it yourself, send an authorised representative, or choose the optional courier return."),
])

# ---------------------------------------------------------------- Saudi Arabia
SA = ("Saudi eVisa portal (official)", "https://visa.visitsaudi.com/")
add_facts("saudi-arabia", [
    ("The Saudi tourist eVisa is open to visitors from 72 eligible countries. Pakistan is not on that list; the portal tells others to contact the nearest Saudi embassy.", SA),
    ("For eligible countries the tourist eVisa is a one-year, multiple-entry visa allowing up to 90 days in the country.", SA),
    ("The tourist visa covers tourism activities such as events, family visits, leisure and Umrah (not Hajj). It does not cover activities such as study.", SA),
])
add_faqs("saudi-arabia", [
    ("Can Pakistanis get the Saudi tourist eVisa online?",
     "Not directly: Pakistan is not on the official list of 72 countries eligible for the Saudi tourist eVisa, and the portal says to contact the nearest Saudi embassy. Umrah and family visit visas have their own routes, so tell us your purpose and we confirm the right one."),
    ("Can I perform Umrah on a Saudi tourist visa?",
     "The official eVisa portal says the tourist visa allows Umrah (not Hajj). For Pakistani passport holders, ask us about Umrah visas and packages from Islamabad."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
