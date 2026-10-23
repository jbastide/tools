"""Parse the saved checker runs into data.csv and print the summary numbers used on the page.

    python3 method/analyze.py

Reads runs/agent/*.txt (agent-run checks) and runs/agent-research/run*.json (the Opus
agent's research). Writes data.csv (one row per checker run) and mentions.csv (one row per
firm named in a Geoptie or agent-research answer).
"""
import csv, json, re, pathlib, collections

PAGE = pathlib.Path(__file__).resolve().parent.parent
RUNS = PAGE / "runs" / "agent"
FIRMS = list(csv.DictReader((PAGE / "firms.csv").open()))
ALIASES = {
    "F01": ["malman"],
    "F02": ["844seemike", "844 see mike", "agruss"],
    "F03": ["flanagan injury"],
    "F04": ["disparti"],
    "F05": ["the horwitz law group", "horwitz law group"],
    "F06": ["mccready"],
    "F07": ["anesi"],
    "F08": ["postman law"],
    "F09": ["saks, robinson", "saks robinson"],
    "F10": ["rundio"],
}
ENGINES = ["ChatGPT", "Perplexity", "Claude", "Google"]


def firm_of(name):
    n = name.lower()
    for fid, keys in ALIASES.items():
        if any(k in n for k in keys):
            return fid
    return ""


def header(text, key):
    m = re.search(rf"^{key}: (.*)$", text, re.M)
    return m.group(1).strip() if m else ""


def body(text):
    return text.split("--- result text, verbatim from the page ---", 1)[-1] if "--- result text" in text else \
        text.split("--- result section, verbatim from page text ---", 1)[-1]


def parse_geoptie(text):
    b = body(text).split("--- notes ---")[0]
    flat = re.sub(r"[|;\n]+", " ", b)
    flat = re.sub(r"\s+", " ", flat)
    out = {"score": int(re.search(r"VISIBILITY SCORE (\d+)", flat).group(1))}
    # split into engine sections
    pos = [(m.start(), m.group(1)) for m in re.finditer(r"\b(ChatGPT|Perplexity|Claude|Google) (?=\d+ brands in answer)", flat)]
    for i, (start, eng) in enumerate(pos):
        seg = flat[start:pos[i + 1][0] if i + 1 < len(pos) else len(flat)]
        n = int(re.search(r"(\d+) brands in answer", seg).group(1))
        rank = re.search(r"Ranked #(\d+)", seg)
        rest = seg[rank.end():] if rank else seg.split("Not mentioned", 1)[-1]
        rest = re.sub(r"\+\d+ more results.*", "", rest)
        brands = [x.strip() for _, x in re.findall(r"#(\d+) ([^#]+?)(?=\s*#\d+ |\s*$)", rest.strip())]
        out[eng] = {"n": n, "rank": int(rank.group(1)) if rank else None, "brands": brands}
    return out


def parse_semrush(text):
    b = body(text)
    g = lambda k: (re.search(rf"^{k} ([\d.,]+[KM]?)", b, re.M) or [None, ""])[1]
    return {"score": int(re.search(r"AI Visibility Score (\d+)", b).group(1)), "mentions": g("Mentions"),
            "citations": g("Citations"), "chatgpt": g("ChatGPT"), "gemini": g("Gemini"),
            "ai_mode": g("AI Mode"), "ai_overviews": g("AI Overviews")}


def parse_loamly(text):
    b = body(text)
    m = re.search(r"(\d+)% \| AI VISIBILITY|^(\d+)% AI VISIBILITY", b, re.M)
    pr = re.search(r"(\d+) prompts tested", b)
    sr = re.search(r"SITE READINESS[ |]*(\d+)/100", b)
    return {"score": int(next(x for x in m.groups() if x)), "prompts_tested": int(pr.group(1)) if pr else None,
            "site_readiness": int(sr.group(1)) if sr else None}


def main():
    rows, mentions = [], []
    for f in sorted(RUNS.glob("*_F*_r*.txt")):
        if "generating" in f.name:
            continue
        t = f.read_text()
        checker, firm, rnd = re.match(r"(\w+)_(F\d+)_r(\d+)", f.stem).groups()
        iso = re.search(r"2026-10-\d\dT[\d:]+Z", t)
        started = header(t, "started_utc") or (iso.group(0) if iso else "")
        date = started[:10] or re.search(r"run: \d+, agent, (2026-10-\d\d)", t).group(1)
        row = {"checker": checker, "firm_id": firm, "round": rnd, "date": date, "file": f"runs/agent/{f.name}"}
        if checker == "geoptie":
            g = parse_geoptie(t)
            row["score"] = g["score"]
            for e in ENGINES:
                d = g.get(e, {})
                row[f"{e.lower()}_brands"] = d.get("n", "")
                row[f"{e.lower()}_rank"] = d.get("rank") or ("not named" if d else "")
                for i, b in enumerate(d.get("brands", []), 1):
                    mentions.append({"source": "geoptie", "run": f"{firm}_r{rnd}", "engine": e, "position": i,
                                     "name": b, "firm_id": firm_of(b)})
        elif checker == "semrush":
            row.update(parse_semrush(t))
        elif checker == "loamly":
            row.update(parse_loamly(t))
        rows.append(row)
    for f in sorted((PAGE / "runs" / "agent-research").glob("run*.json")):
        d = json.loads(f.read_text())
        for a in d["answers"]:
            for x in a["firms"]:
                mentions.append({"source": "agent-research", "run": f.stem, "engine": a["id"], "position": x["rank"],
                                 "name": x["name"], "firm_id": firm_of(x["name"])})
    cols = ["checker", "firm_id", "round", "date", "score", "chatgpt_rank", "perplexity_rank", "claude_rank",
            "google_rank", "chatgpt_brands", "perplexity_brands", "claude_brands", "google_brands", "mentions",
            "citations", "chatgpt", "gemini", "ai_mode", "ai_overviews", "prompts_tested", "site_readiness", "file"]
    with (PAGE / "data.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    with (PAGE / "mentions.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["source", "run", "engine", "position", "name", "firm_id"]); w.writeheader(); w.writerows(mentions)

    # summary
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["checker"], r["firm_id"])][r["round"]] = r
    print("firm  geoptie r1/r2   semrush  loamly r1/r2")
    for fm in FIRMS:
        fid = fm["firm_id"]
        g = by[("geoptie", fid)]; s = by[("semrush", fid)]; l = by[("loamly", fid)]
        print(fid, [g[k]["score"] for k in sorted(g)], [s[k]["score"] for k in sorted(s)],
              [l[k]["score"] for k in sorted(l)], [l[k].get("prompts_tested") for k in sorted(l)])
    # engine-level flips in Geoptie between rounds
    flips = total = 0
    for fm in FIRMS:
        g = by[("geoptie", fm["firm_id"])]
        if "1" in g and "2" in g:
            for e in ["chatgpt", "perplexity", "claude"]:
                a = g["1"][f"{e}_rank"] != "not named"; b = g["2"][f"{e}_rank"] != "not named"
                total += 1; flips += a != b
    print(f"geoptie engine-level named/not-named flips between rounds: {flips} of {total}")
    own = collections.Counter(); cross = collections.Counter()
    for m in mentions:
        if m["source"] == "geoptie" and m["firm_id"]:
            (own if m["run"].startswith(m["firm_id"] + "_") else cross)[m["firm_id"]] += 1
    print("geoptie: times each test firm was named in its own runs vs other firms' runs")
    for fm in FIRMS:
        print(" ", fm["firm_id"], own[fm["firm_id"]], cross[fm["firm_id"]])
    ar = collections.Counter(m["firm_id"] for m in mentions if m["source"] == "agent-research" and m["firm_id"])
    print("agent research mentions of test firms:", dict(ar))


if __name__ == "__main__":
    main()
