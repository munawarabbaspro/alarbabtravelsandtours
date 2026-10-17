"""Static audit of dist/: SEO, links, images, schema, duplicates, weight. Read-only."""
import os, re, json, sys, collections, html
from urllib.parse import urlparse, urljoin

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
BASE = "https://www.alarbabtravel.com"
pages = {}
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        if f.endswith(".html"):
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            if rel.startswith("assets/") or "/preview-" in "/" + rel or rel.startswith("preview-"):
                continue
            url = "/" + rel[:-len("index.html")] if rel.endswith("index.html") else "/" + rel
            if url != "/" and url.endswith("/"): url = url[:-1]
            pages[url] = full
print("pages (excluding previews):", len(pages))

def rd(p): return open(p, encoding="utf-8", errors="replace").read()
issues = collections.defaultdict(list)
titles, descs, h1s = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
inlinks = collections.Counter()
allpaths = set(pages)
def exists(path):
    path = path.split("#")[0].split("?")[0]
    if not path: return True
    if path in allpaths or path.rstrip("/") in allpaths: return True
    fp = os.path.join(ROOT, path.lstrip("/"))
    return os.path.isfile(fp) or os.path.isfile(os.path.join(fp, "index.html"))

for url, fp in sorted(pages.items()):
    h = rd(fp)
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    t = html.unescape(m.group(1).strip()) if m else ""
    d = re.search(r'<meta name="description" content="(.*?)"', h, re.S)
    d = html.unescape(d.group(1).strip()) if d else ""
    titles[t].append(url); descs[d].append(url)
    if not t: issues["no title"].append(url)
    elif len(t) > 62: issues["title >62 chars"].append((url, len(t)))
    elif len(t) < 20: issues["title <20 chars"].append((url, len(t)))
    if not d: issues["no meta description"].append(url)
    elif len(d) > 160: issues["meta desc >160"].append((url, len(d)))
    elif len(d) < 70: issues["meta desc <70"].append((url, len(d)))
    n1 = len(re.findall(r"<h1[\s>]", h))
    if n1 != 1: issues["h1 count != 1"].append((url, n1))
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    if h1: h1s[re.sub(r"<[^>]+>", "", h1.group(1)).strip()].append(url)
    can = re.search(r'<link rel="canonical" href="(.*?)"', h)
    exp = BASE + (url if url != "/" else "/")
    if not can: issues["no canonical"].append(url)
    elif can.group(1).rstrip("/") != exp.rstrip("/"): issues["canonical mismatch"].append((url, can.group(1)))
    if 'name="viewport"' not in h: issues["no viewport"].append(url)
    if "<html lang=" not in h: issues["no lang"].append(url)
    if 'property="og:title"' not in h: issues["no og:title"].append(url)
    if 'property="og:image"' not in h: issues["no og:image"].append(url)
    if "noindex" in h: issues["noindex on a real page"].append(url)
    # images
    for im in re.finditer(r"<img\b[^>]*>", h):
        tag = im.group(0)
        if not re.search(r"\balt=", tag): issues["img without alt attr"].append(url)
        if not re.search(r"\bwidth=", tag) or not re.search(r"\bheight=", tag): issues["img without width/height"].append(url)
    # schema
    for sm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try: json.loads(sm.group(1))
        except Exception as e: issues["invalid JSON-LD"].append((url, str(e)[:60]))
    # mixed content / http links
    for m2 in re.finditer(r'(?:src|href)="(http://[^"]+)"', h):
        if "w3.org" not in m2.group(1): issues["http:// reference"].append((url, m2.group(1)[:80]))
    # links
    for lm in re.finditer(r'<a\b[^>]*\bhref="([^"]+)"', h):
        href = html.unescape(lm.group(1))
        if href.startswith(("mailto:", "tel:", "javascript:", "#", "https://wa.me", "https://api.whatsapp")): continue
        if href.startswith("http"):
            u = urlparse(href)
            if u.netloc.endswith("alarbabtravel.com"): href = u.path or "/"
            else: continue
        if not href.startswith("/"):
            href = urljoin(url if url.endswith("/") else url + "/", href)
        tgt = href.split("#")[0].split("?")[0]
        if tgt.startswith("/assets/") or re.search(r"\.(png|jpe?g|webp|svg|pdf|xml|txt|ico)$", tgt):
            if not os.path.isfile(os.path.join(ROOT, tgt.lstrip("/"))): issues["broken asset link"].append((url, tgt))
            continue
        key = tgt.rstrip("/") or "/"
        inlinks[key] += 1
        if not exists(tgt): issues["broken internal link"].append((url, tgt))
    # a tags with target=_blank without rel noopener
    for am in re.finditer(r'<a\b[^>]*target="_blank"[^>]*>', h):
        if "noopener" not in am.group(0): issues["_blank without noopener"].append(url)

print()
for k, v in issues.items():
    if not v: continue
    uniq = list(dict.fromkeys(v if not isinstance(v[0], tuple) else v))
    print(f"[{k}] {len(uniq)}")
    for x in uniq[:8]: print("   ", x)
print()
for name, dct in (("duplicate titles", titles), ("duplicate descriptions", descs), ("duplicate H1", h1s)):
    dup = {k: v for k, v in dct.items() if len(v) > 1 and k}
    print(f"[{name}] {len(dup)}")
    for k, v in list(dup.items())[:6]: print("   ", k[:70], "->", v[:4], "..." if len(v) > 4 else "")
orph = [u for u in pages if u != "/" and inlinks.get(u.rstrip("/") or "/", 0) == 0]
print(f"[orphan pages: no inbound internal link] {len(orph)}")
for u in orph[:15]: print("   ", u)

# sitemap vs pages
sm = rd(os.path.join(ROOT, "sitemap.xml"))
locs = [re.sub(BASE, "", u).rstrip("/") or "/" for u in re.findall(r"<loc>([^<]+)</loc>", sm)]
locs = [l for l in locs if not l.endswith((".png", ".jpg", ".webp")) and "unsplash" not in l and not l.startswith("http")]
missing = [l for l in locs if l not in pages]
notin = [u for u in pages if u not in set(locs) and u != "/404.html"]
print(f"[sitemap urls without a page] {len(missing)}", missing[:5])
print(f"[pages not in sitemap] {len(notin)}", notin[:8])

# weight
big = []
for dp, dn, fn in os.walk(os.path.join(ROOT, "assets")):
    for f in fn:
        p = os.path.join(dp, f)
        s = os.path.getsize(p)
        if s > 150_000 and not f.endswith(".woff2"): big.append((s // 1024, os.path.relpath(p, ROOT)))
big.sort(reverse=True)
print(f"[assets > 150 KB] {len(big)}")
for s, p in big[:15]: print(f"   {s} KB  {p}")
sizes = sorted(((os.path.getsize(f) // 1024, u) for u, f in pages.items()), reverse=True)
print("[heaviest HTML pages KB]", sizes[:5])
