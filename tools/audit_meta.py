"""Sitemap + meta tag audit of dist/ (read-only)."""
import os, re, json, html, collections
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
BASE = "https://www.alarbabtravel.com"
def rd(p): return open(p, encoding="utf-8", errors="replace").read()
P = collections.defaultdict(list)

# ---- pages (excluding previews) ----
pages = {}
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if f.endswith(".html"):
            full = os.path.join(dp, f); rel = os.path.relpath(full, ROOT).replace("\\", "/")
            if rel.startswith("assets/") or rel.startswith("preview-") or "/preview-" in rel: continue
            url = "/" + rel[:-len("index.html")] if rel.endswith("index.html") else "/" + rel
            if url != "/" and url.endswith("/"): url = url[:-1]
            pages[url] = rd(full)
print("real pages:", len(pages))

# ---- sitemap ----
sm = rd(os.path.join(ROOT, "sitemap.xml"))
try:
    tree = ET.fromstring(sm)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "i": "http://www.google.com/schemas/sitemap-image/1.1"}
    urls = tree.findall("s:url", ns)
    print("sitemap urls:", len(urls), "| size KB:", len(sm) // 1024)
    locs = []
    for u in urls:
        loc = u.find("s:loc", ns).text.strip(); locs.append(loc)
        lm = u.find("s:lastmod", ns); pr = u.find("s:priority", ns)
        if not loc.startswith(BASE): P["sitemap: loc not on the canonical host"].append(loc)
        if loc.endswith("/") and loc != BASE + "/": P["sitemap: trailing slash"].append(loc)
        if "/preview-" in loc: P["sitemap: preview url"].append(loc)
        if lm is None: P["sitemap: no lastmod"].append(loc)
        elif not re.match(r"^\d{4}-\d{2}-\d{2}", lm.text): P["sitemap: bad lastmod"].append((loc, lm.text))
        if pr is not None and not (0 <= float(pr.text) <= 1): P["sitemap: bad priority"].append(loc)
        path = loc[len(BASE):] or "/"
        if path != "/": path = path.rstrip("/")
        if path not in pages: P["sitemap: url has no page"].append(loc)
        else:
            h = pages[path]
            if "noindex" in h: P["sitemap: noindex page listed"].append(loc)
            c = re.search(r'<link rel="canonical" href="([^"]+)"', h)
            if not c or c.group(1).rstrip("/") != loc.rstrip("/"): P["sitemap: canonical differs"].append((loc, c.group(1) if c else None))
        for im in u.findall("i:image", ns):
            il = im.find("i:loc", ns).text
            if not il.startswith("http"): P["sitemap image: not absolute"].append(il)
    dup = [k for k, v in collections.Counter(locs).items() if v > 1]
    if dup: P["sitemap: duplicate loc"] = dup
    ext = sum(1 for u in urls for im in u.findall("i:image", ns) if "unsplash" in im.find("i:loc", ns).text)
    print("images in sitemap:", sum(len(u.findall("i:image", ns)) for u in urls), "| hosted on Unsplash:", ext)
except Exception as e:
    P["sitemap: XML does not parse"].append(str(e))

# every real indexable page in the sitemap?
inmap = {l[len(BASE):].rstrip("/") or "/" for l in locs}
for u, h in pages.items():
    if "noindex" not in h and u not in inmap and u != "/404.html": P["indexable page missing from sitemap"].append(u)

# ---- robots + llms ----
rb = rd(os.path.join(ROOT, "robots.txt"))
print("robots.txt:", rb.replace("\n", " | ")[:200])
if "Sitemap:" not in rb: P["robots: no Sitemap line"].append(1)
if re.search(r"Disallow:\s*/\s*$", rb, re.M): P["robots: blocks everything"].append(1)
print("llms.txt:", "yes" if os.path.exists(os.path.join(ROOT, "llms.txt")) else "no")

# ---- meta tags per page ----
def meta(h, name, attr="name"):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(name)), h)
    return html.unescape(m.group(1)) if m else None
need_og = ("og:title", "og:description", "og:image", "og:url", "og:type", "og:site_name", "og:locale")
cnt = collections.Counter()
for u, h in sorted(pages.items()):
    if u == "/404.html": continue
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    t = html.unescape(t.group(1).strip()) if t else ""
    d = meta(h, "description") or ""
    if not t: P["no <title>"].append(u)
    elif len(t) > 62: P["title > 62 chars"].append((u, len(t)))
    if not d: P["no meta description"].append(u)
    elif not 70 <= len(d) <= 160: P["meta description length outside 70-160"].append((u, len(d)))
    if not re.search(r"<meta charset", h, re.I): P["no charset"].append(u)
    if not meta(h, "viewport"): P["no viewport"].append(u)
    if not re.search(r'<html[^>]*\blang="', h): P["no lang"].append(u)
    if not meta(h, "robots"): P["no robots meta"].append(u)
    if not meta(h, "theme-color"): cnt["no theme-color"] += 1
    c = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    exp = BASE + ("" if u == "/" else u) + ("/" if u == "/" else "")
    if not c: P["no canonical"].append(u)
    elif c.group(1).rstrip("/") != exp.rstrip("/"): P["canonical differs from URL"].append((u, c.group(1)))
    for k in need_og:
        if not meta(h, k, "property"): P[f"missing {k}"].append(u)
    if (meta(h, "og:url", "property") or "").rstrip("/") != (c.group(1).rstrip("/") if c else None): P["og:url != canonical"].append(u)
    if not meta(h, "twitter:card"): P["no twitter:card"].append(u)
    oi = meta(h, "og:image", "property") or ""
    if oi and not oi.startswith("https://"): P["og:image not https"].append((u, oi[:60]))
    if oi and "unsplash" in oi: cnt["og:image hosted on Unsplash"] += 1
    if not re.search(r'rel="icon"', h): P["no favicon"].append(u)
    if not re.search(r'rel="apple-touch-icon"', h): P["no apple-touch-icon"].append(u)
    if len(re.findall(r"<h1[\s>]", h)) != 1: P["h1 count != 1"].append(u)
    for sm_ in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try: json.loads(sm_.group(1))
        except Exception as e: P["invalid JSON-LD"].append((u, str(e)[:50]))
    if "98%" in h and "/countries/" not in u: P["'98%' outside country pages"].append(u)
    if re.search(r"\bIATA\b", h, re.I): P["IATA mentioned"].append(u)
for k, v in cnt.items(): print(f"[{k}] {v} pages")

print()
if not P: print("NO ISSUES")
for k, v in P.items():
    uniq = list(dict.fromkeys(v if not isinstance(v[0], list) else map(tuple, v)))
    print(f"[{k}] {len(uniq)}")
    for x in uniq[:6]: print("    ", x)
