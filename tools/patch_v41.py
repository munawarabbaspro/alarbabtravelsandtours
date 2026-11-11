"""v41 - Denmark, Iceland, Norway, Finland, Poland, Czech Republic: official facts + FAQs (read 11 Nov 2026).

Sources read:
  - Embassy of Denmark in Pakistan, Visa: https://um.dk/pakistan/en/travel-and-residence/visa
  - Embassy of Norway in Islamabad, Resuming visa operations in Pakistan (published 26 Mar 2026):
    https://www.norway.no/en/pakistan/norway-pakistan/news-events/resuming-visa-operations-in-pakistan-24.03.2026/
  - Finland Abroad (Ministry for Foreign Affairs of Finland), Pakistan - where to apply for visa to Finland:
    https://finlandabroad.fi/web/pak/where-to-apply-for-a-visa-
  - Netherlands Worldwide, Schengen visa in Pakistan (VFS in Islamabad, Karachi, Lahore):
    https://www.netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-pakistan
  - Embassy of Poland in Islamabad, Notice on new requirements for registration of visa appointments (5 Jun 2025):
    https://www.gov.pl/web/pakistan-en/notice-on-new-requirements-for-registration-of-visa-appointments
  - Embassy of the Czech Republic in Islamabad, Appointments for short-term (Schengen) visa (updated 2 Nov 2026):
    https://mzv.gov.cz/islamabad/en/visa_1/appointments/appointments_for_short_term_schengen.html
No fees or amounts are added.

  py tools/patch_v41.py --dry | py tools/patch_v41.py   (idempotent)
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

# ---------------------------------------------------------------- Denmark + Iceland
DK = ("Embassy of Denmark in Pakistan: Visa", "https://um.dk/pakistan/en/travel-and-residence/visa")
add_facts("denmark", [
    ("Pakistani nationals need a visa to enter Denmark and the other Schengen states, and must get it before leaving Pakistan.", DK),
    ("Check the VFS visa centre website for available appointments before you submit the online application on ApplyVisa. The embassy says longer appointment waits can be expected at Gerry's because of heavy workload.", DK),
    ("A decision on a short-stay visa can be expected within 45 days after the application is considered admissible; it can take longer in individual cases.", DK),
    ("The embassy asks applicants not to use agents, warning that agents charge high prices for false documentation, which usually results in a flat refusal.", DK),
])
add_faqs("denmark", [
    ("How do I apply for a Denmark visa from Pakistan?",
     "Check VFS for an available appointment first, then submit the online application on ApplyVisa and attend the visa centre. We prepare genuine documents and the cover letter with you; the Danish embassy warns that false documents usually lead to refusal."),
    ("How long does a Denmark visa take?",
     "The Embassy of Denmark says a decision can be expected within 45 days after the application is accepted as admissible, sometimes longer."),
])
add_facts("iceland", [
    ("The Embassy of Denmark in Islamabad handles visa applications to Iceland, Greenland and the Faroe Islands.", DK),
])
add_faqs("iceland", [
    ("Where do Pakistanis apply for an Iceland visa?",
     "Through the Embassy of Denmark in Islamabad, which handles visa applications for Iceland. You check VFS for an appointment and submit the online application on ApplyVisa. We prepare the file with you."),
])

# ---------------------------------------------------------------- Norway
NO = ("Embassy of Norway in Islamabad: Resuming visa operations in Pakistan (26 Mar 2026)",
      "https://www.norway.no/en/pakistan/norway-pakistan/news-events/resuming-visa-operations-in-pakistan-24.03.2026/")
add_facts("norway", [
    ("Norway resumed visa operations in Pakistan on 24 March 2026. Visitor's visa applications are submitted through VFS Global / Gerry's International in Islamabad, Lahore and Karachi.", NO),
    ("You must book an appointment online. All visa applications are handled by the Norwegian Embassy in Abu Dhabi.", NO),
])
add_faqs("norway", [
    ("Are Norway visas open in Pakistan?",
     "Yes. The Embassy of Norway says visa operations in Pakistan resumed on 24 March 2026. You book online and submit through VFS Global / Gerry's in Islamabad, Lahore or Karachi; the Norwegian Embassy in Abu Dhabi decides."),
])

# ---------------------------------------------------------------- Finland
FI = ("Finland Abroad: Pakistan - where to apply for a visa to Finland", "https://finlandabroad.fi/web/pak/where-to-apply-for-a-visa-")
NL = ("Netherlands Worldwide: Applying for a Schengen visa for the Netherlands in Pakistan", "https://www.netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-pakistan")
add_facts("finland", [
    ("In visa matters in Pakistan, Finland is represented by the Netherlands.", FI),
    ("Netherlands Schengen applications in Pakistan are submitted at the VFS Global centres in Islamabad, Karachi and Lahore.", NL),
])
add_faqs("finland", [
    ("Where do Pakistanis apply for a Finland visa?",
     "Finland's Ministry for Foreign Affairs says Finland is represented by the Netherlands in visa matters in Pakistan. We check the current submission route with you and prepare the file."),
])
fi = C["finland"]
ni = fi["intro"].replace("meticulous file preparation for the Finnish embassy", "meticulous file preparation for your Finland application (in Pakistan, Finland is represented by the Netherlands in visa matters)")
if ni != fi["intro"]:
    log.append(("finland.intro", 1)); fi["intro"] = ni

# ---------------------------------------------------------------- Poland
PL = ("Embassy of Poland in Islamabad: notice on registration of visa appointments (5 Jun 2025)",
      "https://www.gov.pl/web/pakistan-en/notice-on-new-requirements-for-registration-of-visa-appointments")
add_facts("poland", [
    ("The Embassy of Poland accepts visa applications only directly at the embassy (Street 24, G-5/4, Diplomatic Enclave II, Islamabad), after booking an appointment on e-Konsulat.", PL),
    ("New appointments open every Monday between 9:00 and 15:00 (the next working day if Monday is a holiday). Applications are accepted only if the correct appointment category is booked.", PL),
    ("All applications must be submitted in person by the applicant. The embassy says it does not cooperate with travel agencies.", PL),
    ("Schengen visa applications are for stays of less than 90 days; longer stays need a national visa.", PL),
])
add_faqs("poland", [
    ("How do I book a Poland visa appointment in Pakistan?",
     "On e-Konsulat. The Embassy of Poland opens new appointments every Monday from 9:00 to 15:00, and you must choose the correct category. You then submit the application in person at the embassy in Islamabad."),
    ("Can a travel agent submit my Poland visa application?",
     "No. The Embassy of Poland says applications must be submitted in person by the applicant and it does not cooperate with travel agencies. We can help you prepare and check your documents; you book and attend yourself."),
])

# ---------------------------------------------------------------- Czech Republic
CZ = ("Embassy of the Czech Republic in Islamabad: Appointments for short-term (Schengen) visa (updated 2 Nov 2026)",
      "https://mzv.gov.cz/islamabad/en/visa_1/appointments/appointments_for_short_term_schengen.html")
add_facts("czech-republic", [
    ("Appointments are registered by email to islamabad.schengen@mzv.gov.cz on the last working day of each month, 12:00 to 18:00 Pakistan time, with only the passport number in the subject line.", CZ),
    ("Slots are given by automatic random selection, one month ahead. Send only one email per applicant; emails outside the window are disqualified.", CZ),
    ("The embassy says it does not cooperate with any third-party appointment sellers.", CZ),
    ("After the appointment, a decision is made in most cases within 15 days; some cases take up to 45 days.", CZ),
])
add_faqs("czech-republic", [
    ("How do I get a Czech visa appointment in Islamabad?",
     "Email islamabad.schengen@mzv.gov.cz on the last working day of the month between 12:00 and 18:00 Pakistan time, with only your passport number in the subject. Slots are given by random selection; send only one email."),
    ("How long does a Czech Schengen visa take?",
     "The Czech Embassy says most decisions come within 15 days after your appointment, and some take up to 45 days."),
    ("Should I buy a Czech visa appointment from someone?",
     "No. The Czech Embassy says it does not cooperate with any third-party appointment sellers. We prepare your documents; we do not sell appointments."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
