# one-off patch: new lead pages (eligibility check, city pages, appointments, reservations, flight routes, umrah packages)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new):
    global s
    assert old in s, "missing: " + old[:80]
    s = s.replace(old, new, 1)

NEW = r'''
# ================================================================== lead pages (v3)
ROUTE_LINKS = {"London": "/countries/united-kingdom", "Dubai": "/countries/middle-east/united-arab-emirates", "Toronto": "/countries/canada",
               "Jeddah": "/countries/middle-east/saudi-arabia", "New York": "/countries/united-states", "Istanbul": "/countries/central-asia/turkey",
               "Melbourne": "/countries/australia", "Doha": "/countries/middle-east/qatar"}
ROUTE_IMG = {"London": "1486299267070-83823f5448dd", "Dubai": "1512453979798-5ea266f8880c", "Toronto": "1582778959124-88d5fd4fafa9",
             "Jeddah": "1699954669485-812988f5c2db", "New York": "1568515387631-8b650bbcdb90", "Istanbul": "1589561454226-796a8aa89b05",
             "Melbourne": "1585217514204-d025f2f1b116", "Doha": "1700901742651-6b353164caf3"}

def route_url(city):
    return "/air-ticketing/islamabad-to-" + city.lower().replace(" ", "-")

def umrah_url(u):
    return "/umrah/" + re.sub(r"[^a-z0-9]+", "-", u["title"].lower()).strip("-")

def office_block(title="Visit our Blue Area office"):
    return f\'\'\'<div class="block"><h2>{title}</h2><div class="contactgrid" style="margin-top:6px"><div class="info" style="padding:0;background:none">
<div><span class="ic">📍</span><span><small>ADDRESS</small><a href="{MAP_URL}" target="_blank" rel="noopener">{ADDR}</a></span></div>
<div><span class="ic">🕑</span><span><small>HOURS</small>{HOURS}</span></div>
<div><span class="ic">📞</span><span><small>PHONE</small><a href="tel:{PHONE_I}">{PHONE}</a> | <a href="tel:{LAND_I}">{LAND}</a></span></div>
<div><span class="ic">💬</span><span><small>WHATSAPP</small><a href="{WA}" target="_blank" rel="noopener">{PHONE}</a></span></div></div>
<iframe class="map" title="Map: {NAME} office" loading="lazy" src="https://www.openstreetmap.org/export/embed.html?bbox=73.0600%2C33.7090%2C73.0750%2C33.7180&amp;layer=mapnik&amp;marker=33.7135%2C73.0673"></iframe></div>
<p style="margin-top:12px"><a class="btn light" href="{MAP_URL}" target="_blank" rel="noopener">📍 Get directions on Google Maps</a></p></div>\'\'\'

def local_ld(city, url, desc):
    o = org_ld()
    return {"@context": "https://schema.org", "@type": "TravelAgency", "@id": BASE + url + "#local", "name": f"{NAME} – {city}", "url": BASE + url,
            "parentOrganization": {"@id": BASE + "/#org"}, "description": desc, "telephone": PHONE_I, "address": o["address"], "geo": o["geo"],
            "openingHoursSpecification": o["openingHoursSpecification"], "areaServed": {"@type": "City", "name": city}, "image": o["image"], "priceRange": "$$"}

def build_eligibility():
    elig = {}
    for c in COUNTRIES.values():
        rv = REGIONS[c["region"]]["visas"]
        elig[c["slug"]] = {"n": c["name"], "u": c["url"], "t": c["docs_clean"], "b": rv[1]["requirements"] if len(rv) > 1 else rv[0]["requirements"]}
    for rs in ("united-kingdom", "united-states", "canada", "australia"):
        r = REGIONS[rs]
        elig[rs] = {"n": r["name"], "u": f"/countries/{rs}", "t": r["visas"][0]["requirements"], "b": r["visas"][1]["requirements"] if len(r["visas"]) > 1 else r["visas"][0]["requirements"]}
    opts = "".join(f'<option value="{k}">{e(v["n"])}</option>' for k, v in sorted(elig.items(), key=lambda x: x[1]["n"]))
    content = f\'\'\'<section class="sec" style="margin-top:20px"><div class="layout"><div class="stack">
<form class="block elig" id="eligForm"><h2>Your trip</h2>
<div class="f" style="padding:0;background:none;gap:12px">
<div class="row"><div><label for="ed">1. Destination</label><select id="ed" name="d" required><option value="">Choose country</option>{opts}</select></div>
<div><label for="ep">2. Purpose</label><select id="ep" name="p"><option value="t">Tourism / holiday</option><option value="f">Family / friends visit</option><option value="b">Business / conference</option></select></div></div>
<div class="row"><div><label for="es">3. Your situation</label><select id="es" name="s"><option value="emp">Employed (salaried)</option><option value="biz">Business owner / self-employed</option><option value="stu">Student</option><option value="dep">Housewife / retired / dependant</option></select></div>
<div><label for="eb">4. Previous visas</label><select id="eb" name="h"><option value="none">No previous foreign travel</option><option value="some">Gulf / Asia visas</option><option value="strong">UK / USA / Schengen visas</option></select></div></div>
<div><button class="btn" type="submit">Show my checklist</button></div></div></form>
<div class="block" id="eligOut" hidden aria-live="polite"></div>
<div class="block"><h2>How the free check works</h2><ol class="steps">{steps_html([("Choose your trip", "Pick the country, purpose and your situation above."), ("Read your list", "You get the document list for your case, built from embassy requirements."), ("Free file check", "Send the documents on WhatsApp; an adviser checks them for refusal risks."), ("Apply with us", "We book the appointment, prepare the file and track it to the decision.")])}</ol></div>
</div><aside class="aside">{ctacard("visa eligibility")}</aside></div></section>\'\'\'
    ph = pagehead("Free tool", "Free visa eligibility<br>&amp; documents check", "Answer four questions and get the document checklist for your visa from Pakistan, then send your file to an adviser on WhatsApp for a free review.")
    body = shell("/eligibility-check", [("Home", "/"), ("Free Eligibility Check", None)], ph, content)
    script = "<script>window.ELIG=" + json.dumps(elig, ensure_ascii=False, separators=(",", ":")) + ";</script>"
    ld = [crumbs_ld([("Home", "/"), ("Free Eligibility Check", "/eligibility-check")]),
          {"@context": "https://schema.org", "@type": "WebApplication", "name": "Free visa eligibility & documents check", "url": BASE + "/eligibility-check",
           "applicationCategory": "TravelApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "PKR"}, "provider": {"@id": BASE + "/#org"}}]
    page("/eligibility-check", "Free Visa Eligibility & Documents Check | AL ARBAB",
         "Free visa eligibility check for Pakistani citizens: choose your country, purpose and situation to get your document checklist, then a free file review on WhatsApp.",
         body, ld, "visa eligibility check pakistan, visa documents checklist, free visa assessment islamabad", extra_script=script, priority="0.8")

CITY_PAGES = [
 ("/travel-agency-islamabad", "Islamabad", "Travel Agency in Islamabad", "Travel agency in<br>Blue Area, Islamabad",
  "Visas, air tickets, Umrah, hotels and travel insurance from one IATA-authorized office in Eagle Plaza, Blue Area.",
  "Travel Agency in Islamabad (Blue Area) | AL ARBAB",
  "IATA-authorized travel agency in Blue Area, Islamabad: visas for 50+ countries, air tickets, Umrah packages, hotels & insurance. Free WhatsApp consultation.",
  "travel agency islamabad, travel agency blue area, best travel agency in islamabad, iata travel agent islamabad"),
 ("/visa-consultant-islamabad", "Islamabad", "Visa Consultant in Islamabad", "Visa consultant<br>in Islamabad",
  "Schengen, UK, USA, Canada, Australia and Asia visas prepared by case officers in Blue Area, with a free document check before you apply.",
  "Visa Consultant in Islamabad | Free File Check | AL ARBAB",
  "Visa consultant in Blue Area, Islamabad for Schengen, UK, USA, Canada, Australia, Dubai & Asia visas. 98% approval rate, free document check on WhatsApp.",
  "visa consultant islamabad, visa agent islamabad, visa consultancy blue area, best visa consultant islamabad"),
 ("/travel-agency-rawalpindi", "Rawalpindi", "Travel Agency for Rawalpindi", "Travel agency for<br>Rawalpindi clients",
  "Start on WhatsApp from Rawalpindi: free document check first, then one visit to our Blue Area office when your file is ready.",
  "Travel Agency for Rawalpindi Clients | AL ARBAB",
  "Rawalpindi travellers: free visa document check on WhatsApp, then visit our Blue Area office once. Visas, air tickets, Umrah and hotels from an IATA agent.",
  "travel agency rawalpindi, travel agent rawalpindi, umrah travel agency rawalpindi, air ticket rawalpindi"),
 ("/visa-consultant-rawalpindi", "Rawalpindi", "Visa Consultant for Rawalpindi", "Visa consultant for<br>Rawalpindi",
  "Visa files for Rawalpindi clients handled end to end: document review on WhatsApp, appointment booking and submission support.",
  "Visa Consultant for Rawalpindi | Free File Check | AL ARBAB",
  "Visa consultant for Rawalpindi clients: Schengen, UK, USA, Canada, Dubai & Asia visas. Free WhatsApp document check, one visit to our Blue Area office.",
  "visa consultant rawalpindi, visa agent rawalpindi, visa consultancy rawalpindi, schengen visa rawalpindi"),
]

def build_cities():
    popular = [COUNTRIES[s] for s in ("germany", "france", "italy", "united-arab-emirates", "thailand", "malaysia", "turkey", "saudi-arabia", "singapore", "azerbaijan", "china", "japan") if s in COUNTRIES]
    for url, city, name, h1, lead, title, desc, kw in CITY_PAGES:
        rawal = city == "Rawalpindi"
        visa = "visa" in url
        intro = (f"Rawalpindi clients don't need to travel to Islamabad twice. Send your passport and documents on WhatsApp, our adviser checks them for free, and you visit our Blue Area office only when the file is ready to submit."
                 if rawal else f"{NAME} has served travellers from Blue Area, Islamabad since 2009. One office handles your visa file, flights, hotel, insurance and Umrah, so nothing falls between agencies.")
        services = "".join(feat(ic, n, d, (u, "Open")) for ic, n, d, u in [
            ("◈", "Visa consultancy", "Schengen, UK, USA, Canada, Australia, Gulf and Asia visas with document review and appointments.", "/visa-services"),
            ("✈", "Air tickets", "IATA-authorized tickets on 300+ airlines, group and student fares, 24/7 changes.", "/air-ticketing"),
            ("🕋", "Umrah packages", "Economy to 5-star packages from PKR 185,000 with visa, flights and hotels.", "/umrah"),
            ("🏨", "Hotels & reservations", "Verifiable hotel and flight reservations for visa files, plus holiday stays.", "/flight-hotel-reservation-for-visa"),
            ("🛡", "Travel insurance", "Schengen-compliant policies from Jubilee, Adamjee, United & EFU in 15 minutes.", "/travel-insurance"),
            ("📅", "Visa appointments", "VFS Global, BLS, Gerry's and embassy appointment booking.", "/visa-appointments")])
        steps = steps_html([("WhatsApp your details", "Tell us the country and travel dates; send passport and documents as photos."),
                            ("Free document check", "An adviser checks your file and tells you what is missing and the full price."),
                            ("One office visit", "Visit Blue Area to sign forms and hand over originals when the file is ready."),
                            ("Submission & tracking", "We book the appointment, prepare the file and track it until the decision.")])
        regions = "".join(region_card(REGIONS[s]) for s in ("schengen", "united-kingdom", "united-states", "canada"))
        getting = (f\'\'\'<div class="block"><h2>Getting to our office from Rawalpindi</h2><p>Our office is in Eagle Plaza on Fazal-e-Haq Road, Blue Area, just off Jinnah Avenue. The Rawalpindi–Islamabad Metrobus runs along Jinnah Avenue through Blue Area, and Islamabad Expressway or Murree Road connect Rawalpindi to the Blue Area by car.</p><p>Message us before you leave and we will confirm your adviser is free when you arrive.</p></div>\'\'\' if rawal else "")
        faqs = [(f"Where is {NAME} located?", f"{ADDR}. Open {HOURS}."),
                ("Can I start without visiting the office?", "Yes. Send your documents on WhatsApp for a free check. You visit the office only when your file is ready to submit."),
                ("Do you charge for the first consultation?", "No. The first consultation and document check are free; we quote the full price before you pay anything."),
                ("Are you IATA authorized?", "Yes. We are an IATA-accredited agency since 2015 and issue airline tickets directly.")]
        if rawal:
            faqs.insert(1, ("Do you have an office in Rawalpindi?", "Our office is in Blue Area, Islamabad. Rawalpindi clients start on WhatsApp and visit Blue Area once, when the file is ready."))
        main = f\'\'\'<div class="stack">
<div class="block"><h2>{e(name)} you can trust</h2><p>{intro}</p><div class="chipsrow" style="margin-top:12px"><span>IATA authorized since 2015</span><span>98% approval rate</span><span>20,000+ travellers</span><span>Free first consultation</span></div></div>
{'<div class="block"><h2>Visa regions we handle</h2><div class="rgrid">' + regions + '</div></div>' if visa else '<div class="block"><h2>Everything under one roof</h2><div class="grid">' + services + '</div></div>'}
<div class="block"><h2>How it works{' for ' + city + ' clients' if rawal else ''}</h2><ol class="steps">{steps}</ol></div>
{getting}
<div class="block"><h2>Popular destinations</h2><div class="tiles">{"".join(tile(c) for c in popular)}</div><p style="margin-top:12px"><a class="link" href="/countries">All {len(COUNTRIES)} destinations →</a></p></div>
{office_block()}
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div>
</div>\'\'\'
        others = "".join(f'<a href="{u}">{n} <span>→</span></a>' for u, _, n, *_ in CITY_PAGES if u != url)
        aside = f'<aside class="aside">{ctacard(name.lower())}<nav class="mini"><h3>Also see</h3>{others}<a href="/eligibility-check">Free eligibility check <span>→</span></a></nav></aside>'
        content = f'<div class="layout">{main}{aside}</div>{cta_band()}'
        acts = f'<a class="btn wa" href="{wa("Hi, I am in " + city + " and need help with a visa/trip.")}" target="_blank" rel="noopener">💬 WhatsApp an adviser</a><a class="btn light" href="tel:{PHONE_I}">📞 {PHONE}</a>'
        ph = pagehead(f"{city} · Blue Area office", h1, lead, UNS["cta"] if not visa else UNS["fr"], alt=f"{NAME} – {city}", actions=acts)
        body = shell(url, [("Home", "/"), (name, None)], ph, content)
        ld = [crumbs_ld([("Home", "/"), (name, url)]), local_ld(city, url, desc), faq_ld(faqs)]
        page(url, title, desc, body, ld, kw, priority="0.8")

def build_appointments():
    rows = "".join(f'<tr><td><a class="link" href="{u}">{e(c)}</a></td><td>{e(v)}</td></tr>' for c, v, u in APPOINTMENT_CENTRES)
    need = "".join(f"<li>{x}</li>" for x in ["Passport copy (biodata page) and CNIC copy", "Completed online application or form confirmation", "Visa fee payment (embassy / centre fee)", "Your preferred dates and contact number"])
    bring = "".join(f"<li>{x}</li>" for x in ["Original passport and old passports", "Printed appointment letter and form", "Complete document file (we prepare and index it)", "Photographs as per embassy specification"])
    faqs = [("Which visa centre handles my application?", "It depends on the embassy: for example the UK uses VFS Global, Spain uses BLS International, and the US uses CGI Federal for fees and appointments. The table on this page lists the main ones."),
            ("Can you get an early appointment?", "We monitor slots daily and book the earliest available date that suits your travel plan. Embassies control availability, so no agent can guarantee a specific date."),
            ("Do I need to visit the centre myself?", "Yes, for biometrics and submission you attend in person. We prepare your file and brief you on what to expect.")]
    main = f\'\'\'<div class="stack">
<div class="block"><h2>Embassy &amp; visa centre appointments</h2><p>Most embassies in Islamabad accept applications through an outsourced visa centre or an online portal. We create your account, fill the form, pay the fee correctly and book the earliest suitable slot, then prepare the file you take to the appointment.</p></div>
<div class="block"><h2>Where each embassy takes applications</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Country</th><th>Application route</th></tr></thead><tbody>{rows}</tbody></table></div></div>
<div class="block"><h2>Needed to book</h2><ul class="checks">{need}</ul><h3>Bring on appointment day</h3><ul class="checks">{bring}</ul></div>
<div class="block"><h2>How it works</h2><ol class="steps">{steps_html(PROCESS)}</ol></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>\'\'\'
    content = f'<div class="layout">{main}<aside class="aside">{ctacard("visa appointment booking")}</aside></div>{cta_band()}'
    ph = pagehead("Appointments", "Visa appointment booking<br>in Islamabad", "VFS Global, BLS International, Gerry's, CGI Federal and embassy portals: we book your slot and prepare the file you submit.", UNS["fr"], alt="Visa appointment booking",
                  actions=f'<a class="btn wa" href="{wa("Hi, I need a visa appointment booked.")}" target="_blank" rel="noopener">💬 Book an appointment</a>')
    body = shell("/visa-appointments", [("Home", "/"), ("Visa Appointments", None)], ph, content)
    page("/visa-appointments", "Visa Appointment Booking Islamabad | VFS, BLS | AL ARBAB",
         "Visa appointment booking in Islamabad for VFS Global, BLS International, Gerry's and US CGI Federal. Forms, fees and file preparation by AL ARBAB.",
         body, [crumbs_ld([("Home", "/"), ("Visa Appointments", "/visa-appointments")]), service_ld("Visa appointment booking", "Embassy and visa centre appointment booking in Islamabad.", "/visa-appointments", {"serviceType": "Visa appointment booking"}), faq_ld(faqs)],
         "vfs appointment islamabad, bls appointment islamabad, gerrys appointment, us visa appointment pakistan", priority="0.7")

def build_reservation():
    faqs = [("Do embassies accept reservations instead of paid tickets?", "Many embassies, including most Schengen states, ask for a flight reservation and hotel booking rather than a paid ticket. The US embassy recommends not buying tickets before your visa is approved. We confirm what your embassy expects."),
            ("Are your reservations verifiable?", "Yes. We provide reservations that the embassy can verify, covering every night of your stay and your return flight."),
            ("How fast can I get them?", "Usually the same day once we have your passport details and travel dates.")]
    main = f\'\'\'<div class="stack">
<div class="block"><h2>Reservations that match your visa file</h2><p>Embassies, particularly Schengen and US, check that your flights and hotels match your itinerary and cover the full stay. We issue verifiable flight reservations and hotel bookings that line up with your cover letter, travel insurance and dates, so the file tells one consistent story.</p></div>
<div class="block"><h2>What you get</h2><ul class="checks"><li>Return flight reservation in your passport name</li><li>Hotel bookings for every night of the stay, city by city</li><li>Day-by-day itinerary to match the cover letter</li><li>Schengen-compliant travel insurance on request</li></ul></div>
<div class="block"><h2>How it works</h2><ol class="steps">{steps_html([("Send details", "Passport copy, travel dates and cities on WhatsApp."), ("We draft the plan", "Flights, hotels and itinerary that fit your visa type."), ("Receive documents", "Verifiable reservations, usually the same day."), ("File check", "We check everything matches before you submit.")])}</ol></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>\'\'\'
    content = f'<div class="layout">{main}<aside class="aside">{ctacard("flight and hotel reservation")}</aside></div>{cta_band()}'
    ph = pagehead("Visa documents", "Flight &amp; hotel reservation<br>for visa", "Verifiable flight reservations and hotel bookings for Schengen, UK, US and other visa files, matched to your itinerary.", UNS["sg"], alt="Hotel and flight reservation for visa",
                  actions=f'<a class="btn wa" href="{wa("Hi, I need a flight and hotel reservation for my visa.")}" target="_blank" rel="noopener">💬 Get reservations</a>')
    body = shell("/flight-hotel-reservation-for-visa", [("Home", "/"), ("Flight & Hotel Reservation", None)], ph, content)
    page("/flight-hotel-reservation-for-visa", "Flight & Hotel Reservation for Visa | AL ARBAB",
         "Verifiable flight reservations and hotel bookings for Schengen, UK, US and other visa applications, matched to your itinerary. Same-day service in Islamabad.",
         body, [crumbs_ld([("Home", "/"), ("Flight & Hotel Reservation", "/flight-hotel-reservation-for-visa")]), service_ld("Flight & hotel reservation for visa", "Verifiable reservations for visa applications.", "/flight-hotel-reservation-for-visa"), faq_ld(faqs)],
         "flight reservation for visa, hotel booking for visa, dummy ticket for visa pakistan, schengen hotel reservation", priority="0.7")

def build_routes():
    for city, code, airlines in ROUTES:
        url = route_url(city)
        vlink = ROUTE_LINKS.get(city)
        al = ", ".join(a.title() for a in airlines.split(", "))
        faqs = [(f"Which airlines fly from Islamabad to {city}?", f"Popular options on this route include {al}. We compare direct and one-stop fares and send you the best options."),
                (f"How do I get the cheapest Islamabad to {city} ticket?", "Book early, stay flexible on dates and compare one-stop routes via hubs like Dubai, Doha or Istanbul. Our ticketing officers check these for you."),
                FAQ_AIR[5] if len(FAQ_AIR) > 5 else FAQ_AIR[0]]
        main = f\'\'\'<div class="stack">
<div class="block"><h2>Islamabad to {e(city)} flights</h2><div class="facts" style="margin-top:0"><div><small>Route</small><b>{e(code)}</b></div><div><small>Popular airlines</small><b>{e(al)}</b></div><div><small>E-ticket</small><b>Issued instantly after payment</b></div><div><small>Support</small><b>24/7 changes &amp; cancellations</b></div></div>
<p style="margin-top:14px">As an IATA-authorized agency we see live fares on {e(al)} and other carriers serving {e(city)}. Send your dates on WhatsApp and we reply with the best direct and one-stop options, baggage allowance and fare rules.</p>
<p style="margin-top:12px"><a class="btn wa" href="{wa(f"Hi, I need a fare for Islamabad to {city} ({code}). My dates are: ")}" target="_blank" rel="noopener">💬 Get today's fare</a></p></div>
{f'<div class="block"><h2>Visa for {e(city)}</h2><p>Need a visa for this trip? See the document checklist and fees on our <a class="link" href="{vlink}">visa page</a>. We can book your ticket and handle the visa together.</p></div>' if vlink else ""}
<div class="block"><h2>Before you book</h2><ul class="checks"><li>Passport validity must be at least 6 months.</li><li>Check transit visa requirements for layovers.</li><li>Ensure your name matches your passport exactly.</li><li>Verify baggage allowance (2PC vs 30KG).</li></ul></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>\'\'\'
        others = "".join(f'<a href="{route_url(c)}">Islamabad → {c} <span>→</span></a>' for c, *_ in ROUTES if c != city)
        content = f'<div class="layout">{main}<aside class="aside">{ctacard("Islamabad to " + city + " ticket")}<nav class="mini"><h3>Other routes</h3>{others}</nav></aside></div>{cta_band("Ready to fly?")}'
        ph = pagehead(f"Air tickets · {e(code)}", f"Islamabad to {e(city)}<br>flights", f"Compare {e(al)} and more. IATA-authorized tickets with instant e-ticket and 24/7 support from Blue Area, Islamabad.", ROUTE_IMG.get(city), alt=f"{city} – flights from Islamabad",
                      actions=f'<a class="btn wa" href="{wa(f"Hi, I need a fare for Islamabad to {city}.")}" target="_blank" rel="noopener">💬 Get a fare</a><a class="btn light" href="tel:{PHONE_I}">📞 {PHONE}</a>')
        body = shell("/air-ticketing", [("Home", "/"), ("Air Ticketing", "/air-ticketing"), (f"Islamabad to {city}", None)], ph, content)
        ld = [crumbs_ld([("Home", "/"), ("Air Ticketing", "/air-ticketing"), (f"Islamabad to {city}", url)]), service_ld(f"Islamabad to {city} air tickets", f"Air tickets from Islamabad to {city} on {al}.", url, {"serviceType": "Air ticketing"}), faq_ld(faqs)]
        page(url, f"Islamabad to {city} Flights & Air Tickets | AL ARBAB", f"Islamabad to {city} ({code}) air tickets on {al}. IATA-authorized agent, instant e-tickets, group & student fares. Get today's fare on WhatsApp.",
             body, ld, f"islamabad to {city.lower()} flights, islamabad to {city.lower()} ticket price, {city.lower()} air ticket from pakistan", image=U(ROUTE_IMG[city], 1200) if city in ROUTE_IMG else None, priority="0.6")

def build_umrah_packages():
    for u in DATA["umrah"]:
        url = umrah_url(u)
        price = u["price"].replace("From ", "")
        f = "".join(f"<li>{e(x)}</li>" for x in u["features"])
        others = [o for o in DATA["umrah"] if o is not u]
        faqs = [(f"What is included in the {u['title']}?", ", ".join(u["features"]) + "."),
                (f"How much does the {u['title']} cost?", f"{u['price']} per person. The final price depends on dates, hotel availability and group size; we confirm it before you pay."),
                FAQ_UMRAH[1]]
        main = f\'\'\'<div class="stack">
<div class="block"><h2>{e(u["title"])} at a glance</h2><div class="feebox"><div><small>Price</small><b>{e(u["price"])}</b></div><div><small>Duration</small><b>{e(u["features"][0])}</b></div><div><small>Hotels</small><b>{e(u["features"][1])}</b></div></div></div>
<div class="block"><h2>What's included</h2><ul class="checks">{f}</ul></div>
<div class="block"><h2>Make it yours</h2><p>Choose from 300+ hotels in Makkah and Madinah, change the number of nights in each city, or upgrade transport. Tell us your dates and family size on WhatsApp for a tailored quote.</p>
<p style="margin-top:12px"><a class="btn wa" href="{wa(f"Hi, I want to book the {u['title']} Umrah package ({u['price']}).")}" target="_blank" rel="noopener">💬 Book this package</a></p></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>\'\'\'
        ol = "".join(f'<a href="{umrah_url(o)}">{e(o["title"])} · {e(o["price"].replace("From ", ""))} <span>→</span></a>' for o in others)
        content = f'<div class="layout">{main}<aside class="aside">{ctacard(u["title"] + " Umrah")}<nav class="mini"><h3>Other Umrah packages</h3><a href="/umrah">All Umrah packages <span>→</span></a>{ol}</nav></aside></div>{cta_band("Begin your sacred journey")}'
        ph = pagehead(f"Umrah 2026 · {e(price)}", f"Umrah {e(u['title'])}", f"{e(u['price'])} — " + e(", ".join(u["features"][:3])) + ". Visa, flights and hotels arranged from Islamabad.", UNS["umrah"], alt=f"Umrah {u['title']} – Makkah",
                      actions=f'<a class="btn wa" href="{wa(f"Hi, I want the {u['title']} Umrah package.")}" target="_blank" rel="noopener">💬 Book on WhatsApp</a>')
        body = shell("/umrah", [("Home", "/"), ("Umrah Packages", "/umrah"), (u["title"], None)], ph, content)
        ld = [crumbs_ld([("Home", "/"), ("Umrah Packages", "/umrah"), (u["title"], url)]),
              service_ld(f"Umrah {u['title']}", ", ".join(u["features"]), url, {"serviceType": "Umrah package", "offers": {"@type": "Offer", "priceCurrency": "PKR", "price": re.sub(r"[^\d]", "", u["price"]), "description": u["price"]}}), faq_ld(faqs)]
        page(url, f"Umrah {u['title']} 2026 {price} | AL ARBAB"[:65], f"Umrah {u['title']} from Islamabad: {u['price']}. " + ", ".join(u["features"]) + ". Book on WhatsApp.",
             body, ld, f"umrah {u['title'].lower()}, umrah package {price.lower()}, umrah package islamabad 2026", image=U(UNS["umrah"], 1200), priority="0.7")

# ================================================================== write'''

rep("\n# ================================================================== write", NEW)

# register builders
rep("    build_hotel(); build_insurance(); build_airlines(); build_about(); build_contact(); build_legal(); build_misc()",
    "    build_hotel(); build_insurance(); build_airlines(); build_about(); build_contact(); build_legal(); build_misc()\n    build_eligibility(); build_cities(); build_appointments(); build_reservation(); build_routes(); build_umrah_packages()")

# link route cards and umrah cards to their new pages
rep('''<div class="route"><span class="c">{c}</span><b>Islamabad → {n}</b><small>{al}</small><a href="{wa(f"Hi, I need a fare quote for Islamabad to {n} ({c}).")}" target="_blank" rel="noopener">Get fare quote →</a></div>''',
    '''<div class="route"><span class="c">{c}</span><b><a href="{route_url(n)}">Islamabad → {n}</a></b><small>{al}</small><a href="{route_url(n)}">Route details &amp; fares →</a></div>''')
rep('''<div class="price"><small>From</small>{e(price)}</div><ul>{f}</ul>
<a class="more" href="{wa(f"Hi, I want to book the {u['title']} Umrah package ({u['price']}).")}" target="_blank" rel="noopener">Book now <span>→</span></a></div></article>\'\'\'''',
    '''<div class="price"><small>From</small>{e(price)}</div><ul>{f}</ul>
<a class="more" href="{umrah_url(u)}">Package details <span>→</span></a></div></article>\'\'\'''')

# region pages: official sources
rep('''{fb}
<div class="block"><h2>Why choose {NAME} in Islamabad?</h2>''', '''{fb}
{"" if r["slug"] not in REGION_OFFICIAL else '<div class="block"><h2>Official sources</h2><ul class="srcs">' + "".join(f'<li><a href="{u}" target="_blank" rel="noopener nofollow">{e(n)} ↗</a></li>' for n, u in REGION_OFFICIAL[r["slug"]]) + "</ul></div>"}
<div class="block"><h2>Why choose {NAME} in Islamabad?</h2>''')

# footer: more services + local pages
rep('''           ("/travel-insurance", "Travel Insurance"), ("/partner-airlines", "Partner Airlines"), ("/packages", "Holiday Packages")]''',
    '''           ("/travel-insurance", "Travel Insurance"), ("/partner-airlines", "Partner Airlines"), ("/packages", "Holiday Packages"),
           ("/visa-appointments", "Visa Appointments"), ("/flight-hotel-reservation-for-visa", "Flight & Hotel Reservation"), ("/eligibility-check", "Free Eligibility Check")]''')
rep('''    co = [("/about", "About Us"), ("/contact", "Contact Us"), ("/privacy", "Privacy Policy"), ("/terms", "Terms & Conditions")]''',
    '''    co = [("/about", "About Us"), ("/contact", "Contact Us"), ("/travel-agency-islamabad", "Travel Agency Islamabad"), ("/visa-consultant-islamabad", "Visa Consultant Islamabad"),
          ("/travel-agency-rawalpindi", "Travel Agency Rawalpindi"), ("/visa-consultant-rawalpindi", "Visa Consultant Rawalpindi"), ("/privacy", "Privacy Policy"), ("/terms", "Terms & Conditions")]''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v4")
