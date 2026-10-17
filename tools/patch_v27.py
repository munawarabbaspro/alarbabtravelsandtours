"""v27 - delete the invented per-package star ratings and review counts from data/site-data.json.
They were copied from the old site (4.8-5.0 stars, "1.2k-4.1k reviews") and cannot be backed up, so no replacement number is added.

  py tools/patch_v27.py --dry    show what would be removed
  py tools/patch_v27.py          apply (idempotent)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "site-data.json")
raw = open(P, encoding="utf-8").read()
d = json.loads(raw)
print("round trip identical to the file on disk:", json.dumps(d, ensure_ascii=False, indent=1) in (raw, raw.rstrip("\n")))
n = 0
for p in d["packages"]:
    for k in ("rating", "reviews"):
        if k in p:
            print("-", p["id"], k, "=", p[k]); del p[k]; n += 1
print("fields removed:", n)
if "--dry" in sys.argv:
    print("DRY RUN - nothing written"); sys.exit()
open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
print("written", P)
