"""Filter swept posts for AEO topics, count by month/subreddit, pick threads for comment pulls.

Outputs (in e-reddit/):
  monthly_counts.csv        month, subreddit, total_posts, aeo_posts, aeo_share, core_aeo_posts, core_share
  raw/aeo_posts.jsonl       every AEO-matched post with match flags
  raw/selected_ids.json     threads chosen for comment pulls, with reason
"""
import json, os, re, glob, csv, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "raw")
END_TS = None  # set from data

# Broad AEO filter, as specified in the brief (case-insensitive), except GEO (see below).
TERMS = {
    "AEO": r"\baeo\b",
    "generative engine": r"generative engine",
    "answer engine": r"answer engines?",
    "LLM visibility": r"\bllm visibility",
    "AI visibility": r"\bai visibility",
    "AI Overview": r"\bai overviews?\b",
    "AI Mode": r"\bai mode\b",
    "ChatGPT": r"chat ?gpt",
    "Perplexity": r"\bperplexity\b",
    "LLM traffic": r"\bllm traffic",
    "AI traffic": r"\bai traffic",
    "AI search": r"\bai search",
}
TERM_RE = {k: re.compile(v, re.I) for k, v in TERMS.items()}
# GEO: "geo" is everyday PPC/marketing shorthand for geography (geo-targeting, geo split).
# Count it when written in capitals (GEO), or lower-case "geo" when the post also says AI or LLM
# and does not say geo-target/geo-fence/geo location.
GEO_UPPER = re.compile(r"\bGEO\b")
GEO_ANY = re.compile(r"\bgeo\b(?![- ]?(target|fenc|locat|split|test|restrict|modifier))", re.I)
AI_WORD = re.compile(r"\b(ai|llms?)\b", re.I)
# "Core" AEO = matched by something other than a bare mention of ChatGPT or Perplexity
CORE_EXCLUDE = {"ChatGPT", "Perplexity"}

# Measurement/tracking/reporting topic (tightened after the first pass: bare "tool", "data",
# "clicks" pulled in generic AI-writing threads)
MEASURE = re.compile(
    r"\btrack|\bmeasur|\breport|attribut|analytics|\bga4\b|search console|\bgsc\b|referr|"
    r"dashboard|visibility score|how do (you|i|we) (track|measure|know|report|prove|monitor)|"
    r"\bmonitor|\bkpis?\b|\bmetrics?\b|\bcitations?\b|\bcited\b|share of voice|\broi\b|\bprove\b|"
    r"\bprompts?\b|(aeo|geo|ai visibility|llm|ai search|seo) tools?\b|tools? (for|to) (track|monitor|measure)",
    re.I)
# Added on coordinator request: prompt/query selection and representativeness
PROMPT = re.compile(r"\bprompts?\b|synthetic (prompts|queries)|long[- ]tail|keyword list|near me|"
                    r"\bsentiment\b|\baudit\b|how many (prompts|queries)", re.I)
HEALTH = re.compile(r"\b(health ?care|healthcare|medical|clinic|clinics|dental|dentist|doctor|"
                    r"physician|hospital|patients?|med ?spa|chiropract\w*|pharma\w*|therap(y|ist)|"
                    r"dermatolog\w*|orthodont\w*|plastic surgeon)\b", re.I)
GSC = re.compile(r"search console|\bgsc\b", re.I)
GSC_AI = re.compile(r"generative|\bai\b|ai mode|ai overview|\bllm", re.I)
# "Mentions Search Console + AI/generative": both within 150 characters on the same line
_G, _A = r"(search console|\bgsc\b)", r"(generative|ai overviews?|ai mode|\bai\b|\bllms?\b)"
GSC_NEAR_AI = re.compile(f"{_G}[^\\n]{{0,150}}{_A}|{_A}[^\\n]{{0,150}}{_G}", re.I)


def text(p):
    return f"{p.get('title') or ''}\n{p.get('selftext') or ''}"


def aeo_matches(t):
    hits = [k for k, r in TERM_RE.items() if r.search(t)]
    if GEO_UPPER.search(t) or (GEO_ANY.search(t) and AI_WORD.search(t)):
        hits.append("GEO")
    return hits


def month(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m")


def main():
    posts = []
    for f in sorted(glob.glob(os.path.join(RAW, "posts_*.jsonl"))):
        with open(f) as fh:
            posts += [json.loads(l) for l in fh]
    seen = set(); uniq = []
    for p in posts:
        if p["id"] not in seen:
            seen.add(p["id"]); uniq.append(p)
    posts = uniq
    total = collections.Counter(); aeo = collections.Counter(); core = collections.Counter()
    meas_c = collections.Counter()
    term_counts = collections.Counter()
    aeo_posts = []
    for p in posts:
        m, s = month(p["created_utc"]), p["subreddit"]
        total[(m, s)] += 1
        hits = aeo_matches(text(p))
        if hits:
            aeo[(m, s)] += 1
            for h in hits: term_counts[h] += 1
            is_core = bool(set(hits) - CORE_EXCLUDE)
            if is_core: core[(m, s)] += 1
            q = dict(p, aeo_terms=hits, core=is_core,
                     measurement=is_core and bool(MEASURE.search(text(p))),
                     prompt_topic=bool(PROMPT.search(text(p))),
                     healthcare=bool(HEALTH.search(text(p))))
            aeo_posts.append(q)
            if q["measurement"]: meas_c[(m, s)] += 1
    months = sorted({m for m, _ in total})
    subs = sorted({s for _, s in total})
    with open(os.path.join(ROOT, "monthly_counts.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "subreddit", "total_posts", "aeo_posts_broad", "aeo_share_broad",
                    "aeo_posts_core", "aeo_share_core", "aeo_measurement_posts", "measurement_share"])
        for m in months:
            for s in subs + ["ALL"]:
                if s == "ALL":
                    t = sum(total[(m, x)] for x in subs); a = sum(aeo[(m, x)] for x in subs)
                    c = sum(core[(m, x)] for x in subs); me = sum(meas_c[(m, x)] for x in subs)
                else:
                    t, a, c, me = total[(m, s)], aeo[(m, s)], core[(m, s)], meas_c[(m, s)]
                w.writerow([m, s, t, a, f"{a/t:.4f}" if t else "", c, f"{c/t:.4f}" if t else "",
                            me, f"{me/t:.4f}" if t else ""])
    with open(os.path.join(RAW, "aeo_posts.jsonl"), "w") as fh:
        for q in aeo_posts:
            fh.write(json.dumps(q) + "\n")

    # Selection for comment pulls
    meas = [q for q in aeo_posts if q["measurement"]]
    top = sorted(meas, key=lambda q: -(q.get("num_comments") or 0))[:60]
    sel = {q["id"]: {"reason": ["top60_measurement_by_comments"]} for q in top}
    # Coordinator addition: prompt-selection threads and healthcare threads beyond the top 60
    pr = sorted([q for q in meas if q["prompt_topic"] and q["core"]],
                key=lambda q: -(q.get("num_comments") or 0))[:30]
    for q in pr:
        sel.setdefault(q["id"], {"reason": []})["reason"].append("top30_prompt_topic")
    hc = sorted([q for q in meas if q["healthcare"] and q["core"]],
                key=lambda q: -(q.get("num_comments") or 0))[:20]
    for q in hc:
        sel.setdefault(q["id"], {"reason": []})["reason"].append("top20_healthcare")
    since = 1767225600  # 2026-01-01
    gsc_ai = [p for p in posts if p["created_utc"] >= since and GSC_NEAR_AI.search(text(p))]
    for p in gsc_ai:
        sel.setdefault(p["id"], {"reason": []})["reason"].append("gsc_and_ai_since_2026")
    with open(os.path.join(RAW, "selected_ids.json"), "w") as fh:
        json.dump(sel, fh, indent=1)

    print("total posts", len(posts), "by sub", collections.Counter(p["subreddit"] for p in posts))
    print("AEO broad", len(aeo_posts), "core", sum(q["core"] for q in aeo_posts),
          "measurement subset", len(meas))
    print("term counts", term_counts.most_common())
    print("top60 min comments", min((q.get("num_comments") or 0) for q in top) if top else None)
    print("prompt-topic sel", len(pr), "healthcare sel", len(hc),
          "healthcare AEO posts", sum(q["healthcare"] for q in aeo_posts))
    print("gsc+ai since 2026", len(gsc_ai), "selected total", len(sel))


if __name__ == "__main__":
    main()
