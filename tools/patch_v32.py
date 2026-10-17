"""v32 - official-source facts for six more Asian country guides (read on the official sites on 8 Oct 2026):
Cambodia, Bahrain, Turkey, Uzbekistan, Japan, Azerbaijan. Same rules as v29: only government sources, linked on the page;
no fees; only numbers that the source itself states, and cited.

Not done (not enough verifiable from official sources): Malaysia (official eVISA portal is behind a login, imi.gov.my did not load,
the High Commission's visa page is for Malaysians), Bangladesh (the High Commission's visa pages are PDF attachments only).

Corrections found while reading the sources:
  - Uzbekistan: the official e-Visa portal does NOT list Pakistan among its citizenships (the old text said e-visa for all Pakistani passport holders).
  - Turkey: Pakistani ordinary passports need a visa; the e-Visa is only for holders of a valid Schengen, USA, UK or Ireland visa or residence permit.
  - Japan: since 1 April 2024 applications in Pakistan go through VFS Global / Gerry's Visa, not the embassy desk.

  py tools/patch_v32.py --dry | py tools/patch_v32.py   (idempotent)
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
        C.setdefault(c["slug"], c)       # first record = the one the site renders

def f(text, src):
    return [text, src[0], src[1]]

# ---------------------------------------------------------------- Cambodia
KH = ("Cambodia e-Visa official website (Ministry of Foreign Affairs and International Cooperation)", "https://www.evisa.gov.kh/")
KH_T = ("Cambodia e-Visa: visa type information", "https://www.evisa.gov.kh/information/visa_type/4")
kh = C["cambodia"]
setv(kh, "description", "Cambodia tourist e-Visa (Visa T) for Pakistani travellers, applied for on the official Cambodia e-Visa website. We prepare your details and photo.", "cambodia.description")
setv(kh, "intro", "Cambodia issues tourist e-Visas (Visa T) through its official e-Visa website, run by the Ministry of Foreign Affairs and International Cooperation. You apply online, pay, and download the approved e-Visa. We prepare your details and photo and guide you through the online form. Rules change, so always check the official site.", "cambodia.intro")
setv(kh, "docs", ["Passport valid for more than six months at the time of entry",
                  "A recent passport-size photo in digital format (JPEG or PNG)",
                  "A valid Visa or MasterCard credit card, to pay the e-Visa fee online",
                  "Cambodia e-Arrival form, submitted online before you travel"], "cambodia.docs")
setv(kh, "official_only", True, "cambodia.official_only")
setv(kh, "lead", "Cambodia's tourist e-Visa (Visa T) is applied for online on the official government website. Pakistan is not on the portal's visa-exemption list, and the application form checks eligibility.", "cambodia.lead")
setv(kh, "facts", [
    f("Tourists apply for the e-Visa on the official website: apply online, pay, then receive the approved e-Visa by email or download it from the site.", KH),
    f("The tourist e-Visa (Visa T) is single entry only, valid for 3 months from the date of issue, with a length of stay of 1 month.", KH_T),
    f("Requirements stated for Visa T: a passport valid for more than six months at the time of entry, a recent passport-size photo in digital format (JPEG or PNG), and a valid Visa or MasterCard credit card.", KH_T),
    f("The visa-exemption list for Visa T names Laos, Malaysia, Philippines, Singapore, Vietnam, Thailand, Indonesia, Brunei Darussalam and Myanmar. Pakistan is not on that list.", KH_T),
    f("All travellers, including e-Visa holders, must submit the Cambodia e-Arrival form online. The portal recommends doing it within 7 days before arrival.", KH),
    f("These pages do not say which passports can use the e-Visa. The application form checks this, so confirm your passport there before paying.", KH_T),
], "cambodia.facts")
setv(kh, "faq_extra", [["Which passports can apply for the Cambodia e-Visa?", "The official e-Visa pages do not list eligible nationalities, and the application form does the check. Confirm it on the official website before you pay, and tell us on WhatsApp if the form does not accept your passport."]], "cambodia.faq_extra")

# ---------------------------------------------------------------- Bahrain
BH = ("Bahrain e-Visa official website (Nationality, Passports & Residence Affairs)", "https://www.evisa.gov.bh/")
BH_ON = ("Bahrain e-Visa: countries eligible to get a visa online", "https://www.evisa.gov.bh/list-of-online-visa-country.html")
BH_AR = ("Bahrain e-Visa: countries eligible for visa on arrival", "https://www.evisa.gov.bh/list-of-onarrival-visa-country.html")
BH_PR = ("Bahrain e-Visa: process for obtaining a visa", "https://www.evisa.gov.bh/VisaBhr2En.html")
BH_FAQ = ("Bahrain e-Visa: FAQ", "https://www.evisa.gov.bh/VisaBhr7En.html")
bh = C["bahrain"]
setv(bh, "description", "Bahrain visa for Pakistani citizens: Pakistan is on the official eVisa eligibility lists. We prepare your file and guide you through the online application.", "bahrain.description")
setv(bh, "intro", "Pakistan appears on Bahrain's official list of countries eligible to get a visa online, and also on its on-arrival list, with conditions that the portal shows when you check eligibility. The Bahrain government says its own site is the only official place to apply. AL ARBAB TRAVEL AND TOURS is a private agency: we prepare your documents and guide you through the application, and the decision rests with Bahrain's authorities.", "bahrain.intro")
setv(bh, "docs", ["Your passport and the personal details the online application requires",
                  "The supporting documents listed for your visa type (the portal shows them after you complete the eligibility page)",
                  "A credit card to pay the application fee online",
                  "Your visa printed from the portal (no visa is stamped in the passport before arrival)"], "bahrain.docs")
setv(bh, "official_only", True, "bahrain.official_only")
setv(bh, "lead", "Pakistan is on Bahrain's official lists for online visas and for visas on arrival, both with conditions. The government says its own site is the only official place to apply.", "bahrain.lead")
setv(bh, "facts", [
    f("The Bahrain e-Visa website says it is the only official website to apply for a Bahrain visa, and that no website or company operates on behalf of the Government of Bahrain.", BH),
    f("Pakistan is on the official list of countries eligible to get a visa online. The list says terms and conditions apply.", BH_ON),
    f("Pakistan is also on the official list for visa on arrival, marked 'Conditions apply'. The conditions for your passport are shown on the portal's eligibility page.", BH_AR),
    f("How to apply: complete the eligibility page, choose the visa type and read its conditions, fill in the online form, attach the required documents, and pay by credit card. You are told by email once the application is processed.", BH_PR),
    f("Holding a visa does not guarantee entry, and paying the application fee does not guarantee approval. If an application is not approved, the processing fee is not refunded.", BH),
    f("No visa is stamped in your passport before you arrive in Bahrain. You print the visa from the website.", BH_FAQ),
], "bahrain.facts")
setv(bh, "faq_extra", [["Can Pakistani citizens apply for a Bahrain e-Visa?", "Pakistan is on Bahrain's official list of countries eligible to get a visa online, with conditions. Check your own eligibility on the official Bahrain e-Visa website before you apply."]], "bahrain.faq_extra")

# ---------------------------------------------------------------- Turkey
TR = ("Republic of Türkiye Ministry of Foreign Affairs: visa information for foreigners", "https://www.mfa.gov.tr/visa-information-for-foreigners.en.mfa")
TR_PRE = ("Republic of Türkiye Ministry of Foreign Affairs: pre-application system for the Turkish sticker visa", "https://www.mfa.gov.tr/pre-application-system-for-turkish-sticker-visa.en.mfa")
TR_GEN = ("Republic of Türkiye Ministry of Foreign Affairs: general information about Turkish visas", "https://www.mfa.gov.tr/general-information-about-turkish-visas.en.mfa")
tr = C["turkey"]
setv(tr, "description", "Turkey visa for Pakistani passport holders: a visa is required, and the e-Visa is only open with a valid Schengen, USA, UK or Ireland visa or permit. We prepare your file.", "turkey.description")
setv(tr, "intro", "According to the Turkish Ministry of Foreign Affairs, Pakistani ordinary passport holders need a visa to enter Türkiye. Holders of a valid Schengen, USA, UK or Ireland visa or residence permit may get a one-month single-entry e-Visa online. Everyone else applies for a sticker visa through the Turkish mission, starting with the ministry's online pre-application system. We prepare your file for either route. Rules change, so always check the official site.", "turkey.intro")
setv(tr, "docs", ["Passport valid for at least 6 months from the date of arrival (the Ministry's advice)",
                  "For the e-Visa: a valid Schengen, USA, UK or Ireland visa or residence permit",
                  "For the sticker visa: the online pre-application, then the signed application form, your passport and the original documents at the Turkish mission or visa application centre"], "turkey.docs")
setv(tr, "official_only", True, "turkey.official_only")
setv(tr, "tier_note", "The Turkish e-Visa is only open to Pakistani passport holders with a valid Schengen, USA, UK or Ireland visa or residence permit. Everyone else applies for a sticker visa through the Turkish mission. We prepare your file for the route that applies to you.", "turkey.tier_note")
setv(tr, "lead", "Pakistani ordinary passport holders need a visa for Türkiye. The Turkish Ministry of Foreign Affairs says only holders of a valid Schengen, USA, UK or Ireland visa or residence permit may get the one-month e-Visa.", "turkey.lead")
setv(tr, "facts", [
    f("Pakistan: ordinary passport holders are required to have a visa to enter Türkiye.", TR),
    f("Ordinary passport holders with a valid Schengen, USA, UK or Ireland visa or residence permit may get a one-month single-entry e-Visa on the e-Visa website.", TR),
    f("The e-Visa is only valid when the purpose of travel is tourism or commerce. For other purposes, such as work and study, visas are given by Turkish embassies or consulates.", TR),
    f("Everyone else applies for a sticker visa. Applications start in the Pre-Application System for the Turkish Sticker Visa (visa.gov.tr), then the applicant goes to the Turkish mission to submit the signed application form, the passport and the original documents.", TR_PRE),
    f("The Ministry advises a passport valid for at least 6 months from the date of arrival. The law requires validity of at least 60 days beyond the visa's duration of stay.", TR),
    f("The Ministry reminds visitors that its visa regime can change under the reciprocity principle.", TR_GEN),
], "turkey.facts")
setv(tr, "faq_extra", [["Can a Pakistani citizen get a Turkey e-Visa?", "Only with a valid Schengen, USA, UK or Ireland visa or residence permit, according to the Turkish Ministry of Foreign Affairs. Otherwise you apply for a sticker visa through the Turkish mission."]], "turkey.faq_extra")

# ---------------------------------------------------------------- Uzbekistan  (the old text said e-visa for all Pakistani passport holders)
UZ_EV = ("Uzbekistan e-Visa official portal (Ministry of Foreign Affairs): what you need to know", "https://e-visa.gov.uz/what-you-need-to-know")
UZ_APP = ("Uzbekistan e-Visa official portal: application form", "https://e-visa.gov.uz/application")
UZ_GEN = ("Embassy of Uzbekistan in Pakistan: general information", "https://pakistan.mfa.uz/en/page/visa-general-info")
UZ_REQ = ("Embassy of Uzbekistan in Pakistan: requirements for citizens of Pakistan", "https://pakistan.mfa.uz/en/page/pakistani-citizens-requirements")
UZ_ST = ("Embassy of Uzbekistan in Pakistan: official statement, 26 December 2024", "https://pakistan.mfa.uz/en/news/oficialnoe-zaiavlenie-posolstva-respubliki-uzbekistan-v-islamskoi-respublike-pakistan-1")
uz = C["uzbekistan"]
setv(uz, "description", "Uzbekistan visa for Pakistani citizens: the official e-Visa portal does not list Pakistan, so you deal with the Uzbek embassy in Islamabad. We prepare your file.", "uzbekistan.description")
setv(uz, "intro", "Uzbekistan's official e-Visa portal does not list Pakistan among its citizenships, so Pakistani applicants deal with the Embassy of Uzbekistan in Islamabad. The embassy's online page of requirements for Pakistani citizens is empty at the moment, so confirm the current document list with its consular section before you apply. We prepare your file and follow it up. Rules change, so always check the official sites.", "uzbekistan.intro")
setv(uz, "docs", ["Valid passport",
                  "The visa application and supporting documents the Embassy of Uzbekistan asks for (its online Pakistan requirements page is empty, so confirm the list with the consular section)",
                  "Attendance at the embassy's consular section on its visa days (Monday, Wednesday and Friday, 9:30 to 12:00)"], "uzbekistan.docs")
setv(uz, "official_only", True, "uzbekistan.official_only")
setv(uz, "tier_note", "The official Uzbek e-Visa portal does not list Pakistan, so Pakistani applicants deal with the Embassy of Uzbekistan in Islamabad. We prepare your file and follow it up with you.", "uzbekistan.tier_note")
setv(uz, "lead", "Uzbekistan's official e-Visa portal does not list Pakistan among its citizenships. Pakistani applicants deal with the Embassy of Uzbekistan in Islamabad.", "uzbekistan.lead")
setv(uz, "facts", [
    f("The official e-Visa application form asks you to choose your citizenship from a list. Pakistan is not in that list.", UZ_APP),
    f("The portal says that if a citizen's country is not in its list of countries with a simplified visa procedure, the user is told to contact the appropriate foreign institution of the Ministry of Foreign Affairs of Uzbekistan.", UZ_EV),
    f("The Embassy of Uzbekistan in Islamabad has a consular section at House 40, Khayaban-e-Iqbal Road, Sector F-8/3. Its listed office hours are Monday, Wednesday and Friday, 9:30 to 12:00.", UZ_GEN),
    f("The embassy's page 'Requirements for citizens of the Islamic Republic of Pakistan' has no content online, so the document list should be confirmed with the consular section.", UZ_REQ),
    f("In a statement of 26 December 2024 the embassy says it welcomes visa centres and travel companies, but gives no preference and no exclusive powers to any of them.", UZ_ST),
], "uzbekistan.facts")
setv(uz, "faq_extra", [["Can Pakistani citizens get an Uzbekistan e-Visa?", "The official Uzbek e-Visa portal does not list Pakistan among its citizenships. Pakistani applicants deal with the Embassy of Uzbekistan in Islamabad, and should confirm the current requirements with its consular section."]], "uzbekistan.faq_extra")

# ---------------------------------------------------------------- Japan
JP = ("Embassy of Japan in Pakistan: information for visa applicants", "https://www.pk.emb-japan.go.jp/itpr_ja/VisaInfo.html")
jp = C["japan"]
setv(jp, "description", "Japan visa for Pakistani citizens: since 1 April 2024 applications go through VFS Global / Gerry's Visa. We prepare and check your file before you apply.", "japan.description")
setv(jp, "intro", "According to the Embassy of Japan in Pakistan, visa applications are made through VFS Global / Gerry's Visa and the embassy does not accept applications directly, except diplomatic and official visas. We prepare and check your file before you apply. The decision rests with the embassy, which does not give reasons for a refusal. Rules change, so always check the embassy's site.", "japan.intro")
setv(jp, "docs", ["Visa application form, one per applicant, signed in original and printed on one side of the paper",
                  "One recent photograph, 45 mm x 45 mm, with a light background (preferably white)",
                  "The original supporting documents listed in the embassy's 'Visa Requirements' file (linked on its visa page)",
                  "Where they apply to your trip: letter of guarantee, invitation letter, list of visa applicants, details of company or organisation, and itinerary in Japan"], "japan.docs")
setv(jp, "official_only", True, "japan.official_only")
setv(jp, "tier_note", "In Pakistan, Japan visa applications go through VFS Global / Gerry's Visa. We prepare and check your file and follow it up with you. The embassy decides.", "japan.tier_note")
setv(jp, "lead", "Japan visa applications in Pakistan go through VFS Global / Gerry's Visa. The embassy does not accept applications directly, except diplomatic and official visas.", "japan.lead")
setv(jp, "facts", [
    f("Since 1 April 2024, applications and enquiries go to VFS Global / Gerry's Visa. The embassy does not accept visa applications directly, except diplomatic and official visas.", JP),
    f("Each applicant prepares original documents. One application form is needed for each applicant, signed in original.", JP),
    f("One recent photograph is needed: 45 mm x 45 mm, light background, preferably white.", JP),
    f("The embassy gives the standard processing period as 6 working days at the earliest, from applying at VFS until the visa is issued. Incomplete documents take longer, and in some cases processing can take several months.", JP),
    f("Residents of Sindh and Balochistan apply at the Consulate General of Japan in Karachi.", JP),
    f("If a visa is refused, the reason is not given. A new application can be submitted 6 months after the refusal.", JP),
    f("The embassy does not issue visas on the same day of application.", JP),
], "japan.facts")
setv(jp, "faq_extra", [["Where do I apply for a Japan visa in Pakistan?", "According to the Embassy of Japan in Pakistan, applications go through VFS Global / Gerry's Visa, not the embassy desk. Residents of Sindh and Balochistan apply at the Consulate General in Karachi."]], "japan.faq_extra")

# ---------------------------------------------------------------- Azerbaijan
AZ = ("Embassy of Azerbaijan in Pakistan: ASAN Visa", "https://islamabad.mfa.gov.az/en/category/asan-viza")
AZ_T = ("Embassy of Azerbaijan in Pakistan: documents required for a tourist visa", "https://islamabad.mfa.gov.az/en/category/documents-required-for-visa-issuance/turizm-vizasi")
az = C["azerbaijan"]
setv(az, "description", "Azerbaijan visa for Pakistani travellers: ASAN e-Visa for eligible nationalities, or a tourist visa at the embassy in Islamabad. We prepare your file.", "azerbaijan.description")
setv(az, "intro", "Azerbaijan issues e-Visas through its official ASAN Visa system, but only to citizens of the countries on its official list, which is on evisa.gov.az. The Embassy of Azerbaijan in Islamabad also issues tourist visas and publishes the documents it requires. We prepare your file for the route that applies to you. Rules change, so always check the official sites.", "azerbaijan.intro")
setv(az, "docs", ["Visa application form, filled in on the Azerbaijan visa application website",
                  "Passport, original and copy, valid for at least three months after your planned departure from Azerbaijan",
                  "Two passport-size photos taken within the last 6 months, full face, white background",
                  "Hotel booking confirmation and copies of your inbound and outbound airline tickets",
                  "Medical or health insurance",
                  "Proof that you have enough funds to pay for your stay in Azerbaijan"], "azerbaijan.docs")
setv(az, "official_only", True, "azerbaijan.official_only")
setv(az, "tier_note", "Azerbaijan e-Visas are only issued to nationalities on the official ASAN list. Pakistani travellers can also apply for a tourist visa at the Embassy of Azerbaijan in Islamabad. We prepare your file for the route that applies.", "azerbaijan.tier_note")
setv(az, "lead", "Azerbaijan issues e-Visas only to citizens of countries on its official list. The Embassy of Azerbaijan in Islamabad also issues tourist visas and lists the documents it requires.", "azerbaijan.lead")
setv(az, "facts", [
    f("A single e-Visa issued through ASAN Visa within 3 business days allows a stay of up to 30 days. A multiple-entry e-Visa allows up to 90 days.", AZ),
    f("A single e-Visa can also be requested in an accelerated manner, within 3 hours, on the official evisa.gov.az website.", AZ),
    f("A single e-Visa is issued only to citizens of the countries on the official list on evisa.gov.az. Check that your passport is on that list before you pay.", AZ),
    f("The Embassy of Azerbaijan in Islamabad also issues tourist visas. It requires the visa application form, the passport (original and copy) valid for at least three months after departure, two photos, hotel booking, flight tickets, medical insurance and proof of sufficient funds.", AZ_T),
    f("The embassy accepts only complete applications and may ask for additional documents that are not on its list.", AZ_T),
], "azerbaijan.facts")
setv(az, "faq_extra", [["Do Pakistani citizens get the Azerbaijan e-Visa?", "A single e-Visa is only issued to citizens of the countries on the official list on evisa.gov.az. Check it for your passport. Otherwise, the Embassy of Azerbaijan in Islamabad issues tourist visas and publishes the documents it requires."]], "azerbaijan.faq_extra")

for w, a, b in log:
    print("-", w); print("   BEFORE:", str(a)[:140]); print("   AFTER: ", str(b)[:140])
print("\nchanges:", len(log))
if "--dry" in sys.argv:
    print("DRY RUN - nothing written"); sys.exit()
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
print("written", P)
