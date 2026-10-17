import io,re
P="build.py"; s=io.open(P,encoding="utf-8").read()
def rep(a,b,c=1):
    global s
    assert a in s, a[:80]; s=s.replace(a,b,c)

# 1. replace shared checks/refusal blocks with a compact link block + disclaimer
a=s.index('<div class="block" id="checks">'); b=s.index('{src_block}',a)
s=s[:a]+'''<div class="block" id="checks"><h2>Before you apply for the {e(c["name"])} visa</h2><p>Officers judge the same things on every file: purpose of the trip, enough funds, reasons to return and consistent documents. Read our short guides, then send your file for a free check.</p><div class="chipsrow" style="margin-top:12px"><a href="/guides/bank-statement-for-visa-from-pakistan">Bank statement rules</a><a href="/guides/visa-cover-letter-pakistan">Cover letter template</a><a href="/guides/visa-refused-what-to-do">If a visa is refused</a><a href="/guides/visa-documents-explained">Documents explained</a></div></div>
'''+s[b:]
rep('''("checks", "What the embassy checks"), ("refusal", "Refusal reasons")''','''("checks", "Before you apply")''')
# 2. drop two templated FAQs
a=s.index('             (f"Is it easy to get a {c[\'name\']} visa from Pakistan?"'); b=s.index('\n',s.index('How much bank balance is required for a',a))
s=s[:a].rstrip().rstrip(',')+']'+s[b:]
# 3. country-specific documents + disclaimer
rep('''    places = "".join(f"<span>📍 {e(p)}</span>" for p in c["popularPlaces"])''','''    common = {}
    for _o in BY_REGION.get(c["region"], []):
        for _d in _o["docs_clean"]:
            common[_d.lower()] = common.get(_d.lower(), 0) + 1
    _n = max(1, len(BY_REGION.get(c["region"], [])))
    only_here = [d for d in c["docs_clean"] if common.get(d.lower(), 0) <= max(1, _n // 4)]
    only_block = (f'<div class="block" id="specific"><h2>What is specific to {e(c["name"])}</h2><p>Most {e(REGIONS[c["region"]]["name"])} checklists share the basics. These items are particular to {e(c["name"])}:</p><ul class="docs">' + "".join(f"<li>{e(d)}</li>" for d in only_here[:6]) + "</ul></div>") if only_here else ""
    places = "".join(f"<span>📍 {e(p)}</span>" for p in c["popularPlaces"])''')
rep('''<div class="block" id="documents"><h2>Required documents for''','''{only_block}
<div class="block" id="documents"><h2>Required documents for''')
rep('''<p class="note">{REVIEWED}</p>
</div>\'\'\'
    vlinks''','''<p class="note">{REVIEWED} {NAME} is licensed by the Department of Tourist Services (DTS). We are not an embassy or government office, and no agency can guarantee a visa: the decision is made by the embassy.</p>
</div>\'\'\'
    vlinks''')
io.open(P,"w",encoding="utf-8").write(s); print("ok")
