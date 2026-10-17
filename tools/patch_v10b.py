# one-off patch (part 2): guides and llms.txt without fees
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

a = s.index('    url = "/guides/visa-fees-for-pakistani-passport"')
b = s.index("    # 2. schengen requirements")
s = s[:a] + '''    url = "/guides/visa-requirements-for-pakistani-passport"
    blocks = ""
    for r in DATA["regions"]:
        cs = [c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]]
        if not cs:
            continue
        vv = visit_visa(r["slug"])
        rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{len(c["docs_clean"])} documents</td><td>{e(short_time(vv["processingTime"]) if vv else "—")}</td><td>{"Yes" if any("polio" in d.lower() for d in c["docs_clean"]) else "—"}</td></tr>' for c in cs)
        blocks += f'<div class="block" id="{r["slug"]}"><h2>{e(r["name"])}</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Country</th><th>Checklist</th><th>Typical processing</th><th>Polio card</th></tr></thead><tbody>{rows}</tbody></table></div></div>'
    special = "".join(f'<tr><td><a class="link" href="/countries/{rs}">{e(REGIONS[rs]["name"])}</a></td><td>{e(REGIONS[rs]["visas"][0]["name"])}</td><td>{e(short_time(REGIONS[rs]["visas"][0]["processingTime"]))}</td></tr>' for rs in ("united-kingdom", "united-states", "canada", "australia"))
    faqs = [("Why don't you list visa fees?", "Embassy charges change often with exchange rates and policy, so a published number would soon be wrong. Message us on WhatsApp and we confirm the current all-in cost for your case."),
            ("Which documents do almost all countries ask for?", "A valid passport, photographs, a bank statement and confirmed flight and hotel bookings appear on almost every checklist. See our documents guide for what each one means."),
            ("How long does processing take?", "It ranges from a few days for e-visas to several weeks for Schengen, UK and US visas. Apply early, especially before summer and Eid travel.")]
    toc = "".join(f'<a href="#{r["slug"]}">{e(r["name"])} <span>↓</span></a>' for r in DATA["regions"] if [c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]])
    main = f\'\'\'<div class="stack"><div class="block"><h2>How to use this list</h2><p>This page compares visa requirements for Pakistani passport holders across the {len(COUNTRIES)} destinations we handle from Islamabad, grouped by region: how many documents each checklist has, typical processing time, and whether a polio vaccination card is listed. Click a country for its full document list.</p><p class="note" style="margin-top:12px">Updated {UPDATED}. Rules change; we confirm the latest checklist for your case on WhatsApp.</p></div>
<div class="block"><h2>UK, USA, Canada &amp; Australia</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Destination</th><th>Main visit visa</th><th>Typical processing</th></tr></thead><tbody>{special}</tbody></table></div></div>
{blocks}<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>\'\'\'
    guides.append((url, "Visa requirements for Pakistani passport holders 2026", f"Compare document checklists and processing times for {len(COUNTRIES)} countries, grouped by region.",
                   f"Visa Requirements for Pakistani Passport 2026 ({len(COUNTRIES)} Countries)",
                   f"Visa requirements for Pakistani passport holders in 2026: compare document checklists and processing times for {len(COUNTRIES)} countries including Schengen, UK, USA, Dubai and Asia.",
                   main, toc, faqs, UNS["fr"], "visa requirements for pakistani passport, visa for pakistani, which countries visa pakistan, visa processing time pakistan"))
''' + s[b:]

rep('''<td>{e(short_fee(c["fee"]))}</td><td>{e(route.get(c["name"], "VFS / BLS / Gerry\\'s (by embassy)"))}</td>''', '''<td>{e(route.get(c["name"], "VFS / BLS / Gerry\\'s (by embassy)"))}</td>''')
rep('''<thead><tr><th>Country</th><th>Fee</th><th>Where you apply</th><th>Top attraction</th></tr></thead>''', '''<thead><tr><th>Country</th><th>Where you apply</th><th>Top attraction</th></tr></thead>''')
rep('''"Documents, fees and the application route for all 29 Schengen countries, in one place."''', '''"Documents, application route and process for all 29 Schengen countries, in one place."''')
rep('''"Schengen visa requirements for Pakistanis in 2026: document checklist, €90 fee, where to apply (VFS, BLS, Gerry's) and a comparison of all 29 countries."''',
    '''"Schengen visa requirements for Pakistanis in 2026: document checklist, €30,000 insurance rule, where to apply (VFS, BLS, Gerry's) and all 29 countries compared."''')
rep('''"Plain-language guides built from the checklists we use every day in our Blue Area office: fees, documents and the Schengen process."''',
    '''"Plain-language guides built from the checklists we use every day in our Blue Area office: requirements, documents and the Schengen process."''')
rep('''"Visa guides for Pakistani travellers: visa fees for 86 countries, Schengen requirements from Pakistan, and visa documents explained, from AL ARBAB in Islamabad."''',
    '''"Visa guides for Pakistani travellers: requirements for 86 countries, Schengen requirements from Pakistan, and visa documents explained, from AL ARBAB in Islamabad."''')
rep('''"/guides/visa-fees-for-pakistani-passport", "/guides/schengen''', '''"/guides/visa-requirements-for-pakistani-passport", "/guides/schengen''')
rep('''[f"- [{c['name']} visa]({BASE}{c['url']}): fee {c['fee']}" for c in COUNTRIES.values()]''', '''[f"- [{c['name']} visa]({BASE}{c['url']}): {len(c['docs_clean'])} documents on the checklist" for c in COUNTRIES.values()]''')
io.open(P, "w", encoding="utf-8").write(s)
print("patched v10b")
