"""v25 – UI/UX audit fixes (CSS side): contrast, focus ring, mobile contact dock, touch targets, text size, SVG icons.
Run once from the project folder:  py tools/patch_v25.py   (idempotent: it stops if the v11 marker is already there)."""
import re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "assets", "style.css")
s = open(P, encoding="utf-8").read()
if "/* v11: audit fixes" in s:
    sys.exit("already patched")

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old, s.count(old))
    s = s.replace(old, new)

# 1) text size: nothing below 12px, small text +1px (11->12, 12.5->13 ...). 15px and up is left alone.
STEP = {11: 12, 11.5: 12, 12: 13, 12.5: 13, 13: 14, 13.5: 14, 14: 15, 14.5: 15}
def bump(v):
    v = float(v)
    if v >= 15:
        return None
    return STEP.get(v, 12 if v < 11 else None)
def fix_fs(m):
    n = bump(m.group(2))
    return m.group(0) if n is None else f"{m.group(1)}{n:g}px"
s = re.sub(r"(font-size:\s*)(\d+(?:\.\d+)?)px", fix_fs, s)
s = re.sub(r"(font:[^;}]*?\s)(\d+(?:\.\d+)?)px", fix_fs, s)

# 2) contrast: WhatsApp green that passes 4.5:1 with white text (#17803f = 5.0:1)
rep(".btn.wa:hover{background:#17803f}", ".btn.wa:hover{background:#0f6330}")
rep(".fab:hover{transform:translateY(-3px);background:#17803f}", ".fab:hover{transform:translateY(-3px);background:#0f6330}")
s = s.replace("#1fa855", "#17803f")
rep(".fab{background:#25D366}.fab:hover{background:#1ebe5a}", ".fab{background:#17803f}.fab:hover{background:#0f6330}")

# 3) focus ring: two-tone (dark ring + white halo) so it shows on light and dark surfaces
rep(":focus-visible{outline:3px solid var(--teal);outline-offset:3px;border-radius:8px}",
    ":focus-visible{outline:3px solid #091413;outline-offset:2px;border-radius:8px;box-shadow:0 0 0 2px #fff}")
rep(".book:focus-visible{box-shadow:0 0 0 3px var(--teal),1px 1px 12px rgba(9,20,19,.45)}",
    ".book:focus-visible{box-shadow:0 0 0 3px #fff,0 0 0 6px #091413,1px 1px 12px rgba(9,20,19,.45)}")
rep('.dests button[aria-selected="true"]', '.dests button[aria-pressed="true"]')

# 4) header: on tablets show a compact WhatsApp button next to the burger; phones use the bottom dock
rep(".burger{display:block}.cta-dark{display:none}", ".burger{display:grid;place-items:center;margin-left:0;order:3}.cta-dark{order:2}")

# 5) emoji in CSS content -> SVG masks
rep('.tips li::before{content:"💡";position:absolute;left:13px;top:11px}',
    '.tips li::before{content:"";position:absolute;left:13px;top:12px;width:18px;height:18px;background:#9a5b00;'
    '-webkit-mask:var(--m-bulb) center/contain no-repeat;mask:var(--m-bulb) center/contain no-repeat}')

s = s.rstrip() + r'''

/* v11: audit fixes (CTA dock, contrast, touch targets, text size, focus, icons) */
:root{
  --m-pin:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E");
  --m-bulb:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z'/%3E%3C/svg%3E")
}
.pl::before{content:"";display:inline-block;width:14px;height:14px;margin-right:6px;vertical-align:-2px;background:#d93a2b;-webkit-mask:var(--m-pin) center/contain no-repeat;mask:var(--m-pin) center/contain no-repeat}
svg.e{width:1.15em;height:1.15em;vertical-align:-.22em;margin-right:.35em}
.feat .ic svg.e{width:24px;height:24px;margin:0}
.chip svg.e,.start i svg.e,.faces span svg.e{margin:0}
.faces span svg.e{width:18px;height:18px}
img.fl{display:inline-block;width:20px;height:14px;border-radius:2px;vertical-align:-2px;margin-right:6px;box-shadow:0 0 0 1px rgba(0,0,0,.18)}
.feat .ic img.fl{width:28px;height:19px;margin:0}
.air .top img.fl{width:32px;height:22px;margin:0}

/* readable body text: 16px for the main paragraphs */
.block p,.prose p,.prose ul,.legal ul,.pagehead p,.ph p.lead2,.hero p.sub,.sec .lead{font-size:16px}
.hero p.sub{max-width:380px}
input,select,textarea{font-size:16px}

/* WhatsApp CTA: dark ring colours, readable label */
.btn.wa,.fab,.dk-wa{color:#fff}
.fa-cta .btn.wa{background:var(--ink)}.fa-cta .btn.wa:hover{background:var(--green)}
.fab{font-size:15px;min-height:48px}

/* hero slideshow pause control (WCAG 2.2.2) */
.dpause{position:absolute;left:16px;bottom:16px;z-index:5;width:44px;height:44px;border-radius:50%;background:rgba(9,20,19,.84);color:#fff;display:grid;place-items:center;box-shadow:0 6px 16px -6px rgba(0,0,0,.6);transition:background .2s}
.dpause:hover{background:var(--green)}

/* trust line under the contact banners + Google reviews link */
.band .tl{grid-column:1/-1;display:flex;gap:8px 20px;flex-wrap:wrap;font-size:14px;color:#cfe0db;border-top:1px solid rgba(255,255,255,.16);padding-top:14px;margin:0}
.tl span{display:inline-flex;align-items:center;gap:7px}
.band .glink{grid-column:1/-1;margin:0}
.band .glink a,.fA .glink a{color:#7ff0d6;font-weight:700;text-decoration:underline;text-underline-offset:3px;display:inline-flex;align-items:center;min-height:44px}
.fA .glink{margin-top:10px;font-size:14px}

/* tap targets: 44px minimum on phones/tablets/touch screens, desktop mice keep the compact layout */
.burger{width:44px;height:44px}
.brand{min-height:44px}
a.sb{width:44px;height:44px}
.dock{display:none;transition:transform .2s}
.dock.off{transform:translateY(120%)}
@media(max-width:1000px),(pointer:coarse){
  .btn,.start,.chip,.cta-dark,.tabs button,.dests button,.filters button,.nl button,.pill{min-height:44px}
  .pill{display:flex;align-items:center}
  .book .page .more,.card .more,.vt .go,.air a,.route a{display:flex;align-items:center;min-height:44px}
  .tbl a,.chipsrow a,.srcs a,.link,.fA ul a,.fa-contact a,.info span a,.prose h3 a,.crumbs a{display:inline-flex;align-items:center;min-height:44px;padding-block:0}
  .smap a{display:flex;align-items:center;min-height:44px}
  .mini a{min-height:44px;align-items:center;padding-block:0}
  .fA .fl a{display:inline-flex;align-items:center;min-height:44px;padding-block:0}
  .fA ul{gap:0}
  .fa-more .fl{gap:0 18px}
  details.faq summary{min-height:44px;align-items:center}
  input,select,textarea{min-height:44px}
}
@media(max-width:1000px){
  .fab{display:none}
  .dock{display:flex;gap:10px;position:fixed;left:0;right:0;bottom:0;z-index:70;padding:10px 12px calc(10px + env(safe-area-inset-bottom,0px));background:var(--shell);box-shadow:0 -10px 28px -12px rgba(9,20,19,.5)}
  .dk{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;min-height:48px;border-radius:999px;font:800 16px/1 Inter,sans-serif;color:#fff;transition:background .2s}
  .dk-wa{background:#17803f}.dk-wa:hover{background:#0f6330}
  .dk-call{background:var(--ink)}.dk-call:hover{background:var(--green)}
  footer.fA{padding-bottom:calc(76px + env(safe-area-inset-bottom,0px))}
  #toast{bottom:92px}
}
@media(max-width:600px){
  .cta-dark{display:none}.burger{margin-left:auto}
  .card p,.vt p,.rcard p,.feat p,.docs li,.checks li,.checks2 li,.refuse li,.tips li,.out-docs li,.steps span,.note,.ctacard p,.timeline p,.umrah p,.band p,details.faq p,.air ul,.route small,.srcs a{font-size:15px}
  .block p,.prose p,.pagehead p,.ph p.lead2,.hero p.sub,.sec .lead{font-size:16px;line-height:1.65}
  details.faq summary{font-size:16px}
  .fA p,.fA ul,.fa-more .fl,.fa-bottom{font-size:14px}
}
@media(prefers-reduced-motion:reduce){.dock{transition:none}}
'''
open(P, "w", encoding="utf-8").write(s)
print("style.css patched:", len(s), "bytes")
