# one-off patch: answer Google "People also ask" questions found in competitor research (no fees/prices)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# generic PAA for "travel agency in islamabad" / "visa consultant in islamabad"
rep('''FAQ_VISA = [''', '''PAA_AGENCY = [
 ("How do I choose the best travel agency or visa consultant in Islamabad?", "Check that the agency is IATA-authorized, has a real office you can visit, shows its Google reviews openly, gives you a written document checklist, and quotes the full cost before you pay. AL ARBAB TRAVEL AND TOURS has been in Eagle Plaza, Blue Area since 2009 and is IATA-authorized."),
 ("How much does a travel agency charge for a visa?", "Service charges depend on the country, visa type and how much work your file needs. We quote the full cost on WhatsApp before you pay anything, and the first consultation and document check are free."),
 ("Can a visa consultant guarantee my visa?", "No honest consultant can. The decision is always made by the embassy. A good consultant reduces refusal risk by checking your documents, finances and cover letter before you apply."),
]
FAQ_VISA = [''')
rep('''{sec("Frequently asked questions", "", faq_html(FAQ_GENERAL))}''', '''{sec("Frequently asked questions", "", faq_html(FAQ_GENERAL + PAA_AGENCY))}''')
rep('''    ld = [faq_ld(FAQ_GENERAL), {"@context": "https://schema.org", "@type": "ItemList", "name": "Exclusive travel packages",''',
    '''    ld = [faq_ld(FAQ_GENERAL + PAA_AGENCY), {"@context": "https://schema.org", "@type": "ItemList", "name": "Exclusive travel packages",''')

# city pages get the agency PAA too
rep('''        if rawal:
            faqs.insert(1, ("Do you have an office in Rawalpindi?",''', '''        faqs += PAA_AGENCY[:2]
        if rawal:
            faqs.insert(1, ("Do you have an office in Rawalpindi?",''')

# Schengen PAA on the Schengen guide
rep('''    sfaq = [(f["q"], f["a"]) for f in sc["faqs"]] + [q for q in FAQ_GENERAL if "Schengen" in q[0] or "bank" in q[0].lower()][:2]''',
    '''    sfaq = [(f["q"], f["a"]) for f in sc["faqs"]] + [q for q in FAQ_GENERAL if "Schengen" in q[0] or "bank" in q[0].lower()][:2] + [
        ("Can I get a Schengen visa in 7 days?", "Rarely. Embassies normally decide within 15 calendar days of your appointment, and it can take longer in peak season. Plan 4–6 weeks ahead, including the wait for an appointment."),
        ("How can I get a Schengen visa more easily from Pakistan?", "Apply to the embassy of the country where you will spend the most nights, show a steady 6-month bank history with a clear source of income, prove strong ties to Pakistan, and make your hotel, flight and insurance dates match your cover letter exactly."),
        ("Which Schengen country should I apply to?", "The country where you will spend the most nights. If your stays are equal, apply to the country you enter first. Applying to an 'easier' embassy that doesn't match your itinerary is a common reason for refusal.")]''')

# country-specific PAA (only where we are confident)
rep('''    faqs += [(f["q"], f["a"]) for f in r["faqs"]][:2]
    siblings''', '''    faqs += [(f["q"], f["a"]) for f in r["faqs"]][:2]
    faqs += COUNTRY_PAA.get(c["slug"], [])
    siblings''')
rep('''PAA_AGENCY = [''', '''COUNTRY_PAA = {
 "malaysia": [("Can I get a Malaysia visa in 2 days?", "Malaysia eVisa decisions usually take a few working days, and we can't promise a 2-day result. Apply at least a week before travel; tell us your date and we advise the fastest option available.")],
 "italy": [("Who can help me with an Italy visa in Islamabad?", "Our Blue Area office prepares Italy Schengen files end to end: document check, appointment, insurance, hotel and flight reservations, and cover letter. Start with a free assessment on WhatsApp.")],
}

PAA_AGENCY = [''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v11")
