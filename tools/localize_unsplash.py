"""Download every Unsplash photo the site uses once (1200px) and store 400/800/1200 WebP copies in src/assets/uns/.

Why: hot-linked Unsplash images load from another host (extra DNS + TLS) and at fixed sizes, which made the route and country
pages slow (Lighthouse LCP 3.9 s on /air-ticketing/islamabad-to-dubai, Nov 2026). build.py serves the local copy when it exists.

  py tools/localize_unsplash.py            (skips photos already done; run after adding new Unsplash ids)
"""
import io, os, re, sys, glob, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "assets", "uns")
WIDTHS = (400, 800, 1200)
os.makedirs(OUT, exist_ok=True)

pids = set()
for f in glob.glob(os.path.join(ROOT, "dist", "**", "*.html"), recursive=True):
    pids.update(re.findall(r"images\.unsplash\.com/photo-([\w-]+)", open(f, encoding="utf-8", errors="ignore").read()))
for f in (os.path.join(ROOT, "src", "build.py"), os.path.join(ROOT, "src", "data", "site-data.json")):
    pids.update(re.findall(r"photo-([0-9]+-[0-9a-f]+)", open(f, encoding="utf-8").read()))
    pids.update(re.findall(r'="(1[0-9]{9,12}-[0-9a-f]{12})"', open(f, encoding="utf-8").read()))

done = fail = 0
for pid in sorted(pids):
    if all(os.path.exists(os.path.join(OUT, f"{pid}-{w}.webp")) for w in WIDTHS):
        continue
    url = f"https://images.unsplash.com/photo-{pid}?auto=format&fm=jpg&q=85&w=1600"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (site image cache)"})
        data = urllib.request.urlopen(req, timeout=60).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as ex:
        print("FAIL", pid, ex); fail += 1; continue
    for w in WIDTHS:
        r = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(OUT, f"{pid}-{w}.webp"), "WEBP", quality=68, method=6)
    done += 1
print(f"{len(pids)} photos, {done} downloaded, {fail} failed")
