"""v42 - China, South Korea, Hong Kong: official facts + FAQs (read 11 Nov 2026).

Sources read:
  - Embassy of China in Pakistan, Instruction for Chinese Visa Application (28 Apr 2025):
    https://pk.china-embassy.gov.cn/eng/lsfw/va/202504/t20250428_11606290.htm
  - Embassy of China in Pakistan, Notice on Online Submission of Arrival Card (28 Nov 2025):
    https://pk.china-embassy.gov.cn/eng/lsfw/va/202511/t20251128_11762876.htm
  - Embassy of China in Pakistan, Most Common Reasons for the Returned Visa Application:
    https://pk.china-embassy.gov.cn/eng/lsfw/va/202504/t20250428_11606302.htm
  - Embassy of the Republic of Korea in Pakistan, Visa Requirements:
    https://overseas.mofa.go.kr/pk-en/wpge/m_3159/contents.do
  - Hong Kong Immigration Department, Visit visa / entry permit requirements:
    https://www.immd.gov.hk/eng/services/visas/visit-transit/visit-visa-entry-permit.html
No fees or amounts are added.

  py tools/patch_v42.py --dry | py tools/patch_v42.py   (idempotent)
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

# ---------------------------------------------------------------- China
CN = ("Embassy of China in Pakistan: Instruction for Chinese Visa Application", "https://pk.china-embassy.gov.cn/eng/lsfw/va/202504/t20250428_11606290.htm")
CN_ARR = ("Embassy of China in Pakistan: Notice on Online Submission of Arrival Card", "https://pk.china-embassy.gov.cn/eng/lsfw/va/202511/t20251128_11762876.htm")
CN_RET = ("Embassy of China in Pakistan: Most common reasons for returned visa applications", "https://pk.china-embassy.gov.cn/eng/lsfw/va/202504/t20250428_11606302.htm")
add_facts("china", [
    ("Fill the online Visa Application Form on bio.visaforchina.cn and upload all documents. After the 'Online Visa Approved' email, submit your passport, the Visa Application Certificate and original documents at Gerry's Center in Islamabad, Karachi or Lahore.", CN),
    ("The Embassy in Islamabad takes applicants who permanently live in Islamabad, Rawalpindi and Punjab (the Consulate General in Lahore does not accept visa applications currently). The Consulate General in Karachi takes Sindh and Balochistan.", CN),
    ("The tourist (L) visa is issued to tourists visiting China in a group of at least 5 people, with an Invitation Letter for Tourist Group from the authorised tourism office in China.", CN),
    ("The embassy generally needs 4 working days to process an application and does not provide a fast service. Fingerprints are collected at Gerry's Center (with some exemptions).", CN),
    ("Since 20 November 2025, foreign nationals can submit the China arrival card online before travel, on the National Immigration Administration website or app.", CN_ARR),
    ("Common reasons the embassy returns business (M) visa files: fake or incomplete invitation letters, unreadable police character certificates, unverifiable proof of funds, and errors on the form such as a mismatched name or passport number.", CN_RET),
])
add_faqs("china", [
    ("How do I apply for a China visa from Pakistan?",
     "Fill the online form on bio.visaforchina.cn and upload your documents. When you receive the 'Online Visa Approved' email, take your passport, the Visa Application Certificate and the originals to Gerry's Center in Islamabad, Karachi or Lahore. We prepare and check the file before you upload it."),
    ("Can I get a China tourist visa alone?",
     "The Embassy of China says the tourist (L) visa is issued to tourists visiting in a group of at least 5 people, with a group invitation from the authorised tourism office in China. Individual travellers usually go on another category, such as business with an invitation; we check which fits your trip."),
    ("How long does a China visa take in Pakistan?",
     "The embassy generally needs 4 working days and does not offer a fast service. Processing can vary case by case."),
    ("Why do China visa files get returned?",
     "The embassy lists fake or incomplete invitation letters, unreadable police character certificates, unverifiable proof of funds and form errors such as a mismatched name or passport number. We check these before submission."),
])

# ---------------------------------------------------------------- South Korea
KR = ("Embassy of the Republic of Korea in Pakistan: Visa Requirements", "https://overseas.mofa.go.kr/pk-en/wpge/m_3159/contents.do")
add_facts("south-korea", [
    ("Pakistani nationals with an ordinary passport must obtain a visa to enter Korea. Applicants must appear in person to submit their own application.", KR),
    ("The embassy accepts applications Monday to Friday, 9:30 to 11:30 (hours can change). Processing takes a minimum of 8 weeks after the application is received.", KR),
    ("For short-term visits (business C-3-4, or family visit and conference C-3-1), the Korean inviter provides an original invitation letter and guarantee letter notarized in Korea.", KR),
    ("Applicants submit a passport valid at least six months, one application form filled in personally, one recent colour photo and the documents for their visa category, such as a bank statement for the previous six months.", KR),
    ("The embassy does not have any obligation to explain the reason for a refusal.", KR),
])
add_faqs("south-korea", [
    ("Can someone else submit my Korea visa application?",
     "No. The Embassy of Korea in Pakistan says applicants must appear in person to submit their own application. We prepare and check your file; you submit it at the embassy."),
    ("How long does a Korea visa take from Pakistan?",
     "The embassy says a minimum of 8 weeks after it receives the application, so apply well before your travel date."),
    ("Do I need an invitation for a Korea visit visa?",
     "For short-term business, family visit or conference visas, the embassy asks for an original invitation letter and guarantee letter from the Korean inviter, notarized in Korea."),
    ("Will the Korean embassy tell me why my visa was refused?",
     "No. The embassy says it has no obligation to explain the reason for a refusal, so the file should be checked carefully before you apply."),
])

# ---------------------------------------------------------------- Hong Kong
HK = ("Hong Kong Immigration Department: visit visa / entry permit requirements", "https://www.immd.gov.hk/eng/services/visas/visit-transit/visit-visa-entry-permit.html")
add_facts("hong-kong", [
    ("Pakistan is on the Hong Kong Immigration Department's list of nationalities that need a visa. All Pakistani nationals except diplomatic and official passport holders need a valid visa, including transit passengers who stay airside.", HK),
    ("You can apply at the nearest Chinese diplomatic or consular mission (some missions pass applications to the Chinese Visa Application Service Center), or apply to the Immigration Department directly by post or through a local sponsor in Hong Kong.", HK),
    ("Visitors must have adequate funds for their stay without working and hold onward or return tickets (unless in transit to the Chinese Mainland or Macao).", HK),
])
add_faqs("hong-kong", [
    ("Do Pakistanis need a visa for Hong Kong?",
     "Yes. The Hong Kong Immigration Department lists Pakistan as visa required, even for transit passengers who stay airside. Only diplomatic and official passport holders are visa-free."),
    ("Where do Pakistanis apply for a Hong Kong visa?",
     "At the Chinese mission or its Chinese Visa Application Service Center, or directly to the Hong Kong Immigration Department by post or through a local sponsor in Hong Kong. We check which route fits your trip and prepare the file."),
    ("Do I need a visa to transit through Hong Kong airport?",
     "Yes. The Immigration Department says the visa requirement for Pakistani nationals also applies to transit passengers who stay airside."),
])
hk = C["hong-kong"]
ni = hk["intro"].replace("We assist Pakistani citizens with online visa applications and thorough documentation review for smooth entry.",
                         "We prepare Hong Kong visa files for Pakistani citizens, through the Chinese visa centre or a Hong Kong sponsor, with a thorough documentation review.")
if ni != hk["intro"]:
    log.append(("hong-kong.intro", 1)); hk["intro"] = ni

if "--dry" in sys.argv:
    print(log)
else:
    open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print(log, "written")
