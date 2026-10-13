"""Read each run's transcript: model ID, tokens, tool calls, searches refused, wall time, and an audit.

Usage: OSINT_TRANSCRIPTS=<folder of agent-<id>.jsonl> python3 usage.py ids.json [folders.json] > usage.csv
Nothing from the transcripts is printed except counts and audit hits.

Token counts: the transcript logs input, cache-write and cache-read tokens for every model response.
It does not log a final output-token count, so output is estimated from the characters the model
visibly wrote (text and tool-call arguments) at 3.5 characters per token. Hidden reasoning is not counted.
"""
import csv, json, os, re, sys
from collections import Counter
from datetime import datetime

SUB = os.environ["OSINT_TRANSCRIPTS"]
RUNS = json.load(open(sys.argv[1]))
FOLDERS = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
# USD per million tokens at list price (platform.claude.com/docs/en/about-claude/pricing, read October 13, 2026):
# input, output, 5-minute cache write, cache read. Haiku 5.5 requests over 100,000 prompt tokens pay 5x.
PRICE = {"haiku": (0.10, 0.50, 0.125, 0.01), "sonnet": (2.0, 10.0, 2.5, 0.10), "opus": (4.0, 20.0, 5.0, 0.20)}
SEARCH_FEE = 0.01      # USD per web search performed ($10 per 1,000), from the same pricing page
OWN = re.compile(r"copyfororiginals|does-google-record-calls|key\.json|\.grader|/projects/tools/", re.I)
WS = re.compile(r"/scratchpad/(ws-[0-9a-f]{8}|[A-Za-z0-9_.\-]+)")
ts = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))

rows = []
for run, aid in RUNS.items():
    tier = run.split("-")[0]
    mine = os.path.basename(FOLDERS.get(run, ""))
    tools, models, per, calls = Counter(), Counter(), {}, {}
    first = last = None
    own_hits, outside, shell_fetch, chars = set(), set(), 0, 0
    refused_budget = refused_domain = searches_run = 0
    for line in open(os.path.join(SUB, f"agent-{aid}.jsonl"), encoding="utf-8"):
        o = json.loads(line)
        if o.get("timestamp"):
            first = first or o["timestamp"]; last = o["timestamp"]
        m = o.get("message") or {}
        content = m.get("content") if isinstance(m.get("content"), list) else []
        if o.get("type") == "assistant" and m.get("id"):
            u = m.get("usage") or {}
            cur = per.setdefault(m["id"], Counter())
            if not cur:
                models[m.get("model", "")] += 1
            for k, f in (("in", "input_tokens"), ("cw", "cache_creation_input_tokens"),
                         ("cr", "cache_read_input_tokens")):
                cur[k] = max(cur[k], u.get(f, 0) or 0)
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and o.get("type") == "assistant":
                chars += len(b.get("text", ""))
            elif b.get("type") == "tool_use":
                tools[b["name"]] += 1
                calls[b["id"]] = b["name"]
                arg = json.dumps(b.get("input", {}))
                chars += len(arg)
                if b["name"] == "Bash" and re.search(r"\bcurl\b|\bwget\b", arg):
                    shell_fetch += 1
                is_block_list = b["name"] == "WebSearch" and "blocked_domains" in arg
                if not is_block_list:
                    own_hits.update(h.lower() for h in OWN.findall(arg))
                if mine:
                    outside.update(d for d in WS.findall(arg) if d != mine)
            elif b.get("type") == "tool_result" and calls.get(b.get("tool_use_id")) == "WebSearch":
                t = b.get("content"); t = t if isinstance(t, str) else json.dumps(t)
                if "Web search was not performed" in t:
                    refused_budget += 1
                elif "not accessible to our user agent" in t:
                    refused_domain += 1
                else:
                    searches_run += 1
    p, cost_in, big = PRICE[tier], 0.0, 0
    tok = Counter()
    for cur in per.values():
        q = p
        if tier == "haiku" and cur["in"] + cur["cw"] + cur["cr"] > 100_000:
            q, big = tuple(5 * x for x in p), big + 1          # Haiku 5.5 long-prompt rate
        cost_in += (cur["in"] * q[0] + cur["cw"] * q[2] + cur["cr"] * q[3]) / 1e6
        tok.update(cur)
    out_tok = round(chars / 3.5)
    out_rate = p[1] * (5 if tier == "haiku" and big else 1)     # worst case for Haiku
    rows.append({
        "run": run, "model_id": " ".join(models), "model_responses": len(per),
        "tool_calls": sum(tools.values()) - tools.get("SubagentHandback", 0),
        "web_search_calls": tools.get("WebSearch", 0), "searches_run": searches_run,
        "searches_refused_site_blocked": refused_domain, "searches_refused_by_cap": refused_budget,
        "web_fetch_calls": tools.get("WebFetch", 0), "shell_calls": tools.get("Bash", 0),
        "shell_calls_fetching_pages": shell_fetch,
        "input_tokens": tok["in"], "cache_write_tokens": tok["cw"], "cache_read_tokens": tok["cr"],
        "peak_context_tokens": max((c["in"] + c["cw"] + c["cr"] for c in per.values()), default=0),
        "responses_over_100k": big, "visible_output_tokens_est": out_tok,
        "cost_input_side_usd": round(cost_in, 3), "cost_output_est_usd": round(out_tok * out_rate / 1e6, 3),
        "cost_search_fees_usd": round(searches_run * SEARCH_FEE, 2),
        "cost_est_usd": round(cost_in + out_tok * out_rate / 1e6 + searches_run * SEARCH_FEE, 3),
        "minutes": round((ts(last) - ts(first)).total_seconds() / 60, 1),
        "audit_own_site_or_key": " ".join(sorted(own_hits)),
        "audit_paths_outside_own_folder": " ".join(sorted(outside)),
    })
w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
