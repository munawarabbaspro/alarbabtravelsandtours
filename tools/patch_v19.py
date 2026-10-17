# one-off patch: 5 evergreen guides (PAA topics), footer "popular visa pages" links, reviewed-by line, logo ImageObject
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

NEW = r'''
# ================================================================== evergreen guides (round 2)
def _ul(items, cls="checks"):
    return f'<ul class="{cls}">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

GUIDES2 = [
 dict(url="/guides/bank-statement-for-visa-from-pakistan", pid=UNS["cta"],
      h1="Bank statement for a visa from Pakistan", title="Bank Statement for Visa from Pakistan: What Embassies Check",
      lead="What visa officers look for in your bank statement and maintenance certificate, and the mistakes that cause refusals.",
      desc="Bank statement for a visa from Pakistan: what embassies check, how many months, maintenance certificate, sponsor statements and common mistakes that lead to refusal.",
      kw="bank statement for visa pakistan, bank maintenance certificate visa, how much bank balance for visa, sponsor bank statement visa",
      sections=[
       ("What the officer is checking", "<p>The bank statement answers one question: can you pay for this trip and still return to a stable life in Pakistan? Officers look at the pattern of your account, not only the closing balance.</p>" + _ul(["Regular income such as salary credits, business receipts or rent", "A balance that stays reasonably steady over the months", "Spending that matches your lifestyle and job", "Money for the trip that is clearly yours or your sponsor's"])),
       ("How many months and which documents", "<p>Most embassies ask for the last 6 months, signed and stamped by the bank, together with an account maintenance certificate. Some e-visas ask for 3 months. The country checklist on our site tells you what each embassy wants.</p>"),
       ("Mistakes that cause refusals", _ul(["<b>Sudden large deposits</b> just before applying with no explanation", "<b>Borrowed money</b> placed in the account for the application", "<b>Income that doesn't match</b> the salary slips, tax returns or employment letter", "<b>Unsigned or unstamped</b> statements and missing maintenance certificates"], "refuse")),
       ("If someone else is paying (sponsor)", "<p>A parent, spouse or child can sponsor your trip. Include their bank statement, income proof, CNIC, a sponsorship letter and proof of relationship such as the NADRA FRC or marriage certificate.</p>"),
       ("Is there a minimum balance?", "<p>Most embassies don't publish one fixed minimum for visit visas. The officer judges whether your funds cover the full trip for the number of days you plan to stay. Send us your statement and we tell you, free, whether it is strong enough.</p>")],
      faqs=[("How many months of bank statement are needed for a visa?", "Usually the last 6 months, signed and stamped, with an account maintenance certificate. Some e-visas accept 3 months."),
            ("Can I add money to my account before applying?", "Large unexplained deposits just before applying are a common refusal reason. If money comes in, keep proof of where it came from."),
            ("Can my father or husband sponsor my visa?", "Yes. Add their bank statement, income proof, CNIC, a sponsorship letter and proof of relationship (FRC or marriage certificate).")]),
 dict(url="/guides/visa-cover-letter-pakistan", pid=UNS["fr"],
      h1="How to write a visa cover letter (with template)", title="Visa Cover Letter Format for Pakistani Applicants (Template)",
      lead="A clear cover letter ties your documents together. Here is what to include and a simple template you can adapt.",
      desc="How to write a visa cover letter from Pakistan: what to include (purpose, itinerary, funding, ties to Pakistan), mistakes to avoid and a simple template to adapt.",
      kw="visa cover letter pakistan, cover letter for schengen visa, cover letter for uk visit visa, visa application letter format",
      sections=[
       ("What a good cover letter does", "<p>The officer reads your cover letter first. It should explain your trip in plain words and point to the documents that prove each claim.</p>" + _ul(["Who you are: name, passport number, job or business", "Why you are travelling and for how long", "A short day-by-day plan with cities and hotels", "Who pays for the trip", "Why you will come back: job, business, studies, family, property", "A list of the documents attached"])),
       ("Mistakes to avoid", _ul(["<b>Copy-pasted letters</b> that don't match your bookings", "<b>Dates that differ</b> from the flight, hotel and insurance", "<b>Over-long letters</b>: one page is enough", "<b>Claims without proof</b>, such as income not shown in the bank statement"], "refuse")),
       ("Simple template", "<p class=\"note\" style=\"white-space:pre-line\">To: The Visa Officer, Embassy of [Country], Islamabad\nSubject: Application for a [visit/tourist/business] visa — [Full name], Passport [number]\n\nI am [job title] at [company] since [year] / I run [business] since [year]. I plan to visit [country] from [date] to [date] for [purpose].\nMy plan: [city 1, dates, hotel] → [city 2, dates, hotel]. I will return to Pakistan on [date].\nThe trip will be paid by [me / sponsor name and relationship]; bank statements are attached.\nI will return because [job / business / studies / family / property in Pakistan].\nAttached: passport, photographs, bank statement and maintenance certificate, employment letter / business documents, tax returns, flight and hotel reservations, travel insurance.\n\nSincerely,\n[Name, phone, email, signature]</p>"),
       ("Need help?", "<p>We draft cover letters as part of every visa file, matched to your bookings and documents.</p>")],
      faqs=[("How long should a visa cover letter be?", "One page is enough. Keep it clear and factual and make sure every claim is backed by a document."),
            ("Should the cover letter be signed?", "Yes. Sign and date it, and include your contact details."),
            ("Do I need a separate letter for my family?", "One letter can cover a family travelling together; list each traveller and their relationship.")]),
 dict(url="/guides/visa-refused-what-to-do", pid=UNS["cta"],
      h1="Visa refused? What to do next", title="Visa Refused from Pakistan? What to Do Next | AL ARBAB",
      lead="A refusal is not the end. Read the reason, fix the weak points and reapply with a stronger file.",
      desc="Visa refused from Pakistan? How to read the refusal letter, common refusal reasons, when to reapply, and how to build a stronger file next time.",
      kw="visa refused what to do, schengen visa refusal reapply, uk visa refused reapply, visa rejection reasons pakistan",
      sections=[
       ("1. Read the refusal letter carefully", "<p>Most embassies state the reason, for example doubts about the purpose of the trip, insufficient funds or weak ties to Pakistan. That reason tells you exactly what to fix.</p>"),
       ("2. Fix the real problem, not just the paperwork", _ul(["<b>Funds doubted</b>: show a steadier bank history and explain any large deposits", "<b>Purpose unclear</b>: give a clear itinerary, bookings and a precise cover letter", "<b>Weak ties</b>: add proof of job, leave approval, business, property or family", "<b>Inconsistent documents</b>: make dates, names and figures match everywhere"], "checks")),
       ("3. Reapply or challenge?", "<p>Many refusals are best handled by reapplying with a stronger file. Some countries allow an appeal or review; the refusal letter explains the options and deadlines. Always declare previous refusals honestly on new applications.</p>"),
       ("4. Get a second opinion", "<p>Send us the refusal letter and your documents on WhatsApp. We tell you, free, what went wrong and whether to reapply now or wait.</p>")],
      faqs=[("Can I reapply after a visa refusal?", "Usually yes. Reapply once you have fixed the reason given in the refusal letter."),
            ("Does a refusal affect future visas?", "You must declare it on future applications. A refusal followed by a strong, honest application can still succeed."),
            ("Will the embassy refund the fee after refusal?", "Embassy fees are generally non-refundable, so it is worth fixing the file before you reapply.")]),
 dict(url="/guides/schengen-travel-insurance-from-pakistan", pid=UNS["it"],
      h1="Schengen travel insurance from Pakistan", title="Schengen Travel Insurance from Pakistan: €30,000 Rule",
      lead="Every Schengen visa application needs valid travel medical insurance. Here is what the policy must cover and how to get it quickly.",
      desc="Schengen travel insurance from Pakistan: €30,000 minimum medical cover, valid in all Schengen states for the whole stay, and how to get an embassy-verifiable policy in Islamabad.",
      kw="schengen travel insurance pakistan, travel insurance for schengen visa, 30000 euro travel insurance, travel insurance islamabad",
      sections=[
       ("What the policy must cover", _ul(["At least €30,000 medical cover, including emergency hospital treatment", "Repatriation for medical reasons", "Valid in all Schengen states", "Covering the full dates of your stay"])),
       ("Common mistakes", _ul(["<b>Dates too short</b> compared with the flight reservation", "<b>Cover only for one country</b> instead of the whole Schengen area", "<b>Policies that can't be verified</b> by the embassy"], "refuse")),
       ("Getting a policy in Islamabad", "<p>We issue verifiable policies from Pakistani insurers through our Blue Area office, usually within 15 minutes once we have your passport details and travel dates. See <a class=\"link\" href=\"/travel-insurance\">travel insurance</a>.</p>")],
      faqs=[("Is travel insurance mandatory for a Schengen visa?", "Yes. Schengen applications require travel medical insurance with at least €30,000 cover, valid in all Schengen states."),
            ("Can I buy insurance after the visa is issued?", "No. The insurance is part of the application and must be submitted with your file."),
            ("Does the policy need to match my travel dates?", "Yes. It must cover the full period of your stay shown in your bookings.")]),
 dict(url="/guides/how-to-check-visa-status", pid=UNS["dubai2"],
      h1="How to check your visa application status", title="How to Check Visa Status: VFS, US, UK, Canada | AL ARBAB",
      lead="Where to track your application after submission, depending on how you applied.",
      desc="How to check your visa application status from Pakistan: VFS Global and BLS tracking, the US CEAC status page, UK and Canada online accounts, and e-visa portals.",
      kw="visa status check, vfs visa tracking, us visa status check pakistan, schengen visa status check, e visa status check",
      sections=[
       ("Applied through a visa centre (VFS Global, BLS, etc.)", "<p>Use the tracking page of the visa centre where you submitted, with the reference number on your receipt. You will also get emails or SMS updates when your passport is ready for collection.</p>"),
       ("United States", "<p>Check the status of a non-immigrant visa on the official <a class=\"link\" href=\"https://ceac.state.gov/CEACStatTracker/Status.aspx\" target=\"_blank\" rel=\"noopener nofollow\">CEAC status page ↗</a> using your case number.</p>"),
       ("United Kingdom and Canada", "<p>UK applicants receive decision updates by email after submitting at the visa application centre. Canada applicants track progress in their IRCC online account.</p>"),
       ("E-visas", "<p>For e-visas (for example Malaysia, Turkey, Azerbaijan, Sri Lanka), log in to the same official portal you applied on. The country pages on our site link to each official portal.</p>"),
       ("We track it for you", "<p>When we file your application, we track it and message you on WhatsApp when there is an update.</p>")],
      faqs=[("Where do I find my reference number?", "On the receipt or confirmation email you received when you submitted the application or paid the fee."),
            ("What does 'administrative processing' mean for a US visa?", "Your case needs extra checks after the interview. Wait for an update on the CEAC page; it can take several weeks."),
            ("Can you check my visa status for me?", "Yes. If we filed your application, send us your name on WhatsApp and we check it.")]),
]

def build_guides2():
    cards = []
    for g in GUIDES2:
        secs = "".join(f'<div class="block" id="s{i}"><h2>{h}</h2>{body}</div>' for i, (h, body) in enumerate(g["sections"]))
        toc = "".join(f'<a href="#s{i}">{H.unescape(h)[:40]} <span>↓</span></a>' for i, (h, _) in enumerate(g["sections"]))
        main = f'<div class="stack">{secs}<div class="block" id="faqs"><h2>FAQs</h2>{faq_html(g["faqs"])}</div><p class="note">{REVIEWED}</p></div>'
        others = "".join(f'<a href="{o["url"]}">{e(o["h1"])} <span>→</span></a>' for o in GUIDES2 if o is not g)
        aside = f'<aside class="aside"><nav class="mini toc" aria-label="On this page"><h3>On this page</h3>{toc}</nav>{ctacard("visa file")}<nav class="mini"><h3>More guides</h3><a href="/guides">All guides <span>→</span></a>{others}</nav></aside>'
        ph = pagehead(f"Guide · Updated {UPDATED}", e(g["h1"]), e(g["lead"]), g["pid"], alt=g["h1"], actions=f'<a class="btn wa" href="{wa("Hi, I have a question: " + g["h1"])}" target="_blank" rel="noopener">💬 Ask an adviser</a>')
        body = shell("/guides", [("Home", "/"), ("Guides", "/guides"), (g["h1"], None)], ph, f'<div class="layout">{main}{aside}</div>{cta_band()}')
        art = {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["desc"], "image": U(g["pid"], 1200), "datePublished": TODAY, "dateModified": TODAY,
               "author": {"@type": "Organization", "name": NAME, "url": BASE + "/"}, "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + g["url"], "inLanguage": "en-PK"}
        title = g["title"] if len(g["title"]) <= 65 else g["title"][:62].rsplit(" ", 1)[0]
        page(g["url"], title, g["desc"], body, [crumbs_ld([("Home", "/"), ("Guides", "/guides"), (g["h1"], g["url"])]), art, faq_ld(g["faqs"])], g["kw"], image=U(g["pid"], 1200), priority="0.7")
        cards.append(f'<a class="vt" href="{g["url"]}"><h3>{e(g["h1"])}</h3><p>{e(g["lead"])}</p><span class="go">Read the guide →</span></a>')
    return cards

REVIEWED = f"Reviewed by the {NAME} visa team, Blue Area, Islamabad · Updated {UPDATED}. Rules change; we confirm the latest requirements for your case."

POPULAR = [("/countries/schengen", "Schengen visa from Pakistan"), ("/countries/united-kingdom", "UK visit visa"), ("/countries/united-states", "USA B1/B2 visa"),
           ("/countries/canada", "Canada visit visa"), ("/countries/middle-east/united-arab-emirates", "Dubai visa from Pakistan"), ("/countries/middle-east/saudi-arabia", "Saudi visit visa"),
           ("/countries/central-asia/turkey", "Turkey visa from Pakistan"), ("/countries/south-asia/malaysia", "Malaysia visa"), ("/countries/south-asia/thailand", "Thailand visa"),
           ("/countries/central-asia/azerbaijan", "Azerbaijan e-visa"), ("/umrah", "Umrah packages 2026"), ("/honeymoon-packages", "Honeymoon packages")]

# ================================================================== write'''
rep("\n# ================================================================== write", NEW)

# guides hub shows the new guides too
rep('''    cards = "".join(f'<a class="vt" href="{g[0]}"><h3>{e(g[1])}</h3><p>{e(g[2])}</p><span class="go">Read the guide →</span></a>' for g in guides)''',
    '''    cards = "".join(f'<a class="vt" href="{g[0]}"><h3>{e(g[1])}</h3><p>{e(g[2])}</p><span class="go">Read the guide →</span></a>' for g in guides) + "".join(build_guides2())''')

# footer: popular visa pages with descriptive anchors
rep('''    <div><h2 class="fh">Visa Destinations</h2><ul>{li(reg)}</ul></div>''', '''    <div><h2 class="fh">Visa Destinations</h2><ul>{li(reg)}</ul><h2 class="fh" style="margin-top:22px">Popular</h2><ul>{li(POPULAR)}</ul></div>''')

# reviewed-by line on country pages
rep('''<div class="block" id="faqs"><h2>{e(c["name"])} visa FAQs</h2>{faq_html(faqs)}</div>
</div>''', '''<div class="block" id="faqs"><h2>{e(c["name"])} visa FAQs</h2>{faq_html(faqs)}</div>
<p class="note">{REVIEWED}</p>
</div>''')

# logo as ImageObject with size (Google logo guidelines)
rep('''"name": NAME, "url": BASE + "/", "logo": LOGO,''', '''"name": NAME, "url": BASE + "/", "logo": {"@type": "ImageObject", "url": LOGO, "width": 513, "height": 412},''')
# llms.txt lists the new guides
rep('''              "/umrah", "/air-ticketing", "/eligibility-check", "/contact"]:''', '''              "/umrah", "/air-ticketing", "/eligibility-check", "/contact"] + [g["url"] for g in GUIDES2]:''')
io.open(P, "w", encoding="utf-8").write(s)
print("patched v19")
