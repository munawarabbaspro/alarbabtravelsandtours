import io
P="build.py"; s=io.open(P,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s, a[:80]; s=s.replace(a,b,1)
rep('''    desc = (f"{c['name']} visa from Pakistan 2026: {len(c['docs_clean'])}-document checklist, how to apply, what the embassy checks and refusal reasons. "
            f"Free file check in Blue Area, Islamabad.")''','''    desc = f"{c['name']} visa from Pakistan 2026: {len(c['docs_clean'])}-document checklist, how to apply & refusal reasons. Free file check, Blue Area. WhatsApp {PHONE}"
    if len(desc) > 160:
        desc = f"{c['name']} visa from Pakistan 2026: {len(c['docs_clean'])} documents & how to apply. Free file check in Islamabad. WhatsApp {PHONE}"''')
rep('''"DTS-licensed travel agency in Islamabad. Visa consultancy for 50+ countries, cheap flights, Umrah packages & holiday deals. 98% visa approval."''',
    '''f"DTS-licensed travel agency in Blue Area, Islamabad since 2009: visas for 50+ countries, air tickets, Umrah & tours. Free assessment: {PHONE}"''')
rep('''"Visa consultant in Blue Area, Islamabad for Schengen, UK, USA, Canada, Australia, Dubai & Asia visas. 98% approval rate, free document check on WhatsApp."''',
    '''f"Visa consultant in Blue Area, Islamabad since 2009: Schengen, UK, USA, Canada, Dubai & Asia visas. Free document check on WhatsApp {PHONE}"''')
io.open(P,"w",encoding="utf-8").write(s); print("ok")
