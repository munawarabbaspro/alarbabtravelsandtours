# one-off patch: glass "gcard" image cards (style from the Uiverse card the client shared)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new):
    global s
    assert old in s, "missing: " + old[:80]
    s = s.replace(old, new, 1)

ARROW = '<svg viewBox="0 0 12 12" width="16" height="16" aria-hidden="true"><path d="M4.646 2.146a.5.5 0 0 0 0 .708L7.793 6L4.646 9.146a.5.5 0 1 0 .708.708l3.5-3.5a.5.5 0 0 0 0-.708l-3.5-3.5a.5.5 0 0 0-.708 0z" fill="currentColor"/></svg>'

rep('''def region_card(r):''', f'''GC_ARROW = '{ARROW}'

def gcard(href, pid, alt, title, sub, tag, side1, side2, flagcode=None):
    """Glass image card: photo in a notched frame, frosted text panel, round arrow button."""
    if pid:
        media = picture(pid, alt, 600, 900, "(max-width:600px) 50vw, 260px", widths=(400, 600, 900))
    elif flagcode:
        media = f'<span class="g-orb"></span><span class="g-flag">{{flag(flagcode, alt, 88)}}</span>'
    else:
        media = '<span class="g-orb"></span>'
    return (f'<a class="gcard" href="{{href}}"><span class="g-frame"><span class="g-photo">{{media}}</span></span>'
            f'<span class="g-body"><span class="g-panel"><b>{{e(title)}}</b><small>{{e(sub)}}</small><span class="g-tag">{{e(tag)}}</span></span>'
            f'<span class="g-side"><small>{{e(side1)}}</small><small>{{e(side2)}}</small><span class="g-btn">{{GC_ARROW}}</span></span></span></a>')

def region_card(r):''')

rep('''    cnt = f"{n} countries" if n else f'{len(r["visas"])} visa types'
    return f'<a class="rcard" href="/countries/{r["slug"]}"><div class="im">{im}</div><div class="bd"><span class="n">{cnt}</span><h3>{e(r["name"])}</h3><p>{e(r["shortDesc"])}</p></div></a>\'''',
    '''    cnt = f"{n} countries" if n else f'{len(r["visas"])} visa types'
    return gcard(f"/countries/{r['slug']}", r["img"], r["name"] + " visa from Pakistan", r["name"], r["shortDesc"], cnt, "AL ARBAB", "visa", r["flag"])''')

rep('''        vd_cards += f'<a class="dest" href="{link}">{im}<div><small>{v["flag"]} {e(v["tag"])}</small><h3>{e(v["country"])}</h3><p>{e(v["landmark"])}</p></div></a>\'''',
    '''        vd_cards += gcard(link, pid, v["country"].title() + " – " + v["landmark"], v["country"].title(), v["landmark"], v["tag"], v["flag"], "visa")''')
rep('''  <div class="grid g4">{vd_cards}</div>''', '''  <div class="rgrid">{vd_cards}</div>''')

io.open(P, "w", encoding="utf-8").write(s)
print("patched v5")
