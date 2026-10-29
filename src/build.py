#!/usr/bin/env python3
"""AL ARBAB TRAVEL AND TOURS - static site generator.

    py build.py            -> writes the full site to ./dist

Content lives in data/site-data.json (extracted from the old site) and in the
PAGE TEXT section below. Edit, re-run, upload the contents of dist/.
"""
import json, os, re, shutil, html as H
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))   # src/: source folder
SITE = os.path.dirname(ROOT)                                  # repo root: dist/ is written here
OUT = os.path.join(SITE, "dist")
DATA = json.load(open(os.path.join(ROOT, "data", "site-data.json"), encoding="utf-8"))
B = DATA["brand"]

MONEY = r"(?:PKR|Rs\.?|EUR|USD|GBP|AUD|CAD|€|£|\$)\s?\d[\d,.]*\+?|\d[\d,.]*\+?\s?(?:PKR|EUR|USD|GBP|AUD|CAD)\b"
FEE_WORD = re.compile(r"\bfees?\b|\bcharges?\b|\bcost\b|\bprice\b", re.I)

def no_fee(text):
    """Remove fee amounts from a requirement line; returns None if the whole line is about the fee."""
    if re.match(r"\s*(visa\s+)?fees?\s*:", text, re.I):
        return None
    if not (FEE_WORD.search(text) and re.search(MONEY, text)):
        return text
    t = re.sub(r"\s*\([^)]*(?:" + MONEY + r")[^)]*\)", "", text)
    t = re.sub(r"(?:approx\.?\s*)?(?:" + MONEY + r")(?:\s*[-–/]\s*(?:approx\.?\s*)?(?:" + MONEY + r"|\d[\d,.]*))?", "", t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip(" -–:,;/")
    return t if len(t) > 3 and not re.fullmatch(r"(visa\s+)?fees?.*", t, re.I) else None

def clean_list(xs):
    return [y for y in (no_fee(x) for x in xs) if y]

def clean_faqs(fs):
    return [f for f in fs if not (FEE_WORD.search(f["q"]) and re.search(MONEY, f["a"])) and not re.search(r"\bfees?\b", f["q"], re.I)]

for _lst in DATA["countries"].values():
    for _c in _lst:
        _c["docs"] = clean_list(_c["docs"])
for _r in DATA["regions"]:
    _r["generalRequirements"] = clean_list(_r["generalRequirements"])
    _r["faqs"] = clean_faqs(_r["faqs"])
    if isinstance(_r["visas"], list):
        for _v in _r["visas"]:
            _v["requirements"] = clean_list(_v["requirements"])
for _v in DATA["visaTypeTemplate"]:
    _v["requirements"] = clean_list(_v["requirements"])
DATA["faqSchengenGeneral"] = clean_faqs(DATA["faqSchengenGeneral"])
# no work-permit / overseas-employment offers (needs a BEOE OEP licence)
DATA["services"] = [x for x in DATA["services"] if not re.search(r"work permit|employment visa", x["title"] + " " + x["desc"], re.I)]
for _r in DATA["regions"]:
    _r["shortDesc"] = re.sub(r",?\s*(and\s+)?work permits?", "", _r["shortDesc"], flags=re.I)

def no_iata(x):
    """Old-site texts called the agency IATA-authorized; replace with neutral / DTS wording."""
    if isinstance(x, str):
        x = re.sub(r"\bIATA[- ](?:authori[sz]ed|accredited|certified|direct)\s*", "", x, flags=re.I)
        x = re.sub(r"\b(?:full )?IATA (?:accreditation|certification)\b", "a DTS licence", x, flags=re.I)
        x = re.sub(r"\s*\bIATA\b\s*", " ", x).replace("  ", " ")
        return x
    if isinstance(x, list):
        return [no_iata(i) for i in x]
    if isinstance(x, dict):
        return {k: (v if k == "iata" else no_iata(v)) for k, v in x.items()}
    return x

for _k in ("faqSchengenGeneral", "faqAir"):
    DATA[_k] = [f for f in DATA[_k] if "iata" not in f["q"].lower()]
for _k in ("services", "countries", "regions", "faqSchengenGeneral", "faqAir", "airlines", "packages", "visaDest", "heroDest"):
    DATA[_k] = no_iata(DATA[_k])
DATA["faqAir"] = clean_faqs(DATA["faqAir"])
PHOTOS = {}   # slug -> [[place, unsplash id], ...]  first = hero.  Edit data/images.tsv to change photos.
for _ln in open(os.path.join(ROOT, "data", "images.tsv"), encoding="utf-8"):
    if _ln.strip() and not _ln.startswith("#"):
        _s, _p, _i = [x.strip() for x in _ln.split("|")]
        PHOTOS.setdefault(_s, []).append([_p, _i])

BASE = "https://www.alarbabtravel.com"
NAME = B["name"]
PHONE, PHONE_I = B["mobile"], "+923152323811"
PHONE_SCHENGEN_I = "+923099923232"   # Schengen & visa file preparation desk
PHONE_D = PHONE[:4] + "-" + PHONE[4:]   # 0315-2323811 for search snippets
LAND, LAND_I = B["landline"], "+92512000066"
EMAIL = B["email"]
WA = "https://wa.me/923152323811"
# WhatsApp routing (owner, Oct 2026), edited in data/whatsapp-routing.json: every WhatsApp link on a page goes to the desk
# for that page's topic, with that desk's opening message. Calls (tel:) and the schema stay on the main number. route_wa() applies it in page().
WA_ROUTING = json.load(open(os.path.join(ROOT, "data", "whatsapp-routing.json"), encoding="utf-8"))
WA_DESK = {k: v.lstrip("+") for k, v in WA_ROUTING["whatsappNumbers"].items()}          # wa.me wants digits only
WA_TEXT = dict(WA_ROUTING["messageTemplates"], default=WA_ROUTING["messageTemplates"]["general"])
WA_LABEL = dict(WA_ROUTING["labels"], default=WA_ROUTING["labels"]["general"])   # hover label on the floating WhatsApp button

def wa_desk(url):
    """general (exceptions) -> schengen -> asian -> default; a route matches itself and the pages under it"""
    under = lambda key: any(url == p or url.startswith(p + "/") for p in WA_ROUTING["routing"].get(key, []))
    return "default" if under("general") else "schengen" if under("schengen") else "asian" if under("asian") else "default"

_SCH_CACHE = []
def sch_names():
    """lower-case destination names that are handled by the Schengen desk (used by the forms to pick the WhatsApp number)"""
    if not _SCH_CACHE:
        names = {"schengen", "europe", "uk", "u.k", "england", "britain", "london", "usa"} - {"usa"}
        for c in COUNTRIES.values():
            if "schengen" in (wa_desk(c["url"]), wa_desk("/countries/" + c["slug"])):
                names.add(c["name"].lower())
        for r_ in REGIONS.values():
            if wa_desk("/countries/" + r_["slug"]) == "schengen":
                names.add(r_["name"].lower())
        _SCH_CACHE.append(sorted(names))
    return _SCH_CACHE[0]

def disp(num):
    """923099923232 -> 0309-9923232"""
    return "0" + num[2:5] + "-" + num[5:]

def route_wa(url, html):
    desk = wa_desk(url)
    num, main = WA_DESK[desk], WA.rsplit("/", 1)[1]    # links are generated with the main number (WA), then re-pointed here
    html = re.sub(rf'href="https://wa\.me/{main}(?:\?text=[^"]*)?"', f'href="https://wa.me/{num}?text={quote(WA_TEXT[desk])}"', html)
    html = html.replace(f'window.SITE={{wa:"{WA}"', f'window.SITE={{wa:"https://wa.me/{num}"')   # forms add their own text
    html = html.replace("@WALABEL@", e(WA_LABEL[desk]))
    if num != main:   # wherever the number is shown as the WhatsApp number (buttons, meta description), show the desk's number
        html = html.replace(f"WhatsApp {PHONE_D}", f"WhatsApp {disp(num)}")
        html = re.sub(rf'(<a [^>]*href="https://wa\.me/{num}[^"]*"[^>]*>)(.*?)(</a>)',
                      lambda m: m.group(1) + m.group(2).replace(PHONE_D, disp(num)).replace(PHONE, disp(num)) + m.group(3), html, flags=re.S)
    return html
ADDR = B["address"]
HOURS = "Monday – Saturday: 9:00 AM – 8:00 PM"
MAP_URL = B["mapUrl"]
LOGO = BASE + "/assets/logo.png"          # absolute (schema, Open Graph)
import hashlib
def _v(name):
    return hashlib.md5(open(os.path.join(ROOT, "assets", name), "rb").read()).hexdigest()[:8]
asset_hash = _v   # _v is reused as a loop variable further down
LOGO_SRC = f"/assets/logo-80.png?v={_v('logo-80.png')}"   # 80px header logo (~3 KB)
ORBIT_MARK = f"/assets/brand/mark1-plane.png?v={_v('brand/mark1-plane.png')}"
LOGO_FULL = f"/assets/brand/logo1-plane.png?v={_v('brand/logo1-plane.png')}"
AL_MARK = f"/assets/brand/al-mark.png?v={_v('brand/al-mark.png')}"   # the owner's own AL mark (red + silver, with plane)
AL_MARK_S = f"/assets/brand/al-mark-s.png?v={_v('brand/al-mark-s.png')}"
AL_TILE = f"/assets/brand/al-glass-60.png?v={_v('brand/al-glass-60.png')}"      # glass icon tile: 1x
AL_TILE2 = f"/assets/brand/al-glass-120.png?v={_v('brand/al-glass-120.png')}"   # 2x
AL_TILE3 = f"/assets/brand/al-glass-360.png?v={_v('brand/al-glass-360.png')}"   # splash
AL_MARK_M = f"/assets/brand/al-mark-m.png?v={_v('brand/al-mark-m.png')}"   # footer size
LOGO_STICKER = f"/assets/brand/sticker.png?v={_v('brand/sticker.png')}"
LOGO_STICKER_S = f"/assets/brand/sticker-s.png?v={_v('brand/sticker-s.png')}"   # 2x of the header size, resized properly so it stays sharp   # the cream + gold logo, works on any background
LOGO_LIGHT = f"/assets/brand/logo1-plane-light.png?v={_v('brand/logo1-plane-light.png')}"
LOGO_DARK = f"/assets/brand/logo1-plane-dark.png?v={_v('brand/logo1-plane-dark.png')}"   # clean dark letters, for light headers   # white letters, for the dark footer   # the licensed AL ARBAB mark, used unchanged
ICON32 = f"/assets/icon-32.png?v={_v('icon-32.png')}"
ICON192 = f"/assets/icon-192.png?v={_v('icon-192.png')}"
APPJS = f"/assets/app.js?v={_v('app.js')}"
TODAY = "2026-10-17"
UPDATED = "October 2026"
GSC_CODE = ""         # Google Search Console HTML-tag code (content value only). Empty = no tag.
BING_CODE = ""        # Bing Webmaster verification code. Empty = no tag.
GA_ID = "G-T4BRVJZGNR"   # Google Analytics 4 measurement ID (AL ARBAB). Empty = no tracking script.
# Trust signals. Leave empty until you have the real value; nothing is shown (and nothing is invented) while a field is empty.
DTS_LICENCE = ""      # DTS licence number, e.g. "TA-1234". Shown in the footer and under the contact banners.
GBP_URL = "https://maps.google.com/?cid=2894299413323017788"   # Google Business Profile / Google Maps reviews link
G_RATING = "5.0"      # real Google star rating (as text). Shown ONLY on the home page and in the footer. Update with the GBP figure.
G_COUNT = "16"        # real number of Google reviews (as text). Update when it changes.
# Success-rate claim. It is shown ONLY on Asian visit visa pages (see asian_claim()), always with its scope, period and note.
# No other page may show "98%" or the word "guaranteed" (write_all() fails the build if one does).
SUCCESS_CLAIM = "98% success rate on Asian visit visa files*"
SUCCESS_PERIOD = "2025–2026"   # the period your own files cover. Change it, and re-check the figure, whenever you update the claim.
SUCCESS_NOTE = f"*Based on our files processed in {SUCCESS_PERIOD}. Final decision rests with the embassy."
ASIAN_REGIONS = {"south-asia", "east-asia", "central-asia", "middle-east"}
# only profiles checked in Oct 2026 (the old /alarbabtravels Facebook, Instagram and X links no longer exist; LinkedIn unverified)
SOCIAL = [("fb", B["socials"]["facebook"], "Facebook"), ("ig", B["socials"]["instagram"], "Instagram")]

e = H.escape

# ------------------------------------------------------------------ icons (inline SVG, 24x24)
_P = {
 "wa": '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>',
 "fb": '<path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/>',
 "x": '<path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>',
 "in": '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
 "ig": '<rect x="3" y="3" width="18" height="18" rx="5.2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.1" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.2"/>',
 "phone": '<path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>',
 "pin": '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>',
 "clock": '<path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>',
 "gmail": '<path fill="#4285F4" d="M1.636 21.002h3.819V11.73L0 7.638v11.728c0 .905.732 1.636 1.636 1.636z"/><path fill="#34A853" d="M18.545 21.002h3.819c.904 0 1.636-.732 1.636-1.636V7.638l-5.455 4.092z"/><path fill="#FBBC04" d="M18.545 4.638v7.092L24 7.638V5.457c0-2.023-2.309-3.178-3.927-1.964z"/><path fill="#EA4335" d="M5.455 11.73V4.638L12 9.548l6.545-4.91v7.092L12 16.64z"/><path fill="#C5221F" d="M0 5.457v2.181l5.455 4.092V4.638L3.927 3.493C2.309 2.28 0 3.434 0 5.457z"/>',
}

# outline icons (stroke = currentColor) that replace the emoji used as icons
_S = {
 "plane": '<path d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5z"/>',
 "shield": '<path d="M12 3l8 3v6c0 4.5-3.2 8-8 9-4.8-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
 "kaaba": '<rect x="4" y="6" width="16" height="14" rx="1.5"/><path d="M4 10.5h16M12.5 20v-5h3.5v5"/>',
 "hotel": '<rect x="5" y="3" width="14" height="18" rx="1.5"/><path d="M9 7.5h2M13 7.5h2M9 11.5h2M13 11.5h2M10 21v-4h4v4"/>',
 "bed": '<path d="M3 19V6M3 15h18v4M21 15v-2.5a3 3 0 0 0-3-3h-7V15"/><circle cx="7" cy="11.5" r="1.7"/>',
 "suitcase": '<rect x="3" y="7.5" width="18" height="12.5" rx="2"/><path d="M9 7.5V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5v2M8 7.5V20M16 7.5V20"/>',
 "briefcase": '<rect x="3" y="7.5" width="18" height="12.5" rx="2"/><path d="M9 7.5V6a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 6v1.5M3 13h18M11 13v1.8h2V13"/>',
 "family": '<circle cx="9" cy="8" r="3"/><path d="M3 20v-1a5 5 0 0 1 5-5h2a5 5 0 0 1 5 5v1"/><circle cx="17" cy="9.5" r="2.4"/><path d="M17.5 14.2a4 4 0 0 1 3.5 4V20"/>',
 "home": '<path d="M3.5 11L12 3.5 20.5 11"/><path d="M5.5 9.5V20h5v-6h3v6h5V9.5"/>',
 "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
 "award": '<circle cx="12" cy="9" r="6"/><path d="M8.7 14.3L7.5 21 12 18.5 16.5 21l-1.2-6.7"/>',
 "tag": '<path d="M3 12.5V4h8.5L21 13.5 13.5 21z"/><circle cx="7.8" cy="8.8" r="1.3"/>',
 "clock2": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/>',
 "bolt": '<path d="M13 2.5L4.5 13.5H11l-1 8L19.5 10H13z"/>',
 "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3.2 3.4 3.2 14.6 0 18M12 3c-3.2 3.4-3.2 14.6 0 18"/>',
 "percent": '<path d="M19 5L5 19"/><circle cx="7.2" cy="7.2" r="2.2"/><circle cx="16.8" cy="16.8" r="2.2"/>',
 "ticket": '<path d="M3 7.5h18V10a2 2 0 0 0 0 4v2.5H3V14a2 2 0 0 0 0-4z"/><path d="M14.5 8v8" stroke-dasharray="1.8 2"/>',
 "medical": '<rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M12 8v8M8 12h8"/>',
 "bus": '<rect x="4" y="4" width="16" height="13" rx="2.5"/><path d="M4 11h16M7.5 20v-3M16.5 20v-3"/><circle cx="8" cy="14" r=".4"/><circle cx="16" cy="14" r=".4"/>',
 "passport": '<rect x="5" y="3" width="14" height="18" rx="2"/><circle cx="12" cy="10.5" r="3"/><path d="M9 17h6"/>',
 "bulb": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
 "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
 "grad": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5M22 9v6"/>',
 "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
 "eye": '<path d="M2 12s3.8-7 10-7 10 7 10 7-3.8 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "gem": '<path d="M6 4h12l4 5-10 11L2 9z"/><path d="M2 9h20M9 4L7 9l5 11 5-11-2-5"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "pause": '<path d="M8.5 5v14M15.5 5v14"/>',
 "play": '<path d="M8 4.5v15l11-7.5z"/>',
}

def ico(name, size=22, color="currentColor", cls="i"):
    if name in _S:
        return (f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.9" '
                f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{_S[name]}</svg>')
    return f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" aria-hidden="true" focusable="false">{_P[name]}</svg>'

# tile colours for the contact lists (brand colours)
IC_TILE = {"📍": ("ic-map", "pin", "#EA4335"), "📞": ("ic-call", "phone", "#ffffff"), "✉": ("ic-mail", "gmail", None), "🕑": ("ic-time", "clock", "#5f6368"),
           "💬": ("ic-wa", "wa", "#ffffff"), "👍": ("ic-fb", "fb", "#1877F2")}

def _tile(m):
    cls, name, col = IC_TILE[m.group(1)]
    return f'<span class="ic {cls}">{ico(name, 24, col) if col else ico(name, 24, None)}</span>'

# every emoji still used as an icon -> outline SVG (flags are handled separately and become flag images)
EMO = {"👨‍👩‍👧": "family", "✈️": "plane", "✈": "plane", "🛡": "shield", "🕋": "kaaba", "🏨": "hotel", "🛏": "bed", "🌴": "suitcase", "🧳": "suitcase",
       "💼": "briefcase", "🏠": "home", "✅": "check", "🏆": "award", "💰": "tag", "💸": "percent", "🕑": "clock2", "⚡": "bolt", "🌍": "globe",
       "🌐": "globe", "🎫": "ticket", "🩺": "medical", "🚌": "bus", "🛂": "passport", "◈": "passport", "💡": "bulb", "📅": "calendar",
       "🎓": "grad", "🎯": "target", "🔭": "eye", "💎": "gem"}
_EMO_RX = re.compile("|".join(re.escape(k) for k in sorted(EMO, key=len, reverse=True)))
_FLAG_RX = re.compile("([\U0001F1E6-\U0001F1FF])([\U0001F1E6-\U0001F1FF])")

def _flag_img(m):
    code = "".join(chr(ord(c) - 0x1F1E6 + 97) for c in m.groups())
    return f'<img class="fl" src="https://flagcdn.com/w40/{code}.png" srcset="https://flagcdn.com/w80/{code}.png 2x" width="20" height="14" alt="" loading="lazy" decoding="async">'

def _text_emoji(m):
    t = _FLAG_RX.sub(_flag_img, m.group(1))
    t = _EMO_RX.sub(lambda x: ico(EMO[x.group(0)], 18, cls="i e"), t)
    return ">" + t.replace("️", "") + "<"

def finish_icons(html):
    """Swap emoji for SVG icons in the final page HTML (buttons, contact lists, feature tiles, chips)."""
    html = re.sub(r'<span class="ic">(📍|📞|✉|🕑|💬|👍)</span>', _tile, html)
    html = html.replace("💬 ", ico(("wa"), 18) + " ").replace("💬", ico("wa", 20))
    html = html.replace("📞 ", ico("phone", 17) + " ").replace("📞", ico("phone", 18))
    html = html.replace("📍 Get directions", ico("pin", 17) + " Get directions").replace("📍 Show map", ico("pin", 17, "#EA4335") + " Show map")
    # remaining emoji inside text nodes only (never inside attributes, scripts or styles)
    parts = re.split(r"(<script.*?</script>|<style.*?</style>)", html, flags=re.S)
    parts = [p if p.startswith(("<script", "<style")) else re.sub(r">([^<]*)<", _text_emoji, p) for p in parts]
    return "".join(parts)

def attr(s):
    return H.escape(s, quote=False).replace('"', "&quot;")

def fit_desc(d):
    d = " ".join(d.split())
    if len(d) < 110:
        d += " Free assessment at our Blue Area office, Islamabad."
    if len(d) > 160:
        d = d[:157].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return d

# ------------------------------------------------------------------ images
UNS = dict(th="1528181304800-259b08848526", my="1596422846543-75c6fc197f07", id="1537996194471-e657df975ab4",
           sg="1525625293386-3f8f99389edd", umrah="1591604129939-f1efa4d9f7fa", np="1544735716-392fe2489ffa",
           ae="1512453979798-5ea266f8880c", dubai2="1518684079-3c830dcef090", pk="1589182373726-e4f658ab50f0",
           it="1552832230-c0197dd311b5", fr="1502602898657-3e91760cbb34", cta="1507608616759-54f48f0af0ee",
           # topic photos for the guide pages (Unsplash, free licence)
           g_plan="1524850011238-e3d235c7d4c9", g_bank="1554224155-6726b3ff858f", g_letter="1455390582262-044cdead277a",
           g_passport="1581553673739-c4906b5d0de8", g_passport2="1655722725332-9925c96dd627")
KNOWN_BY_CODE = {"th": UNS["th"], "my": UNS["my"], "id": UNS["id"], "sg": UNS["sg"], "np": UNS["np"], "ae": UNS["ae"],
                 "pk": UNS["pk"], "it": UNS["it"], "fr": UNS["fr"], "sa": UNS["umrah"]}

def uns_id(url):
    m = re.match(r"https://images\.unsplash\.com/photo-([\w-]+)", url or "")
    return m.group(1) if m else None

def U(pid, w):
    if pid.startswith("/"):            # owner's own photo in assets/ (one size, already cache-busted)
        return pid
    return f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&q=70&w={w}"

def picture(pid, alt, w=800, h=533, sizes="(max-width:600px) 100vw, 400px", lazy=True, cls="", widths=(400, 800, 1200), high=False):
    srcset = pid if pid.startswith("/") else ", ".join(f"{U(pid, x)} {x}w" for x in widths)
    attrs = 'loading="lazy" decoding="async"' if lazy else ('fetchpriority="high" decoding="async"' if high else 'decoding="async"')
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{U(pid, w)}" srcset="{srcset}" sizes="{sizes}" alt="{e(alt)}" width="{w}" height="{h}" {attrs}>'

def flag(code, alt="", w=44):
    if not code:
        return ""
    return f'<img src="https://flagcdn.com/w80/{code}.png" srcset="https://flagcdn.com/w160/{code}.png 2x" width="{w}" height="{round(w*0.68)}" alt="{e(alt)}" loading="lazy" decoding="async">'

def wa(msg):
    return f"{WA}?text={quote(msg)}"

# hero "WhatsApp us" button for pages whose hero has no other WhatsApp button (route_wa points it at the page's desk)
WA_HERO = f'<a class="btn wa" href="{WA}" target="_blank" rel="noopener">💬 WhatsApp us</a>'

# ------------------------------------------------------------------ data model
REGION_FLAG = {"schengen": "eu", "united-states": "us", "united-kingdom": "gb", "canada": "ca", "australia": "au"}
REGION_IMG = {"schengen": UNS["fr"], "middle-east": UNS["ae"], "south-asia": UNS["th"]}
REGION_LOCAL = {"south-asia": "south-asia-ho-chi-minh-city.webp", "east-asia": "east-asia-taipei.webp",
                "central-asia": "central-asia-astana.webp", "middle-east": "middle-east-dubai-marina.webp",
                "schengen": "schengen-cologne.webp", "united-kingdom": "united-kingdom-york.webp", "canada": "canada-quebec-city.webp",
                "united-states": "united-states-san-francisco.webp"}
REGIONS = {r["slug"]: r for r in DATA["regions"]}
for r in DATA["regions"]:
    rp = PHOTOS.get("R:" + r["slug"])
    r["img"] = (rp[0][1] if rp else None) or uns_id(r["image"]) or REGION_IMG.get(r["slug"])
    if r["slug"] in REGION_LOCAL:                     # owner's photos (assets/regions/)
        r["img"] = f'/assets/regions/{REGION_LOCAL[r["slug"]]}?v={asset_hash("regions/" + REGION_LOCAL[r["slug"]])}'
    r["flag"] = REGION_FLAG.get(r["slug"])
    _tpl_times = {v["processingTime"] for v in DATA["visaTypeTemplate"]}
    if isinstance(r["visas"], list):
        for _v in r["visas"]:
            if _v.get("processingTime") in _tpl_times and r["slug"] not in ("united-states", "united-kingdom", "canada", "australia"):
                _v["processingTime"] = "Varies by embassy and season."
    if not isinstance(r["visas"], list) or not r["visas"]:
        r["visas"] = json.loads(json.dumps(DATA["visaTypeTemplate"]).replace("{{C}}", r["name"]))
        for _v in r["visas"]:
            _v["processingTime"] = "Varies by embassy and season."

LIST_REGION = [("schengen", "schengen"), ("south-asia", "south-asia"), ("central-asia", "central-asia"),
               ("north-africa", "north-africa"), ("southern-africa", "southern-africa"), ("middle-east", "middle-east"),
               ("east-asia", "east-asia"), ("south-america", "south-america"), ("mexico", "south-america"),
               ("oceania", "oceania"), ("ireland", "united-kingdom")]
COUNTRIES, BY_REGION = {}, {}
for key, reg in LIST_REGION:
    for c in DATA["countries"][key]:
        BY_REGION.setdefault(reg, [])
        if c["slug"] in COUNTRIES:                     # e.g. Turkey listed twice: link to the first page
            if COUNTRIES[c["slug"]] not in BY_REGION[reg]:
                BY_REGION[reg].append(COUNTRIES[c["slug"]])
            continue
        c = dict(c, region=reg)
        c.setdefault("popularPlaces", [])
        c["url"] = f"/countries/{reg}/{c['slug']}"
        c["gallery"] = [g for g in PHOTOS.get(c["slug"], []) if g[1]]
        c["img"] = (c["gallery"][0][1] if c["gallery"] else None) or uns_id(c["image"]) or KNOWN_BY_CODE.get(c["code"])
        if c["slug"] == "thailand":                    # keep the temple photo used in the home hero
            c["img"] = UNS["th"]
        c["docs_clean"] = c["docs"]
        COUNTRIES[c["slug"]] = c
        BY_REGION[reg].append(c)

def visit_visa(reg):
    vs = REGIONS[reg]["visas"]
    return vs[0] if vs else None

PACKAGES = DATA["packages"]
PKG_COUNTRY = {"thailand-phuket": "thailand", "malaysia-kl": "malaysia", "indonesia-bali": "indonesia", "singapore-city": "singapore",
               "nepal-himalayas": "nepal", "dubai-desert-safari": "united-arab-emirates", "italy-schengen": "italy"}
for p in PACKAGES:
    p["url"] = f"/packages/{p['id']}"
    cc = COUNTRIES.get(PKG_COUNTRY.get(p["id"], ""))
    p["img"] = (cc["img"] if cc and p["id"] != "thailand-phuket" else None) or uns_id(p["image"])

def cimg(slug, fallback):
    c = COUNTRIES.get(slug)
    return c["img"] if c and c.get("gallery") else fallback

# home hero destinations (lat/lon for live weather; x/y = flight-arc end point)
# img = Unsplash id, or local=<file in assets/hero/> for the owner's own photos
HERO = [
 dict(n="Thailand", city="Phuket (Phang Nga Bay)", lat=7.88, lon=98.39, code="HKT", visa="e-Visa", x=600, y=230, img="thai-lagoon", url="/countries/south-asia/thailand"),
 dict(n="Malaysia", city="Kuala Lumpur (Petronas)", lat=3.14, lon=101.69, code="KUL", visa="eVisa", x=660, y=320, img=cimg("malaysia", UNS["my"]), url="/countries/south-asia/malaysia"),
 dict(n="Indonesia", city="Bali Island (Ulun Danu)", lat=-8.41, lon=115.19, code="DPS", visa="e-Visa", x=700, y=400, img=cimg("indonesia", UNS["id"]), url="/countries/south-asia/indonesia"),
 dict(n="Singapore", city="Marina Bay & Sentosa", lat=1.29, lon=103.86, code="SIN", visa="e-Visa", x=640, y=360, img="singapore-marina", url="/countries/south-asia/singapore"),
 dict(n="Nepal", city="Kathmandu & Himalayas", lat=27.7, lon=85.32, code="KTM", visa="Visa on Arrival", x=470, y=210, img=cimg("nepal", UNS["np"]), url="/countries/south-asia/nepal"),
 dict(n="Vietnam", city="Ho Chi Minh City (Saigon)", lat=10.82, lon=106.63, code="SGN", visa="e-Visa", x=680, y=270, img="1521019795854-14e15f600980", url="/countries/south-asia/vietnam"),
]

# owner's country photos (assets/countries/). Applied after HERO and PACKAGES so the slider and package covers keep theirs.
COUNTRY_LOCAL = {"thailand": "thailand-chiang-mai.webp", "malaysia": "malaysia-kuala-lumpur.webp",
                 "singapore": "singapore-marina-bay.webp", "indonesia": "indonesia-bali-ulun-danu.webp"}
for _s, _f in COUNTRY_LOCAL.items():
    COUNTRIES[_s]["img"] = f"/assets/countries/{_f}?v={asset_hash('countries/' + _f)}"
PKG_LOCAL = {"dubai-desert-safari": "dubai-burj-khalifa.webp", "italy-schengen": "italy-venice-rialto.webp",
             "nepal-himalayas": "nepal-kathmandu-boudhanath.webp"}
UMRAH_IMG = f"/assets/umrah/umrah-makkah-madinah.webp?v={asset_hash('umrah/umrah-makkah-madinah.webp')}"   # owner's Umrah photo
for p in PACKAGES:                                # package covers use the same owner photos
    if PKG_COUNTRY.get(p["id"]) in COUNTRY_LOCAL:
        p["img"] = COUNTRIES[PKG_COUNTRY[p["id"]]]["img"]
    elif p["id"].startswith("umrah"):
        p["img"] = UMRAH_IMG
    if p["id"] in PKG_LOCAL:                     # owner's own package photos (assets/packages/)
        p["img"] = f"/assets/packages/{PKG_LOCAL[p['id']]}?v={asset_hash('packages/' + PKG_LOCAL[p['id']])}"

def AU(pid, w):
    """Absolute image URL for Open Graph / schema (local photos need the domain)."""
    return BASE + pid if pid.startswith("/") else U(pid, w)

def hero_img(h, w):
    """URL of a hero photo: local files are served from /assets/hero/ with a cache-busting hash."""
    if h.get("local"):
        return f'/assets/hero/{h["local"]}?v={asset_hash("hero/" + h["local"])}'
    return hero_local(h["img"], w) or HQ(h["img"], w)

def hero_local(pid, w):
    """Self-hosted WebP copy of a hero photo (assets/hero/<id>-<1000|1500|2000>.webp), or None if it was not downloaded."""
    for ww in (1000, 1500, 2000):
        if ww >= w and os.path.exists(os.path.join(ROOT, "assets", "hero", f"{pid}-{ww}.webp")):
            return f"/assets/hero/{pid}-{ww}.webp?v={asset_hash(f'hero/{pid}-{ww}.webp')}"
    return None

def HQ(pid, w):
    """Hero photos: the slot is tall (about 700x870), so a landscape photo is scaled up by its HEIGHT. Ask for a big, cleaner copy (q=75, up to 2000px)."""
    return U(pid, w).replace("q=70", "q=75")

def hero_srcset(h):
    if h.get("local"):
        return ""
    return ", ".join(f"{hero_local(h['img'], w) or HQ(h['img'], w)} {w}w" for w in (1000, 1500, 2000))

# official portals for the "Sources" box on country pages (only well-known government sites)
OFFICIAL = {
 "malaysia": [("Malaysia eVISA portal", "https://malaysiavisa.imi.gov.my/")],
 "turkey": [("Turkey Ministry of Foreign Affairs: visa information for foreigners", "https://www.mfa.gov.tr/visa-information-for-foreigners.en.mfa"), ("Turkey Ministry of Foreign Affairs: sticker visa pre-application system", "https://www.mfa.gov.tr/pre-application-system-for-turkish-sticker-visa.en.mfa"), ("Turkey e-Visa website", "https://www.evisa.gov.tr/")],
 "azerbaijan": [("Azerbaijan ASAN e-Visa", "https://evisa.gov.az/"), ("Embassy of Azerbaijan in Pakistan: visa information", "https://islamabad.mfa.gov.az/en/category/consular-service-and-visa")],
 "sri-lanka": [("Sri Lanka ETA (official)", "https://www.eta.gov.lk/slvisa/")],
 "singapore": [("Singapore ICA: check if you need an entry visa", "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements")],
 "thailand": [("Thailand e-Visa (official)", "https://www.thaievisa.go.th/")],
 "indonesia": [("Indonesia e-Visa (Imigrasi)", "https://evisa.imigrasi.go.id/")],
 "cambodia": [("Cambodia e-Visa (official)", "https://www.evisa.gov.kh/"), ("Cambodia e-Visa: visa type information", "https://www.evisa.gov.kh/information/visa_type/4")],
 "vietnam": [("Vietnam e-Visa (official)", "https://evisa.gov.vn/")],
 "egypt": [("Egypt e-Visa portal", "https://visa2egypt.gov.eg/")],
 "oman": [("Royal Oman Police e-Visa", "https://evisa.rop.gov.om/")],
 "bahrain": [("Bahrain e-Visa (official)", "https://www.evisa.gov.bh/"), ("Bahrain e-Visa: countries eligible online", "https://www.evisa.gov.bh/list-of-online-visa-country.html"), ("Bahrain e-Visa: process for obtaining a visa", "https://www.evisa.gov.bh/VisaBhr2En.html")],
 "uzbekistan": [("Uzbekistan e-Visa portal", "https://e-visa.gov.uz/"), ("Embassy of Uzbekistan in Pakistan: consular services", "https://pakistan.mfa.uz/en/page/consular-services")],
 "japan": [("Embassy of Japan in Pakistan: visa information", "https://www.pk.emb-japan.go.jp/itpr_ja/VisaInfo.html")],
 "saudi-arabia": [("Saudi visa platform", "https://visa.visitsaudi.com/")],
 "kenya": [("Kenya eTA (official)", "https://www.etakenya.go.ke/")],
 "philippines": [("Philippine DFA: visa general information", "https://consular.dfa.gov.ph/visa-general-info/"), ("Philippine DFA: visa FAQs", "https://consular.dfa.gov.ph/visa-faqs/"),
                 ("eVisaPH: check if you need a visa", "https://evisa.gov.ph/"), ("eVisaPH: Philippine visa policy", "https://evisa.gov.ph/page/policy")],
 "tajikistan": [("Tajikistan e-Visa portal (Ministry of Foreign Affairs)", "https://www.evisa.tj/"), ("Tajikistan e-Visa: Get informed", "https://www.evisa.tj/#/getinformed"),
                ("Tajikistan e-Visa: FAQ", "https://www.evisa.tj/#/help")],
 "australia": [("Visitor visa subclass 600 (Home Affairs)", "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600")],
}
REGION_OFFICIAL = {
 "united-kingdom": [("UK Standard Visitor visa (GOV.UK)", "https://www.gov.uk/standard-visitor")],
 "united-states": [("US visitor visas (travel.state.gov)", "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html"), ("DS-160 online form (CEAC)", "https://ceac.state.gov/genniv/")],
 "canada": [("Visit Canada (IRCC)", "https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada.html")],
 "australia": [("Visitor visa subclass 600 (Home Affairs)", "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600")],
 "schengen": [("Schengen visa policy (European Commission)", "https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/visa-policy_en")],
}
REFUSAL = [("Weak financial proof", "Bank statements with sudden large deposits, a low closing balance or no maintenance certificate."),
           ("Unclear ties to Pakistan", "No proof of job, business, property or family that shows you will return."),
           ("Mismatched details", "Names, dates or salary figures that differ between the form, bank statement and letters."),
           ("Incomplete bookings", "Missing hotel or flight reservations for the full stay, or insurance below the required cover."),
           ("Weak cover letter", "No clear purpose of visit, itinerary or explanation of who pays for the trip.")]
APPOINTMENT_CENTRES = [("United Kingdom", "VFS Global (UK Visa Application Centre)", "/countries/united-kingdom"),
                       ("United States", "CGI Federal fee & appointment; interview at US Embassy Islamabad or Consulate Karachi", "/countries/united-states"),
                       ("Spain", "BLS International", "/countries/schengen/spain"), ("Netherlands", "VFS Global", "/countries/schengen/netherlands"),
                       ("Sweden", "VFS Global", "/countries/schengen/sweden"), ("Greece", "GVCW visa centre", "/countries/schengen/greece"),
                       ("France", "France-Visas online portal", "/countries/schengen/france"), ("Denmark", "ApplyVisa portal", "/countries/schengen/denmark"),
                       ("Norway", "UDI online portal", "/countries/schengen/norway"), ("Other Schengen states", "VFS Global / BLS / Gerry's, depending on the embassy", "/countries/schengen")]

# ------------------------------------------------------------------ page text
VISA_SERVICES = [
 ("tourist-visa", "Tourist Visa", "🌴", "Plan your holiday with tourist visa processing and @N@ country guides.", "visit"),
 ("family-visit-visa", "Family Visit Visa", "👨‍👩‍👧", "Reunite with family abroad through our reliable visit visa service.", "visit"),
 ("family-reunification", "Family Reunification", "🏠", "Long-term family reunion visas with documentation support.", None),
 ("schengen-visa", "Schengen Visa", "🇪🇺", "Single visa to explore 29 European countries seamlessly.", "visit"),
 ("business-visa", "Business Visa", "💼", "Business and corporate travel visas, fast and reliable.", "business"),
 ("student-visa", "Student Visa", "🎓", "Study abroad support — UK, USA, Canada, Australia & more.", None),
]
SERVICE_DEST = {
 "tourist-visa": ["thailand", "malaysia", "singapore", "indonesia", "sri-lanka", "vietnam", "japan", "cambodia", "azerbaijan", "turkey"],
 "family-visit-visa": ["united-arab-emirates", "saudi-arabia", "germany", "france", "italy", "ireland"],
 "family-reunification": ["germany", "france", "italy", "spain", "netherlands", "sweden"],
 "schengen-visa": ["germany", "france", "italy", "spain", "netherlands", "switzerland", "austria", "belgium", "greece", "portugal", "sweden", "norway"],
 "business-visa": ["china", "united-arab-emirates", "turkey", "germany", "south-korea", "japan"],
 "student-visa": ["ireland", "germany", "malaysia", "china", "australia", "new-zealand"],
}
SERVICE_REGIONS = {"student-visa": ["united-kingdom", "united-states", "canada", "australia"],
                   "schengen-visa": ["schengen"], "tourist-visa": ["schengen", "united-states", "united-kingdom"]}
INCLUDED = ["End-to-end documentation & embassy support", "Personalized visa pathway assessment", "Document checklist tailored to your case",
            "Form filling & application review", "Embassy appointment booking", "Interview preparation & coaching", "Real-time application tracking"]
PROCESS = [("Consultation", "We review your profile and select the best embassy based on your itinerary."),
           ("Documentation", "We compile your cover letter, financial proofs, and bookings."),
           ("Appointment", "We secure an early appointment at VFS / BLS / Gerry's."),
           ("Submission", "You submit the file and biometrics at the center.")]
FAQ_GENERAL = [(f["q"], f["a"]) for f in DATA["faqSchengenGeneral"]]
FAQ_AIR = [(f["q"], f["a"]) for f in DATA["faqAir"]]
COUNTRY_PAA = {
 "malaysia": [("Can I get a Malaysia visa in 2 days?", "Malaysia eVisa decisions usually take a few working days, and we can't promise a 2-day result. Apply at least a week before travel; tell us your date and we advise the fastest option available.")],
 "italy": [("Who can help me with an Italy visa in Islamabad?", "Our Blue Area office prepares Italy Schengen files end to end: document check, appointment, insurance, hotel and flight reservations, and cover letter. Start with a free assessment on WhatsApp.")],
}

# priority Asian destinations: bespoke title/description, a "how we prepare your file" block, extra FAQs and sources (official facts only, no fees, no approval promises)
COUNTRY_SEO = {
 "south-korea": ("South Korea Visa from Pakistan: Documents & Process 2026",
                 "South Korea visit visa from Pakistan: the 7-document checklist, funds and travel-history tips, and how we prepare your file in Blue Area, Islamabad. WhatsApp {PHONE_D}"),
 "japan": ("Japan Visa from Pakistan: Documents & Process 2026",
           "Japan visit visa from Pakistan: the checklist, itinerary and funds tips, and how we prepare your file in Blue Area, Islamabad. Free file check on WhatsApp {PHONE_D}"),
 "vietnam": ("Vietnam Visa from Pakistan: e-Visa & Documents 2026",
             "Vietnam visa from Pakistan: documents for the official e-Visa, photo and passport tips, and file help in Blue Area, Islamabad. Free check on WhatsApp {PHONE_D}"),
}
COUNTRY_FOCUS = {
 "south-korea": ("How we prepare your South Korea visit visa file",
                 "South Korean officers read the whole file together, so each paper has to tell the same story. This is what we check before you submit.",
                 ["<b>Trip plan</b>: a day-by-day itinerary that matches your flight and hotel reservations",
                  "<b>Funds</b>: bank statements that fit your income, with the source of any large deposit explained",
                  "<b>Ties to Pakistan</b>: employment, business or study letters, and family documents that show you will return",
                  "<b>Travel history</b>: earlier visas and stamps in order; a first trip abroad needs stronger funds and ties evidence",
                  "<b>Current form and route</b>: we confirm them on the official portal and embassy page before submission"]),
 "japan": ("How we prepare your Japan visit visa file",
           "Japan's checklist is short, so each document is read closely. We make sure the papers agree with each other before you submit.",
           ["<b>Itinerary</b>: a day-by-day schedule of stay in the format the embassy asks for, matching your bookings",
            "<b>Funds</b>: recent bank statements that fit your income and the length of the trip",
            "<b>Ties to Pakistan</b>: an employer or business letter and family documents that show you will return",
            "<b>Same details everywhere</b>: names, dates and employer written the same way on every paper",
            "<b>Current route</b>: we confirm the application route and forms with the embassy page before you apply"]),
 "vietnam": ("How we prepare your Vietnam e-Visa application",
             "Vietnam issues visas for Pakistani travellers through its official e-Visa portal. Most problems come from small mistakes in the upload, so we check them first.",
             ["<b>Passport scan</b>: clear, uncropped and with at least the validity the portal asks for",
              "<b>Photo</b>: a recent portrait that meets the portal's size and background rules",
              "<b>Details match</b>: name, passport number and dates typed exactly as in the passport",
              "<b>Entry options</b>: we choose the entry type and dates offered on the portal for your trip",
              "<b>Official portal only</b>: apply on evisa.gov.vn; we do not use look-alike sites"]),
}
COUNTRY_PAA.update({
 "south-korea": [("Is a South Korea visa easy for Pakistani travellers?", "It depends on the whole file: purpose of the trip, funds, ties to Pakistan and travel history. We cannot promise approval; we make sure your file is complete and consistent before you submit. The embassy makes the decision."),
                 ("Can a first-time traveller apply for a South Korea visa?", "Yes. First-time applicants usually need to show clear funds, a realistic itinerary and strong reasons to return to Pakistan. Send us your profile on WhatsApp and we tell you what to strengthen."),
                 ("Where do I check the official South Korea visa rules?", "On the Korea Visa Portal and the Embassy of the Republic of Korea in Pakistan. Both are linked in the sources section of this page.")],
 "japan": [("Is a Japan visa easy for Pakistani travellers?", "Japan reads each paper closely, so consistency matters more than volume. We cannot promise approval; we check that your itinerary, funds and ties agree before you submit. The embassy makes the decision."),
           ("Do I need an itinerary for the Japan visa?", "A day-by-day plan of your stay is normally part of a Japan visit visa file. It should match your flight and hotel bookings. We prepare it with you."),
           ("Where do I check the official Japan visa rules?", "On the Embassy of Japan in Pakistan visa page and the Ministry of Foreign Affairs of Japan, both linked in the sources section of this page.")],
 "vietnam": [("Do Pakistanis apply for a Vietnam visa online?", "Vietnam issues e-Visas through its official portal, evisa.gov.vn. You upload your passport page and photo, choose your entry options and follow the portal's steps. We check the upload before you submit."),
             ("What is the most common Vietnam e-Visa mistake?", "A passport scan or photo that does not meet the portal's rules, or details typed differently from the passport. Both can delay the application."),
             ("Can you apply for my Vietnam e-Visa?", "Yes. We prepare and check your application from our Blue Area office. Final decision rests with the Vietnamese authorities.")],
})
OFFICIAL.setdefault("south-korea", [("Korea Visa Portal (official)", "https://www.visa.go.kr/"), ("Embassy of the Republic of Korea in Pakistan", "https://overseas.mofa.go.kr/pk-en/index.do")])
OFFICIAL["japan"] = OFFICIAL.get("japan", []) + [("Ministry of Foreign Affairs of Japan: visas", "https://www.mofa.go.jp/j_info/visit/visa/index.html")]

DOC_GROUPS = [
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

ROUTE_PHRASE = {"Online e-visa": "an online e-visa", "Online ETA": "an online ETA", "Visa on arrival / e-visa": "a visa on arrival or e-visa",
                "Schengen visa (embassy / visa centre)": "a Schengen visa at the embassy or its visa centre", "Embassy / visa centre": "the embassy or its visa centre"}

def proc_phrase(vv):
    p = (vv["processingTime"] if vv else "").strip().rstrip(".")
    if not p or p.lower().startswith("varies"):
        return "processing time varies by embassy and season"
    return "processing typically takes " + p.lower().replace("typically ", "")

ONLINE_ROUTE = {"sri-lanka": "Online ETA", "kenya": "Online ETA"}
ROUTE_OVERRIDE = {"philippines": "Embassy / visa centre", "uzbekistan": "Embassy / visa centre", "japan": "Embassy / visa centre",
                  "turkey": "E-visa or embassy", "azerbaijan": "E-visa or embassy"}   # DFA: temporary visitor visa applied for in person at the embassy

def visa_route(c):
    if c["slug"] in ROUTE_OVERRIDE:
        return ROUTE_OVERRIDE[c["slug"]]
    if c["slug"] in ONLINE_ROUTE:
        return ONLINE_ROUTE[c["slug"]]
    if c["slug"] in OFFICIAL and c["region"] not in ("oceania",):
        return "Online e-visa"
    t = (c["intro"] + " " + c["description"] + " " + " ".join(c["docs_clean"])).lower()
    if c["region"] == "schengen":
        return "Schengen visa (embassy / visa centre)"
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

PAA_AGENCY = [
 ("How do I choose the best travel agency or visa consultant in Islamabad?", "Check that the agency is licensed by the Department of Tourist Services (DTS), has a real office you can visit, shows its Google reviews openly, gives you a written document checklist, and quotes the full cost before you pay. AL ARBAB TRAVEL AND TOURS is in Eagle Plaza, Blue Area, Islamabad, and is licensed by the Department of Tourist Services (DTS)."),
 ("How much does a travel agency charge for a visa?", "Service charges depend on the country, visa type and how much work your file needs. We quote the full cost on WhatsApp before you pay anything, and the first consultation and document check are free."),
 ("Can a visa consultant guarantee my visa?", "No honest consultant can. The decision is always made by the embassy. A good consultant reduces refusal risk by checking your documents, finances and cover letter before you apply."),
]
FAQ_VISA = [
 ("Is AL ARBAB TRAVEL AND TOURS a licensed travel agency?", "Yes. We are licensed by the Department of Tourist Services (DTS), Government of Pakistan, and our office is in Eagle Plaza, Blue Area, Islamabad."),
 ("Which visas do you process from Islamabad?", "We offer two services. Visit visa processing for Asian countries: we process and follow up your visa. Visa file preparation and guidance for Europe, Schengen, the UK, the USA, Canada, Australia and other countries: we prepare and organise your file and guide you, and the embassy makes the final decision. We help with tourist, family visit, family reunification, business and student visas, with @N@ country guides."),
 ("Do you publish a visa success rate?", "Only for Asian visit visa files, and only on those pages, with the period it covers and a note that the embassy decides. We publish no rate for other destinations, because every embassy applies its own standards. What we do for every file is check your documents for free before you apply, so gaps are fixed early."),
 ("Who makes the final visa decision?", "The final decision to grant or refuse any visa rests solely with the respective embassy, high commission or consulate. We prepare and represent your file to give it the strongest possible chance."),
]
FAQ_UMRAH = [
 ("How much does an Umrah package from Pakistan cost in 2026?", "Prices change with the season, airfare and hotel availability, so we quote on the day. Choose Economy, 3 Star, 4 Star or 5 Star and send your dates on WhatsApp for today's price."),
 ("Who arranges my Umrah package?", "AL ARBAB TRAVEL AND TOURS is a DTS-licensed travel agency in Blue Area, Islamabad. We arrange Umrah packages, hotels and flights, and we prepare your Umrah visa file. The Saudi authorities issue the visa and make the final decision."),
 ("Can I customize my Umrah itinerary?", "Yes. Choose your hotels in Makkah and Madinah, pick private GMC or luxury bus transport, and stay 7, 10, 15 or 30 days — as a group or private family package."),
]
ROUTES = [("London", "ISB → LHR", "PIA, EMIRATES, TURKISH"), ("Dubai", "ISB → DXB", "EMIRATES, FLYDUBAI, PIA"),
          ("Toronto", "ISB → YYZ", "TURKISH, EMIRATES, QATAR"), ("Jeddah", "ISB → JED", "PIA, SAUDI, FLYNAS"),
          ("New York", "ISB → JFK", "EMIRATES, TURKISH, QATAR"), ("Istanbul", "ISB → IST", "TURKISH AIRLINES"),
          ("Melbourne", "ISB → MEL", "EMIRATES, QATAR, THAI"), ("Doha", "ISB → DOH", "QATAR AIRWAYS, PIA")]

# ------------------------------------------------------------------ schema
def org_ld():
    return {"@context": "https://schema.org", "@type": ["TravelAgency", "LocalBusiness"], "@id": BASE + "/#org",
            "name": NAME, "url": BASE + "/", "logo": {"@type": "ImageObject", "url": LOGO, "width": 513, "height": 412}, "image": LOGO,
            # every value below is shown on the site (home, footer, contact, policies); nothing schema-only
            "description": ORG_DESC,
            "telephone": [PHONE_I, PHONE_SCHENGEN_I, LAND_I], "email": EMAIL,
            "address": {"@type": "PostalAddress", "streetAddress": "Eagle Plaza, Mezzanine No. 121, Fazal-e-Haq Road, Blue Area",
                        "addressLocality": "Islamabad", "addressRegion": "Islamabad Capital Territory", "postalCode": "44000", "addressCountry": "PK"},
            "geo": {"@type": "GeoCoordinates", "latitude": 33.7135, "longitude": 73.0673}, "hasMap": MAP_URL,
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "09:00", "closes": "20:00"}],
            "areaServed": [{"@type": "Country", "name": "Pakistan"}] + [{"@type": "City", "name": n} for n in ("Islamabad", "Rawalpindi")],
            "sameAs": [s[1] for s in SOCIAL],
            "knowsAbout": ["Visit visa processing for Asian countries", "Thailand visit visa", "Malaysia visit visa", "Singapore visit visa", "Indonesia visit visa",
                           "Visa file preparation and guidance", "Schengen visa", "UK Standard Visitor visa", "USA B1/B2 visa", "Canada visitor visa", "Australia visitor visa",
                           "Umrah packages", "Air ticketing", "Travel insurance"],
            "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "license", "name": "Travel agency licence",
                              "recognizedBy": {"@type": "GovernmentOrganization", "name": "Department of Tourist Services (DTS), Government of Pakistan"}},
            "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE_I, "contactType": "customer support", "areaServed": "PK"}]}

DISCLAIMER_LINE = f"{NAME} is a private travel and visa consultancy and is not affiliated with any embassy or government."
ORG_DESC = ("DTS-licensed travel agency and visa consultancy in Blue Area, Islamabad: visit visa processing for Asian countries, and visa file preparation "
            "and guidance for Europe, the UK, the USA, Canada, Australia and other countries. Air tickets, Umrah packages, hotels and travel insurance.")

def website_ld():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": NAME, "inLanguage": "en-PK", "publisher": {"@id": BASE + "/#org"}}

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + (u or "/")} for i, (n, u) in enumerate(items)]}

def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def service_ld(name, desc, url, extra=None):
    d = {"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc, "url": BASE + url,
         "provider": {"@id": BASE + "/#org"}, "areaServed": {"@type": "Country", "name": "Pakistan"}}
    d.update(extra or {})
    return d

# ------------------------------------------------------------------ chrome
NAV = [("/countries", "Destinations"), ("/air-ticketing", "Flights"), ("/umrah", "Umrah"),
       ("/packages", "Packages"), ("/pakistan-tours", "Pakistan Tours"), ("/eligibility-check", "Free Check"), ("/contact", "Contact")]   # "Visas" dropdown comes first (nav_dropdown)
CSS = open(os.path.join(ROOT, "assets", "style.css"), encoding="utf-8").read()
CSS = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
CSS = re.sub(r"\s*\n\s*", "", CSS)
CSS = re.sub(r"\s*([{};,>])\s*", r"\1", CSS).replace(";}", "}")
PAGE_THEME = "milky"   # page colours: "milky" (assets/theme-milky.css: milky glass) or None (the earlier sage green)
if PAGE_THEME:
    _pt = re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", f"theme-{PAGE_THEME}.css"), encoding="utf-8").read(), flags=re.S)
    _pt = re.sub(r"\s*[\r\n]+\s*", "", _pt)
    CSS += re.sub(r"\s*([{};,>])\s*", r"\1", _pt).replace(";}", "}")
NCARD_THEME = "mix"   # colour theme of the destination cards: "mix" (assets/ncard-mix.css), "glow" (dark blue, assets/ncard-glow.css) or None (plain dark)
if NCARD_THEME:
    _gl = re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", f"ncard-{NCARD_THEME}.css"), encoding="utf-8").read(), flags=re.S)
    _gl = re.sub(r"\s*[\r\n]+\s*", "", _gl)
    CSS += re.sub(r"\s*([{};,>])\s*", r"\1", _gl).replace(";}", "}")
SVG_DEFS = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><symbol id="lgmark" viewBox="0 0 215 200"><g transform="translate(0,6)"><path d="M170,30 C146,38 120,58 102,84 C84,110 70,134 54,148 C42,158 30,152 30,138 C30,126 36,116 44,110 C34,120 24,134 28,152 C31,172 60,178 86,160 C114,140 140,106 158,76 C165,63 169,46 170,30 Z" fill="#e0150f"/></g><g transform="translate(184,26) rotate(-38) scale(.95)"><path d="M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z" fill="currentColor"/></g><g fill="#e0150f"><circle cx="150" cy="28" r="3.4" opacity=".9"/><circle cx="136" cy="36" r="2.6" opacity=".65"/><circle cx="124" cy="44" r="1.9" opacity=".4"/></g></symbol><clipPath id="blobclip" clipPathUnits="objectBoundingBox"><path d="M0,0.5 Q0,0.40 0.06,0.40 L0.20,0.40 Q0.27,0.40 0.27,0.30 L0.27,0.09 Q0.27,0 0.35,0 L0.93,0 Q1,0 1,0.07 L1,0.93 Q1,1 0.93,1 L0.07,1 Q0,1 0,0.93 Z"/></clipPath></defs></svg>'

# header button style (both from Uiverse.io, MIT; CSS in style.css):
#   "pearl"  = glossy black pills, a sparkle marks the current page
#   "ripple" = outlined pills, a green circle grows from the centre on hover / current page
NAV_STYLE = "ripple"
NAV_SOFT = True    # soft raised pill menu, current page pressed in with a red light (set False for the earlier round buttons)
NAV_BOARD = False   # departure-board menu: each page is a gate, letters are split-flap tiles that flip on hover (set False to go back to the round buttons)
BOARD_JS = ("<script>(function(){var h=document.currentScript.previousElementSibling;if(!h)return;var A='ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "R=matchMedia('(prefers-reduced-motion: reduce)').matches;h.querySelectorAll('.menu .pill').forEach(function(p,i){var s=p.querySelector('.nm');if(!s)return;"
            "var t=s.textContent.trim().toUpperCase(),on=p.matches('[aria-current=page],.is-cur'),c='';"
            "for(var k=0;k<t.length;k++)c+=t[k]===' '?'<b class=\"x\"></b>':'<b>'+t[k]+'</b>';"
            "var g=document.createElement('span');g.className='gt';g.setAttribute('aria-hidden','true');g.innerHTML='GATE 0'+(i+1)+'<em></em>';"
            "var q=document.createElement('span');q.className='ch';q.setAttribute('aria-hidden','true');q.innerHTML=c;p.insertBefore(g,p.firstChild);p.insertBefore(q,s);"
            "if(on)p.classList.add('bd-on');if(R)return;var busy=0;function flip(){if(busy)return;busy=1;var bs=q.querySelectorAll('b:not(.x)'),n=0;"
            "bs.forEach(function(b,j){var w=b.textContent,m=0,x=5+j*2,iv=setInterval(function(){m++;if(m>=x){b.textContent=w;clearInterval(iv);if(j===bs.length-1)busy=0}else b.textContent=A[Math.floor(Math.random()*26)]},45)})}"
            "p.addEventListener('mouseenter',flip);p.addEventListener('focus',flip)});h.classList.add('bd-on')})()</script>")
SPARK = '<span class="sp" aria-hidden="true"><i>✧</i><i>✦</i></span>' if NAV_STYLE == "pearl" else ""
CSS = re.sub(r"\.%s [^{]*\{[^}]*\}" % ("ripple" if NAV_STYLE == "pearl" else "pearl"), "", CSS)   # inline only the chosen style

def pill(u, n, cur):
    on = cur == u or (u != "/" and cur.startswith(u + "/"))
    return f'<a class="pill" href="{u}"{" aria-current=\"page\"" if on else ""}>{SPARK if on else ""}<span class="nm">{n}</span></a>'

def header(cur):
    BRAND_IMG = f'<img class="lgf" src="{AL_MARK_S}" srcset="{AL_MARK_S} 1x, {AL_MARK} 2x" alt="" width="60" height="48"><span class="bt"><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span>'
    links = "".join(pill(u, n, cur) for u, n in NAV)
    return f'''<header class="nav {NAV_STYLE}{" board" if NAV_BOARD else ""}{" soft" if NAV_SOFT else ""}" role="banner">
  <a class="brand" href="/" aria-label="AL ARBAB TRAVEL &amp; TOURS home">{BRAND_IMG}</a>
  <button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu">{ico("menu", 22)}</button>
  <nav class="menu" id="menu" aria-label="Main navigation">{pill("/", "Home", cur)}{nav_dropdown(cur)}{links}</nav>
  <a class="cta-dark" href="{WA}" target="_blank" rel="noopener">{ico("wa", 16)} WhatsApp us</a>
</header>{BOARD_JS if NAV_BOARD else ""}'''

def asian_claim(c):
    """True only for country pages of the Asian regions (Pakistan itself excluded): the one place the success-rate claim may appear."""
    return c["region"] in ASIAN_REGIONS and c["slug"] != "pakistan"

# ------------------------------------------------------------------ two service tiers (owner's structure, Oct 2026)
TIER1_NAME = "Visit Visa Processing — Asian Countries"
TIER2_NAME = "Visa File Preparation & Guidance — Europe, Schengen, UK, USA, Canada, Australia and others"
TIER2_SHORT = "Visa File Preparation & Guidance"
# Owner's priority order. Philippines and Tajikistan have no country guide yet; they are skipped (not shown) until a guide
# is written from official sources, so no placeholder page is ever published.
TIER1_ORDER = ["thailand", "malaysia", "singapore", "indonesia", "sri-lanka", "vietnam", "japan", "cambodia", "philippines",
               "azerbaijan", "bahrain", "turkey", "uzbekistan", "tajikistan", "bangladesh"]
REGION_ORDER = ["south-asia", "east-asia", "central-asia", "middle-east", "schengen", "united-kingdom", "united-states", "canada",
                "australia", "oceania", "north-africa", "southern-africa", "south-america"]
TIER2_MAIN = [("schengen", "Schengen (Europe)"), ("united-kingdom", "United Kingdom"), ("united-states", "United States"),
              ("canada", "Canada"), ("australia", "Australia")]

def tier_of(c):
    """1 = we process and follow up the visit visa (Asian countries); 2 = we prepare the file and guide the client."""
    return 1 if asian_claim(c) else 2

def regions_ordered():
    return [REGIONS[s] for s in REGION_ORDER if s in REGIONS] + [r for r in DATA["regions"] if r["slug"] not in REGION_ORDER]

def asian_priority():
    return [COUNTRIES[s] for s in TIER1_ORDER if s in COUNTRIES and tier_of(COUNTRIES[s]) == 1]

def asian_rest():
    seen, out = {c["slug"] for c in asian_priority()}, []
    for reg in REGION_ORDER:
        for c in BY_REGION.get(reg, []):
            if c["region"] == reg and tier_of(c) == 1 and c["slug"] not in seen:
                out.append(c); seen.add(c["slug"])
    return out

def tier2_countries():
    seen, out = set(), []
    for reg in REGION_ORDER:
        if reg in ASIAN_REGIONS:
            continue
        for c in BY_REGION.get(reg, []):
            if c["region"] == reg and c["slug"] not in seen:
                out.append(c); seen.add(c["slug"])
    return out + [c for c in COUNTRIES.values() if tier_of(c) == 2 and c["slug"] not in seen]   # e.g. Pakistan (visa for visitors)

def country_rank():
    """url -> position in the site-wide order: Asian priority list, other Asian countries, then everything else."""
    return {c["url"]: i for i, c in enumerate(asian_priority() + asian_rest() + tier2_countries())}

def by_rank(cs):
    rk = country_rank()
    return sorted(cs, key=lambda c: rk.get(c["url"], 10**6))

def tier_links():
    return ('<p class="tier-links"><a class="link" href="/visa-services#tiers">Our two services</a> '
            '<a class="link" href="/compliance">Our compliance commitment</a> <a class="link" href="/fees-and-refunds">Fees &amp; refund policy</a></p>')

def tier_block(name, tier, what="visa", note=""):
    """Service-tier box near the top of every country and visa-type page."""
    if tier == 1:
        return (f'<div class="block tier t1" id="service"><p class="tier-tag">{e(TIER1_NAME)}</p><h2>How we help with your {e(name)} visit visa</h2>'
                f'<p>We process and follow up {e(name)} visit visa applications from our Blue Area office: a free consultation, a document checklist for your case, '
                f'file preparation, submission and follow-up, and honest updates until the decision. Final decision rests with the embassy.</p>{f"<p>{e(note)}</p>" if note else ""}{tier_links()}</div>')
    return (f'<div class="block tier t2" id="service"><p class="tier-tag">{e(TIER2_SHORT)}</p><h2>How we help with your {e(name)} {e(what)}</h2>'
            f'<p>We prepare and organise your {e(name)} {e(what)} file and guide you through the embassy or visa centre submission, including biometrics or an interview where required. '
            f'We do not guarantee approval. The embassy or consulate makes the final decision.</p>{tier_links()}</div>')

def official_facts(c):
    """Facts taken only from official government sources, each with its source link (used for country guides researched from official sites)."""
    fs = c.get("facts")
    if not fs:
        return ""
    li = "".join(f'<li><span>{e(t)}<br><a class="link" href="{u}" target="_blank" rel="noopener nofollow">Source: {e(n)} ↗</a></span></li>' for t, n, u in fs)
    return (f'<div class="block" id="official"><h2>What the official sources say about the {e(c["name"])} visa</h2><ul class="checks">{li}</ul>'
            f'<p class="note" style="margin-top:12px">Checked on the official sites in {UPDATED}. Rules change, so check the official site before you apply. Final decision rests with the embassy.</p></div>')

def tier_block_region(r):
    if r["slug"] in ASIAN_REGIONS:
        return (f'<div class="block tier t1" id="service"><p class="tier-tag">{e(TIER1_NAME)}</p><h2>How we help with {e(r["name"])} visas</h2>'
                f'<p>Visit visas: we process and follow up applications for the {e(r["name"])} countries on this page, from a free consultation and document checklist to submission, '
                f'follow-up and honest updates. Business visas: we prepare your file and guide you. Final decision rests with the embassy.</p>{tier_links()}</div>')
    return tier_block(r["name"], 2)

SLUG_FLAG = {"schengen": "eu", "united-kingdom": "gb", "united-states": "us", "canada": "ca", "australia": "au", "sri-lanka": "lk", "azerbaijan": "az", "bahrain": "bh",
             "turkey": "tr", "uzbekistan": "uz", "tajikistan": "tj", "bangladesh": "bd", "cambodia": "kh", "philippines": "ph", "vietnam": "vn", "japan": "jp",
             "thailand": "th", "malaysia": "my", "singapore": "sg", "indonesia": "id"}

def local_flag(code, name):
    """Round flag for a chip: self-hosted file when we have it, else the flag CDN."""
    if code and os.path.exists(os.path.join(ROOT, "assets", "flags", "w80", f"{code}.png")):
        return f'<img class="tfl" src="/assets/flags/w80/{code}.png" alt="" width="26" height="26" loading="lazy" decoding="async">'
    return ""

def tier_chip(url, name, slug, code=None):
    return f'<a class="tchip" href="{url}">{local_flag(code or SLUG_FLAG.get(slug), name)}<span>{e(name)}</span></a>'

def tiers_section(id_="tiers", h2="Two ways we help"):
    a = "".join(tier_chip(c["url"], c["name"], c["slug"], c.get("flag")) for c in asian_priority())
    bb = "".join(tier_chip(f"/countries/{s}", n, s) for s, n in TIER2_MAIN)
    def title(t):
        if " — " in t:
            x, y = t.split(" — ", 1)
            return f'{e(x)} <em>{e(y)}</em>'
        return e(t)
    words = h2.split(" ")
    h2h = (" ".join(words[:-2]) + " " if len(words) > 2 else "") + f'<em>{" ".join(words[-2:])}</em>' if len(words) > 2 else f'<em>{e(h2)}</em>'
    head = (f'<div class="tw-head"><span class="tw-eb"><i></i>Our services</span><h2>{h2h}</h2>'
            f'<p class="lead">Choose the service that matches your destination.</p></div>')
    inner = (f'<div class="tiers tw"><article class="tcard t1"><span class="tw-eb sm">Service 1</span><h3>{title(TIER1_NAME)}</h3>'
             f'<p>We process and follow up your visit visa for Asian countries, from the document checklist to submission and follow-up, with honest updates on your file. Final decision rests with the embassy.</p>'
             f'<div class="chipsrow tw-chips">{a}</div>'
             f'<div class="tw-act"><a class="tw-btn p" href="/eligibility-check">Check my documents</a><a class="tw-btn" href="/countries#asia">All Asian countries <span aria-hidden="true">&rarr;</span></a></div></article>'
             f'<article class="tcard t2"><span class="tw-eb sm">Service 2</span><h3>{title(TIER2_NAME)}</h3>'
             f'<p>We prepare and organise your file and guide you through the embassy or visa centre submission. We do not guarantee approval. The embassy or consulate makes the final decision.</p>'
             f'<div class="chipsrow tw-chips">{bb}</div>'
             f'<div class="tw-act"><a class="tw-btn p" href="/eligibility-check">Check my documents</a><a class="tw-btn" href="/countries#guidance">All other destinations <span aria-hidden="true">&rarr;</span></a></div></article></div>')
    return (f'<section class="sec reveal" id="{id_}">{head}{inner}</section>')

def tiers_note():
    """Short version for the individual visa-service pages."""
    return (f'<div class="block tier"><p class="tier-tag">Our two services</p><h2>Which service applies to you?</h2>'
            f'<p><b>{e(TIER1_NAME)}:</b> we process and follow up your visit visa for Asian countries such as '
            + ", ".join(e(c["name"]) for c in asian_priority()[:7]) + '.</p>'
            f'<p><b>{e(TIER2_NAME)}:</b> we prepare and organise your file and guide you through the submission. We do not guarantee approval; the embassy or consulate makes the final decision.</p>'
            f'{tier_links()}</div>')

HOW_WE_WORK = [("Free consultation", "Tell us your destination and travel plans on WhatsApp, by phone or at our Blue Area office."),
               ("Document checklist", "We give you a written checklist for your destination and your situation."),
               ("File preparation", "We check your documents and prepare and organise your file. We only work with genuine documents."),
               ("Submission or guidance", "Asian visit visas: we submit and follow up your application. Europe, UK, USA, Canada, Australia and others: we guide you through the embassy or visa centre submission."),
               ("Honest updates", "We tell you where your file stands, including the risks and the reasons if a visa is refused. Final decision rests with the embassy.")]

HW_IMG = {0: ("hw1", "seal", 92, 73, "Free consultation"), 1: ("hw2", "pic", 76, 76, "Checklist being filled in"), 3: ("hw4", "pic", 76, 76, "Submitting a file"), 4: ("hw5", "seal", 96, 82, "Honesty")}
HW_FOLDER = ('<svg class="hwi seal" viewBox="0 0 96 80" width="92" height="76" aria-hidden="true"><defs><linearGradient id="hwf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6aa7ff"/><stop offset="1" stop-color="#0e7c86"/></linearGradient></defs>'
             '<path d="M6 14a6 6 0 0 1 6-6h22l8 9h42a6 6 0 0 1 6 6v46a6 6 0 0 1-6 6H12a6 6 0 0 1-6-6z" fill="url(#hwf)"/><path d="M6 28h84v38a6 6 0 0 1-6 6H12a6 6 0 0 1-6-6z" fill="#fff" opacity=".18"/>'
             '<circle cx="48" cy="50" r="15" fill="#fff"/><path d="M40 50l6 6 11-12" fill="none" stroke="#0e7c86" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def how_we_work(id_="how-we-work"):
    steps = [("wh1", "Free consultation", "Step 1", "Start with us →", "/contact", "1", "WhatsApp or office", "Where", "WhatsApp", "Cost", "Free"),
             ("wh2", "Document checklist", "Step 2", "Free check →", "/eligibility-check", "2", "Your own checklist", "You get", "Checklist", "Format", "Written"),
             ("wh3", "File preparation", "Step 3", "Our commitment →", "/compliance", "3", "File made ready", "We check", "Documents", "Only", "Genuine"),
             ("wh4", "Submission or guidance", "Step 4", "Our services →", "/visa-services", "4", "Submit or guide", "Asia", "We submit", "Others", "We guide"),
             ("wh5", "Honest updates", "Step 5", "Fees and refunds →", "/fees-and-refunds", "5", "Where your file is", "We tell", "The risks", "Decision", "Embassy")]
    cards = "".join(ncard_pic(h, im, t, pill, notch, f'<b style="font:900 20px/1 Archivo,sans-serif;color:#073b40">{n}</b>', t, sub, k1, v1, k2, v2)
                    for im, t, pill, notch, h, n, sub, k1, v1, k2, v2 in steps)
    head = ('<div class="tw-head"><span class="tw-eb"><i></i>Our process</span><h2>How <em>we work</em></h2>'
            '<p class="lead">Five steps for every file. No guarantees and no shortcuts.</p></div>')
    return (f'<section class="sec reveal" id="{id_}">{head}<div class="grid g5">{cards}</div><p class="note" style="margin-top:16px">Read our <a class="link" href="/fees-and-refunds">fees &amp; refund policy</a> '
            f'and our <a class="link" href="/compliance">compliance commitment</a>.</p></section>')

def nav_dropdown(cur):
    def chip(url, name, code):
        fl = local_flag(code, name)
        return f'<a class="ddc" href="{url}">{fl}<span>{e(name)}</span></a>'
    a = "".join(chip(c["url"], c["name"], c.get("code") or SLUG_FLAG.get(c["slug"])) for c in asian_priority())
    b = "".join(chip(f"/countries/{sl}", n, SLUG_FLAG.get(sl) or (COUNTRIES.get(sl) or {}).get("code")) for sl, n in TIER2_MAIN)
    on = " is-cur" if cur.startswith("/visa-services") else ""
    return (f'<details class="dd"><summary class="pill{on}">{SPARK if on else ""}<span class="nm">Visas</span><span class="chev" aria-hidden="true"></span></summary><div class="dd-panel ddx">'
            f'<div class="ddx-sec"><p class="dd-h">Visit visa processing &mdash; Asia</p><p class="dd-note">We process and follow up your visa.</p><div class="ddx-grid">{a}</div></div>'
            f'<div class="ddx-sec"><p class="dd-h">File preparation &amp; guidance</p><p class="dd-note">We prepare your file and guide you. The embassy decides.</p><div class="ddx-grid">{b}</div></div>'
            f'<div class="ddx-foot"><a class="ddx-btn" href="/countries#asia">All Asian countries</a><a class="ddx-btn" href="/countries#guidance">All other destinations</a>'
            f'<a class="ddx-btn pri" href="/visa-services">How our two services work &rarr;</a></div></div></details>')

def google_line():
    """Link to the Google reviews. Shows nothing until GBP_URL is set; the rating only appears when G_RATING and G_COUNT are set too."""
    if not GBP_URL:
        return ""
    txt = f"★ {e(G_RATING)} on Google · {e(G_COUNT)} reviews" if (G_RATING and G_COUNT) else "Read our Google reviews →"
    return f'<p class="glink"><a href="{e(GBP_URL)}" target="_blank" rel="noopener">{txt}</a></p>'

def google_badge():
    """Home-page hero badge with the real Google rating (home page and footer are the only places it is shown)."""
    if not (GBP_URL and G_RATING and G_COUNT):
        return ""
    return (f'<a class="social gbadge" href="{e(GBP_URL)}" target="_blank" rel="noopener" '
            f'aria-label="Rated {e(G_RATING)} out of 5 on Google from {e(G_COUNT)} reviews (opens Google Maps)">'
            f'<span class="gstars" aria-hidden="true">★★★★★</span><span><strong>{e(G_RATING)} on Google</strong><small>{e(G_COUNT)} reviews</small></span></a>')

def trust_line():
    """Address + licence line used under the contact banners, so visitors can see the agency is a real office they can visit."""
    lic = f"DTS Licence No. {e(DTS_LICENCE)}" if DTS_LICENCE else "DTS licensed"
    return f'<p class="tl"><span>{ico("pin", 15, "currentColor")}{ADDR}</span><span>{ico("shield", 15)}{lic}</span><span>{ico("clock2", 15)}{HOURS}</span></p>'

FB_LINE = "DTS-licensed visa and travel desk in Blue Area, Islamabad: visit visas, Umrah, air tickets and hotels."

def footer():
    follow = "".join(f'<a class="fs fs-{s_}" href="{u}" target="_blank" rel="noopener me">{ico(s_, 18, "#fff")}<span>{n}</span></a>' for s_, u, n in SOCIAL) + \
             f'<a class="fs fs-wa" href="{WA}" target="_blank" rel="noopener">{ico("wa", 18)}<span>WhatsApp</span></a>'
    svc = [("/visa-services", "Visa Consultancy"), ("/umrah", "Umrah Packages 2026"), ("/air-ticketing", "Air Ticketing"), ("/hotel-booking", "Hotel Bookings"),
           ("/travel-insurance", "Travel Insurance"), ("/partner-airlines", "Airlines We Book"), ("/packages", "Holiday Packages"),
           ("/honeymoon-packages", "Honeymoon Packages"), ("/visa-appointments", "Visa Appointments"), ("/flight-hotel-reservation-for-visa", "Flight & Hotel Reservation"), ("/eligibility-check", "Free Eligibility Check")]
    reg = [(f"/countries/{r['slug']}", r["name"]) for r in regions_ordered()]
    co = [("/about", "About Us"), ("/contact", "Contact Us"), ("/travel-agency-islamabad", "Travel Agency Islamabad"), ("/visa-consultant-islamabad", "Visa Consultant Islamabad"),
          ("/travel-agency-rawalpindi", "Travel Agency Rawalpindi"), ("/visa-consultant-rawalpindi", "Visa Consultant Rawalpindi"), ("/guides", "Visa Guides"), ("/editorial-policy", "Editorial Policy"), ("/sources", "Official sources"), ("/sitemap", "Sitemap"),
          ("/terms", "Terms & Conditions"), ("/privacy", "Privacy Policy"), ("/fees-and-refunds", "Fees & Refund Policy"), ("/disclaimer", "Disclaimer"), ("/compliance", "Compliance Commitment")]
    li = lambda xs: "".join(f'<li><a href="{u}">{e(n)}</a></li>' for u, n in xs)
    asia_links = " ".join(f'<a href="{c["url"]}">{e(c["name"])}</a>' for c in asian_priority())
    regions = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in reg)
    company = " ".join(f'<a href="{u}">{e(n)}</a>' for u, n in co)
    soc = "".join(f'<a class="fb-s" href="{u}" target="_blank" rel="noopener me" aria-label="{n}">{ico(s_, 18, "#0a1530")}</a>' for s_, u, n in SOCIAL) + \
          f'<a class="fb-s fb-sw" href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp">{ico("wa", 18)}</a>'
    f_svc = [("/visa-services", "Visa consultancy"), ("/umrah", "Umrah packages 2026"), ("/air-ticketing", "Air ticketing"), ("/hotel-booking", "Hotel bookings"),
             ("/packages", "Holiday packages")]
    f_vis = POPULAR[:5]
    f_co = [("/about", "About us"), ("/contact", "Contact"), ("/guides", "Visa guides"), ("/eligibility-check", "Free eligibility check"), ("/pakistan-tours", "Pakistan tours")]
    col = lambda h, xs, more: f'<div class="fb-col"><h2 class="fh">{h}</h2><ul>{li(xs)}</ul><a class="fb-more" href="{more[0]}">{more[1]} &rarr;</a></div>'
    return f'''<footer class="fB">
  <div class="fb-card">
    <div class="fb-top">
      <div class="fa-brand"><a class="brand" href="/" aria-label="AL ARBAB TRAVEL &amp; TOURS home"><img class="lgf" src="{AL_MARK_M}" srcset="{AL_MARK_M} 1x, {AL_MARK} 2x" alt="" width="77" height="62" loading="lazy"><span class="bt"><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></a><h2 class="sr">{NAME}</h2>
        <p>{e(FB_LINE)}</p>{google_line()}</div>
      <div class="fb-col fb-visit"><h2 class="fh">Visit us</h2><ul class="fa-contact">
        <li>{ico("pin", 18, "#ff7a6b")}<a href="{MAP_URL}" target="_blank" rel="noopener">{ADDR}</a></li>
        <li>{ico("phone", 17, "#0e7c86")}<span><a href="tel:{PHONE_I}">{PHONE_D}</a> · <a href="tel:{LAND_I}">{LAND}</a></span></li>
        <li>{ico("clock", 18, "#4a6366")}<span>{HOURS}</span></li>
        <li>{ico("gmail", 18, None)}<a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
      <div class="fb-cta"><p>Planning a visa or trip? An adviser checks your documents for free.</p>
        <div class="fb-btns"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">{ico("wa", 16)} WhatsApp {PHONE_D}</a><a class="btn light" href="tel:{PHONE_I}">{ico("phone", 16)} Call now</a></div></div>
    </div>
    <div class="fb-grid">
      {col("Services", f_svc, ("/visa-services", "All services"))}
      {col("Popular visas", f_vis, ("/countries", "All destinations"))}
      {col("Company", f_co, ("/guides", "All guides"))}
    </div>
    <div class="fb-nl"><div><h2 class="fh">Newsletter</h2><p>Visa updates, flight offers and Umrah packages from {NAME}. No spam.</p></div>
      <form class="nl" id="nlForm"><label for="nle" class="sr">Email address</label><input id="nle" type="email" placeholder="Your email address" required><button type="submit">Subscribe</button></form></div>
    <details class="fb-all"><summary>Browse all countries, regions &amp; policies</summary>
      <div class="fb-allg"><div><h2 class="fh">Asian visit visa guides</h2><p class="fl">{asia_links}</p></div>
        <div><h2 class="fh">Browse by region</h2><p class="fl">{regions}</p></div>
        <div><h2 class="fh">Company &amp; guides</h2><p class="fl">{company}</p></div></div></details>
    <div class="fb-bottom"><span class="fb-copy">© 2026 {NAME}</span><span class="fa-dts">DTS licensed · Islamabad</span><div class="fb-soc" aria-label="Follow us">{soc}</div></div>
    <p class="fb-disc">{DISCLAIMER_LINE} Final decision on every visa rests with the embassy. <a href="/disclaimer">Disclaimer</a> · <a href="/terms">Terms</a> · <a href="/privacy">Privacy</a> · <a href="/fees-and-refunds">Fees &amp; refunds</a> · <a href="/compliance">Compliance</a></p>
  </div>
</footer>
<a class="fab" href="{wa("Hi AL ARBAB TRAVEL AND TOURS, I need help with a visa enquiry.")}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp: @WALABEL@">💬 <span>Chat on WhatsApp</span><b class="fab-tip" aria-hidden="true">@WALABEL@</b></a>
<div class="dock" role="region" aria-label="Contact us"><a class="dk dk-wa" href="{wa("Hi AL ARBAB TRAVEL AND TOURS, I need help with a visa enquiry.")}" target="_blank" rel="noopener">{ico("wa", 22)}<span>WhatsApp</span></a><a class="dk dk-call" href="tel:{PHONE_I}">{ico("phone", 20)}<span>Call now</span></a></div>
<div id="toast" role="status" aria-live="polite"></div>'''

PAGES = {}   # url -> (html, priority, noindex)
# fonts are served from /assets/fonts (latin subset, SIL OFL): no Google Fonts requests, text paints sooner
_FR = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
FONT_FILES = {"Archivo": ("archivo-latin.woff2", "700 900"), "Inter": ("inter-latin.woff2", "400 700")}
FONT_URL = {k: f"/assets/fonts/{v[0]}?v={asset_hash('fonts/' + v[0])}" for k, v in FONT_FILES.items()}
FONT_CSS = "".join(f"@font-face{{font-family:{k};font-style:normal;font-weight:{FONT_FILES[k][1]};font-display:swap;src:url({FONT_URL[k]}) format('woff2');unicode-range:{_FR}}}" for k in FONT_FILES)
FONT_PRELOAD = "".join(f'<link rel="preload" as="font" type="font/woff2" href="{u}" crossorigin>' for u in FONT_URL.values())
VERIFY_TAGS = (f'<meta name="google-site-verification" content="{GSC_CODE}">' if GSC_CODE else '') + (f'<meta name="msvalidate.01" content="{BING_CODE}">' if BING_CODE else '')
GA_TAG = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{GA_ID}");</script>'
          if GA_ID else "")

def an(word):
    """'a' or 'an' in front of a country or visa name (e.g. 'an Italy visa', 'a Thailand visa')."""
    return ("an " if word[:1].lower() in "aeiou" else "a ") + word

# Titles and descriptions the owner specified (checked Oct 2026). Used by page() below.
META_OVERRIDE = {
    "/countries/schengen/italy": ("Italy Visa from Pakistan 2026: Documents | AL ARBAB",
        "Italy Schengen visa from Pakistan: document checklist, bank statement and insurance rules, and file help in Blue Area, Islamabad. Free file check."),
    "/visa-consultant-islamabad": ("Visa Consultant in Islamabad (Blue Area) | AL ARBAB",
        "Visa consultant in Blue Area, Islamabad. Free document check for Schengen, UK, Malaysia, Thailand and more. Call 051-2000066."),
    "/about": ("Visa Consultant & Travel Agency Islamabad | AL ARBAB",
        "AL ARBAB Travel and Tours, Eagle Plaza, Blue Area, Islamabad. Visa help, air tickets and Umrah. Get a free document check on WhatsApp today."),
}

def page(url, title, desc, body, ld=None, kw="", image=None, extra_head="", extra_script="", priority="0.7", noindex=False, home=False):
    title, desc = META_OVERRIDE.get(url, (title, desc))   # title, description, og:title, og:description and twitter tags all use these
    canon = BASE + url
    if not noindex and len(title) > 60 and title.endswith(" | AL ARBAB"):
        title = title[:-len(" | AL ARBAB")]   # keep titles inside one search-result line
    desc = fit_desc(desc) if not noindex else desc
    img = image if (image and image.startswith(BASE)) else (BASE + "/assets/og-default.jpg")   # social image is always one of our own files, never a third-party host
    lds = ([org_ld(), website_ld()] if home else [org_ld()]) + (ld or [])
    if not noindex:
        kind = "CollectionPage" if url in ("/countries", "/packages", "/guides", "/sitemap") else ("Article" if url.startswith("/guides/") else "WebPage")
        wp = {"@context": "https://schema.org", "@type": "WebPage" if kind == "Article" else kind, "@id": canon + "#webpage", "url": canon, "name": title, "description": fit_desc(desc),
              "inLanguage": "en-PK", "isPartOf": {"@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": NAME}, "about": {"@id": BASE + "/#org"},
              "dateModified": TODAY, "primaryImageOfPage": {"@type": "ImageObject", "url": img}}
        lds.append(wp)
    ldt = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>' for x in lds)
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large,max-snippet:-1"
    kwm = f'<meta name="keywords" content="{e(kw)}">' if kw else ""
    html = f'''<!doctype html>
<html lang="en-PK">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title, quote=False)}</title>
<meta name="description" content="{attr(desc)}">
{kwm}
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#A0B1AE">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="en-pk" href="{canon}"><link rel="alternate" hreflang="x-default" href="{canon}">
<meta name="geo.region" content="PK-IS"><meta name="geo.placename" content="Islamabad"><meta name="geo.position" content="33.7135;73.0673"><meta name="ICBM" content="33.7135, 73.0673">
<link rel="icon" type="image/png" sizes="32x32" href="{ICON32}"><link rel="apple-touch-icon" href="{ICON192}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:locale" content="en_PK">
<meta property="og:title" content="{attr(title)}"><meta property="og:description" content="{attr(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{attr(title)}"><meta name="twitter:description" content="{attr(desc)}"><meta name="twitter:image" content="{img}">
<link rel="preconnect" href="https://images.unsplash.com">
{FONT_PRELOAD}
{extra_head}
{VERIFY_TAGS}{GA_TAG if not noindex else ""}
<script>document.documentElement.classList.add('js')</script>
<style>{FONT_CSS}{CSS}</style>
{ldt}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{SVG_DEFS}
{body}
{footer()}
<script>window.SITE={{wa:"{WA}",email:"{EMAIL}",waS:"https://wa.me/{WA_DESK["schengen"]}",waA:"https://wa.me/{WA_DESK["asian"]}",sch:{json.dumps(sch_names())}}};</script>
{extra_script}
<script src="{APPJS}" defer></script>
</body>
</html>'''
    html = route_wa(url, finish_icons(html).replace("@N@", str(len(COUNTRIES))))
    html = re.sub(r"https://flagcdn\.com/(w\d+)/([a-z-]+)\.png", lambda m: f"/assets/flags/{m.group(1)}/{m.group(2)}.png" if os.path.exists(os.path.join(ROOT, "assets", "flags", m.group(1), m.group(2) + ".png")) else m.group(0), html)   # flags are self-hosted
    PAGES[url] = (html, priority, noindex)

def faq_html(faq):
    return "".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faq)

def sec(h2, lead, inner, id_=""):
    i = f' id="{id_}"' if id_ else ""
    l = f'<p class="lead">{lead}</p>' if lead else ""
    return f'<section class="sec reveal"{i}><div class="head"><div><h2>{h2}</h2></div>{l}</div>{inner}</section>'

def crumbs_html(items):
    parts = [f'<a href="{u}">{e(n)}</a>' if u else f'<span aria-current="page">{e(n)}</span>' for n, u in items]
    return '<nav class="crumbs" aria-label="Breadcrumb" style="margin:26px 6px 0">' + " / ".join(parts) + "</nav>"

def cta_band(title="Ready to plan your trip?", text=None):
    text = text or f"Send us your route, dates or visa question. We reply during office hours. {HOURS}."
    return f'''<section class="sec reveal"><div class="band"><div><h2>{title}</h2><p>{text}</p></div>
<div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn wa" href="{WA}" target="_blank" rel="noopener">💬 WhatsApp {PHONE}</a><a class="btn light" href="tel:{PHONE_I}">📞 Call now</a></div>{trust_line()}</div></section>'''

def ctacard(topic):
    return f'''<div class="ctacard"><p class="open" data-open-status>Office hours: Mon–Sat, 9 AM – 8 PM</p><h2>Free assessment</h2><p>Send us your profile on WhatsApp for a free first check of your {e(topic)} case. No charge for the first evaluation.</p>
<a class="btn wa" href="{wa(f"Hi AL ARBAB TRAVEL AND TOURS, I need help with {topic}.")}" target="_blank" rel="noopener">💬 WhatsApp us</a>
<a class="btn light" href="tel:{PHONE_I}">📞 Call {PHONE}</a>
<div class="line"><span><b>Office:</b> {ADDR}</span><span><b>Hours:</b> {HOURS}</span><span><b>Landline:</b> {LAND}</span></div></div>'''

def shell(cur, crumbs, ph_html, content):
    return f'''<main id="main"><div class="wrap"><div class="shell"><div class="inner">
{header(cur)}
{crumbs_html(crumbs)}
{ph_html}
</div></div>
{content}
</div></main>'''

def pagehead(eyebrow, h1, lead, pid=None, flagcode=None, alt="", actions=""):
    if pid:
        pic = f'<div class="pic">{picture(pid, alt, 1200, 900, "(max-width:1000px) 100vw, 520px", lazy=False, high=True, widths=(600, 900, 1200))}</div>'
    elif flagcode:
        pic = f'<div class="pic"><div class="flagbig"><img src="https://flagcdn.com/w320/{flagcode}.png" srcset="https://flagcdn.com/w640/{flagcode}.png 2x" alt="{e(alt)} flag" width="320" height="213" fetchpriority="high"></div></div>'
    else:
        pic = ""
    eb = f'<p class="eyebrow"><i></i>{eyebrow}</p>' if eyebrow else ""
    grid = "" if pic else ' style="grid-template-columns:1fr"'
    act = f'<div class="actions">{actions}</div>' if actions else ""
    return f'<div class="ph"{grid}><div>{eb}<h1 style="margin-top:14px">{h1}</h1><p class="lead2">{lead}</p>{act}</div>{pic}</div>'

def tile(c):
    sub = ", ".join(c["popularPlaces"][:2]) or "Visa guide"
    th = (f'<span class="th"><img src="{U(c["img"], 160)}"{"" if c["img"].startswith("/") else f' srcset="{U(c["img"], 320)} 2x"'} alt="{e(c["name"])} – {e(c["popularPlaces"][0] if c["popularPlaces"] else c["name"])}" width="72" height="54" loading="lazy" decoding="async">{flag(c["code"], c["name"] + " flag", 22)}</span>'
          if c["img"] else flag(c["code"], c["name"] + " flag"))
    return f'<a class="tile" href="{c["url"]}" data-name="{e(c["name"].lower())}">{th}<span><b>{e(c["name"])}</b><small>{e(sub)}</small></span></a>'

SHORT_COUNTRY = {"United Arab Emirates": "UAE"}   # short labels for the small all-caps tag on package cards

def pkg_card(p):
    """Book card: the inside page holds the package details; the photo cover swings open on hover, focus or tap."""
    li = "".join(f"<li>{e(x)}</li>" for x in p["highlights"])
    return f'''<article class="book" tabindex="0">
<div class="page"><span class="tag">{e(SHORT_COUNTRY.get(p["country"], p["country"]))}</span><h3>{e(p["title"])}</h3><p><b>{e(p["duration"])}</b><br>{e(p["amenities"])}</p><ul>{li}</ul>
<a class="more" href="{p["url"]}">View package details <span>→</span></a></div>
<div class="cover" aria-hidden="true">{picture(p["img"], "", 600, 800, "(max-width:600px) 100vw, 300px", widths=(400, 600, 900))}
<span class="cv"><small>{e(p["duration"])}</small><b>{e(p["title"])}</b><i>Open ›</i></span></div>
</article>'''

def feat(ic, h, p, link=None):
    l = f'<p style="margin-top:12px"><a class="link" href="{link[0]}">{link[1]} →</a></p>' if link else ""
    return f'<div class="feat"><div class="ic">{ic}</div><h3>{h}</h3><p>{p}</p>{l}</div>'

WF = {"wf1": ("cut", "Two hands holding a coin, clear pricing"), "wf2": ("snap", "A customer support adviser with a headset"), "wf3": ("cut", "An adviser working at one desk"),
      "wf4": ("cut", "First check, a red tick"), "wf5": ("wide", "Tourist visa: passport, boarding pass and an aeroplane"), "wf6": ("snap", "A family with passports and tickets at the airport"),
      "wf7": ("snap", "A family reunited at the airport"),
      "wh1": ("cut", "Free consultation"), "wh2": ("snap", "A checklist being filled in"), "wh3": ("snap", "An adviser preparing a visa file at a desk"), "wh4": ("snap", "Submitting a file"), "wh5": ("cut", "Honesty"), "wf8": ("wide", "Schengen visit visa from Pakistan")}

def feat_pic(img, h, p, link=None):
    kind, alt = WF[img]
    l = f'<a class="tw-btn sm" href="{link[0]}">{link[1]} <span aria-hidden="true">&rarr;</span></a>' if link else ""
    pic = f'<img src="/assets/cards/{img}.webp?v={asset_hash("cards/" + img + ".webp")}" alt="{alt}" loading="lazy" decoding="async" width="280" height="150">'
    return f'<article class="fcard"><div class="fmedia {kind}">{pic}</div><h3>{h}</h3><p>{p}</p>{l}</article>'

def glass_sec(eyebrow, h2_html, lead, inner, id_=""):
    i = f' id="{id_}"' if id_ else ""
    ld = f'<p class="lead">{lead}</p>' if lead else ""
    return f'<section class="sec reveal"{i}><div class="tw-head"><span class="tw-eb"><i></i>{eyebrow}</span><h2>{h2_html}</h2>{ld}</div>{inner}</section>'

GC_ARROW = '<svg viewBox="0 0 12 12" width="16" height="16" aria-hidden="true"><path d="M4.646 2.146a.5.5 0 0 0 0 .708L7.793 6L4.646 9.146a.5.5 0 1 0 .708.708l3.5-3.5a.5.5 0 0 0 0-.708l-3.5-3.5a.5.5 0 0 0-.708 0z" fill="currentColor"/></svg>'

def short_fee(f):
    """'Approx 15,000 - 20,000 PKR (eVisa)' -> 'PKR 15,000+', '90 EUR (...)' -> 'EUR 90', '£135 ...' -> '£135'."""
    m = re.search(r"(\d[\d,]*)\s*-\s*\d[\d,]*\s*(PKR|EUR|USD|GBP)", f)
    if m:
        return f"{m.group(2)} {m.group(1)}+"
    m = re.search(r"(\d[\d,]*)\s*(PKR|EUR|USD|GBP)", f) or re.search(r"(PKR|EUR|USD|GBP)\s*(\d[\d,]*)", f)
    if m:
        g = m.groups()
        return f"{g[1]} {g[0]}" if g[0][0].isdigit() else f"{g[0]} {g[1]}"
    m = re.search(r"([£$€])\s?(\d[\d,]*)", f)
    return f"{m.group(1)}{m.group(2)}" if m else "On request"

def short_time(t):
    m = re.search(r"(\d+)\s*(?:to|-|–)\s*(\d+)\s*(working days|weeks|days)", t or "")
    if m:
        return f"{m.group(1)}–{m.group(2)} {m.group(3).replace('working days', 'days')}"
    m = re.search(r"(\d+)\s*(working days|weeks|days)", t or "")
    return f"~{m.group(1)} {m.group(2).replace('working days', 'days')}" if m else "See guide"

def ncard(href, pid, alt, pill, notch, icon, title, sub, s1l, s1v, s2l, s2v, flagcode=None):
    """Dark collectible card: framed photo with pill on top and a notch tab at the bottom, icon tile, title, two stats."""
    if pid:
        media = picture(pid, alt, 600, 600, "(max-width:600px) 130vw, 420px", widths=(400, 600, 900))   # square card, landscape photo: scaled by height, so ask for a wider file
    elif flagcode:
        media = f'<span class="n-flag">{flag(flagcode, alt, 110)}</span>'
    else:
        media = '<span class="n-orb"></span>'
    return (f'<a class="ncard" href="{href}"><span class="n-media">{media}<span class="n-pill">{e(pill)}</span><span class="n-notch">{e(notch)}</span></span>'
            f'<span class="n-head"><span class="n-ico">{icon}</span><span class="n-name"><b>{e(title)}</b><small>{e(sub)}</small></span></span>'
            f'<span class="n-stats"><span><small>{e(s1l)}</small><b>{e(s1v)}</b></span><span><small>{e(s2l)}</small><b>{e(s2v)}</b></span></span></a>')

def ncard_pic(href, img, alt, pill, notch, icon, title, sub, s1l, s1v, s2l, s2v):
    """Same card as the country cards, with one of our own pictures in the frame."""
    kind = WF[img][0]
    src = f'/assets/cards/{img}.webp?v={asset_hash("cards/" + img + ".webp")}'
    media = f'<img src="{src}" alt="{e(alt)}" width="420" height="420" loading="lazy" decoding="async">'
    cls = " n-cut" if kind == "cut" else (" n-wide" if kind == "wide" else "")
    return (f'<a class="ncard" href="{href}"><span class="n-media{cls}">{media}<span class="n-pill">{e(pill)}</span><span class="n-notch">{e(notch)}</span></span>'
            f'<span class="n-head"><span class="n-ico">{icon}</span><span class="n-name"><b>{e(title)}</b><small>{e(sub)}</small></span></span>'
            f'<span class="n-stats"><span><small>{e(s1l)}</small><b>{e(s1v)}</b></span><span><small>{e(s2l)}</small><b>{e(s2v)}</b></span></span></a>')

LOGO_ICON = f'<img class="mki" src="{AL_MARK_S}" alt="" width="40" height="32" loading="lazy">'

def region_card(r):
    n = len(BY_REGION.get(r["slug"], []))
    if r["img"]:
        im = picture(r["img"], r["name"] + " visa from Pakistan", 800, 533, "(max-width:600px) 100vw, 320px")
    elif r["flag"]:
        im = f'<div style="position:absolute;inset:0;display:grid;place-items:center">{flag(r["flag"], r["name"] + " flag", 96)}</div>'
    else:
        im = f'<div style="position:absolute;inset:0;display:grid;place-items:center;color:#fff;font:900 22px Archivo,sans-serif;letter-spacing:.06em;text-transform:uppercase">{e(r["name"])}</div>'
    cnt = (f"{n} countr" + ("y" if n == 1 else "ies")) if n else f'{len(r["visas"])} visa types'
    vv = r["visas"][0] if r["visas"] else None
    icon = flag(r["flag"], "", 40) if r["flag"] else LOGO_ICON
    sub = r["shortDesc"].split(".")[0]
    return ncard(f"/countries/{r['slug']}", r["img"], r["name"] + " visa from Pakistan", cnt, "Visa guide →", icon, r["name"], sub,
                 "Processing", short_time(vv["processingTime"]) if vv else "See guide", "Visa types", str(len(r["visas"])), r["flag"])

def steps_html(items):
    return "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in items)

# ================================================================== PAGES
def build_home():
    d0 = HERO[0]
    find = [[c["name"], c["url"]] for c in by_rank(list(COUNTRIES.values()))] + [[r["name"], f"/countries/{r['slug']}"] for r in DATA["regions"]] + \
           [["Umrah", "/umrah"], ["Saudi Arabia", "/countries/middle-east/saudi-arabia"], ["Dubai", "/countries/middle-east/united-arab-emirates"],
            ["USA", "/countries/united-states"], ["UK", "/countries/united-kingdom"], ["Europe", "/countries/schengen"]]
    datalist = "".join(f'<option value="{e(n)}">' for n, _ in find)
    # Asian priority destinations (owner's order): first four as large cards, the rest as tiles
    pri = asian_priority()
    pri_cards = "".join(ncard(c["url"], c["img"], f'{c["name"]} – {(c["popularPlaces"] or ["visit visa"])[0]}', "Visit visa processing", "Visa guide →",
                              flag(c["code"], "", 40), c["name"], ", ".join(c["popularPlaces"][:2]) or "Visit visa",
                              "How you apply", ROUTE_SHORT.get(visa_route(c), visa_route(c)), "First check", "Free", c["code"]) for c in pri[:4])
    asian_featured = sec("Visit visa processing — Asian countries", "Our priority destinations, in order. We process and follow up your visit visa. Final decision rests with the embassy.",
                         f'<div class="rgrid">{pri_cards}</div><h3 class="sub-h">More Asian countries</h3><div class="tiles">{"".join(tile(c) for c in pri[4:])}</div>'
                         f'<p style="margin-top:20px"><a class="btn" href="/countries#asia">All Asian countries</a></p>', "asian-visas")
    why = "".join([
        ncard_pic("/fees-and-refunds", "wf1", "Clear pricing", "Before you pay", "Fees policy →", "💰", "Clear Pricing", "Fare or fee sent on WhatsApp", "Quote", "First", "Sent on", "WhatsApp"),
        ncard_pic("/contact", "wf2", "Customer support", "Mon–Sat", "Contact us →", "🕑", "Customer Support", "Phone and WhatsApp support", "Phone", PHONE, "Hours", "9am–8pm"),
        ncard_pic("/about", "wf3", "One desk", "Blue Area", "About us →", "⚡", "One Desk", "Documents, visits, e-tickets", "Office", "Blue Area", "City", "Islamabad"),
        ncard_pic("/eligibility-check", "wf4", "Free first check", "Free", "Check my documents →", "🏆", "Free First Check", "We check your documents first", "Cost", "Free", "Send on", "WhatsApp")])
    _svc_stats = {"tourist-visa": ("Guides", str(len(COUNTRIES)), "Start", "Free check"), "family-visit-visa": ("Type", "Visit visa", "Start", "Free check"),
                  "family-reunification": ("Type", "Family reunion", "Start", "Free check"), "schengen-visa": ("Countries", "29", "Start", "Free check")}
    svc = "".join(ncard_pic(f"/visa-services/{s}", f"wf{5 + i}", n, d_pill, "Learn more →", ic, n, d, *_svc_stats[s])
                  for i, (s, n, ic, d, _) in enumerate(VISA_SERVICES[:4]) for d_pill in [("Visa service")])
    regions = "".join(region_card(r) for r in regions_ordered()[:8])
    src = hero_srcset(d0)
    d0_src = hero_img(d0, 1500)
    d0_set = f' srcset="{src}" sizes="(max-width:1000px) 125vw, 1300px"' if src else ""
    body = f'''<main id="main"><div class="wrap"><div class="shell"><div class="inner">
{header("/")}
<section class="hero" aria-labelledby="h1">
  <div class="left">
    <p class="eyebrow rise" style="animation-delay:.3s"><i></i>DTS Licensed Travel Agency | Blue Area, Islamabad</p>
    <h1 id="h1" class="rise" style="animation-delay:.45s">Visa Consultant &amp; Travel Agency in <em>Islamabad</em></h1>
    <p class="sub rise" style="animation-delay:.6s"><b class="tag">Explore the world with us.</b> {NAME}: <a class="il" href="/visa-consultant-islamabad">visa consultancy</a> with @N@ country guides, air ticketing, hotel stays &amp; Umrah packages from our <a class="il" href="/travel-agency-islamabad">travel agency in Blue Area, Islamabad</a>.</p>
    <div class="actions rise" style="animation-delay:.75s"><a class="start wa" href="{WA}" target="_blank" rel="noopener"><i>{ico("wa", 18)}</i>WhatsApp us</a><a class="start" href="/visa-services"><i>»</i>Discover Now</a><a class="start" href="/air-ticketing"><i>✈</i>Book Flights</a></div>
    <p class="rise" style="animation-delay:.9s;margin-top:16px"><a class="link" id="hlink" href="{d0["url"]}">{d0["n"]} visa guide →</a></p>
    <div class="weather wx rise" style="animation-delay:1s" aria-live="polite">
      <div class="wx-top"><span class="wx-live"><i></i>LIVE WEATHER</span><span id="wtime">--:--</span></div>
      <div class="wx-main"><div class="wx-ico" id="wico" aria-hidden="true"></div><div class="wx-temp"><b id="temp">--</b><sup>°C</sup></div></div>
      <p class="wx-place"><b id="wplace">{d0["city"]}</b><span id="wdesc">Loading…</span></p>
      <div class="wx-grid"><span><small>Feels like</small><b id="wfeel">--</b></span><span><small>Wind</small><b id="wwind">--</b></span><span><small>Humidity</small><b id="whum">--</b></span><span><small>Today</small><b id="whl">--</b></span></div>
      <p class="wx-src">Updates every 10 min · <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a></p>
    </div>
  </div>
  <div class="visual">
    <div class="dests" id="dtabs" role="group" aria-label="Featured destinations"></div>
    <button class="dpause" id="dpause" type="button" aria-pressed="false" aria-label="Pause the destination slideshow">{ico("pause", 20)}</button>
    <div class="blob" id="blob">
      <img class="photo on" id="photoA" src="{d0_src}"{d0_set} alt="{d0["n"]} – {d0["city"]} travel and visa packages from Islamabad" fetchpriority="high" width="1200" height="800">
      <img class="photo" id="photoB" alt="" width="1200" height="800">
      <div class="float" style="left:60%;top:44%"><em style="background:#0e7c86">✓</em><span>Visa<b id="f3t">{d0["visa"]}</b></span></div>
      {google_badge()}
    </div>
  </div>
</section>
<div class="chips">
  <a class="chip" href="/visa-services">◈ Visa Consultancy</a><a class="chip" href="/air-ticketing">✈ Air Ticketing</a><a class="chip" href="/umrah">🕋 Umrah Packages</a><a class="chip" href="/hotel-booking">🏨 Hotels</a><a class="chip" href="/travel-insurance">🛡 Insurance</a>
  <div class="stats"><div><b>@N@</b><small>Country guides</small></div></div>
</div>
</div>
<form class="search" id="searchForm" aria-label="Find a destination or plan a trip">
  <div><label for="to">Where to?</label><input id="to" name="to" list="destlist" placeholder="Thailand, Dubai, Germany…" required autocomplete="off"><datalist id="destlist"></datalist></div>
  <div><label for="in">Check in</label><input id="in" name="in" type="date"></div>
  <div><label for="out">Check out</label><input id="out" name="out" type="date"></div>
  <div><label for="pax">Travelers</label><select id="pax" name="pax"><option>1 Adult</option><option selected>2 Adults, 1 Child</option><option>2 Adults</option><option>Family (5+)</option><option>Group</option></select></div>
  <button class="btn" type="submit">Search</button>
</form></div>
{tiers_section()}
{asian_featured}
{how_we_work()}
{sec("Exclusive travel packages", "All-inclusive international packages curated for Pakistani travelers.", f'<div class="grid g4">{"".join(pkg_card(p) for p in PACKAGES)}</div><p style="margin-top:20px"><a class="btn light" href="/packages">See all packages</a></p>', "packages")}
{sec("Umrah packages 2026", "We arrange Umrah packages, hotels and flights, and prepare your Umrah visa file.",
  f'''<div class="umrah"><div class="t"><span class="eyebrow">🕋 Umrah Packages 2026</span><h3>Umrah Packages — Makkah &amp; Madinah Stays</h3><p>We are a travel agency that arranges Umrah packages, hotels and flights, and prepares your Umrah visa file. Choose Economy, 3 Star, 4 Star or 5 Star and message us on WhatsApp for today's price.</p><div><a class="btn" href="/umrah">Explore Umrah packages</a></div></div><div class="pic">{picture(UMRAH_IMG, "Umrah packages 2026 – Kaaba, Makkah", 1000, 667, "(max-width:1000px) 100vw, 560px")}</div></div>''', "umrah")}
{sec("Visa support across every continent", "Choose a region to see country-by-country requirements, documents and processing times.", f'<div class="rgrid">{regions}</div><p style="margin-top:20px"><a class="btn" href="/countries">View all {len(COUNTRIES)} country guides</a></p>')}
{glass_sec("Why AL ARBAB", "Why travel <em>with us?</em>", "", f'<div class="grid g4">{why}</div>')}
{glass_sec("Visa services", "Our visa <em>services</em>", 'From tourist visas to student visas — one desk in Blue Area, Islamabad. <a class="il" href="/visa-consultant-islamabad">Talk to a visa consultant in Islamabad →</a>', f'<div class="grid g4">{svc}</div><p style="margin-top:22px"><a class="tw-btn p" href="/visa-services">See all visa services <span aria-hidden="true">&rarr;</span></a></p>')}
{reviews_block()}
{sec("Frequently asked questions", "", faq_html(FAQ_GENERAL + PAA_AGENCY))}
</div></main>'''
    ld = [faq_ld(FAQ_GENERAL + PAA_AGENCY), {"@context": "https://schema.org", "@type": "ItemList", "name": "Exclusive travel packages",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + p["url"], "name": p["title"]} for i, p in enumerate(PACKAGES)]}]
    hero_js = [{k: h[k] for k in ("n", "city", "lat", "lon", "code", "visa", "x", "y", "url")} | {"img": hero_img(h, 2000)} for h in HERO]
    script = f'<script>window.DEST={json.dumps(hero_js, ensure_ascii=False)};window.FIND={json.dumps(find, ensure_ascii=False)};</script>'
    pre_set = f' imagesrcset="{src}" imagesizes="(max-width:1000px) 125vw, 1300px"' if src else ""
    pre = f'<link rel="preload" as="image" href="{d0_src}"{pre_set} fetchpriority="high">'
    page("/", "Visa Consultant & Travel Agency in Islamabad | AL ARBAB",
         f"DTS-licensed travel agency in Blue Area, Islamabad: visas with @N@ country guides, air tickets, Umrah & tours. Free assessment: {PHONE_D}",
         body, ld, "visa consultant islamabad, travel agency islamabad, schengen visa pakistan, uk visa islamabad, usa visa pakistan, umrah packages 2026, flight tickets islamabad",
         extra_head=pre, extra_script=script, priority="1.0", home=True)
    cards_preview()

HERO_BG = "photos"   # home hero background: "aurora" (frosted glass gradient, assets/hero-aurora.css) or "photos" (country photo slider)
GLASS_HOME = True   # frosted-glass hero on the home page (assets/glass-hero.css); False = the earlier split hero

def glass_home():
    """Turns the home hero into the frosted-glass design: the destination photo fills the panel, glass rail, stat card, live weather and search bar float on it."""
    if not GLASS_HOME:
        return
    h, pr, noi = PAGES["/"]
    css = re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "glass-hero.css"), encoding="utf-8").read(), flags=re.S)
    css = " ".join(css.split())   # collapse whitespace and newlines
    h = h.replace('<div class="shell">', '<div class="shell gh">', 1)
    rail = ('<nav class="grail" aria-label="Quick links">'
            + "".join(f'<a href="{u}" aria-label="{n}" title="{n}"{t}>{ico(i, 22, "#fff")}</a>' for u, n, i, t in [
                ("/visa-services", "Visa services", "passport", ""), ("/air-ticketing", "Air ticketing", "plane", ""), ("/umrah", "Umrah packages", "kaaba", ""),
                ("/hotel-booking", "Hotel booking", "hotel", ""), ("/travel-insurance", "Travel insurance", "shield", ""),
                (WA, "WhatsApp us", "wa", ' class="wa" target="_blank" rel="noopener"')]) + '</nav>')
    stat = (f'<div class="gstat"><small>Visa help</small><b>{len(COUNTRIES)}</b><span>country guides, from Blue Area, Islamabad</span>'
            f'<a href="/countries" aria-label="See all {len(COUNTRIES)} country guides">&rarr;</a></div>')
    d0_ = HERO[0]
    vvw = (f'<div class="vvw" id="vvw"><span class="vv-t"><span>Visit visa<i class="vv-live" aria-hidden="true"></i></span><a class="vv-a" id="vvl" href="{d0_["url"]}">{e(d0_["n"])} guide &rarr;</a></span>'
           f'<div class="vv-r"><div><b>ISB</b><small>Islamabad</small></div><i class="vv-p" aria-hidden="true">&#9992;</i>'
           f'<div class="vv-d"><b id="vvk">{e(d0_["code"])}</b><small id="vvy">{e(d0_["city"].split(" (")[0])}</small></div></div>'
           f'<div class="vv-pn"><div class="vv-tl"><i class="vv-fill"></i><i class="vv-pp" aria-hidden="true">&#9992;</i><b></b><b></b><b></b></div>'
           f'<div class="vv-lb"><span>DOCUMENTS</span><span>CHECK</span><span>FILE</span></div></div>'
           f'</div>')
    h = h.replace('<section class="hero"', rail + stat + vvw + '<section class="hero"', 1)
        # flight route: start/end points in the 800x560 viewBox of the hero svg, chosen for the glass layout
    SX, SY, EX, EY = 290, 470, 500, 395
    h = h.replace('cx="150" cy="470"', f'cx="{SX}" cy="{SY}"').replace('x="150" y="502"', f'x="{SX}" y="{SY + 32}"')
    h = h.replace("</head>", f"<script>window.FLIGHT={{sx:{SX},sy:{SY},lift:84,dash:'2 9',to:function(){{return [{EX},{EY}]}}}}</script><style>{css}</style></head>", 1)
    if HERO_BG == "photos":   # photo slider + small glass frame (assets/hero-frame.css); rest of the hero unchanged
        fc = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "hero-frame.css"), encoding="utf-8").read(), flags=re.S).split())
        frame = f'<div class="gframe" aria-hidden="true"><small>Visit visa</small><b id="gfn">{e(HERO[0]["n"])}</b><span>{e(HERO[0]["visa"])}</span></div>'
        h = h.replace('<div class="visual">', '<div class="visual">' + frame, 1) if False else h.replace('<div class="blob" id="blob">', '<div class="blob" id="blob">' + frame, 1)
        h = h.replace("</head>", f"<style>{fc}</style></head>", 1)
    if HERO_BG == "aurora":
        ac = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "hero-aurora.css"), encoding="utf-8").read(), flags=re.S).split())
        h = re.sub(r'<link rel="preload" as="image"[^>]*>', "", h, count=1)   # no hero photo to preload
        h = re.sub(r'(<img class="photo on" id="photoA") src="[^"]*"( srcset="[^"]*")?( sizes="[^"]*")?', r'', h, count=1)
        h = h.replace('<div class="blob" id="blob">', '<div class="blob" id="blob"><div class="aur" aria-hidden="true"><i class="a1"></i><i class="a2"></i><i class="a3"></i><i class="a4"></i><b class="b1"></b><b class="b2"></b><b class="b3"></b><b class="b4"></b><b class="b5"></b><div class="glass"></div></div>', 1)
        h = h.replace("</head>", f"<script>window.HERO_NOPHOTO=1</script><style>{ac}</style></head>", 1)
    PAGES["/"] = (h, pr, noi)

HERO_COLORS = {   # /preview-hero-<name>: the aurora hero in other colours (noindex, not in the sitemap, not in the zip)
    "orange": ("#130b04", "#ffb020", "#ff6a00", "#ff8a00", "#ff3d00", "#ffd23a", "#ff7a1a", "#ff5e3a", "255,150,40"),
    "green":  ("#04120a", "#4dff7a", "#18c964", "#22d3ee", "#10b981", "#a3e635", "#22c55e", "#34d399", "60,230,120"),
    "frost":  ("#eef4fb", "#22d3ee", "#7c5cff", "#38bdf8", "#c084fc", "#a5f3fc", "#f0abfc", "#67e8f9", "90,190,255"),
    "sunny":  ("#fff4e0", "#ffc21a", "#ff9800", "#ffb300", "#ff8f00", "#ffd54a", "#ffa000", "#ff9f1a", "255,160,0"),
}

def hero_color_previews():
    CUR = ' aria-current="page"'
    if HERO_BG != "aurora":
        return
    h0, _, _ = PAGES["/"]
    names = ["pink (live now)"] + list(HERO_COLORS)
    for k, (base, a1, a1b, a2, a2b, a3, a3b, a4, glow) in HERO_COLORS.items():
        css = (f".gh .inner{{background:{base}}}.aur{{background:radial-gradient(120% 90% at 50% 10%,{base},#050505 70%)}}"
               f".aur .a1{{background:radial-gradient(circle at 40% 40%,{a1},{a1b} 55%,transparent 72%)}}"
               f".aur .a2{{background:radial-gradient(circle at 50% 50%,{a2},{a2b} 55%,transparent 72%)}}"
               f".aur .a3{{background:radial-gradient(circle at 50% 50%,{a3},{a3b} 60%,transparent 74%)}}"
               f".aur .a4{{background:radial-gradient(circle,{a4},transparent 70%)}}"
               f".aur b{{background:radial-gradient(circle at 35% 30%,rgba(255,255,255,.9),rgba({glow},.8) 35%,rgba({glow},.35) 70%,transparent 72%);box-shadow:0 0 24px rgba({glow},.6)}}"
               ".hcbar{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:9998;display:flex;gap:8px;padding:8px;border-radius:999px;background:#0b1220;box-shadow:0 10px 30px rgba(0,0,0,.4)}"
               ".hcbar a{color:#fff;font:600 13px Inter,sans-serif;padding:8px 16px;border-radius:999px;min-height:40px;display:inline-flex;align-items:center}.hcbar a[aria-current]{background:#fff;color:#0b1220}")
        bar = '<nav class="hcbar" aria-label="Hero colour preview">' + "".join(
            f'<a href="{"/" if n.startswith("pink") else "/preview-hero-" + n}"{CUR if n == k else ""}>{n.title()}</a>' for n in names) + "</nav>"
        if k == "frost":
            css += (".aur{background:radial-gradient(120% 90% at 50% 10%,#f7fbff,#dfeeff 70%)}.aur i{opacity:.95}"
                    ".gh .blob::after{background:linear-gradient(180deg,rgba(20,40,90,.28),rgba(20,40,90,.1) 40%,rgba(20,40,90,.16) 70%,rgba(20,40,90,.42))}"
                    ".aur .glass{background:rgba(255,255,255,.22);border-color:rgba(255,255,255,.7)}")
        if k == "sunny":
            css += (".aur{background:radial-gradient(120% 90% at 50% 10%,#fffaf0,#ffe9c2 70%)}.aur i{opacity:1}"
                    ".aur .a1{width:78%;height:92%}.aur .a2{width:66%;height:80%;opacity:.95}.aur .a3{width:56%;height:70%;opacity:.95}"
                    ".gh .blob::after{background:linear-gradient(180deg,rgba(120,60,0,.28),rgba(120,60,0,.12) 40%,rgba(120,60,0,.18) 70%,rgba(120,60,0,.4))}"
                    ".aur .glass{background:rgba(255,255,255,.18);border-color:rgba(255,255,255,.6)}")
        h = h0.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", bar + "</body>", 1)
        h = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,nofollow">', h, count=1)
        h = h.replace(f'<link rel="canonical" href="{BASE}/">', f'<link rel="canonical" href="{BASE}/preview-hero-{k}">')
        h = re.sub(r"<title>.*?</title>", f"<title>Hero colour preview {k} | AL ARBAB</title>", h, count=1, flags=re.S)
        PAGES[f"/preview-hero-{k}"] = (h, "0.1", True)

HERO_ROAD = True   # /preview-hero-road: glass destination cards over a full-bleed photo (style from a reference video; our own photo and cards). noindex, not in the sitemap, not in the zip.

def hero_road_preview():
    if not HERO_ROAD:
        return
    bg = "/assets/hero/1568508432206-7541b535f84c-2000.webp"
    cards = [("Thailand", "BANGKOK · PHUKET", "#ff9a5a", "#ff3d7f", "#2b1f4a", "#ffd1a6", "e-Visa"),
             ("Malaysia", "KUALA LUMPUR", "#7fd6ff", "#2e6bff", "#0f1d3d", "#cfeaff", "e-Visa"),
             ("Singapore", "MARINA BAY", "#ffb36b", "#ff5a36", "#3a1608", "#ffe0c2", "On arrival"),
             ("Indonesia", "BALI", "#a8f0c6", "#2fbf8f", "#06261c", "#d9ffee", "e-Visa")]
    cs = ""
    for i, (n, sub, a, b2, ink, tint, route) in enumerate(cards):
        cs += (f'<a class="gc" href="/countries" style="--a:{a};--b:{b2};--ink:{ink};--tint:{tint};--d:{i * .12}s">'
               f'<span class="gc-sky"></span><span class="gc-top"><i>{i + 1:02d}</i><span class="gc-route">{route}</span></span>'
               f'<span class="gc-name">{n.upper()}</span><span class="gc-sub">{sub}</span><span class="gc-go">View guide &rarr;</span></a>')
    stats = "".join(f'<div class="st"><b>{v}</b><small>{l}</small></div>' for v, l in [("88", "country guides"), ("26", "visa destinations"), ("4", "visa routes"), ("Blue Area", "Islamabad office")])
    css = ROAD_CSS.replace("BG", bg)
    content = f"""<main class="rd" id="main"><div class="bgimg" aria-hidden="true"></div>
<header class="top"><div class="brand"><span></span>AL ARBAB · Travel &amp; Tours</div><nav class="nav" aria-label="Preview"><span>Visas</span><span>Flights</span><span>Umrah</span><span>Contact</span></nav></header>
<section class="main"><p class="eyebrow">Blue Area, Islamabad</p>
<h1>Visa &amp; travel <em>made simple</em></h1>
<p class="lead">Asian visit visas we process directly, Schengen, UK, USA and Canada files prepared and guided, plus flights, Umrah and hotels from one desk.</p>
<div class="cta"><a class="p" href="{WA}" target="_blank" rel="noopener">WhatsApp us</a><a class="g" href="/countries">Browse destinations</a></div></section>
<div class="row" aria-label="Featured destinations">{cs}</div>
<div class="stats">{stats}</div></main>"""
    page("/preview-hero-road", "Hero glass preview | AL ARBAB", "Preview only.", content, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-hero-road"]
    PAGES["/preview-hero-road"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

ROAD_CSS = """
.rd{position:relative;min-height:100vh;overflow:hidden;background:#0b0f1e;color:#fff}
.rd .bgimg{position:absolute;inset:0;background:url(BG) center/cover no-repeat;transform:scale(1.04);animation:rdz 22s ease-in-out infinite alternate}
.rd .bgimg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,8,20,.35),rgba(6,8,20,.15) 40%,rgba(6,8,20,.55))}
@keyframes rdz{to{transform:scale(1.12) translateX(-1.5%)}}
.rd .top{position:absolute;left:0;right:0;top:0;display:flex;justify-content:space-between;align-items:center;padding:22px 5vw;z-index:3}
.rd .brand{display:flex;align-items:center;gap:12px;font:800 14px Archivo,sans-serif;letter-spacing:.12em;text-transform:uppercase}
.rd .brand span{display:block;width:3px;height:30px;background:#ffb020;border-radius:3px}
.rd .nav{display:flex;gap:26px;font:600 13px Inter,sans-serif;letter-spacing:.06em;text-transform:uppercase;opacity:.85}
.rd .main{position:relative;z-index:2;padding:11vh 5vw 0}
.rd .eyebrow{display:inline-block;font:700 11px Inter,sans-serif;letter-spacing:.3em;text-transform:uppercase;color:#ffc56b}
.rd h1{font:900 clamp(34px,5.4vw,72px)/.98 Archivo,sans-serif;text-transform:uppercase;margin:14px 0 0;max-width:14ch;text-shadow:0 6px 40px rgba(0,0,0,.35)}
.rd h1 em{font-style:italic;font-weight:300;text-transform:none;color:#ffc56b}
.rd .lead{max-width:480px;font:500 15px/1.55 Inter,sans-serif;color:#eef2ff;margin-top:18px;text-shadow:0 2px 14px rgba(0,0,0,.4)}
.rd .cta{display:flex;gap:12px;margin-top:24px;flex-wrap:wrap}
.rd .cta a{min-height:48px;padding:0 22px;border-radius:999px;display:inline-flex;align-items:center;font:700 14px Inter,sans-serif}
.rd .cta .p{background:#fff;color:#0b1220}.rd .cta .g{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.4);backdrop-filter:blur(12px);color:#fff}
.rd .row{position:absolute;left:0;right:0;bottom:118px;z-index:2;display:flex;gap:20px;padding:0 5vw;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}
.rd .row::-webkit-scrollbar{display:none}
.gc{position:relative;flex:0 0 clamp(200px,20vw,250px);height:clamp(220px,30vh,290px);border-radius:26px;overflow:hidden;color:var(--ink);display:flex;flex-direction:column;justify-content:flex-end;padding:20px;scroll-snap-align:start;
  background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.55);backdrop-filter:blur(22px) saturate(160%);-webkit-backdrop-filter:blur(22px) saturate(160%);box-shadow:0 30px 60px -28px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.6);transition:transform .45s cubic-bezier(.2,.8,.2,1),box-shadow .45s;animation:gcin .8s cubic-bezier(.2,.8,.2,1) var(--d) both;text-decoration:none}
.gc:hover{transform:translateY(-10px) scale(1.02)}
.gc-sky{position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 0,var(--a),transparent 60%),linear-gradient(180deg,var(--tint),var(--b) 110%);opacity:.9;z-index:-1}
.gc-top{position:absolute;top:16px;left:16px;right:16px;display:flex;justify-content:space-between;align-items:center}
.gc-top i{font:800 13px Archivo,sans-serif;font-style:normal;background:rgba(255,255,255,.85);color:#0b1220;border-radius:999px;padding:5px 11px}
.gc-route{font:700 10px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;background:rgba(0,0,0,.35);color:#fff;padding:5px 9px;border-radius:999px}
.gc-name{font:900 clamp(26px,2.4vw,34px)/.95 Archivo,sans-serif;letter-spacing:.01em}
.gc-sub{font:600 11px Inter,sans-serif;letter-spacing:.14em;margin-top:6px;opacity:.85}
.gc-go{margin-top:14px;font:700 12px Inter,sans-serif;padding-top:12px;border-top:1px solid rgba(0,0,0,.18)}
@keyframes gcin{from{opacity:0;transform:translateY(40px) scale(.96)}}
.rd .stats{position:absolute;left:0;right:0;bottom:0;z-index:3;display:grid;grid-template-columns:repeat(4,1fr);background:rgba(8,10,24,.72);backdrop-filter:blur(18px);border-top:1px solid rgba(255,255,255,.14)}
.rd .st{padding:22px 5vw;border-right:1px solid rgba(255,255,255,.12)}.rd .st:last-child{border-right:0}
.rd .st b{display:block;font:900 clamp(22px,2.6vw,34px)/1 Archivo,sans-serif;color:#ffc56b}
.rd .st small{display:block;margin-top:6px;font:600 11px Inter,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:#c7d0ea}
@media(max-width:760px){.rd .nav{display:none}.rd .stats{grid-template-columns:repeat(2,1fr)}.rd .row{bottom:200px}.rd .main{padding-top:10vh}}
@media(prefers-reduced-motion:reduce){.rd .bgimg,.gc{animation:none}}
"""

SPLASH = True
SPLASH = True   # welcome screen on the home page, once per session (assets/splash.css + splash.js); skipped for crawlers and "reduce motion"

def splash_home():
    if not SPLASH:
        return
    h, pr, noi = PAGES["/"]
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "splash.css"), encoding="utf-8").read(), flags=re.S).split())
    js = re.sub(r"\n\s*", "\n", open(os.path.join(ROOT, "assets", "splash.js"), encoding="utf-8").read())
    gate = ("<script>(function(){try{if(!sessionStorage.getItem('abSplash')&&!/bot|crawl|spider|lighthouse|pagespeed|headless|gtmetrix/i.test(navigator.userAgent)"
            "&&innerWidth>=1000&&!matchMedia('(prefers-reduced-motion: reduce)').matches&&!location.hash)document.documentElement.classList.add('splash')}catch(e){}})()</script>")
    letters = lambda t, o=0: "".join(f'<span class="sp" style="--i:{i + o}"></span>' if ch == " " else f'<span style="--i:{i + o}">{ch}</span>' for i, ch in enumerate(t))
    plane = '<svg viewBox="-24 -20 48 40" aria-hidden="true"><path d="M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z" fill="#fff"/></svg>'
    overlay = (f'<div id="splash" aria-hidden="true"><canvas id="spc"></canvas><i class="sp-fl"></i><div class="sp-in"><div class="sp-logo"><img src="{AL_MARK}" alt="" width="321" height="260" loading="lazy"><span class="sp-t"><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></div><i class="sp-bar"></i></div>'
               f'<button class="sp-skip" type="button" tabindex="-1">Skip</button></div>')
    h = h.replace("</head>", f"{gate}<style>{css}</style></head>", 1)
    h = h.replace("<body>", "<body>" + overlay, 1)
    h = h.replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/"] = (h, pr, noi)

SPLASH_PREVIEWS = True   # /preview-splash: twenty typography-only welcome screens in seven colour themes (noindex, not in the sitemap, not in the zip)
SPLASH_VARIANTS = [
    ("Mask rise", "Each line slides up out of a hidden mask, then a thin rule draws under it. Sharp and calm."),
    ("Outline fill", "The name appears as a thin outline, then fills from the bottom like liquid."),
    ("Letter flip", "Letters flip up one by one in 3D, then TRAVEL & TOURS spreads out into place."),
    ("Word slider", "A one-line slot slides through WELCOME, VISAS, FLIGHTS, UMRAH and lands on AL ARBAB."),
    ("Split meet", "The top half of the name flies in from the left, the bottom half from the right, and they join."),
    ("Metal shine", "Dark lettering with a bright shine sweeping across, hairlines and the office coordinates in the corners."),
    ("Typed", "The name is typed out with a blinking cursor, like a boarding terminal."),
    ("Sharpen in", "Wide, blurred letters pull together and snap into sharp focus."),
    ("Boarding pass", "A boarding pass slides in, a scanner line reads it, then WELCOME ABOARD."),
    ("Departure board", "Airport split-flap board: letters flick through random characters and settle on AL ARBAB TRAVEL & TOURS."),
    ("World routes", "Flight routes draw out from Islamabad to Thailand, Dubai, Malaysia, Singapore and Umrah, then the name rises."),
    ("Passport stamp", "A round WELCOME passport stamp slams onto the screen with a small shake, then the name fades in."),
    ("Plane progress", "A progress bar with a small plane riding its tip and a percentage counter, then the name appears at 100%."),
    ("Orbit globe", "A line globe with a plane circling it on a dotted orbit, then the name fades in."),
    ("Document scan", "A passport-style document is scanned by a laser line, a tick pops, then WELCOME."),
    ("Monogram ring", "A big A inside a rotating ring of text: AL ARBAB, TRAVEL & TOURS, ISLAMABAD, VISA, FLIGHTS, UMRAH."),
    ("Card fan", "Three cards (VISA, FLIGHTS, UMRAH) fan out with soft shadows, then the name rises."),
    ("Counter fill", "The name is an outline that fills from the bottom while a big counter runs from 0 to 100."),
    ("Line draw", "Like the reference you sent: dark navy screen, the name drawn as thin lines with a cyan and a white dash chasing along the letters, then it fills."),
    ("Line monogram", "Like the reference you sent: a small A drawn in cyan and white lines inside a spinning ring, the name appears under it."),
]
SPLASH_THEMES = [("ocean", "Ocean (reference)", "#0b1c26"), ("black", "Black", "#050606"), ("green", "Deep green", "#0d2f26"), ("navy", "Navy", "#0f1c3d"), ("violet", "Violet", "#241552"),
                 ("milky", "Milky white", "#f6fbfb"), ("aurora", "Aurora", "#a9cfc2")]

def splash_previews():
    """One noindex page where each typography-only welcome screen can be played full screen in several colour themes. Nothing here is on the live pages."""
    if not SPLASH_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "splash-previews.css"), encoding="utf-8").read(), flags=re.S).split())
    cards = "".join(f'<div class="spv-card"><span class="n">OPTION {i + 1}</span><b>{e(n)}</b><small>{e(d)}</small><button type="button" data-v="{i + 1}">Play</button></div>' for i, (n, d) in enumerate(SPLASH_VARIANTS))
    ths = '<div class="spv-th"><b>Colour theme:</b>' + "".join(f'<button type="button" aria-pressed="false"><i style="background:{c}"></i>{e(n)}</button>' for k, n, c in SPLASH_THEMES) + '</div>'
    content = (f'<section class="sec"><div class="head"><div><h2>Welcome screen options</h2></div><p class="lead">Typography only, no logo. Pick a colour theme, then press Play. '
               f'Inside the screen, "Theme" cycles the colours and "Replay" runs it again. Nothing here is live yet.</p></div>{ths}'
               f'<div class="spv-bar"><button type="button" id="spvAll">Play all, one after another</button></div><div class="spv-grid">{cards}</div></section>')
    ph = pagehead("Preview", "Welcome screens", "Twenty typography-only options for the first screen of the home page, in seven colour themes. Tell me the number and the theme you like.")
    body = shell("/preview-splash", [("Home", "/"), ("Welcome screen preview", None)], ph, content)
    js = open(os.path.join(ROOT, "assets", "splash-previews.js"), encoding="utf-8").read().replace("__N__", json.dumps([n for n, _ in SPLASH_VARIANTS])).replace("__TH__", json.dumps([[k, n] for k, n, _ in SPLASH_THEMES]))
    page("/preview-splash", "Welcome screen preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-splash"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-splash"] = (h, pr, True)

LOGO_PREVIEWS = True   # /preview-logo: logo concepts (AL mark + wordmark) in colour combinations, as a backlit signage mock (noindex, not in the sitemap, not in the zip)

def logo_previews():
    if not LOGO_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "logo-previews.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "logo-previews.js"), encoding="utf-8").read()
    content = '''<section class="sec"><div class="head"><div><h2>Logo preview</h2></div><p class="lead">Three concepts, each with AL in the mark, shown in six colour combinations. Pick a concept, a colour set and a wall. Nothing here is live.</p></div>
<div class="lp-ctl lp-con"><b>Concept:</b><button type="button">1 · Blade + wordmark</button><button type="button">2 · Monogram tile</button><button type="button">3 · Stacked arc</button></div>
<div class="lp-ctl lp-wall"><b>Signage wall:</b><button type="button" data-w="light">Light wall</button><button type="button" data-w="dark">Dark wall</button><span id="lpName" style="font:600 13px Inter,sans-serif;margin-left:8px"></span></div>
<div class="wall light" id="lpWall"><div class="lg" id="lpWallLogo"></div></div>
<div class="lp-row"><div><p class="lp-cap">On white</p><div class="lp-card w" id="lpWhite"></div></div><div><p class="lp-cap">On dark</p><div class="lp-card k" id="lpDark"></div></div></div>
<div class="lp-row"><div><p class="lp-cap">In the website header</p><div class="lp-head" id="lpHead"></div></div><div><p class="lp-cap">Small sizes (favicon, app icon)</p><div class="lp-fav" id="lpFav"></div></div></div>
<h3 class="sub-h" style="margin-top:28px">All colour combinations for this concept (click one)</h3><div class="pgrid" id="lpGrid"></div></section>'''
    ph = pagehead("Preview", "Logo options", "A swoosh or AL mark with a bold wordmark and spaced TRAVEL &amp; TOURS, in the style of a backlit shop sign. Preview only; final choice later.")
    body = shell("/preview-logo", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo", "Logo preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-logo"] = (h, pr, True)

LOGO2_PREVIEWS = True   # /preview-logo-orbit: plane + orbit logo options with gradients (noindex, not in the sitemap, not in the zip)

def logo2_previews():
    if not LOGO2_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "logo2-previews.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "logo2-previews.js"), encoding="utf-8").read()
    content = """<section class="sec"><div class="head"><div><h2>Your supplied logo, unchanged</h2></div><p class="lead">This is the exact licensed mark from the file you sent. Nothing is redrawn or shaded. Only the surroundings change: lockups, backgrounds, tiles. Nothing here is live.</p></div>
<div class="l2g" id="l2Cards"></div>
<h3 class="sub-h" style="margin-top:30px">On colour gradients (the mark sits on a white badge so it stays exactly as supplied)</h3><div class="l2g" id="l2Grad"></div></section>"""
    ph = pagehead("Preview", "Your logo, in use", "The supplied plane and orbit mark in a header, a lockup, an app icon, a welcome screen and on eight gradient backgrounds. Tell me the ones you like.")
    body = shell("/preview-logo-orbit", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-orbit", "Logo preview orbit | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-orbit"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-logo-orbit"] = (h, pr, True)

LOGOSIGN_PREVIEWS = True   # /preview-logo-sign: swoosh + plane logo as backlit signage and on-site fit, 8 colours (noindex, not in the sitemap, not in the zip)

def logosign_previews():
    if not LOGOSIGN_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "logo-sign.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "logo-sign.js"), encoding="utf-8").read()
    content = """<section class="sec"><div class="head"><div><h2>Swoosh + plane signage</h2></div><p class="lead">An original swoosh mark with AL ARBAB and an aeroplane, drawn as a backlit shop sign and then fitted into the website. Pick a colour, the plane position and the wall. Nothing here is live.</p></div>
<div class="ls-ctl ls-pal"></div>
<div class="ls-ctl ls-pl"><b>Aeroplane:</b><button type="button" data-v="tip">Flying off the tip</button><button type="button" data-v="in">Inside the swoosh</button><button type="button" data-v="off">None</button></div>
<div class="ls-ctl ls-wall"><b>Wall:</b><button type="button" data-v="night">Night</button><button type="button" data-v="light">Day</button></div>
<p class="ls-name" id="lsName"></p>
<div id="lsMain"></div>
<h3 class="sub-h" style="margin-top:28px">Every colour on a day wall (click one to see it large above)</h3><div class="agrid" id="lsAll"></div>
<h3 class="sub-h" style="margin-top:28px">How it fits on the website (in the selected colour)</h3>
<div class="fgrid"><div class="fbox m"><h4>Header</h4><div id="fHead"></div></div><div class="fbox"><h4>Over the hero photo, in glass</h4><div id="fHero" style="width:100%"></div></div>
<div class="fbox d"><h4>Footer</h4><div id="fFoot" style="width:100%;display:grid;justify-items:center"></div></div><div class="fbox m"><h4>Favicon and app icon</h4><div class="fav" id="fFav"></div></div>
<div class="fbox"><h4>Welcome screen</h4><div id="fSplash" style="width:100%"></div></div></div></section>"""
    ph = pagehead("Preview", "Signage + website fit", "The swoosh and plane as a backlit sign in eight colours, then in the header, hero, footer, favicon and welcome screen. Tell me the colour and plane position you like.")
    body = shell("/preview-logo-sign", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-sign", "Logo signage preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-sign"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-logo-sign"] = (h, pr, True)

LOGOAL_PREVIEWS = True   # /preview-logo-al: AL monogram + plane marks (noindex, not in the sitemap, not in the zip)

def logoal_previews():
    if not LOGOAL_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "logo-al.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "logo-al.js"), encoding="utf-8").read()
    content = """<section class="sec"><div class="head"><div><h2>AL monogram marks</h2></div><p class="lead">The swoosh tail is replaced by the letters AL, drawn as clean geometric shapes, with the aeroplane kept. Five designs, five colour sets. Nothing here is live.</p></div>
<div class="al-ctl al-pal"></div>
<div class="al-ctl al-bg"><b>Background:</b><button type="button" data-b="white">White</button><button type="button" data-b="milky">Milky</button><button type="button" data-b="dark">Dark</button></div>
<div class="alg" id="alGrid"></div></section>"""
    ph = pagehead("Preview", "AL logo options", "Five ways to turn the tail into AL: a ligature, a swoosh foot, a speed italic, an orbit ring and an app tile. Tell me the number and colour.")
    body = shell("/preview-logo-al", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-al", "AL logo preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-al"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-logo-al"] = (h, pr, True)

LOGOPK_PREVIEWS = True   # /preview-logo-pk: the AL + plane-on-orbit mark from alarbabtravel.pk, plus new designs in that style (noindex, not in the sitemap, not in the zip)

def logopk_previews():
    if not LOGOPK_PREVIEWS:
        return
    svg = open(os.path.join(ROOT, "assets", "brand", "al-mark-pk.svg"), encoding="utf-8").read()
    inner = re.sub(r"^\s*<svg[^>]*>|</svg>\s*$", "", svg.strip())
    inner = inner.replace('fill="#ffffff"', 'style="fill:var(--lt,#fff)"').replace('fill="#e61e2b"', 'style="fill:var(--rd,#e61e2b)"')
    sym = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="alpk" viewBox="4400 4000 6200 5000">' + inner + '</symbol></svg>'
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "logo-al.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "logo-pk.js"), encoding="utf-8").read()
    content = sym + """<section class="sec"><div class="head"><div><h2>AL + plane on an orbit</h2></div><p class="lead">The first card is the mark from your alarbabtravel.pk site, unchanged. The other four are new designs in the same idea: bold AL letters, a red orbit and a plane. No tail. Nothing here is live.</p></div>
<div class="al-ctl al-pal"></div>
<div class="al-ctl al-bg"><b>Background:</b><button type="button" data-b="white">White</button><button type="button" data-b="milky">Milky</button><button type="button" data-b="dark">Dark</button></div>
<div class="alg" id="pkGrid"></div></section>"""
    ph = pagehead("Preview", "AL mark options", "The AL mark with a plane on an orbit, like on alarbabtravel.pk, with new designs next to it. Tell me the number and colour.")
    body = shell("/preview-logo-pk", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-pk", "AL mark preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-pk"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-logo-pk"] = (h, pr, True)

LOGOCR_PREVIEWS = True   # /preview-logo-cr: 15 original AL + aeroplane marks, red first, with colour sets (noindex, not in the sitemap, not in the zip)

def logocr_previews():
    if not LOGOCR_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "logo-al.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "logo-cr.js"), encoding="utf-8").read()
    content = """<section class="sec"><div class="head"><div><h2>15 AL + aeroplane marks</h2></div><p class="lead">All new and original, red first. Each card shows the mark large, in the header pill, and at 64, 32 and 20 px. Switch the colour set and the background to see how each one applies. Nothing here is live.</p></div>
<div class="al-ctl al-pal"></div>
<div class="al-ctl al-bg"><b>Background:</b><button type="button" data-b="white">White</button><button type="button" data-b="milky">Milky</button><button type="button" data-b="dark">Dark</button></div>
<div class="alg" id="crGrid"></div></section>"""
    ph = pagehead("Preview", "15 AL logo designs", "New AL and aeroplane marks in red, with colour sets and backgrounds to try. Tell me the numbers you like.")
    body = shell("/preview-logo-cr", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-cr", "AL logo designs preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-cr"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-logo-cr"] = (h, pr, True)

LOGOFINAL_PREVIEWS = True   # /preview-logo-final: the two supplied logos (and logo 1 with a plane) on the website (noindex, not in the sitemap, not in the zip)

def logofinal_previews():
    if not LOGOFINAL_PREVIEWS:
        return
    V = [("A", "Logo 1, as supplied", "logo1.png", "mark1.png"), ("B", "Logo 1 with a plane on the tip", "logo1-plane.png", "mark1-plane.png"), ("C", "Logo 2, as supplied", "logo2.png", "mark2.png")]
    src = lambda f: f"/assets/brand/{f}?v={asset_hash('brand/' + f)}"
    cards = ""
    for k, n, lg, mk in V:
        L, M = src(lg), src(mk)
        cards += f"""<article class="lf {k}"><h3>{k} · {n}</h3>
<div class="row"><div class="bx w"><img src="{L}" alt="" style="height:150px"></div><div class="bx m"><img src="{L}" alt="" style="height:150px"></div></div>
<p class="cap">Header</p><div class="bx m hdr"><div class="pillh"><img src="{L}" alt="" style="height:50px"></div><span class="fake">HOME · VISAS · DESTINATIONS · FLIGHTS · UMRAH</span></div>
<p class="cap">Header, mark + name</p><div class="bx m hdr"><div class="pillh"><img src="{M}" alt="" style="height:44px"><span class="nm"><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></div></div>
<p class="cap">Footer (dark)</p><div class="bx k"><div class="pillh"><img src="{L}" alt="" style="height:50px"></div></div>
<p class="cap">Welcome screen</p><div class="bx n"><div class="tile"><img src="{L}" alt="" style="height:120px"></div></div>
<p class="cap">Favicon / app icon</p><div class="bx m fav"><span style="width:96px;height:96px;background-image:url({M})"></span><span style="width:48px;height:48px;background-image:url({M})"></span><span style="width:32px;height:32px;background-image:url({M})"></span><span style="width:16px;height:16px;border-radius:4px;background-image:url({M})"></span></div></article>"""
    css = """.lfg{display:grid;gap:22px}.lf{display:grid;gap:8px;padding:18px;border-radius:24px;background:rgba(255,255,255,.7);border:1px solid #fff;box-shadow:0 22px 44px -30px rgba(15,23,42,.45)}
.lf h3{font:800 18px Archivo,sans-serif;margin:0 0 4px}.cap{font:700 12px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#506661;margin:8px 0 0}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:12px}
.bx{border-radius:18px;min-height:110px;display:flex;align-items:center;justify-content:center;gap:16px;padding:18px;flex-wrap:wrap;border:1px solid rgba(11,18,32,.08)}
.bx img{display:block;width:auto;max-width:100%}.bx.w{background:#fff}.bx.m{background:radial-gradient(60% 50% at 8% 8%,#e4f6f5,transparent 62%),radial-gradient(55% 50% at 92% 14%,#e8f6f5,transparent 62%),#f6fbfb}
.bx.k{background:#0a0f0e}.bx.n{background:radial-gradient(60% 50% at 20% 15%,#17604b,transparent 65%),linear-gradient(160deg,#0d2f26,#071d17);min-height:220px}
.hdr{justify-content:flex-start}.pillh{display:flex;align-items:center;gap:10px;padding:8px 20px 8px 14px;border-radius:999px;background:rgba(255,255,255,.9);border:1px solid #fff;box-shadow:0 14px 30px -20px rgba(15,23,42,.5)}
.pillh .nm{display:grid;line-height:1.05}.pillh b{font:900 20px Archivo,sans-serif;color:#0a1530}.pillh small{font:700 11px Inter,sans-serif;letter-spacing:.2em;color:#506661}
.fake{font:700 12px Inter,sans-serif;letter-spacing:.08em;color:#506661}.tile{background:#fff;border-radius:28px;padding:20px 26px;box-shadow:0 30px 60px -24px rgba(0,0,0,.6)}
.fav{align-items:flex-end}.fav span{display:block;background-color:#fff;background-repeat:no-repeat;background-position:center;background-size:78%;border-radius:22%;box-shadow:0 10px 24px -14px rgba(15,23,42,.5),inset 0 0 0 1px rgba(11,18,32,.08);flex:none}.fav img{width:100%!important;height:auto!important;max-height:100%;object-fit:contain}.lf.C .bx.w,.lf.C .bx.m{background:#0d1214}.lf.C .pillh{background:#0d1214;border-color:#2a3640}.lf.C .pillh b{color:#fff}.lf.C .pillh small{color:#9fb0ab}.lf.C .tile{background:#0d1214}.lf.C .fav span{background-color:#0d1214}.lf.C .fake{color:#9fb0ab}"""
    content = f"""<section class="sec"><div class="head"><div><h2>Your two logos on the website</h2></div><p class="lead">A and C are exactly as you sent them (white background removed). B is logo 1 with a red plane added on the top tip. Nothing here is live.</p></div><div class="lfg">{cards}</div></section>"""
    ph = pagehead("Preview", "Final logo preview", "Logo 1, logo 1 with a plane, and logo 2: in the header, footer, welcome screen and as a favicon. Tell me A, B or C.")
    body = shell("/preview-logo-final", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-final", "Final logo preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-final"]
    PAGES["/preview-logo-final"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

LOGOSTICKER_PREVIEWS = True   # /preview-logo-sticker: the cream sticker logo on the website (noindex, not in the sitemap, not in the zip)

def logosticker_previews():
    if not LOGOSTICKER_PREVIEWS:
        return
    L = f"/assets/brand/sticker.png?v={asset_hash('brand/sticker.png')}"
    M = f"/assets/brand/sticker-mark.png?v={asset_hash('brand/sticker-mark.png')}"
    css = """.sk{display:grid;gap:14px}.sk .cap{font:700 12px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#506661;margin:8px 0 0}
.sk .bx{border-radius:20px;min-height:120px;display:flex;align-items:center;gap:18px;padding:18px;flex-wrap:wrap;border:1px solid rgba(11,18,32,.1)}
.sk img{display:block;width:auto;max-width:100%}.sk .w{background:#fff}.sk .m{background:radial-gradient(60% 50% at 8% 8%,#e4f6f5,transparent 62%),radial-gradient(55% 50% at 92% 14%,#e8f6f5,transparent 62%),#f6fbfb}
.sk .k{background:#0a0f0e}.sk .p{background:linear-gradient(180deg,rgba(8,20,18,.35),rgba(8,20,18,.6)),linear-gradient(135deg,#f2a15a,#3b6d8f 60%,#0c2a3a)}
.sk .n{background:radial-gradient(60% 50% at 20% 15%,#17604b,transparent 65%),linear-gradient(160deg,#0d2f26,#071d17);min-height:240px;justify-content:center}
.sk .fk{display:flex;gap:16px;align-items:flex-end}.sk .fk span{display:block;background:#fff;border-radius:22%;box-shadow:0 10px 24px -14px rgba(15,23,42,.5);background-repeat:no-repeat;background-position:center;background-size:80%}
.sk .nav{display:flex;align-items:center;gap:14px;width:100%;flex-wrap:nowrap}.sk .nav i{font:700 12px Inter,sans-serif;font-style:normal;letter-spacing:.08em;color:#506661;white-space:nowrap;overflow:hidden}
.sk .ncard{display:flex;align-items:center;justify-content:center}"""
    content = f"""<section class="sec"><div class="head"><div><h2>New sticker logo on the website</h2></div><p class="lead">Cut out cleanly from its white background (the cream and gold outline stay as supplied). Preview only, nothing is live.</p></div>
<div class="sk"><p class="cap">As supplied, on white and on the site background</p><div class="bx w"><img src="{L}" alt="" style="height:130px"></div><div class="bx m"><img src="{L}" alt="" style="height:130px"></div>
<p class="cap">Header, light (inner pages)</p><div class="bx m"><div class="nav"><img src="{L}" alt="" style="height:54px"><i>HOME · VISAS · DESTINATIONS · FLIGHTS · UMRAH · PACKAGES</i></div></div>
<p class="cap">Header over the hero photo (home)</p><div class="bx p"><div class="nav"><img src="{L}" alt="" style="height:54px"><i style="color:#fff">HOME · VISAS · DESTINATIONS · FLIGHTS · UMRAH · PACKAGES</i></div></div>
<p class="cap">Footer (dark)</p><div class="bx k"><img src="{L}" alt="" style="height:80px"></div>
<p class="cap">Welcome screen</p><div class="bx n"><img src="{L}" alt="" style="height:150px"></div>
<p class="cap">Favicon / app icon (the red 7 and plane)</p><div class="bx m"><div class="fk"><span style="width:96px;height:96px;background-image:url({M})"></span><span style="width:48px;height:48px;background-image:url({M})"></span><span style="width:32px;height:32px;background-image:url({M})"></span><span style="width:16px;height:16px;background-image:url({M});border-radius:4px"></span></div></div></div></section>"""
    ph = pagehead("Preview", "Sticker logo preview", "The new cream and gold logo in the header, footer, welcome screen and favicon. Tell me if I should apply it.")
    body = shell("/preview-logo-sticker", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-sticker", "Sticker logo preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-sticker"]
    PAGES["/preview-logo-sticker"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

PLANES_PREVIEW = False   # /preview-plane-a, /preview-plane-b: the two supplied aeroplane renders flying the hero route (noindex, not in the sitemap, not in the zip)

def planes_preview():
    if not PLANES_PREVIEW:
        return
    h0, _, _ = PAGES["/"]
    m = re.search(r'<g id="plane">.*?</g>', h0, flags=re.S)
    assert m
    opts = {"a": ("plane-a.png", 223, 520, "rotate(8)"), "b": ("plane-b.png", 288, 520, "rotate(-21) scale(-1,1)")}
    for k, (f, ih, iw, tf) in opts.items():
        w = 64; hh = w * ih / iw
        img = f'<g id="plane"><g transform="{tf}"><image href="/assets/brand/{f}?v={asset_hash("brand/" + f)}" x="{-w/2}" y="{-hh/2}" width="{w}" height="{hh:.1f}"/></g></g>'
        h = h0[:m.start()] + img + h0[m.end():]
        bar = ('<div style="position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:9999;display:flex;gap:8px;padding:8px 10px;border-radius:999px;background:#0b1220;font:600 13px Inter,sans-serif">'
               + "".join(f'<a href="/preview-plane-{x}" style="padding:8px 16px;border-radius:999px;color:{"#0b1220" if x == k else "#fff"};background:{"#fff" if x == k else "rgba(255,255,255,.14)"}">Plane {x.upper()}</a>' for x in "ab") + '</div>')
        h = h.replace("<body>", "<body>" + bar, 1)
        h = re.sub(r"<title>.*?</title>", "<title>Plane preview | AL ARBAB</title>", h, count=1, flags=re.S)
        h = h.replace(f'<link rel="canonical" href="{BASE}/">', f'<link rel="canonical" href="{BASE}/preview-plane-{k}">')
        h = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,nofollow">', h, count=1)
        PAGES[f"/preview-plane-{k}"] = (h, "0.1", True)

LOGOTEXT_PREVIEWS = True   # /preview-logo-text: text colour presets for the sticker logo (noindex, not in the sitemap, not in the zip)

def logotext_previews():
    if not LOGOTEXT_PREVIEWS:
        return
    P = [("navy", "Navy + Navy (current)", "sticker"), ("navy-red", "AL ARBAB navy, TRAVEL red", "sticker-navy-red"), ("black-red", "AL ARBAB black, TRAVEL red", "sticker-black-red"),
         ("green-maroon", "AL ARBAB green, TRAVEL maroon", "sticker-green-maroon"), ("blue-navy", "AL ARBAB blue, TRAVEL navy", "sticker-blue-navy"),
         ("maroon-black", "AL ARBAB maroon, TRAVEL black", "sticker-maroon-black"), ("teal-navy", "AL ARBAB teal, TRAVEL navy", "sticker-teal-navy"),
         ("violet-black", "AL ARBAB violet, TRAVEL black", "sticker-violet-black"), ("charcoal-red", "AL ARBAB charcoal, TRAVEL red", "sticker-charcoal-red"),
         ("green-black", "AL ARBAB green, TRAVEL black", "sticker-green-black")]
    cards = ""
    for k, n, f in P:
        u = f"/assets/brand/{f}.png?v={asset_hash('brand/' + f + '.png')}"
        cards += f"""<article class="tp"><h3>{n}</h3><div class="b w"><img src="{u}" alt="" style="height:96px"></div>
<div class="b m"><div class="nv"><img src="{u}" alt="" style="height:58px"><i>HOME · VISAS · DESTINATIONS · FLIGHTS</i></div></div>
<div class="b p"><img src="{u}" alt="" style="height:58px"></div><div class="b k"><img src="{u}" alt="" style="height:58px"></div></article>"""
    css = """.tpg{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(330px,100%),1fr));gap:16px}.tp{display:grid;gap:8px;padding:14px;border-radius:22px;background:rgba(255,255,255,.7);border:1px solid #fff;box-shadow:0 20px 40px -30px rgba(15,23,42,.45)}
.tp h3{font:800 16px Archivo,sans-serif;margin:0}.tp .b{border-radius:14px;padding:12px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(11,18,32,.08);min-height:74px}.tp img{display:block;width:auto;max-width:100%}
.tp .w{background:#fff}.tp .m{background:radial-gradient(60% 50% at 8% 8%,#e4f6f5,transparent 62%),radial-gradient(55% 50% at 92% 14%,#e8f6f5,transparent 62%),#f6fbfb;justify-content:flex-start}
.tp .p{background:linear-gradient(180deg,rgba(8,20,18,.3),rgba(8,20,18,.55)),linear-gradient(135deg,#f2a15a,#3b6d8f 60%,#0c2a3a)}.tp .k{background:#0a0f0e}
.tp .nv{display:flex;align-items:center;gap:12px}.tp .nv i{font:700 11px Inter,sans-serif;font-style:normal;letter-spacing:.08em;color:#506661;white-space:nowrap}"""
    content = f"""<section class="sec"><div class="head"><div><h2>Logo text colour presets</h2></div><p class="lead">Two-colour text presets: AL ARBAB in one colour and TRAVEL & TOURS in another. The red 7, plane, cream fill and gold outline stay the same. Each shows on white, the site header, a hero photo and the dark footer. Nothing is live.</p></div><div class="tpg">{cards}</div></section>"""
    ph = pagehead("Preview", "Logo text colours", "Pick the text colour you like for the new logo. I will apply it to the header, footer, welcome screen and favicon files.")
    body = shell("/preview-logo-text", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-logo-text", "Logo text colour preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-logo-text"]
    PAGES["/preview-logo-text"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

HEADERLOGO_PREVIEWS = True   # /preview-header-logo: modern header logo lockups (noindex, not in the sitemap, not in the zip)

def headerlogo_previews():
    if not HEADERLOGO_PREVIEWS:
        return
    M = f"/assets/brand/mark1-plane.png?v={asset_hash('brand/mark1-plane.png')}"
    S = f"/assets/brand/sticker-s.png?v={asset_hash('brand/sticker-s.png')}"
    def lock(cls, name, dark):
        return f'<div class="lk {cls} {"on-photo" if dark else ""}"><span class="mk"><img src="{M}" alt=""></span><span class="tx"><b>AL <em>ARBAB</em></b><small>TRAVEL &amp; TOURS</small></span></div>'
    V = [("1 · Clean two-tone", "c1"), ("2 · Frosted glass pill", "c2"), ("3 · Dark pill", "c3"), ("4 · Mark in a circle badge", "c4"),
         ("5 · Stacked, centred", "c5"), ("6 · Gradient name + red rule", "c6"), ("7 · Large mark, light text", "c7")]
    cards = ""
    for n, c in V:
        cards += f'<article class="hl"><h3>{n}</h3><div class="st m">{lock(c, n, False)}<i>HOME · VISAS · DESTINATIONS · FLIGHTS · UMRAH</i></div><div class="st p">{lock(c, n, True)}<i>HOME · VISAS · DESTINATIONS · FLIGHTS · UMRAH</i></div></article>'
    cards += f'<article class="hl"><h3>0 · Current sticker logo</h3><div class="st m"><img src="{S}" alt="" style="height:64px"><i>HOME · VISAS · DESTINATIONS · FLIGHTS · UMRAH</i></div><div class="st p"><img src="{S}" alt="" style="height:64px"><i>HOME · VISAS · DESTINATIONS · FLIGHTS · UMRAH</i></div></article>'
    css = """.hlg{display:grid;gap:16px}.hl{display:grid;gap:8px;padding:14px;border-radius:22px;background:rgba(255,255,255,.7);border:1px solid #fff;box-shadow:0 20px 40px -30px rgba(15,23,42,.45)}
.hl h3{font:800 16px Archivo,sans-serif;margin:0}.st{display:flex;align-items:center;gap:22px;padding:14px 18px;border-radius:16px;overflow:hidden;border:1px solid rgba(11,18,32,.08)}
.st i{font:700 11px Inter,sans-serif;font-style:normal;letter-spacing:.1em;color:#506661;white-space:nowrap}.st.p i{color:#fff}
.st.m{background:radial-gradient(60% 50% at 8% 8%,#e4f6f5,transparent 62%),radial-gradient(55% 50% at 92% 14%,#e8f6f5,transparent 62%),#f6fbfb}
.st.p{background:linear-gradient(180deg,rgba(8,20,18,.25),rgba(8,20,18,.5)),linear-gradient(120deg,#3f8fd0,#2e8a73 55%,#e8b45a)}
.lk{display:flex;align-items:center;gap:10px;flex:none}.lk .mk img{display:block;height:46px;width:auto}.lk b{display:block;font:900 22px/1 Archivo,sans-serif;color:#073b40;letter-spacing:.01em;white-space:nowrap}
.lk b em{font-style:normal;color:#0e7c86}.lk small{display:block;font:700 10.5px Inter,sans-serif;letter-spacing:.3em;color:#073b40;margin-top:5px;white-space:nowrap}
.lk.on-photo b,.lk.on-photo b em{color:#fff;text-shadow:0 1px 8px rgba(0,0,0,.35)}.lk.on-photo small{color:#fff}
.c2{padding:6px 20px 6px 10px;border-radius:999px;background:rgba(255,255,255,.55);border:1px solid rgba(255,255,255,.8);backdrop-filter:blur(14px);box-shadow:0 14px 30px -18px rgba(0,0,0,.4)}.c2.on-photo{background:rgba(255,255,255,.2);border-color:rgba(255,255,255,.5)}
.c3{padding:6px 20px 6px 10px;border-radius:999px;background:#0d1a2e;box-shadow:0 14px 30px -18px rgba(0,0,0,.6)}.c3 b,.c3 b em{color:#fff}.c3 small{color:#9fb6d6}
.c4 .mk{width:58px;height:58px;border-radius:50%;background:#fff;display:grid;place-items:center;box-shadow:0 10px 22px -10px rgba(0,0,0,.45)}.c4 .mk img{height:34px}
.c5{flex-direction:column;gap:2px;text-align:center}.c5 .tx{display:grid;justify-items:center}.c5 .mk img{height:44px}
.c6 b{background:linear-gradient(90deg,#0e7c86,#073b40);-webkit-background-clip:text;background-clip:text;color:transparent}.c6 b em{color:transparent}.c6.on-photo b{background:none;color:#fff}
.c6 small{position:relative;color:#506661}.c6 small::after{content:"";display:block;height:2px;width:60%;margin-top:5px;background:linear-gradient(90deg,#e30613,transparent)}
.c7 .mk img{height:60px}.c7 b{font-weight:800;font-size:19px;letter-spacing:.04em}.c7 small{letter-spacing:.34em}"""
    content = f"""<section class="sec"><div class="head"><div><h2>Modern header logo options</h2></div><p class="lead">Same red 7 and plane, with the name set in clean modern type instead of the cream sticker block. Each option is shown on the light site header and over a hero photo. Nothing is live.</p></div><div class="hlg">{cards}</div></section>"""
    ph = pagehead("Preview", "Header logo options", "Seven modern lockups next to the current sticker logo. Tell me the number.")
    body = shell("/preview-header-logo", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-header-logo", "Header logo preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-header-logo"]
    PAGES["/preview-header-logo"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

ALSYMBOL_PREVIEWS = True   # /preview-al-symbol: the red 7 + plane symbol combined with AL (noindex, not in the sitemap, not in the zip)

def alsymbol_previews():
    if not ALSYMBOL_PREVIEWS:
        return
    M = f"/assets/brand/mark1-plane.png?v={asset_hash('brand/mark1-plane.png')}"
    img = f'<img class="s7" src="{M}" alt="">'
    D = [("1 · 7 + stacked AL", f'<div class="sy a1">{img}<span class="al"><b>A</b><b>L</b></span></div>'),
         ("2 · AL tucked under the 7", f'<div class="sy a2">{img}<span class="al">AL</span></div>'),
         ("3 · 7 swoosh behind big AL", f'<div class="sy a3"><span class="al">AL</span>{img}</div>'),
         ("4 · Round badge", f'<div class="sy a4"><span class="ring">{img}<span class="al">AL</span></span></div>'),
         ("5 · Blue tile, white AL, red 7", f'<div class="sy a5"><span class="tile"><span class="al">AL</span>{img}</span></div>'),
         ("6 · AL with the 7 as its first stroke", f'<div class="sy a6">{img}<span class="al">AL</span><i class="ln"></i></div>')]
    cards = ""
    for n, h in D:
        cards += f'<article class="as"><h3>{n}</h3><div class="row"><div class="bx w big">{h}</div><div class="bx k big">{h}</div></div><div class="row"><div class="bx m small">{h}</div><div class="bx w tiny">{h}</div></div></article>'
    css = """.asg{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(380px,100%),1fr));gap:16px}.as{display:grid;gap:8px;padding:14px;border-radius:22px;background:rgba(255,255,255,.7);border:1px solid #fff;box-shadow:0 20px 40px -30px rgba(15,23,42,.45)}
.as h3{font:800 16px Archivo,sans-serif;margin:0}.row{display:grid;grid-template-columns:1fr 1fr;gap:8px}.bx{border-radius:14px;min-height:150px;display:grid;place-items:center;overflow:hidden;border:1px solid rgba(11,18,32,.08)}
.bx.w{background:#fff}.bx.k{background:#0d1a2e}.bx.m{background:radial-gradient(60% 50% at 8% 8%,#e4f6f5,transparent 62%),radial-gradient(55% 50% at 92% 14%,#e8f6f5,transparent 62%),#f6fbfb;min-height:90px}.bx.tiny{min-height:90px}
.sy{--u:1;position:relative;display:flex;align-items:center;gap:calc(8px*var(--u));font-family:Archivo,sans-serif}.bx.small .sy,.bx.tiny .sy{--u:.5}
.s7{display:block;height:calc(84px*var(--u));width:auto}.al{font-weight:900;line-height:.9;color:#073b40}.bx.k .al{color:#fff}
.a1 .al{display:grid;font-size:calc(52px*var(--u));letter-spacing:-.02em;color:#0e7c86}.bx.k .a1 .al{color:#fff}
.a2{flex-direction:column;gap:0}.a2 .s7{height:calc(104px*var(--u))}.a2 .al{font-size:calc(58px*var(--u));margin-top:calc(-30px*var(--u));letter-spacing:.02em;color:#073b40}
.a3{align-items:flex-end}.a3 .al{font-size:calc(84px*var(--u));letter-spacing:-.04em;color:#073b40}.a3 .s7{position:absolute;left:calc(-24px*var(--u));top:calc(-30px*var(--u));height:calc(72px*var(--u));opacity:.95}
.a4 .ring{width:calc(150px*var(--u));height:calc(150px*var(--u));border-radius:50%;background:#fff;border:calc(5px*var(--u)) solid #0e7c86;display:grid;place-items:center;position:relative;box-shadow:0 12px 26px -14px rgba(0,0,0,.5)}
.a4 .s7{position:absolute;top:calc(14px*var(--u));height:calc(66px*var(--u))}.a4 .al{position:absolute;bottom:calc(20px*var(--u));font-size:calc(38px*var(--u));color:#073b40}
.a5 .tile{width:calc(150px*var(--u));height:calc(150px*var(--u));border-radius:calc(34px*var(--u));background:linear-gradient(145deg,#2a86d8,#073b40);display:grid;place-items:center;position:relative;box-shadow:0 14px 30px -14px rgba(0,0,0,.5)}
.a5 .al{color:#fff;font-size:calc(62px*var(--u));letter-spacing:-.02em;margin-top:calc(26px*var(--u))}.a5 .s7{position:absolute;top:calc(-14px*var(--u));left:calc(10px*var(--u));height:calc(88px*var(--u));filter:drop-shadow(0 4px 8px rgba(0,0,0,.35))}
.a6 .al{font-size:calc(58px*var(--u));letter-spacing:-.03em;color:#073b40;margin-left:calc(-14px*var(--u))}.a6 .ln{position:absolute;left:calc(30px*var(--u));right:0;bottom:calc(-6px*var(--u));height:calc(4px*var(--u));border-radius:4px;background:linear-gradient(90deg,#e30613,#0e7c86)}"""
    content = f"""<section class="sec"><div class="head"><div><h2>The 7 symbol with AL</h2></div><p class="lead">Your red 7 and plane (unchanged) combined with the letters AL in six ways. Each is shown large on white and on dark, then at header size and at a very small size. Nothing is live.</p></div><div class="asg">{cards}</div></section>"""
    ph = pagehead("Preview", "7 + AL symbol", "Six ways to put AL together with the red 7 and plane. Tell me the number.")
    body = shell("/preview-al-symbol", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-al-symbol", "AL symbol preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-al-symbol"]
    PAGES["/preview-al-symbol"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

ALSHAPE_PREVIEWS = True   # /preview-al-shapes: symbol-only AL designs (Arabic Alif-Lam and Latin AL) with a plane (noindex, not in the sitemap, not in the zip)

def alshape_previews():
    if not ALSHAPE_PREVIEWS:
        return
    PL = "M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z"
    pl = lambda x, y, r, s, c="#e30613": f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="{PL}" fill="{c}"/></g>'
    G = lambda i: f'<defs><linearGradient id="g{i}" gradientUnits="userSpaceOnUse" x1="10" y1="10" x2="190" y2="190"><stop offset="0" stop-color="#ff4d3d"/><stop offset="1" stop-color="#b00012"/></linearGradient></defs>'
    st = lambda d, w, i, extra="": f'<path d="{d}" fill="none" stroke="url(#g{i})" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
    S = []
    # 1 Arabic Alif-Lam, bold geometric, plane as the accent above
    S.append(("1 · Alif-Lam, bold", G(1) + st("M136,52 V164", 24, 1) + st("M84,30 V120 C84,160 62,176 30,150", 24, 1) + pl(150, 24, -30, 1.1)))
    # 2 Alif-Lam, Lam's hook becomes a flight swoosh up to the plane
    S.append(("2 · Alif-Lam, swoosh to the plane", G(2) + st("M62,52 V164", 24, 2) + st("M118,30 V130 C118,170 150,170 170,120 C178,98 184,70 196,44", 24, 2) + pl(194, 30, -62, 1.15)))
    # 3 Alif-Lam inside a pointed arch
    S.append(("3 · Alif-Lam in a pointed arch", G(3) + st("M30,180 V104 C30,64 72,44 100,14 C128,44 170,64 170,104 V180", 12, 3) + st("M118,80 V150", 18, 3) + st("M86,62 V130 C86,158 70,166 52,150", 18, 3, 'opacity="1"') + pl(158, 38, -36, .9)))
    # 4 Latin AL as one monoline: plane is the crossbar of the A
    S.append(("4 · AL, plane as the crossbar", G(4) + st("M20,172 L66,44 L112,172", 18, 4) + pl(66, 128, 0, 1.55, "#e30613") + st("M142,44 V172 H188", 18, 4)))
    # 5 Italic speed AL with cuts
    S.append(("5 · AL, speed italic with cuts", G(5) + '<g transform="translate(26,0) skewX(-12)">' + st("M22,176 L66,40 L110,176", 26, 5, 'stroke-linejoin="miter"') + st("M40,128 H92", 18, 5) + st("M140,40 V176 H186", 26, 5, 'stroke-linejoin="miter"') + '</g>'
             + '<path d="M0,170 L200,70" stroke="#fff" stroke-width="5"/>' + pl(176, 30, -30, 1.1)))
    # 6 Arch A with L inside (Latin, Islamic arch silhouette)
    S.append(("6 · Arch-shaped A with L inside", G(6) + st("M34,178 V108 C34,66 74,46 100,16 C126,46 166,66 166,108 V178", 20, 6) + st("M84,92 V146 H128", 20, 6) + pl(172, 34, -36, .95)))
    # 7 Alif-Lam as a round badge with plane orbit
    S.append(("7 · Alif-Lam, round badge + orbit", G(7) + '<circle cx="100" cy="104" r="78" fill="url(#g7)"/>' + st("M118,60 V150", 18, 7, 'stroke="#fff"').replace("url(#g7)", "#fff") + st("M80,46 V112 C80,142 62,152 42,134", 18, 7).replace("url(#g7)", "#fff")
             + '<ellipse cx="100" cy="104" rx="96" ry="30" fill="none" stroke="#15171b" stroke-width="5" stroke-dasharray="290 70" transform="rotate(-24 100 104)"/>' + pl(176, 52, -50, 1.1, "#15171b")))
    # 8 App tile with white Alif-Lam and plane
    S.append(("8 · Red tile, white Alif-Lam", G(8) + '<rect x="6" y="6" width="188" height="188" rx="44" fill="url(#g8)"/>' + st("M126,56 V150", 20, 8).replace("url(#g8)", "#fff") + st("M80,40 V112 C80,144 62,154 40,136", 20, 8).replace("url(#g8)", "#fff") + pl(150, 44, -34, 1.0, "#fff")))
    cards = ""
    for n, s in S:
        sv = f'<svg viewBox="0 0 200 200">{s}</svg>'
        cards += f'<article class="sp"><h3>{n}</h3><div class="b w"><span class="lg">{sv}</span></div><div class="b k"><span class="lg">{sv}</span></div><div class="b m"><span class="sm">{sv}</span><span class="xs">{sv}</span></div></article>'
    css = """.spg{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(260px,100%),1fr));gap:14px}.sp{display:grid;gap:8px;padding:12px;border-radius:20px;background:rgba(255,255,255,.7);border:1px solid #fff;box-shadow:0 18px 36px -28px rgba(15,23,42,.45)}
.sp h3{font:800 14px Archivo,sans-serif;margin:0}.sp .b{border-radius:14px;display:flex;align-items:center;justify-content:center;gap:16px;min-height:150px;border:1px solid rgba(11,18,32,.08)}
.sp .w{background:#fff}.sp .k{background:#0d1a2e}.sp .m{background:radial-gradient(60% 50% at 8% 8%,#e4f6f5,transparent 62%),#f6fbfb;min-height:70px}
.sp .lg{width:120px;height:120px;display:block}.sp .sm{width:48px;height:48px;display:block}.sp .xs{width:24px;height:24px;display:block}.sp svg{width:100%;height:100%;display:block;overflow:visible}"""
    content = f"""<section class="sec"><div class="head"><div><h2>AL symbol designs</h2></div><p class="lead">Symbol only, no writing under it. Shapes built from the Arabic Alif-Lam (ال, how "Al" is written in Arabic) and from Latin AL, each with an aeroplane, in red. Shown large on white and dark, then at 48 and 24 px. Nothing is live.</p></div><div class="spg">{cards}</div></section>"""
    ph = pagehead("Preview", "AL symbol shapes", "Eight symbol-only designs to replace the red 7 and plane. Tell me the number.")
    body = shell("/preview-al-shapes", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-al-shapes", "AL symbol shapes | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-al-shapes"]
    PAGES["/preview-al-shapes"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

MINE_PREVIEWS = True   # /preview-al-mine: the owner's own AL mark in 12 colour sets (noindex, not in the sitemap, not in the zip)

def mine_previews():
    if not MINE_PREVIEWS:
        return
    T = [("original", "1 · Original", "Your teal and silver, as designed"),
         ("red-silver", "2 · Brand red + silver", "The AL ARBAB red with the silver ribbon"),
         ("red-navy", "3 · Red + navy", "Red letter, deep navy ribbon"),
         ("navy-gold", "4 · Navy + gold", "Royal navy with a gold ribbon"),
         ("emerald-gold", "5 · Green + gold", "Brand green with gold"),
         ("blue-sky", "6 · Blue + sky", "Clean travel blue, light ribbon"),
         ("teal-coral", "7 · Teal + coral", "Your teal with a warm coral ribbon"),
         ("purple-rose", "8 · Purple + rose gold", "Purple with a rose gold ribbon"),
         ("orange-navy", "9 · Orange + navy", "Sunset orange with navy"),
         ("charcoal-red", "10 · Charcoal + red", "Dark letter with a red ribbon"),
         ("mono-navy", "11 · Mono navy", "One colour in two shades"),
         ("mono-white", "12 · Mono white", "For dark areas: footer and welcome screen")]
    cards = ""
    for tid, nm, note in T:
        src = f"/assets/brand/preview-mine/{tid}.png"
        im = lambda c: f'<img class="{c}" src="{src}" alt="" loading="lazy">'
        light_only = tid != "mono-white"
        dark_only = tid == "mono-white"
        big_w = f'<div class="b w">{im("lg")}</div>' if not dark_only else '<div class="b w"><small>White version is for dark backgrounds only</small></div>'
        big_k = f'<div class="b k">{im("lg")}</div>'
        hdr = f'<div class="b m"><span class="pill">{im("hd")}<span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></span>{im("sm")}<span class="apt">{im("xs")}</span></div>' if not dark_only else f'<div class="b k m2"><span class="pill dk">{im("hd")}<span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></span>{im("sm")}</div>'
        cards += f'<article class="mn"><h3>{nm}</h3><p>{note}</p>{big_w}{big_k}{hdr}</article>'
    css = """.mng{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:14px}.mn{display:grid;gap:8px;padding:12px;border-radius:20px;background:rgba(255,255,255,.72);border:1px solid #fff;box-shadow:0 18px 36px -28px rgba(15,23,42,.45)}
.mn h3{font:800 15px Archivo,sans-serif;margin:0}.mn p{margin:0;font-size:13px;opacity:.75}.mn .b{border-radius:14px;display:flex;align-items:center;justify-content:center;gap:16px;min-height:150px;border:1px solid rgba(11,18,32,.08)}
.mn .w{background:#fff}.mn .k{background:#231f20}.mn .m{background:radial-gradient(60% 50% at 8% 8%,#e4f6f5,transparent 62%),#f6fbfb;min-height:84px;gap:10px;padding:8px}.mn .m2{min-height:84px;padding:8px}
.mn .lg{width:170px;height:auto;display:block}.mn .hd{height:38px;width:auto;display:block}.mn .sm{height:44px;width:auto;display:block}.mn .xs{height:22px;width:auto;display:block}
.mn .apt{display:grid;place-items:center;width:34px;height:34px;border-radius:9px;background:#fff;border:1px solid rgba(11,18,32,.1)}.mn .apt .xs{height:20px}
.mn .pill{display:inline-flex;align-items:center;gap:8px;padding:6px 12px 6px 8px;border-radius:999px;background:rgba(255,255,255,.85);border:1px solid rgba(11,18,32,.1)}.mn .pill.dk{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.2);color:#fff}
.mn .pill b{display:block;font:800 14px Archivo,sans-serif;line-height:1.05}.mn .pill small{display:block;font:700 8.5px Archivo,sans-serif;letter-spacing:.14em;opacity:.7}.mn .b>small{font-size:12px;color:#fff;opacity:.7;text-align:center;padding:10px}.mn .w>small{color:#333}.mn .pill.dk small{color:#fff}"""
    content = f"""<section class="sec"><div class="head"><div><h2>Your AL mark in 12 colour sets</h2></div><p class="lead">The shape is exactly your design, only the colours change. Each card shows it large on white and on dark, then in the header pill, at 44 px and as a 22 px app tile. Nothing here is live.</p></div><div class="mng">{cards}</div></section>"""
    ph = pagehead("Preview", "AL mark colour sets", "Your own AL design in 12 colour sets. Tell me the number you like.")
    body = shell("/preview-al-mine", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-al-mine", "AL mark colour sets | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-al-mine"]
    PAGES["/preview-al-mine"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

MINETEXT_PREVIEWS = True   # /preview-al-text: colour presets for the "AL ARBAB / TRAVEL & TOURS" wording next to the mark (noindex, not in the sitemap, not in the zip)

def minetext_previews():
    if not MINETEXT_PREVIEWS:
        return
    g = lambda c: f"linear-gradient({c},{c})"
    gr = lambda a, c, d=100: f"linear-gradient({d}deg,{a},{c})"
    # name, note, light bg (AL, ARBAB, small), dark bg (AL, ARBAB, small)
    P = [("1 · Ink + grey", "What it is now: dark ink, grey line", (g("#0b1220"), g("#0b1220"), "#5b6472"), (g("#fff"), g("#fff"), "#b8c0cc")),
         ("2 · Red AL, navy ARBAB", "Two tones: AL in the mark's red", (g("#e30613"), g("#073b40"), "#5b6472"), (g("#ff3b4a"), g("#fff"), "#b8c0cc")),
         ("3 · Navy + red line", "Deep navy name, red small line", (g("#073b40"), g("#073b40"), "#e30613"), (g("#fff"), g("#fff"), "#ff6b73")),
         ("4 · Navy + gold", "Navy name, gold small line", (g("#073b40"), g("#073b40"), "#b8820a"), (g("#ffd86b"), g("#fff"), "#ffd86b")),
         ("5 · Red gradient", "Name in a red gradient, charcoal line", (gr("#ff2a3a", "#a30010"), gr("#ff2a3a", "#a30010"), "#3a4250"), (gr("#ff5a66", "#e30613"), g("#fff"), "#b8c0cc")),
         ("6 · Navy to blue gradient", "Smooth navy to blue, silver line", (gr("#073b40", "#2f6fe0"), gr("#073b40", "#2f6fe0"), "#6b7686"), (gr("#9fdcd9", "#fff"), gr("#9fdcd9", "#fff"), "#b8c0cc")),
         ("7 · Charcoal + red AL", "Charcoal name, only AL in red", (g("#e30613"), g("#1f2329"), "#6b7280"), (g("#ff3b4a"), g("#e8edf5"), "#9aa4b2")),
         ("8 · Green + gold", "Brand green, gold small line", (g("#0e7c86"), g("#0e7c86"), "#b8820a"), (g("#5bd68a"), g("#fff"), "#ffd86b")),
         ("9 · Gold gradient", "Gold on dark, navy on light", (gr("#9a6a0a", "#d9a21a"), g("#073b40"), "#5b6472"), (gr("#ffd86b", "#f0b429"), gr("#ffd86b", "#f0b429"), "#e9d9a8")),
         ("10 · Royal blue + sky", "Blue name, sky blue line", (g("#1456d9"), g("#1456d9"), "#4f93f0"), (g("#7cc0ff"), g("#fff"), "#9fdcd9")),
         ("11 · Black + silver", "Black name, silver line. Quiet and formal", (g("#000"), g("#000"), "#7a828e"), (g("#fff"), g("#fff"), "#c4cad4")),
         ("12 · Purple + rose", "Purple name, rose gold line", (g("#5b2bb5"), g("#5b2bb5"), "#b9604f"), (g("#c9a7ff"), g("#fff"), "#f0b8a6"))]
    mk = f"/assets/brand/al-mark.png"
    def lock(v):
        a, r, s = v
        return (f'<span class="lk" style="--a:{a};--r:{r};--s:{s}"><img src="{mk}" alt="" width="60" height="48">'
                f'<span><b><i>AL</i> <em>ARBAB</em></b><small>TRAVEL &amp; TOURS</small></span></span>')
    cards = ""
    for nm, note, lt, dk in P:
        cards += (f'<article class="tx"><h3>{nm}</h3><p>{note}</p><div class="b w">{lock(lt)}</div>'
                  f'<div class="b k">{lock(dk)}</div><div class="b h">{lock(dk)}</div></article>')
    css = """.txg{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:14px}.tx{display:grid;gap:8px;padding:12px;border-radius:20px;background:rgba(255,255,255,.72);border:1px solid #fff;box-shadow:0 18px 36px -28px rgba(15,23,42,.45)}
.tx h3{font:800 15px Archivo,sans-serif;margin:0}.tx p{margin:0;font-size:13px;opacity:.75}.tx .b{border-radius:14px;display:flex;align-items:center;padding:12px 14px;min-height:78px;border:1px solid rgba(11,18,32,.08)}
.tx .w{background:#fff}.tx .k{background:#0b1213}.tx .h{background:linear-gradient(135deg,#27496d,#0a1620 70%)}
.tx .lk{display:inline-flex;align-items:center;gap:10px}.tx .lk img{height:48px;width:auto;display:block}.tx .lk span{display:grid;gap:3px;text-align:left}
.tx .lk b{font:900 21px/1 Archivo,sans-serif;letter-spacing:.01em;display:block;white-space:nowrap}
.tx .lk b i,.tx .lk b em{font-style:normal;background:var(--a);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}
.tx .lk b em{background:var(--r);-webkit-background-clip:text;background-clip:text}
.tx .lk small{font:700 9.5px/1 Archivo,sans-serif;letter-spacing:.2em;color:var(--s)}"""
    content = f"""<section class="sec"><div class="head"><div><h2>Colours for "AL ARBAB, Travel &amp; Tours"</h2></div><p class="lead">The logo mark stays exactly as it is. Only the wording beside it changes colour. Each card shows it on white (inner pages), on black (footer) and on a dark photo-style background (home header). Nothing here is live.</p></div><div class="txg">{cards}</div></section>"""
    ph = pagehead("Preview", "Logo text colours", "Twelve colour presets for the AL ARBAB wording next to the mark. Tell me the number.")
    body = shell("/preview-al-text", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-al-text", "Logo text colours | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-al-text"]
    PAGES["/preview-al-text"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

GALAXY_PREVIEWS = True   # /preview-splash-galaxy: welcome screen with a galaxy / star-flight background (noindex, not in the sitemap, not in the zip)

def galaxy_previews():
    if not GALAXY_PREVIEWS:
        return
    js = open(os.path.join(ROOT, "assets", "galaxy-preview.js"), encoding="utf-8").read()
    stage = lambda cls, st="": (f'<div class="gx {cls}"{f" data-set={chr(34)}{st}{chr(34)}" if st else ""}><canvas aria-hidden="true"></canvas><i class="flash"></i><div class="gl"><img src="{AL_MARK}" alt="" width="321" height="260">'
                         f'<span class="gt"><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></div><i class="gbar"></i></div>')
    css = """.gx{position:relative;overflow:hidden;border-radius:22px;background:#04070f;display:grid;place-items:center;border:1px solid rgba(11,18,32,.15)}
.gx.wide{aspect-ratio:16/9;width:100%}.gx.phone{aspect-ratio:9/17;width:min(250px,100%);border-radius:30px}
.gx canvas{position:absolute;inset:0;width:100%;height:100%;display:block}
.gx .flash{position:absolute;inset:0;background:radial-gradient(circle at 50% 48%,rgba(160,200,255,.9),rgba(60,110,255,.35) 30%,transparent 62%);opacity:0;pointer-events:none}
.gx .gl{position:relative;display:grid;justify-items:center;gap:12px;opacity:0;transform:scale(.55);filter:blur(10px)}
.gx .gl img{width:clamp(110px,24%,200px);height:auto;display:block;filter:drop-shadow(0 0 22px rgba(90,150,255,.55))}
.gx.phone .gl img{width:46%}
.gx .gt{display:grid;gap:7px;text-align:center}.gx .gt b{font:900 clamp(22px,4vw,40px)/1 Archivo,sans-serif;letter-spacing:.03em;background:linear-gradient(100deg,#9fdcd9,#fff);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}
.gx.phone .gt b{font-size:22px}.gx .gt small{font:700 11px/1 Archivo,sans-serif;letter-spacing:.32em;color:#c4cad4}
.gx .gbar{position:absolute;left:50%;bottom:9%;width:min(200px,46%);height:3px;margin-left:calc(min(200px,46%) / -2);border-radius:3px;background:rgba(255,255,255,.12);overflow:hidden}
.gx .gbar::before{content:"";display:block;height:100%;background:linear-gradient(90deg,#ff3b30,#e30613);transform:scaleX(0);transform-origin:left}
.gx.go .gl{animation:gpop .9s cubic-bezier(.2,1.2,.3,1) 1.05s forwards}
.gx.go .flash{animation:gflash .8s ease-out 1s forwards}
.gx.go .gbar::before{animation:gfill 2.3s cubic-bezier(.5,0,.3,1) .1s forwards}
.gx.still .gl{animation:none;opacity:1;transform:none;filter:none}.gx.still .gbar::before{animation:none;transform:none}
@keyframes gpop{to{opacity:1;transform:none;filter:blur(0)}}
@keyframes gflash{0%{opacity:0}30%{opacity:.75}100%{opacity:0}}
@keyframes gfill{to{transform:scaleX(1)}}
.gxw{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:start}@media(max-width:800px){.gxw{grid-template-columns:1fr}}
.gxb{margin-top:14px;display:flex;gap:10px;flex-wrap:wrap}.gxb button{min-height:44px;padding:0 20px;border-radius:999px;border:0;background:#0b1213;color:#fff;font:700 14px Inter,sans-serif;cursor:pointer}"""
    content = f"""<section class="sec"><div class="head"><div><h2>Galaxy welcome screen</h2></div><p class="lead">A blue and purple nebula, a short star flight, then the logo pops in with a flash and the bar fills. Plain canvas, a few KB, no libraries. Shown as a desktop screen and a phone screen. Press Replay to see it again. Nothing here is live.</p></div>
<div class="gxw">{stage("wide")}{stage("phone")}</div>
<div class="gxb"><button type="button" data-replay>Replay</button></div></section>"""
    ph = pagehead("Preview", "Galaxy welcome screen", "Star-flight welcome screen with the AL ARBAB logo. Tell me if you want it applied.")
    body = shell("/preview-splash-galaxy", [("Home", "/"), ("Splash preview", None)], ph, content)
    page("/preview-splash-galaxy", "Galaxy welcome screen | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-splash-galaxy"]
    h = h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-splash-galaxy"] = (h, pr, True)

    def lab(t): return f'<h3 class="gxh">{t}</h3>'
    content2 = f"""<section class="sec"><div class="head"><div><h2>Galaxy welcome screen with country flags</h2></div><p class="lead">Instead of plain dots, small flag cards with the country name fly out of the centre, then the logo pops in. Three versions: Asian countries, Schengen countries, and both mixed. Shown on a desktop screen, with the mixed one also on a phone. Press Replay to see them again. The flags are decoration only. Nothing here is live.</p></div>
{lab("A · Asian countries")}{stage("wide", "asia")}{lab("B · Schengen countries")}{stage("wide", "schengen")}{lab("C · Asian + Schengen mixed")}<div class="gxw">{stage("wide", "mix")}{stage("phone", "mix")}</div>
<div class="gxb"><button type="button" data-replay>Replay all</button></div></section>"""
    ph2 = pagehead("Preview", "Galaxy screen with flags", "Country flags flying out of the galaxy, Asian, Schengen and mixed. Tell me which one.")
    body2 = shell("/preview-splash-flags", [("Home", "/"), ("Splash preview", None)], ph2, content2)
    page("/preview-splash-flags", "Galaxy screen with flags | AL ARBAB", "Preview only.", body2, noindex=True, priority="0.1")
    h2, pr2, noi2 = PAGES["/preview-splash-flags"]
    h2 = h2.replace("</head>", f"<style>{' '.join(css.split())}.gxh{{font:800 16px Archivo,sans-serif;margin:22px 0 10px}}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-splash-flags"] = (h2, pr2, True)

    # circle flags, three styles
    stg = lambda cls, sty: stage(cls, "mix").replace('data-set="mix"', f'data-set="mix" data-style="{sty}"')
    row = lambda t, n, sty: f'<h3 class="gxh">{t}</h3><p class="gxn">{n}</p><div class="gxw">{stg("wide", sty)}{stg("phone", sty)}</div>'
    content3 = f"""<section class="sec"><div class="head"><div><h2>Circle flags, three designs</h2></div><p class="lead">Smaller, round flags flying out of the galaxy before the logo pops in. Pick the design, and use the buttons to try Asian, Schengen or both. Each is shown on desktop and phone. Nothing here is live.</p></div>
<div class="gxb gxs"><button type="button" data-setbtn="asia">Asian</button><button type="button" data-setbtn="schengen">Schengen</button><button type="button" data-setbtn="mix" class="on">Mixed</button><button type="button" data-replay>Replay</button></div>
{row("1 · Glow rings", "Round flag with a white ring and a soft blue glow, name underneath.", "ring")}
{row("2 · Glass pills", "A small glass capsule: round flag on the left, country name inside.", "pill")}
{row("3 · Comets", "Round flag with a light trail behind it, like a comet flying toward you.", "comet")}</section>"""
    ph3 = pagehead("Preview", "Galaxy circle flags", "Three circle-flag designs for the galaxy welcome screen. Tell me the number.")
    body3 = shell("/preview-splash-circles", [("Home", "/"), ("Splash preview", None)], ph3, content3)
    page("/preview-splash-circles", "Galaxy circle flags | AL ARBAB", "Preview only.", body3, noindex=True, priority="0.1")
    h3, pr3, noi3 = PAGES["/preview-splash-circles"]
    h3 = h3.replace("</head>", f"<style>{' '.join(css.split())}.gxh{{font:800 16px Archivo,sans-serif;margin:24px 0 4px}}.gxn{{margin:0 0 10px;font-size:13px;opacity:.75}}.gxs button.on{{background:#e30613}}.gxs{{margin:0 0 6px}}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-splash-circles"] = (h3, pr3, True)

NAVBAR_PREVIEWS = True   # /preview-navbar: six new navigation bar concepts (noindex, not in the sitemap, not in the zip)

def navbar_previews():
    if not NAVBAR_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "nav-previews.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "nav-previews.js"), encoding="utf-8").read()
    P = {"home": "M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6", "visa": "M7 3h8l4 4v14H7zM15 3v4h4M10 14l2 2 3-4",
         "globe": "M3 12a9 9 0 1 0 18 0a9 9 0 1 0-18 0M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18",
         "moon": "M20 14A8 8 0 1 1 10 4a6.5 6.5 0 0 0 10 10z", "bag": "M4 8h16v12H4zM9 8V6a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M4 13h16",
         "check": "M4 12a8 8 0 1 0 16 0a8 8 0 1 0-16 0M8.5 12.5l2.5 2.5 4.5-5", "phone": "M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"}
    PLANE = '<svg viewBox="-24 -20 48 40" aria-hidden="true"><path d="M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z"/></svg>'
    ic = lambda k: f'<svg class="nb-i" viewBox="0 0 24 24" aria-hidden="true"><path d="{P[k]}"/></svg>'
    planeic = '<svg class="nb-i nb-f" viewBox="-24 -20 48 40" aria-hidden="true"><path d="M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z"/></svg>'
    wa = '<svg class="nb-i nb-f" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm5.2 14c-.2.6-1.2 1.2-1.7 1.2-.4.1-1 .1-1.6-.1-3.2-1.3-5.2-4.5-5.4-4.7-.1-.2-1.3-1.7-1.3-3.2 0-1.5.8-2.2 1-2.5.3-.3.6-.4.8-.4h.6c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.4.6c-.1.2-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.3.1.5.1.6-.1l.9-1.1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.8-.1 1.4z"/></svg>'
    mk = f"{AL_MARK_S}"
    logo = f'<a class="nb-lgo" href="#"><img src="{mk}" alt="" width="48" height="38"><span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></a>'
    names = ["Home", "Visas", "Destinations", "Flights", "Umrah", "Packages"]
    stg = lambda inner, lt=False: f'<div class="nb-stg{" lt" if lt else ""}">{inner}<div class="nb-fake"></div><div class="nb-tg"><button type="button">{"Dark" if lt else "Light"}</button></div></div>'

    # A flight route
    A = stg('<nav class="nb-fr" aria-label="Preview">' + logo + '<div class="nb-route">' + "".join(f'<a class="nb-st{" on" if i == 0 else ""}" href="#">{n}</a>' for i, n in enumerate(names)) +
            '<i class="nb-line"></i><i class="nb-trail"></i><i class="nb-pl">' + PLANE + '</i></div><a class="nb-wa" href="#">' + wa + 'WhatsApp</a></nav>')
    # B boarding pass
    codes = ["A1", "B2", "C3", "D4", "E5", "F6"]
    B = stg('<nav class="nb-bp" aria-label="Preview"><div class="nb-a">' + logo + '</div><div class="nb-b">' + "".join(f'<a class="{"on" if i == 0 else ""}" href="#"><em>GATE {codes[i]}</em>{n}</a>' for i, n in enumerate(names)) +
            '</div><div class="nb-c"><i class="nb-bar"></i><a class="nb-wa" href="#">' + wa + 'Book now</a></div></nav>', True)
    # C floating dock
    keys = ["home", "visa", "globe", "plane", "moon", "bag"]
    D = '<div class="nb-dk"><div class="nb-bar">' + "".join(f'<a class="nb-it{" on" if i == 0 else ""}" href="#"><span>{names[i]}</span>{planeic if k == "plane" else ic(k)}</a>' for i, k in enumerate(keys)) + \
        f'<i class="nb-sep"></i><a class="nb-it" href="#"><span>Free check</span>{ic("check")}</a><a class="nb-it nb-wa2" href="#"><span>WhatsApp</span>{wa}</a></div></div>'
    C = stg(D)
    # D editorial
    links = "".join(f'<a class="nb-l{" on" if i == 0 else ""}" href="#"><sup>0{i + 1}</sup><span class="nb-r"><span>{n}</span><span>{n}</span></span></a>' for i, n in enumerate(names))
    E = stg('<nav class="nb-ed" aria-label="Preview">' + logo + f'<div class="nb-links">{links}</div><a class="nb-cta" href="#">Talk to us<i>&rarr;</i></a></nav>', True)
    # E islands
    nv = "".join(f'<a class="{"on" if i == 0 else ""}" href="#">{n}</a>' for i, n in enumerate(names))
    F = stg(f'<nav class="nb-is" aria-label="Preview"><div class="nb-isl nb-lg">{logo}</div><div class="nb-isl nb-nv"><i class="nb-hl"></i>{nv}</div><div class="nb-isl nb-cta"><a href="#">{wa}WhatsApp</a></div></nav>')
    # F side rail
    rail = f'<span class="nb-lgm"><img src="{mk}" alt="" width="48" height="38"></span>' + "".join(
        f'<a class="{"on" if i == 0 else ""}" href="#">{planeic if k == "plane" else ic(k)}<b>{names[i]}</b></a>' for i, k in enumerate(keys)) + f'<a class="nb-wa3" href="#">{wa}<b>WhatsApp</b></a>'
    G = stg(f'<div class="nb-rl"><nav class="nb-rail" aria-label="Preview">{rail}</nav><div class="nb-main"><h4>Visa Consultant &amp; Travel Agency in Islamabad</h4><p>The rail stays slim and out of the way. Hover an icon and it opens into a label.</p></div></div>')
    items = [
        ("A · Flight route", "The menu is a flight path. Each page is a stop, and a small plane flies along the dotted route to the page you point at. Travel-only idea, nobody else has it.", A),
        ("B · Boarding pass", "The bar is a boarding pass with side notches, dashed tear lines and gate numbers. Light card, so it works on any hero photo.", B),
        ("C · Floating dock", "Icon dock that floats in the middle of the page. Icons grow toward the pointer and show a name tag.", C),
        ("D · Editorial numbers", "Magazine style. Plain text, numbered, with rolling text on hover. No boxes or buttons at all.", E),
        ("E · Islands", "Three separate dark islands: logo, menu, WhatsApp. A red highlight glides under the item you point at.", F),
        ("F · Side rail", "A slim vertical rail on the left that opens into labels on hover. On phones it becomes a bottom tab bar.", G)]
    cards = "".join(f'<article class="nbx"><h3>{t}</h3><p>{d}</p>{h}</article>' for t, d, h in items)
    content = f"""<section class="sec"><div class="head"><div><h2>Six new navigation bars</h2></div><p class="lead">Move the pointer over each bar to try it. Use the Light / Dark button on a card to see it on a light or a dark background. These are on-screen concepts, so the links do not open anything. Nothing here is live.</p></div>{cards}</section>"""
    ph = pagehead("Preview", "New navigation bar designs", "Six different ideas for the top bar. Tell me the letter and I will build it for the whole site, with a phone version.")
    body = shell("/preview-navbar", [("Home", "/"), ("Navigation preview", None)], ph, content)
    page("/preview-navbar", "Navigation bar designs | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-navbar"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-navbar"] = (h, pr, True)

NAVD_PREVIEWS = True   # /preview-navbar-d: three crystal-glass tube / funnel treatments on top of navigation bar D (noindex, not in the sitemap, not in the zip)

def navd_previews():
    if not NAVD_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "nav-d.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "nav-d.js"), encoding="utf-8").read()
    names = ["Home", "Visas", "Destinations", "Flights", "Umrah", "Packages"]
    logo = f'<a class="nd-lg" href="#"><img src="{AL_MARK_S}" alt="" width="48" height="38"><span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></a>'
    cta = '<a class="nd-cta" href="#">Talk to us<i>&rarr;</i></a>'
    item = lambda i, n, on="": f'<a class="nd-l{on}" href="#" data-n="{n}"><sup>0{i + 1}</sup><span>{n}</span></a>'
    items = lambda: "".join(item(i, n) for i, n in enumerate(names))
    stg = lambda inner: f'<div class="nd-s">{inner}<div class="nd-fake"></div><div class="nd-tg"><button type="button">Light</button></div></div>'
    one = stg(f'<div class="nd-row">{logo}<div class="nd-links"><div class="nd-tube"><div class="nd-lay nd-base">{items()}</div><i class="nd-lens"></i><div class="nd-lay nd-top" aria-hidden="true">{items()}</div></div></div>{cta}</div>')
    two = stg(f'<div class="nd-row">{logo}<div class="nd-hold"><button class="nd-ar nd-prev" type="button" aria-label="Previous">&lsaquo;</button><div class="nd-drum"><div class="nd-cyl">{items()}</div></div><i class="nd-win"></i><button class="nd-ar nd-next" type="button" aria-label="Next">&rsaquo;</button></div>{cta}</div>')
    three = stg(f'<div class="nd-fun"><div class="nd-funnel"><i class="nd-gl"></i><i class="nd-rim"></i><span class="nd-tx">Home</span><i class="nd-bm"></i></div><div class="nd-row">{logo}<div class="nd-links"><div class="nd-lay">{items()}</div></div>{cta}</div><i class="nd-ln"></i></div>')
    cards = [("1 · Glass lens tube", "A clear crystal tube slides over the page you point at. Through the glass the number and name turn glowing red, with a red light under it. Same editorial bar as D.", one),
             ("2 · Rotating drum", "Pages sit on a turning cylinder, like a time picker. Use the arrows, the mouse wheel or click a name. The one inside the crystal window is red.", two),
             ("3 · Crystal funnel", "A faceted glass funnel sits above the bar and follows your page. The page name drops into it in red and a red light falls onto the menu.", three)]
    body_cards = "".join(f'<article class="nd-x"><h3>{t}</h3><p>{d}</p>{h}</article>' for t, d, h in cards)
    content = f"""<section class="sec"><div class="head"><div><h2>Bar D with a crystal glass tube</h2></div><p class="lead">Three ways to put a glass tube or funnel on the numbered bar. Point at the names, click one, and try the Light / Dark button. Links do not open here. Nothing is live.</p></div>{body_cards}</section>"""
    ph = pagehead("Preview", "Bar D, crystal glass tube", "Lens, drum and funnel on top of the numbered bar. Tell me the number.")
    body = shell("/preview-navbar-d", [("Home", "/"), ("Navigation preview", None)], ph, content)
    page("/preview-navbar-d", "Bar D crystal tube | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-navbar-d"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-navbar-d"] = (h, pr, True)

NAVPRO_PREVIEWS = True   # /preview-navbar-pro: four pro-level treatments on bar D (noindex, not in the sitemap, not in the zip)

def navpro_previews():
    if not NAVPRO_PREVIEWS:
        return
    from urllib.parse import quote
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "nav-pro.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "nav-pro.js"), encoding="utf-8").read()
    names = ["Home", "Visas", "Destinations", "Flights", "Umrah", "Packages"]
    dmap = ("<svg xmlns='http://www.w3.org/2000/svg' width='200' height='60'><defs>"
            "<linearGradient id='r' x1='0' x2='1'><stop offset='0' stop-color='#ff0000'/><stop offset='.22' stop-color='#800000'/><stop offset='.78' stop-color='#800000'/><stop offset='1' stop-color='#000000'/></linearGradient>"
            "<linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#00ff00'/><stop offset='.3' stop-color='#008000'/><stop offset='.7' stop-color='#008000'/><stop offset='1' stop-color='#000000'/></linearGradient></defs>"
            "<rect width='200' height='60' fill='#000'/><rect width='200' height='60' fill='url(#r)'/>"
            "<rect width='200' height='60' fill='url(#g)' style='mix-blend-mode:screen'/><rect width='200' height='60' fill='#000080' style='mix-blend-mode:screen'/></svg>")
    defs = (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
            f'<filter id="np-liq" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feImage href="data:image/svg+xml;utf8,{quote(dmap)}" x="0" y="0" width="100%" height="100%" preserveAspectRatio="none" result="m"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="m" scale="30" xChannelSelector="R" yChannelSelector="G"/></filter>'
            f'<filter id="np-goo" x="-10%" y="-60%" width="120%" height="220%"><feGaussianBlur in="SourceGraphic" stdDeviation="6" result="b"/>'
            f'<feColorMatrix in="b" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -8"/></filter></defs></svg>')
    logo = f'<a class="np-lg" href="#"><img src="{AL_MARK_S}" alt="" width="48" height="38"><span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></a>'
    cta = '<a class="np-cta" href="#"><span>Talk to us</span><i>&rarr;</i></a>'
    item = lambda i, n, on="": f'<a class="np-l{on}" href="#"><sup>0{i + 1}</sup><span>{n}</span></a>'
    items = lambda: "".join(item(i, n) for i, n in enumerate(names))
    stg = lambda inner, cls="": f'<div class="np-s {cls}">{inner}<div class="np-fake"></div><div class="np-tg"><button type="button">Light</button></div></div>'
    A = stg(f'<div class="np-row">{logo}<div class="np-links"><div class="np-trk"><div class="np-lay np-base">{items()}</div><div class="np-lay np-top" aria-hidden="true">{items()}</div><i class="np-lens"></i></div></div>{cta}</div>', "np-A")
    B = stg(f'<div class="np-row">{logo}<div class="np-links np-th"><div class="np-tube"><div class="np-glass"><div class="np-liq"><i class="np-fill"></i><i class="np-b2"></i><i class="np-b1"></i><i class="np-head"></i></div></div><div class="np-lay">{items()}</div></div></div>{cta}</div>', "np-B")
    doc = "<div class=\"np-doc\">" + "<i></i>" * 14 + "</div>"
    Cbar = f'<div class="np-bar"><span class="np-lgt">{logo}</span><div class="np-links"><div class="np-lay">{items()}</div></div><div class="np-cur"><i class="np-ring"></i><span class="np-curname">01  Home</span></div>{cta}</div>'
    C = f'<div class="np-s np-C" style="padding-bottom:70px"><div class="np-sc">{Cbar}{doc}</div><p class="np-hint">Scroll inside the box. Hover the capsule to open it again.</p><div class="np-tg"><button type="button">Light</button></div></div>'
    D = stg(f'<div class="np-row">{logo}<div class="np-links"><div class="np-trk"><div class="np-lay np-base">{items()}</div><div class="np-lay np-top" aria-hidden="true">{items()}</div><i class="np-loupe"></i></div></div>{cta}</div>', "np-D")
    cards = [("A · Liquid glass lens", "A real glass lens with spring physics. It stretches as it flies to the page, bends the text behind it at the edges (true refraction in Chrome and Edge, a clean blur elsewhere), and the page inside glows red.", A),
             ("B · Mercury in a crystal tube", "The whole menu sits inside a long glass tube. Red liquid rises to your page, with a drop that stretches away from it like mercury. It also tells you how far through the site you are.", B),
             ("C · Scroll morph capsule", "Scroll the grey box. The full bar condenses into a small crystal capsule with a progress ring and the name of where you are. Hover it and it opens up again. Keeps the page clean on a phone.", C),
             ("D · Loupe", "A glass loupe follows your pointer with a soft delay and magnifies the page names under it in red. When you leave, it rests on the page you are on.", D)]
    body_cards = "".join(f'<article class="np-x"><h3>{t}</h3><p>{d}</p>{h}</article>' for t, d, h in cards)
    content = f"""{defs}<section class="sec"><div class="head"><div><h2>Pro-level crystal bars</h2></div><p class="lead">Four more ideas on the numbered bar D. They use spring physics, SVG light refraction and scroll-aware morphing, with plain CSS and a small script. Try each with the pointer, and use Light / Dark on a card. Nothing is live.</p></div>{body_cards}</section>"""
    ph = pagehead("Preview", "Pro crystal navigation bars", "Four pro-level versions of bar D. Tell me the letter.")
    body = shell("/preview-navbar-pro", [("Home", "/"), ("Navigation preview", None)], ph, content)
    page("/preview-navbar-pro", "Pro crystal bars | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-navbar-pro"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-navbar-pro"] = (h, pr, True)

NAVX_PREVIEWS = True   # /preview-navbar-x: five navigation ideas with no glass at all (noindex, not in the sitemap, not in the zip)

def navx_previews():
    if not NAVX_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "nav-x.css"), encoding="utf-8").read(), flags=re.S).split())
    js = open(os.path.join(ROOT, "assets", "nav-x.js"), encoding="utf-8").read()
    names = ["Home", "Visas", "Destinations", "Flights", "Umrah", "Packages"]
    logo = lambda: f'<a class="nx-lg" href="#"><img src="{AL_MARK_S}" alt="" width="50" height="40"><span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></a>'
    wa = '<a class="nx-wa" href="#">WhatsApp</a>'
    cells = ""
    for i, n in enumerate(names):
        w = n.upper()[:12]
        ch = "".join(f"<b>{c}</b>" for c in w)
        cells += f'<a class="nx-fl{" on" if i == 0 else ""}" href="#"><span class="nx-gt">GATE {i + 1:02d}<em>{"BOARDING" if i == 0 else "ON TIME"}</em></span><span class="nx-ch">{ch}</span></a>'
    A = f'<div class="nx-s nx-A"><div class="nx-top">{logo()}<div class="nx-bd">{cells}</div>{wa}</div><div class="nx-sub"><span>Departures</span><span><i>&#9679;</i> Islamabad (ISB)</span><span>Click a gate</span></div></div>'
    tags = "".join(f'<a class="nx-tag{" on" if i == 0 else ""}" href="#" style="--i:{i}"><i class="str"></i><span class="nx-bd2"><sup>0{i + 1}</sup><b>{n}</b><i class="bc"></i></span></a>' for i, n in enumerate(names))
    B = f'<div class="nx-s nx-B"><div class="nx-rail"><i class="nx-bar"></i>{logo()}<div class="nx-tags">{tags}</div>{wa}</div></div>'
    HQ_ = ["1568508432206-7541b535f84c", "1525625293386-3f8f99389edd", "1592364395653-83e648b20cc2", "1718179634911-8551f8b0cccf", "1521019795854-14e15f600980", "1576506730652-f0e4ad14828f"]
    caps = ["Start here", "Visa guides", "Choose a country", "Air tickets", "Umrah packages", "Holiday packages"]
    lst = "".join(f'<a href="#" style="--i:{i}" data-c="{caps[i]}"><sup>0{i + 1}</sup>{n}</a>' for i, n in enumerate(names))
    pics = "".join(f'<img src="/assets/hero/{p}-1000.webp" alt="" loading="lazy" width="500" height="600">' for p in HQ_)
    C = (f'<div class="nx-s nx-C"><div class="nx-hd">{logo()}<div style="display:flex;gap:10px;align-items:center">{wa}<button class="nx-mb" type="button">MENU<i></i></button></div></div>'
         f'<h4 class="nx-hero">Visas, flights &amp; Umrah from Islamabad</h4><div class="nx-ov"><nav class="nx-ls">{lst}</nav><div class="nx-pic">{pics}<span>Start here</span></div></div></div>')
    cols = ["#e30613", "#073b40", "#f2792b", "#0e7c86", "#7a3fd1", "#0b0e14"]
    blocks = "".join(f'<a class="nx-cl{" on" if i == 0 else ""}" href="#" style="--c:{cols[i]}"><em>0{i + 1}</em><b>{n}</b><i>&#8599;</i></a>' for i, n in enumerate(names))
    D = f'<div class="nx-s nx-D"><div class="nx-gr"><div class="nx-c0">{logo()}</div>{blocks}<a class="nx-cw" href="#">WhatsApp us</a></div><div class="nx-strip"><span>Blue Area, Islamabad</span><span>Mon&ndash;Sat 9 AM&ndash;8 PM</span></div></div>'
    P = {"Home": "M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6", "Visas": "M7 3h8l4 4v14H7zM15 3v4h4M10 14l2 2 3-4", "Destinations": "M3 12a9 9 0 1 0 18 0a9 9 0 1 0-18 0M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18",
         "Umrah": "M20 14A8 8 0 1 1 10 4a6.5 6.5 0 0 0 10 10z", "Packages": "M4 8h16v12H4zM9 8V6a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M4 13h16"}
    plane = '<svg class="f" viewBox="-24 -20 48 40" aria-hidden="true"><path d="M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z"/></svg>'
    dcol = ["#e30613", "#f2792b", "#0e7c86", "#7a3fd1", "#14181f", "#0e7fa8"]
    dots = ""
    for i, n in enumerate(names):
        icon = f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{P.get(n, "M22 2L11 13M22 2l-7 20-4-9-9-4z")}"/></svg>'
        dots += f'<a class="nx-dot{" on" if i == 0 else ""}" href="#" style="background:{dcol[i]}">{icon}<span>{n}</span></a>'
    E = f'<div class="nx-s nx-E">{logo()}{wa}<button class="nx-hub" type="button" aria-label="Menu"><img src="{AL_MARK_S}" alt="" width="50" height="40"></button><div class="nx-fan">{dots}</div><p class="nx-note">Tap the round logo to fold and unfold the menu.</p></div>'
    cards = [("A · Departure board", "The menu is an airport departures board. Every page is a gate. Point at one and its letters flip like a real split-flap display. Click a gate and it changes to BOARDING.", A),
             ("B · Luggage tags", "Six colour tags hang from a rail on strings and sway slowly. Point at a tag and it swings. Click one and it is pulled down, so you can see where you are.", B),
             ("C · Full-screen type", "The bar is almost empty: logo, WhatsApp and one MENU button. Press MENU and a huge editorial type menu drops down. Each name fills in and shows its photo.", C),
             ("D · Swiss colour blocks", "Not a row of buttons but a grid, like a poster. Heavy black lines, big numbers. Each block floods with its own colour from the bottom when you point at it.", D),
             ("E · Fan menu", "One round logo in the centre. Tap it and the pages fan out underneath on an arc as coloured badges with icons. A thumb-friendly menu that works the same on a phone.", E)]
    body_cards = "".join(f'<article class="nx-x"><h3>{t}</h3><p>{d}</p>{h}</article>' for t, d, h in cards)
    content = f"""<section class="sec"><div class="head"><div><h2>Five navigation ideas, no glass</h2></div><p class="lead">No crystal, no frosted glass. These are solid, physical ideas: a flight board, luggage tags, a poster grid, a giant type menu and a fan. Point at them and click. Nothing is live.</p></div>{body_cards}</section>"""
    ph = pagehead("Preview", "Five different navigation ideas", "No glass. Departure board, luggage tags, full-screen type, Swiss colour blocks and a fan menu. Tell me the letter.")
    body = shell("/preview-navbar-x", [("Home", "/"), ("Navigation preview", None)], ph, content)
    page("/preview-navbar-x", "Five navigation ideas | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-navbar-x"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-navbar-x"] = (h, pr, True)

FLIGHT_PREVIEWS = True   # /preview-flight: six aeroplane route animations for the home hero (noindex, not in the sitemap, not in the zip)

def flight_previews():
    if not FLIGHT_PREVIEWS:
        return
    js = open(os.path.join(ROOT, "assets", "flight-previews.js"), encoding="utf-8").read()
    css = """.fl-g{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}@media(max-width:800px){.fl-g{grid-template-columns:1fr}}
.fl-c h3{font:900 17px Archivo,sans-serif;margin:0 0 3px}.fl-c p{margin:0 0 8px;font-size:13.5px;opacity:.8}
.fl-s{position:relative;aspect-ratio:16/9;border-radius:18px;overflow:hidden;background:#0b1a24 url(/assets/hero/1568508432206-7541b535f84c-1000.webp) center/cover;border:1px solid rgba(11,18,32,.15)}
.fl-s::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,12,24,.25),rgba(0,12,24,.45))}
.fl-s svg{position:absolute;inset:0;width:100%;height:100%}
.fl-b{margin:14px 0 0}.fl-b button{min-height:44px;padding:0 22px;border-radius:99px;border:0;background:#0b1213;color:#fff;font:700 14px Inter,sans-serif;cursor:pointer}"""
    items = [("contrail", "1 · Contrail", "A big white plane draws a soft glowing contrail that trails behind it and fades. Simple and clean, feels like real flight."),
             ("dots", "2 · Dotted comet", "The plane drops a line of white dots as it flies, like a route being laid down on a map. A pulse rings the destination."),
             ("ticket", "3 · Ticket route", "A thin route with an ISB tag and an HKT tag. A stop dot fills in as the plane passes. Looks like a flight-booking screen."),
             ("neon", "4 · Neon route", "A red-to-white glowing line is drawn as the plane flies. Ripples spread from Islamabad and sparkles light up along the way."),
             ("depth", "5 · Altitude and shadow", "The plane climbs: it gets bigger in the middle of the route while its shadow on the sea gets smaller and lighter. Gives real depth."),
             ("paper", "6 · Paper plane loop", "A friendly paper plane that does a loop-the-loop on its way. Playful, different from every other travel site.")]
    cards = "".join(f'<article class="fl-c"><h3>{t}</h3><p>{d}</p><div class="fl-s" data-m="{m}"><svg viewBox="0 0 800 450" preserveAspectRatio="xMidYMid slice" aria-hidden="true"></svg></div></article>' for m, t, d in items)
    content = f"""<section class="sec"><div class="head"><div><h2>Aeroplane route animations</h2></div><p class="lead">Six ways to animate the plane on the home hero, shown on the Thailand photo with the route from Islamabad (ISB) to Phuket (HKT). They repeat on their own. Press Replay to restart all. Nothing here is live.</p></div>
<div class="fl-g">{cards}</div><div class="fl-b"><button type="button" data-fl-replay>Replay all</button></div></section>"""
    ph = pagehead("Preview", "Aeroplane animation designs", "Six route and plane animations for the home hero. Tell me the number.")
    body = shell("/preview-flight", [("Home", "/"), ("Animation preview", None)], ph, content)
    page("/preview-flight", "Aeroplane animations | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-flight"]
    h = h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-flight"] = (h, pr, True)

GLASSLOGO_PREVIEWS = True   # /preview-glass-logo: the AL mark as a glossy 3D glass app icon (noindex, not in the sitemap, not in the zip)

def glasslogo_previews():
    if not GLASSLOGO_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "glass-logo.css"), encoding="utf-8").read(), flags=re.S).split())
    m = AL_MARK
    mk = f'<span class="gl-m" style="--m:url({m})"><img src="{m}" alt=""></span>'
    def card(n, t, d, cls, bg, extra=""):
        return (f'<article class="gl-c"><h3>{t}</h3><p>{d}</p><div class="gl-s {bg} gl-{n}"><i class="gl-orb" style="left:-10%;top:-8%;width:44%;height:44%;background:#7fa8ff"></i>'
                f'<i class="gl-orb" style="right:-12%;bottom:-10%;width:42%;height:42%;background:#9bb8ff"></i><div class="gl-t">{mk}</div>{extra}</div></article>')
    refl = f'<div class="gl-r"><img src="{m}" alt=""></div>'
    cards = (card(1, "1 · Frosted glass tile", "Like your reference: a soft frosted glass tile, your red and silver mark with gloss, light and a soft blue shadow.", "", "lt") +
             card(2, "2 · Black glass, red glow", "Dark glass tile with a bright edge, and the red mark glowing like a light behind glass.", "", "dk") +
             card(3, "3 · Crystal mark on red", "The mark is made of clear crystal glass, sitting on a glossy red tile. Most like a real glass object.", "", "rd") +
             card(4, "4 · Floating glossy mark", "No tile. The mark floats with a high gloss, a deep shadow and a mirror reflection.", "", "lt", "") .replace('</div></article>', refl + '</div></article>') +
             card(5, "5 · Crystal on dark glass", "Clear glass mark inside a frosted dark glass tile with a red edge light.", "", "dk"))
    hdr_l = f'<div class="gl-hd"><div class="gl-s lt gl-1" style="width:84px;aspect-ratio:1;border-radius:20px;border:0"><div class="gl-t" style="width:84%">{mk}</div></div><b style="font:900 20px Archivo,sans-serif">AL ARBAB</b><span style="font:700 11px Archivo,sans-serif;letter-spacing:.2em;opacity:.7">TRAVEL &amp; TOURS</span></div>'
    hdr_d = f'<div class="gl-hd dk"><div class="gl-s dk gl-2" style="width:84px;aspect-ratio:1;border-radius:20px;border:0"><div class="gl-t" style="width:84%">{mk}</div></div><b style="font:900 20px Archivo,sans-serif;color:#fff">AL ARBAB</b><span style="font:700 11px Archivo,sans-serif;letter-spacing:.2em;color:#aeb6c4">TRAVEL &amp; TOURS</span></div>'
    content = f"""<section class="sec"><div class="head"><div><h2>AL logo in glass style</h2></div><p class="lead">Your reference is a glossy 3D glass app icon. Here is the same mark treated that way. The shape and colours of the logo are not changed, only the material around and over it. Below the cards you can see how it sits in the header. Nothing is live.</p></div><div class="gl-g">{cards}</div>{hdr_l}{hdr_d}</section>"""
    ph = pagehead("Preview", "AL logo in glass", "Your AL mark as a glossy 3D glass app icon. Tell me the number.")
    body = shell("/preview-glass-logo", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-glass-logo", "AL logo in glass | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-glass-logo"]
    PAGES["/preview-glass-logo"] = (h.replace("</head>", f"<style>{css}</style></head>", 1), pr, True)

NAVSOFT_PREVIEWS = True   # /preview-navbar-soft: soft raised pill navigation, after the owner's button reference (noindex, not in the sitemap, not in the zip)

def navsoft_previews():
    if not NAVSOFT_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "nav-soft.css"), encoding="utf-8").read(), flags=re.S).split())
    items = [("Home", "Start"), ("Visas", "Guides"), ("Destinations", "Countries"), ("Flights", "Tickets"), ("Umrah", "Packages"), ("Packages", "Holidays")]
    logo = f'<a class="sf-lg" href="#"><img src="{AL_MARK_S}" alt="" width="46" height="36"><span><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span></a>'
    wa = '<a class="sf-wa" href="#">WhatsApp us</a>'
    def pills(knob, active=0, sub=True):
        out = ""
        for i, (n, s) in enumerate(items):
            k = {"dot": "<i></i>", "plus": "+" if n in ("Visas", "Destinations") else "&rarr;"}[knob]
            out += f'<a class="sf-p{" on" if i == active else ""}" href="#"><span class="sf-t"><b>{n}</b><small>{s}</small></span><span class="sf-k">{k}</span></a>'
        return out
    def stage(cls, inner): return f'<div class="sf-s sf-{cls}"><div class="sf-row">{logo}<nav class="sf-nav" aria-label="Preview">{inner}</nav>{wa}</div></div>'
    cards = [("A · Soft pills with a light", "Your reference as a menu: every page is a raised soft pill with its name and a small line under it, and a round knob. The page you are on has its knob lit.", stage("A", pills("dot"))),
             ("B · Plus and arrow pills", "Same pills, but the knob shows a + on the menus that open (Visas, Destinations) and an arrow on the rest. The current page glows orange like the last button in your picture.", stage("B", pills("plus"))),
             ("C · Pressed-in current page", "The page you are on is pushed into the surface, like a pressed physical button, with a red light. All others stay raised.", stage("C", pills("dot", 2))),
             ("D · One tray", "Quieter version: one sunken tray holds all the pages as plain labels, and the current one is a raised pill. Easiest to fit on small screens.", stage("D", pills("dot", 1)))]
    body_cards = "".join(f'<article class="sf-x"><h3>{t}</h3><p>{d}</p>{h}</article>' for t, d, h in cards)
    js = "document.querySelectorAll('.sf-nav').forEach(function(n){n.querySelectorAll('.sf-p').forEach(function(p){p.addEventListener('click',function(e){e.preventDefault();n.querySelectorAll('.sf-p').forEach(function(x){x.classList.remove('on')});p.classList.add('on')})})});document.querySelectorAll('.sf-lg,.sf-wa').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault()})});"
    content = f"""<section class="sec"><div class="head"><div><h2>Soft raised pill navigation</h2></div><p class="lead">The same single row as now (Home, Visas, Destinations and so on), only the button design changes, taken from your reference: soft, raised pills with a light. Click a pill to make it the current page. The real header has eight pages, so on a narrow screen it folds into the menu button as it does today. Nothing is live.</p></div>{body_cards}<p class="sf-note">Preview only. The site header has not been changed.</p></section>"""
    ph = pagehead("Preview", "Soft pill navigation", "Your button reference applied to the navigation row. Tell me the letter.")
    body = shell("/preview-navbar-soft", [("Home", "/"), ("Navigation preview", None)], ph, content)
    page("/preview-navbar-soft", "Soft pill navigation | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-navbar-soft"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-navbar-soft"] = (h, pr, True)

GLASSLOGOBLUE_PREVIEWS = True   # /preview-glass-logo-blue: the AL mark in the reference's blue glass colours (noindex, not in the sitemap, not in the zip)

def glasslogoblue_previews():
    if not GLASSLOGOBLUE_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", (open(os.path.join(ROOT, "assets", "glass-logo.css"), encoding="utf-8").read() + open(os.path.join(ROOT, "assets", "glass-logo-blue.css"), encoding="utf-8").read()), flags=re.S).split())
    m = f"/assets/brand/al-mark-blue.png?v={asset_hash('brand/al-mark-blue.png')}"
    mk = f'<span class="gl-m" style="--m:url({m})"><img src="{m}" alt=""></span>'
    def card(n, t, d, bg, extra=""):
        return (f'<article class="gl-c"><h3>{t}</h3><p>{d}</p><div class="gl-s {bg} gl-{n}"><i class="gl-orb" style="left:-10%;top:-8%;width:44%;height:44%;background:#6f9bff"></i>'
                f'<i class="gl-orb" style="right:-12%;bottom:-10%;width:42%;height:42%;background:#8fb0ff"></i><div class="gl-t">{mk}</div>{extra}</div></article>')
    refl = f'<div class="gl-r"><img src="{m}" alt=""></div>'
    cards = (card(1, "1 · Exactly like your reference", "A frosted white glass tile on a pale blue surface. The mark uses the three blues of the reference: deep blue, bright blue and a white-lilac ribbon.", "pb") +
             card(3, "2 · Blue crystal tile", "A glossy blue glass tile, with the mark carved in clear white crystal. Strong colour, good for the favicon and the app icon.", "pb") +
             card(2, "3 · Dark navy glass", "Deep navy glass with a blue glow behind the mark. For the footer and the welcome screen.", "nv") +
             card(4, "4 · Floating, no tile", "No tile. The blue mark floats with a gloss, a soft blue shadow and a mirror reflection.", "pb") .replace('</div></article>', refl + '</div></article>') +
             card(5, "5 · Crystal on dark glass", "A clear glass mark inside a dark frosted tile with a blue edge light.", "nv"))
    hdr_l = f'<div class="gl-hd"><div class="gl-s pb gl-1" style="width:84px;aspect-ratio:1;border-radius:20px;border:0"><div class="gl-t" style="width:84%">{mk}</div></div><b style="font:900 20px Archivo,sans-serif;color:#0a2fb0">AL ARBAB</b><span style="font:700 11px Archivo,sans-serif;letter-spacing:.2em;opacity:.7">TRAVEL &amp; TOURS</span></div>'
    hdr_d = f'<div class="gl-hd dk"><div class="gl-s nv gl-2" style="width:84px;aspect-ratio:1;border-radius:20px;border:0"><div class="gl-t" style="width:84%">{mk}</div></div><b style="font:900 20px Archivo,sans-serif;color:#fff">AL ARBAB</b><span style="font:700 11px Archivo,sans-serif;letter-spacing:.2em;color:#aeb6c4">TRAVEL &amp; TOURS</span></div>'
    content = f"""<section class="sec gl-blue"><div class="head"><div><h2>AL logo in the reference blue</h2></div><p class="lead">Same glass icon look, now in the colours of your reference picture: deep blue, bright blue and a white-lilac ribbon. The shape of the AL mark and the plane are unchanged. The brand red stays as the other option. Nothing is live.</p></div><div class="gl-g">{cards}</div>{hdr_l}{hdr_d}</section>"""
    ph = pagehead("Preview", "AL logo, blue glass", "The AL mark in the reference blue glass colours. Tell me the number.")
    body = shell("/preview-glass-logo-blue", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-glass-logo-blue", "AL logo blue glass | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-glass-logo-blue"]
    PAGES["/preview-glass-logo-blue"] = (h.replace("</head>", f"<style>{css}</style></head>", 1), pr, True)

BRANDPILL_PREVIEWS = True   # /preview-brand-pill: the logo and name as a soft pill to match the soft nav pills (noindex, not in the sitemap, not in the zip)

def brandpill_previews():
    if not BRANDPILL_PREVIEWS:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "brand-pill.css"), encoding="utf-8").read(), flags=re.S).split())
    names = ["Home", "Visas", "Destinations", "Flights", "Umrah", "Packages", "Free Check", "Contact"]
    nav = "".join(f'<a class="bp-p{" on" if i == 0 else ""}" href="#">{n}</a>' for i, n in enumerate(names))
    img = f'<img src="{AL_MARK_S}" alt="" width="54" height="44">'
    txt = '<span class="nm"><b>AL ARBAB</b><small>TRAVEL &amp; TOURS</small></span>'
    variants = [("A", "A · Raised soft pill", "The logo and name sit together in one raised pill, same material as the menu buttons.", f'<a class="bp-b bp-A" href="#">{img}{txt}</a>'),
                ("B", "B · Logo in a round knob", "The mark sits in a round raised knob, like the knobs on the menu pills, and the name beside it.", f'<a class="bp-b bp-B" href="#"><span class="kn">{img}</span>{txt}</a>'),
                ("C", "C · Pressed tray, mark rising out", "A sunken tray with the logo popping out of it, bigger than the pill. Most eye-catching.", f'<a class="bp-b bp-C" href="#">{img}{txt}</a>'),
                ("D", "D · Dark pill", "A black glass-look pill with a white name. The strongest contrast against the light menu buttons.", f'<a class="bp-b bp-D" href="#">{img}{txt}</a>'),
                ("E", "E · Name with a red capsule", "Bold name, and TRAVEL &amp; TOURS inside a small red capsule, like a badge.", f'<a class="bp-b bp-E" href="#">{img}{txt}</a>')]
    cards = ""
    for k, t, d, brand in variants:
        cards += (f'<article class="bp-x"><h3>{t}</h3><p>{d}</p><div class="bp-s"><div class="bp-row">{brand}<nav class="bp-nav">{nav}</nav><a class="bp-wa" href="#">WhatsApp us</a></div>'
                  f'<div class="bp-tg"><button type="button">Light</button></div></div></article>')
    js = ("document.querySelectorAll('.bp-tg button').forEach(function(b){b.addEventListener('click',function(){var s=b.closest('.bp-s');s.classList.toggle('lt');b.textContent=s.classList.contains('lt')?'Photo':'Light'})});"
          "document.querySelectorAll('.bp-x a').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault()})});")
    content = f"""<section class="sec"><div class="head"><div><h2>Logo and name as a soft pill</h2></div><p class="lead">The menu buttons are soft raised pills, so here the logo and the name are put in the same kind of shape. Each is shown beside the real menu, on the hero photo. Use the Light button to see it on a light page. Nothing is live.</p></div>{cards}<p class="bp-note">Preview only. The header has not been changed.</p></section>"""
    ph = pagehead("Preview", "Logo as a soft pill", "Five ways to put the logo and name in the same pill shape as the menu. Tell me the letter.")
    body = shell("/preview-brand-pill", [("Home", "/"), ("Logo preview", None)], ph, content)
    page("/preview-brand-pill", "Logo pill preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-brand-pill"]
    h = h.replace("</head>", f"<style>{css}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-brand-pill"] = (h, pr, True)

FLIGHT2_PREVIEWS = True   # /preview-flight-2: five new route ideas for the home hero, in place of the dotted arc (noindex, not in the sitemap, not in the zip)

def flight2_previews():
    if not FLIGHT2_PREVIEWS:
        return
    PL = "M22,0 C22,-2 20,-3 17,-3 L4,-3 L-4,-17 L-9,-17 L-5,-3 L-14,-3 L-17,-8 L-20,-8 L-17,0 L-20,8 L-17,8 L-14,3 L-5,3 L-9,17 L-4,17 L4,3 L17,3 C20,3 22,2 22,0 Z"
    css = """.f2-g{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}@media(max-width:800px){.f2-g{grid-template-columns:1fr}}
.f2-c h3{font:900 17px Archivo,sans-serif;margin:0 0 3px}.f2-c p{margin:0 0 8px;font-size:13.5px;opacity:.8}
.f2-s{position:relative;aspect-ratio:16/9;border-radius:18px;overflow:hidden;background:#0b1a24 url(/assets/hero/1568508432206-7541b535f84c-1000.webp) center/cover;border:1px solid rgba(11,18,32,.15)}
.f2-s::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,12,24,.3),rgba(0,12,24,.5))}
.f2-s svg{position:absolute;inset:0;width:100%;height:100%}
.f2-s text{font-family:Archivo,Inter,sans-serif}
@keyframes f2dr{0%{stroke-dashoffset:1;opacity:1}55%{stroke-dashoffset:0;opacity:1}92%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}}
@keyframes f2fd{0%,50%{opacity:0}58%,92%{opacity:1}100%{opacity:0}}
@keyframes f2pl{0%,3%{opacity:0}6%,92%{opacity:1}100%{opacity:0}}
@keyframes f2ping{0%{r:6;opacity:.9}100%{r:60;opacity:0}}
@keyframes f2sw{to{transform:rotate(360deg)}}
@keyframes f2mer{0%{transform:scaleX(1)}50%{transform:scaleX(-1)}100%{transform:scaleX(1)}}
@keyframes f2stamp{0%,52%{opacity:0;transform:scale(1.9) rotate(-26deg)}60%{opacity:.95;transform:scale(.96) rotate(-12deg)}64%,92%{opacity:.92;transform:scale(1) rotate(-12deg)}100%{opacity:0;transform:scale(1) rotate(-12deg)}}
@keyframes f2blip{0%,48%{opacity:.25;r:6}54%{opacity:1;r:10}90%{opacity:1;r:8}100%{opacity:.25;r:6}}
.f2-dr{stroke-dasharray:1;animation:f2dr 6s linear infinite}
.f2-fd{animation:f2fd 6s linear infinite}
.f2-pl{animation:f2pl 6s linear infinite}
.f2-bp{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:flex;width:min(86%,640px);color:#10151c;filter:drop-shadow(0 18px 24px rgba(0,0,0,.45))}
.f2-bp>div{background:#fffdf7;padding:14px 18px;display:flex;flex-direction:column;justify-content:center}
.f2-bp .l{border-radius:14px 0 0 14px;min-width:120px}.f2-bp .m{flex:1;position:relative;align-items:stretch;padding:0 6px}.f2-bp .r{min-width:120px;text-align:right}
.f2-bp .s{border-radius:0 14px 14px 0;border-left:2px dashed rgba(16,21,28,.3);align-items:center;gap:8px;min-width:96px}
.f2-bp small{font:700 9px/1 Inter,sans-serif;letter-spacing:.2em;color:#7a8190}
.f2-bp b{font:900 clamp(26px,5.4vw,46px)/1 Archivo,sans-serif}.f2-bp span.c{font:700 12px Inter,sans-serif;color:#5d6676}
.f2-bp .line{position:absolute;left:8px;right:8px;top:50%;border-top:3px dotted #9aa1ad}
.f2-bp .plane{position:absolute;top:50%;left:0;width:34px;height:28px;margin:-14px 0 0 -17px;color:#e30613;animation:f2fly 4.2s ease-in-out infinite}
.f2-bp .plane svg{width:100%;height:100%;fill:currentColor}
@keyframes f2fly{0%{left:2%}60%,100%{left:96%}}
.f2-bp .code{width:56px;height:56px;background:repeating-linear-gradient(90deg,#10151c 0 3px,transparent 3px 5px,#10151c 5px 6px,transparent 6px 9px)}
.f2-bp .s em{font:800 10px Inter,sans-serif;font-style:normal;letter-spacing:.14em;color:#e30613}"""
    def svg(inner): return f'<svg viewBox="0 0 800 450" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{inner}</svg>'
    plane = lambda path, dur=3.3: (f'<g class="f2-pl"><g><path d="{PL}" fill="#fff" stroke="#0a1530" stroke-width="1.2" transform="scale(1.35)"/>'
                                   f'<animateMotion dur="6s" repeatCount="indefinite" rotate="auto" path="{path}" keyPoints="0;1;1" keyTimes="0;.55;1" calcMode="linear"/></g></g>')
    chip = lambda x, y, t, fill="#fff", col="#0b0e14": (f'<rect x="{x - 32}" y="{y}" width="64" height="26" rx="13" fill="{fill}"/>'
                                                       f'<text x="{x}" y="{y + 18}" text-anchor="middle" font-size="14" font-weight="800" fill="{col}">{t}</text>')
    # 1 boarding pass card
    s1 = ('<div class="f2-bp"><div class="l"><small>FROM</small><b>ISB</b><span class="c">Islamabad</span></div>'
          f'<div class="m"><i class="line"></i><span class="plane"><svg viewBox="-24 -20 48 40"><path d="{PL}"/></svg></span></div>'
          '<div class="r"><small>TO</small><b>HKT</b><span class="c">Phuket</span></div>'
          '<div class="s"><i class="code"></i><em>BOARDING</em></div></div>')
    # 2 globe with arc
    arc2 = "M335,200 Q420,40 485,290"
    s2 = svg('<defs><radialGradient id="gb" cx="38%" cy="32%"><stop offset="0" stop-color="#9fd2ff" stop-opacity=".75"/><stop offset=".6" stop-color="#2a6fd6" stop-opacity=".55"/><stop offset="1" stop-color="#0a2a6b" stop-opacity=".7"/></radialGradient></defs>'
             '<circle cx="400" cy="235" r="125" fill="url(#gb)" stroke="rgba(255,255,255,.7)" stroke-width="2"/>'
             + "".join(f'<ellipse cx="400" cy="235" rx="125" ry="{ry}" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="1.2"/>' for ry in (28, 62, 96))
             + "".join(f'<ellipse cx="400" cy="235" rx="125" ry="125" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="1.2" style="transform-origin:400px 235px;animation:f2mer 9s linear infinite;animation-delay:{-i * 1.5}s;transform-box:fill-box" transform="" />' for i in range(4))
             + '<circle cx="335" cy="200" r="7" fill="#fff"/><circle cx="335" cy="200" r="3" fill="#0a1530"/>'
             f'<path class="f2-dr" pathLength="1" d="{arc2}" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>'
             '<circle cx="485" cy="290" r="8" fill="#e30613" class="f2-fd"/><circle cx="485" cy="290" r="8" fill="none" stroke="#fff" stroke-width="2" style="animation:f2ping 2.4s ease-out infinite"/>'
             + chip(335, 214, "ISB") + chip(485, 306, "HKT", "#e30613", "#fff") + plane(arc2))
    # 3 altitude profile
    p3 = "M70,350 C230,350 250,120 400,120 S570,350 730,350"
    s3 = svg('<defs><linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".4"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
             '<line x1="50" y1="350" x2="750" y2="350" stroke="rgba(255,255,255,.6)" stroke-width="2"/>'
             f'<path d="{p3} L730,350 L70,350Z" fill="url(#ar)" class="f2-fd"/>'
             '<line x1="400" y1="120" x2="400" y2="350" stroke="rgba(255,255,255,.5)" stroke-width="2" stroke-dasharray="3 8" stroke-linecap="round"/>'
             f'<path class="f2-dr" pathLength="1" d="{p3}" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
             '<circle cx="70" cy="350" r="9" fill="#fff"/><circle cx="730" cy="350" r="9" fill="#e30613"/>'
             + chip(70, 368, "ISB") + chip(730, 368, "HKT", "#e30613", "#fff")
             + '<text x="400" y="102" text-anchor="middle" font-size="15" font-weight="800" fill="#fff" letter-spacing="3">CRUISING</text>' + plane(p3))
    # 4 radar
    s4 = svg('<defs><radialGradient id="sw" cx="0" cy="0" r="1"><stop offset="0" stop-color="#7dffb4" stop-opacity=".55"/><stop offset="1" stop-color="#7dffb4" stop-opacity="0"/></radialGradient></defs>'
             + "".join(f'<circle cx="150" cy="340" r="{r}" fill="none" stroke="rgba(255,255,255,.4)" stroke-width="1.5"/>' for r in (110, 220, 330, 440, 550))
             + '<g style="transform-origin:150px 340px;animation:f2sw 4s linear infinite"><path d="M150,340 L700,340 A550,550 0 0 0 640,200 Z" fill="url(#sw)" transform="translate(0,0)" style="transform-origin:150px 340px;transform:rotate(-24deg)"/></g>'
             '<circle cx="150" cy="340" r="6" fill="none" stroke="#fff" stroke-width="2" style="animation:f2ping 2.6s ease-out infinite"/>'
             '<circle cx="150" cy="340" r="8" fill="#fff"/>'
             '<path d="M150,340 L650,120" stroke="rgba(255,255,255,.6)" stroke-width="2" stroke-dasharray="3 9" stroke-linecap="round"/>'
             '<circle cx="650" cy="120" r="8" fill="#ff4d5a" style="animation:f2blip 4s linear infinite"/>'
             + chip(150, 356, "ISB") + chip(650, 138, "HKT", "#e30613", "#fff") + plane("M150,340 L650,120"))
    # 5 passport stamp
    p5 = "M110,360 Q330,60 600,170"
    s5 = svg('<defs><filter id="ink" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence baseFrequency=".9" numOctaves="2" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="3"/></filter>'
             '<path id="cp" d="M0,-52 a52,52 0 1 1 -.1,0"/></defs>'
             f'<path class="f2-dr" pathLength="1" d="{p5}" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-dasharray="1"/>'
             '<circle cx="110" cy="360" r="8" fill="#fff"/>' + chip(110, 376, "ISB") + plane(p5)
             + '<g style="transform-origin:640px 210px;animation:f2stamp 6s linear infinite"><g transform="translate(640 210)" filter="url(#ink)" fill="none" stroke="#e4f6f5" stroke-width="5">'
             '<circle r="86"/><circle r="72" stroke-width="2.5"/><circle r="34" stroke-width="2"/>'
             '<text fill="#e4f6f5" stroke="none" font-size="17" font-weight="800" letter-spacing="3" text-anchor="middle"><textPath href="#cp2" startOffset="50%">PHUKET &#183; THAILAND &#183; ISB</textPath></text>'
             '<text fill="#e4f6f5" stroke="none" font-size="30" font-weight="900" text-anchor="middle" y="10">HKT</text></g></g>')
    s5 = s5.replace('<path id="cp" d="M0,-52 a52,52 0 1 1 -.1,0"/>', '<path id="cp2" d="M-62,0 a62,62 0 1 1 124,0"/>')
    items = [("pass", "1 · Boarding pass card", "A real boarding-pass ticket sits in the middle of the photo: ISB on one side, the destination code on the other, a plane flying along the dotted line between them, and a barcode with BOARDING.", s1),
             ("globe", "2 · Globe and arc", "A small glowing globe with a light arc from Islamabad to the destination, a pulsing marker where you land and the plane riding the arc. Turns the route into a world view.", s2),
             ("profile", "3 · Flight profile", "Like a flight-tracker app: a line climbs, cruises and descends, with the area below filled. ISB and the destination sit on the ground line and the plane rides the curve.", s3),
             ("radar", "4 · Radar", "Radar rings and a sweeping beam from Islamabad. The destination lights up red as the beam passes it, and the plane flies the bearing.", s4),
             ("stamp", "5 · Passport stamp", "The plane draws its route, and when it lands a round passport-style stamp slams down on the destination with an ink texture. A travel-document feel that nobody else has.", s5)]
    cards = "".join(f'<article class="f2-c"><h3>{t}</h3><p>{d}</p><div class="f2-s">{h}</div></article>' for m, t, d, h in items)
    content = f"""<section class="sec"><div class="head"><div><h2>New route designs for the hero</h2></div><p class="lead">Five different things to put in the circled place, instead of the dotted arc. Each repeats on its own, and all show the route from Islamabad (ISB) to Phuket (HKT) on the Thailand photo. Nothing is live.</p></div><div class="f2-g">{cards}</div></section>"""
    ph = pagehead("Preview", "New hero route designs", "Five new designs for the plane route in the hero. Tell me the number.")
    body = shell("/preview-flight-2", [("Home", "/"), ("Animation preview", None)], ph, content)
    page("/preview-flight-2", "New hero route designs | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-flight-2"]
    PAGES["/preview-flight-2"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

HEROIDEAS_PREVIEWS = True   # /preview-hero-ideas: three hero ideas that do a job: live twin clocks, destination wheel, ticket printer (noindex, not in the sitemap, not in the zip)

def heroideas_previews():
    if not HEROIDEAS_PREVIEWS:
        return
    js = open(os.path.join(ROOT, "assets", "hero-ideas.js"), encoding="utf-8").read()
    css = """.hx-g{display:grid;gap:18px}.hx-c h3{font:900 18px Archivo,sans-serif;margin:0 0 3px}.hx-c p{margin:0 0 8px;font-size:13.5px;opacity:.8;max-width:78ch}
.hx-s{position:relative;min-height:380px;border-radius:20px;overflow:hidden;border:1px solid rgba(11,18,32,.15);color:#fff;
  background:linear-gradient(180deg,rgba(0,12,26,.35),rgba(0,12,26,.6)),url(/assets/hero/1568508432206-7541b535f84c-1000.webp) center/cover}
.hx-s button{font-family:Inter,sans-serif}
.hx-chips{position:absolute;left:0;right:0;bottom:14px;display:flex;gap:8px;flex-wrap:wrap;justify-content:center;padding:0 12px}
.hx-chips button{display:inline-flex;align-items:center;gap:7px;min-height:38px;padding:0 14px;border-radius:99px;border:1px solid rgba(255,255,255,.4);background:rgba(10,20,30,.55);color:#fff;font-weight:700;font-size:13px;cursor:pointer}
.hx-chips button.on{background:#fff;color:#0b1220}.hx-chips img{border-radius:3px}
/* 1 twin clocks */
.hx-twin{position:absolute;left:0;right:0;top:44px;display:flex;align-items:center;justify-content:center;gap:clamp(10px,3vw,40px);padding:0 14px;flex-wrap:wrap}
.hx-cl{display:grid;gap:8px;justify-items:center}.hx-cl small{font:800 12px Inter,sans-serif;letter-spacing:.22em}.hx-cl em{font:600 12px Inter,sans-serif;font-style:normal;opacity:.75}
.hx-fl{display:flex;gap:4px;align-items:center}
.hx-fl b{position:relative;display:block;width:clamp(34px,6vw,58px);height:clamp(54px,9.4vw,92px);line-height:clamp(54px,9.4vw,92px);text-align:center;border-radius:8px;overflow:hidden;
  background:linear-gradient(#262a31 0 49%,#0b0d11 50% 100%);color:#ffd23f;font:700 clamp(30px,5.4vw,58px)/1 "JetBrains Mono",Consolas,monospace;box-shadow:0 10px 18px -8px rgba(0,0,0,.7)}
.hx-fl b::after{content:"";position:absolute;left:0;right:0;top:50%;height:2px;background:#000}
.hx-c{font:800 40px Inter,sans-serif}.hx-fl i.hx-c{color:#ffd23f;font-style:normal;font-size:clamp(26px,4.4vw,46px);padding:0 2px}
.hx-s.flip .hx-fl b{animation:hxfl .5s ease}
@keyframes hxfl{0%{transform:rotateX(0)}50%{transform:rotateX(-90deg)}100%{transform:rotateX(0)}}
.hx-mid{position:relative;display:grid;justify-items:center;gap:10px;min-width:clamp(90px,16vw,200px)}
.hx-ln{display:block;width:100%;border-top:3px dotted rgba(255,255,255,.7)}
.hx-pl{position:absolute;top:-13px;left:0;width:34px;height:28px;color:#fff;animation:hxfly 3.4s ease-in-out infinite;filter:drop-shadow(0 3px 5px rgba(0,0,0,.5))}.hx-pl svg{width:100%;height:100%;fill:currentColor}
@keyframes hxfly{0%{left:0}70%,100%{left:calc(100% - 34px)}}
.hx-mid strong{font:900 16px Inter,sans-serif;background:#e30613;border-radius:99px;padding:6px 14px;margin-top:10px;white-space:nowrap}
/* 2 wheel */
.hx-wh{position:absolute;inset:0;display:grid;justify-items:center;align-content:start;padding-top:34px}
.hx-arc{position:relative;width:0;height:0;margin-top:40px}
.hx-dot{position:absolute;left:0;top:0;width:60px;height:60px;margin:-30px 0 0 -30px;padding:0;border-radius:50%;border:3px solid rgba(255,255,255,.85);background:#111;cursor:pointer;overflow:hidden;
  transition:transform .55s cubic-bezier(.3,1.3,.5,1),opacity .3s;box-shadow:0 12px 20px -8px rgba(0,0,0,.7)}
.hx-dot img{width:100%;height:100%;object-fit:cover;display:block}.hx-dot.on{border-color:#ffd23f;box-shadow:0 0 0 5px rgba(255,210,63,.3),0 16px 26px -8px rgba(0,0,0,.7)}
.hx-info{position:absolute;left:50%;transform:translateX(-50%);bottom:34px;text-align:center;display:grid;gap:5px;width:min(90%,420px)}
.hx-info small{font:700 11px Inter,sans-serif;letter-spacing:.22em;opacity:.8}.hx-info b{font:900 clamp(28px,5vw,44px)/1 Archivo,sans-serif}.hx-info span{font:700 14px Inter,sans-serif;opacity:.85}
.hx-info a{justify-self:center;margin-top:8px;padding:11px 18px;border-radius:99px;background:#15a34a;color:#fff;font:800 13px Inter,sans-serif;text-decoration:none}
.hx-ar{position:absolute;top:50%;margin-top:-40px;width:44px;height:44px;border-radius:50%;border:1px solid rgba(255,255,255,.5);background:rgba(10,20,30,.55);color:#fff;font-size:22px;cursor:pointer}.hx-ar.l{left:16px}.hx-ar.r{right:16px}
/* 3 ticket printer */
.hx-pr{position:absolute;inset:0;display:grid;justify-items:center;align-content:start;padding-top:26px}
.hx-slot{position:relative;z-index:3;width:min(86%,520px);height:46px;border-radius:14px;background:linear-gradient(#2b2f37,#13161b);box-shadow:0 14px 22px -10px rgba(0,0,0,.7);display:grid;place-items:center}
.hx-slot::after{content:"";position:absolute;left:14px;right:14px;bottom:8px;height:6px;border-radius:4px;background:#000;box-shadow:inset 0 2px 3px rgba(0,0,0,.9)}
.hx-slot span{font:800 11px Inter,sans-serif;letter-spacing:.24em;color:#aeb6c4;margin-bottom:8px}
.hx-tkw{position:relative;width:min(80%,470px);height:190px;overflow:hidden;margin-top:-6px;z-index:2}
.hx-tk{position:absolute;left:0;right:0;top:0;display:grid;grid-template-columns:1fr 1.2fr 1fr;grid-template-rows:auto auto;gap:6px 8px;padding:16px 18px;border-radius:0 0 14px 14px;background:#fffdf7;color:#10151c;transform:translateY(-110%)}
.hx-tk.out{animation:hxprint 1.1s cubic-bezier(.3,1,.4,1) forwards}
@keyframes hxprint{0%{transform:translateY(-110%)}100%{transform:translateY(0)}}
.hx-tk small{display:block;font:700 9px Inter,sans-serif;letter-spacing:.2em;color:#7a8190}.hx-tk b{display:block;font:900 clamp(26px,5vw,40px)/1 Archivo,sans-serif}.hx-tk span{font:700 12px Inter,sans-serif;color:#5d6676}
.hx-t2{position:relative;align-self:center}.hx-ln2{display:block;border-top:3px dotted #9aa1ad}.hx-pl2{position:absolute;top:-13px;left:0;width:30px;height:24px;color:#e30613;animation:hxfly 3s ease-in-out infinite}.hx-pl2 svg{width:100%;height:100%;fill:currentColor}
.hx-t3{text-align:right}
.hx-t4{grid-column:1/-1;display:flex;align-items:center;gap:12px;border-top:2px dashed rgba(16,21,28,.25);padding-top:10px}
.hx-bc{flex:none;width:70px;height:26px;background:repeating-linear-gradient(90deg,#10151c 0 2px,transparent 2px 4px,#10151c 4px 5px,transparent 5px 8px)}
.hx-t4 em{font:700 11.5px Inter,sans-serif;font-style:normal;color:#10151c}
.hx-print{position:absolute;right:16px;top:30px;min-height:40px;padding:0 16px;border-radius:99px;border:0;background:#e30613;color:#fff;font-weight:800;font-size:12.5px;cursor:pointer;z-index:4}"""
    items = [("clock", "1 · Two live clocks, Islamabad and the destination", "Real, live time in Islamabad and in the destination, shown on flip-board tiles, with how many hours ahead it is. A traveller always wonders this. Tap a country and the destination clock flips. It is useful, and it moves."),
             ("wheel", "2 · Destination wheel", "A dial of country flags on an arc. Spin it with the arrows, the mouse wheel or a tap. The country in front is shown big, with its city and a WhatsApp button for that visa. The visitor picks, instead of looking at a picture."),
             ("ticket", "3 · Trip ticket printer", "A small printer slot at the top. Choose a country and a boarding-style trip ticket prints out of it for that destination, ending with Send your documents on WhatsApp. The visitor leaves with something that looks like their own ticket.")]
    cards = "".join(f'<article class="hx-c"><h3>{t}</h3><p>{d}</p><div class="hx-s" data-m="{m}"></div></article>' for m, t, d in items)
    content = f"""<section class="sec"><div class="head"><div><h2>Hero ideas that do a job</h2></div><p class="lead">After searching what good travel sites do, the clear finding is that the ones people remember let the visitor do something, instead of just watching an animation: pick a destination, see something real, take something away. So these three are working tools, not decoration. Try each one. Nothing is live.</p></div><div class="hx-g">{cards}</div></section>"""
    ph = pagehead("Preview", "Hero ideas that work", "Three working hero ideas from research. Tell me the number.")
    body = shell("/preview-hero-ideas", [("Home", "/"), ("Hero preview", None)], ph, content)
    page("/preview-hero-ideas", "Hero ideas | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-hero-ideas"]
    h = h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-hero-ideas"] = (h, pr, True)

CONTRAIL_PREVIEWS = True   # /preview-contrail: an airliner with a big looping contrail and step callouts, after the owner's reference slide (noindex, not in the sitemap, not in the zip)

def contrail_previews():
    if not CONTRAIL_PREVIEWS:
        return
    PATH = "M470,202 C300,230 170,270 168,335 C166,410 330,430 500,410 C700,390 880,360 1060,312"
    plane = ('<g id="ctp"><g transform="scale(1.05)">'
             '<ellipse cx="0" cy="26" rx="120" ry="8" fill="rgba(0,20,60,.18)"/>'
             '<polygon points="12,-12 -44,-52 -66,-52 -26,-10" fill="#dfe6f2"/>'
             '<polygon points="-122,-6 -152,-58 -108,-58 -72,-14" fill="#16306b"/><polygon points="-136,-30 -118,-30 -108,-58 -150,-58" fill="#e30613"/>'
             '<path d="M-124,0 C-124,-15 -62,-21 20,-21 L92,-17 C122,-13 134,-4 136,0 C134,6 122,11 92,13 L20,17 C-62,17 -124,15 -124,0Z" fill="url(#ctb)"/>'
             '<path d="M-124,3 C-100,10 -40,15 20,15 L92,12 C112,9 128,5 135,1 C128,8 112,14 92,16 L20,20 C-62,20 -118,16 -124,3Z" fill="rgba(60,80,130,.35)"/>'
             '<path d="M112,-10 L130,-3 L112,-3Z" fill="#14233f"/>'
             '<line x1="-96" y1="-6" x2="96" y2="-6" stroke="#2a3f6e" stroke-width="3" stroke-dasharray="3 7" stroke-linecap="round"/>'
             '<polygon points="14,6 -50,60 -74,60 -24,6" fill="#f4f7fc" stroke="#c6d0e2" stroke-width="1"/>'
             '<ellipse cx="-12" cy="30" rx="20" ry="8" fill="#e8edf6" stroke="#b6c1d6" stroke-width="1"/>'
             '<polygon points="-92,6 -118,26 -132,26 -108,4" fill="#eef2f9"/>'
             '</g></g>')
    css = """.ct-c h3{font:900 18px Archivo,sans-serif;margin:0 0 3px}.ct-c p{margin:0 0 10px;font-size:13.5px;opacity:.8;max-width:78ch}
.ct-s{position:relative;aspect-ratio:16/9;border-radius:20px;overflow:hidden;border:1px solid rgba(11,18,32,.15);color:#fff;background:linear-gradient(180deg,#2f86f0 0%,#62b4ff 55%,#bfe3ff 100%)}
.ct-s.ph{background:linear-gradient(180deg,rgba(0,40,100,.4),rgba(0,40,100,.15)),url(/assets/hero/1568508432206-7541b535f84c-1000.webp) center/cover}
.ct-s svg{position:absolute;inset:0;width:100%;height:100%}
.ct-ttl{position:absolute;left:5%;top:6%;font:800 clamp(18px,3.4vw,40px)/1 Archivo,sans-serif;letter-spacing:.01em;text-shadow:0 2px 12px rgba(0,40,120,.35)}
.ct-n{position:absolute;opacity:0;animation:ctin .9s ease forwards;border-left:1px solid rgba(255,255,255,.65);padding-left:10px;max-width:22%}
.ct-n i{display:block;font:italic 200 clamp(22px,4vw,48px)/1 Inter,sans-serif;letter-spacing:.01em}
.ct-n span{display:block;margin-top:6px;font:600 clamp(10px,1.3vw,15px)/1.35 Inter,sans-serif;text-shadow:0 1px 6px rgba(0,40,120,.4)}
@keyframes ctin{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.ct-dr{stroke-dasharray:1;stroke-dashoffset:1;animation:ctdr 3.6s cubic-bezier(.45,.05,.3,1) forwards}
@keyframes ctdr{to{stroke-dashoffset:0}}
.ct-b{display:flex;gap:8px;margin:12px 0 0;flex-wrap:wrap}.ct-b button{min-height:42px;padding:0 18px;border-radius:99px;border:0;background:#0b1213;color:#fff;font:700 13.5px Inter,sans-serif;cursor:pointer}.ct-b button.on{background:#e30613}"""
    notes = [("01", "Send your documents on WhatsApp", "left:6%;top:30%"), ("02", "Free document check by an adviser", "left:21%;top:17%"), ("03", "Your file is prepared and the checklist completed", "left:38%;top:12%"),
             ("04", "Submission guidance and follow-up", "left:4%;top:62%"), ("05", "The embassy decides; we keep you informed", "left:24%;top:72%"), ("06", "Flights and hotels with us, if you need them", "left:57%;top:72%")]
    sky = ('<defs><linearGradient id="ctb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#cfd8ea"/></linearGradient>'
           '<linearGradient id="ctg" gradientUnits="userSpaceOnUse" x1="170" y1="200" x2="1000" y2="330"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset=".45" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
           '<filter id="ctf" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="4"/></filter></defs>'
           '<g opacity=".95"><ellipse cx="1050" cy="70" rx="90" ry="20" fill="#fff" opacity=".45"/><ellipse cx="980" cy="52" rx="60" ry="14" fill="#fff" opacity=".4"/></g>'
           '<polygon points="0,600 90,545 150,570 230,520 300,560 380,600 0,675" fill="#cfe6ff"/><polygon points="250,675 420,590 500,610 600,575 700,640 760,675" fill="#dff0ff"/>'
           '<polygon points="520,675 640,610 720,625 820,585 920,625 1010,600 1100,640 1200,610 1200,675" fill="#cfe6ff"/><polygon points="0,640 120,610 210,640 330,625 450,660 480,675 0,675" fill="#e8f4ff"/>'
           '<polygon points="780,675 900,640 980,655 1090,630 1200,650 1200,675" fill="#f2f9ff"/>')
    trail = (f'<path class="ct-dr" pathLength="1" d="{PATH}" fill="none" stroke="url(#ctg)" stroke-width="30" stroke-linecap="round" filter="url(#ctf)" opacity=".8"/>'
             f'<path class="ct-dr" pathLength="1" d="{PATH}" fill="none" stroke="url(#ctg)" stroke-width="12" stroke-linecap="round"/>')
    motion = (f'<g>{plane}<animateMotion dur="3.6s" begin="0s" fill="freeze" rotate="auto" path="{PATH}" calcMode="spline" keyTimes="0;1" keySplines=".45 .05 .3 1"/></g>')
    def stage(extra=""):
        return f'<div class="ct-s{extra}"><svg viewBox="0 0 1200 675" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{sky}<g transform="translate(-30,-5)">{trail}{motion}</g></svg></div>'
    tpl = stage()
    js = ("(function(){var w=document.getElementById('ctw');var mode='';function draw(){w.innerHTML=window.__ct[mode]}"
          "document.querySelectorAll('[data-ct]').forEach(function(b){b.addEventListener('click',function(){mode=b.getAttribute('data-ct');"
          "document.querySelectorAll('[data-ct]').forEach(function(x){x.classList.toggle('on',x===b)});draw()})});"
          "document.getElementById('ctr').addEventListener('click',draw);})();")
    data = "window.__ct={'':" + json.dumps(stage()) + ",' ph':" + json.dumps(stage(" ph")) + "};"
    content = f"""<section class="sec"><div class="head"><div><h2>Airliner with a looping contrail</h2></div><p class="lead">After your reference slide: a big airliner with a soft white contrail that loops across the sky. The numbers and the steps are removed, so only the airliner and its loop remain, in the middle. It plays once and the plane rests at the right. Use Replay, and switch between the blue sky and the Thailand photo. Nothing is live.</p></div>
<article class="ct-c"><h3>Airliner and contrail, nothing else</h3><p>Only the airliner and its contrail, in the middle of the frame. No numbers and no text.</p><div id="ctw">{tpl}</div>
<div class="ct-b"><button type="button" id="ctr">Replay</button><button type="button" data-ct="" class="on">Blue sky</button><button type="button" data-ct=" ph">Thailand photo</button></div></article></section>"""
    ph = pagehead("Preview", "Contrail with steps", "Your reference slide made for AL ARBAB. Tell me what to change.")
    body = shell("/preview-contrail", [("Home", "/"), ("Hero preview", None)], ph, content)
    page("/preview-contrail", "Contrail preview | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-contrail"]
    h = h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1).replace("</body>", f"<script>{data}{js}</script></body>", 1)
    PAGES["/preview-contrail"] = (h, pr, True)

WIDGETS_PREVIEWS = True   # /preview-widgets: neon dark widget cards with the agency's own content, after the owner's reference (noindex, not in the sitemap, not in the zip)

def widgets_previews():
    if not WIDGETS_PREVIEWS:
        return
    from urllib.parse import quote
    js = open(os.path.join(ROOT, "assets", "widgets-preview.js"), encoding="utf-8").read()
    mask = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 340 330' preserveAspectRatio='none'><path d='M30,0 H196 Q214,0 214,18 V28 Q214,46 232,46 H310 Q340,46 340,76 V300 Q340,330 310,330 H30 Q0,330 0,300 V30 Q0,0 30,0Z'/></svg>")
    m = "url(\"data:image/svg+xml," + quote(mask) + "\")"
    css = ("""#wd-root{--m:%s}.wd-g{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%%),1fr));gap:20px;background:#6b6d70;padding:22px;border-radius:24px}
.wd{--a:#35ff4a;position:relative;min-height:330px;color:#ececec;font-family:Archivo,Inter,sans-serif}
.wd-bg{position:absolute;inset:0;background:linear-gradient(160deg,#171717,#000 55%%);-webkit-mask:var(--m) center/100%% 100%% no-repeat;mask:var(--m) center/100%% 100%% no-repeat;filter:drop-shadow(0 20px 20px rgba(0,0,0,.5))}
.wd-in{position:relative;z-index:1;padding:20px 22px 16px;display:grid;gap:12px;min-height:330px;grid-template-rows:auto auto 1fr auto}
.wd-dots{position:absolute;right:22px;top:6px;z-index:2;font:900 22px/1 Inter;letter-spacing:2px;color:#e4e4e4}
.wd-t{font:600 22px/1.05 Archivo,sans-serif;color:#e8e8e8}.wd-t small{display:block;margin-top:4px;font:500 12px Inter,sans-serif;color:#8d8d8d}
.wd-t sup{font-size:.55em;vertical-align:top;color:#bdbdbd}
.wd-big{font:300 clamp(64px,8vw,86px)/.9 Archivo,sans-serif;letter-spacing:-.04em;color:#e9e9e9;font-variant-numeric:tabular-nums}.wd-big sup{font-size:.34em;letter-spacing:0;color:#9d9d9d;margin-left:3px;vertical-align:top}
.wd-big em{font:500 15px Inter,sans-serif;font-style:normal;color:#9d9d9d;letter-spacing:0;margin-left:6px}
.wd-pn{position:relative;border-radius:18px;background:var(--a);color:#06100a;padding:12px 16px;box-shadow:0 0 36px -6px var(--a);display:grid;gap:8px;align-content:center;min-height:92px}
.wd-pn small{font:700 10px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase}
.wd-tl{position:relative;height:3px;background:repeating-linear-gradient(90deg,#06100a 0 4px,transparent 4px 7px);margin:10px 0 2px}
.wd-tl b{position:absolute;top:-6px;width:4px;height:15px;background:#06100a;border-radius:2px}
.wd-lb{display:flex;justify-content:space-between;font:700 10.5px Inter,sans-serif;letter-spacing:.04em}
.wd-bd{position:absolute;right:12px;top:-12px;padding:6px 12px;border-radius:10px 10px 0 0;background:var(--a);color:#06100a;font:800 14px Inter,sans-serif;box-shadow:0 0 20px -4px var(--a)}
.wd-bd.off{filter:grayscale(1) brightness(.7)}
.wd-ft{display:flex;gap:14px;align-items:center;justify-content:space-between;font:600 12.5px Inter,sans-serif;color:#cfcfcf}
.wd-ft i{display:inline-block;width:8px;height:8px;border-radius:50%%;background:var(--a);margin-right:7px;box-shadow:0 0 8px var(--a)}
.wd-cd{position:absolute;left:22px;bottom:-22px;display:flex;gap:6px;z-index:3}
.wd-cd button{width:18px;height:18px;border-radius:50%%;border:2px solid rgba(255,255,255,.7);cursor:pointer;padding:0}
.wd-cd button.on{box-shadow:0 0 0 3px rgba(255,255,255,.35)}
.wd-cd button[data-k=g]{background:#35ff4a}.wd-cd button[data-k=y]{background:#e8ff1a}.wd-cd button[data-k=o]{background:#ff5a12}.wd-cd button[data-k=p]{background:#ff1f5c}.wd-cd button[data-k=b]{background:#2fb6ff}
.wd-now{position:absolute;top:-8px;width:3px;height:19px;margin-left:-1px;background:#fff;border-radius:2px;box-shadow:0 0 8px #fff;transition:left 1s}
.wd-rt{display:flex;align-items:flex-end;justify-content:space-between;gap:10px}.wd-rt b{font:300 clamp(46px,6vw,64px)/.9 Archivo,sans-serif;letter-spacing:-.03em}.wd-rt small{display:block;font:500 12px Inter,sans-serif;color:#8d8d8d;margin-top:4px}
.wd-pl{align-self:center;color:var(--a);font-size:26px;filter:drop-shadow(0 0 8px var(--a));animation:wdhop 2.2s ease-in-out infinite}
@keyframes wdhop{50%%{transform:translateX(10px)}}
.wd-bar{display:flex;gap:6px;flex-wrap:wrap}.wd-btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 16px;border-radius:99px;font:800 13px Inter,sans-serif;color:#eee;
  background:radial-gradient(120%% 120%% at 30%% 20%%,#444,#151515);box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 8px 14px rgba(0,0,0,.5);text-decoration:none}
.wd-btn.a{background:var(--a);color:#06100a;box-shadow:0 0 22px -6px var(--a)}
.wd-star{font-size:26px;color:#06100a;letter-spacing:6px}
.wd-wave{display:flex;align-items:center;justify-content:space-between;gap:3px;height:62px}.wd-wave i{display:block;width:4px;height:20px;border-radius:2px;background:#1a0800;opacity:.85}
.wd-sc{position:relative;height:36px;background:repeating-linear-gradient(90deg,#14000a 0 2px,transparent 2px 12px);-webkit-mask:linear-gradient(transparent 0,#000 40%%);mask:linear-gradient(transparent 0,#000 40%%)}
.wd-needle{position:absolute;top:-8px;bottom:-4px;width:3px;background:#fff;left:30%%;box-shadow:0 0 10px #fff;border-radius:2px}
.wd-note{margin:30px 0 0;font-size:13px;opacity:.7}
.wd-all{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px;align-items:center}.wd-all button{min-height:40px;padding:0 16px;border-radius:99px;border:0;background:#0b1213;color:#fff;font:700 13px Inter,sans-serif;cursor:pointer}
@media(max-width:560px){.wd-big{font-size:64px}}""" % m)
    dots = '<div class="wd-cd">' + "".join(f'<button type="button" data-k="{k}" aria-label="{n}"></button>' for k, n in (("g", "Green"), ("y", "Yellow"), ("o", "Orange"), ("p", "Pink"), ("b", "Blue"))) + '</div>'
    def card(c, inner): return f'<article class="wd" data-c="{c}"><div class="wd-bg"></div><span class="wd-dots">&bull;&bull;&bull;</span><div class="wd-in">{inner}</div>{dots}</article>'
    c1 = card("g", '<div class="wd-t"><span id="wd-day">Monday</span></div><div class="wd-big" id="wd-time">00:00</div>'
              '<div class="wd-pn"><span class="wd-bd" id="wd-st">OPEN</span><small>Office hours</small><div class="wd-tl"><b style="left:0"></b><b style="left:calc(100% - 4px)"></b><b id="wd-now" class="wd-now" style="left:0;background:#fff"></b></div><div class="wd-lb"><span>9 AM</span><span>MON &ndash; SAT</span><span>8 PM</span></div></div>'
              '<div class="wd-ft"><span><i></i>Blue Area, Islamabad</span><span>Mon&ndash;Sat</span></div>')
    c2 = card("g", '<div class="wd-t">Visit visa<small id="wd-ctry">Thailand visit visa</small></div><div class="wd-rt"><div><b>ISB</b><small>Islamabad</small></div><span class="wd-pl">&#9992;</span><div style="text-align:right"><b id="wd-code">HKT</b><small id="wd-city">Phuket</small></div></div>'
              '<div class="wd-pn"><small>How it starts</small><div class="wd-tl"><b style="left:0"></b><b style="left:50%"></b><b style="left:calc(100% - 4px)"></b></div><div class="wd-lb"><span>DOCUMENTS</span><span>CHECK</span><span>FILE</span></div></div>'
              '<div class="wd-ft"><span><i></i>Send on WhatsApp</span><span>Free check</span></div>')
    c3 = card("y", '<div class="wd-t">Visa guides<small>From Blue Area, Islamabad</small></div><div class="wd-big"><span id="wd-88">0</span><em>country guides</em></div>'
              '<div class="wd-pn"><small>What we do</small><div class="wd-tl"><b style="left:0"></b><b style="left:50%"></b><b style="left:calc(100% - 4px)"></b></div><div class="wd-lb"><span>ASIA FIRST</span><span>EUROPE</span><span>UK &middot; USA</span></div></div>'
              '<div class="wd-ft"><span><i></i>13 regions</span><span>Updated guides</span></div>')
    c4 = card("y", '<div class="wd-t">Google reviews<small>AL ARBAB TRAVEL AND TOURS</small></div><div class="wd-big"><span id="wd-50">0.0</span><em>16 reviews</em></div>'
              '<div class="wd-pn" style="justify-items:center"><small>Rating on Google</small><div class="wd-star">&#9733;&#9733;&#9733;&#9733;&#9733;</div></div>'
              '<div class="wd-ft"><span><i></i>Read the reviews</span><span>Google Maps</span></div>')
    c5 = card("o", '<div class="wd-t">WhatsApp<small>Send your documents here</small></div><div class="wd-big" style="font-size:clamp(38px,5vw,52px)">0315 2323811</div>'
              '<div class="wd-pn"><small>Message us</small><div class="wd-wave"></div></div>'
              '<div class="wd-bar"><a class="wd-btn a" href="#">Open WhatsApp</a><a class="wd-btn" href="#">Call now</a></div>')
    c6 = card("p", '<div class="wd-t">Call the office<small>Landline</small></div><div class="wd-big" style="font-size:clamp(40px,5.2vw,56px)">051 2000066</div>'
              '<div class="wd-pn"><small>Mon &ndash; Sat &middot; 9 AM &ndash; 8 PM</small><div class="wd-sc"><span class="wd-needle"></span></div></div>'
              '<div class="wd-bar"><a class="wd-btn a" href="#">Call</a><a class="wd-btn" href="#">Email</a><a class="wd-btn" href="#">Directions</a></div>')
    allbar = '<div class="wd-all"><b>Try a colour on all cards:</b>' + "".join(f'<button type="button" data-all="{k}">{n}</button>' for k, n in (("g", "Green"), ("y", "Yellow"), ("o", "Orange"), ("p", "Pink"), ("b", "Blue"))) + '</div>'
    content = f"""<section class="sec" id="wd-root"><div class="head"><div><h2>Dark neon widget cards</h2></div><p class="lead">Your reference, with our own content: office hours with a live clock, the visa route that cycles through countries, the number of guides, Google rating, WhatsApp and phone. The clock, the open or closed status and the numbers are live. Each card has colour dots, so you can try green, yellow, orange, pink or blue. Nothing is live on the site.</p></div>{allbar}<div class="wd-g">{c1}{c2}{c3}{c4}{c5}{c6}</div><p class="wd-note">Preview only. The plane animation is gone from this idea.</p></section>"""
    ph = pagehead("Preview", "Neon widget cards", "Your reference widgets filled with the agency's own content. Tell me the colours and where they should go.")
    body = shell("/preview-widgets", [("Home", "/"), ("Widget preview", None)], ph, content)
    page("/preview-widgets", "Neon widgets | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-widgets"]
    h = h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-widgets"] = (h, pr, True)

WIDGETSLIME_PREVIEWS = True   # /preview-widgets-lime: eight widget designs in lime on black, different shapes (noindex, not in the sitemap, not in the zip)

def widgetslime_previews():
    if not WIDGETSLIME_PREVIEWS:
        return
    from urllib.parse import quote
    js = open(os.path.join(ROOT, "assets", "widgets-lime.js"), encoding="utf-8").read()
    def svgmask(path, vb="0 0 340 330"):
        return 'url("data:image/svg+xml,' + quote(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{vb}' preserveAspectRatio='none'><path d='{path}'/></svg>") + '")'
    notch = svgmask("M30,0 H196 Q214,0 214,18 V28 Q214,46 232,46 H310 Q340,46 340,76 V300 Q340,330 310,330 H30 Q0,330 0,300 V30 Q0,0 30,0Z")
    tab = svgmask("M30,46 H110 Q128,46 128,28 V18 Q128,0 146,0 H310 Q340,0 340,30 V300 Q340,330 310,330 H30 Q0,330 0,300 V76 Q0,46 30,46Z")
    css = ("""@property --p{syntax:"<number>";inherits:false;initial-value:0}#lm-root{--notch:%s;--tab:%s}
.lm-g{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%%),1fr));gap:22px;background:#6b6d70;padding:24px;border-radius:24px;grid-auto-flow:dense}
.lmc{--a:#d9ff00;position:relative;min-height:320px;color:#ececec;font-family:Archivo,Inter,sans-serif}
.lmc .bg{position:absolute;inset:0;background:linear-gradient(160deg,#181818,#000 55%%);filter:drop-shadow(0 18px 18px rgba(0,0,0,.5))}
.lmc .in{position:relative;z-index:1;padding:20px 22px 16px;display:grid;gap:12px;min-height:320px;grid-template-rows:auto auto 1fr auto}
.lmc.s-notch .bg{-webkit-mask:var(--notch) center/100%% 100%% no-repeat;mask:var(--notch) center/100%% 100%% no-repeat}
.lmc.s-tab .bg{-webkit-mask:var(--tab) center/100%% 100%% no-repeat;mask:var(--tab) center/100%% 100%% no-repeat}.lmc.s-tab .in{padding-top:30px}
.lmc.s-pill{grid-column:span 2;min-height:150px;align-self:start}.lmc.s-pill .bg{border-radius:999px}.lmc.s-pill .in{min-height:150px;display:flex;align-items:center;gap:24px;padding:18px 34px;flex-wrap:wrap}
.lmc.s-circle{min-height:320px}.lmc.s-circle .bg{border-radius:50%%}.lmc.s-circle .in{min-height:320px;place-items:center;text-align:center;align-content:center}
.lmc.s-tall .bg{border-radius:36px 36px 120px 36px}
.lmc.s-chamfer .bg{clip-path:polygon(0 0,calc(100%% - 44px) 0,100%% 44px,100%% 100%%,44px 100%%,0 calc(100%% - 44px))}
.lmc.s-squircle .bg{border-radius:42%% / 34%%}.lmc.s-squircle .in{padding:30px 34px}
.lmc.s-leaf .bg{border-radius:100px 14px 100px 14px}.lmc.s-leaf .in{padding:26px 34px}
.t{font:600 21px/1.05 Archivo,sans-serif;color:#e8e8e8}.t small{display:block;margin-top:4px;font:500 12px Inter,sans-serif;color:#8d8d8d}
.big{font:300 clamp(60px,7.4vw,82px)/.9 Archivo,sans-serif;letter-spacing:-.04em;color:#e9e9e9;font-variant-numeric:tabular-nums}.big sup{font-size:.34em;letter-spacing:0;color:#9d9d9d;margin-left:3px;vertical-align:top}
.big em{font:500 14px Inter,sans-serif;font-style:normal;color:#9d9d9d;letter-spacing:0;margin-left:6px}
.pn{position:relative;border-radius:18px;background:var(--a);color:#0a0d00;padding:12px 16px;box-shadow:0 0 34px -8px var(--a);display:grid;gap:8px;align-content:center;min-height:86px}
.pn small{font:700 10px Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase}
.tl{position:relative;height:3px;background:repeating-linear-gradient(90deg,#0a0d00 0 4px,transparent 4px 7px);margin:10px 0 2px}.tl b{position:absolute;top:-6px;width:4px;height:15px;background:#0a0d00;border-radius:2px}
.lb{display:flex;justify-content:space-between;font:700 10.5px Inter,sans-serif;letter-spacing:.04em}
.bd{position:absolute;right:12px;top:-12px;padding:6px 12px;border-radius:10px 10px 0 0;background:var(--a);color:#0a0d00;font:800 13px Inter,sans-serif;box-shadow:0 0 18px -4px var(--a)}.bd.off{filter:grayscale(1) brightness(.7)}
.lm-now{position:absolute;top:-8px;width:3px;height:19px;margin-left:-1px;background:#fff;border-radius:2px;box-shadow:0 0 8px #fff}
.ft{display:flex;gap:14px;align-items:center;justify-content:space-between;font:600 12.5px Inter,sans-serif;color:#cfcfcf}.ft i{display:inline-block;width:8px;height:8px;border-radius:50%%;background:var(--a);margin-right:7px;box-shadow:0 0 8px var(--a)}
.dots{position:absolute;right:22px;top:6px;z-index:2;font:900 22px/1 Inter;letter-spacing:2px;color:#e4e4e4}
.rt{display:flex;align-items:flex-end;justify-content:space-between;gap:10px}.rt b{font:300 clamp(44px,5.6vw,60px)/.9 Archivo,sans-serif;letter-spacing:-.03em}.rt small{display:block;font:500 12px Inter,sans-serif;color:#8d8d8d;margin-top:4px}
.pl{align-self:center;color:var(--a);font-size:26px;filter:drop-shadow(0 0 8px var(--a));animation:lmhop 2.2s ease-in-out infinite}@keyframes lmhop{50%%{transform:translateX(10px)}}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 16px;border-radius:99px;font:800 13px Inter,sans-serif;color:#eee;background:radial-gradient(120%% 120%% at 30%% 20%%,#444,#151515);box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 8px 14px rgba(0,0,0,.5);text-decoration:none}
.btn.a{background:var(--a);color:#0a0d00;box-shadow:0 0 22px -6px var(--a)}.bar{display:flex;gap:8px;flex-wrap:wrap}
.lm-wave{display:flex;align-items:center;justify-content:space-between;gap:3px;height:58px}.lm-wave i{display:block;width:4px;height:20px;border-radius:2px;background:#0a0d00;opacity:.85}
.lm-ring{--p:0;position:relative;width:200px;height:200px;border-radius:50%%;background:conic-gradient(var(--a) calc(var(--p)*1%%),#2a2a2a 0);display:grid;place-items:center;box-shadow:0 0 40px -8px var(--a);transition:--p 1.6s}
.lm-ring::after{content:"";position:absolute;inset:14px;border-radius:50%%;background:#0b0b0b}.lm-ring span{position:relative;z-index:1;font:300 64px/1 Archivo,sans-serif;letter-spacing:-.04em;color:#eee}
.stp{display:grid;gap:0;position:relative;padding-left:22px}.stp::before{content:"";position:absolute;left:5px;top:6px;bottom:6px;width:3px;background:repeating-linear-gradient(180deg,var(--a) 0 6px,transparent 6px 10px)}
.stp li{position:relative;list-style:none;padding:7px 0;font:700 13.5px Inter,sans-serif}.stp li::before{content:"";position:absolute;left:-22px;top:11px;width:13px;height:13px;border-radius:50%%;background:var(--a);box-shadow:0 0 10px var(--a)}.stp li small{display:block;font:500 11px Inter,sans-serif;color:#8d8d8d;margin-top:2px}
.lm-tab{min-height:36px;padding:0 14px;border-radius:12px 12px 0 0;border:0;background:#1c1c1c;color:#bbb;font:800 12.5px Inter,sans-serif;cursor:pointer}.lm-tab.on{background:var(--a);color:#0a0d00}
.lm-rows{display:grid;gap:8px;background:var(--a);color:#0a0d00;padding:14px 16px;border-radius:0 14px 14px 14px;box-shadow:0 0 30px -8px var(--a);font:700 13px Inter,sans-serif}.lm-rows[hidden]{display:none}
.lm-rows span{display:flex;justify-content:space-between;border-bottom:1px dashed rgba(10,13,0,.35);padding-bottom:6px}
.sc{position:relative;height:34px;background:repeating-linear-gradient(90deg,#0a0d00 0 2px,transparent 2px 12px);-webkit-mask:linear-gradient(transparent 0,#000 40%%);mask:linear-gradient(transparent 0,#000 40%%)}.lm-needle{position:absolute;top:-8px;bottom:-4px;width:3px;background:#fff;left:30%%;box-shadow:0 0 10px #fff;border-radius:2px}
.nm{position:absolute;left:22px;bottom:-26px;font:700 11.5px Inter,sans-serif;color:#fff;opacity:.9;letter-spacing:.04em}
.note{margin:36px 0 0;font-size:13px;opacity:.7}""" % (notch, tab))
    def c(shape, name, inner): return f'<article class="lmc s-{shape}"><div class="bg"></div><span class="dots">&bull;&bull;&bull;</span><div class="in">{inner}</div><span class="nm">{name}</span></article>'
    cards = []
    cards.append(c("notch", "1 · Notch card", '<div class="t">Visa guides<small>From Blue Area, Islamabad</small></div><div class="big"><span class="lm-88">0</span><em>country guides</em></div>'
                   '<div class="pn"><small>What we do</small><div class="tl"><b style="left:0"></b><b style="left:50%"></b><b style="left:calc(100% - 4px)"></b></div><div class="lb"><span>ASIA FIRST</span><span>EUROPE</span><span>UK &middot; USA</span></div></div>'
                   '<div class="ft"><span><i></i>13 regions</span><span>Updated guides</span></div>'))
    cards.append(c("pill", "2 · Pill strip", '<div><div class="t">Office hours<small>Blue Area, Islamabad</small></div></div><div class="big lm-time" style="font-size:72px">00:00</div>'
                   '<div class="pn" style="flex:1;min-width:240px"><span class="bd lm-st">OPEN</span><small>Mon &ndash; Sat</small><div class="tl"><b style="left:0"></b><b style="left:calc(100% - 4px)"></b><b class="lm-now" style="left:0"></b></div><div class="lb"><span>9 AM</span><span>8 PM</span></div></div>'))
    cards.append(c("circle", "3 · Ring gauge", '<div class="t" style="text-align:center">Google rating<small>16 reviews</small></div><div class="lm-ring"><span class="lm-50">0.0</span></div><div class="ft" style="justify-content:center"><span><i></i>5 out of 5</span></div>'))
    cards.append(c("tall", "4 · Tall steps card", '<div class="t">How a file moves<small>Our process</small></div><ul class="stp" style="margin:0;padding-left:22px">'
                   '<li>Send documents<small>On WhatsApp</small></li><li>Free check<small>By an adviser</small></li><li>File prepared<small>Checklist complete</small></li><li>Submission<small>Guidance and follow-up</small></li><li>Embassy decides<small>We keep you informed</small></li></ul>'
                   '<div class="ft"><span><i></i>Start free</span></div>'))
    cards.append(c("chamfer", "5 · Cut-corner route", '<div class="t">Visit visa<small>Islamabad to destination</small></div><div class="rt"><div><b>ISB</b><small>Islamabad</small></div><span class="pl">&#9992;</span><div style="text-align:right"><b class="lm-code">HKT</b><small class="lm-city">Phuket</small></div></div>'
                   '<div class="pn"><small>Route</small><div class="tl"><b style="left:0"></b><b style="left:50%"></b><b style="left:calc(100% - 4px)"></b></div><div class="lb"><span>DOCUMENTS</span><span>CHECK</span><span>FILE</span></div></div>'
                   '<div class="ft"><span><i></i>Send on WhatsApp</span></div>'))
    cards.append(c("squircle", "6 · Squircle WhatsApp", '<div class="t">WhatsApp<small>Send your documents here</small></div><div class="big" style="font-size:clamp(34px,4.4vw,46px)">0315 2323811</div>'
                   '<div class="pn"><small>Message us</small><div class="lm-wave"></div></div><div class="bar"><a class="btn a" href="#">Open WhatsApp</a><a class="btn" href="#">Call</a></div>'))
    cards.append(c("tab", "7 · Folder tabs", '<div class="lm-tabs"><div style="display:flex;gap:4px"><button class="lm-tab on" type="button">Visas</button><button class="lm-tab" type="button">Flights</button><button class="lm-tab" type="button">Umrah</button></div>'
                   '<div class="lm-rows"><span>Asian visit visas<b>First</b></span><span>Europe and UK<b>Files</b></span><span>Free check<b>WhatsApp</b></span></div>'
                   '<div class="lm-rows" hidden><span>Air ticketing<b>Yes</b></span><span>Hotel booking<b>Yes</b></span><span>Flight and hotel reservation<b>For visa</b></span></div>'
                   '<div class="lm-rows" hidden><span>Umrah packages<b>2026</b></span><span>3, 4 and 5 star<b>Choose</b></span><span>Visa support<b>Included</b></span></div></div>'
                   '<div class="ft"><span><i></i>Tap a tab</span></div>'))
    cards.append(c("leaf", "8 · Leaf call card", '<div class="t">Call the office<small>Landline</small></div><div class="big" style="font-size:clamp(38px,5vw,52px)">051 2000066</div>'
                   '<div class="pn"><small>Mon &ndash; Sat &middot; 9 AM &ndash; 8 PM</small><div class="sc"><span class="lm-needle"></span></div></div>'
                   '<div class="bar"><a class="btn a" href="#">Call</a><a class="btn" href="#">Email</a></div>'))
    content = f"""<section class="sec" id="lm-root"><div class="head"><div><h2>Lime on black: eight widget designs</h2></div><p class="lead">The lime colour of your picture, on black, in eight different designs and eight different shapes: notch card, wide pill, round ring, tall card, cut corner, squircle, folder tabs and a leaf. All use our own content. The clock, OPEN or CLOSED, the destination and the numbers are live. Nothing is live on the site.</p></div><div class="lm-g">{''.join(cards)}</div><p class="note">Preview only.</p></section>"""
    ph = pagehead("Preview", "Lime widget designs", "Eight lime widget designs with different shapes. Tell me which numbers you like.")
    body = shell("/preview-widgets-lime", [("Home", "/"), ("Widget preview", None)], ph, content)
    page("/preview-widgets-lime", "Lime widgets | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-widgets-lime"]
    h = h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1).replace("</body>", f"<script>{js}</script></body>", 1)
    PAGES["/preview-widgets-lime"] = (h, pr, True)

HEROTITLE_PREVIEWS = True   # /preview-hero-title: the hero headline in the reference's charcoal + violet (noindex, not in the sitemap, not in the zip)

def herotitle_previews():
    if not HEROTITLE_PREVIEWS:
        return
    css = """.ht-g{display:grid;gap:18px}.ht-c h3{font:900 17px Archivo,sans-serif;margin:0 0 3px}.ht-c p{margin:0 0 8px;font-size:13.5px;opacity:.8;max-width:76ch}
.ht-s{position:relative;border-radius:20px;overflow:hidden;padding:46px 30px;text-align:center;border:1px solid rgba(11,18,32,.12)}
.ht-s h4{margin:0;font:400 clamp(26px,3.6vw,50px)/1.08 Inter,sans-serif;text-transform:uppercase;letter-spacing:-.01em}
.ht-s h4 em{font-style:normal}.ht-s h4::after{content:"."}
.ht-a{background:radial-gradient(60% 90% at 90% 20%,#e6dcff,transparent 65%),#efecfb}.ht-a h4{color:#23232d}.ht-a h4 em,.ht-a h4::after{color:#6a55f5}
.ht-b{background:linear-gradient(180deg,rgba(0,20,40,.25),rgba(0,20,40,.35)),url(/assets/hero/1568508432206-7541b535f84c-1000.webp) center/cover}
.ht-b h4{display:inline-block;padding:20px 34px 22px;border-radius:30px;background:rgba(246,244,255,.84);-webkit-backdrop-filter:blur(16px) saturate(140%);backdrop-filter:blur(16px) saturate(140%);color:#23232d;box-shadow:0 30px 60px -30px rgba(20,10,60,.55),inset 0 1px 0 #fff}
.ht-b h4 em,.ht-b h4::after{color:#6a55f5}
.ht-c2{background:linear-gradient(180deg,rgba(0,20,40,.4),rgba(0,20,40,.5)),url(/assets/hero/1568508432206-7541b535f84c-1000.webp) center/cover}
.ht-c2 h4{color:#fff;text-shadow:0 6px 30px rgba(0,0,0,.5)}.ht-c2 h4 em,.ht-c2 h4::after{color:#b3a6ff}"""
    t = 'Visa Consultant &amp; Travel Agency in <em>Islamabad</em>'
    items = [("A · Exactly the reference", "Lavender page, charcoal letters, one violet word and a violet full stop. This is how it looks on a plain light panel.", "ht-a"),
             ("B · On the photo, in a frosted lavender panel (applied)", "Same colours, put on the Thailand photo inside a soft lavender glass panel so the charcoal letters stay easy to read.", "ht-b"),
             ("C · White on the photo, light violet word", "The same idea for a dark photo: white thin letters with the violet word brightened.", "ht-c2")]
    cards = "".join(f'<article class="ht-c"><h3>{n}</h3><p>{d}</p><div class="ht-s {c}"><h4>{t}</h4></div></article>' for n, d, c in items)
    content = f"""<section class="sec"><div class="head"><div><h2>Hero headline colours</h2></div><p class="lead">The colours of your reference (charcoal letters, one violet word, violet full stop) tried on our headline. It is still the real H1, only the style changes. Nothing else changes.</p></div><div class="ht-g">{cards}</div></section>"""
    ph = pagehead("Preview", "Hero headline colours", "Charcoal and violet on the hero title, three ways.")
    body = shell("/preview-hero-title", [("Home", "/"), ("Hero preview", None)], ph, content)
    page("/preview-hero-title", "Hero headline colours | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
    h, pr, noi = PAGES["/preview-hero-title"]
    PAGES["/preview-hero-title"] = (h.replace("</head>", f"<style>{' '.join(css.split())}</style></head>", 1), pr, True)

CARDS_PREVIEW = False   # /preview-cards-*: colour options for the destination cards (noindex, not in the sitemap, not in the zip); set False to drop them
CARD_SETS = [("green", "Green", "Fresh green. Matches the AL ARBAB brand green."), ("blue", "Blue", "Sky blue. Calm, clean, travel-like."),
             ("orange", "Orange", "Warm orange. Strongest call to action."), ("mix", "Mix", "Each card takes the next colour: green, blue, orange, pink.")]

def cards_preview():
    """Four noindex pages that show the real destination cards in light pastel-gradient colour options. Nothing on the live pages changes."""
    if not CARDS_PREVIEW:
        return
    css = re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "card-previews.css"), encoding="utf-8").read(), flags=re.S)
    css = " ".join(css.split())
    regs = regions_ordered()[:8]
    pri = asian_priority()[:4]
    for key, label, note in CARD_SETS:
        cur = ' aria-current="page"'
        bar = '<nav class="pvbar" aria-label="Colour previews"><span>Card colour preview:</span>' + "".join(
            f'<a href="/preview-cards-{k}"{cur if k == key else ""}>{l}</a>' for k, l, _ in CARD_SETS) + '<a href="/countries">Current cards (live)</a></nav>'
        pri_cards = "".join(ncard(c["url"], c["img"], f'{c["name"]} - {(c["popularPlaces"] or ["visit visa"])[0]}', "Visit visa processing", "Visa guide →",
                                  flag(c["code"], "", 40), c["name"], ", ".join(c["popularPlaces"][:2]) or "Visit visa",
                                  "How you apply", ROUTE_SHORT.get(visa_route(c), visa_route(c)), "First check", "Free", c["code"]) for c in pri)
        content = (f'<div class="pv pv-{key}"><section class="sec"><div class="head"><div><h2>Asian countries: {label}</h2></div><p class="lead">{note} This is a preview only; the live site still shows the old cards.</p></div>'
                   f'<div class="rgrid">{pri_cards}</div></section>'
                   f'<section class="sec"><div class="head"><div><h2>Regions: {label}</h2></div></div><div class="rgrid">{"".join(region_card(r) for r in regs)}</div></section></div>')
        ph = pagehead("Preview", f"Card colours: {label}", "Pick the one you like and tell me. Nothing here is live.")
        body = bar + shell(f"/preview-cards-{key}", [("Home", "/"), ("Card preview", None)], ph, content)
        url = f"/preview-cards-{key}"
        page(url, f"Card colour preview {label} | AL ARBAB", "Preview only.", body, noindex=True, priority="0.1")
        h, pr, noi = PAGES[url]
        PAGES[url] = (h.replace("</head>", f"<style>{css}</style></head>", 1), pr, True)

COLORS_PREVIEW = True   # /preview-colors*: page background colour options with a switcher (noindex, not in the sitemap, not in the zip); set False to drop them
# each theme only replaces the page colours (outer background, shell, panels, cards); text and buttons stay as they are
THEMES = [("m-milk", "Milk white", {"--bg": "#FFFFFF", "--panel": "#F4F6F5", "--shell": "#FFFFFF", "--card": "#F7F9F8", "--soft": "#E6ECEA"}),
          ("m-off", "Off-white", {"--bg": "#F3F1EC", "--panel": "#F7F5F0", "--shell": "#FFFFFF", "--card": "#f6fbfb", "--soft": "#E9E5DC"}),
          ("m-pearl", "Pearl", {"--bg": "#ECEFF1", "--panel": "#F2F5F6", "--shell": "#FAFBFB", "--card": "#F8FAFA", "--soft": "#DCE3E6"}),
          ("m-cream", "Cream", {"--bg": "#F5EEDF", "--panel": "#FAF4E8", "--shell": "#FFFDF8", "--card": "#FDF9F0", "--soft": "#EADFC8"}),
          ("m-mint", "Milk + Mint", {"--bg": "#E4F0EA", "--panel": "#EEF6F2", "--shell": "#FAFEFC", "--card": "#F6FBF8", "--soft": "#CFE3D9"}),
          ("m-sky", "Milk + Sky", {"--bg": "#E3EDF5", "--panel": "#EEF4F9", "--shell": "#FBFDFF", "--card": "#F6FAFD", "--soft": "#CFDEEA"}),
          ("m-glass", "Milky glass", {"--bg": "radial-gradient(60% 50% at 8% 8%,#e4f6f5 0,transparent 62%),radial-gradient(55% 50% at 92% 14%,#e8f6f5 0,transparent 62%),radial-gradient(62% 56% at 70% 97%,#fde9df 0,transparent 62%),radial-gradient(50% 45% at 4% 90%,#fbe3ea 0,transparent 60%),#f6fbfb", "--panel": "rgba(255,255,255,.62)", "--shell": "rgba(255,255,255,.55)", "--card": "rgba(255,255,255,.72)", "--soft": "rgba(255,255,255,.6)", "--g": "1"}),
          ("sage", "Sage (old)", {"--bg": "#A0B1AE", "--panel": "#DCE5E2", "--shell": "#f1f5f4", "--card": "#E9EFED", "--soft": "#B8CCC8"}),
          ("sky", "Sky", {"--bg": "#9FBAD0", "--panel": "#DDE9F2", "--shell": "#F2F7FA", "--card": "#EAF1F6", "--soft": "#BCD2E2"}),
          ("mint", "Mint", {"--bg": "#8FC4A8", "--panel": "#D8EDE2", "--shell": "#F0F8F4", "--card": "#E4F2EA", "--soft": "#B0D7C1"}),
          ("sand", "Sand", {"--bg": "#CDBFA8", "--panel": "#EFE7DA", "--shell": "#FAF6EF", "--card": "#F3ECE0", "--soft": "#DCCFB9"}),
          ("blush", "Blush", {"--bg": "#D4B3BB", "--panel": "#F3E3E6", "--shell": "#FBF5F6", "--card": "#F6EAEC", "--soft": "#E3C8CE"}),
          ("lilac", "Lilac", {"--bg": "#B3AED0", "--panel": "#E6E3F2", "--shell": "#F6F5FB", "--card": "#EEECF6", "--soft": "#CBC6E2"}),
          ("slate", "Slate", {"--bg": "#B4BCC6", "--panel": "#E3E7EC", "--shell": "#F4F6F8", "--card": "#ECEFF3", "--soft": "#CBD2DA"}),
          ("g-aurora", "Glass Aurora", {"--bg": "radial-gradient(60% 52% at 12% 8%,#7fe3a2 0,transparent 62%),radial-gradient(55% 50% at 92% 14%,#80d0ff 0,transparent 62%),radial-gradient(62% 56% at 72% 96%,#ff9f7a 0,transparent 62%),radial-gradient(50% 45% at 6% 92%,#ffd1dc 0,transparent 60%),#a9cfc2", "--panel": "rgba(255,255,255,.34)", "--shell": "rgba(255,255,255,.3)", "--card": "rgba(255,255,255,.46)", "--soft": "rgba(255,255,255,.42)", "--g": "1"}),
          ("g-ocean", "Glass Ocean", {"--bg": "radial-gradient(60% 52% at 10% 10%,#7cc4ff 0,transparent 62%),radial-gradient(58% 52% at 94% 20%,#b9a6ff 0,transparent 62%),radial-gradient(60% 56% at 60% 97%,#6fe0d0 0,transparent 62%),#a7c2e6", "--panel": "rgba(255,255,255,.34)", "--shell": "rgba(255,255,255,.3)", "--card": "rgba(255,255,255,.46)", "--soft": "rgba(255,255,255,.42)", "--g": "1"}),
          ("g-sunset", "Glass Sunset", {"--bg": "radial-gradient(60% 52% at 10% 8%,#ffb48a 0,transparent 62%),radial-gradient(56% 52% at 92% 16%,#ff9bb0 0,transparent 62%),radial-gradient(62% 56% at 70% 97%,#c9a8ff 0,transparent 62%),#e8bfae", "--panel": "rgba(255,255,255,.34)", "--shell": "rgba(255,255,255,.3)", "--card": "rgba(255,255,255,.46)", "--soft": "rgba(255,255,255,.42)", "--g": "1"}),
          ("g-brand", "Glass Brand", {"--bg": "radial-gradient(58% 50% at 14% 10%,#5fd48a 0,transparent 62%),radial-gradient(56% 50% at 90% 18%,#2fd1b0 0,transparent 62%),radial-gradient(60% 55% at 60% 97%,#f2b84b 0,transparent 62%),#9cc7b4", "--panel": "rgba(255,255,255,.34)", "--shell": "rgba(255,255,255,.3)", "--card": "rgba(255,255,255,.46)", "--soft": "rgba(255,255,255,.42)", "--g": "1"}),
          ("g-silk", "Silk Violet", {"--bg": "radial-gradient(46% 20% at 52% 80%,rgba(112,140,236,.55),transparent 72%),linear-gradient(162deg,transparent 50%,#cfc8f4 53%,#bdb6ee 100%),linear-gradient(104deg,transparent 35%,rgba(214,184,252,.9) 41%,rgba(196,164,250,.95) 58%,transparent 64%),linear-gradient(118deg,#a29bf0 0%,#b9a6f5 100%)", "--panel": "rgba(255,255,255,.36)", "--shell": "rgba(255,255,255,.32)", "--card": "rgba(255,255,255,.5)", "--soft": "rgba(255,255,255,.44)", "--g": "1"}),
          ("g-silk-blue", "Silk Blue", {"--bg": "radial-gradient(46% 20% at 52% 80%,rgba(86,130,226,.5),transparent 72%),linear-gradient(162deg,transparent 50%,#cbdcf6 53%,#b6cdf0 100%),linear-gradient(104deg,transparent 35%,rgba(190,214,252,.9) 41%,rgba(168,198,250,.95) 58%,transparent 64%),linear-gradient(118deg,#8fb4f0 0%,#a8c3f6 100%)", "--panel": "rgba(255,255,255,.36)", "--shell": "rgba(255,255,255,.32)", "--card": "rgba(255,255,255,.5)", "--soft": "rgba(255,255,255,.44)", "--g": "1"}),
          ("g-silk-rose", "Silk Rose", {"--bg": "radial-gradient(46% 20% at 52% 80%,rgba(226,126,164,.45),transparent 72%),linear-gradient(162deg,transparent 50%,#f8d6de 53%,#f0c0cc 100%),linear-gradient(104deg,transparent 35%,rgba(252,214,226,.9) 41%,rgba(248,190,208,.95) 58%,transparent 64%),linear-gradient(118deg,#eba8c4 0%,#f4bcc8 100%)", "--panel": "rgba(255,255,255,.36)", "--shell": "rgba(255,255,255,.32)", "--card": "rgba(255,255,255,.5)", "--soft": "rgba(255,255,255,.44)", "--g": "1"}),
          ("g-silk-mint", "Silk Mint", {"--bg": "radial-gradient(46% 20% at 52% 80%,rgba(60,170,140,.45),transparent 72%),linear-gradient(162deg,transparent 50%,#c6eedd 53%,#b0e2cb 100%),linear-gradient(104deg,transparent 35%,rgba(190,242,220,.9) 41%,rgba(166,232,206,.95) 58%,transparent 64%),linear-gradient(118deg,#7fd2b4 0%,#9fe0c4 100%)", "--panel": "rgba(255,255,255,.36)", "--shell": "rgba(255,255,255,.32)", "--card": "rgba(255,255,255,.5)", "--soft": "rgba(255,255,255,.44)", "--g": "1"})]
THEME_JS = r"""(function(){var T=__T__,F=__F__,r=document.documentElement,bs=document.querySelectorAll('.tpbar button[data-t]'),fs=document.querySelectorAll('.tpbar button[data-f]');
function set(k){var t=T[k]||T['m-glass'];for(var v in t)r.style.setProperty(v,t[v]);r.style.setProperty('--bgfx',t['--bg']);r.classList.toggle('tpglass',t['--g']==='1');bs.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.t===k?'true':'false')});try{localStorage.setItem('pvTheme',k)}catch(e){}}
function setF(k){F.forEach(function(f){r.classList.remove('tpf-'+f)});if(k!=='black')r.classList.add('tpf-'+k);fs.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.f===k?'true':'false')});try{localStorage.setItem('pvFooter',k)}catch(e){}}
var q=(location.search.match(/[?&]t=([\w-]+)/)||[])[1],qf=(location.search.match(/[?&]f=([\w-]+)/)||[])[1],s='',sf='';try{s=localStorage.getItem('pvTheme')||'';sf=localStorage.getItem('pvFooter')||''}catch(e){}
var tg=document.querySelector('.tptoggle'),gr=document.getElementById('tpgroups');tg.addEventListener('click',function(){var o=tg.getAttribute('aria-expanded')==='true';tg.setAttribute('aria-expanded',o?'false':'true');gr.hidden=o;tg.innerHTML=o?'Show options &#9660;':'Hide options &#9650;'});set(q||s||'m-glass');setF(qf||sf||'black');bs.forEach(function(b){b.addEventListener('click',function(){set(b.dataset.t)})});fs.forEach(function(b){b.addEventListener('click',function(){setF(b.dataset.f)})});})();"""

FOOTERS = [("black", "Black (current)", "#0a0f0e"), ("green", "Deep green", "#14352c"), ("navy", "Navy", "#14213d"), ("teal", "Teal", "#0f4a46"),
           ("milky", "Milky glass", "#ffffff"), ("mint", "Soft mint", "#d9eee4")]

def colors_preview():
    """Copies of three live pages with a colour switcher bar, so the owner can click through page-colour options. The real pages are untouched."""
    if not COLORS_PREVIEW:
        return
    css = " ".join(re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets", "theme-preview.css"), encoding="utf-8").read(), flags=re.S).split())
    pages = [("/", "/preview-colors", "Home"), ("/countries", "/preview-colors-countries", "Destinations"), ("/packages", "/preview-colors-packages", "Packages")]
    tmap = {k: v for k, _, v in THEMES}
    cur = ' aria-current="page"'
    for src, dst, _ in pages:
        h, _, _ = PAGES[src]
        def _grp(label, test):
            return f'<div class="grp"><b>{label}</b>' + "".join(f'<button type="button" data-t="{k}" aria-pressed="false"><i style="background:{v["--bg"]}"></i>{n}</button>' for k, n, v in THEMES if test(k)) + '</div>'
        fsw = '<div class="grp"><b>Footer:</b>' + "".join(f'<button type="button" data-f="{k}" aria-pressed="false"><i style="background:{c}"></i>{n}</button>' for k, n, c in FOOTERS) + '</div>'
        sw = fsw + _grp("Milky:", lambda k: k.startswith("m-")) + _grp("Colours:", lambda k: k[:2] not in ("m-", "g-")) + _grp("Glass:", lambda k: k.startswith("g-"))
        nav = "".join(f'<a href="{d}"{cur if d == dst else ""}>{n}</a>' for _, d, n in pages)
        bar = f'<nav class="tpbar" aria-label="Colour preview"><button type="button" class="tptoggle" aria-expanded="true" aria-controls="tpgroups">Hide options &#9650;</button><div id="tpgroups" class="tpgroups">{sw}<div class="grp"><b>Page:</b>{nav}</div></div></nav>'
        h = h.replace("<body>", "<body>" + bar, 1)
        h = h.replace("</body>", "<script>" + THEME_JS.replace("__T__", json.dumps(tmap)).replace("__F__", json.dumps([k for k, _, _ in FOOTERS if k != "black"])) + "</script></body>", 1)
        h = re.sub(r"<title>.*?</title>", "<title>Page colour preview | AL ARBAB</title>", h, count=1, flags=re.S)
        h = h.replace(f'<link rel="canonical" href="{BASE}{src}">', f'<link rel="canonical" href="{BASE}{dst}">')
        h = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,nofollow">', h, count=1)
        h = h.replace("</head>", f"<style>{css}</style></head>", 1)
        PAGES[dst] = (h, "0.1", True)

def build_countries_hub():
    pri, rest, t2 = asian_priority(), asian_rest(), tier2_countries()
    tiles = lambda cs: "".join(tile(c) for c in cs)
    # tier 2 grouped by region (Asian regions excluded), Pakistan (visa for visitors) last
    t2_groups = ""
    for r in regions_ordered():
        if r["slug"] in ASIAN_REGIONS:
            continue
        cs = [c for c in t2 if c["region"] == r["slug"]]
        if cs:
            t2_groups += f'<div data-group="{r["slug"]}" style="margin-top:22px"><h3 class="hub-h3"><a href="/countries/{r["slug"]}">{e(r["name"])}</a></h3><div class="tiles">{tiles(cs)}</div></div>'
    other = [c for c in t2 if c["region"] in ASIAN_REGIONS]
    if other:
        t2_groups += f'<div data-group="other" style="margin-top:22px"><h3 class="hub-h3">Visa for visitors to Pakistan</h3><div class="tiles">{tiles(other)}</div></div>'
    main_links = "".join(f'<a href="/countries/{s}">{e(n)}</a>' for s, n in TIER2_MAIN)
    content = f'''<section class="sec reveal"><div class="head"><div><h2>Find your country</h2></div><p class="lead">Type a country name to jump straight to its visa requirements.</p></div>
<div class="finder"><label for="finder" class="sr">Search countries</label><input id="finder" type="search" placeholder="Search {len(COUNTRIES)} country guides — e.g. Thailand, Japan, Germany" autocomplete="off"><output id="finderCount" for="finder"></output></div></section>
<section class="sec reveal" id="asia"><div class="head"><div><h2>{e(TIER1_NAME)}</h2></div><p class="lead">We process and follow up visit visas for these countries. Priority destinations first. Final decision rests with the embassy.</p></div>
<div data-group="asia-priority"><div class="tiles">{tiles(pri)}</div></div>
<div data-group="asia-more" style="margin-top:22px"><h3 class="hub-h3">More Asian countries</h3><div class="tiles">{tiles(rest)}</div></div></section>
<section class="sec reveal" id="guidance"><div class="head"><div><h2>{e(TIER2_NAME)}</h2></div><p class="lead">We prepare and organise your file and guide you through the embassy or visa centre submission. We do not guarantee approval. The embassy or consulate makes the final decision.</p></div>
<div class="chipsrow">{main_links}</div>{t2_groups}</section>
{sec("Destinations by region", "Asian regions first, then Europe, the UK, the USA, Canada, Australia and others.", f'<div class="rgrid">{"".join(region_card(r) for r in regions_ordered())}</div>')}
<section class="sec reveal"><div class="prose"><h2>Visa support for global destinations from Islamabad</h2><p>{NAME} is a visa consultancy in Islamabad with {len(COUNTRIES)} country guides. We work in two ways: we process and follow up visit visas for Asian countries, and we prepare files and guide you for Europe, the UK, the USA, Canada, Australia and other countries.</p>
<div class="two"><div><h3><a href="/countries/south-asia">Asia &amp; the Middle East</a></h3><p>Visit visas for {", ".join(e(c["name"]) for c in pri[:7])} and more: we process and follow up your application. Final decision rests with the embassy.</p></div>
<div><h3><a href="/countries/schengen">Schengen &amp; European visas</a></h3><p>We prepare your Schengen file for all 29 member states, including France, Germany, Italy and Spain, and guide you through the visa centre submission. The embassy makes the final decision.</p></div>
<div><h3><a href="/countries/united-states">The Americas (USA &amp; Canada)</a></h3><p>We help with the DS-160, document review and interview preparation for USA visas, and with Canada visit visa files. You attend the interview or biometrics yourself.</p></div>
<div><h3><a href="/countries/oceania">Oceania (Australia &amp; New Zealand)</a></h3><p>We prepare visitor visa files for Australia and New Zealand and guide you through the online application.</p></div></div></div></section>
{cta_band()}'''
    ph = pagehead("Destinations", "Visa support across<br>every continent", f"Asian visit visas first, then Europe, the UK, the USA, Canada, Australia and more: {len(COUNTRIES)} country guides in 13 regions, from Blue Area, Islamabad.", PGPIC["pg-dest"], alt="Amalfi Coast, Italy – Schengen visa from Pakistan", actions=WA_HERO)
    body = shell("/countries", [("Home", "/"), ("Destinations", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Destinations", "/countries")]), {"@context": "https://schema.org", "@type": "ItemList", "name": "Visa destinations",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + c["url"], "name": f'{c["name"]} visa'} for i, c in enumerate(pri + rest + t2)]}]
    page("/countries", f"Visa Destinations from Islamabad | {len(COUNTRIES)} Country Guides | AL ARBAB",
         f"Asian visit visa processing first, then file preparation for Schengen, UK, USA, Canada and Australia: documents and requirements in {len(COUNTRIES)} country guides.",
         body, ld, "visa destinations pakistan, visa requirements for pakistanis, visa consultant islamabad", priority="0.9")

def build_region(r):
    url = f"/countries/{r['slug']}"
    cs = by_rank(BY_REGION.get(r["slug"], []))
    vt = "".join(f'<a class="vt" href="{url}/visa/{v["slug"]}"><h3>{e(v["name"])}</h3><p>{e(v["heroText"])}</p><div class="meta"><span>⏱ {e(v["processingTime"])}</span></div><span class="go">View requirements &amp; fees →</span></a>' for v in r["visas"])
    reqs = "".join(f"<li>{e(x)}</li>" for x in r["generalRequirements"])
    faqs = [(f["q"], f["a"]) for f in r["faqs"]]
    cb = f'<div class="block"><h2>Select your destination country</h2><p>We handle appointments and documentation for all {len(cs)} countries listed below.</p><div class="tiles" style="margin-top:14px">{"".join(tile(c) for c in cs)}</div></div>' if cs else ""
    fb = f'<div class="block"><h2>{e(r["name"])} visa FAQs</h2>{faq_html(faqs)}</div>' if faqs else ""
    main = f'''<div class="stack">
{tier_block_region(r)}
<div class="block"><h2>Expert immigration guidance for {e(r["name"])}</h2><p>{e(r["intro"])}</p></div>
{cb}
<div class="block"><h2>Select your visa type</h2><div class="grid" style="margin-top:12px">{vt}</div></div>
<div class="block"><h2>General requirements</h2><ul class="docs">{reqs}</ul></div>
<div class="block"><h2>Application process</h2><ol class="steps">{steps_html([(s["title"], s["desc"]) for s in r["stepByStep"]])}</ol></div>
{fb}
{"" if r["slug"] not in REGION_OFFICIAL else '<div class="block"><h2>Official sources</h2><ul class="srcs">' + "".join(f'<li><a href="{u}" target="_blank" rel="noopener nofollow">{e(n)} ↗</a></li>' for n, u in REGION_OFFICIAL[r["slug"]]) + "</ul></div>"}
<div class="block"><h2>Why choose {NAME} in Islamabad?</h2><p>As a DTS-licensed visa consultant in Blue Area, Islamabad, we check your documents for free before you apply. We provide transparent, end-to-end guidance without hidden fees or false promises.</p><div class="chipsrow" style="margin-top:12px"><span>DTS Licensed Travel Agency</span><span>Free first document check</span></div></div>
</div>'''
    vlinks = "".join(f'<a href="{url}/visa/{v["slug"]}">{e(v["name"])} <span>→</span></a>' for v in r["visas"])
    others = "".join(f'<a href="/countries/{o["slug"]}">{e(o["name"])} <span>→</span></a>' for o in regions_ordered() if o["slug"] != r["slug"])
    aside = f'<aside class="aside">{ctacard(r["name"] + " visa")}<nav class="mini" aria-label="{e(r["name"])} visa types"><h3>Visa types</h3>{vlinks}</nav><nav class="mini" aria-label="Other regions"><h3>Other regions</h3>{others}</nav></aside>'
    content = f'<div class="layout">{main}{aside}</div>{cta_band()}'
    acts = f'<a class="btn wa" href="{wa("Hi, I need help with a " + r["name"] + " visa.")}" target="_blank" rel="noopener">💬 Free evaluation</a><a class="btn light" href="{url}/visa/{r["visas"][0]["slug"]}">{e(r["visas"][0]["name"])}</a>'
    ph = pagehead("Destination guide", f'{e(r["name"])} visa consultant in Islamabad', e(r["shortDesc"]) + " Apply from Blue Area, Islamabad with DTS-licensed visa consultants.", r["img"], r["flag"], r["name"], acts)
    body = shell("/countries", [("Home", "/"), ("Destinations", "/countries"), (r["name"], None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Destinations", "/countries"), (r["name"], url)]),
          service_ld(f"{r['name']} visa consultancy", r["seoDescription"], url, {"serviceType": "Visa consultancy"})]
    if faqs:
        ld.append(faq_ld(faqs))
    if cs:
        ld.append({"@context": "https://schema.org", "@type": "ItemList", "name": f"{r['name']} visa destinations",
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + c["url"], "name": f"{c['name']} visa"} for i, c in enumerate(cs)]})
    title = r["seoTitle"] + " | AL ARBAB" if len(r["seoTitle"]) <= 52 else r["seoTitle"]
    page(url, title, r["seoDescription"], body, ld, r["keywords"], image=((BASE + U(r["img"], 1200)) if r["img"].startswith("/") else U(r["img"], 1200)) if r["img"] else None, priority="0.8")
    for v in r["visas"]:
        build_region_visa(r, v)

def build_region_visa(r, v):
    url = f"/countries/{r['slug']}/visa/{v['slug']}"
    reqs = "".join(f"<li>{e(x)}</li>" for x in v["requirements"])
    tips = "".join(f"<li>{e(x)}</li>" for x in v["tips"])
    other = [o for o in r["visas"] if o["slug"] != v["slug"]]
    lname = v["name"].lower()
    cs = by_rank([c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]])
    rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{len(c["docs_clean"])} documents</td><td>{e(", ".join(c["popularPlaces"][:2]) or "—")}</td></tr>' for c in cs)
    table = (f'<div class="block"><h2>{e(r["name"])} {e(lname)}: countries we handle</h2><p>Document checklists for Pakistani passport holders across {len(cs)} {e(r["name"])} destinations. Open a country for its full list.</p>'
             f'<div style="overflow-x:auto;margin-top:12px"><table class="tbl"><thead><tr><th>Country</th><th>Checklist</th><th>Popular places</th></tr></thead><tbody>{rows}</tbody></table></div></div>') if cs else ""
    gen = "".join(f"<li>{e(x)}</li>" for x in r["generalRequirements"])
    rfaq = [(f["q"], f["a"]) for f in r["faqs"]]
    region_extra = (f'<div class="block"><h2>About {e(r["name"])} visas from Pakistan</h2><p>{e(r["intro"])}</p><h3>General requirements in {e(r["name"])}</h3><ul class="checks">{gen}</ul></div>'
                    + table
                    + f'<div class="block"><h2>{e(r["name"])} application process</h2><ol class="steps">{steps_html([(st["title"], st["desc"]) for st in r["stepByStep"]])}</ol></div>'
                    + (f'<div class="block"><h2>{e(r["name"])} {e(lname)} FAQs</h2>{faq_html(rfaq)}</div>' if rfaq else ""))
    claim = (f'<p style="margin-top:12px"><b class="claim">{e(SUCCESS_CLAIM)}</b></p><p class="note" style="margin-top:12px">{e(SUCCESS_NOTE)}</p>'
             if r["slug"] in ASIAN_REGIONS and v["slug"] == "visit-visa" else "")
    vtier = 1 if (r["slug"] in ASIAN_REGIONS and v["slug"] == "visit-visa") else 2
    main = f'''<div class="stack">
{tier_block(r["name"], vtier, lname)}
<div class="block"><h2>Expert processing for {e(r["name"])} {e(lname)}s</h2><p>{NAME} ensures your {e(lname)} application for {e(r["name"])} is meticulously prepared. We guide you through the entire process, minimizing errors and maximizing your chances of approval.</p>{claim}</div>
<div class="block"><h2>Required documents checklist</h2><ul class="docs">{reqs}</ul></div>
<div class="block"><h2>Processing time &amp; cost</h2><div class="facts" style="margin-top:0;grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Processing time</small><b>{e(v["processingTime"])}</b></div><div><small>Cost</small><b>Today's price on WhatsApp</b></div></div><p class="note" style="margin-top:12px">Embassy charges change often, so we don't publish them. Message us for the current all-in cost for your case.</p></div>
{region_extra}
<div class="block"><h2>Expert tips</h2><ul class="tips">{tips}</ul></div>
<div class="block"><h2>What we do for you</h2><div class="chipsrow"><span>Form filling &amp; error checking</span><span>Document translation &amp; attestation guidance</span><span>Appointment scheduling &amp; mock interviews</span></div></div>
</div>'''
    ol = "".join(f'<a href="/countries/{r["slug"]}/visa/{o["slug"]}">{e(o["name"])} <span>→</span></a>' for o in other)
    cl = "".join(f'<a href="{c["url"]}">{e(c["name"])} <span>→</span></a>' for c in by_rank(BY_REGION.get(r["slug"], []))[:8])
    aside = f'<aside class="aside">{ctacard(r["name"] + " " + v["name"])}<nav class="mini"><h3>{e(r["name"])}</h3><a href="/countries/{r["slug"]}">Visa guide overview <span>→</span></a>{ol}{cl}</nav></aside>'
    content = f'<div class="layout">{main}{aside}</div>' + cta_band(f"Ready to apply for your {e(v['name'])}?", "Don't risk your application with incomplete documents. Let our visa consultants in Islamabad handle your case.")
    acts = f'<a class="btn wa" href="{wa("Hi, I want to apply for a " + r["name"] + " " + v["name"] + ".")}" target="_blank" rel="noopener">💬 Start application</a>'
    ph = pagehead(f'{e(r["name"])} visas', f'{e(r["name"])} {e(v["name"])}', e(v["heroText"]), r["img"], r["flag"], r["name"], acts)
    body = shell("/countries", [("Home", "/"), ("Destinations", "/countries"), (r["name"], f"/countries/{r['slug']}"), (v["name"], None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Destinations", "/countries"), (r["name"], f"/countries/{r['slug']}"), (v["name"], url)]),
          service_ld(f"{r['name']} {v['name']}", v["seoDescription"], url, {"serviceType": v["name"]})]
    if rfaq:
        ld.append(faq_ld(rfaq))
    t = f"{r['name']} {v['name']} from Pakistan: Documents | AL ARBAB"
    if len(t) > 65:
        t = f"{r['name']} {v['name']} from Pakistan | AL ARBAB"
    page(url, t, v["seoDescription"], body, ld, v["keywords"], priority="0.6")

def build_country(c):
    r = REGIONS[c["region"]]
    vv = visit_visa(c["region"])
    docs = "".join(f"<li>{e(x)}</li>" for x in c["docs_clean"])
    grouped = "".join(f'<h3>{e(g)}</h3><ul class="docs">' + "".join(f"<li>{e(x)}</li>" for x in xs) + "</ul>" for g, xs in group_docs(c["docs_clean"]))
    checks = "".join(f"<li><b>{e(a)}</b><span>{b}</span></li>" for a, b in embassy_checks(c))
    key_docs = [d.split("(")[0].strip().rstrip(",;") for d in c["docs_clean"][:4]]
    _voa = visa_route(c).startswith("Visa on arrival")
    pp = proc_phrase(vv)
    if c.get("lead"):
        lead_txt = c["lead"] + " "
    elif _voa:
        lead_txt = f"Pakistani passport holders can get a visa on arrival in {c['name']} if they meet the entry conditions; some travellers apply online in advance. {pp[0].upper()}{pp[1:]}. "
    else:
        lead_txt = f"Pakistani passport holders need a visa for {c['name']}. You apply through {ROUTE_PHRASE.get(visa_route(c), visa_route(c).lower())}, and {pp}. "
    tier = tier_of(c)
    we_do = (f"{NAME} processes and follows up your {c['name']} visit visa from Blue Area, Islamabad" if tier == 1 else
             f"{NAME} prepares and organises your {c['name']} visa file from Blue Area, Islamabad and guides you through the submission")
    quick = e(lead_txt + f"The checklist has {len(c['docs_clean'])} documents, including {', '.join(key_docs[:-1]).lower()} and {key_docs[-1].lower()}. ") + \
            f'{e(we_do)}; <a class="link" href="{wa("Hi, I need help with a " + c["name"] + " visa.")}" target="_blank" rel="noopener">start with a free WhatsApp check</a>. Final decision rests with the embassy.'

    common = {}
    for _o in BY_REGION.get(c["region"], []):
        for _d in _o["docs_clean"]:
            common[_d.lower()] = common.get(_d.lower(), 0) + 1
    _n = max(1, len(BY_REGION.get(c["region"], [])))
    only_here = [d for d in c["docs_clean"] if common.get(d.lower(), 0) <= max(1, _n // 4)]
    only_here = [] if c.get("official_only") else only_here
    only_block = (f'<div class="block" id="specific"><h2>What is specific to {e(c["name"])}</h2><p>Most {e(REGIONS[c["region"]]["name"])} checklists share the basics. These items are particular to {e(c["name"])}:</p><ul class="docs">' + "".join(f"<li>{e(d)}</li>" for d in only_here[:6]) + "</ul></div>") if only_here else ""
    places = "".join(f"<span class='pl'>{e(p)}</span>" for p in c["popularPlaces"])
    gal = "".join(f'<figure>{picture(g[1], f"{g[0]}, {c["name"]}", 800, 600, "(max-width:600px) 100vw, 300px")}<figcaption class="pl">{e(g[0])}</figcaption></figure>' for g in c["gallery"])
    rest = "".join(f"<span class='pl'>{e(p)}</span>" for p in c["popularPlaces"][len(c["gallery"]):])
    if gal:
        places_block = f'<div class="block"><h2>Top places to visit in {e(c["name"])}</h2><div class="gallery">{gal}</div>{f"<div class=\"chipsrow\" style=\"margin-top:12px\">{rest}</div>" if rest else ""}</div>'
    else:
        places_block = f'<div class="block"><h2>Top places to visit in {e(c["name"])}</h2><div class="chipsrow">{places}</div></div>' if places else ""
    st = [(s["title"], s["desc"]) for s in r["stepByStep"]] if len(r["stepByStep"]) >= 3 else PROCESS
    proc = vv["processingTime"] if vv else "Embassy dependent"
    faqs = [(f"What documents do I need for {an(c['name'])} visa from Pakistan?", "The main documents are: " + "; ".join(c["docs_clean"][:6]) + ". The full checklist is on this page."),
            (f"How much does {an(c['name'])} visa cost from Pakistan?", "Embassy charges change often, so we don't publish them. Message us on WhatsApp and we confirm the current all-in cost for your case before you pay anything."),
            (f"How long does {c['name']} visa processing take?", f"{proc} Processing can take longer in peak season."),
            ((f"Can AL ARBAB TRAVEL AND TOURS apply for my {c['name']} visa from Islamabad?",
              f"Yes. We process and follow up {c['name']} visit visa applications from our Blue Area office: document checklist, file preparation, submission and follow-up. "
              f"We can also arrange flight reservations, hotel bookings and travel insurance. Message us on WhatsApp at {PHONE} for a free assessment. Final decision rests with the embassy.")
             if tier == 1 else
             (f"Can AL ARBAB TRAVEL AND TOURS help with my {c['name']} visa from Islamabad?",
              f"Yes. We prepare and organise your {c['name']} visa file, book the appointment where needed and guide you through the embassy or visa centre submission. "
              f"You attend biometrics or an interview in person where the embassy requires it. We can also arrange flight reservations, hotel bookings and travel insurance. "
              f"We do not guarantee approval; the embassy or consulate makes the final decision."))]
    faqs += COUNTRY_PAA.get(c["slug"], [])
    faqs += [tuple(x) for x in c.get("faq_extra", [])]
    route = visa_route(c)
    faqs += [(f"Is the {c['name']} visa open for Pakistani passport holders?",
              (f"Yes. We are handling {c['name']} applications for Pakistani passport holders from our Islamabad office ({re.sub(r'\s*\(.*?\)', '', route).strip().lower()}). " if tier == 1 else
               f"Yes. We prepare {c['name']} visa files for Pakistani passport holders from our Islamabad office ({re.sub(r'\s*\(.*?\)', '', route).strip().lower()}). ") +
              "Rules can change at short notice, so message us on WhatsApp to confirm the current position before you book anything.")]
    siblings = by_rank([x for x in BY_REGION[c["region"]] if x["slug"] != c["slug"] and x["region"] == c["region"]])
    srcs = OFFICIAL.get(c["slug"], []) + REGION_OFFICIAL.get(c["region"], [])
    src_block = (f'<div class="block" id="sources"><h2>Official sources</h2><p>Always confirm the latest rules on the official portal. We check every file against these requirements before submission. <a class="link" href="/editorial-policy">How we keep this page accurate →</a></p><ul class="srcs">'
                 + "".join(f'<li><a href="{u}" target="_blank" rel="noopener nofollow">{e(n)} ↗</a></li>' for n, u in srcs) + "</ul></div>") if srcs else ""
    refusal = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in REFUSAL)
    toc_items = [("service", "Our service"), ("official", "Official facts") if c.get("facts") else None, ("about", "Overview"), ("fee", "Cost & processing"), ("documents", "Documents"), ("places", "Places to visit") if places_block else None,
                 ("process", "How to apply"), ("checks", "Before you apply"), ("sources", "Official sources") if src_block else None, ("faqs", "FAQs")]
    toc = '<nav class="mini toc" aria-label="On this page"><h3>On this page</h3>' + "".join(f'<a href="#{i}">{n} <span>↓</span></a>' for i, n in filter(None, toc_items)) + "</nav>"
    places_block = places_block.replace('<div class="block">', '<div class="block" id="places">', 1)
    _fz = COUNTRY_FOCUS.get(c["slug"])
    focus_block = (f'<div class="block" id="prepare"><h2>{e(_fz[0])}</h2><p>{e(_fz[1])}</p><ul class="checks" style="margin-top:12px">' + "".join(f"<li>{x}</li>" for x in _fz[2]) + "</ul></div>") if _fz else ""
    main = f'''<div class="stack">
<div class="block answer" id="answer"><h2>{e(c["name"])} visa from Pakistan: quick answer</h2><p>{quick}</p></div>
{tier_block(c["name"], tier, note=c.get("tier_note", ""))}
{official_facts(c)}
<div class="block" id="about"><h2>{e(c["name"])} visa services in Islamabad</h2><p>{e(c["intro"])}</p></div>
{focus_block}
<div class="block" id="fee"><h2>{e(c["name"])} visa cost &amp; processing time</h2><div class="feebox" style="grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Processing time</small><b>{e(proc)}</b></div><div><small>Cost</small><b>Today's price on WhatsApp</b></div></div>
<p style="margin-top:12px">Embassy charges change with exchange rates and policy, so we don't publish them. Send us your travel dates and we confirm the current all-in cost for your case. No payment until you agree.</p>
<p style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap;align-items:center"><a class="btn wa" href="{wa("Hi, what is the total cost for a " + c["name"] + " visa?")}" target="_blank" rel="noopener">💬 Ask today's price</a><a class="link" href="/guides/visa-requirements-for-pakistani-passport">Compare {len(COUNTRIES)} country guides →</a></p></div>
{only_block}
<div class="block" id="documents"><h2>Required documents for {e(c["name"])} visa</h2>{grouped}<p class="note" style="margin-top:14px">Requirements can change; we give you an updated checklist for your exact case. <a class="link" href="/eligibility-check?d={c["slug"]}">Get your personal checklist →</a> · <a class="link" href="/guides/visa-documents-explained">What each document means →</a></p></div>
{places_block}
<div class="block" id="process"><h2>How the {e(c["name"])} application works</h2><p>Your file goes through consultation, documentation, appointment or online submission, and tracking. The full step-by-step process for {e(REGIONS[c["region"]]["name"])} visas is on the <a class="link" href="/countries/{c["region"]}">{e(REGIONS[c["region"]]["name"])} visa guide</a>.</p></div>
<div class="block" id="checks"><h2>Before you apply for the {e(c["name"])} visa</h2><p>Officers judge the same things on every file: purpose of the trip, enough funds, reasons to return and consistent documents. Read our short guides, then send your file for a free check.</p><div class="chipsrow" style="margin-top:12px"><a href="/guides/bank-statement-for-visa-from-pakistan">Bank statement rules</a><a href="/guides/visa-cover-letter-pakistan">Cover letter template</a><a href="/guides/visa-refused-what-to-do">If a visa is refused</a><a href="/guides/visa-documents-explained">Documents explained</a></div></div>
{src_block}
<div class="block" id="faqs"><h2>{e(c["name"])} visa FAQs</h2>{faq_html(faqs)}</div>
<p class="note">{REVIEWED} {NAME} is licensed by the Department of Tourist Services (DTS). We are not an embassy or government office, and no agency can guarantee a visa: the decision is made by the embassy. <a class="link" href="/disclaimer">Disclaimer</a> · <a class="link" href="/fees-and-refunds">Fees &amp; refund policy</a> · <a class="link" href="/compliance">Compliance commitment</a></p>
</div>'''
    vlinks = "".join(f'<a href="/countries/{c["region"]}/visa/{v["slug"]}">{e(r["name"])} {e(v["name"])} <span>→</span></a>' for v in r["visas"])
    sib = "".join(f'<a href="{x["url"]}">{e(x["name"])} <span>→</span></a>' for x in siblings[:10])
    sibnav = f'<nav class="mini" aria-label="Nearby countries"><h3>More in {e(r["name"])}</h3>{sib}</nav>' if sib else ""
    if c["slug"] in REGIONS and c["slug"] != c["region"]:
        sibnav = f'<nav class="mini"><h3>Full guide</h3><a href="/countries/{c["slug"]}">{e(c["name"])} visa types &amp; process <span>→</span></a></nav>' + sibnav
    aside = f'<aside class="aside">{toc}{ctacard(c["name"] + " visa")}<nav class="mini" aria-label="Related"><h3>{e(r["name"])}</h3><a href="/countries/{r["slug"]}">{e(r["name"])} overview <span>→</span></a>{vlinks}</nav>{sibnav}</aside>'
    rel = sec(f'More {e(r["name"])} destinations', "", '<div class="tiles">' + "".join(tile(x) for x in siblings[:12]) + "</div>") if siblings else ""
    facts = f'<div class="facts"><div><small>How you apply</small><b>{e(visa_route(c))}</b></div><div><small>Documents</small><b>{len(c["docs_clean"])} on the checklist</b></div><div><small>Processing</small><b>{e(proc)}</b></div><div><small>Region</small><b>{e(r["name"])}</b></div><div><small>Our service</small><b>{"Visit visa processing &amp; follow-up" if tier == 1 else "File preparation &amp; guidance"}</b></div>' + (f'<div><small>Track record</small><b>{e(SUCCESS_CLAIM)}</b></div></div><p class="note" style="margin-top:12px">{e(SUCCESS_NOTE)}</p>' if asian_claim(c) else '<div><small>First check</small><b>Free on WhatsApp</b></div></div>')
    content = f'<div class="layout">{main}{aside}</div>{rel}' + cta_band(f"Start your {e(c['name'])} journey today")
    acts = f'<a class="btn wa" href="{wa("Hi, I want to apply for a " + c["name"] + " visa.")}" target="_blank" rel="noopener">💬 Free assessment</a><a class="btn light" href="tel:{PHONE_I}">📞 {PHONE}</a>'
    ph = pagehead(f'{e(r["name"])} · Updated {UPDATED}', f'{e(c["name"])} visa from Pakistan', e(c["description"]) + f' Prepared by our visa consultants in Blue Area, Islamabad.', c["img"], c["code"], (f"{c['gallery'][0][0]}, {c['name']}" if c["gallery"] else f"{c['name']} – " + (c["popularPlaces"][0] if c["popularPlaces"] else "visa from Pakistan")), acts) + facts
    body = shell("/countries", [("Home", "/"), ("Destinations", "/countries"), (r["name"], f"/countries/{r['slug']}"), (c["name"], None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Destinations", "/countries"), (r["name"], f"/countries/{r['slug']}"), (c["name"], c["url"])]),
          service_ld(f"{c['name']} visa consultancy in Islamabad", c["description"], c["url"],
                     {"serviceType": "Visit visa processing" if tier == 1 else "Visa file preparation and guidance"}),
          faq_ld(faqs)]
    title = f"{c['name']} Visa from Pakistan: Requirements 2026 | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Requirements from Pakistan | AL ARBAB"
    if len(title) > 65:
        title = f"{c['name']} Visa Requirements | AL ARBAB"
    desc = f"{c['name']} visa from Pakistan 2026: {len(c['docs_clean'])}-document checklist, how to apply & refusal reasons. Free file check, Blue Area. WhatsApp {PHONE_D}"
    if len(desc) > 160:
        desc = f"{c['name']} visa from Pakistan 2026: {len(c['docs_clean'])} documents & how to apply. Free file check in Islamabad. WhatsApp {PHONE_D}"
    if c["slug"] in COUNTRY_SEO:
        title, desc = COUNTRY_SEO[c["slug"]][0], COUNTRY_SEO[c["slug"]][1].replace("{PHONE_D}", PHONE_D)
    page(c["url"], title, desc[:160], body, ld, c["keywords"], image=AU(c["img"], 1200) if c["img"] else None, priority="0.8" if tier == 1 else "0.7")

def pkg_widget():
    """Compact dashboard-style card on the Packages hero (after the owner's widget reference)."""
    top = PACKAGES[0]
    fl = "".join(f'<span><img src="/assets/flags/w80/{c}.png" alt="" width="40" height="40" loading="lazy" decoding="async"></span>' for c in ("th", "my", "id", "sg", "np")
                 if os.path.exists(os.path.join(ROOT, "assets", "flags", "w80", f"{c}.png")))
    ph_svg = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>'
    ck_svg = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
    return (f'<div class="pkw"><div class="pkw-top"><span class="pkw-eb">Holiday packages</span><b>{len(PACKAGES)}</b><small>packages from Islamabad</small></div>'
            f'<div class="pkw-flags">{fl}</div>'
            f'<a class="pkw-last" href="{top["url"]}"><small>Popular package</small><b>{e(top["title"])}</b><span>{e(top["duration"])}</span><em>Details &rarr;</em></a>'
            f'<div class="pkw-btns"><a class="pkw-r" href="tel:{PHONE_I}" aria-label="Call {PHONE}">{ph_svg}</a><a class="pkw-r" href="/eligibility-check" aria-label="Free eligibility check">{ck_svg}</a>'
            f'<a class="pkw-p" href="/umrah">Umrah</a><a class="pkw-p go" href="{wa("Hi, I want a holiday package quote.")}" target="_blank" rel="noopener">Get quote &rarr;</a></div></div>')

def build_packages():
    tour_cards = build_tours()
    content = f'''{sec("Tour packages by destination", "Honeymoon, family and group trips planned to your dates — flights, hotels and visa in one booking.", f'<div class="rgrid">{"".join(tour_cards)}</div><p style="margin-top:20px"><a class="btn light" href="/honeymoon-packages">Honeymoon packages</a></p>', "tours")}
{sec("Holiday packages", "All-inclusive international packages curated for Pakistani travelers — visa, flights and hotels arranged by one team.", f'<div class="grid g4">{"".join(pkg_card(p) for p in PACKAGES)}</div>')}
{sec("Can't find your trip?", "", '<div class="note">We build custom itineraries for families, honeymooners and groups. Tell us the destination, dates and budget on WhatsApp and we send a full quote with visa, flights and hotels.</div>')}
{cta_band()}'''
    ph = pagehead("Exclusive packages", "Holiday packages<br>from Islamabad", "Thailand, Malaysia, Bali, Singapore, Nepal, Dubai, Europe and Umrah — complete packages with visa support, hotels and sightseeing.", PGPIC["pg-pkg"], alt="International holiday packages from Islamabad", actions=WA_HERO)
    body = shell("/packages", [("Home", "/"), ("Packages", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Packages", "/packages")]), {"@context": "https://schema.org", "@type": "ItemList", "name": "Holiday packages",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + p["url"], "name": p["title"]} for i, p in enumerate(PACKAGES)]}]
    page("/packages", "Holiday Packages from Pakistan 2026 | AL ARBAB",
         "Thailand, Malaysia, Bali, Singapore, Nepal, Dubai, Italy & Umrah packages from Islamabad. Visa, flights & hotels in one booking. Get a WhatsApp quote.",
         body, ld, "holiday packages from pakistan, thailand tour package islamabad, dubai package pakistan, bali package pakistan", priority="0.8")
    for p in PACKAGES:
        build_package(p)

def build_package(p):
    li = "".join(f"<li>{e(x)}</li>" for x in p["highlights"])
    others = [o for o in PACKAGES if o["id"] != p["id"]]
    link = p["link"]
    stay = p["amenities"].split("|")[0].strip()
    main = f'''<div class="stack">
<div class="block"><h2>Package overview</h2><div class="facts" style="margin-top:0"><div><small>Duration</small><b>{e(p["duration"])}</b></div><div><small>Stay</small><b>{e(stay)}</b></div><div><small>Country</small><b>{e(p["country"])}</b></div></div>
<p style="margin-top:14px">{e(p["title"])} — {e(p["duration"])} with {e(p["amenities"].replace(" | ", " and "))}. Curated by {NAME} for travelers from Pakistan, with visa guidance, flights and hotels arranged by one team.</p></div>
<div class="block"><h2>Highlights</h2><ul class="checks">{li}</ul></div>
<div class="block"><h2>Visa &amp; travel documents</h2><p>We handle the visa process for this trip as part of your booking. See the full document checklist on the <a class="link" href="{link}">{e(p["country"])} page</a>.</p></div>
<div class="block"><h2>Price &amp; availability</h2><p>Prices depend on travel dates, hotel category and group size. Send your dates on WhatsApp and we reply with a complete quote. We reply during office hours.</p><p style="margin-top:14px"><a class="btn wa" href="{wa(f"Hi, please send me a quote for the {p['title']} package ({p['duration']}).")}" target="_blank" rel="noopener">💬 Get price on WhatsApp</a></p></div>
</div>'''
    ol = "".join(f'<a href="{o["url"]}">{e(o["title"])} <span>→</span></a>' for o in others[:6])
    aside = f'<aside class="aside">{ctacard(p["title"] + " package")}<nav class="mini"><h3>Other packages</h3>{ol}</nav></aside>'
    more = '<div class="grid g4">' + "".join(pkg_card(o) for o in others[:4]) + "</div>"
    content = f'<div class="layout">{main}{aside}</div>{sec("You may also like", "", more)}{cta_band()}'
    acts = f'<a class="btn wa" href="{wa(f"Hi, I am interested in the {p['title']} package.")}" target="_blank" rel="noopener">💬 Book on WhatsApp</a><a class="btn light" href="{link}">Visa requirements</a>'
    ph = pagehead(f'{p["flag"]} {e(p["country"])}', e(p["title"]), f'{e(p["duration"])} · {e(p["amenities"])}', p["img"], alt=p["title"], actions=acts)
    body = shell("/packages", [("Home", "/"), ("Packages", "/packages"), (p["title"], None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Packages", "/packages"), (p["title"], p["url"])]),
          {"@context": "https://schema.org", "@type": "TouristTrip", "name": p["title"], "description": f'{p["duration"]} — {p["amenities"]}. ' + ", ".join(p["highlights"]),
           "image": AU(p["img"], 1200), "url": BASE + p["url"], "provider": {"@id": BASE + "/#org"},
           "itinerary": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": h} for i, h in enumerate(p["highlights"])]}}]
    title = f'{p["title"]} Package | AL ARBAB'
    page(p["url"], title, f'{p["title"]}: {p["duration"]}, {p["amenities"]}. Highlights: {", ".join(p["highlights"])}. Book from Islamabad.'[:160],
         body, ld, priority="0.7", image=AU(p["img"], 1200))

def build_visa_services():
    svc = "".join(feat(ic, n, d, (f"/visa-services/{s}", "Learn more")) for s, n, ic, d, _ in VISA_SERVICES) + feat("✈", "Airline Tickets", "Air ticketing with real-time fares from major airlines.", ("/air-ticketing", "Learn more"))
    inc = "".join(f"<li>{x}</li>" for x in INCLUDED)
    content = f'''{tiers_section("tiers", "Our two visa services")}
{how_we_work()}
{sec("Visas tailored to your journey", "Whether you're visiting family, studying abroad or expanding your business — our expert team handles every detail.", f'<div class="grid g4">{svc}</div>', "services")}
<section class="sec reveal"><div class="split"><div class="prose"><h2>What's included</h2><ul class="checks">{inc}</ul><p><a class="btn" href="/contact">Start your application</a></p></div>
<div class="prose" style="align-content:center"><span class="eyebrow">First step</span><div class="big">Free</div><p>Send your documents on WhatsApp for a free first check. The embassy makes the final decision on every visa.</p></div></div></section>
{sec("Popular visa destinations", "Asian regions first, where we process and follow up your visit visa.", f'<div class="rgrid">{"".join(region_card(r) for r in regions_ordered()[:4])}</div>')}
<section class="sec reveal"><div class="prose"><h2>Expert visa consultants in Islamabad for global destinations</h2>
<p>{NAME} provides visa consultancy and travel support in Islamabad (ISB). Whether you need a visa consultant in Islamabad, are planning a European tour, or are handling a family reunification case, we guide you through a transparent application process. The embassy makes the final decision.</p>
<div class="two"><div><h3><a href="/countries#asia">Asian visit visas</a></h3><p>We process and follow up visit visas for {", ".join(e(c["name"]) for c in asian_priority()[:7])} and other Asian countries. Final decision rests with the embassy.</p></div>
<div><h3><a href="/countries/schengen">Schengen visa from Pakistan</a></h3><p>Applying for a Schengen visa in Islamabad can be complex due to stringent documentation requirements. As a Europe visa consultant in Islamabad, we specialize in tourist, business, and family visit visas for all Schengen states, including Germany, France, Italy, and Spain.</p></div>
<div><h3><a href="/countries/united-kingdom">UK visa consultant Islamabad</a></h3><p>Whether you need a Business Visa, a Standard Visitor Visa, or a Tourist Visa, our visa agents in ISB assist with UKVI requirements, financial proof compilation, and interview preparation.</p></div>
<div><h3><a href="/countries/united-states">USA visa file preparation (B1/B2)</a></h3><p>Securing a US visa requires meticulous preparation. We help with DS-160 form filling, document review and interview preparation, from B1/B2 tourist visas to business visas. You attend the interview yourself.</p></div>
<div><h3><a href="/countries/canada">Canada</a> &amp; <a href="/countries/australia">Australia</a> visas</h3><p>We prepare visitor visa files for Canada (TRV) and Australia (Subclass 600) with care and accuracy, and guide you through the online application.</p></div></div>
<h2>Why choose our visa consultancy in ISB?</h2><p>Located in Blue Area, {NAME} is a DTS-licensed travel agency and visa consultancy. We don't just fill out forms; we prepare each file around your specific profile.</p>
<div class="kw"><span>Visa agent ISB</span><span>Visa processing Islamabad</span><span>Visa documentation Islamabad</span><span>Embassy visa support Islamabad</span></div></div></section>
{sec("Frequently asked questions", "", faq_html(FAQ_VISA))}
{cta_band()}'''
    acts = f'<a class="btn wa" href="{wa("Hi, I need visa consultancy.")}" target="_blank" rel="noopener">💬 Free assessment</a><a class="btn light" href="/countries">All destinations</a>'
    ph = pagehead("Visa services", "Visas tailored<br>to your journey", "Two services from Blue Area, Islamabad: visit visa processing for Asian countries, and visa file preparation and guidance for Europe, Schengen, the UK, the USA, Canada, Australia and others.", UNS["th"], alt="Thailand – visit visa processing from Islamabad", actions=acts)
    body = shell("/visa-services", [("Home", "/"), ("Visa Services", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Visa Services", "/visa-services")]), faq_ld(FAQ_VISA),
          service_ld("Visa consultancy in Islamabad", "Two services: visit visa processing for Asian countries, and visa file preparation and guidance for Europe, Schengen, the UK, the USA, Canada, Australia and others. @N@ country guides.", "/visa-services",
                     {"serviceType": "Visa consultancy", "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Visa services", "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "url": BASE + f"/visa-services/{s}"}} for s, n, _, _, _ in VISA_SERVICES]}})]
    page("/visa-services", "Visa Services: Tourist, Family, Business & Student | AL ARBAB",
         "Visa services in Blue Area, Islamabad: Schengen, UK, USA, Canada & Australia visas. Documentation, appointments, interview coaching and a free document check.",
         body, ld, "visa consultant islamabad, visa agency islamabad, schengen visa pakistan, uk visa islamabad, usa visa pakistan", priority="0.9")
    for s in VISA_SERVICES:
        build_service(*s)

def build_service(slug, name, ic, desc, req_kind):
    url = f"/visa-services/{slug}"
    tpl = {v["slug"]: v for v in DATA["visaTypeTemplate"]}
    req = tpl["visit-visa" if req_kind == "visit" else "business-visa"] if req_kind else None
    dests = [COUNTRIES[s] for s in SERVICE_DEST.get(slug, []) if s in COUNTRIES]
    regs = [REGIONS[s] for s in SERVICE_REGIONS.get(slug, []) if s in REGIONS]
    inc = "".join(f"<li>{x}</li>" for x in INCLUDED)
    ln = name.lower()
    if req:
        items = "".join(f"<li>{e(x)}</li>" for x in req["requirements"])
        req_block = f'<div class="block"><h2>Typical documents for {e(an(ln))}</h2><ul class="docs">{items}</ul><p class="note" style="margin-top:14px">Each embassy has its own checklist. Open your destination below for its exact requirements and fee.</p></div>'
    else:
        req_block = f'<div class="block"><h2>Documents for {e(an(ln))}</h2><p>Documents for {e(an(ln))} depend heavily on the destination country and your personal profile. After a free assessment we give you a written checklist for your exact case.</p></div>'
    faqs = FAQ_VISA[2:] + FAQ_GENERAL[:2]
    db = f'<div class="block"><h2>Popular destinations for {e(ln)}s</h2><div class="tiles">{"".join(tile(c) for c in dests)}</div></div>' if dests else ""
    rb = f'<div class="block"><h2>Regional guides</h2><div class="rgrid">{"".join(region_card(r) for r in regs)}</div></div>' if regs else ""
    main = f'''<div class="stack">
<div class="block"><h2>{e(name)} consultancy in Islamabad</h2><p>{e(desc)} {NAME} is based in Blue Area and checks your documents for free before you apply.</p></div>
{tiers_note()}
<div class="block"><h2>What's included</h2><ul class="checks">{inc}</ul></div>
{req_block}
<div class="block"><h2>How we work</h2><ol class="steps">{steps_html(HOW_WE_WORK)}</ol></div>
{db}
{rb}
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div>
</div>'''
    others = "".join(f'<a href="/visa-services/{s}">{n} <span>→</span></a>' for s, n, *_ in VISA_SERVICES if s != slug)
    aside = f'<aside class="aside">{ctacard(name)}<nav class="mini"><h3>Other visa services</h3>{others}</nav></aside>'
    content = f'<div class="layout">{main}{aside}</div>{cta_band()}'
    pid = next((c["img"] for c in dests if c["img"]), UNS["fr"])
    VS_PIC = {"family-visit-visa": f'/assets/cards/vs-family-visit.webp?v={asset_hash("cards/vs-family-visit.webp")}'}   # owner's own picture for this page
    pid = VS_PIC.get(slug, pid)
    acts = f'<a class="btn wa" href="{wa("Hi, I need help with a " + name + ".")}" target="_blank" rel="noopener">💬 Free assessment</a>'
    ph = pagehead(f"{ic} Visa services", f"{e(name)} from Pakistan", e(desc) + " End-to-end documentation, appointments and interview preparation from Blue Area, Islamabad.", pid, alt=name, actions=acts)
    body = shell("/visa-services", [("Home", "/"), ("Visa Services", "/visa-services"), (name, None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Visa Services", "/visa-services"), (name, url)]), service_ld(f"{name} consultancy", desc, url, {"serviceType": name}), faq_ld(faqs)]
    st_title = f"{name} from Pakistan: Documents & Process | AL ARBAB" if slug != "schengen-visa" else "Schengen Visa Service: Documents & Appointments | AL ARBAB"
    if len(st_title) > 65:
        st_title = f"{name} from Pakistan: Documents | AL ARBAB"
    page(url, st_title, f"{desc} Expert {ln} documentation, embassy appointments and interview prep in Blue Area, Islamabad."[:160],
         body, ld, f"{ln} pakistan, {ln} consultant islamabad, apply {ln} from pakistan", priority="0.7")

def build_air():
    feats = "".join(feat(*x) for x in [("✅", "DTS licensed", "Licensed by the Department of Tourist Services, Government of Pakistan."), ("🌍", "International Routes", "All major airlines worldwide."), ("💸", "Fares", "Fares quoted on WhatsApp for your dates, with clear fees."), ("🕑", "Support", "Booking changes handled Mon–Sat, 9am–8pm.")])
    rt = "".join(f'<div class="route"><span class="c">{c}</span><b><a href="{route_url(n)}">Islamabad → {n}</a></b><small>{al}</small><a href="{route_url(n)}">Route details &amp; fares →</a></div>' for n, c, al in ROUTES)
    chk = "".join(f"<li>{x}</li>" for x in ["Passport validity must be at least 6 months.", "Check transit visa requirements for layovers.", "Ensure your name matches your passport exactly.", "Verify baggage allowance (2PC vs 30KG)."])
    content = f'''{sec("Why book flights with us", "", f'<div class="grid g4">{feats}</div>')}
<section class="sec reveal"><div class="split"><div class="prose"><span class="eyebrow">Global network</span><h2>Flights from Islamabad to destinations worldwide</h2><p>As a licensed travel agency, we book tickets with major airlines. Send your route and dates and we check availability and fares for you.</p><div class="kw"><span>E-Tickets</span><span>Group Discounts</span><span>Student Fares</span><span>Multi-city Routes</span></div></div>
<div class="prose" style="align-content:center"><span class="eyebrow">Fare quotes</span><div class="big" style="font-size:clamp(30px,4vw,48px)">WhatsApp</div><p>Ready to fly? Send us your route and dates. We reply during office hours.</p><p><a class="btn wa" href="{WA}" target="_blank" rel="noopener">Contact ticketing officer</a></p></div></div></section>
{sec("Popular flight routes from Islamabad", "Our most frequently booked international sectors and the top airlines servicing them.", f'<div class="grid g4">{rt}</div>')}
<section class="sec reveal"><div class="prose"><h2>Why choose {NAME} for your flight bookings?</h2>
<p>{NAME} is a licensed travel agent in Blue Area, Islamabad, with access to fares on many international airlines.</p>
<div class="two"><div><h3>Flights from Islamabad</h3><p>We book flights from Islamabad to London, New York, Toronto, Dubai, and Melbourne. We compare direct routes with options through other hubs, so you can choose the fare and route that suit you.</p></div>
<div><h3>Global airline partnerships</h3><p>Emirates, Qatar Airways, Turkish Airlines, PIA and more — we provide seamless reservations and early access to promotional fares. <a class="link" href="/partner-airlines">See the airlines we book →</a></p></div>
<div><h3>Corporate &amp; group travel</h3><p>Group flight booking in Islamabad lets you block seats with minimal deposits and manage name changes flexibly. Perfect for weddings, sports teams, and religious groups.</p></div>
<div><h3>Special student discounts</h3><p>Discounted tickets with extra baggage allowances on airlines like Virgin Atlantic, Etihad, and British Airways. Bring your university offer letter and save on your first journey abroad.</p></div></div>
<h3>Ticketing checklist</h3><ul class="checks">{chk}</ul>
<h3>Changes &amp; cancellations</h3><p>Flight cancelled? Need a date change? Message us on WhatsApp and we handle it as the airline's fare rules allow. Support: Mon–Sat, 9am–8pm.</p></div></section>
{sec("Frequently asked questions", "Everything you need to know about booking flights with us.", faq_html(FAQ_AIR))}
{cta_band("Ready to fly?")}'''
    acts = f'<a class="btn wa" href="{wa("Hi, I need a flight quote.")}" target="_blank" rel="noopener">💬 Get a fare quote</a><a class="btn light" href="/partner-airlines">Airlines we book</a>'
    ph = pagehead("Air ticketing", "Air tickets on every<br>major airline", "Tickets on major airlines, domestic and international. Support: Mon–Sat, 9am–8pm.", PGPIC["pg-air"], alt="Airliner at an airport at sunset", actions=acts)
    body = shell("/air-ticketing", [("Home", "/"), ("Air Ticketing", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Air Ticketing", "/air-ticketing")]), faq_ld(FAQ_AIR), service_ld("Air ticketing in Islamabad", "Air ticketing on major airlines, with e-tickets.", "/air-ticketing", {"serviceType": "Air ticketing"})]
    page("/air-ticketing", "Air Ticketing Agency Islamabad | Flight Tickets | AL ARBAB",
         "Air ticketing in Islamabad. Flights to London, Dubai, Toronto, Jeddah & more on major airlines. E-tickets, group & student fares. Fares on WhatsApp.",
         body, ld, "air ticketing islamabad, flight tickets islamabad, licensed travel agent pakistan, pia booking islamabad, emirates tickets islamabad", priority="0.9")

def build_umrah():
    pk = ""
    for n_, u in enumerate(DATA["umrah"]):
        ft = u["features"]
        f = "".join(f"<li>{e(x)}</li>" for x in ft[2:])
        pk += (f'<article class="pln{" feat" if n_ == 1 else ""}"><div class="pln-top"><span class="pln-pill">{e(ft[0])}</span><h3>{e(u["title"])}</h3>'
               f'<p>{e(ft[1]) if len(ft) > 1 else ""}</p><a class="pln-btn" href="{umrah_url(u)}">Package details <span aria-hidden="true">&rarr;</span></a></div>'
               f'<ul class="pln-list">{f}</ul></article>')
    ph_ = "".join(feat(*x) for x in [("✈️", "Flights", "We arrange return flights and quote them for your dates on WhatsApp."), ("🏨", "Hotels", "We book Makkah and Madinah hotels for your dates."), ("🚌", "Transport", "Shared or private transport, as listed in your package."), ("🛂", "Umrah visa file", "We prepare your visa file. The Saudi authorities make the decision.")])
    why = "".join(f"<li><span><b>{a}</b><br>{b}</span></li>" for a, b in [("Visa file preparation", "We check your documents and prepare your Umrah visa file. The decision rests with the Saudi authorities."), ("Hotels confirmed for your dates", "Confirmed Makkah & Madinah hotel location before you pay"), ("Flights arranged", "Return flights from Islamabad, quoted for your dates on WhatsApp"), ("Support", "WhatsApp and phone support, Mon–Sat, 9am–8pm")])
    content = f'''<section class="sec reveal"><div class="umrah"><div class="t"><span class="eyebrow">Spiritual journey</span><h2 class="qh">"Perform Umrah and Hajj, as they remove poverty and sins…"</h2><p>— Prophet Muhammad (PBUH). From budget-friendly economy stays to premium 5-star luxury experiences — we arrange your hotels, flights and Umrah visa file.</p></div><div class="pic">{picture(UMRAH_IMG, "Umrah packages from Pakistan 2026 – Makkah", 1000, 667, "(max-width:1000px) 100vw, 560px")}</div></div></section>
{sec("Choose the package that fits your journey", "Pre-designed packages and fully customizable options to suit your preferences.", f'<div class="plns">{pk}</div>', "packages")}
{sec("What we arrange for your Umrah", f"{NAME} is a DTS-licensed travel agency in Blue Area, Islamabad. We arrange Umrah packages, hotels and flights, and we prepare your Umrah visa file.", f'<div class="grid g4">{ph_}</div>')}
<section class="sec reveal"><div class="band"><div><h2>Customized Umrah planning</h2><p>Build your own itinerary: choose your hotels in Makkah &amp; Madinah, private GMC or luxury bus transport, flexible stays of 7, 10, 15 or 30 days, as a group or private family package.</p></div><div><a class="btn wa" href="{wa("Hi, I would like a custom Umrah quote.")}" target="_blank" rel="noopener">Request custom quote</a></div></div></section>
<section class="sec reveal"><div class="prose"><h2>Umrah travel agency in Islamabad</h2>
<p>{NAME} is a travel agency in Islamabad that arranges Umrah packages for 2026: hotels, flights, transport and Umrah visa file preparation. Tell us your dates and group size on WhatsApp and we quote today's price.</p>
<div class="two"><div><h3>Economy &amp; budget Umrah 2026</h3><p>Our Economy packages suit families looking for a lower-cost option. Hotel distance and transport are listed on each package.</p></div>
<div><h3>5 Star Umrah</h3><p>Our 5 Star packages use hotels close to the Haram, with private transport. Exact hotels and distances are confirmed for your dates.</p></div></div>
<h2>Why book your Umrah with us?</h2><ul class="checks">{why}</ul></div></section>
{sec("Frequently asked questions", "", faq_html(FAQ_UMRAH))}
{cta_band("Begin your sacred journey")}'''
    acts = f'<a class="btn wa" href="{wa("Hi, I want Umrah package details.")}" target="_blank" rel="noopener">💬 Umrah enquiry</a>'
    ph = pagehead("Spiritual journey", "Umrah packages designed<br>for peace of mind", "Economy to 5-star Umrah packages 2026 from Islamabad: hotels, flights and Umrah visa file preparation. Support: Mon–Sat, 9am–8pm.", UMRAH_IMG, alt="Kaaba, Makkah – Umrah 2026", actions=acts)
    body = shell("/umrah", [("Home", "/"), ("Umrah Packages", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Umrah Packages", "/umrah")]), faq_ld(FAQ_UMRAH),
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Umrah packages 2026", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Service", "name": f"Umrah {u['title']}", "provider": {"@id": BASE + "/#org"},
            }} for i, u in enumerate(DATA["umrah"])]}]
    page("/umrah", "Umrah Packages 2026 from Pakistan | AL ARBAB",
         "Umrah packages 2026 from Islamabad: Economy, 3 Star, 4 Star and 5 Star. We arrange hotels and flights and prepare your Umrah visa file. Price on WhatsApp.",
         body, ld, "umrah packages 2026, umrah packages from pakistan, umrah packages islamabad, 5 star umrah packages", image=AU(UMRAH_IMG, 1200), priority="0.9")

def build_hotel():
    t = "".join(feat(*x) for x in [("🏨", "Luxury Stays", "5-star resorts, suites and exclusive properties."), ("🛏", "Mid-range Comfort", "Trusted brands and great locations."), ("💡", "Budget Friendly", "Verified value stays for smart travelers."), ("🌐", "Hotels worldwide", "Hotels across Europe, the Americas, the Middle East and Asia, booked to match your visa file.")])
    content = f'''{sec("Hotels for every budget", "", f'<div class="grid g4">{t}</div><p style="margin-top:20px"><a class="btn wa" href="{wa("Hi, I need a hotel booking.")}" target="_blank" rel="noopener">Book a hotel</a></p>')}
<section class="sec reveal"><div class="prose"><h2>Expert hotel booking agent in Islamabad</h2><p>Securing the right accommodation is critical, especially when applying for visas. As a hotel booking agent in Islamabad, {NAME} offers verifiable hotel reservations for visa applications. Embassies, particularly for Schengen and the US, require confirmed hotel bookings; we ensure your documentation is flawless to prevent visa rejections.</p>
<h3>What embassies check in a hotel booking</h3><ul class="checks"><li>Your name exactly as in the passport</li><li>Every night of the stay covered, city by city</li><li>Dates that match the flight reservation and cover letter</li><li>Hotel address and contact details the embassy can verify</li></ul>
<p>Need flights too? See our <a class="link" href="/flight-hotel-reservation-for-visa">flight &amp; hotel reservation for visa</a> service.</p>
<p>Beyond visa compliance, we offer exceptional deals for holidaymakers and corporate travelers. Whether you need a luxury 5-star resort in Dubai, a boutique hotel in Paris, or a budget-friendly stay in London, our international partnerships help us offer strong rates.</p></div></section>
{cta_band()}'''
    ph = pagehead("Hotels", "Stay where you love,<br>save where it matters", "From 5-star icons to boutique gems and value stays — we book it all, including verifiable reservations for visa files.", UNS["sg"], alt="Hotel booking – Singapore", actions=WA_HERO)
    body = shell("/hotel-booking", [("Home", "/"), ("Hotel Booking", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Hotel Booking", "/hotel-booking")]), service_ld("Hotel booking", "Hotel reservations worldwide, including verifiable bookings for visa applications.", "/hotel-booking", {"serviceType": "Hotel booking"})]
    page("/hotel-booking", "Hotel Booking Agent Islamabad | Visa Hotel Reservations",
         "Verifiable hotel reservations for visa applications and holidays. Luxury, mid-range and budget stays worldwide, booked by our Blue Area office.",
         body, ld, "hotel booking islamabad, hotel reservation for visa, hotel booking agent pakistan", priority="0.7")

def build_insurance():
    cov = "".join(feat(*x) for x in [("🩺", "Medical Coverage", "Medical emergencies, hospital stays and repatriation abroad, up to the limit of the policy you choose."), ("🧳", "Trip Protection", "Cover for trip cancellations, delays or lost baggage, depending on the policy."), ("🇪🇺", "Schengen Compliant", "Policies that meet the €30,000 minimum medical cover Schengen embassies require.")])
    covers = "".join(f"<li>{x}</li>" for x in ["Emergency medical expenses and hospital stays", "Medical evacuation and repatriation", "Trip cancellations and severe delays", "Loss of passport or checked baggage"])
    content = f'''{sec("What our travel insurance covers", "", f'<div class="grid">{cov}</div>')}
{sec("Policies from Pakistani insurers", "We arrange travel insurance from licensed Pakistani insurers and check that the cover meets your embassy's requirements before you apply.", "")}
<section class="sec reveal"><div class="prose"><h2>Comprehensive travel &amp; medical insurance in Pakistan</h2>
<div class="two"><div><h3>Schengen visa requirements</h3><p>Applying for a visa to Europe? Securing Schengen-approved travel insurance in Islamabad is a mandatory step. All Schengen embassies require a valid policy covering the exact duration of your stay. We provide strictly compliant policies that meet the mandatory minimum €30,000 medical emergency coverage.</p></div>
<div><h3>A policy the embassy can check</h3><p>We arrange your policy from a licensed Pakistani insurer and check the dates, the countries covered and the medical cover against your visa application. Ask us how the embassy can verify your policy before you pay.</p></div></div>
<h3>What our policies cover</h3><ul class="checks">{covers}</ul>
<h3>Issued from our Blue Area office</h3><p>Whether you need coverage for a USA visa, a UK family visit, or a European tour, send us a picture of your passport via WhatsApp or visit our office in Blue Area, Islamabad. We issue your verifiable travel insurance certificate once we have your details. We reply during office hours.</p></div></section>
{cta_band("Insure your journey today", "Get your verifiable travel insurance over WhatsApp or at our Blue Area office.")}'''
    acts = f'<a class="btn wa" href="{wa("Hi, I need a travel insurance quote.")}" target="_blank" rel="noopener">💬 Get insurance quote</a>'
    ph = pagehead("Travel insurance", "Travel covered.<br>Mind at ease.", "Schengen-compliant policies, global medical cover and trip cancellation protection from licensed Pakistani insurers.", UNS["it"], alt="Schengen travel insurance", actions=acts)
    body = shell("/travel-insurance", [("Home", "/"), ("Travel Insurance", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Travel Insurance", "/travel-insurance")]), service_ld("Travel insurance", "Schengen-compliant, embassy-verifiable travel insurance issued from Islamabad.", "/travel-insurance", {"serviceType": "Travel insurance"})]
    page("/travel-insurance", "Travel Insurance Pakistan | Schengen Compliant | AL ARBAB",
         "Schengen-compliant travel insurance from licensed Pakistani insurers, with the €30,000 minimum medical cover, arranged from our Blue Area office in Islamabad.",
         body, ld, "travel insurance pakistan, schengen travel insurance islamabad, travel insurance for visa", priority="0.7")

def build_airlines():
    cats = []
    for a in DATA["airlines"]:
        if a["category"] not in cats:
            cats.append(a["category"])
    slug = lambda s: re.sub(r"[^a-z]+", "-", s.lower()).strip("-")
    n = len(DATA["airlines"])
    tabs = f'<button type="button" data-r="all" aria-pressed="true">All ({n})</button>' + "".join(f'<button type="button" data-r="{slug(c)}" aria-pressed="false">{e(c)} ({sum(1 for a in DATA["airlines"] if a["category"] == c)})</button>' for c in cats)
    cards = ""
    for a in DATA["airlines"]:
        fl = "".join(f"<li>• {e(x)}</li>" for x in a["features"])
        cards += f'<article class="air" data-region="{slug(a["category"])}"><div class="top"><span style="font-size:26px">{a["flag"]}</span><span class="code">{e(a["iata"])}</span></div><h3>{e(a["name"])}</h3><small>Est. {e(a["founded"])} · {e(a["hub"])}</small><ul>{fl}</ul><a href="{wa(f"Hi, I want a fare on {a['name']} ({a['iata']}).")}" target="_blank" rel="noopener">Enquire now →</a></article>'
    wh = "".join(feat(*x) for x in [("🎫", "Today's fares", "We check live fares and send you the options on WhatsApp"), ("📞", "Route advice", "We compare routes and cabins for your trip"), ("✅", "DTS licensed", "Licensed by the Department of Tourist Services, Government of Pakistan."), ("💬", "WhatsApp booking", "Book via WhatsApp, Mon–Sat, 9am–8pm. No paperwork.")])
    content = f'''<section class="sec reveal">
<h2 class="sr">Airlines by region</h2><div class="tabs" id="airTabs" role="group" aria-label="Filter airlines by region">{tabs}</div><div class="grid g4">{cards}</div></section>
{sec("Why book flights with us", "", f'<div class="grid g4">{wh}</div>')}
{cta_band("Ready to fly?", "Tell us your destination and we check fares across airlines for you. We reply during office hours.")}'''
    ph = pagehead("Airlines we book", "World-class airlines.<br>One agency.", f"{NAME} is a DTS-licensed travel agency that books tickets on major airlines. From budget to luxury — we connect Pakistan to the world.", UNS["dubai2"], alt="Airlines we book from Islamabad", actions=WA_HERO)
    body = shell("/partner-airlines", [("Home", "/"), ("Airlines We Book", None)], ph, content)
    page("/partner-airlines", "Airlines We Book | Emirates, Qatar, PIA, Turkish | AL ARBAB",
         "DTS-licensed agency for tickets on PIA, Emirates, Qatar Airways, Etihad, Turkish, British Airways, Saudia & more. Today's fares on WhatsApp from Islamabad.",
         body, [crumbs_ld([("Home", "/"), ("Airlines We Book", "/partner-airlines")])], "airlines islamabad, emirates tickets islamabad, qatar airways pakistan, turkish airlines islamabad", priority="0.6")

def build_about():
    vh = "".join(feat(*x) for x in [("🎯", "Our mission", "Empower every traveler with transparent, expert visa and travel guidance — no shortcuts, no false promises, no surprises."), ("🔭", "Our vision", "To give every client clear, honest visa and travel guidance, and to keep improving how we serve them."), ("💎", "Our values", "Honesty in assessment, expertise in execution, accountability in results, and an obsessive focus on the client experience.")])
    ex = "".join(f'<a class="feat" href="{u}" style="display:block"><h3>{a}</h3><p>{b}</p></a>' for a, b, u in [("Schengen Visas", "Expert profiling for Europe", "/countries/schengen"), ("USA & UK Visas", "B1/B2 and Standard Visitor", "/countries/united-states"), ("Umrah Packages", "Hotels, flights and visa file", "/umrah"), ("Global Ticketing", "Competitive fares worldwide", "/air-ticketing"), ("Travel Insurance", "Schengen-compliant policies", "/travel-insurance"), ("Corporate Travel", "B2B travel management", "/contact")])
    content = f'''<section class="sec reveal"><div class="split"><div class="prose"><span class="eyebrow">About us</span><h2>Visa and travel advice from Blue Area, Islamabad</h2><p>{NAME} is a DTS-licensed travel agency and visa consultancy in Blue Area, Islamabad. Our aim is simple: make global travel accessible to every Pakistani family, student and professional, with transparent advice and a free first check of your documents.</p><p>From complex Schengen and US visitor visas to family reunification and global air ticketing, our dedicated <a class="il" href="/visa-consultant-islamabad">visa consultants</a> and <a class="il" href="/travel-agency-islamabad">travel agency team</a> in Blue Area deliver premium service at every step of your application.</p><p><a class="btn" href="/contact">Book a free consultation</a></p></div>
<div class="prose" style="align-content:center"><div class="stats" style="margin:0;gap:34px"><div><b class="big" style="font-size:54px">@N@</b><small>Country guides</small></div><div><b class="big" style="font-size:54px">DTS</b><small>Licensed agency</small></div></div></div></div></section>
{sec("The foundation of our success", "The core principles that drive every application we process and every ticket we book.", f'<div class="grid">{vh}</div>')}
{sec("Meet our visa consultants", "The people who check your file.", '<div class="cards">' + "".join(f'<figure class="quote">{(chr(60) + "img src=" + chr(34) + m["photo"] + chr(34) + " alt=" + chr(34) + e(m["name"]) + chr(34) + " width=" + chr(34) + "96" + chr(34) + " height=" + chr(34) + "96" + chr(34) + " loading=" + chr(34) + "lazy" + chr(34) + " class=" + chr(34) + "avatar" + chr(34) + ">") if m.get("photo") else ""}<figcaption><b>{e(m["name"])}</b>{e(m.get("role", ""))}</figcaption><blockquote>{e(m.get("bio", ""))}</blockquote></figure>' for m in TEAM) + "</div>") if TEAM else ""}
{sec("Comprehensive global expertise", "We strategically build your profile to ensure maximum approval chances across travel sectors.", f'<div class="grid g4">{ex}</div>')}
{cta_band("Visit our Blue Area office", f"{ADDR}. {HOURS}. Book a dedicated 1-on-1 consultation.")}'''
    ph = pagehead("Our story", "Visa consultancy<br>from the heart of Islamabad", f"{NAME} helps travelers with visas, flights and travel plans from Blue Area, Islamabad, with {len(COUNTRIES)} country guides.", f'/assets/cards/about-hero.webp?v={asset_hash("cards/about-hero.webp")}', alt="A flight map and flight overview seen from an aeroplane window", actions=WA_HERO)
    body = shell("/about", [("Home", "/"), ("About Us", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("About Us", "/about")]), {"@context": "https://schema.org", "@type": "AboutPage", "name": f"About {NAME}", "url": BASE + "/about", "about": {"@id": BASE + "/#org"}}]
    page("/about", "About Us | Visa & Travel Agency in Blue Area | AL ARBAB",
         f"AL ARBAB TRAVEL AND TOURS is a DTS-licensed travel agency in Blue Area, Islamabad: visas, air tickets, Umrah, hotels and insurance, with {len(COUNTRIES)} country guides.",
         body, ld, priority="0.6")

def build_contact():
    info = [("📍", "Office", f'<a href="{MAP_URL}" target="_blank" rel="noopener">{ADDR}</a>'), ("📞", "Phone", f'<a href="tel:{PHONE_I}">{PHONE}</a> | <a href="tel:{LAND_I}">{LAND}</a>'), ("✉", "Email", f'<a href="mailto:{EMAIL}">{EMAIL}</a>'),
            ("🕑", "Hours", HOURS), ("💬", "WhatsApp", f'<a href="{WA}" target="_blank" rel="noopener">{PHONE}</a>'), ("👍", "Facebook", f'<a href="{B["socials"]["facebook"]}" target="_blank" rel="noopener me">Follow us on Facebook</a>')]
    ih = "".join(f'<div><span class="ic">{a}</span><span><small>{b.upper()}</small>{c}</span></div>' for a, b, c in info)  # emoji keys become brand icons in finish_icons()
    opts = "".join(f"<option>{o}</option>" for o in ["Schengen / Europe", "USA", "UK", "Canada", "Australia", "Thailand", "Malaysia", "Indonesia (Bali)", "Singapore", "Dubai / UAE", "Turkey", "China", "Japan", "Umrah / Saudi Arabia", "Air ticket only", "Other"])
    content = f'''<section class="sec reveal" style="margin-top:20px"><div class="contactgrid"><div class="info">{ih}
<div class="map map-facade" data-src="https://www.google.com/maps?q=Eagle%20Plaza%2C%20Fazal-e-Haq%20Road%2C%20Blue%20Area%2C%20Islamabad&amp;output=embed" data-title="Map: {NAME} office, Blue Area, Islamabad"><button type="button" class="btn light">📍 Show map</button><span>Eagle Plaza, Fazal-e-Haq Road, Blue Area, Islamabad</span></div></div>
<form class="f" id="contactForm"><h2 style="font-size:24px;text-transform:uppercase">Send a message</h2><p style="font-size:13px;color:#3a5558">Fill out the form and it opens WhatsApp with your message. We reply during office hours.</p>
<div class="row"><div><label for="name">Full name</label><input id="name" name="name" required autocomplete="name"></div><div><label for="email">Email address</label><input id="email" name="email" type="email" required autocomplete="email"></div></div>
<div class="row"><div><label for="phone">WhatsApp number</label><input id="phone" name="phone" type="tel" required autocomplete="tel"></div><div><label for="dest">Target destination</label><select id="dest" name="dest">{opts}</select></div></div>
<div><label for="msg">Travel plans &amp; details</label><textarea id="msg" name="msg" rows="4"></textarea></div>
<div><button class="btn wa" type="submit">Send your inquiry via WhatsApp</button></div></form></div></section>
{sec("Not sure which service you need?", "", '<div class="block"><p>See what our <a class="il" href="/travel-agency-islamabad">travel agency in Islamabad</a> and our <a class="il" href="/visa-consultant-islamabad">visa consultants in Islamabad</a> can do for your trip, then message us on WhatsApp for a free document check.</p></div>')}'''
    ph = pagehead("Contact", "We'd love<br>to hear from you", "Walk in, call, email or message us on WhatsApp. We reply during office hours.", actions=WA_HERO)
    body = shell("/contact", [("Home", "/"), ("Contact", None)], ph, content)
    ld = [crumbs_ld([("Home", "/"), ("Contact", "/contact")]), {"@context": "https://schema.org", "@type": "ContactPage", "name": f"Contact {NAME}", "url": BASE + "/contact", "about": {"@id": BASE + "/#org"}}]
    page("/contact", "AL ARBAB Travel Islamabad Contact Number & WhatsApp",
         f"Visit AL ARBAB TRAVEL AND TOURS at Eagle Plaza, Blue Area, Islamabad. Call {PHONE} / {LAND}, email or WhatsApp. Open Mon–Sat 9 AM–8 PM.",
         body, ld, priority="0.8")

def build_policies():
    """Terms, Privacy, Fees & Refunds, Disclaimer, Compliance. Plain, conservative wording; business details that are assumptions are listed for the owner."""
    contact = f'<p>Contact: <a class="link" href="tel:{PHONE_I}">{PHONE}</a> · <a class="link" href="mailto:{EMAIL}">{EMAIL}</a> · WhatsApp <a class="link" href="{WA}" target="_blank" rel="noopener">{PHONE}</a><br>{ADDR}<br>Office hours: {HOURS}.</p>'
    upd = f'<p class="note">Last updated: {UPDATED}.</p>'
    terms = f"""<div class="block legal">{upd}
<h2>1. Who we are</h2><p>{NAME} ("we", "us") is a private, DTS-licensed travel agency and visa consultancy at {ADDR}. We are not an embassy, consulate, visa centre or government office, and we are not affiliated with any of them. By using our services or website you accept these terms.</p>
<h2>2. Our services</h2><p>We offer two visa services:</p><ul>
<li><b>{e(TIER1_NAME)}:</b> we process and follow up your visit visa application for Asian countries, from the document checklist to submission and follow-up.</li>
<li><b>{e(TIER2_NAME)}:</b> we prepare and organise your file and guide you through the embassy or visa centre submission. You attend biometrics or an interview yourself where the embassy requires it.</li></ul>
<p>We also arrange air tickets, hotel bookings, travel insurance and Umrah packages (hotels, flights and Umrah visa file preparation).</p>
<h2>3. No guarantee of approval</h2><p>The embassy, high commission, consulate or other issuing authority makes the final decision on every visa. We do not guarantee that any visa will be approved, or how long a decision will take. A past result on another file is not a promise about yours.</p>
<h2>4. What you must do</h2><ul><li>Give us genuine, valid and complete documents and information. You are responsible for their accuracy.</li>
<li>Tell us about any previous visa refusal, deportation, overstay or travel history the embassy may ask about.</li>
<li>Reply to our requests in good time, and tell us at once if anything in your file changes.</li>
<li>Pay embassy and visa centre fees yourself or through us, as agreed in writing.</li></ul>
<h2>5. Genuine documents only</h2><p>We never submit fake, altered or misleading documents, bank statements, bookings or information, and we will not do so at a client's request. If we find that a document or statement is false, we may stop work on the file and tell the relevant authority where the law requires it. Our fee is not refundable in that case. See our <a class="link" href="/compliance">compliance commitment</a>.</p>
<h2>6. Fees and refunds</h2><p>Embassy and visa centre fees are separate from our service fee. We quote our service fee before you pay. Our <a class="link" href="/fees-and-refunds">fees &amp; refund policy</a> explains what is and is not refundable.</p>
<h2>7. Processing times</h2><p>Processing times are set by embassies and visa centres and can change without notice. Any time we mention is an estimate, not a promise.</p>
<h2>8. Airlines, hotels, insurers and other suppliers</h2><p>Tickets, hotels, insurance and Umrah components are provided under the rules of the airline, hotel, insurer or other supplier. Changes, cancellations and refunds follow those rules, and any supplier charges apply.</p>
<h2>9. Information on our website</h2><p>Our country pages are a general guide built from official sources and our checklists, and rules change. Always confirm the current requirements on the official portal linked on the page, or with us before you apply. See our <a class="link" href="/disclaimer">disclaimer</a>.</p>
<h2>10. Confidentiality</h2><p>We handle your documents and personal data as described in our <a class="link" href="/privacy">privacy policy</a>.</p>
<h2>11. Limits of our responsibility</h2><p>We are not responsible for an embassy's decision, for delays or rule changes outside our control, or for losses that result from false or incomplete information supplied by you. Nothing in these terms limits any right or liability that cannot be limited under the law of Pakistan.</p>
<h2>12. Complaints</h2><p>If you are unhappy with our service, tell us by WhatsApp, phone or email and we will look into it and reply during office hours.</p>
<h2>13. Changes and governing law</h2><p>We may update these terms; the version on this page applies from the date shown. These terms are governed by the laws of Pakistan.</p>{contact}</div>"""
    fees = f"""<div class="block legal">{upd}
<h2>1. Embassy, visa centre and government fees</h2><p>These fees are set by the embassy, visa centre or government and are paid to them, not to us. They change often, so we do not publish them on this website; we confirm the current amount for your case before you pay. Once paid, they are not refundable by us, whatever the outcome of your application. Any refund of these fees depends on the authority's own rules.</p>
<h2>2. Our service fee</h2><p>Our service fee covers our work on your file, for example the consultation, the document checklist and file preparation. For Asian visit visas it also covers submission and follow-up; for other destinations it covers guidance through the submission. We tell you the fee in writing (for example on WhatsApp) before you pay, and we say what it includes. Please ask us if anything is unclear before you pay.</p>
<h2>3. Refunds of our service fee</h2><ul><li>Before we start work on your file: you may cancel and we will refund what you paid us.</li>
<li>After we start work (for example once we have reviewed your documents or begun preparing your file): the fee is for the work done, so it is not refundable.</li>
<li>If a visa is refused: our fee is for our work, not for the outcome, so it is not refunded because of a refusal. We will explain the reasons the embassy gave and the options open to you.</li>
<li>If you give us false or misleading documents or information: we stop work and the fee is not refundable.</li></ul>
<h2>4. Air tickets, hotels, insurance and Umrah packages</h2><p>These follow the rules and charges of the airline, hotel, insurer or other supplier. Date changes, cancellations and refunds depend on the fare or booking conditions confirmed to you when you book. We will tell you those conditions before you pay.</p>
<h2>5. Payment</h2><p>We give you a receipt for every payment. Please pay only to the payment details we confirm in writing from our official contact numbers: {PHONE} and {LAND}.</p>
<h2>6. Refund requests</h2><p>To ask for a refund, contact us by WhatsApp, phone or email with your name and file details. Where a refund is due, we process it as soon as we reasonably can and tell you how long the payment method takes.</p>
<p class="note">Read together with our <a class="link" href="/terms">terms &amp; conditions</a>. We do not guarantee visa approval; the embassy makes the final decision.</p>{contact}</div>"""
    privacy = f"""<div class="block legal">{upd}
<h2>1. Who is responsible for your data</h2><p>{NAME}, {ADDR}, is responsible for the personal information you give us. {DISCLAIMER_LINE}</p>
<h2>2. What we collect</h2><ul><li><b>Identity details:</b> name, passport details, CNIC, date of birth, nationality, photographs.</li>
<li><b>Contact details:</b> phone and WhatsApp number, email address, address.</li>
<li><b>File documents:</b> for example bank statements, tax and employment documents, travel history, bookings and invitation letters that an embassy may request.</li>
<li><b>Messages:</b> what you send us by WhatsApp, email, phone or the website forms.</li></ul>
<h2>3. Why we use it</h2><ul><li>To give you the service you ask for: checking and preparing your file, submitting or guiding your application, booking tickets, hotels, insurance or Umrah components.</li>
<li>To contact you about your file, appointments and decisions.</li><li>To meet legal duties and to keep records of our work.</li></ul>
<h2>4. Who we share it with</h2><p>Only as needed for your file: embassies, consulates and visa centres; airlines, hotels, insurers and other suppliers you ask us to book; and government authorities where the law requires. We do not sell your data and we do not share it for advertising.</p>
<h2>5. Keeping it safe</h2><p>Your documents are used only by people who work on your file. We take reasonable steps to protect them from loss and unauthorised access. No method of sending or storing data is completely secure, so please share documents only through our official contact numbers and email.</p>
<h2>6. How long we keep it</h2><p>We keep your file records for as long as needed to complete the service, answer questions about it and meet legal and accounting duties. You can ask us to delete your documents once the service is complete, unless we must keep them by law.</p>
<h2>7. Your choices</h2><p>You may ask us to show you the information we hold about you, correct it or delete it. Contact us using the details below.</p>
<h2>8. Our website</h2><p>Our website does not use advertising trackers. It loads fonts, flags and photos from third-party servers, and the live weather on the home page comes from a weather service; those providers receive your IP address as part of normal web requests. The map loads only when you open it. When you tap a WhatsApp, call or email link, the service you use handles that message under its own policy.</p>
<h2>9. Changes</h2><p>If we change this policy we update this page and the date above.</p>{contact}</div>"""
    disc = f"""<div class="block legal">{upd}
<h2>Who we are</h2><p><b>{DISCLAIMER_LINE}</b> We are a DTS-licensed travel agency (Department of Tourist Services, Government of Pakistan).</p>
<h2>No guarantee</h2><p>The embassy, high commission, consulate or other issuing authority makes the final decision on every visa. We do not guarantee approval, processing times or entry to any country. For Umrah, the Saudi authorities issue the visa.</p>
<h2>Information on this website</h2><p>Country pages give general guidance for Pakistani passport holders, based on official sources and our own checklists. Rules, forms, fees and processing times change, sometimes without notice. Use the official portal linked on each page as the authority, and confirm your case with us before you apply.</p>
<h2>Success figures</h2><p>The only success figure we publish appears on our Asian visit visa pages, with its period and a note that the embassy decides. It describes our own files in that period. It is not a promise about your application, and it does not apply to Europe, Schengen, the UK, the USA, Canada, Australia or any other destination.</p>
<h2>Links to other websites</h2><p>We link to official government and visa centre websites. We do not control them and are not responsible for their content.</p>
<p class="note">See also our <a class="link" href="/terms">terms &amp; conditions</a>, <a class="link" href="/fees-and-refunds">fees &amp; refund policy</a> and <a class="link" href="/compliance">compliance commitment</a>.</p>{contact}</div>"""
    comp = f"""<div class="block legal">{upd}
<h2>Our commitment</h2><ul class="checks">
<li>We follow international laws and the rules of every embassy and visa centre involved in your file.</li>
<li>We never submit fake or altered documents, fake bank statements, fake bookings or false information.</li>
<li>We guide every client honestly about the risks and about possible refusal.</li>
<li>We do not guarantee outcomes. The embassy or consulate makes the final decision.</li></ul>
<h2>What this means for you</h2><p>If a document is missing, weak or does not match the rest of your file, we tell you and help you fix it with genuine documents. If your case carries a real risk of refusal, we say so before you pay. If you ask us to include something false, we will say no and may stop work on your file.</p>
<p class="note">See our <a class="link" href="/terms">terms &amp; conditions</a>, <a class="link" href="/fees-and-refunds">fees &amp; refund policy</a> and <a class="link" href="/disclaimer">disclaimer</a>.</p>{contact}</div>"""
    for url, name, h1, lead, block, title, desc in [
        ("/terms", "Terms & Conditions", "Terms &amp; Conditions", f"The terms for services provided by {NAME}.", terms, "Terms & Conditions | AL ARBAB TRAVEL AND TOURS", "Terms for AL ARBAB TRAVEL AND TOURS visa consultancy in Islamabad: our two services, your responsibilities, no guarantee of approval, fees and refunds."),
        ("/privacy", "Privacy Policy", "Privacy Policy", f"How {NAME} handles your passport, CNIC and travel information.", privacy, "Privacy Policy | AL ARBAB TRAVEL AND TOURS", "How AL ARBAB TRAVEL AND TOURS collects, uses, shares and protects your passport, CNIC and travel documents for visa, flight, hotel and Umrah services."),
        ("/fees-and-refunds", "Fees & Refund Policy", "Fees &amp; Refund Policy", "What you pay, who you pay it to, and what can be refunded.", fees, "Fees & Refund Policy | AL ARBAB TRAVEL AND TOURS", "Fees and refunds at AL ARBAB TRAVEL AND TOURS: embassy fees are paid to the embassy, our service fee is quoted before you pay, and when it can be refunded."),
        ("/disclaimer", "Disclaimer", "Disclaimer", DISCLAIMER_LINE, disc, "Disclaimer | AL ARBAB TRAVEL AND TOURS", "AL ARBAB TRAVEL AND TOURS is a private travel and visa consultancy and is not affiliated with any embassy or government. We do not guarantee visa approval."),
        ("/compliance", "Our Compliance Commitment", "Our compliance<br>commitment", "We follow the law and each embassy's rules, and we only submit genuine documents.", comp, "Our Compliance Commitment | AL ARBAB TRAVEL AND TOURS", "How AL ARBAB TRAVEL AND TOURS works: we follow each embassy's rules, never submit fake documents or false information, and guide clients honestly about risks and refusals.")]:
        ph = pagehead("Legal &amp; trust", h1, lead)
        body = shell(url, [("Home", "/"), (name, None)], ph, f'<div style="margin-top:20px">{block}</div>')
        page(url, title, desc, body, [crumbs_ld([("Home", "/"), (name, url)])], priority="0.4")

def build_misc():
    body = f'<main id="main"><div class="wrap"><div class="shell"><div class="inner">{header("")}<div class="ph" style="grid-template-columns:1fr"><div><h1>Pakistan visa</h1><p class="lead2">This page has moved to <a class="link" href="/countries/south-asia/pakistan">Pakistan visa services</a>.</p></div></div></div></div></div></main>'
    page("/pakistan-visa", "Pakistan Visa Services | AL ARBAB", "Pakistan visa services have moved.", body,
         extra_head='<meta http-equiv="refresh" content="0; url=/countries/south-asia/pakistan">', noindex=True)
    body = f'<main id="main"><div class="wrap"><div class="shell"><div class="inner">{header("")}<div class="ph" style="grid-template-columns:1fr"><div><h1>Page not<br>found</h1><p class="lead2">The page you are looking for does not exist. Try our visa services, destinations or Umrah packages.</p><div class="actions"><a class="btn" href="/">Back to home</a><a class="btn light" href="/countries">All destinations</a></div></div></div></div></div></div></main>'
    page("/404", "Page not found | AL ARBAB TRAVEL AND TOURS", "Page not found.", body, noindex=True)

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
    return f'''<div class="block"><h2>{title}</h2><div class="contactgrid" style="margin-top:6px"><div class="info" style="padding:0;background:none">
<div><span class="ic">📍</span><span><small>ADDRESS</small><a href="{MAP_URL}" target="_blank" rel="noopener">{ADDR}</a></span></div>
<div><span class="ic">🕑</span><span><small>HOURS</small>{HOURS}</span></div>
<div><span class="ic">📞</span><span><small>PHONE</small><a href="tel:{PHONE_I}">{PHONE}</a> | <a href="tel:{LAND_I}">{LAND}</a></span></div>
<div><span class="ic">💬</span><span><small>WHATSAPP</small><a href="{WA}" target="_blank" rel="noopener">{PHONE}</a></span></div></div>
<div class="map map-facade" data-src="https://www.google.com/maps?q=Eagle%20Plaza%2C%20Fazal-e-Haq%20Road%2C%20Blue%20Area%2C%20Islamabad&amp;output=embed" data-title="Map: {NAME} office"><button type="button" class="btn light">📍 Show map</button><span>Eagle Plaza, Fazal-e-Haq Road, Blue Area, Islamabad</span></div></div>
<p style="margin-top:12px"><a class="btn light" href="{MAP_URL}" target="_blank" rel="noopener">📍 Get directions on Google Maps</a></p></div>'''

def local_ld(city, url, desc):
    o = org_ld()
    return {"@context": "https://schema.org", "@type": "TravelAgency", "@id": BASE + url + "#local", "name": f"{NAME} – {city}", "url": BASE + url,
            "parentOrganization": {"@id": BASE + "/#org"}, "description": desc, "telephone": PHONE_I, "address": o["address"], "geo": o["geo"],
            "openingHoursSpecification": o["openingHoursSpecification"], "areaServed": {"@type": "City", "name": city}, "image": o["image"]}

def build_eligibility():
    elig = {}
    for c in COUNTRIES.values():
        rv = REGIONS[c["region"]]["visas"]
        elig[c["slug"]] = {"n": c["name"], "u": c["url"], "t": c["docs_clean"], "b": rv[1]["requirements"] if len(rv) > 1 else rv[0]["requirements"]}
    for rs in ("united-kingdom", "united-states", "canada", "australia"):
        r = REGIONS[rs]
        elig[rs] = {"n": r["name"], "u": f"/countries/{rs}", "t": r["visas"][0]["requirements"], "b": r["visas"][1]["requirements"] if len(r["visas"]) > 1 else r["visas"][0]["requirements"]}
    opts = "".join(f'<option value="{k}">{e(v["n"])}</option>' for k, v in sorted(elig.items(), key=lambda x: x[1]["n"]))
    content = f'''<section class="sec" style="margin-top:20px"><div class="layout"><div class="stack">
<form class="block elig" id="eligForm"><h2>Your trip</h2>
<div class="f" style="padding:0;background:none;gap:12px">
<div class="row"><div><label for="ed">1. Destination</label><select id="ed" name="d" required><option value="">Choose country</option>{opts}</select></div>
<div><label for="ep">2. Purpose</label><select id="ep" name="p"><option value="t">Tourism / holiday</option><option value="f">Family / friends visit</option><option value="b">Business / conference</option></select></div></div>
<div class="row"><div><label for="es">3. Your situation</label><select id="es" name="s"><option value="emp">Employed (salaried)</option><option value="biz">Business owner / self-employed</option><option value="stu">Student</option><option value="dep">Housewife / retired / dependant</option></select></div>
<div><label for="eb">4. Previous visas</label><select id="eb" name="h"><option value="none">No previous foreign travel</option><option value="some">Gulf / Asia visas</option><option value="strong">UK / USA / Schengen visas</option></select></div></div>
<div><button class="btn" type="submit">Show my checklist</button></div></div></form>
<div class="block" id="eligOut" hidden aria-live="polite"></div>
<div class="block"><h2>How the free check works</h2><ol class="steps">{steps_html([("Choose your trip", "Pick the country, purpose and your situation above."), ("Read your list", "You get the document list for your case, built from embassy requirements."), ("Free file check", "Send the documents on WhatsApp; an adviser checks them for refusal risks."), ("Apply with us", "We book the appointment, prepare the file and track it to the decision.")])}</ol></div>
</div><aside class="aside">{ctacard("visa eligibility")}</aside></div></section>'''
    ph = pagehead("Free tool", "Free visa eligibility<br>&amp; documents check", "Answer four questions and get the document checklist for your visa from Pakistan, then send your file to an adviser on WhatsApp for a free review.", actions=WA_HERO)
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
  "Visas, air tickets, Umrah, hotels and travel insurance from one DTS-licensed office in Eagle Plaza, Blue Area.",
  "Travel Agency in Islamabad (Blue Area) | AL ARBAB",
  "DTS-licensed travel agency in Blue Area, Islamabad: visas, air tickets, Umrah, hotels & insurance. Free WhatsApp consultation: 0315-2323811",
  "travel agency islamabad, travel agency blue area, best travel agency in islamabad, licensed travel agent islamabad"),
 ("/visa-consultant-islamabad", "Islamabad", "Visa Consultant in Islamabad", "Visa consultant<br>in Islamabad",
  "Schengen, UK, USA, Canada, Australia and Asia visas prepared at our Blue Area office, with a free document check before you apply.",
  "Visa Consultant in Islamabad | Free File Check | AL ARBAB",
  f"Visa consultant in Blue Area, Islamabad: Schengen, UK, USA, Canada, Dubai & Asia visas. Free document check on WhatsApp {PHONE_D}",
  "visa consultant islamabad, visa agent islamabad, visa consultancy blue area, visa consultant in islamabad"),
 ("/travel-agency-rawalpindi", "Rawalpindi", "Travel Agency for Rawalpindi", "Travel agency for<br>Rawalpindi clients",
  "Start on WhatsApp from Rawalpindi: free document check first, then one visit to our Blue Area office when your file is ready.",
  "Travel Agency for Rawalpindi Clients | AL ARBAB",
  "Rawalpindi travellers: free visa document check on WhatsApp, then visit our Blue Area office once. Visas, air tickets, Umrah and hotels from a DTS-licensed agency.",
  "travel agency rawalpindi, travel agent rawalpindi, umrah travel agency rawalpindi, air ticket rawalpindi"),
 ("/visa-consultant-rawalpindi", "Rawalpindi", "Visa Consultant for Rawalpindi", "Visa consultant for<br>Rawalpindi",
  "Visa files for Rawalpindi clients handled end to end: document review on WhatsApp, appointment booking and submission support.",
  "Visa Consultant for Rawalpindi | Free File Check | AL ARBAB",
  "Visa consultant for Rawalpindi clients: Schengen, UK, USA, Canada, Dubai & Asia visas. Free WhatsApp document check, one visit to our Blue Area office.",
  "visa consultant rawalpindi, visa agent rawalpindi, visa consultancy rawalpindi, schengen visa rawalpindi"),
]

def build_cities():
    popular = (asian_priority() + [COUNTRIES[s] for s in ("germany", "france", "italy") if s in COUNTRIES])[:12]   # Asian priority first
    for url, city, name, h1, lead, title, desc, kw in CITY_PAGES:
        rawal = city == "Rawalpindi"
        visa = "visa" in url
        isb_page = "/visa-consultant-islamabad" if visa else "/travel-agency-islamabad"
        intro = (f'Rawalpindi clients don\'t need to travel to Islamabad twice. Send your passport and documents on WhatsApp, our adviser checks them for free, and you visit our <a class="il" href="{isb_page}">Blue Area office</a> only when the file is ready to submit.'
                 if rawal else f"{NAME} serves travellers from Blue Area, Islamabad. One office handles your visa file, flights, hotel, insurance and Umrah, so nothing falls between agencies. "
                 + ('For flights, Umrah, hotels and insurance as well, see our <a class="il" href="/travel-agency-islamabad">travel agency in Islamabad</a>.' if visa
                    else 'Need help with one specific visa? Talk to our <a class="il" href="/visa-consultant-islamabad">visa consultants in Islamabad</a>.'))
        services = "".join(feat(ic, n, d, (u, "Open")) for ic, n, d, u in [
            ("◈", "Visa consultancy", "Schengen, UK, USA, Canada, Australia, Gulf and Asia visas with document review and appointments.", "/visa-services"),
            ("✈", "Air tickets", "Air tickets on major airlines, group and student fares, changes handled Mon–Sat, 9am–8pm.", "/air-ticketing"),
            ("🕋", "Umrah packages", "Economy to 5-star packages with visa, flights and hotels.", "/umrah"),
            ("🏨", "Hotels & reservations", "Verifiable hotel and flight reservations for visa files, plus holiday stays.", "/flight-hotel-reservation-for-visa"),
            ("🛡", "Travel insurance", "Schengen-compliant policies from licensed Pakistani insurers.", "/travel-insurance"),
            ("📅", "Visa appointments", "VFS Global, BLS, Gerry's and embassy appointment booking.", "/visa-appointments")])
        steps = steps_html([("WhatsApp your details", "Tell us the country and travel dates; send passport and documents as photos."),
                            ("Free document check", "An adviser checks your file and tells you what is missing and the full price."),
                            ("One office visit", "Visit Blue Area to sign forms and hand over originals when the file is ready."),
                            ("Submission & tracking", "We book the appointment, prepare the file and track it until the decision.")])
        regions = "".join(region_card(REGIONS[s]) for s in ("south-asia", "east-asia", "schengen", "united-kingdom"))
        getting = (f'''<div class="block"><h2>Getting to our office from Rawalpindi</h2><p>Our office is in Eagle Plaza on Fazal-e-Haq Road, Blue Area, just off Jinnah Avenue. The Rawalpindi–Islamabad Metrobus runs along Jinnah Avenue through Blue Area, and Islamabad Expressway or Murree Road connect Rawalpindi to the Blue Area by car.</p><p>Message us before you leave and we will confirm your adviser is free when you arrive.</p></div>''' if rawal else "")
        faqs = [(f"Where is {NAME} located?", f"{ADDR}. Open {HOURS}."),
                ("Can I start without visiting the office?", "Yes. Send your documents on WhatsApp for a free check. You visit the office only when your file is ready to submit."),
                ("Do you charge for the first consultation?", "No. The first consultation and document check are free; we quote the full price before you pay anything."),
                ("Are you a licensed travel agency?", "Yes. We are licensed by the Department of Tourist Services (DTS), Government of Pakistan.")]
        faqs += PAA_AGENCY[:2]
        if rawal:
            faqs.insert(1, ("Do you have an office in Rawalpindi?", "Our office is in Blue Area, Islamabad. Rawalpindi clients start on WhatsApp and visit Blue Area once, when the file is ready."))
        main = f'''<div class="stack">
<div class="block"><h2>{e(name)} you can trust</h2><p>{intro}</p><div class="chipsrow" style="margin-top:12px"><span>DTS licensed</span><span>Free first consultation</span></div></div>
{'<div class="block"><h2>Visa regions we handle</h2><div class="rgrid">' + regions + '</div></div>' if visa else '<div class="block"><h2>Everything under one roof</h2><div class="grid">' + services + '</div></div>'}
<div class="block"><h2>How it works{' for ' + city + ' clients' if rawal else ''}</h2><ol class="steps">{steps}</ol></div>
{getting}
<div class="block"><h2>Popular destinations</h2><div class="tiles">{"".join(tile(c) for c in popular)}</div><p style="margin-top:12px"><a class="link" href="/countries">All {len(COUNTRIES)} country guides →</a></p></div>
{office_block()}
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div>
</div>'''
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
    main = f'''<div class="stack">
<div class="block"><h2>Embassy &amp; visa centre appointments</h2><p>Most embassies in Islamabad accept applications through an outsourced visa centre or an online portal. We create your account, fill the form, pay the fee correctly and book the earliest suitable slot, then prepare the file you take to the appointment.</p></div>
<div class="block"><h2>Where each embassy takes applications</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Country</th><th>Application route</th></tr></thead><tbody>{rows}</tbody></table></div></div>
<div class="block"><h2>Needed to book</h2><ul class="checks">{need}</ul><h3>Bring on appointment day</h3><ul class="checks">{bring}</ul></div>
<div class="block"><h2>How it works</h2><ol class="steps">{steps_html(PROCESS)}</ol></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>'''
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
    main = f'''<div class="stack">
<div class="block"><h2>Reservations that match your visa file</h2><p>Embassies, particularly Schengen and US, check that your flights and hotels match your itinerary and cover the full stay. We issue verifiable flight reservations and hotel bookings that line up with your cover letter, travel insurance and dates, so the file tells one consistent story.</p></div>
<div class="block"><h2>What you get</h2><ul class="checks"><li>Return flight reservation in your passport name</li><li>Hotel bookings for every night of the stay, city by city</li><li>Day-by-day itinerary to match the cover letter</li><li>Schengen-compliant travel insurance on request</li></ul></div>
<div class="block"><h2>How it works</h2><ol class="steps">{steps_html([("Send details", "Passport copy, travel dates and cities on WhatsApp."), ("We draft the plan", "Flights, hotels and itinerary that fit your visa type."), ("Receive documents", "Verifiable reservations, usually the same day."), ("File check", "We check everything matches before you submit.")])}</ol></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>'''
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
                (f"How do I get a good fare on an Islamabad to {city} ticket?", "Book early, stay flexible on dates and compare one-stop routes via hubs like Dubai, Doha or Istanbul. Our ticketing officers check these for you."),
                FAQ_AIR[5] if len(FAQ_AIR) > 5 else FAQ_AIR[0]]
        main = f'''<div class="stack">
<div class="block"><h2>Islamabad to {e(city)} flights</h2><div class="facts" style="margin-top:0"><div><small>Route</small><b>{e(code)}</b></div><div><small>Popular airlines</small><b>{e(al)}</b></div><div><small>E-ticket</small><b>Issued after payment</b></div><div><small>Support</small><b>Mon–Sat, 9am–8pm</b></div></div>
<p style="margin-top:14px">We see live fares on {e(al)} and other carriers serving {e(city)}. Send your dates on WhatsApp and we reply with the best direct and one-stop options, baggage allowance and fare rules.</p>
<p style="margin-top:12px"><a class="btn wa" href="{wa(f"Hi, I need a fare for Islamabad to {city} ({code}). My dates are: ")}" target="_blank" rel="noopener">💬 Get today's fare</a></p></div>
{f'<div class="block"><h2>Visa for {e(city)}</h2><p>Need a visa for this trip? See the document checklist and fees on our <a class="link" href="{vlink}">visa page</a>. We can book your ticket and handle the visa together.</p></div>' if vlink else ""}
<div class="block"><h2>Before you book</h2><ul class="checks"><li>Passport validity must be at least 6 months.</li><li>Check transit visa requirements for layovers.</li><li>Ensure your name matches your passport exactly.</li><li>Verify baggage allowance (2PC vs 30KG).</li></ul></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>'''
        others = "".join(f'<a href="{route_url(c)}">Islamabad → {c} <span>→</span></a>' for c, *_ in ROUTES if c != city)
        content = f'<div class="layout">{main}<aside class="aside">{ctacard("Islamabad to " + city + " ticket")}<nav class="mini"><h3>Other routes</h3>{others}</nav></aside></div>{cta_band("Ready to fly?")}'
        ph = pagehead(f"Air tickets · {e(code)}", f"Islamabad to {e(city)}<br>flights", f"Compare {e(al)} and more. Air tickets with e-tickets and support Mon–Sat, 9am–8pm, from Blue Area, Islamabad.", ROUTE_IMG.get(city), alt=f"{city} – flights from Islamabad",
                      actions=f'<a class="btn wa" href="{wa(f"Hi, I need a fare for Islamabad to {city}.")}" target="_blank" rel="noopener">💬 Get a fare</a><a class="btn light" href="tel:{PHONE_I}">📞 {PHONE}</a>')
        body = shell("/air-ticketing", [("Home", "/"), ("Air Ticketing", "/air-ticketing"), (f"Islamabad to {city}", None)], ph, content)
        ld = [crumbs_ld([("Home", "/"), ("Air Ticketing", "/air-ticketing"), (f"Islamabad to {city}", url)]), service_ld(f"Islamabad to {city} air tickets", f"Air tickets from Islamabad to {city} on {al}.", url, {"serviceType": "Air ticketing"}), faq_ld(faqs)]
        page(url, f"Islamabad to {city} Flights & Air Tickets | AL ARBAB", f"Islamabad to {city} ({code}) air tickets on {al}. Licensed agency, e-tickets, group & student fares. Get today's fare on WhatsApp.",
             body, ld, f"islamabad to {city.lower()} flights, islamabad to {city.lower()} ticket price, {city.lower()} air ticket from pakistan", image=U(ROUTE_IMG[city], 1200) if city in ROUTE_IMG else None, priority="0.6")

def build_umrah_packages():
    for u in DATA["umrah"]:
        url = umrah_url(u)
        price = u["price"].replace("From ", "")
        f = "".join(f"<li>{e(x)}</li>" for x in u["features"])
        others = [o for o in DATA["umrah"] if o is not u]
        faqs = [(f"What is included in the {u['title']}?", ", ".join(u["features"]) + "."),
                (f"How much does the {u['title']} cost?", "Prices change with dates, airfare and hotel availability, so we quote on the day. Send your dates and family size on WhatsApp for today's price."),
                FAQ_UMRAH[1]]
        main = f'''<div class="stack">
<div class="block"><h2>{e(u["title"])} at a glance</h2><div class="feebox"><div><small>Price</small><b>Today's price on WhatsApp</b></div><div><small>Duration</small><b>{e(u["features"][0])}</b></div><div><small>Hotels</small><b>{e(u["features"][1])}</b></div></div></div>
<div class="block"><h2>What's included</h2><ul class="checks">{f}</ul></div>
<div class="block"><h2>Make it yours</h2><p>Choose your hotels in Makkah and Madinah, change the number of nights in each city, or upgrade transport. Tell us your dates and family size on WhatsApp for a tailored quote.</p>
<p style="margin-top:12px"><a class="btn wa" href="{wa(f"Hi, I want to book the {u['title']} Umrah package. Please send today's price.")}" target="_blank" rel="noopener">💬 Book this package</a></p></div>
<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>'''
        ol = "".join(f'<a href="{umrah_url(o)}">{e(o["title"])} <span>→</span></a>' for o in others)
        content = f'<div class="layout">{main}<aside class="aside">{ctacard(u["title"] + " Umrah")}<nav class="mini"><h3>Other Umrah packages</h3><a href="/umrah">All Umrah packages <span>→</span></a>{ol}</nav></aside></div>{cta_band("Begin your sacred journey")}'
        ph = pagehead("Umrah 2026", f"Umrah {e(u['title'])}", e(", ".join(u["features"][:3])) + ". Visa, flights and hotels arranged from Islamabad.", UMRAH_IMG, alt=f"Umrah {u['title']} – Makkah",
                      actions=f'<a class="btn wa" href="{wa(f"Hi, I want the {u['title']} Umrah package.")}" target="_blank" rel="noopener">💬 Book on WhatsApp</a>')
        body = shell("/umrah", [("Home", "/"), ("Umrah Packages", "/umrah"), (u["title"], None)], ph, content)
        ld = [crumbs_ld([("Home", "/"), ("Umrah Packages", "/umrah"), (u["title"], url)]),
              service_ld(f"Umrah {u['title']}", ", ".join(u["features"]), url, {"serviceType": "Umrah package"}), faq_ld(faqs)]
        page(url, f"Umrah {u['title']} 2026 from Islamabad | AL ARBAB", f"Umrah {u['title']} from Islamabad: " + ", ".join(u["features"]) + ". Get today's price on WhatsApp.",
             body, ld, f"umrah {u['title'].lower()}, umrah package islamabad 2026, umrah package from pakistan", image=AU(UMRAH_IMG, 1200), priority="0.7")

# ================================================================== guides & sitemap (SEO round)
DOC_GUIDE = [
 ("passport", "Passport", ["passport"], "Valid for at least 6 months beyond your return date, with 2 or more blank pages. Embassies often ask for copies of old passports and previous visas too.", "Directorate General of Immigration & Passports"),
 ("cnic", "CNIC", ["cnic"], "A clear A4 copy of your computerised national identity card, front and back.", "NADRA"),
 ("frc", "Family Registration Certificate (FRC) / MRC", ["frc", "family registration", "mrc", "marriage certificate"], "Shows your family members and relationships. Asked for family trips, sponsored applicants and children. MRC is the marriage registration certificate.", "NADRA"),
 ("bank", "Bank statement & account maintenance certificate", ["bank statement", "maintenance certificate"], "Usually the last 6 months, signed and stamped by the bank. Embassies look for a steady balance and a clear source of funds, not sudden large deposits.", "Your bank"),
 ("tax", "NTN & income tax returns", ["ntn", "tax return", "fbr"], "Your National Tax Number certificate and filed returns for the last 2–3 years show taxable income in Pakistan.", "FBR (Federal Board of Revenue)"),
 ("job", "Employment letter & salary slips", ["employment", "salary slip", "job letter", "occupation"], "A letter on company letterhead with your designation, salary, joining date and approved leave, plus recent salary slips.", "Your employer"),
 ("business", "Business documents", ["business", "chamber of commerce", "secp"], "For owners: Chamber of Commerce membership, SECP or business registration, letterhead and business bank statement.", "Chamber of Commerce / SECP"),
 ("polio", "Polio vaccination certificate", ["polio"], "Many destinations ask Pakistani travellers for a valid polio vaccination certificate (the yellow card). Get it before you travel.", "Authorised vaccination centres"),
 ("insurance", "Travel medical insurance", ["insurance"], "Schengen states require at least €30,000 medical cover valid for the whole stay. Other countries may ask for it too.", "Licensed insurers (Jubilee, Adamjee, United, EFU…)"),
 ("bookings", "Flight reservation & hotel booking", ["flight", "hotel", "accommodation", "lodging", "itinerary"], "A return flight reservation and hotel bookings for every night, matching your dates. Many embassies prefer reservations over paid tickets.", "Your travel agent"),
 ("cover", "Cover letter", ["cover letter"], "Explains the purpose of the trip, the day-by-day plan, who pays, and your ties to Pakistan.", "You (we help draft it)"),
 ("photos", "Photographs", ["photo"], "Recent passport-size photos on a white background, usually 35×45 mm; some embassies need 50×50 mm.", "Any professional photo studio"),
 ("invite", "Invitation letter", ["invitation"], "For family or business visits: a letter from your host or the inviting company with their ID or registration details.", "Your host abroad"),
]

def doc_count(keys):
    return sum(1 for c in COUNTRIES.values() if any(any(k in d.lower() for k in keys) for d in c["docs"]))

def build_guides():
    guides = []
    # 1. visa fees table
    url = "/guides/visa-requirements-for-pakistani-passport"
    blocks = ""
    for r in regions_ordered():
        cs = by_rank([c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]])
        if not cs:
            continue
        vv = visit_visa(r["slug"])
        rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{len(c["docs_clean"])} documents</td><td>{e(short_time(vv["processingTime"]) if vv else "—")}</td><td>{"Yes" if any("polio" in d.lower() for d in c["docs_clean"]) else "—"}</td></tr>' for c in cs)
        blocks += f'<div class="block" id="{r["slug"]}"><h2>{e(r["name"])}</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Country</th><th>Checklist</th><th>Typical processing</th><th>Polio card</th></tr></thead><tbody>{rows}</tbody></table></div></div>'
    special = "".join(f'<tr><td><a class="link" href="/countries/{rs}">{e(REGIONS[rs]["name"])}</a></td><td>{e(REGIONS[rs]["visas"][0]["name"])}</td><td>{e(short_time(REGIONS[rs]["visas"][0]["processingTime"]))}</td></tr>' for rs in ("united-kingdom", "united-states", "canada", "australia"))
    faqs = [("Why don't you list visa fees?", "Embassy charges change often with exchange rates and policy, so a published number would soon be wrong. Message us on WhatsApp and we confirm the current all-in cost for your case."),
            ("Which documents do almost all countries ask for?", "A valid passport, photographs, a bank statement and confirmed flight and hotel bookings appear on almost every checklist. See our documents guide for what each one means."),
            ("How long does processing take?", "It ranges from a few days for e-visas to several weeks for Schengen, UK and US visas. Apply early, especially before summer and Eid travel.")]
    toc = "".join(f'<a href="#{r["slug"]}">{e(r["name"])} <span>↓</span></a>' for r in regions_ordered() if [c for c in BY_REGION.get(r["slug"], []) if c["region"] == r["slug"]])
    main = f'''<div class="stack"><div class="block"><h2>How to use this list</h2><p>This page compares visa requirements for Pakistani passport holders across our {len(COUNTRIES)} country guides, grouped by region: how many documents each checklist has, typical processing time, and whether a polio vaccination card is listed. Click a country for its full document list.</p><p class="note" style="margin-top:12px">Updated {UPDATED}. Rules change; we confirm the latest checklist for your case on WhatsApp.</p></div>
<div class="block"><h2>UK, USA, Canada &amp; Australia</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Destination</th><th>Main visit visa</th><th>Typical processing</th></tr></thead><tbody>{special}</tbody></table></div></div>
{blocks}<div class="block"><h2>FAQs</h2>{faq_html(faqs)}</div></div>'''
    guides.append((url, "Visa requirements for Pakistani passport holders 2026", f"Compare document checklists and processing times in {len(COUNTRIES)} country guides, grouped by region.",
                   f"Visa Requirements for Pakistani Passport 2026 ({len(COUNTRIES)} Guides)",
                   f"Visa requirements for Pakistani passport holders in 2026: compare document checklists and processing times in {len(COUNTRIES)} country guides including Schengen, UK, USA, Dubai and Asia.",
                   main, toc, faqs, UNS["fr"], "visa requirements for pakistani passport, visa for pakistani, which countries visa pakistan, visa processing time pakistan"))
    # 2. schengen requirements
    url = "/guides/schengen-visa-requirements-from-pakistan"
    sc = REGIONS["schengen"]
    route = {c: v for c, v, _ in APPOINTMENT_CENTRES}
    rows = "".join(f'<tr><td><a class="link" href="{c["url"]}">{e(c["name"])}</a></td><td>{e(route.get(c["name"], "VFS / BLS / Gerry\'s (by embassy)"))}</td><td>{e(c["popularPlaces"][0] if c["popularPlaces"] else "—")}</td></tr>' for c in BY_REGION["schengen"])
    gen = "".join(f"<li>{e(x)}</li>" for x in sc["generalRequirements"])
    sfaq = [(f["q"], f["a"]) for f in sc["faqs"]] + [q for q in FAQ_GENERAL if "Schengen" in q[0] or "bank" in q[0].lower()][:2] + [
        ("Can I get a Schengen visa in 7 days?", "Rarely. Embassies normally decide within 15 calendar days of your appointment, and it can take longer in peak season. Plan 4–6 weeks ahead, including the wait for an appointment."),
        ("How can I get a Schengen visa more easily from Pakistan?", "Apply to the embassy of the country where you will spend the most nights, show a steady 6-month bank history with a clear source of income, prove strong ties to Pakistan, and make your hotel, flight and insurance dates match your cover letter exactly."),
        ("Which Schengen country should I apply to?", "The country where you will spend the most nights. If your stays are equal, apply to the country you enter first. Applying to an 'easier' embassy that doesn't match your itinerary is a common reason for refusal.")]
    main = f'''<div class="stack"><div class="block"><h2>Schengen visa from Pakistan in short</h2><p>{e(sc["intro"])}</p><p style="margin-top:10px">One Schengen visa lets you visit all 29 member states. Apply at the embassy of the country where you will spend the most nights, or the country you enter first if your stays are equal.</p></div>
<div class="block" id="requirements"><h2>Documents every Schengen embassy asks for</h2><ul class="checks">{gen}</ul><p style="margin-top:12px"><a class="link" href="/guides/visa-documents-explained">What each document means →</a></p></div>
<div class="block" id="countries"><h2>All 29 Schengen countries compared</h2><div style="overflow-x:auto"><table class="tbl"><thead><tr><th>Country</th><th>Where you apply</th><th>Top attraction</th></tr></thead><tbody>{rows}</tbody></table></div></div>
<div class="block" id="process"><h2>Step-by-step process</h2><ol class="steps">{steps_html([(x["title"], x["desc"]) for x in sc["stepByStep"]])}</ol></div>
<div class="block" id="refusal"><h2>Why Schengen visas get refused</h2><ul class="refuse">{"".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in REFUSAL)}</ul></div>
<div class="block" id="faqs"><h2>FAQs</h2>{faq_html(sfaq)}</div></div>'''
    toc = "".join(f'<a href="#{i}">{n} <span>↓</span></a>' for i, n in [("requirements", "Documents"), ("countries", "29 countries"), ("process", "Process"), ("refusal", "Refusal reasons"), ("faqs", "FAQs")])
    guides.append((url, "Schengen visa requirements from Pakistan (2026)", "Documents, application route and process for all 29 Schengen countries, in one place.",
                   "Schengen Visa Requirements from Pakistan 2026 | AL ARBAB",
                   "Schengen visa requirements for Pakistanis in 2026: document checklist, €30,000 insurance rule, where to apply (VFS, BLS, Gerry's) and all 29 countries compared.",
                   main, toc, sfaq, UNS["it"], "schengen visa requirements pakistan, schengen visa documents pakistan, schengen visa from islamabad, easiest schengen visa pakistan"))
    # 3. documents explained
    url = "/guides/visa-documents-explained"
    items = ""
    for i, name, keys, what, issuer in DOC_GUIDE:
        n = doc_count(keys)
        items += f'<div class="block" id="{i}"><h2>{e(name)}</h2><p>{e(what)}</p><div class="feebox" style="margin-top:12px;grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Where to get it</small><b>{e(issuer)}</b></div><div><small>Asked by</small><b>{n} of {len(COUNTRIES)} country guides</b></div></div></div>'
    dfaq = [("Which document causes the most refusals?", "Weak or unexplained bank statements are the most common problem, followed by missing proof of ties to Pakistan."),
            ("Do I need translations?", "Documents in Urdu usually need an English translation; some embassies also want attestation. We tell you exactly which ones for your case.")]
    main = f'''<div class="stack"><div class="block"><h2>Visa documents in plain words</h2><p>Every embassy checklist uses the same handful of documents. Here is what each one is, where Pakistani applicants get it, and how many of the {len(COUNTRIES)} country guides on our site ask for it.</p></div>{items}<div class="block"><h2>FAQs</h2>{faq_html(dfaq)}</div></div>'''
    toc = "".join(f'<a href="#{i}">{e(n.split(" (")[0])} <span>↓</span></a>' for i, n, *_ in DOC_GUIDE)
    guides.append((url, "Visa documents explained for Pakistani applicants", "FRC, maintenance certificate, polio card, NTN, insurance and more: what each document is and where to get it.",
                   "Visa Documents Explained: FRC, Bank Statement, Polio | AL ARBAB",
                   "What FRC, bank maintenance certificate, NTN, polio certificate, travel insurance and cover letters mean for your visa from Pakistan, and where to get each one.",
                   main, toc, dfaq, UNS["g_passport"], "visa documents pakistan, frc for visa, bank maintenance certificate visa, polio certificate travel pakistan, ntn for visa"))
    for url, h1, lead, title, desc, main, toc, faqs, pid, kw in guides:
        aside = f'<aside class="aside"><nav class="mini toc" aria-label="On this page"><h3>On this page</h3>{toc}</nav>{ctacard("visa")}<nav class="mini"><h3>More guides</h3>' + "".join(f'<a href="{g[0]}">{e(g[1])} <span>→</span></a>' for g in guides if g[0] != url) + "</nav></aside>"
        ph = pagehead(f"Guide · Updated {UPDATED}", e(h1), e(lead), pid, alt=h1, actions=f'<a class="btn wa" href="{wa("Hi, I have a question about " + h1 + ".")}" target="_blank" rel="noopener">💬 Ask an adviser</a>')
        body = shell("/guides", [("Home", "/"), ("Guides", "/guides"), (h1, None)], ph, f'<div class="layout">{main}{aside}</div>{cta_band()}')
        art = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "image": U(pid, 1200), "datePublished": TODAY, "dateModified": TODAY,
               "author": {"@type": "Organization", "name": NAME, "url": BASE + "/"}, "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + url, "inLanguage": "en-PK"}
        page(url, title, desc, body, [crumbs_ld([("Home", "/"), ("Guides", "/guides"), (h1, url)]), art, faq_ld(faqs)], kw, image=U(pid, 1200), priority="0.8")
    cards = "".join(f'<a class="vt" href="{g[0]}"><h3>{e(g[1])}</h3><p>{e(g[2])}</p><span class="go">Read the guide →</span></a>' for g in guides) + "".join(build_guides2())
    ph = pagehead("Visa guides", "Visa guides for<br>Pakistani travellers", "Plain-language guides built from the checklists we use every day in our Blue Area office: requirements, documents and the Schengen process.", UNS["g_passport2"], alt="Visa guides", actions=WA_HERO)
    body = shell("/guides", [("Home", "/"), ("Guides", None)], ph, sec("All visa guides", "", f'<div class="grid">{cards}</div>') + cta_band())
    page("/guides", "Visa Guides for Pakistani Travellers 2026 | AL ARBAB",
         "Visa guides for Pakistani travellers: requirements in @N@ country guides, Schengen requirements from Pakistan, and visa documents explained, from AL ARBAB in Islamabad.",
         body, [crumbs_ld([("Home", "/"), ("Guides", "/guides")])], priority="0.8")

LEGAL_URLS = ["/terms", "/privacy", "/fees-and-refunds", "/disclaimer", "/compliance", "/editorial-policy"]
SECTIONS = [("Main pages", lambda u: u.count("/") == 1 and not u.startswith("/guides") and u not in LEGAL_URLS), ("Legal & trust", lambda u: u in LEGAL_URLS), ("Visa services", lambda u: u.startswith("/visa-services/")),
            ("Guides", lambda u: u.startswith("/guides")), ("Regions & visa types", lambda u: u.startswith("/countries/") and (u.count("/") == 2 or "/visa/" in u)),
            ("Countries", lambda u: u.startswith("/countries/") and u.count("/") == 3 and "/visa/" not in u), ("Flights", lambda u: u.startswith("/air-ticketing/")),
            ("Umrah, packages & tours", lambda u: u.startswith("/umrah/") or u.startswith("/packages/") or u.startswith("/tours/") or u.startswith("/pakistan-tours") or u == "/honeymoon-packages")]

def page_title(html):
    m = re.search(r"<title>([^<]*)</title>", html)
    return H.unescape(m.group(1)).replace(" | AL ARBAB TRAVEL AND TOURS", "").replace(" | AL ARBAB", "") if m else ""

def build_editorial():
    main = f'''<div class="stack">
<div class="block"><h2>Where our visa information comes from</h2><p>Every country page is built from the document checklists our consultants use for real applications in our Blue Area office. Where a government publishes its rules online, we link that official source on the page so you can check it yourself.</p></div>
<div class="block"><h2>How we keep it current</h2><ul class="checks"><li>Pages show the month they were last updated.</li><li>When an embassy or visa centre changes a requirement, we update the checklist and the date.</li><li>We don't publish embassy fees or package prices, because they change too often to stay accurate online. We confirm the current cost on WhatsApp before you pay.</li><li>Processing times are shown as typical ranges, never promises.</li></ul></div>
<div class="block"><h2>What we never do</h2><ul class="refuse"><li><b>Guarantee a visa</b><span>The decision always belongs to the embassy, high commission or consulate.</span></li><li><b>Invent reviews or success numbers</b><span>Reviews on this site come from real clients.</span></li><li><b>Ask for false documents</b><span>We only work with genuine, verifiable documents.</span></li></ul></div>
<div class="block"><h2>Found something out of date?</h2><p>Tell us on WhatsApp at <a class="link" href="{WA}" target="_blank" rel="noopener">{PHONE}</a> or email <a class="link" href="mailto:{EMAIL}">{EMAIL}</a> and we will check and correct it.</p></div>
</div>'''
    ph = pagehead("Trust", "How we keep our<br>visa information accurate", f"Sources, update process and the promises we don't make at {NAME}.")
    body = shell("/editorial-policy", [("Home", "/"), ("Editorial Policy", None)], ph, f'<div style="margin-top:20px">{main}</div>')
    page("/editorial-policy", "Editorial Policy: How We Keep Visa Info Accurate | AL ARBAB",
         f"Where AL ARBAB's visa checklists come from, how often they are updated, why we don't publish fees, and what we never promise.",
         body, [crumbs_ld([("Home", "/"), ("Editorial Policy", "/editorial-policy")])], priority="0.4")

def build_sources():
    """One page that gathers every official source linked from the country and region pages."""
    groups, total, dests = "", 0, 0
    seen_region = set()
    for reg in REGION_ORDER:
        items = []
        for c in BY_REGION.get(reg, []):
            s = OFFICIAL.get(c["slug"], [])
            if s: items.append((c, s))
        rs = REGION_OFFICIAL.get(reg, [])
        if not items and not rs:
            continue
        r = REGIONS.get(reg)
        rn = r["name"] if r else reg.replace("-", " ").title()
        body = ""
        if rs:
            body += '<h3 class="sub-h">For the whole region</h3><ul class="srcs">' + "".join(f'<li><a href="{u}" target="_blank" rel="noopener nofollow">{e(n)} ↗</a></li>' for n, u in rs) + "</ul>"
            total += len(rs)
        for c, s in items:
            dests += 1; total += len(s)
            body += f'<h3 class="sub-h"><a href="{c["url"]}">{e(c["name"])}</a></h3><ul class="srcs">' + "".join(f'<li><a href="{u}" target="_blank" rel="noopener nofollow">{e(n)} ↗</a></li>' for n, u in s) + "</ul>"
        groups += f'<div class="block"><h2>{e(rn)}</h2>{body}</div>'
    intro = (f'<div class="block"><h2>How to use this page</h2><p>Each country page on this site links the official portal or embassy page its checklist is based on. '
             f'This page collects them in one place: <b>{total} official links across {dests} destinations</b>. Rules can change at short notice, so always confirm on the official page. '
             f'<a class="link" href="/editorial-policy">How we keep our information accurate →</a></p></div>')
    ph = pagehead("Trust", "Official sources for<br>every visa guide", f"The government and embassy pages behind our country guides: {total} links, {dests} destinations.")
    body = shell("/sources", [("Home", "/"), ("Official sources", None)], ph, f'<div class="stack" style="margin-top:20px">{intro}{groups}</div>')
    page("/sources", "Official Sources for Our Visa Guides | AL ARBAB",
         f"The official government and embassy pages behind our visa guides: {total} links across {dests} destinations, in one place.",
         body, [crumbs_ld([("Home", "/"), ("Official sources", "/sources")])], priority="0.5")

def build_html_sitemap():
    groups = ""
    for name, test in SECTIONS:
        rk = country_rank(); crank = {c["url"]: rk[c["url"]] for c in COUNTRIES.values()}
        items = sorted(((page_title(h), u) for u, (h, _, noi) in PAGES.items() if not noi and u != "/" and test(u)), key=lambda t: (crank.get(t[1], 10**6), t[0]))
        if items:
            groups += f'<div class="block"><h2>{e(name)} ({len(items)})</h2><ul class="smap">' + "".join(f'<li><a href="{u}">{e(t)}</a></li>' for t, u in items) + "</ul></div>"
    ph = pagehead("Sitemap", "All pages", f"Every page on the {NAME} website, grouped by section.")
    body = shell("/sitemap", [("Home", "/"), ("Sitemap", None)], ph, f'<div class="stack" style="margin-top:20px">{groups}</div>')
    page("/sitemap", "Sitemap | AL ARBAB TRAVEL AND TOURS", f"All pages on the {NAME} website: visa services, {len(COUNTRIES)} country guides, regions, flights, Umrah packages and travel guides.",
         body, [crumbs_ld([("Home", "/"), ("Sitemap", "/sitemap")])], priority="0.3", noindex=True)   # list page for visitors; links are followed, the page itself stays out of search results

# ================================================================== international tours & honeymoon (confirmed service)
TOURS = [  # (url slug, country slug, display name, honeymoon-friendly, linked package id or None)
 ("maldives-tour-package-from-pakistan", "maldives", "Maldives", True, None),
 ("turkey-tour-package-from-pakistan", "turkey", "Turkey", True, None),
 ("baku-tour-package-from-islamabad", "azerbaijan", "Baku, Azerbaijan", True, None),
 ("thailand-tour-package-from-islamabad", "thailand", "Thailand", True, "thailand-phuket"),
 ("bali-tour-package-from-pakistan", "indonesia", "Bali, Indonesia", True, "indonesia-bali"),
 ("dubai-tour-package-from-pakistan", "united-arab-emirates", "Dubai", True, "dubai-desert-safari"),
 ("malaysia-tour-package-from-pakistan", "malaysia", "Malaysia", True, "malaysia-kl"),
 ("singapore-tour-package-from-pakistan", "singapore", "Singapore", False, "singapore-city"),
 ("nepal-tour-package-from-pakistan", "nepal", "Nepal", False, "nepal-himalayas"),
 ("europe-tour-package-from-pakistan", "italy", "Europe (Italy & Schengen)", True, "italy-schengen"),
]
ARRANGE = ["Return flights from Islamabad (or Lahore / Karachi on request)", "Visa file preparation and appointment where needed", "Hotels or resorts in the category you choose",
           "Airport transfers and sightseeing on request", "Travel insurance", "WhatsApp support during the trip, Mon–Sat, 9am–8pm"]

ROUTE_SHORT = {"Online e-visa": "E-visa", "Online ETA": "ETA", "Visa on arrival / e-visa": "On arrival",
               "Schengen visa (embassy / visa centre)": "Schengen", "Embassy / visa centre": "Embassy", "E-visa or embassy": "E-visa / embassy"}

def tour_url(slug):
    return "/tours/" + slug

def build_tours():
    pk = {p["id"]: p for p in PACKAGES}
    cards = []
    for slug, cs, name, honey, pid in TOURS:
        c = COUNTRIES[cs]
        p = pk.get(pid)
        url = tour_url(slug)
        gal = "".join(f'<figure>{picture(g[1], f"{g[0]}, {c["name"]}", 800, 600, "(max-width:600px) 100vw, 300px")}<figcaption class="pl">{e(g[0])}</figcaption></figure>' for g in c["gallery"])
        route = visa_route(c)
        if p:
            pkg_block = (f'<div class="block" id="package"><h2>Ready-made package: {e(p["title"])}</h2><div class="feebox" style="grid-template-columns:repeat(2,minmax(0,1fr))"><div><small>Duration</small><b>{e(p["duration"])}</b></div><div><small>Stay</small><b>{e(p["amenities"])}</b></div></div>'
                         f'<ul class="checks" style="margin-top:12px">' + "".join(f"<li>{e(h)}</li>" for h in p["highlights"]) + f'</ul><p style="margin-top:12px"><a class="link" href="{p["url"]}">Full package details →</a> Prefer different dates or hotels? We tailor it.</p></div>')
        else:
            pkg_block = (f'<div class="block" id="package"><h2>Your {e(name)} trip, planned around you</h2><p>We build each {e(name)} trip to your dates, budget and hotel category rather than selling one fixed itinerary. '
                         f'Tell us how many nights, who is travelling and the kind of stay you want, and we send a full plan with flights, hotels and visa on WhatsApp.</p></div>')
        honey_block = (f'<div class="block" id="honeymoon"><h2>{e(name)} honeymoon from Pakistan</h2><p>Planning a honeymoon? Tell us your wedding date and we plan the trip around it, with couple-friendly hotels, private transfers on request and the visa handled for both of you. '
                       f'Newly married couples usually need a <a class="link" href="/guides/visa-documents-explained#frc">marriage registration certificate (MRC)</a> for the visa file.</p></div>') if honey else ""
        faqs = [(f"Do Pakistanis need a visa for {c['name']}?", (f"Pakistani passport holders can get a visa on arrival in {c['name']} if they meet the entry conditions." if route.startswith("Visa on arrival") else f"Yes. You apply through {ROUTE_PHRASE.get(route, route.lower())}. We prepare the file as part of your tour.") + f" See the full {c['name']} checklist on our visa page."),
                (f"How much does a {name} tour package from Pakistan cost?", "Prices change with dates, airfare and hotel availability, so we quote on the day. Send your dates and number of travellers on WhatsApp for today's price."),
                (f"Can you plan a {name} trip from Lahore or Karachi?", "Yes. Flights can start from Islamabad, Lahore or Karachi; the visa file is prepared through our Islamabad office and documents can be shared on WhatsApp.")]
        main = f'''<div class="stack">
<div class="block answer" id="answer"><h2>{e(name)} tour from Pakistan: quick answer</h2><p>{e(f"AL ARBAB TRAVEL AND TOURS arranges {name} trips from Islamabad with flights, hotels and the visa in one booking. ")}{e("Pakistani travellers can get a visa on arrival if they meet the entry conditions. " if route.startswith("Visa on arrival") else f"The visa is {ROUTE_PHRASE.get(route, route.lower())}; we prepare the file for you. ")}Get today's price and a plan for your dates on <a class="link" href="{wa("Hi, I want a " + name + " tour package.")}" target="_blank" rel="noopener">WhatsApp</a>.</p></div>
{pkg_block}
{honey_block}
<div class="block" id="places"><h2>Places you can visit in {e(name)}</h2><div class="gallery">{gal}</div></div>
<div class="block" id="included"><h2>What we arrange</h2><ul class="checks">{"".join(f"<li>{e(x)}</li>" for x in ARRANGE)}</ul></div>
<div class="block" id="visa"><h2>{e(c["name"])} visa for this trip</h2><p>{e(c["name"])} checklist: {len(c["docs_clean"])} documents. How you apply: {e(route.lower())}. <a class="link" href="{c["url"]}">See the full {e(c["name"])} visa requirements →</a></p></div>
<div class="block" id="how"><h2>How booking works</h2><ol class="steps">{steps_html([("Share your plan", "Dates, number of travellers and budget on WhatsApp."), ("Get a quote", "Flights, hotels and visa costed for your dates."), ("Visa & bookings", "We prepare the visa file and confirm flights and hotels."), ("Travel", "Documents and WhatsApp support for the trip, Mon–Sat, 9am–8pm.")])}</ol></div>
<div class="block" id="faqs"><h2>FAQs</h2>{faq_html(faqs)}</div>
</div>'''
        others = "".join(f'<a href="{tour_url(t[0])}">{e(t[2])} tour <span>→</span></a>' for t in TOURS if t[0] != slug)
        aside = f'<aside class="aside">{ctacard(name + " tour")}<nav class="mini"><h3>More tours</h3><a href="/honeymoon-packages">Honeymoon packages <span>→</span></a>{others}</nav></aside>'
        ph = pagehead(f"Tour package · {UPDATED}", f"{e(name)} tour package<br>from Pakistan", f"Flights, hotels and visa for {e(name)} in one booking, planned to your dates from Blue Area, Islamabad.", c["img"], c["code"], name,
                      actions=f'<a class="btn wa" href="{wa("Hi, I want a " + name + " tour package. My dates are: ")}" target="_blank" rel="noopener">💬 Plan my trip</a><a class="btn light" href="{c["url"]}">Visa requirements</a>')
        body = shell("/packages", [("Home", "/"), ("Packages", "/packages"), (f"{name} tour", None)], ph, f'<div class="layout">{main}{aside}</div>{cta_band()}')
        ld = [crumbs_ld([("Home", "/"), ("Packages", "/packages"), (f"{name} tour", url)]),
              {"@context": "https://schema.org", "@type": "TouristTrip", "name": f"{name} tour package from Pakistan", "description": f"Flights, hotels and visa for {name}, planned to your dates.",
               "touristType": ["Couples", "Families"] if honey else ["Families", "Groups"], "provider": {"@id": BASE + "/#org"}, "image": AU(c["img"], 1200) if c["img"] else LOGO,
               "itinerary": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": g[0]} for i, g in enumerate(c["gallery"])]}}, faq_ld(faqs)]
        title = f"{name} Tour Package from Pakistan 2026 | AL ARBAB"
        if len(title) > 65:
            title = f"{name} Tour Package from Pakistan | AL ARBAB"
        page(url, title, f"{name} tour package from Pakistan 2026: flights, hotels and visa in one booking from Islamabad. Honeymoon and family trips planned to your dates. Price on WhatsApp.",
             body, ld, f"{name.lower()} tour package from pakistan, {name.lower()} honeymoon package, {name.lower()} tour from islamabad", image=AU(c["img"], 1200) if c["img"] else None, priority="0.8")
        cards.append(ncard(url, c["img"], f"{name} tour package", "Honeymoon & family" if honey else "Family & groups", "Plan my trip →",
                           flag(c["code"], "", 40), f"{name}", ", ".join(g[0].split(",")[0] for g in c["gallery"][:2]), "Visa", ROUTE_SHORT.get(route, "Embassy"), "Booking", "WhatsApp"))
    # honeymoon hub
    hon = [t for t in TOURS if t[3]]
    hcards = "".join(cards[i] for i, t in enumerate(TOURS) if t[3])
    faqs = [("Which honeymoon destinations are popular from Pakistan?", "Maldives, Turkey, Bali, Thailand, Dubai, Baku and Europe are the destinations couples ask us about most."),
            ("What documents do newly married couples need?", "Both passports, the marriage registration certificate (MRC) or updated FRC, bank statements and the usual visa documents for the destination."),
            ("How early should we book a honeymoon?", "Six to eight weeks before the wedding is comfortable for most visas; Schengen and UK need more time, especially in summer.")]
    content = f'''<section class="sec"><div class="rgrid">{hcards}</div></section>
<section class="sec reveal"><div class="prose"><h2>Honeymoon packages from Islamabad, planned to your wedding date</h2><p>We plan honeymoons from Pakistan to {", ".join(t[2] for t in hon)}. Each trip is built around your dates and budget, with flights, hotels or resorts, transfers on request and both visas prepared together.</p><h3>What we arrange</h3><ul class="checks">{"".join(f"<li>{e(x)}</li>" for x in ARRANGE)}</ul></div></section>
{sec("FAQs", "", faq_html(faqs))}{cta_band("Planning your honeymoon?", "Send your wedding date, preferred destination and budget on WhatsApp and we reply with options.")}'''
    ph = pagehead("Honeymoon", "Honeymoon packages<br>from Pakistan", "Maldives, Turkey, Bali, Thailand, Dubai, Baku and Europe — flights, hotels and visas for both of you, planned from Blue Area, Islamabad.", COUNTRIES["maldives"]["img"], alt="Maldives honeymoon",
                  actions=f'<a class="btn wa" href="{wa("Hi, we are planning our honeymoon. Wedding date: ")}" target="_blank" rel="noopener">💬 Plan our honeymoon</a>')
    body = shell("/packages", [("Home", "/"), ("Packages", "/packages"), ("Honeymoon packages", None)], ph, content)
    page("/honeymoon-packages", "Honeymoon Packages from Pakistan 2026 | AL ARBAB",
         "Honeymoon packages from Pakistan to Maldives, Turkey, Bali, Thailand, Dubai, Baku and Europe: flights, hotels and visas for both of you, planned from Islamabad.",
         body, [crumbs_ld([("Home", "/"), ("Packages", "/packages"), ("Honeymoon packages", "/honeymoon-packages")]), faq_ld(faqs)],
         "honeymoon package from pakistan, honeymoon packages from islamabad, maldives honeymoon package from pakistan, turkey honeymoon package", priority="0.8")
    return cards

# ================================================================== evergreen guides (round 2)
def _ul(items, cls="checks"):
    return f'<ul class="{cls}">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

GUIDES2 = [
 dict(url="/guides/bank-statement-for-visa-from-pakistan", pid=UNS["g_bank"],
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
 dict(url="/guides/visa-cover-letter-pakistan", pid=UNS["g_letter"],
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
 dict(url="/guides/visa-refused-what-to-do", pid=UNS["g_plan"],
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
       ("Getting a policy in Islamabad", "<p>We issue verifiable policies from Pakistani insurers through our Blue Area office once we have your passport details and travel dates. We reply during office hours. See <a class=\"link\" href=\"/travel-insurance\">travel insurance</a>.</p>")],
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

 dict(url="/guides/noc-letter-for-visa-pakistan", pid=UNS["g_letter"],
      h1="NOC letter for a visa from Pakistan", title="NOC Letter for Visa from Pakistan: Who Needs It and What to Include",
      lead="When an employer or institute letter is asked for, what it should say and what officers check in it.",
      desc="NOC letter for a visa from Pakistan: when employers or institutes are asked for one, what the letter should contain and common mistakes.",
      kw="noc letter for visa pakistan, employer noc visa, noc for visit visa, job letter for visa pakistan",
      sections=[
       ("What an NOC is", "<p>A No Objection Certificate (NOC) is a letter from your employer or institute saying you are allowed to travel and that you will return to your job or studies. Embassies ask for it, or for an equivalent employment letter, to confirm your ties to Pakistan.</p>"),
       ("What the letter should contain", _ul(["<b>Your details</b>: full name as on the passport, CNIC number, designation and joining date", "<b>Travel purpose and dates</b>: country, approximate dates and the approved leave period", "<b>Return statement</b>: that you will resume duty after the trip", "<b>Company details</b>: letterhead, stamp, signature and a contact number or email"])),
       ("Common mistakes", _ul(["Name or designation that does not match the salary slips or bank statement", "Leave dates that do not match the trip dates in the application", "A letter with no stamp, no signature or no contact details", "Unsigned copies sent instead of the original"])),
       ("Business owners and students", "<p>If you run a business, officers usually look for registration documents, a tax number and recent business bank statements instead of an employer NOC. Students normally provide a letter from the institute with enrolment and leave details. Your exact checklist depends on the country, so see the <a class=\"link\" href=\"/countries\">country guide</a> you are applying for.</p>")],
      faqs=[("Is an NOC compulsory for every visa?", "No. It depends on the embassy and your profile. Many checklists ask for an employment letter or NOC for salaried applicants; the country page lists what applies."),
            ("Can a self-employed person get an NOC?", "A self-employed applicant normally shows business registration and tax documents instead. We tell you what the embassy expects for your case."),
            ("Does an NOC mean the visa will be approved?", "No. It is one supporting document. The embassy makes the final decision.")]),
 dict(url="/guides/visa-interview-preparation-pakistan", pid=UNS["g_passport"],
      h1="Visa interview preparation for Pakistani applicants", title="Visa Interview Preparation for Pakistani Applicants",
      lead="Plain, honest preparation for a short embassy interview: what is usually asked and how to answer consistently.",
      desc="Visa interview preparation for Pakistani applicants: common questions, how to answer clearly and consistently, and what to carry to the appointment.",
      kw="visa interview questions pakistan, embassy interview preparation, visa interview tips, how to pass visa interview pakistan",
      sections=[
       ("What the officer wants to confirm", "<p>The interview is short. The officer checks three things: the purpose of the trip is genuine, you can pay for it, and you have good reasons to return to Pakistan. Answers that match your documents are the strongest preparation.</p>"),
       ("Questions that are commonly asked", _ul(["Where are you going, for how long and why?", "Who is paying for the trip?", "What do you do for work or study, and for how long?", "Where will you stay and what is your plan?", "Have you travelled abroad before?"])),
       ("How to answer", _ul(["Answer only what is asked, in short and clear sentences", "Keep dates, employer, income and itinerary exactly as in your file", "Bring your original documents in the same order as the checklist", "If you do not know something, say so instead of guessing"])),
       ("What not to do", _ul(["Do not memorise answers that differ from your documents", "Do not carry documents you cannot explain", "Do not argue with the officer if asked for more papers"]))],
      faqs=[("Does every visa need an interview?", "No. Many e-visas and several visa-centre applications have no interview. The country page tells you what applies."),
            ("Can an agency attend the interview for me?", "No. Where an interview or biometrics is required you attend in person. We prepare your file and brief you before the appointment."),
            ("What if I am asked for an extra document?", "Provide it if you have it, or follow the officer's instructions on how to submit it. Message us if you need help with the next step.")]),
 dict(url="/guides/visa-appointment-booking-pakistan", pid=UNS["g_plan"],
      h1="Visa appointment booking from Pakistan", title="Visa Appointment Booking from Pakistan: How It Works",
      lead="How embassy and visa-centre appointments generally work, and how to avoid losing a slot.",
      desc="Visa appointment booking from Pakistan: how embassy and visa-centre slots generally work, what to prepare first and how to avoid losing a booking.",
      kw="visa appointment pakistan, vfs appointment islamabad, embassy appointment booking, visa appointment slot",
      sections=[
       ("Where appointments are made", "<p>Some countries use the embassy portal, others a visa application centre such as VFS Global or BLS. The route differs by country and can change, so check the official page on the country guide before you book.</p>"),
       ("Prepare before you book", _ul(["A valid passport with enough validity and blank pages", "Photographs in the size the embassy asks for", "Your document file, ready in the order of the checklist", "Travel dates that fit the validity of the visa you need"])),
       ("Avoid losing the slot", _ul(["Use the exact name and passport number from the passport", "Do not book several slots under different details", "Keep the confirmation page and bring it with the original documents", "Arrive on time with only the documents asked for"])),
       ("How we help", "<p>We check your file against the checklist, help you choose the right category and guide you through booking. You attend biometrics or the interview in person where required. Final decision rests with the embassy.</p>")],
      faqs=[("Can I book an appointment without a complete file?", "You can, but preparing the file first avoids having to reschedule. A missing document at the counter can mean a wasted slot."),
            ("Can I reschedule a booked appointment?", "Many portals allow it within their own rules. Check the confirmation email for the conditions."),
            ("Does an appointment mean the visa is approved?", "No. It only lets you submit your file. The embassy makes the decision.")]),
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

# ---------------------------------------------------------------- Pakistan tours (no prices; conditions are seasonal)
PGPIC = {n: f"/assets/cards/{n}.webp?v={asset_hash('cards/' + n + '.webp')}" for n in ("pg-dest", "pg-air", "pg-pkg")}
PKPIC = {n: f"/assets/cards/{n}.webp?v={asset_hash('cards/' + n + '.webp')}" for n in ("pk-valley", "pk-hunza", "pk-skardu", "pk-swat", "pk-naran", "pk-khunjerab")}
PK_TOURS = [
 dict(slug="hunza", img="pk-hunza", name="Hunza Valley", region="Gilgit-Baltistan",
      intro="Hunza sits on the Karakoram Highway in Gilgit-Baltistan, with mountain views, old forts and lakes along the route.",
      places=["Baltit Fort", "Altit Fort", "Attabad Lake", "Passu Cones", "Hussaini Suspension Bridge", "Khunjerab Pass (seasonal)"],
      note="Mountain road conditions and landslides can change travel times. Khunjerab Pass is open only in certain months."),
 dict(slug="skardu", img="pk-skardu", name="Skardu", region="Gilgit-Baltistan",
      intro="Skardu is the gateway to high lakes and plateaus in Baltistan, reached by road on the Karakoram Highway or by flight when weather allows.",
      places=["Shangrila Lake", "Deosai National Park (seasonal)", "Upper Kachura Lake", "Shigar Fort", "Satpara Lake"],
      note="Flights to Skardu depend on weather and may be rescheduled. Deosai is accessible only in the summer months."),
 dict(slug="swat-kalam", img="pk-swat", name="Swat & Kalam", region="Khyber Pakhtunkhwa",
      intro="Swat is a green river valley in Khyber Pakhtunkhwa, with Kalam and its forests and lakes higher up the valley.",
      places=["Mingora", "Malam Jabba", "Kalam", "Mahodand Lake", "Ushu Forest"],
      note="Higher areas can be closed by snow or rain. We confirm road conditions before you travel."),
 dict(slug="naran-kaghan", img="pk-naran", name="Naran & Kaghan", region="Khyber Pakhtunkhwa",
      intro="The Kaghan Valley runs from Balakot to Naran and beyond, with lakes and high passes that open in the summer season.",
      places=["Saif-ul-Malook Lake", "Lalazar", "Lulusar Lake", "Babusar Top (seasonal)", "Shogran & Siri Paye"],
      note="Upper Kaghan and Babusar Top are seasonal and open only when the road is cleared."),
]

def build_pakistan_tours():
    ARR = ["Transport from Islamabad or your city, planned around your group size", "Hotels or guest houses to the category you choose", "A day-by-day plan with the places above and the timing that suits the season",
           "Help with road, weather and permit questions before you leave"]
    cards = ""
    for t in PK_TOURS:
        url = "/pakistan-tours/" + t["slug"]
        pl = "".join(f"<li>{e(p)}</li>" for p in t["places"])
        faqs = [(f"When should I plan a trip to {t['name']}?", "Seasons differ by altitude: higher places open in summer and are closed by snow in winter. Tell us your dates and we confirm what is accessible."),
                (f"How much does a {t['name']} tour cost?", "It depends on your dates, group size and hotel category, so we quote on WhatsApp after you share your plan."),
                (f"Can you plan {t['name']} for a family or a group?", "Yes. Send the number of travellers and ages and we plan transport and stays around them.")]
        gal = ''
        if t['slug'] == 'hunza':
            gal = '<div class="block" id="gallery"><h2>Along the route</h2><div class="gallery">' + ''.join(f'<figure>{picture(PKPIC[k], a, 800, 600, "(max-width:600px) 100vw, 300px")}<figcaption class="pl">{a}</figcaption></figure>' for k, a in (('pk-khunjerab', 'Khunjerab Pass border gate'), ('pk-valley', 'River valley in Gilgit-Baltistan'))) + '</div></div>'
        main = f"""<div class="stack">
<div class="block answer" id="answer"><h2>{e(t['name'])} tour: quick answer</h2><p>{e(t['intro'])} {e(NAME)} plans trips to {e(t['name'])} from Islamabad around your dates and group. Message us on WhatsApp for a plan.</p></div>
<div class="block" id="places"><h2>Places you can include</h2><ul class="checks">{pl}</ul></div>
{gal}<div class="block" id="season"><h2>Season and road conditions</h2><p>{e(t['note'])}</p></div>
<div class="block" id="included"><h2>What we arrange</h2><ul class="checks">{"".join(f"<li>{e(x)}</li>" for x in ARR)}</ul></div>
<div class="block" id="faqs"><h2>FAQs</h2>{faq_html(faqs)}</div></div>"""
        others = "".join(f'<a href="/pakistan-tours/{o["slug"]}">{e(o["name"])} <span>→</span></a>' for o in PK_TOURS if o is not t)
        aside = f'<aside class="aside">{ctacard(t["name"] + " tour")}<nav class="mini"><h3>More Pakistan tours</h3><a href="/pakistan-tours">All Pakistan tours <span>→</span></a>{others}</nav></aside>'
        ph = pagehead(f"Pakistan tour · {UPDATED}", f"{e(t['name'])} tour<br>from Islamabad", e(t["intro"]), PKPIC[t["img"]], alt=t["name"],
                      actions=f'<a class="btn wa" href="{wa("Hi, I want to plan a " + t["name"] + " tour.")}" target="_blank" rel="noopener">💬 Plan this trip</a>')
        body = shell("/pakistan-tours", [("Home", "/"), ("Pakistan tours", "/pakistan-tours"), (t["name"], None)], ph, f'<div class="layout">{main}{aside}</div>{cta_band()}')
        page(url, f"{t['name']} Tour from Islamabad | AL ARBAB", f"{t['name']} tour from Islamabad: places to include, season and road notes, and what we arrange. Plan on WhatsApp with AL ARBAB, Blue Area.",
             body, [crumbs_ld([("Home", "/"), ("Pakistan tours", "/pakistan-tours"), (t["name"], url)]), faq_ld(faqs)], f"{t['name'].lower()} tour from islamabad, {t['name'].lower()} tour package", image=None, priority="0.6")
        cards += ncard(url, PKPIC[t["img"]], t["name"], "Pakistan tour", "See the tour →", f'<b style="font:900 20px/1 Archivo,sans-serif;color:#073b40">{e(t["name"][0])}</b>', t["name"], t["region"], "From", "Islamabad", "Quote", "On WhatsApp")
    ph = pagehead("Pakistan tours", "Pakistan tours<br>from Islamabad", "Northern Pakistan trips planned around your dates, from our Blue Area office.", PKPIC["pk-valley"], alt="Pakistan tours")
    body = shell("/pakistan-tours", [("Home", "/"), ("Pakistan tours", None)], ph, sec("Choose a destination", "Prices depend on dates, group size and hotels, so we quote on WhatsApp.", f'<div class="rgrid">{cards}</div>') + cta_band())
    page("/pakistan-tours", "Pakistan Tours from Islamabad: Hunza, Skardu, Swat | AL ARBAB",
         "Pakistan tours from Islamabad: Hunza, Skardu, Swat and Naran Kaghan planned around your dates and group by AL ARBAB, Blue Area. Plan on WhatsApp.",
         body, [crumbs_ld([("Home", "/"), ("Pakistan tours", "/pakistan-tours")])], "pakistan tour packages from islamabad, hunza tour, skardu tour, swat tour, naran kaghan tour", priority="0.7")

REVIEWED = f"Updated {UPDATED}. Rules change; we confirm the latest requirements for your case."

# footer "Popular visas & trips": Asian priority countries first (owner's order), then the guidance destinations
POPULAR = [(c["url"], f'{c["name"]} visa') for c in asian_priority()[:7]] + \
          [("/countries/schengen", "Schengen visa from Pakistan"), ("/countries/united-kingdom", "UK visit visa"), ("/countries/united-states", "USA B1/B2 visa"),
           ("/countries/canada", "Canada visit visa"), ("/umrah", "Umrah packages 2026"), ("/pakistan-tours", "Pakistan tours")]

# ================================================================== write
def write_all():
    bad = [u for u, (h, _, _) in PAGES.items() if re.search(r"\bIATA\b", re.sub(r"<script[^>]*>.*?</script>", "", h, flags=re.S))]
    assert not bad, f"IATA still mentioned on: {bad[:10]}"
    # The success-rate claim may appear only on Asian visit visa pages, worded exactly as SUCCESS_CLAIM + SUCCESS_NOTE.
    asian_pages = {c["url"] for c in COUNTRIES.values() if asian_claim(c)} | {f"/countries/{r['slug']}/visa/visit-visa" for r in DATA["regions"] if r["slug"] in ASIAN_REGIONS}
    over = [u for u, (h, _, _) in PAGES.items() if re.search(r"\b98\s?%", h) and u not in asian_pages]
    assert not over, f"'98%' appears outside Asian visit visa pages: {over[:10]}"
    unscoped = [u for u in asian_pages if u in PAGES and not (e(SUCCESS_CLAIM) in PAGES[u][0] and e(SUCCESS_NOTE) in PAGES[u][0])]
    assert not unscoped, f"Asian visit visa page without the claim and its note: {unscoped[:10]}"
    # Removed because they were not true / not verifiable: the "20,000+ travelers" figure and per-package star ratings.
    banned = [u for u, (h, _, _) in PAGES.items() if re.search(r"20,000\+?\s*(?:happy\s+)?(?:travell?ers|clients|customers)|over 20,000|\b20K\b|class=\"rate\"|\d\.\d\s*\(\d[\d\.,k]*\s*(?:reviews)?\)", h)]
    assert not banned, f"removed claim is back on: {banned[:10]}"
    # The real Google rating may be shown only in the footer (every page) and the hero badge (home page).
    _g = f"{G_RATING} on Google" if (G_RATING and G_COUNT) else None
    stray = [u for u, (h, _, _) in PAGES.items() if _g and u not in ("/", "/preview-glass", "/preview-colors", "/preview-plane-a", "/preview-plane-b", "/preview-hero-orange", "/preview-hero-green", "/preview-hero-sunny", "/preview-hero-frost", "/preview-hero-road") and h.count(_g) > 1]   # the preview is a copy of the home page
    assert not stray, f"Google rating shown more than once (outside footer + home hero) on: {stray[:10]}"
    # Claims removed in the Oct 2026 clean-up (owner's rules). Any of these coming back fails the build.
    gone = re.compile(r"24/7|around the clock|since 2009|Established 2009|foundingDate|15\+\s*Years|\b50\+|\b80\+|\b140\+|\b200\+|300\+ airlines|over 300 airlines|\b22\+|\b290\+|"
                      r"15\s*MINS|15 minutes|within minutes|(?:one|1) business hour|\b86 (?:countries|destinations)|Reviewed by the|senior consultant reviews|top visa consultan|best visa consultant|"
                      r"\bpremier\b|most trusted|most universally trusted|[Cc]heap flights|cheapest|Top rated|Top Rated|Best Seller|Fast Approval|Instant Visa|"
                      r"Ministry of Hajj|Ministry-authori[sz]ed|Authori[sz]ed Umrah|authorized Umrah|Direct Ministry|Maqam|aggregateRating|ratingValue|reviewCount|\"@type\":\"Review\"")
    back = [(u, gone.search(h).group(0)) for u, (h, _, _) in PAGES.items() if gone.search(h)]
    assert not back, f"removed claim is back: {back[:10]}"
    left = [u for u, (h, _, _) in PAGES.items() if "@N@" in h]
    assert not left, f"country-count placeholder not replaced on: {left[:5]}"
    # "guarantee" is allowed only when it denies a promise ("no agency can guarantee a visa").
    _ok = re.compile(r"can guarantee a (?:visa|specific date)|Can a visa consultant guarantee my visa\?|<b>Guarantee a visa</b>|(?:do|does|will) not guarantee|no guarantee|No guarantee|letters? of guarantee|guarantee(?:d)? (?:letter|document)", re.I)
    promise = [u for u, (h, _, _) in PAGES.items() if re.search(r"guarant", _ok.sub("", h), re.I)]
    assert not promise, f"'guarantee' used as a promise on: {promise[:10]}"
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):                      # empty dist/ but keep the folder (a dev server may be serving it)
        p = os.path.join(OUT, f)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(os.path.join(OUT, "assets"))
    for _f in ("logo.png", "logo-80.png", "icon-32.png", "icon-192.png", "og-default.jpg"):
        shutil.copy(os.path.join(ROOT, "assets", _f), os.path.join(OUT, "assets", _f))
    shutil.copytree(os.path.join(ROOT, "assets", "hero"), os.path.join(OUT, "assets", "hero"))   # owner's hero photos
    shutil.copytree(os.path.join(ROOT, "assets", "regions"), os.path.join(OUT, "assets", "regions"))   # owner's region photos
    shutil.copytree(os.path.join(ROOT, "assets", "fonts"), os.path.join(OUT, "assets", "fonts"))   # self-hosted fonts
    shutil.copytree(os.path.join(ROOT, "assets", "flags"), os.path.join(OUT, "assets", "flags"))   # self-hosted flags
    shutil.copytree(os.path.join(ROOT, "assets", "cards"), os.path.join(OUT, "assets", "cards"))   # feature card pictures
    shutil.copytree(os.path.join(ROOT, "assets", "steps"), os.path.join(OUT, "assets", "steps"))   # how-we-work pictures
    shutil.copytree(os.path.join(ROOT, "assets", "countries"), os.path.join(OUT, "assets", "countries"))   # owner's country photos
    shutil.copytree(os.path.join(ROOT, "assets", "umrah"), os.path.join(OUT, "assets", "umrah"))   # owner's Umrah photo
    shutil.copytree(os.path.join(ROOT, "assets", "packages"), os.path.join(OUT, "assets", "packages"))   # owner's package photos
    if os.path.isdir(os.path.join(ROOT, "assets", "brand")):
        shutil.copytree(os.path.join(ROOT, "assets", "brand"), os.path.join(OUT, "assets", "brand"))   # the licensed logo mark
    js = open(os.path.join(ROOT, "assets", "app.js"), encoding="utf-8").read()
    open(os.path.join(OUT, "assets", "app.js"), "w", encoding="utf-8").write(re.sub(r"\n\s*", "\n", js))
    for url, (html, _, _) in PAGES.items():
        if _ and GA_TAG:   # noindex pages (previews, copies of the home page) must not send analytics
            html = html.replace(GA_TAG, "")
        if url == "/404":
            path = os.path.join(OUT, "404.html")
        elif url == "/":
            path = os.path.join(OUT, "index.html")
        else:
            path = os.path.join(OUT, url.strip("/"), "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(re.sub(r">\s*\n\s*<", ">\n<", html))
    def imgs(html):
        out = []
        for m in re.finditer(r'<img[^>]+src="(/assets/(?:hero|countries|regions|packages|umrah)/[^"?]+)[^"]*"[^>]*alt="([^"]+)"', html):
            if BASE + m.group(1) not in [o[0] for o in out]:
                out.append((BASE + m.group(1), m.group(2)))
        return out[:8]
    urls = ""
    _rk = country_rank(); _crank = {c["url"]: _rk[c["url"]] for c in COUNTRIES.values()}
    for u, (h, p, noi) in sorted(PAGES.items(), key=lambda x: (-float(x[1][0:][1]), _crank.get(x[0], -1), x[0])):
        if noi:
            continue
        im = "".join(f"<image:image><image:loc>{src}</image:loc></image:image>" for src, _ in imgs(h))
        urls += f"<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority>{im}</url>\n"
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + urls + "</urlset>\n")
    llms = [f"# {NAME}", "", f"> DTS-licensed travel agency and visa consultancy in Blue Area, Islamabad, Pakistan. Visa help with {len(COUNTRIES)} country guides, air tickets, Umrah packages, hotels and travel insurance.", "",
            f"- Address: {ADDR}", f"- Phone / WhatsApp: {PHONE}, landline {LAND}", f"- Email: {EMAIL}", f"- Hours: {HOURS}", "", "## Key pages"]
    for u in ["/visa-services", "/countries", "/guides/visa-requirements-for-pakistani-passport", "/guides/schengen-visa-requirements-from-pakistan", "/guides/visa-documents-explained",
              "/umrah", "/air-ticketing", "/eligibility-check", "/contact"] + [g["url"] for g in GUIDES2]:
        if u in PAGES:
            llms.append(f"- [{page_title(PAGES[u][0])}]({BASE}{u})")
    llms += ["", "## Countries"] + [f"- [{c['name']} visa]({BASE}{c['url']}): {len(c['docs_clean'])} documents on the checklist" for c in COUNTRIES.values()]
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write("\n".join(llms) + "\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    # hosting helpers: Netlify / Cloudflare Pages, Vercel, Apache (cPanel)
    open(os.path.join(OUT, "_redirects"), "w").write("/pakistan-visa  /countries/south-asia/pakistan  301\n")
    open(os.path.join(OUT, "_headers"), "w").write("/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: SAMEORIGIN\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()\n")
    json.dump({"cleanUrls": True, "trailingSlash": False, "redirects": [{"source": "/pakistan-visa", "destination": "/countries/south-asia/pakistan", "permanent": True}],
               "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                           {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
                                                          {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                                                          {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=()"}]}]},
              open(os.path.join(OUT, "vercel.json"), "w"), indent=1)
    open(os.path.join(OUT, ".htaccess"), "w").write("""Options -MultiViews -Indexes
DirectorySlash Off
ErrorDocument 404 /404.html
RewriteEngine On
RewriteRule ^pakistan-visa/?$ /countries/south-asia/pakistan [R=301,L]
# force https + www
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} !^www\\. [NC]
RewriteRule ^ https://www.alarbabtravel.com%{REQUEST_URI} [R=301,L]
# /page/ -> /page
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.+)/$ /$1 [R=301,L]
# serve /page from /page/index.html
RewriteCond %{REQUEST_FILENAME} -d
RewriteCond %{REQUEST_FILENAME}/index.html -f
RewriteRule ^(.+)$ /$1/index.html [L]
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml application/xml text/plain
</IfModule>
<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 1 hour"
ExpiresByType application/javascript "access plus 1 year"
ExpiresByType image/png "access plus 1 year"
ExpiresByType image/webp "access plus 1 year"
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType font/woff2 "access plus 1 year"
</IfModule>
""")

if __name__ == "__main__":
    build_home(); build_countries_hub(); build_packages(); build_visa_services(); build_air(); build_umrah()
    build_hotel(); build_insurance(); build_airlines(); build_about(); build_contact(); build_policies(); build_misc()
    build_eligibility(); build_cities(); build_appointments(); build_reservation(); build_routes(); build_umrah_packages(); build_guides()
    for r in DATA["regions"]:
        build_region(r)
    for c in COUNTRIES.values():
        build_country(c)
    build_editorial()
    build_sources()
    build_pakistan_tours()
    build_html_sitemap()
    glass_home()
    hero_color_previews()
    hero_road_preview()
    planes_preview()
    colors_preview()
    splash_previews()
    logo_previews()
    logo2_previews()
    logosign_previews()
    logoal_previews()
    logopk_previews()
    logocr_previews()
    logofinal_previews()
    logosticker_previews()
    logotext_previews()
    headerlogo_previews()
    alsymbol_previews()
    alshape_previews()
    mine_previews()
    minetext_previews()
    navbar_previews()
    navd_previews()
    navpro_previews()
    navx_previews()
    flight_previews()
    glasslogo_previews()
    glasslogoblue_previews()
    navsoft_previews()
    brandpill_previews()
    flight2_previews()
    heroideas_previews()
    contrail_previews()
    widgets_previews()
    widgetslime_previews()
    herotitle_previews()
    galaxy_previews()
    splash_home()
    write_all()
    total = sum(len(h) for h, _, _ in PAGES.values())
    print(f"built {len(PAGES)} pages ({len(COUNTRIES)} countries, {len(DATA['regions'])} regions) - {total/1024:.0f} KB HTML")
