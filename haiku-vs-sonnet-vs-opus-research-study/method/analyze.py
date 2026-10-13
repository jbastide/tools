"""Join the quote check, the two blind grades, the usage read and the two fact lists into the published files.

Usage: python3 analyze.py           (after verify.py; writes ../data.csv, ../runs.csv, ../facts.csv, ../sources.csv)

Outputs: data.csv (one row per claim), runs.csv (one row per run),
facts.csv (one row per fact, with the runs that found it), sources.csv (one row per cited page).
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict
from urllib.parse import urlparse
from pagetext import loose

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("OSINT_WORK", HERE)          # claims_checked.csv, run_checks.csv, usage.csv, blind_map.csv, grader files
OUT = os.environ.get("OSINT_OUT", os.path.join(HERE, ".."))   # where the published CSV files go
KEY = json.load(open(os.path.join(HERE, "key.json")))
EXTRA = json.load(open(os.path.join(HERE, "extras.json")))
ORDER = ["haiku-1", "haiku-2", "haiku-3", "sonnet-1", "sonnet-2", "sonnet-3", "opus-1", "opus-2", "opus-3"]

claims = list(csv.DictReader(open(os.path.join(WORK, "claims_checked.csv"))))
usage = {r["run"]: r for r in csv.DictReader(open(os.path.join(WORK, "usage.csv")))}
runsum = {r["run"]: r for r in csv.DictReader(open(os.path.join(WORK, "run_checks.csv")))}
bmap = {(r["run"], r["claim_id"]): r["blind_id"] for r in csv.DictReader(open(os.path.join(WORK, "blind_map.csv")))}

def grades(name):
    p = os.path.join(WORK, name)
    if not os.path.exists(p):
        return None
    return {f["id"]: f["grade"].upper() for f in json.load(open(p)).get("flags", [])}
g1, g2 = grades("grader1.json"), grades("grader2.json")

def host(u):
    return urlparse(u).netloc.replace("www.", "").replace("old.", "")

def canon(u):
    """One label per page: host plus path, with tracking and language parameters dropped."""
    p = urlparse(u)
    path = re.sub(r"/+$", "", p.path)
    m = re.search(r"reddit\.com/r/([^/]+)/comments/([a-z0-9]+)", u)
    if m:
        return f"reddit.com/r/{m.group(1)}/comments/{m.group(2)}"
    q = "&".join(sorted(x for x in p.query.split("&") if x and not re.match(r"(hl|utm_|ref|sjid|visit_id|rd|co|oco)", x)))
    return host(u) + path + ("?" + q if q else "")

def kind(h):
    if h.endswith("google.com"):
        return "Google"
    if h in ("ncbar.gov", "wisbar.org", "ctbar.org", "nycbar.org", "americanbar.org"):
        return "Bar"
    if h in ("reddit.com", "localsearchforum.com", "linkedin.com", "groups.google.com"):
        return "Thread or post"
    return "Trade press, blog or other"

for c in claims:
    q, h = loose(c["quote"]), host(c["url"])
    c["host"] = h
    c["page"] = canon(c["url"])
    c["source_group"] = kind(h)
    c["extra_finds"] = " ".join(x["id"] for x in EXTRA
                                if any(loose(p) in q for p in x.get("phrases", [])) or h in x.get("hosts", []))
    bid = bmap.get((c["run"], c["claim_id"]), "")
    c["blind_id"] = bid
    c["grader1"] = g1.get(bid, "OK") if g1 is not None else ""      # blank = this set was not graded
    c["grader2"] = g2.get(bid, "OK") if g2 is not None else ""

cols = ["run", "model", "claim_id", "blind_id", "question", "source_type", "source_group", "host", "page", "url",
        "quote_grade", "quote_chars", "key_facts", "extra_finds", "grader1", "grader2", "claim", "quote"]
with open(os.path.join(OUT, "data.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader()
    w.writerows(sorted(claims, key=lambda c: (ORDER.index(c["run"]), int(re.sub(r"\D", "", c["claim_id"]) or 0))))

by = defaultdict(list)
for c in claims:
    by[c["run"]].append(c)
rows = []
for run in ORDER:
    cs, u, s = by[run], usage[run], runsum[run]
    grp = Counter(c["source_group"] for c in cs)
    rows.append({
        "run": run, "model_id": u["model_id"], "claims": len(cs),
        "quotes_verbatim": sum(c["quote_grade"] == "verbatim" for c in cs),
        "quotes_not_verbatim": sum(c["quote_grade"] != "verbatim" for c in cs),
        "pages_cited": len({c["page"] for c in cs}), "sites_cited": len({c["host"] for c in cs}),
        "key_facts_found": len({f for c in cs for f in c["key_facts"].split()}), "key_facts_total": len(KEY),
        "extra_finds": len({f for c in cs for f in c["extra_finds"].split()}), "extra_finds_total": len(EXTRA),
        "claims_google": grp["Google"], "claims_bar": grp["Bar"],
        "claims_thread": grp["Thread or post"], "claims_other": grp["Trade press, blog or other"],
        "grader1_part": sum(c["grader1"] == "PART" for c in cs) if g1 is not None else "",
        "grader1_not": sum(c["grader1"] == "NOT" for c in cs) if g1 is not None else "",
        "flagged_by_both": sum(c["grader1"] != "OK" and c["grader2"] != "OK" for c in cs) if g1 is not None and g2 is not None else "",
        "grader2_part": sum(c["grader2"] == "PART" for c in cs) if g2 is not None else "",
        "grader2_not": sum(c["grader2"] == "NOT" for c in cs) if g2 is not None else "",
        "leads": s["leads"], "not_found": s["not_found"],
        **{k: u[k] for k in ("tool_calls", "searches_run", "searches_refused_site_blocked", "searches_refused_by_cap",
                             "web_fetch_calls", "shell_calls", "shell_calls_fetching_pages", "model_responses",
                             "input_tokens", "cache_write_tokens", "cache_read_tokens", "peak_context_tokens",
                             "responses_over_100k", "visible_output_tokens_est", "cost_input_side_usd",
                             "cost_output_est_usd", "cost_search_fees_usd", "cost_est_usd", "minutes")},
    })
with open(os.path.join(OUT, "runs.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

frows = []
for group, items, col, label in (("key", KEY, "key_facts", "fact"), ("extra", EXTRA, "extra_finds", "find")):
    for it in items:
        found = [r for r in ORDER if any(it["id"] in c[col].split() for c in by[r])]
        frows.append({"list": group, "id": it["id"], "fact": it[label],
                      "haiku_runs": sum(r.startswith("haiku") for r in found),
                      "sonnet_runs": sum(r.startswith("sonnet") for r in found),
                      "opus_runs": sum(r.startswith("opus") for r in found),
                      "runs_found": " ".join(found)})
with open(os.path.join(OUT, "facts.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(frows[0].keys())); w.writeheader(); w.writerows(frows)

pages = defaultdict(lambda: {"runs": set(), "claims": 0, "group": "", "url": ""})
for c in claims:
    p = pages[c["page"]]; p["runs"].add(c["run"]); p["claims"] += 1; p["group"] = c["source_group"]; p["url"] = p["url"] or c["url"]
with open(os.path.join(OUT, "sources.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["page", "source_group", "example_url", "claims", "runs_citing", "haiku_runs", "sonnet_runs", "opus_runs"])
    for k, p in sorted(pages.items(), key=lambda kv: (-len(kv[1]["runs"]), kv[0])):
        r = p["runs"]
        w.writerow([k, p["group"], p["url"], p["claims"], len(r), sum(x.startswith("haiku") for x in r),
                    sum(x.startswith("sonnet") for x in r), sum(x.startswith("opus") for x in r)])
print(len(claims), "claims;", len(pages), "pages")
