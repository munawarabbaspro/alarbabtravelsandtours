# one-off patch from SERP research: quick-answer box (AI Overview / featured snippet), per-country PAA, contact-number title
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# per-country "People also ask" answers (no fees, no promises)
rep('''    faqs += COUNTRY_PAA.get(c["slug"], [])''', '''    faqs += COUNTRY_PAA.get(c["slug"], [])
    route = visa_route(c)
    faqs += [(f"Is the {c['name']} visa open for Pakistani passport holders?", f"Yes. We are handling {c['name']} applications for Pakistani passport holders from our Islamabad office ({route.lower()}). Rules can change at short notice, so message us on WhatsApp to confirm the current position before you book anything."),
             (f"Is it easy to get a {c['name']} visa from Pakistan?", f"It depends on your file. Applicants with a steady bank history, a clear reason for the trip, strong ties to Pakistan and some previous travel usually do well. Our free file check tells you where your {c['name']} application is weak before you apply."),
             (f"How much bank balance is required for a {c['name']} visa?", "Most embassies don't publish one fixed minimum for visit visas. The officer checks that your balance can cover the whole trip and that the money comes from a regular, explainable income. Send us your statement and we assess it for free.")]''')

# quick-answer box at the top of each country page (short, factual, quotable)
rep('''<div class="block" id="about"><h2>{e(c["name"])} visa services in Islamabad</h2><p>{e(c["intro"])}</p></div>''',
    '''<div class="block answer" id="answer"><h2>{e(c["name"])} visa from Pakistan: quick answer</h2><p>{quick}</p></div>
<div class="block" id="about"><h2>{e(c["name"])} visa services in Islamabad</h2><p>{e(c["intro"])}</p></div>''')
rep('''    checks = "".join(f"<li><b>{e(a)}</b><span>{b}</span></li>" for a, b in embassy_checks(c))''', '''    checks = "".join(f"<li><b>{e(a)}</b><span>{b}</span></li>" for a, b in embassy_checks(c))
    key_docs = [d.split("(")[0].strip().rstrip(",;") for d in c["docs_clean"][:4]]
    quick = e(f"Pakistani passport holders need a visa for {c['name']}. You apply through {visa_route(c).lower()}, and processing typically takes {proc.lower().replace('typically ', '').rstrip('.')}. "
              f"The checklist has {len(c['docs_clean'])} documents, including {', '.join(key_docs[:-1]).lower()} and {key_docs[-1].lower()}. ") + \\
            f'{NAME} prepares the full file from Blue Area, Islamabad; <a class="link" href="{wa("Hi, I need help with a " + c["name"] + " visa.")}" target="_blank" rel="noopener">start with a free WhatsApp check</a>.'
''')
rep('''    proc = vv["processingTime"] if vv else "Embassy dependent"
    faqs = [''', '''    proc = vv["processingTime"] if vv else "Embassy dependent"
    faqs = [''')  # (proc is defined before quick-answer uses it; no-op anchor check)

# contact page: people search for the contact number
rep('''    page("/contact", "Contact Visa Consultant Islamabad | AL ARBAB Blue Area",''', '''    page("/contact", "AL ARBAB Travel Islamabad Contact Number & WhatsApp",''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v14")
