"""v40 - Belgium, Luxembourg and Sweden: official facts + FAQs (read 11 Nov 2026).

Sources read:
  - Embassy of Belgium in Pakistan, Online Visa Application Procedure (last updated 10 Mar 2025);
    the section is titled "Visa for Belgium and Grand-Duchy Luxembourg":
    https://pakistan.diplomatie.belgium.be/en/travel-belgium/visa-belgium-and-grand-duchy-luxembourg/online-visa-application-procedure
  - Embassy of Sweden in Islamabad, news of 7 Jul 2025, "If you need to apply for a visa, you can now do so in Islamabad":
    https://www.swedenabroad.se/en/embassies/pakistan-islamabad/current/news/if-you-need-to-apply-for-a-visa-you-can-now-do-so-in-islamabad/
No fees or amounts are added.

  py tools/patch_v40.py --dry | py tools/patch_v40.py   (idempotent)
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

BE = ("Embassy of Belgium in Pakistan: Online visa application procedure (updated 10 Mar 2025)",
      "https://pakistan.diplomatie.belgium.be/en/travel-belgium/visa-belgium-and-grand-duchy-luxembourg/online-visa-application-procedure")
BE_FACTS = [
    ("Short-stay and long-stay visa forms must be filled out online on Visa On Web and submitted electronically.", BE),
    ("Appointments are made only through the Visa On Web portal, which redirects you to the VFS booking site. You print the form and go to the visa application centre you chose.", BE),
    ("The online form expires if it is not confirmed at the visa application centre within 30 days.", BE),
    ("At the centre your photo is taken live and fingerprints are taken if required. The application is processed at the Belgian Embassy, and you can track it through VFS Global or the Belgian Ministry of Interior.", BE),
]
add_facts("belgium", BE_FACTS)
add_faqs("belgium", [
    ("How do I apply for a Belgium visa from Pakistan?",
     "Fill the form online on Visa On Web, book the appointment through that portal (it redirects to VFS), print the form and take it with your documents to the visa centre you chose. We prepare the form and the file with you."),
    ("How long is the Belgium online visa form valid?",
     "30 days. The Embassy of Belgium says the form expires if it is not confirmed at the visa application centre within 30 days, so book the appointment soon after you fill it."),
])
add_facts("luxembourg", [
    ("The Embassy of Belgium in Pakistan handles visas for Belgium and the Grand-Duchy of Luxembourg in one section. Forms are filled online on Visa On Web and appointments are booked through it, which redirects to VFS.", BE),
])
add_faqs("luxembourg", [
    ("Where do Pakistanis apply for a Luxembourg visa?",
     "Through the Embassy of Belgium in Pakistan, whose visa section covers Belgium and the Grand-Duchy of Luxembourg. You fill the form online on Visa On Web and book the VFS appointment through it. We prepare the file with you."),
])

SE = ("Embassy of Sweden in Islamabad: visa applications in Islamabad (7 Jul 2025)",
      "https://www.swedenabroad.se/en/embassies/pakistan-islamabad/current/news/if-you-need-to-apply-for-a-visa-you-can-now-do-so-in-islamabad/")
add_facts("sweden", [
    ("Since 7 July 2025, Pakistani citizens and residents of Pakistan can apply in Islamabad for a visa to visit Sweden for up to 90 days.", SE),
    ("Applications are handled by the external provider VFS Global in Islamabad; you contact VFS to make an appointment.", SE),
])
add_faqs("sweden", [
    ("Can I apply for a Sweden visit visa in Pakistan?",
     "Yes. Since 7 July 2025 Pakistani citizens and residents can apply in Islamabad for visits of up to 90 days, through VFS Global, according to the Embassy of Sweden."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
