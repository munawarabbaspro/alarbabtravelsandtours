"""Write src/data/lastmod.json: the real date each page last changed, taken from git history of dist/.

Commits that only touch markup on every page (speed work: scripts, image hosts, CSS) are listed in SKIP and do not count
as a content change. Run before build.py:  py tools/lastmod.py
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"d482ee0"}                       # 21 Nov 2026 speed commit: changed every page's markup, not its content
def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
commits = [l.split() for l in git("log", "--format=%h %cs", "--", "dist").splitlines()]   # newest first
last = {}
for h, d in commits:
    if h in SKIP:
        continue
    for f in git("show", "--name-only", "--format=", h, "--", "dist").splitlines():
        if f.startswith("dist/") and f.endswith("index.html") and f not in last:
            last[f] = d
out = {}
for f, d in last.items():
    u = "/" + f[len("dist/"):-len("index.html")].rstrip("/")
    out[u if u != "/" else "/"] = d
json.dump(out, open(os.path.join(ROOT, "src", "data", "lastmod.json"), "w"), indent=0, sort_keys=True)
from collections import Counter
print(len(out), "pages;", dict(Counter(out.values())))
