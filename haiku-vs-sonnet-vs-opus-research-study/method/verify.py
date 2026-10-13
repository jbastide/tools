"""Machine-check every quote in every run against the page it cites, then score recall against key.json.

Usage: python3 verify.py            (reads ../runs/*.json, writes claims_checked.csv and run_checks.csv here)
       OSINT_RUNS=../pilot/runs OSINT_OUT=../pilot python3 verify.py

Quote grades
  verbatim     the whole quote is on the page (spacing, punctuation and case ignored)
  near         at least 80% of the quote's 5-word sequences are on the page (edited, trimmed or stitched)
  not_on_page  the page was read and the quote is not there
  unreachable  the page could not be fetched from this machine (blocked, removed, or script-rendered)
"""
import csv, glob, json, os, re, sys
from urllib.parse import urlparse
from pagetext import page_text, loose, words

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.environ.get("OSINT_RUNS", os.path.join(HERE, "..", "runs"))
KEY = json.load(open(os.path.join(HERE, "key.json")))
OWN = "copyfororiginals.com"

def load(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    try:
        return json.loads(raw), True
    except Exception:
        m = re.search(r"\{.*\}", raw, re.S)          # tolerate a code fence or stray text
        try:
            return json.loads(m.group(0)), False
        except Exception:
            return {"claims": [], "leads": [], "not_found": []}, False

_pages = {}
def page(url):
    if url not in _pages:
        status, text = page_text(url)
        _pages[url] = (status, loose(text), " ".join(words(text)))
    return _pages[url]

def grade(quote, url):
    if not url.startswith("http"):
        return "unreachable", 0.0
    status, lz, wtext = page(url)
    q = loose(quote)
    if status == "200" and q and q in lz:
        return "verbatim", 1.0
    if status != "200" or len(lz) < 400:      # too little text to judge: blocked, removed or script-rendered
        return "unreachable", 0.0
    w = words(quote)
    sh = [" ".join(w[i:i + 5]) for i in range(max(1, len(w) - 4))]
    hit = sum(1 for s in sh if s in wtext) / len(sh) if sh else 0.0
    return ("near" if hit >= 0.8 else "not_on_page"), round(hit, 2)

def covers(fact, claim):
    q = loose(claim.get("quote", ""))
    if any(loose(p) in q for p in fact["phrases"]):
        return True
    rx = fact.get("regex")
    blob = (claim.get("claim", "") + " " + claim.get("quote", "") + " " + claim.get("url", ""))
    return bool(rx and re.search(rx, blob, re.I | re.S))

rows, summary = [], []
for path in sorted(glob.glob(os.path.join(RUNS, "*.json"))):
    run = os.path.basename(path)[:-5]
    data, valid = load(path)
    claims = [c for c in data.get("claims", []) if isinstance(c, dict)]
    counts = {"verbatim": 0, "near": 0, "not_on_page": 0, "unreachable": 0}
    for c in claims:
        g, share = grade(str(c.get("quote", "")), str(c.get("url", "")))
        c["_grade"], c["_share"] = g, share
        counts[g] += 1
        c["_facts"] = [f["id"] for f in KEY if covers(f, c)]
        rows.append({"run": run, "model": run.split("-")[0], "claim_id": c.get("id", ""),
                     "question": c.get("question", ""), "source_type": c.get("source_type", ""),
                     "host": urlparse(str(c.get("url", ""))).netloc, "url": c.get("url", ""),
                     "quote_grade": g, "shingle_share": share,
                     "quote_chars": len(str(c.get("quote", ""))),
                     "key_facts": " ".join(c["_facts"]),
                     "claim": c.get("claim", ""), "quote": c.get("quote", "")})
    ok = lambda c: c["_grade"] == "verbatim"
    found_any = {f for c in claims for f in c["_facts"]}
    found_ok = {f for c in claims if ok(c) for f in c["_facts"]}
    urls = {c.get("url", "") for c in claims}
    summary.append({"run": run, "model": run.split("-")[0], "valid_json": valid,
                    "claims": len(claims), **counts,
                    "distinct_urls": len(urls),
                    "distinct_hosts": len({urlparse(u).netloc for u in urls}),
                    "key_facts_verbatim": len(found_ok), "key_facts_any": len(found_any),
                    "key_total": len(KEY),
                    "missed_key_facts": " ".join(f["id"] for f in KEY if f["id"] not in found_ok),
                    "extra_verbatim_claims": sum(1 for c in claims if ok(c) and not c["_facts"]),
                    "leads": len(data.get("leads", [])), "not_found": len(data.get("not_found", [])),
                    "cites_own_site": any(OWN in u for u in urls),
                    "over_300_chars": sum(1 for c in claims if len(str(c.get("quote", ""))) > 300)})

out = os.environ.get("OSINT_OUT", HERE)
for name, data in (("claims_checked.csv", rows), ("run_checks.csv", summary)):
    if data:
        with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
for s in summary:
    print(s)
