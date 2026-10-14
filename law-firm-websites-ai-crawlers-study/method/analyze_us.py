"""Turn the collection JSON into the per-site CSV and a stats JSON.
Usage: python3 -I analyze_us.py <collect.json> <raw_dir> <wayback.json or -> <out.csv> <stats.json> [fetch2.json]"""
import collections, csv, json, os, re, statistics, sys, hashlib

AI = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "anthropic-ai", "PerplexityBot",
      "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot", "Bytespider", "meta-externalagent", "Amazonbot"]
AI_L = {a.lower() for a in AI} | {"claude-web", "cohere-ai", "ai2bot", "diffbot", "youbot", "duckassistbot", "meta-externalfetcher",
                                  "exasearchbot", "timpibot", "oai-adsbot", "amzn-searchbot", "imagesiftbot"}
NAMES = ["gptbot", "claudebot", "perplexitybot", "googlebot", "bingbot"]

def is_html(b):
    h = b[:600].lstrip().lower()
    return h.startswith(b"<!doctype") or h.startswith(b"<html") or b"<head" in h or b"<body" in h

def parse_robots(text):
    groups, cur, last_ua, signals = [], None, False, []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line: continue
        k, v = [x.strip() for x in line.split(":", 1)]; k = k.lower()
        if k == "user-agent":
            if not last_ua: cur = {"agents": [], "rules": []}; groups.append(cur)
            cur["agents"].append(v.lower()); last_ua = True
        elif k in ("allow", "disallow"):
            if cur is not None: cur["rules"].append((k, v))
            last_ua = False
        elif k == "content-signal": signals.append(v)
    return groups, signals

def full_block(rules):
    return any(k == "disallow" and v in ("/", "/*") for k, v in rules) and not any(k == "allow" and v in ("/", "/*") for k, v in rules)

def verdict(groups, bot):
    named = [g for g in groups if bot.lower() in g["agents"]]
    if named: return "disallowed" if full_block([r for g in named for r in g["rules"]]) else "named_allowed"
    return "disallowed_all_bots" if full_block([r for g in groups if "*" in g["agents"] for r in g["rules"]]) else "no_rule"

def outcome(statuses):
    if all(x == 200 for x in statuses): return "served"
    if all(x == 0 for x in statuses): return "unreachable"
    if all(x != 200 for x in statuses):
        codes = sorted({x for x in statuses if x})
        return "refused_" + "_".join(str(c) for c in codes)
    return "mixed"

def main():
    d = json.load(open(sys.argv[1])); raw = sys.argv[2]
    wb = json.load(open(sys.argv[3])) if sys.argv[3] != "-" and os.path.exists(sys.argv[3]) else {}
    f2 = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else {"robots_txt": [], "llms_txt": {}}
    ux = f2.get("us_exit", {})
    rows, extra = [], {}
    for s in d["sites"]:
        dom = s["domain"]; row = {"firm": s["firm"], "website": dom}
        # robots.txt
        body, src = b"", "unreadable"
        R = s["robots.txt"]; p = f"{raw}/{dom}.robots.txt"
        if R["status"] == 200 and os.path.exists(p):
            body = open(p, "rb").read()
            src = "live" if body.strip() and not is_html(body) else "none"
            if src == "none": body = b""
        elif R["status"] in (404, 410): src = "none"
        elif dom in ux:
            body = open(f"{raw}/{dom}.robots.txt.usexit", "rb").read(); src = "us_exit"
        elif dom in f2["robots_txt"]:
            body = open(f"{raw}/{dom}.robots.txt.fetch2", "rb").read(); src = "second_fetch"
        elif dom in wb and wb[dom].get("status") == 200:
            body = open(f"{raw}/{dom}.robots.txt.wayback", "rb").read(); c = wb[dom]["capture"]
            src = f"archived_{c[:4]}-{c[4:6]}-{c[6:8]}"
            if is_html(body): body, src = b"", "unreadable"
        groups, signals = parse_robots(body.decode("utf-8", "replace"))
        named = sorted({a for g in groups for a in g["agents"] if a in AI_L})
        row["robots_txt_source"] = src; row["robots_names_ai_crawlers"] = len(named) if src != "unreadable" else ""
        V = {a: (verdict(groups, a) if src != "unreadable" else "unknown") for a in AI}
        for a in ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Google-Extended", "CCBot"):
            row["robots_" + a.lower().replace("-", "_")] = V[a]
        row["robots_ai_crawlers_disallowed"] = ";".join(a for a in AI if V[a].startswith("disallowed"))
        row["robots_content_signal"] = signals[0] if signals else ""
        # llms.txt
        L = s["llms.txt"]; p = f"{raw}/{dom}.llms.txt"; lb = open(p, "rb").read() if os.path.exists(p) else b""; lsrc = "live"
        if L["status"] not in (200, 404, 410) and dom in ux:
            L = {"status": ux[dom]["llms_status"], "ctype": ux[dom]["llms_ctype"]}; lb = open(p + ".usexit", "rb").read(); lsrc = "us_exit"
        row["llms_txt_bytes"] = ""; row["llms_txt_generator"] = ""
        if L["status"] == 200 and lb.strip() and not is_html(lb) and "html" not in L["ctype"].lower():
            t = lb.decode("utf-8", "replace"); first = t.lstrip("﻿").strip().splitlines()[0].strip().lower()
            row["llms_txt"] = "robots_syntax" if first.startswith("user-agent") else "yes"
            row["llms_txt_bytes"] = len(lb)
            g = re.search(r"yoast|rank ?math|aioseo|all in one seo|seopress|hostinger|milemark schema pro|generated by[^\n]{0,60}", t, re.I)
            g = g.group(0).lower() if g else ""
            row["llms_txt_generator"] = ("Yoast SEO" if "yoast" in g else "Rank Math" if "rank" in g else "Hostinger Tools" if "hostinger" in g else
                                         "MileMark Schema Pro" if "milemark" in g else "All in One SEO" if ("aioseo" in g or "all in one" in g) else
                                         "SEOPress" if "seopress" in g else ("other: " + g[13:60].strip() if g else "not stated")) if row["llms_txt"] == "yes" else ""
            extra[dom] = {"llms_md5": hashlib.md5(lb).hexdigest()[:8], "disallow_training": b"Disallow-Training" in lb}
        elif L["status"] in (404, 410) or (L["status"] == 200 and (is_html(lb) or "html" in L["ctype"].lower() or not lb.strip())):
            row["llms_txt"] = "no"
        elif dom in f2["llms_txt"]:
            e = f2["llms_txt"][dom]; row["llms_txt"] = e["llms_txt"]; row["llms_txt_generator"] = e.get("generator", ""); row["llms_txt_bytes"] = e.get("approx_bytes", "")
        else: row["llms_txt"] = "not_readable"
        row["llms_txt_source"] = "" if row["llms_txt"] == "not_readable" else ("second_fetch" if (L["status"] not in (200, 404, 410) and dom in f2["llms_txt"]) else lsrc)
        # user-agent runs
        st = {k: [r[k]["status"] for r in s["runs"]] for k in ["browser"] + NAMES}
        by = {k: [r[k]["bytes"] for r in s["runs"]] for k in st}
        row["browser_style_request"] = outcome(st["browser"])
        base_bytes = statistics.median([b for b, c in zip(by["browser"], st["browser"]) if c == 200] or [0])
        for k in NAMES:
            o = outcome(st[k])
            if o == "served" and base_bytes > 8000 and statistics.median(by[k]) < 0.3 * base_bytes: o = "served_small_page"
            row["request_as_" + k] = o
            row["refused_runs_" + k] = sum(x != 200 for x in st[k])
        row["run_statuses_browser_gptbot_claudebot_perplexitybot_googlebot_bingbot"] = " ".join("/".join(str(x) for x in st[k]) for k in ["browser"] + NAMES)
        hs = [r["browser"] for r in s["runs"]]
        row["server_header"] = next((h["server"] for h in hs if h.get("server")), "") or "none"
        row["cloudflare"] = "yes" if any(h.get("cf_ray") for r in s["runs"] for h in r.values()) else "no"
        snips = collections.Counter(r[k].get("snippet", "")[:90] for r in s["runs"] for k in NAMES + ["browser"] if r[k]["status"] != 200 and r[k].get("snippet"))
        row["refusal_page_text"] = snips.most_common(1)[0][0] if snips else ""
        rows.append(row)
    w = csv.DictWriter(open(sys.argv[4], "w", newline="", encoding="utf-8"), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump({"extra": extra, "runs_meta": d.get("runs_meta"), "started_utc": d.get("started_utc"), "ended_utc": d.get("ended_utc")}, open(sys.argv[5], "w"), indent=1)
    print(len(rows), "rows")
main()
