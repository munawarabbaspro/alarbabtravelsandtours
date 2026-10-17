"""Pre-deploy test of the built site (dist/). Live pages only (preview-* pages are skipped; they are noindex and not in the zip).
Checks: H1, title/description, canonical, robots, JSON-LD parses, FAQ schema = visible FAQ, internal links and assets exist,
image alt/size, sitemap coverage, banned claims, phone numbers, file sizes."""
import os, re, json, html, sys
from collections import Counter, defaultdict
D = os.path.join(os.path.dirname(__file__), "..", "dist")
BASE = "https://www.alarbabtravel.com"
pages = {}
for root, _, files in os.walk(D):
    for f in files:
        if f.endswith(".html"):
            p = os.path.join(root, f)
            rel = "/" + os.path.relpath(p, D).replace("\\", "/")
            url = "/" if rel == "/index.html" else rel[:-len("/index.html")] if rel.endswith("/index.html") else rel
            if url.startswith("/preview-"):
                continue
            pages[url] = open(p, encoding="utf-8").read()
issues = defaultdict(list)
def add(k, u, x=""):
    issues[k].append(f"{u} {x}".strip())
titles, descs = Counter(), Counter()
sm = open(os.path.join(D, "sitemap.xml"), encoding="utf-8").read()
smurls = set(u.replace(BASE, "") or "/" for u in re.findall(r"<loc>([^<]+)</loc>", sm))
def exists(path):
    path = path.split("#")[0].split("?")[0]
    if path in ("", "/"):
        return True
    fp = os.path.join(D, path.lstrip("/"))
    return os.path.isfile(fp) or os.path.isfile(os.path.join(fp, "index.html")) or os.path.isfile(fp + ".html")
redirects = open(os.path.join(D, "_redirects"), encoding="utf-8").read() if os.path.exists(os.path.join(D, "_redirects")) else ""
redir_src = set(l.split()[0] for l in redirects.splitlines() if l.strip() and not l.startswith("#"))
for u, h in pages.items():
    body = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", h)
    noi = re.search(r'<meta name="robots" content="[^"]*noindex', h)
    n1 = len(re.findall(r"<h1[\s>]", body))
    if n1 != 1 and u != "/404" and not h.count('http-equiv="refresh"'):
        add("H1 count != 1", u, str(n1))
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    t = html.unescape(t.group(1).strip()) if t else ""
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    d = html.unescape(d.group(1)) if d else ""
    if not t: add("missing title", u)
    if not d: add("missing description", u)
    if not noi:
        titles[t] += 1; descs[d] += 1
        if len(t) > 65: add("title > 65 chars", u, f"({len(t)}) {t}")
        if not (110 <= len(d) <= 165): add("description length outside 110-165", u, f"({len(d)})")
        c = re.search(r'<link rel="canonical" href="([^"]+)"', h)
        if not c: add("missing canonical", u)
        elif not c.group(1).startswith(BASE): add("canonical not on www domain", u, c.group(1))
        elif c.group(1) != BASE + (u if u != "/" else "/"): add("canonical differs from URL", u, c.group(1))
        if u not in smurls and u != "/404": add("indexable page not in sitemap", u)
    elif u in smurls:
        add("noindex page in sitemap", u)
    # JSON-LD
    faq_q = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            j = json.loads(m.group(1))
        except Exception as e:
            add("JSON-LD does not parse", u, str(e)[:60]); continue
        for item in (j if isinstance(j, list) else [j]):
            if item.get("@type") == "FAQPage":
                faq_q += [q["name"] for q in item.get("mainEntity", [])]
            s = json.dumps(item)
            if "aggregateRating" in s or '"Review"' in s: add("rating/review schema", u)
    vis_q = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<summary>(.*?)</summary>", body, re.S)]
    for q in faq_q:
        if q not in vis_q: add("FAQ schema question not visible", u, q[:60])
    # links and assets
    for href in re.findall(r'href="(/[^"]*)"', body):
        if href.startswith("//"): continue
        if not exists(href) and href.split("#")[0].split("?")[0] not in redir_src:
            add("broken internal link", u, href)
    for src in re.findall(r'<img[^>]+src="(/[^"]+)"', body):
        if not exists(src): add("missing image file", u, src)
    for tag in re.findall(r"<img\b[^>]*>", body):
        if "alt=" not in tag: add("img without alt", u, tag[:80])
        if "width=" not in tag or "height=" not in tag: add("img without width/height", u, tag[:80])
    for a in re.findall(r"<a\b[^>]*>(.*?)</a>", body, re.S):
        pass
    # claims (owner rules)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", body))
    for pat, k in [(r"\bIATA\b", "IATA"), (r"since 2009|Established 2009", "since 2009"), (r"\bNo\.\s?1\b(?!2)", "No.1"), (r"#1\b", "#1"),
                   (r"5320968|5436696", "old phone number"), (r"alarbabtravels\.pk|localhost", "wrong host"), (r"best visa consultant|top rated", "superlative")]:
        if re.search(pat, txt, re.I): add("claim: " + k, u)
    if re.search(r"\b98\s?%", txt): issues["info: 98% claim pages"].append(u)
    if re.search(r"DTS[- ]licen", txt, re.I): issues["info: DTS licensed wording pages"].append(u)
    if re.search(r"\bDubai\b|\bUAE\b", txt): issues["info: Dubai/UAE mentioned"].append(u)
    sz = len(h.encode())
    if sz > 250_000: add("HTML > 250 KB", u, f"{sz//1024} KB")
for t, n in titles.items():
    if n > 1: add("duplicate title", "", f"x{n} {t}")
for d, n in descs.items():
    if n > 1: add("duplicate description", "", f"x{n} {d[:70]}")
for s in smurls:
    if s not in pages: add("sitemap URL has no page", s)
robots = open(os.path.join(D, "robots.txt"), encoding="utf-8").read() if os.path.exists(os.path.join(D, "robots.txt")) else ""
if f"Sitemap: {BASE}/sitemap.xml" not in robots: add("robots.txt sitemap line", "/robots.txt")
print(f"live pages: {len(pages)}  sitemap urls: {len(smurls)}")
for k in sorted(issues):
    v = issues[k]
    print(f"\n[{len(v)}] {k}")
    for x in v[:6]:
        print("   ", x)
