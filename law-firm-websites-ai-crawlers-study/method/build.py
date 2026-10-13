"""Build the per-site CSV and print the summary. Usage: python3 -I build.py <scratch_dir> <out.csv>"""
import json, csv, sys, collections, re
S = sys.argv[1]
P = json.load(open(S + "/parsed.json")); F = {s["domain"]: s for s in json.load(open(S + "/fetch.json"))["sites"]}
R = [{s["domain"]: s for s in json.load(open(S + "/" + f))["sites"]} for f in ("ua2.json", "ua3.json")]
PARKED = set()  # five parked addresses in the first sample were replaced by the firms' real sites
AI = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "anthropic-ai", "PerplexityBot",
      "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot", "Bytespider", "meta-externalagent", "Amazonbot"]
AI_L = {a.lower() for a in AI} | {"claude-web", "cohere-ai", "ai2bot", "diffbot", "youbot", "duckassistbot", "meta-externalfetcher", "exasearchbot", "timpibot", "oai-adsbot", "amzn-searchbot", "imagesiftbot"}
rows = []
for p in P:
    d = p["domain"]
    if d in PARKED: continue
    runs = {k: [p["home_" + k]] + [r[d][k]["status"] for r in R] for k in ("browser", "gptbot", "claudebot", "perplexitybot")}
    byt = {k: [r[d][k]["bytes"] for r in R] for k in runs}
    b = runs["browser"]
    base = "served" if all(x == 200 for x in b) else ("refused_403" if all(x == 403 for x in b) else "unreachable")
    row = {"firm": p["firm"], "website": d}
    src = p["robots_source"]
    row["robots_txt_source"] = "live" if src == "live" else ("archived_" + src[8:12] + "-" + src[12:14] + "-" + src[14:16] if src.startswith("wayback") else src)
    named = [a for a in p["named_agents"] if a in AI_L]
    row["robots_names_ai_crawlers"] = len(named)
    for a in ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"):
        v = p["robots_" + a]; row["robots_" + a.lower().replace("-", "_")] = {"blocked_by_name": "disallowed", "blocked_by_wildcard": "disallowed_all_bots", "named_not_blocked": "named_allowed", "no_rule": "no_rule"}[v]
    row["robots_ai_crawlers_disallowed"] = ";".join(a for a in AI if p["robots_" + a].startswith("blocked"))
    row["robots_content_signal"] = p["content_signal"].split(" | ")[0]
    lt = p["llms_txt"]
    if lt == "yes":
        fl = p["llms_first_line"].lstrip("﻿").strip().lower()
        row["llms_txt"] = "robots_syntax" if fl.startswith("user-agent") else "yes"
        row["llms_txt_bytes"] = p["llms_bytes"]; g = p["llms_generator_hint"].lower()
        row["llms_txt_generator"] = "Yoast SEO" if "yoast" in g else "Rank Math" if "rank math" in g else "Hostinger Tools" if "hostinger" in g else "MileMark Schema Pro" if "milemark" in g else "not stated"
    else:
        row["llms_txt"] = "no" if lt == "no" else "not_readable"; row["llms_txt_bytes"] = ""; row["llms_txt_generator"] = ""
    row["browser_style_request"] = base
    for k in ("gptbot", "claudebot", "perplexitybot"):
        r = runs[k]
        row["request_as_" + k] = "served" if all(x == 200 for x in r) else "refused_403" if all(x == 403 for x in r) else "refused_429" if all(x == 429 for x in r) else "unreachable" if base == "unreachable" else "mixed"
    row["run_statuses_browser_gptbot_claudebot_perplexitybot"] = " ".join("/".join(str(x) for x in runs[k]) for k in runs)
    row["server_header"] = p["server"] or "none"
    rows.append(row)
w = csv.DictWriter(open(sys.argv[2], "w", newline="", encoding="utf-8"), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
C = collections.Counter; n = len(rows); print("n", n)
print("robots source", C(r["robots_txt_source"][:8] for r in rows))
print("names >=1 AI crawler", sum(r["robots_names_ai_crawlers"] > 0 for r in rows), "| disallows >=1:", [(r["website"], r["robots_ai_crawlers_disallowed"]) for r in rows if r["robots_ai_crawlers_disallowed"]])
print("named AI by source", C((r["robots_txt_source"][:4], r["robots_names_ai_crawlers"] > 0) for r in rows))
print("content signal", [(r["website"], r["robots_content_signal"]) for r in rows if r["robots_content_signal"]])
print("llms", C(r["llms_txt"] for r in rows)); print("llms gen", C(r["llms_txt_generator"] for r in rows if r["llms_txt"] == "yes"))
print("baseline", C(r["browser_style_request"] for r in rows))
sv = [r for r in rows if r["browser_style_request"] == "served"]
print("baseline served n", len(sv), C((r["request_as_gptbot"], r["request_as_claudebot"], r["request_as_perplexitybot"]) for r in sv).most_common())
for k in ("gptbot", "claudebot", "perplexitybot"): print(k, C(r["request_as_" + k] for r in sv))
print("any consistent refusal", sum(any(r["request_as_" + k].startswith("refused") for k in ("gptbot", "claudebot", "perplexitybot")) for r in sv))
print("refused & robots says?", [(r["website"], r["request_as_gptbot"], r["request_as_claudebot"], r["request_as_perplexitybot"], r["robots_gptbot"], r["robots_claudebot"], r["server_header"]) for r in sv if any(r["request_as_" + k].startswith("refused") for k in ("gptbot", "claudebot", "perplexitybot"))])
rf = [r for r in rows if r["browser_style_request"] == "refused_403"]
print("baseline refused n", len(rf), C((r["request_as_gptbot"], r["request_as_claudebot"], r["request_as_perplexitybot"]) for r in rf).most_common())
print("llms among readable", C(r["llms_txt"] for r in rows if r["llms_txt"] != "not_readable"))
