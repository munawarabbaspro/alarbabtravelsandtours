# one-off patch: 3D rotating landmark ring on the home page (style from the client's Uiverse reference)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new):
    global s
    assert old in s, "missing: " + old[:80]
    s = s.replace(old, new, 1)

rep('''def build_home():''', '''RING = [("Eiffel Tower", "France", "1502602898657-3e91760cbb34", "/countries/schengen/france"),
        ("Petronas Towers", "Malaysia", "1576506730652-f0e4ad14828f", "/countries/south-asia/malaysia"),
        ("Burj Khalifa", "Dubai", "1512453979798-5ea266f8880c", "/countries/middle-east/united-arab-emirates"),
        ("Kaaba, Makkah", "Umrah", "1693590614566-1d3ea9ef32f7", "/umrah"),
        ("Big Ben", "United Kingdom", "1486299267070-83823f5448dd", "/countries/united-kingdom"),
        ("Mount Fuji", "Japan", "1526481280693-3bfa7568e0f3", "/countries/east-asia/japan"),
        ("Santorini", "Greece", "1570077188670-e3a8d69ac5ff", "/countries/schengen/greece"),
        ("Cappadocia", "Turkey", "1505783638529-f3fdc62e1bb1", "/countries/central-asia/turkey"),
        ("Marina Bay Sands", "Singapore", "1525625293386-3f8f99389edd", "/countries/south-asia/singapore"),
        ("Colosseum", "Italy", "1552832230-c0197dd311b5", "/countries/schengen/italy")]

def ring_html():
    cards = "".join(f\'\'\'<a class="r3" style="--index:{i}" href="{u}"><img src="{U(pid, 300)}" srcset="{U(pid, 600)} 2x" alt="{e(n)}, {e(c)}" width="150" height="220" loading="lazy" decoding="async"><span><b>{e(c)}</b>{e(n)}</span></a>\'\'\'
                    for i, (n, c, pid, u) in enumerate(RING))
    return f\'<div class="ring-wrap" aria-label="Popular destinations"><div class="ring" style="--quantity:{len(RING)}">{cards}</div><p class="ring-hint">Hover to pause · click a destination</p></div>\'

def build_home():''')

rep('''{sec("Visa support across every continent", "Choose a region to see country-by-country requirements, fees and documents.", f'<div class="rgrid">{regions}</div>''',
    '''{sec("Visa support across every continent", "Choose a region to see country-by-country requirements, fees and documents.", ring_html() + f'<div class="rgrid">{regions}</div>''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v7")
