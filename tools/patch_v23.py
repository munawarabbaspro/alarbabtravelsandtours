# one-off patch: real brand/UI icons (SVG) instead of emoji for contact, WhatsApp, call, location, Gmail, Facebook, social links
import io, re
P = "build.py"; s = io.open(P, encoding="utf-8").read()
def rep(a, b, n=1):
    global s
    assert a in s, a[:80]; s = s.replace(a, b, n)

ICONS = r'''
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

def ico(name, size=22, color="currentColor", cls="i"):
    return f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" aria-hidden="true" focusable="false">{_P[name]}</svg>'

# tile colours for the contact lists (brand colours)
IC_TILE = {"📍": ("ic-map", "pin", "#EA4335"), "📞": ("ic-call", "phone", "#ffffff"), "✉": ("ic-mail", "gmail", None), "🕑": ("ic-time", "clock", "#5f6368"),
           "💬": ("ic-wa", "wa", "#ffffff"), "👍": ("ic-fb", "fb", "#1877F2")}

def _tile(m):
    cls, name, col = IC_TILE[m.group(1)]
    return f'<span class="ic {cls}">{ico(name, 24, col) if col else ico(name, 24, None)}</span>'

def finish_icons(html):
    """Swap emoji for SVG icons in the final page HTML (buttons, contact lists)."""
    html = re.sub(r'<span class="ic">(📍|📞|✉|🕑|💬|👍)</span>', _tile, html)
    html = html.replace("💬 ", ico(("wa"), 18) + " ").replace("💬", ico("wa", 20))
    html = html.replace("📞 ", ico("phone", 17) + " ").replace("📞", ico("phone", 18))
    html = html.replace("📍 Get directions", ico("pin", 17) + " Get directions")
    return html
'''
rep('''e = H.escape\n''', 'e = H.escape\n' + ICONS, 1)

# social links in footer: real glyphs
rep('''SOCIAL = [("FB", B["socials"]["facebook"], "Facebook"), ("IG", B["socials"]["instagram"], "Instagram"),
          ("X", B["socials"]["twitter"], "X (Twitter)"), ("in", B["socials"]["linkedin"], "LinkedIn")]''',
    '''SOCIAL = [("fb", B["socials"]["facebook"], "Facebook"), ("ig", B["socials"]["instagram"], "Instagram"),
          ("x", B["socials"]["twitter"], "X (Twitter)"), ("in", B["socials"]["linkedin"], "LinkedIn")]''')
rep('''aria-label="{n}">{s}</a>' for s, u, n in SOCIAL)''', '''aria-label="{n}">{ico(s, 18)}</a>' for s, u, n in SOCIAL)''')

# contact page list
rep('''ih = "".join(f'<div><span class="ic">{a}</span><span><small>{b.upper()}</small>{c}</span></div>' for a, b, c in info)''',
    '''ih = "".join(f'<div><span class="ic">{a}</span><span><small>{b.upper()}</small>{c}</span></div>' for a, b, c in info)  # emoji keys become brand icons in finish_icons()''')

# apply in page()
rep('''    PAGES[url] = (html, priority, noindex)''', '''    html = finish_icons(html)
    PAGES[url] = (html, priority, noindex)''')
io.open(P, "w", encoding="utf-8").write(s); print("ok")
