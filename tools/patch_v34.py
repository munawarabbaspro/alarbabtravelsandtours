"""v34 - FAQs for Singapore, Indonesia, Uzbekistan and Bahrain (11 Nov 2026).

Why: Search Console (Sep-Nov 2026): Singapore position 19, Indonesia 16.5, Uzbekistan 14.6, Bahrain 37.7.
Each answer restates a fact already on the page with its official source (ICA, Indonesian e-Visa,
Uzbek MFA/embassy, Bahrain e-Visa). Nothing new is claimed; no fees.

  py tools/patch_v34.py --dry | py tools/patch_v34.py   (idempotent)
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

def add_faqs(slug, items):
    c = C[slug]
    cur = [list(x) for x in (c.get("faq_extra") or [])]
    have = {q for q, _ in cur}
    new = cur + [[q, a] for q, a in items if q not in have]
    if new != cur:
        log.append((slug, len(new) - len(cur))); c["faq_extra"] = new

add_faqs("singapore", [
    ("Do Pakistanis need a visa for Singapore?",
     "Yes. Pakistan is on the list of Singapore's Immigration & Checkpoints Authority (ICA) of travel documents that need a valid Singapore entry visa before travel."),
    ("Is there a Singapore visa on arrival for Pakistani passport holders?",
     "No. ICA does not accept visa applications at the immigration counters, so get your visa before you fly."),
    ("How do Pakistanis apply for a Singapore visa without a sponsor in Singapore?",
     "If you have no local contact with a Singpass or Corppass account, ICA says you apply through an authorised visa agent appointed by the Singapore Overseas Missions, or at the nearest Singapore Overseas Mission. We prepare your documents for that submission."),
    ("How long can I stay in Singapore on a visit visa?",
     "ICA officers at the checkpoint decide whether you may enter and how long you may stay. Your Visit Pass (e-Pass) comes by email, so give a valid email address in the SG Arrival Card."),
])
add_faqs("indonesia", [
    ("Is there an Indonesia visa on arrival for Pakistanis?",
     "No. On the official Indonesian e-Visa website, visa on arrival is not offered for a Pakistani passport. Apply for the e-Visa before you travel."),
    ("Which Indonesia visa do Pakistanis get for a holiday in Bali?",
     "For a Pakistani passport and the purpose 'Tourism, Family Visit, and Transit', the official site offers the C1 Tourist Single Entry Visitor Visa (60 days) and the D1 Tourist Multiple Entry Visa (1, 2 or 5 years)."),
    ("How do I pay for the Indonesia e-Visa and receive it?",
     "The fee is paid online (SIMPONI, or a Mastercard, Visa or JCB card). Once approved, a link to download the visa is sent to your email."),
    ("Do I need an arrival card for Indonesia?",
     "Yes. All travellers must submit an arrival card within 3 days before arriving in Indonesia."),
])
add_faqs("uzbekistan", [
    ("Where is the Uzbekistan Embassy in Islamabad and when is it open?",
     "The consular section is at House 40, Khayaban-e-Iqbal Road, Sector F-8/3, Islamabad. Its listed office hours are Monday, Wednesday and Friday, 9:30 to 12:00."),
    ("Do I have to apply through a particular visa centre for Uzbekistan?",
     "No. In a statement of 26 December 2024 the Embassy of Uzbekistan in Islamabad says it has given no exclusive powers to any visa centre."),
])
add_faqs("bahrain", [
    ("Is there a Bahrain visa on arrival for Pakistanis?",
     "Pakistan is on Bahrain's official visa-on-arrival list, marked 'Conditions apply'. Check the conditions for your passport on the official e-Visa website before you travel, or ask us to check them with you."),
    ("What is the official website for a Bahrain visa?",
     "evisa.gov.bh. The site says it is the only official website to apply for a Bahrain visa and that no website or company operates on behalf of the Government of Bahrain. We help you prepare the form and documents on that site."),
    ("Will the Bahrain visa be stamped in my passport?",
     "No. The visa is not stamped in your passport. You print it from the official website and carry it with you."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
