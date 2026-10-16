"""Merge AI coding outputs, verify every quote against raw JSON, write CSVs and summary JSON.

Inputs: coding/out_*.json, raw/posts_*.jsonl, raw/comments/<id>.json, raw/selected_ids.json
Outputs: categorised_threads.csv, raw/verified_quotes.json, raw/analysis_summary.json
"""
import json, os, glob, csv, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "raw")
CATS = ["NO_LLM_DATA", "GA4_ATTRIBUTION", "GSC_AI_DATA", "TRAFFIC_LOSS_DIAG", "TOOL_COST_ACCURACY",
        "NONDETERMINISM", "REVENUE_ROI", "CLIENT_PRESSURE", "AEO_IS_SEO", "PROMPT_SELECTION",
        "FAN_OUT", "FORMAT_CLAIMS"]

posts = {}
for f in glob.glob(os.path.join(RAW, "posts_*.jsonl")):
    for l in open(f):
        p = json.loads(l); posts[p["id"]] = p
sel = json.load(open(os.path.join(RAW, "selected_ids.json")))
coded = {}
for f in sorted(glob.glob(os.path.join(ROOT, "coding", "out_*.json"))):
    for t in json.load(open(f))["threads"]:
        coded[t["id"]] = t
missing = [i for i in sel if i not in coded]
extra = [i for i in coded if i not in sel]


def bodies(pid):
    p = posts[pid]
    b = {"post": (p.get("title") or "") + "\n" + (p.get("selftext") or "")}
    cp = os.path.join(RAW, "comments", f"{pid}.json")
    if os.path.exists(cp):
        for c in json.load(open(cp)):
            b["c:" + c["id"]] = (c.get("body") or "", c["created_utc"])
    return b


def date(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")


verified, bad = [], []
rows = []
cat_threads = collections.defaultdict(set)
for pid, t in coded.items():
    if pid not in posts:
        bad.append({"id": pid, "why": "unknown thread"}); continue
    p = posts[pid]
    b = bodies(pid)
    cats = [c for c in t.get("categories", []) if c in CATS]
    for c in cats:
        cat_threads[c].add(pid)
    items = [dict(q, kind="cat") for q in t.get("quotes", [])] + \
            [dict(q, kind="gsc", category="GSC_REPORT") for q in t.get("gsc_report_points", [])]
    for q in items:
        src, quote = q.get("source", ""), q.get("quote", "")
        body = b.get(src)
        if isinstance(body, tuple):
            text, ts = body
        else:
            text, ts = body, p["created_utc"]
        ok = text is not None and quote and quote in text
        if not ok:
            # find it anywhere else in the thread (coder cited the wrong source)
            for k, v in b.items():
                vt = v[0] if isinstance(v, tuple) else v
                if quote and quote in vt:
                    src, ok = k, True
                    ts = v[1] if isinstance(v, tuple) else p["created_utc"]
                    break
        rec = {"thread": pid, "subreddit": p["subreddit"], "category": q.get("category"),
               "point": q.get("point"), "quote": quote, "source": src, "date": date(ts),
               "promo": bool(q.get("promo")), "thread_title": p["title"],
               "permalink": f"https://www.reddit.com/r/{p['subreddit']}/comments/{pid}/" +
                            (f"comment/{src[2:]}/" if src.startswith("c:") else "")}
        (verified if ok else bad).append(rec)
    rows.append([pid, p["subreddit"], date(p["created_utc"]), p["title"], p.get("num_comments"),
                 ";".join(sel.get(pid, {}).get("reason", [])), t.get("relevant"),
                 t.get("healthcare"), ";".join(cats),
                 ";".join(g.get("point", "") for g in t.get("gsc_report_points", [])),
                 t.get("note", "")])

rows.sort(key=lambda r: r[2])
with open(os.path.join(ROOT, "categorised_threads.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "subreddit", "date", "title", "num_comments", "selection_reason", "relevant",
                "healthcare", "categories", "gsc_report_points", "coder_note"])
    w.writerows(rows)
json.dump({"verified": verified, "failed": bad}, open(os.path.join(RAW, "verified_quotes.json"), "w"),
          indent=1)

relevant = [r for r in rows if r[6]]
hc = [r for r in rows if r[7]]
summary = {
    "selected": len(sel), "coded": len(coded), "missing": missing, "extra": extra,
    "relevant": len(relevant), "healthcare_threads": len(hc),
    "quotes_verified": len(verified), "quotes_failed": len(bad),
    "category_threads": {c: len(cat_threads[c]) for c in CATS},
    "category_threads_healthcare": {c: len([i for i in cat_threads[c] if coded[i].get("healthcare")])
                                    for c in CATS},
    "by_reason": {},
}
for reason in ["top60_measurement_by_comments", "gsc_and_ai_since_2026", "top30_prompt_topic",
               "top20_healthcare"]:
    ids = [i for i in sel if reason in sel[i]["reason"] and i in coded]
    summary["by_reason"][reason] = {"n": len(ids), "relevant": sum(bool(coded[i].get("relevant")) for i in ids),
                                    **{c: len([i for i in ids if i in cat_threads[c]]) for c in CATS}}
gsc_pts = collections.Counter()
for t in coded.values():
    for g in t.get("gsc_report_points", []):
        gsc_pts[g.get("point", "").lower()] += 1
summary["gsc_report_points"] = gsc_pts.most_common()
summary["gsc_report_threads"] = sum(1 for t in coded.values() if t.get("gsc_report_points"))
json.dump(summary, open(os.path.join(RAW, "analysis_summary.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in summary.items() if k != "gsc_report_points"}, indent=1))
print("gsc points:", gsc_pts.most_common(40))
