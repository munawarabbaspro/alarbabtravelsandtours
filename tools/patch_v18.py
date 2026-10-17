# one-off patch: fix heading order on 7 pages (no h1 -> h3 jumps)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    assert old in s, "missing: " + old[:90]
    s = s.replace(old, new, count)

# home: weather widget title is a label, not a heading
rep('''<div class="weather rise" style="animation-delay:1s" aria-live="polite"><h6><span>LIVE WEATHER</span><span id="wplace">{d0["city"]}</span></h6>''',
    '''<div class="weather rise" style="animation-delay:1s" aria-live="polite"><p class="wtitle"><span>LIVE WEATHER</span><span id="wplace">{d0["city"]}</span></p>''')
# feature grids that opened a page without a section heading
rep('''    content = f\'\'\'<section class="sec reveal"><div class="grid g4">{feats}</div></section>''',
    '''    content = f\'\'\'{sec("Why book flights with us", "", f'<div class="grid g4">{feats}</div>')}''')
rep('''    content = f\'\'\'<section class="sec reveal"><div class="grid g4">{t}</div><p style="margin-top:20px"><a class="btn wa" href="{wa("Hi, I need a hotel booking.")}" target="_blank" rel="noopener">Book a hotel</a></p></section>''',
    '''    content = f\'\'\'{sec("Hotels for every budget", "", f'<div class="grid g4">{t}</div><p style="margin-top:20px"><a class="btn wa" href="{wa("Hi, I need a hotel booking.")}" target="_blank" rel="noopener">Book a hotel</a></p>')}''')
rep('''    content = f\'\'\'<section class="sec reveal"><div class="grid">{cov}</div></section>''', '''    content = f\'\'\'{sec("What our travel insurance covers", "", f'<div class="grid">{cov}</div>')}''')
rep('''<div class="tabs" id="airTabs" role="group" aria-label="Filter airlines by region">{tabs}</div>''', '''<h2 class="sr">Partner airlines by region</h2><div class="tabs" id="airTabs" role="group" aria-label="Filter airlines by region">{tabs}</div>''')
rep('''    body = shell("/guides", [("Home", "/"), ("Guides", None)], ph, f'<section class="sec"><div class="grid">{cards}</div></section>{cta_band()}')''',
    '''    body = shell("/guides", [("Home", "/"), ("Guides", None)], ph, sec("All visa guides", "", f'<div class="grid">{cards}</div>') + cta_band())''')
# umrah: the hadith banner title is a quote -> h2
rep('''<div class="umrah"><div class="t"><span class="eyebrow">Spiritual journey</span><h3>"Perform Umrah and Hajj, as they remove poverty and sins…"</h3>''',
    '''<div class="umrah"><div class="t"><span class="eyebrow">Spiritual journey</span><h2 class="qh">"Perform Umrah and Hajj, as they remove poverty and sins…"</h2>''')
io.open(P, "w", encoding="utf-8").write(s)
print("patched v18")
