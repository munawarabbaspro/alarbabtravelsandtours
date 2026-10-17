# one-off patch: remove every IATA claim; use DTS (Department of Tourist Services) licence instead
import io, re
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

PAIRS = [
 ("Pakistan's #1 IATA Authorized Agency | 98% Visa Approval", "DTS Licensed Travel Agency | 98% Visa Approval"),
 ("Pakistan's #1 IATA authorized travel agency in Islamabad", "DTS-licensed travel agency in Islamabad"),
 ("IATA-authorized travel agency in Blue Area, Islamabad:", "DTS-licensed travel agency in Blue Area, Islamabad:"),
 ("{NAME} is an IATA-authorized travel partner with direct access to real-time fares from", "{NAME} is a DTS-licensed travel agency with access to real-time fares from"),
 ("IATA-authorized global ticketing", "global air ticketing"),
 ("arranged by one IATA-authorized team", "arranged by one team"),
 ("from one IATA-authorized office in Eagle Plaza", "from one DTS-licensed office in Eagle Plaza"),
 ("booked by Islamabad's IATA-authorized agency", "booked by our Blue Area office"),
 ("through authorized GDS / IATA systems", "through authorized airline booking systems"),
 ("<div><b>IATA</b><small>Authorized agent</small></div>", "<div><b>DTS</b><small>Licensed agency</small></div>"),
 ("iata travel agent pakistan", "licensed travel agent pakistan"),
 ("iata travel agent islamabad", "licensed travel agent islamabad"),
 ("As an IATA-certified agency, we bridge", "As a licensed travel agency, we bridge"),
 ("IATA-authorized tickets<br>at the best fares", "Air tickets on every<br>major airline"),
 ("Air Ticketing Agency Islamabad | Cheap Flights IATA", "Air Ticketing Agency Islamabad | Cheap Flights | AL ARBAB"),
 ("IATA Authorized Agent · Islamabad, Pakistan", "DTS Licensed Travel Agency · Islamabad, Pakistan"),
 ("<span>IATA Authorized</span>", "<span>DTS Licensed</span>"),
 ("(IATA Authorized Travel Agency, Islamabad)", "(DTS-licensed travel agency, Islamabad)"),
 ("IATA-authorized travel agency and visa consultancy", "DTS-licensed travel agency and visa consultancy"),
 ("Flight tickets are issued under the standard regulations of IATA and the respective operating airlines.", "Flight tickets are issued under the fare rules of the respective operating airlines."),
 ("Check that the agency is IATA-authorized, has a real office", "Check that the agency is licensed by the Department of Tourist Services (DTS), has a real office"),
 ("since 2009 and is IATA-authorized.", "since 2009 and is licensed by the Department of Tourist Services (DTS)."),
 ("with visas, IATA ticketing and Umrah", "with visas, air tickets and Umrah"),
 ("one IATA-authorized desk in Blue Area", "one desk in Blue Area"),
 ("with Pakistan's IATA-authorized visa consultants", "with DTS-licensed visa consultants"),
 ("As an IATA-authorized agency we see live fares on", "We see live fares on"),
 ("IATA-authorized agent, instant e-tickets", "Licensed agency, instant e-tickets"),
 ("IATA-accredited experts for", "Experts for"),
 ("from an IATA agent", "from a DTS-licensed agency"),
 ("IATA direct lowest fares", "Competitive fares worldwide"),
 ("<span>IATA authorized since 2015</span>", "<span>DTS licensed</span>"),
 ("<span>IATA Authorized Travel Agent</span>", "<span>DTS Licensed Travel Agency</span>"),
]
for a, b in PAIRS:
    rep(a, b, s.count(a))

# timeline: drop the IATA accreditation entry
s = re.sub(r'\("2015", "IATA Accreditation", "[^"]*"\), ', "", s)

# FAQs about IATA -> licence
s = re.sub(r'\("Is AL ARBAB TRAVEL AND TOURS an IATA-authorized travel agency\?", "[^"]*"\)',
           '("Is AL ARBAB TRAVEL AND TOURS a licensed travel agency?", "Yes. We are licensed by the Department of Tourist Services (DTS), Government of Pakistan, and have served travellers from our office in Eagle Plaza, Blue Area, Islamabad since 2009.")', s)
s = re.sub(r'\("Are you IATA authorized\?", "[^"]*"\)',
           '("Are you a licensed travel agency?", "Yes. We are licensed by the Department of Tourist Services (DTS), Government of Pakistan.")', s)

# remaining phrasing variants (feature cards, air page, schema, SEO paragraphs)
for pat, new in [(r"IATA-authorized ticketing", "Air ticketing"), (r"IATA-authorized tickets", "Air tickets"), (r"IATA-authorized airfares", "Competitive airfares"),
                 (r"IATA-authorized air ticketing", "Air ticketing"), (r"IATA-authorized agent with", "DTS-licensed agency with"),
                 (r'\("✅", "IATA [Aa]uthori[sz]ed", "[^"]*"\)', '("✅", "DTS licensed", "Licensed by the Department of Tourist Services, Government of Pakistan.")'),
                 (r'"IATA Authorized", "Officially accredited ticketing agency\."', '"Licensed agency", "Licensed by the Department of Tourist Services (DTS)."'),
                 (r"stands out as a premier IATA-authorized travel agent\. This status is not just a badge; it signifies our commitment to professional standards, financial security, and direct relationships with over 300 airlines worldwide\.",
                  "stands out as a licensed travel agent with access to fares on over 300 airlines worldwide."),
                 (r"stands out as a premier IATA-authorized travel agent\. This status signifies our commitment to professional standards, financial security, and direct relationships with over 300 airlines worldwide\.",
                  "stands out as a licensed travel agent with access to fares on over 300 airlines worldwide.")]:
    s = re.sub(pat, new, s)

# data-level cleanup (old-site texts) right after the fee sanitizer
rep('''DATA["faqSchengenGeneral"] = clean_faqs(DATA["faqSchengenGeneral"])''', '''DATA["faqSchengenGeneral"] = clean_faqs(DATA["faqSchengenGeneral"])

def no_iata(x):
    """Old-site texts called the agency IATA-authorized; replace with neutral / DTS wording."""
    if isinstance(x, str):
        x = re.sub(r"\\bIATA[- ](?:authori[sz]ed|accredited|certified|direct)\\s*", "", x, flags=re.I)
        x = re.sub(r"\\b(?:full )?IATA (?:accreditation|certification)\\b", "a DTS licence", x, flags=re.I)
        x = re.sub(r"\\s*\\bIATA\\b\\s*", " ", x).replace("  ", " ")
        return x
    if isinstance(x, list):
        return [no_iata(i) for i in x]
    if isinstance(x, dict):
        return {k: (v if k == "iata" else no_iata(v)) for k, v in x.items()}
    return x

for _k in ("faqSchengenGeneral", "faqAir"):
    DATA[_k] = [f for f in DATA[_k] if "iata" not in f["q"].lower()]
for _k in ("services", "countries", "regions", "faqSchengenGeneral", "faqAir", "airlines", "packages", "visaDest", "heroDest"):
    DATA[_k] = no_iata(DATA[_k])''')

# schema: licence as a credential
rep('''            "sameAs": [s[1] for s in SOCIAL],''', '''            "sameAs": [s[1] for s in SOCIAL],
            "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "license", "name": "Travel agency licence",
                              "recognizedBy": {"@type": "GovernmentOrganization", "name": "Department of Tourist Services (DTS), Government of Pakistan"}},''')

# build guard: fail if any IATA claim reaches the output
rep('''def write_all():''', '''def write_all():
    bad = [u for u, (h, _, _) in PAGES.items() if re.search(r"\\bIATA\\b", re.sub(r"<script[^>]*>.*?</script>", "", h, flags=re.S))]
    assert not bad, f"IATA still mentioned on: {bad[:10]}"''')

io.open(P, "w", encoding="utf-8").write(s)
left = [m.group(0) for m in re.finditer(r".{0,40}IATA.{0,40}", s) if "def no_iata" not in m.group(0)]
print("patched v12; IATA left in build.py:", len(left))
for l in left[:20]:
    print("  ", l)
