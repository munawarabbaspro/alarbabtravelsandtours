# one-off patch: competitor-inspired upgrades
#  - country pages: documents grouped by category, "what the embassy checks", visa route fact
#  - data-driven testimonials (data/reviews.json) and team (data/team.json): shown only when real data exists
import io, json, os
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

rep('''PAA_AGENCY = [''', '''DOC_GROUPS = [
 ("Identity & family", ["passport", "cnic", "frc", "family registration", "marriage", "birth certificate", "photo", "nadra", "id card"]),
 ("Money & income", ["bank", "statement", "maintenance", "tax", "ntn", "fbr", "salary", "income", "funds", "property", "asset", "sponsor"]),
 ("Job or business", ["employment", "employer", "job", "leave", "noc", "business", "chamber", "secp", "company", "letterhead", "occupation", "student"]),
 ("Trip & bookings", ["flight", "ticket", "hotel", "accommodation", "lodging", "itinerary", "reservation", "invitation", "cover letter", "insurance", "form", "application"]),
]

def group_docs(docs):
    out = {g: [] for g, _ in DOC_GROUPS}
    out["Other"] = []
    for d in docs:
        dl = d.lower()
        for g, keys in DOC_GROUPS:
            if any(k in dl for k in keys):
                out[g].append(d)
                break
        else:
            out["Other"].append(d)
    return [(g, xs) for g, xs in out.items() if xs]

def visa_route(c):
    t = (c["intro"] + " " + c["description"] + " " + " ".join(c["docs_clean"])).lower()
    if "visa on arrival" in t or "on-arrival" in t:
        return "Visa on arrival / e-visa"
    if "eta" in t.split() or "electronic travel authori" in t:
        return "Online ETA"
    if "e-visa" in t or "evisa" in t or "e visa" in t:
        return "Online e-visa"
    if c["region"] == "schengen":
        return "Schengen visa (embassy / visa centre)"
    return "Embassy / visa centre"

def embassy_checks(c):
    n = e(c["name"])
    return [("Purpose of the trip", f"A clear reason to visit {n} that matches your bookings, cover letter and the length of stay."),
            ("Enough money", "A bank history that can pay for the whole trip, with a steady balance and a source of income the embassy can see."),
            ("Reasons to come back", "Your job, business, studies, family or property in Pakistan that make it clear you will return."),
            ("Travel history", "Previous visas and trips, especially to the UK, USA, Schengen or the Gulf, strengthen a first application."),
            ("Consistent documents", "Names, dates and figures that match across the form, bank statement, letters and reservations.")]

REVIEWS = json.load(open(os.path.join(ROOT, "data", "reviews.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "data", "reviews.json")) else []
TEAM = json.load(open(os.path.join(ROOT, "data", "team.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "data", "team.json")) else []

def reviews_block(limit=6):
    """Real client reviews from data/reviews.json; renders nothing until that file has entries."""
    if not REVIEWS:
        return ""
    cards = "".join(f'<figure class="quote"><blockquote>“{e(r["text"])}”</blockquote><figcaption><b>{e(r["name"])}</b>{" · " + e(r["visa"]) if r.get("visa") else ""}{" · " + e(r["date"]) if r.get("date") else ""}</figcaption></figure>' for r in REVIEWS[:limit])
    return sec("What our clients say", "Reviews from clients whose visas, tickets and Umrah we handled.", f'<div class="cards">{cards}</div>')

PAA_AGENCY = [''')

# country page: grouped documents + embassy checks + route fact
rep('''<div class="block" id="documents"><h2>Required documents for {e(c["name"])} visa</h2><ul class="docs">{docs}</ul>''',
    '''<div class="block" id="documents"><h2>Required documents for {e(c["name"])} visa</h2>{grouped}''')
rep('''    docs = "".join(f"<li>{e(x)}</li>" for x in c["docs_clean"])
    places''', '''    docs = "".join(f"<li>{e(x)}</li>" for x in c["docs_clean"])
    grouped = "".join(f'<h3>{e(g)}</h3><ul class="docs">' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul>" for g, xs in group_docs(c["docs_clean"]))
    checks = "".join(f"<li><b>{e(a)}</b><span>{b}</span></li>" for a, b in embassy_checks(c))
    places''')
rep('''<div class="block" id="refusal"><h2>Common reasons {e(c["name"])} visas get refused</h2>''',
    '''<div class="block" id="checks"><h2>What the {e(c["name"])} embassy looks for</h2><p>Every visa officer is answering the same questions about your file. Make sure your documents answer them clearly.</p><ul class="checks2">{checks}</ul></div>
<div class="block" id="refusal"><h2>Common reasons {e(c["name"])} visas get refused</h2>''')
rep('''("process", "How to apply"), ("refusal", "Refusal reasons")''', '''("process", "How to apply"), ("checks", "What the embassy checks"), ("refusal", "Refusal reasons")''')
rep('''    facts = f'<div class="facts"><div><small>Documents</small><b>{len(c["docs_clean"])} on the checklist</b></div>''',
    '''    facts = f'<div class="facts"><div><small>How you apply</small><b>{e(visa_route(c))}</b></div><div><small>Documents</small><b>{len(c["docs_clean"])} on the checklist</b></div>''')

# reviews on home + city pages (only when data exists)
rep('''{sec("Frequently asked questions", "", faq_html(FAQ_GENERAL + PAA_AGENCY))}''', '''{reviews_block()}
{sec("Frequently asked questions", "", faq_html(FAQ_GENERAL + PAA_AGENCY))}''')

# team section on about page (only when data exists)
rep('''{sec("A legacy of trust", "", f'<div class="timeline">{tl}</div>')}''', '''{sec("A legacy of trust", "", f'<div class="timeline">{tl}</div>')}
{sec("Meet our visa consultants", "The people who check your file.", '<div class="cards">' + "".join(f'<figure class="quote">{(chr(60) + "img src=" + chr(34) + m["photo"] + chr(34) + " alt=" + chr(34) + e(m["name"]) + chr(34) + " width=" + chr(34) + "96" + chr(34) + " height=" + chr(34) + "96" + chr(34) + " loading=" + chr(34) + "lazy" + chr(34) + " class=" + chr(34) + "avatar" + chr(34) + ">") if m.get("photo") else ""}<figcaption><b>{e(m["name"])}</b>{e(m.get("role", ""))}</figcaption><blockquote>{e(m.get("bio", ""))}</blockquote></figure>' for m in TEAM) + "</div>") if TEAM else ""}''')

io.open(P, "w", encoding="utf-8").write(s)
for fn in ("reviews.json", "team.json"):
    p = os.path.join("data", fn)
    if not os.path.exists(p):
        io.open(p, "w", encoding="utf-8").write("[]\n")
print("patched v13")
