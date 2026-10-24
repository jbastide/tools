"""Write ../planted.csv and ../audit.csv from the receipts repository's benchmark and review files.

Usage: python3 prepare.py PATH_TO_RECEIPTS_REPO

planted.csv  one row per planted case: the claim as checked, the page, and each method's verdict
audit.csv    one row per item receipts flagged in the agent-shopping research notes, with the verdict
             of the source-by-source review that followed and whether the notes were corrected
"""
import csv, json, os, re, sys

R = os.path.expanduser(sys.argv[1])
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
P = os.path.join(R, "bench", "results", "planted")
V = os.path.join(R, "private", "reports", "2026-10-24-agent-shopping-synthesis", "verification")

def jl(path):
    return {json.loads(l)["id"]: json.loads(l) for l in open(path, encoding="utf-8") if l.strip()}

cases = [json.loads(l) for l in open(os.path.join(P, "cases.jsonl"), encoding="utf-8")]
mc, hh = jl(os.path.join(P, "scores-minicheck.jsonl")), jl(os.path.join(P, "scores-hhem.jsonl"))
jw = jl(os.path.join(P, "scores-judge-gemma-4-12b-it-qat-q4_0.jsonl"))
js = jl(os.path.join(P, "scores-judge-gemma-4-12b-it-qat-q4_0-split.jsonl"))
NEG = re.compile(r"\b(not|never|no|none|nor|cannot)\b|n't\b", re.I)
original = {c["base"]: c["claim"] for c in cases if c["kind"] == "original"}
with open(os.path.join(ROOT, "planted.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["case", "source_claim", "kind", "should_pass", "counted", "claim_as_checked", "url",
                "minicheck_score", "minicheck", "minicheck_seconds", "hhem_score", "hhem", "hhem_seconds",
                "judge", "judge_seconds", "judge_split", "judge_split_seconds", "split_into_facts"])
    for c in cases:
        i = c["id"]
        counted = not (c["kind"] == "negation" and NEG.search(original.get(c["base"], "")))
        w.writerow([i, c["base"], c["kind"], c["kind"] == "original", counted, c["claim"], c["url"],
                    mc[i]["score"], mc[i]["verdict"], mc[i]["seconds"], hh[i]["score"], hh[i]["verdict"], hh[i]["seconds"],
                    jw[i]["verdict"], jw[i]["seconds"], js[i]["verdict"], js[i]["seconds"], len(js[i].get("facts") or [])])

batches = [x for k in range(1, 5) for x in json.load(open(os.path.join(V, f"batch{k}.json"), encoding="utf-8"))]
flagged = {(b["claim_id"], it["text"]): it for b in batches for it in b["items"]}
results = [x for k in range(1, 5) for x in json.load(open(os.path.join(V, f"result{k}.json"), encoding="utf-8"))]
with open(os.path.join(ROOT, "audit.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["claim", "line", "kind", "text", "receipts", "review", "source_url", "source_quote", "note", "corrected"])
    for r in results:
        it = flagged.get((r["claim_id"], r["item_text"]), {})
        corrected = bool(r.get("fix")) and r["claim_id"] != "c98"
        w.writerow([r["claim_id"], r["line"], r["item_type"], r["item_text"], it.get("receipts", ""),
                    r["status"], r.get("url") or "", r.get("quote") or "", r.get("note") or "", corrected])
print(len(cases), "planted cases;", len(results), "audit items")
