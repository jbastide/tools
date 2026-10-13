"""Shuffle every claim from every run into one list with the run label removed, for blind reading."""
import csv, glob, json, os, random, sys
from urllib.parse import urlparse
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.environ.get("OSINT_RUNS", os.path.join(HERE, "..", "runs"))
OUT = os.environ.get("OSINT_OUT", HERE)
items = []
for path in sorted(glob.glob(os.path.join(RUNS, "*.json"))):
    run = os.path.basename(path)[:-5]
    for c in json.load(open(path)).get("claims", []):
        items.append((run, c))
random.seed(20261013)
random.shuffle(items)
with open(os.path.join(OUT, "blind_map.csv"), "w", newline="") as m, \
     open(os.path.join(OUT, "blind_review.txt"), "w") as r:
    w = csv.writer(m); w.writerow(["blind_id", "run", "claim_id"])
    for i, (run, c) in enumerate(items, 1):
        bid = f"B{i:03d}"
        w.writerow([bid, run, c.get("id", "")])
        r.write(f'{bid} [{urlparse(str(c.get("url", ""))).netloc.replace("www.", "")}] '
                f'CLAIM: {c.get("claim", "")}\n     QUOTE: {c.get("quote", "")}\n')
print(len(items), "claims")
