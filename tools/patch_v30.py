"""v30 - site review fixes (7 Oct 2026), data/site-data.json:
outdated visa facts (Thailand sticker visa, Indonesia VoA/B211A), unofficial bank-balance amounts, speed promises
("instant", "24-48 hours", "3 hours"), an approval promise (Oman), a UK success claim, superlatives and "hassle-free".
Thailand and Indonesia get an "official facts" block read on thaievisa.go.th and evisa.imigrasi.go.id on 7 Oct 2026.

  py tools/patch_v30.py --dry    show every change, write nothing
  py tools/patch_v30.py          apply (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "site-data.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
log = []

def setp(obj, key, old, new, where):
    s = obj[key]
    if old in s:
        obj[key] = s.replace(old, new); log.append((where, old, new))
    elif new not in s:
        raise SystemExit(f"NOT FOUND in {where}: {old!r}")

def setv(obj, key, new, where):
    if obj.get(key) != new:
        log.append((where, obj.get(key), new)); obj[key] = new

C = {}
for reg, lst in d["countries"].items():
    for c in lst:
        C.setdefault(c["slug"], c)          # the first record is the one the site renders
R = {r["slug"]: r for r in d["regions"]}

TH = ("Thai e-Visa official website (Ministry of Foreign Affairs of Thailand)", "https://www.thaievisa.go.th/")
ID_HOME = ("Indonesia e-Visa official website (Directorate General of Immigration)", "https://evisa.imigrasi.go.id/")
ID_SEL = ("Indonesia e-Visa: visa selection", "https://evisa.imigrasi.go.id/web/visa-selection")

# Thailand: e-Visa only (sticker wording removed), no unofficial balance
th = C["thailand"]
setv(th, "description", "Thailand visit visa from Pakistan: apply online on the official Thai e-Visa website. We prepare and upload your file from Blue Area, Islamabad.", "thailand.description")
setv(th, "intro", "Thailand is a favourite for Pakistani tourists. Thai visas are applied for online on the official Thai e-Visa website: you create an account, fill in the form, upload your documents and pay the fee, and the e-Visa confirmation is sent by email. We prepare your documents and the application, and arrange hotel vouchers and flight bookings.", "thailand.intro")
setp(th["docs"], 2, "Bank Statement (Last 6 months, showing 200,000+ PKR balance)", "Bank Statement (Last 6 months)", "thailand.docs[2]")
setv(th, "facts", [
    ["Thai visas are applied for online on the official e-Visa website: create an account, fill in the application form, upload your supporting documents and pay the visa fee. The e-Visa confirmation is sent by email.", *TH],
    ["Passports and supporting documents no longer have to be submitted in person at the Royal Thai Embassy or Consulate-General.", *TH],
    ["You can apply only while you are not in Thailand.", *TH],
    ["Print the approval email and show it to the airline and to Thai immigration when you travel.", *TH],
    ["The Embassy or Consulate-General may ask for an interview or more documents. Applying does not mean a visa will be granted, and visa fees are non-refundable.", *TH],
], "thailand.facts")

# Indonesia: Pakistan is offered e-Visa (C1 / D1), not visa on arrival; B211A is the old code
idn = C["indonesia"]
setv(idn, "description", "Indonesia visit visa from Pakistan: Pakistani passport holders apply for a tourist e-Visa on the official Indonesian e-Visa website. Expert guidance for Bali travel.", "indonesia.description")
setv(idn, "intro", "From the tropical paradise of Bali to the bustling streets of Jakarta, Indonesia is a top pick. On the official Indonesian e-Visa website, a Pakistani passport is offered a tourist e-Visa: C1 (single entry) or D1 (multiple entry). We prepare and submit your application and check every document first.", "indonesia.intro")
setp(idn["docs"], 2, "Bank Statement (Last 6 months, showing $2000+ USD equivalent)", "Bank Statement (Last 6 months)", "indonesia.docs[2]")
setv(idn, "facts", [
    ["For a Pakistani passport and the purpose 'Tourism, Family Visit, and Transit', the official site offers the C1 Tourist Single Entry Visitor Visa (60 days) and the D1 Tourist Multiple Entry Visa (1, 2 or 5 years).", *ID_SEL],
    ["Visa on arrival is not offered for a Pakistani passport on that page (it is offered for some other nationalities).", *ID_SEL],
    ["The visa fee is paid online (SIMPONI, or a Mastercard, Visa or JCB card). Once approved, a link to download the visa is sent to your email.", *ID_HOME],
    ["All travellers must submit an arrival card within 3 days before arriving in Indonesia.", *ID_HOME],
], "indonesia.facts")

# other countries: speed promises, unofficial amounts, approval promise
setp(C["malaysia"], "description", "Get your Malaysia e-visa or sticker visa processed quickly in Islamabad.", "Malaysia e-visa or embassy visa for Pakistani passport holders, prepared in Islamabad.", "malaysia.description")
setp(C["malaysia"], "intro", "We specialize in rapid e-visa processing for Pakistani citizens.", "We prepare and submit Malaysia eVisa applications for Pakistani citizens.", "malaysia.intro")
setp(C["sri-lanka"], "intro", "We provide instant ETA (Electronic Travel Authorization) services with just your passport copy.", "We apply for your ETA (Electronic Travel Authorization) on the official portal for you.", "sri-lanka.intro")
setp(C["vietnam"], "intro", "for a hassle-free entry into this vibrant SE Asian nation.", "for your trip to this vibrant South-East Asian nation.", "vietnam.intro")
setp(C["cambodia"], "description", "Quick Cambodia e-visa processing for Pakistani travelers.", "Cambodia e-visa processing for Pakistani travellers.", "cambodia.description")
setp(C["turkey"], "intro", "and instant e-visas for those with valid Schengen/US visas.", "and e-visas for travellers who qualify through a valid visa or residence permit (conditions on evisa.gov.tr).", "turkey.intro")
setp(C["turkey"]["docs"], 2, "Bank Statement (Last 6 months, showing 500,000+ PKR balance)", "Bank Statement (Last 6 months)", "turkey.docs[2]")
setp(C["azerbaijan"], "description", "Instant Azerbaijan ASAN e-visa processing for Pakistani tourists.", "Azerbaijan ASAN e-visa processing for Pakistani tourists, on the official portal.", "azerbaijan.description")
setp(C["azerbaijan"], "intro", "We process your Azerbaijan e-visa within 3 hours to 3 days with minimum documentation.", "We apply for your Azerbaijan e-visa on the official ASAN portal with minimum documentation; the portal shows the processing options when you apply.", "azerbaijan.intro")
setp(C["mauritius"]["docs"], 3, "Proof of Funds ($100 per day)", "Proof of sufficient funds", "mauritius.docs[3]")
setp(C["united-arab-emirates"], "description", "Fast-track UAE and Dubai visit visas from Pakistan. 24-48 hour processing.", "UAE and Dubai visit visas from Pakistan, prepared and submitted from Blue Area, Islamabad.", "uae.description")
setp(C["united-arab-emirates"], "intro", "We provide instant e-visa services for 30, 60, and 90 days, handling all sponsorships and documentation for a smooth entry.", "We prepare and submit your UAE visit visa application and the documents it needs. Visa length, processing time and the decision depend on the UAE authorities.", "uae.intro")
setp(C["oman"], "description", "Quick processing and expert guidance.", "Expert guidance from Islamabad.", "oman.description")
setp(C["oman"], "intro", "through the Royal Oman Police portal, ensuring your application is approved without delay.", "through the Royal Oman Police portal and follow up your application. The decision rests with the Royal Oman Police.", "oman.intro")
setp(C["qatar"], "description", "Fast-track Qatar visit visas and Hayya card assistance from Pakistan.", "Qatar visit visa and Hayya assistance from Pakistan.", "qatar.description")
setp(C["bahrain"], "intro", "handling the online portal submission for rapid approvals.", "handling the online portal submission and follow-up.", "bahrain.intro")
setp(C["iceland"], "intro", "offers unparalleled natural wonders", "offers natural wonders", "iceland.intro")

# regions
setp(R["schengen"], "intro", "offers unparalleled access to 29 European countries", "gives access to 29 European countries on one visa", "schengen.intro")
setp(R["united-kingdom"], "seoDescription", " with high success rates", ", with a free document check", "uk.seoDescription")
setp(R["middle-east"]["stepByStep"][2], "desc", "Receive your eVisa via email or WhatsApp in as little as 24-48 hours.", "Receive your eVisa by email or WhatsApp once it is issued.", "middle-east.stepByStep[2]")
setp(R["middle-east"]["faqs"][0], "a", "Standard processing is 2-3 days, but express options are available.", "It depends on the issuing authority and the season. Tell us your travel date and we advise what is realistic.", "middle-east.faqs[0]")
setp(R["south-asia"], "intro", "applications instantly", "applications on the official portal", "south-asia.intro")
setp(R["central-asia"], "intro", "lightning-fast eVisa services", "eVisa services", "central-asia.intro")
for r in d["regions"]:
    for v in r["visas"]:
        if "hassle-free visit visa" in v.get("heroText", ""):
            setp(v, "heroText", "with a hassle-free visit visa", "with a visit visa", f"{r['slug']}.visas[0].heroText")
for v in d["visaTypeTemplate"]:
    if "hassle-free" in v.get("heroText", ""):
        setp(v, "heroText", "with a hassle-free visit visa", "with a visit visa", "visaTypeTemplate.heroText")
setp(d["services"][1], "desc", "with hassle-free tourist visa processing, with", "with tourist visa processing and", "services[1].desc")

# shared FAQs
setp(d["faqSchengenGeneral"][1], "a",
     "While there is no fixed 'official' amount, embassies look for a consistent closing balance that comfortably covers your entire trip (flights, hotels, daily expenses of €100-€150/day) while leaving enough funds for your return. Typically, a steady closing balance of PKR 1.5M to 2.5M over 6 months is recommended. We provide free profile assessments to guide you on exact financial requirements.",
     "There is no fixed official amount for Pakistani applicants. Embassies look for a steady balance over the last 6 months that comfortably covers your whole trip (flights, hotels and daily expenses) and leaves enough for your return. Send us your statement for a free check.", "faqSchengenGeneral[1]")
setp(d["faqSchengenGeneral"][4], "a", "we ensure your file is 100% accurate before submission to maximize your approval chances.", "we check every document before submission to avoid mistakes that lead to refusals.", "faqSchengenGeneral[4]")
setp(d["faqSchengenGeneral"][6], "a", "you only need a clear scanned copy", "we usually start with a clear scanned copy", "faqSchengenGeneral[6] (docs)")
setp(d["faqSchengenGeneral"][6], "a", " Processing usually takes 24 to 48 working hours.", "", "faqSchengenGeneral[6] (timing)")
before = len(d["faqAir"])
d["faqAir"] = [f for f in d["faqAir"] if "iata" not in f["q"].lower()]   # old "Yes, full IATA accreditation" answer (never shown, removed for good)
if len(d["faqAir"]) != before:
    log.append(("faqAir", "IATA question", "(removed)"))

for w, a, b in log:
    print("-", w); print("   BEFORE:", str(a)[:180]); print("   AFTER: ", str(b)[:180])
print("\nchanges:", len(log))
if "--dry" in sys.argv:
    print("DRY RUN - nothing written"); sys.exit()
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
print("written", P)
