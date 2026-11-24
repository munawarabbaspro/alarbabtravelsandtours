"""One-off: insert the 24 Nov 2026 META_OVERRIDE.update block into src/build.py (idempotent)."""
import os
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "build.py")
s = open(p, encoding="utf-8").read()
if "24 Nov 2026 round" in s:
    print("already applied")
    raise SystemExit
anchor = "_CITY_TRAVEL_PREFIX = ("
assert s.count(anchor) == 1
blk = '''META_OVERRIDE.update({   # 24 Nov 2026 round: Umrah + target Asian countries + Europe/USA (Search Console 7-day data)
    "/umrah": ("Umrah Packages 2026 from Islamabad: Economy to 5 Star",
        "Umrah packages 2026 from Islamabad: Economy, 3, 4 and 5 Star with Makkah and Madinah hotels, flights and visa file preparation. Price on WhatsApp 0315-2323811."),
    "/countries/south-asia/nepal": ("Nepal Visa for Pakistanis: On Arrival & Online Form 2026",
        "Nepal tourist visa for Pakistanis: on arrival at Tribhuvan, Pokhara or Lumbini airports, online form or Nepali mission. 15, 30 or 90 days. File help in Islamabad."),
    "/countries/south-asia/bangladesh": ("Bangladesh Visa from Pakistan: High Commission Islamabad",
        "Bangladesh visa for Pakistanis: apply through the High Commission of Bangladesh in Islamabad, e-Consular appointment, documents checklist and file help in Blue Area."),
    "/countries/south-asia/sri-lanka": ("Sri Lanka ETA from Pakistan: Free 30-Day Tourist Visa 2026",
        "Sri Lanka free 30-day tourist visa for Pakistanis from 25 May 2026: ETA steps, documents and file help in Blue Area, Islamabad. WhatsApp 0315-2323811."),
    "/countries/south-asia/thailand": ("Thailand e-Visa from Pakistan: Apply Online, Documents 2026",
        "Thailand e-Visa for Pakistanis: apply online on the official portal while outside Thailand, documents checklist and file help in Blue Area. Free check on WhatsApp."),
    "/countries/south-asia/malaysia": ("Malaysia Visa from Pakistan: eVISA Portal, MDAC & Documents",
        "Malaysia visa for Pakistanis: Pakistan is on the visa-required list, apply on the official eVISA portal and add the MDAC 3 days before arrival. File help in Blue Area."),
    "/countries/schengen/italy": ("Italy (Rome) Visa from Pakistan: BLS Centres & Documents",
        "Visa for Rome and Italy from Pakistan: apply at the BLS-Intiana centre for your area, official embassy steps, documents checklist and file help in Blue Area."),
    "/countries/schengen/netherlands": ("Netherlands (Amsterdam) Visa from Pakistan: VFS & Documents",
        "Visa for Amsterdam and the Netherlands from Pakistan: apply at VFS Global in Islamabad, Karachi or Lahore up to 6 months ahead. Official steps and file help in Blue Area."),
    "/travel-insurance": ("Schengen Travel Insurance Pakistan: \\u20ac30,000 Cover | AL ARBAB",
        "Schengen travel insurance in Pakistan: the \\u20ac30,000 minimum medical cover embassies ask for, insurers on the German Embassy list, arranged from Blue Area, Islamabad."),
    "/countries/united-states": ("USA Visa from Pakistan: B1/B2, DS-160 & Interview Help | AL ARBAB",
        "USA B1/B2 visa from Pakistan: DS-160 form, appointment scheduling and interview preparation from Blue Area, Islamabad. The final decision rests with the US embassy."),
})
'''
s = s.replace(anchor, blk + anchor, 1)
open(p, "w", encoding="utf-8").write(s)
print("applied")
