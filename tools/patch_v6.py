# one-off patch: package cards as "book" cards (cover swings open on hover/tap; style from the client's Uiverse reference)
import io
P = "build.py"
s = io.open(P, encoding="utf-8").read()
old = s[s.index("def pkg_card(p):"):s.index("def feat(ic, h, p, link=None):")]
new = '''def pkg_card(p):
    """Book card: the inside page holds the package details; the photo cover swings open on hover, focus or tap."""
    li = "".join(f"<li>{e(x)}</li>" for x in p["highlights"])
    return f\'\'\'<article class="book" tabindex="0">
<div class="page"><span class="tag">{e(p["tag"])} · {e(p["country"])}</span><h3>{e(p["title"])}</h3><p><b>{e(p["duration"])}</b><br>{e(p["amenities"])}</p><ul>{li}</ul>
<a class="more" href="{p["url"]}">View package details <span>→</span></a></div>
<div class="cover" aria-hidden="true">{picture(p["img"], "", 600, 800, "(max-width:600px) 100vw, 300px", widths=(400, 600, 900))}<span class="badge">{e(p["discountBadge"])}</span><span class="rate">★ {p["rating"]} ({e(p["reviews"])})</span>
<span class="cv"><small>{p["flag"]} {e(p["duration"])}</small><b>{e(p["title"])}</b><i>Open ›</i></span></div>
</article>\'\'\'

'''
s = s.replace(old, new)
io.open(P, "w", encoding="utf-8").write(s)
print("patched v6")
