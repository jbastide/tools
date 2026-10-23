# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic>=2.1,<3", "requests>=2.32"]
# ///
"""Reference run for the free AI visibility checker test drive.

Sends the buyer questions in reference-prompts.json straight to each model's API with
live web search on, and saves every raw response under runs/api/<round>/<engine>/.

Keys are read from the environment, or from a KEY=VALUE file whose path is in
AI_REFERENCE_ENV (default ~/.config/copyfororiginals/ai-reference.env). Keys are never
printed or written anywhere. An engine whose key is missing is skipped.

    uv run method/reference_run.py --round 1 --dry-run     # list the calls, no requests
    uv run method/reference_run.py --round 1 --budget 15   # run, stop at about $15
"""
import argparse, json, os, sys, time, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent
FIRMS_CSV = PAGE / "firms.csv"
PROMPTS = json.loads((HERE / "reference-prompts.json").read_text())

# USD per 1M tokens (input, output) and per web search call, from each provider's
# pricing page on October 23, 2026. Perplexity reports its own cost in usage.cost.
PRICES = {
    "claude": {"model": "claude-opus-5-5", "in": 4.00, "out": 20.00, "search": 0.010},
    "openai": {"model": "chat-latest", "in": 5.00, "out": 30.00, "search": 0.010},
    "perplexity": {"model": "perplexity/sonar", "in": 0.25, "out": 2.50, "search": 0.001},
}
CHICAGO = {"city": "Chicago", "region": "Illinois", "country": "US"}


def load_keys():
    path = pathlib.Path(os.environ.get("AI_REFERENCE_ENV",
                        "~/.config/copyfororiginals/ai-reference.env")).expanduser()
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def calls(round_no):
    import csv
    firms = list(csv.DictReader(FIRMS_CSV.open()))
    out = []
    for p in PROMPTS["category_prompts"]:
        for rep in range(1, PROMPTS["category_repeats"] + 1):
            out.append({"prompt_id": p["id"], "rep": rep, "text": p["text"]})
    for f in firms:
        text = PROMPTS["firm_prompt"].format(name=f["name_entered"], website=f["website"])
        for rep in range(1, PROMPTS["firm_repeats"] + 1):
            out.append({"prompt_id": f["firm_id"], "rep": rep, "text": text})
    return out


# ---------- engines: each returns (raw_json, answer_text, cited_urls, cost_usd, model) ----------

def ask_claude(text):
    import anthropic
    client = anthropic.Anthropic(max_retries=3)
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5,
              "user_location": {"type": "approximate", "city": "Chicago",
                                "region": "Illinois", "country": "US"}}]
    messages = [{"role": "user", "content": text}]
    raws, cost = [], 0.0
    for _ in range(5):  # resume pause_turn at most 5 times
        r = client.beta.messages.create(
            model=PRICES["claude"]["model"], max_tokens=16000,
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            tools=tools, messages=messages)
        raws.append(r.model_dump(mode="json"))
        u = r.usage
        searches = getattr(getattr(u, "server_tool_use", None), "web_search_requests", 0) or 0
        p = PRICES["claude"]
        cost += (u.input_tokens * p["in"] + u.output_tokens * p["out"]) / 1e6 + searches * p["search"]
        if r.stop_reason != "pause_turn":
            break
        messages = [{"role": "user", "content": text}, {"role": "assistant", "content": r.content}]
    final = raws[-1]
    answer, urls = [], []
    for b in final["content"]:
        if b.get("type") == "text":
            answer.append(b.get("text", ""))
            for c in b.get("citations") or []:
                if c.get("url"):
                    urls.append(c["url"])
    return {"responses": raws}, "".join(answer), urls, cost, final.get("model")


def _post(url, headers, body):
    import requests
    r = requests.post(url, headers=headers, json=body, timeout=300)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()


def ask_openai(text):
    p = PRICES["openai"]
    raw = _post("https://api.openai.com/v1/responses",
                {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                {"model": p["model"], "input": text,
                 "tools": [{"type": "web_search", "user_location": {"type": "approximate", **CHICAGO}}],
                 "include": ["web_search_call.action.sources"]})
    answer, urls, searches = [], [], 0
    for item in raw.get("output", []):
        if item.get("type") == "web_search_call" and (item.get("action") or {}).get("type") == "search":
            searches += 1
        if item.get("type") == "message":
            for c in item.get("content", []):
                answer.append(c.get("text", ""))
                urls += [a["url"] for a in c.get("annotations") or [] if a.get("url")]
    u = raw.get("usage", {})
    cost = (u.get("input_tokens", 0) * p["in"] + u.get("output_tokens", 0) * p["out"]) / 1e6 + searches * p["search"]
    return raw, "".join(answer), urls, cost, raw.get("model")


def ask_perplexity(text):
    p = PRICES["perplexity"]
    raw = _post("https://api.perplexity.ai/v1/agent",
                {"Authorization": f"Bearer {os.environ['PERPLEXITY_API_KEY']}"},
                {"model": p["model"], "input": text, "tools": [{"type": "web_search"}]})
    answer, urls = [], []
    for item in raw.get("output", []):
        if item.get("type") == "message":
            answer += [c.get("text", "") for c in item.get("content", []) if c.get("type") == "output_text"]
        if item.get("type") == "search_results":
            urls += [r["url"] for r in item.get("results", []) if r.get("url")]
    u = raw.get("usage", {})
    cost = (u.get("cost") or {}).get("total_cost")
    if cost is None:
        cost = (u.get("input_tokens", 0) * p["in"] + u.get("output_tokens", 0) * p["out"]) / 1e6 + p["search"]
    return raw, "".join(answer), urls, float(cost), raw.get("model")


def ask_gemini(text):
    # Off unless --engines names it: Google's Grounding with Google Search terms
    # (ai.google.dev/gemini-api/terms, updated 2026-04-28) bar analyzing Grounded Results
    # and collecting Links by automated means. Jesse decides whether to include it.
    raw = _post("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
                {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
                {"contents": [{"parts": [{"text": text}]}], "tools": [{"google_search": {}}]})
    cand = (raw.get("candidates") or [{}])[0]
    answer = "".join(pt.get("text", "") for pt in (cand.get("content") or {}).get("parts", []))
    meta = cand.get("groundingMetadata") or {}
    u = raw.get("usageMetadata", {})
    out_tokens = u.get("candidatesTokenCount", 0) + u.get("thoughtsTokenCount", 0)
    cost = (u.get("promptTokenCount", 0) * 0.75 + out_tokens * 3.75) / 1e6 + len(meta.get("webSearchQueries", [])) * 0.014
    return raw, answer, [], cost, "gemini-3.8-flash"


ENGINES = {
    "claude": ("ANTHROPIC_API_KEY", ask_claude),
    "openai": ("OPENAI_API_KEY", ask_openai),
    "perplexity": ("PERPLEXITY_API_KEY", ask_perplexity),
    "gemini": ("GEMINI_API_KEY", ask_gemini),
}
DEFAULT_ENGINES = "claude,openai,perplexity"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--engines", default=DEFAULT_ENGINES)
    ap.add_argument("--budget", type=float, default=15.0, help="stop when estimated spend passes this (USD)")
    ap.add_argument("--pause", type=float, default=2.0, help="seconds between calls")
    ap.add_argument("--limit", type=int, default=0, help="only the first N prompts (smoke test)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    load_keys()
    todo = calls(a.round)
    if a.limit:
        todo = todo[:a.limit]
    engines = [e for e in a.engines.split(",") if e in ENGINES]
    live = [e for e in engines if os.environ.get(ENGINES[e][0])]
    print(f"round {a.round}: {len(todo)} prompts x engines {engines} "
          f"(keys found for: {live or 'none'})")
    if a.dry_run:
        for c in todo:
            print(f"  {c['prompt_id']} rep {c['rep']}: {c['text']}")
        return
    spent = 0.0
    log = PAGE / "runs" / "api" / "log.csv"
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    with log.open("a") as lf:
        if new:
            lf.write("round,engine,prompt_id,rep,started_utc,seconds,model,cost_usd,status,file\n")
        for c in todo:
            for e in live:
                d = PAGE / "runs" / "api" / f"r{a.round}" / e
                d.mkdir(parents=True, exist_ok=True)
                f = d / f"{c['prompt_id']}_rep{c['rep']}.json"
                if f.exists():
                    continue  # resumable
                if spent >= a.budget:
                    print(f"budget reached (${spent:.2f}); stopping"); return
                t0 = time.time(); started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                try:
                    raw, answer, urls, cost, model = ENGINES[e][1](c["text"])
                    status = "ok"
                except Exception as ex:  # record and keep going; the error class name is enough
                    raw, answer, urls, cost, model, status = {"error": type(ex).__name__, "detail": str(ex)[:500]}, "", [], 0.0, "", "error"
                spent += cost
                f.write_text(json.dumps({"engine": e, "round": a.round, "prompt_id": c["prompt_id"], "rep": c["rep"],
                                         "prompt": c["text"], "started_utc": started, "model": model,
                                         "answer": answer, "cited_urls": urls, "cost_usd": round(cost, 5),
                                         "raw": raw}, indent=1, ensure_ascii=False))
                lf.write(f"{a.round},{e},{c['prompt_id']},{c['rep']},{started},{time.time()-t0:.1f},{model},{cost:.5f},{status},{f.relative_to(PAGE)}\n")
                lf.flush()
                print(f"{e} {c['prompt_id']} rep {c['rep']}: {status} ${cost:.3f} (total ${spent:.2f})")
                time.sleep(a.pause)
    print(f"done; estimated spend ${spent:.2f}")


if __name__ == "__main__":
    main()
