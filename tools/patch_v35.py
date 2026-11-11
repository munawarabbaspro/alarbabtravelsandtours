"""v35 - FAQs for eight countries whose official facts are already on the page (11 Nov 2026).

Sri Lanka, Vietnam, Cambodia, Philippines, Turkey, Azerbaijan, Tajikistan, Japan.
Every answer restates a fact already stored for that country with its official source. No fees, no promises.

  py tools/patch_v35.py --dry | py tools/patch_v35.py   (idempotent)
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

add_faqs("sri-lanka", [
    ("Is the Sri Lanka visa free for Pakistanis?",
     "Yes, for tourism. From 25 May 2026 Pakistan is one of 40 countries whose nationals get the 30-day tourist visa (ETA) free of charge, according to the official ETA website."),
    ("Do Pakistanis still need an ETA for Sri Lanka?",
     "Yes. Every foreign national, including the 40 free-visa countries, must get an Electronic Travel Authorization (ETA) before arriving in Sri Lanka."),
    ("How long can I stay in Sri Lanka on the free tourist visa?",
     "30 days. Double entry is allowed within that 30-day validity, counted from the date of first arrival. To stay longer you apply for a visa extension and pay the fee that applies."),
])
add_faqs("vietnam", [
    ("How do Pakistanis apply for a Vietnam visa?",
     "Online, on the official e-Visa website evisa.gov.vn: fill in the form, pay online and receive the e-Visa online. We fill the form with you and check your photo and passport scan first."),
    ("How long is the Vietnam e-Visa valid?",
     "Up to 90 days, for single or multiple entry."),
    ("Is the Vietnam e-Visa fee refunded if the visa is refused?",
     "No. The official website says the fee is not refunded if the visa is not granted, so it pays to get the form right the first time."),
    ("Can I enter Vietnam through any airport on an e-Visa?",
     "No. e-Visa holders must enter and leave through the international border gates the government designates. The Immigration Department also recommends completing the pre-arrival form before you travel."),
])
add_faqs("cambodia", [
    ("Do Pakistanis need a visa for Cambodia?",
     "Yes. Pakistan is not on the visa-exemption list for the tourist visa (Visa T), so you need a visa before you travel."),
    ("How long can I stay in Cambodia on the tourist e-Visa?",
     "The tourist e-Visa is single entry, valid for 3 months from the date of issue, with a stay of 1 month."),
    ("What do I need for the Cambodia e-Visa?",
     "A passport valid for more than six months at entry, a recent passport-size photo in digital format (JPEG or PNG), and a Visa or MasterCard credit card for payment."),
    ("Do I need to fill an arrival form for Cambodia?",
     "Yes. All travellers, including e-Visa holders, must submit the Cambodia e-Arrival form online. The official portal recommends doing it within 7 days before arrival."),
])
add_faqs("philippines", [
    ("Do I have to apply in person for a Philippines visa?",
     "Yes. A temporary visitor's visa application is made in person, normally at the embassy or consulate that covers your place of residence. For Pakistan that is the Philippine Embassy in Islamabad, Sector G-5, Diplomatic Enclave."),
    ("What documents do I need for a Philippines visit visa?",
     "A passport valid at least six months beyond your stay, the application form, two passport photos, proof that you are a genuine tourist or businessman, a confirmed return or onward ticket, and the visa fee. The embassy can ask for more."),
    ("Is my old handwritten passport accepted for a Philippines visa?",
     "No. Embassies accept only electronic and machine-readable passports."),
])
add_faqs("turkey", [
    ("Do Pakistanis need a visa for Turkey?",
     "Yes. Türkiye's Ministry of Foreign Affairs says ordinary passport holders from Pakistan need a visa to enter."),
    ("How do I apply for a Turkey sticker visa from Pakistan?",
     "You start in the official Pre-Application System (visa.gov.tr), then take the signed form, your passport and original documents to the Turkish mission. We prepare the file and fill the pre-application with you."),
    ("How long must my passport be valid for Turkey?",
     "The Ministry advises at least 6 months from the date of arrival. The legal minimum is 60 days beyond the visa's duration of stay."),
    ("Can I use the Turkey e-Visa for study or work?",
     "No. The e-Visa is only for tourism or commerce. Visas for work, study and other purposes are given by Turkish embassies or consulates."),
])
add_faqs("azerbaijan", [
    ("How long can I stay in Azerbaijan on the e-Visa?",
     "A single-entry e-Visa allows up to 30 days. A multiple-entry e-Visa allows up to 90 days."),
    ("How fast is the Azerbaijan e-Visa?",
     "The standard single e-Visa is issued within 3 business days. An accelerated one can be requested within 3 hours on evisa.gov.az."),
    ("What does the Azerbaijan Embassy in Islamabad ask for a tourist visa?",
     "The application form, your passport (original and copy) valid at least three months after departure, two photos, hotel booking, flight tickets, medical insurance and proof of sufficient funds. It accepts only complete applications and may ask for more."),
])
add_faqs("tajikistan", [
    ("Can I apply for the Tajikistan e-Visa after arriving?",
     "No. You can apply only while you are outside Tajikistan."),
    ("How long must my passport be valid for a Tajikistan e-Visa?",
     "At least six months after the validity of the e-Visa you request."),
    ("What happens if I make a mistake on the Tajikistan e-Visa form?",
     "The details must match your passport exactly, or the e-Visa is invalid. The fee is not refunded if an application is denied, so we check every field with you before you pay."),
])
add_faqs("japan", [
    ("Can I apply for a Japan visa at the embassy in Islamabad?",
     "No. Since 1 April 2024 applications go to VFS Global / Gerry's Visa. The embassy does not accept visa applications directly, except diplomatic and official visas."),
    ("How long does a Japan visa take from Pakistan?",
     "The embassy gives the standard processing period as 6 working days at the earliest, from applying at VFS until the visa is issued. Incomplete files take longer, sometimes several months."),
    ("What photo size is needed for a Japan visa?",
     "One recent photo, 45 mm x 45 mm, with a light, preferably white, background."),
    ("Can I reapply after a Japan visa refusal?",
     "Yes, 6 months after the refusal. The embassy does not give the reason for a refusal, so the new file should be checked carefully before you apply again."),
])

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
