"""Compute every number the page uses from data.csv. Usage: python3 -I stats.py <data.csv>  (prints JSON)"""
import collections, csv, json, statistics, sys

AI3 = ["gptbot", "claudebot", "perplexitybot"]; CTRL = ["googlebot", "bingbot"]
ROBOT_COLS = [("GPTBot", "robots_gptbot"), ("OAI-SearchBot", "robots_oai_searchbot"), ("ChatGPT-User", "robots_chatgpt_user"),
              ("ClaudeBot", "robots_claudebot"), ("Claude-SearchBot", "robots_claude_searchbot"), ("Claude-User", "robots_claude_user"),
              ("PerplexityBot", "robots_perplexitybot"), ("Google-Extended", "robots_google_extended"), ("CCBot", "robots_ccbot")]

def compute(path):
    R = list(csv.DictReader(open(path, encoding="utf-8"))); C = collections.Counter; S = {"n": len(R)}
    ref = lambda r, k: r["request_as_" + k].startswith("refused")
    # robots.txt
    src = C("archived" if r["robots_txt_source"].startswith("archived") else r["robots_txt_source"] for r in R)
    S["robots_live"], S["robots_second"], S["robots_archived"] = src["live"], src["second_fetch"], src["archived"]
    S["robots_us_exit"] = src["us_exit"]; S["robots_same_day"] = src["live"] + src["second_fetch"] + src["us_exit"]
    S["robots_other"] = {k: v for k, v in src.items() if k not in ("live", "second_fetch", "us_exit", "archived")}
    dates = sorted(r["robots_txt_source"][9:] for r in R if r["robots_txt_source"].startswith("archived"))
    S["archive_first"], S["archive_last"] = (dates[0], dates[-1]) if dates else ("", "")
    named = [r for r in R if r["robots_names_ai_crawlers"] not in ("", "0")]
    S["robots_named_any"] = len(named); S["robots_no_mention"] = len(R) - len(named)
    dis = [r for r in R if r["robots_ai_crawlers_disallowed"]]
    S["robots_disallow_any"] = len(dis); S["robots_named_not_disallowing"] = len(named) - len(dis)
    S["robots_disallow_gpt_and_claude"] = sum(r["robots_gptbot"] == "disallowed" and r["robots_claudebot"] == "disallowed" for r in R)
    S["robots_archived_naming_ai"] = sum(r["robots_txt_source"].startswith("archived") for r in named)
    S["robots_table"] = [{"name": n, "named": sum(r[c] in ("named_allowed", "disallowed") for r in R), "disallowed": sum(r[c] == "disallowed" for r in R)} for n, c in ROBOT_COLS]
    S["robots_wildcard_block"] = sum("disallowed_all_bots" in (r["robots_gptbot"], r["robots_claudebot"]) for r in R)
    S["disallow_lists"] = sorted(([r["website"], r["robots_ai_crawlers_disallowed"].split(";")] for r in dis), key=lambda x: -len(x[1]))
    sig = C(r["robots_content_signal"] for r in R if r["robots_content_signal"])
    S["signal_total"] = sum(sig.values()); S["signal_train_yes"] = sum(v for k, v in sig.items() if "ai-train=yes" in k); S["signal_train_no"] = sum(v for k, v in sig.items() if "ai-train=no" in k)
    S["signals"] = dict(sig)
    # server test
    base = C(r["browser_style_request"] for r in R); sv = [r for r in R if r["browser_style_request"] == "served"]
    S["base_served"] = len(sv); S["base_refused"] = sum(v for k, v in base.items() if k.startswith("refused")); S["base_other"] = {k: v for k, v in base.items() if k != "served" and not k.startswith("refused")}
    S["base_left_out"] = len(R) - len(sv)
    S["names"] = {}
    for k in AI3 + CTRL:
        c = C("refused" if ref(r, k) else ("served" if r["request_as_" + k] == "served" else "mixed" if r["request_as_" + k] == "mixed" else r["request_as_" + k]) for r in sv)
        S["names"][k] = dict(c)
    S["served_all_five_names"] = sum(all(r["request_as_" + k] == "served" for k in AI3 + CTRL) for r in sv)
    S["served_all_ai"] = sum(all(r["request_as_" + k] == "served" for k in AI3) for r in sv)
    refusers = [r for r in sv if any(ref(r, k) for k in AI3)]
    S["ai_refusers"] = len(refusers); S["ai_refusers_sites"] = [r["website"] for r in refusers]
    S["ai_mixed_only"] = sum(1 for r in sv if r not in refusers and any(r["request_as_" + k] == "mixed" for k in AI3))
    S["ctrl_both_served"] = sum(all(r["request_as_" + k] == "served" for k in CTRL) for r in refusers)
    S["ctrl_any_refused"] = sum(any(ref(r, k) for k in CTRL) for r in refusers)
    S["ctrl_google_refused"] = sum(ref(r, "googlebot") for r in refusers)
    S["ctrl_unclear"] = len(refusers) - S["ctrl_both_served"] - S["ctrl_any_refused"]
    S["ai_only_refusers"] = S["ctrl_both_served"]
    S["ctrl_only_refusers"] = sum(1 for r in sv if r not in refusers and any(ref(r, k) for k in CTRL))
    S["bing_only_refusers"] = sum(1 for r in sv if not any(ref(r, k) for k in AI3 + ["googlebot"]) and ref(r, "bingbot"))
    S["refused_all_three_ai"] = sum(all(ref(r, k) for k in AI3) for r in refusers)
    S["refuser_codes"] = dict(C("+".join(sorted({r["request_as_" + k].replace("refused_", "") for k in AI3 if ref(r, k)})) for r in refusers))
    S["refusers_cloudflare"] = sum(r["cloudflare"] == "yes" for r in refusers)
    col = {"gptbot": "robots_gptbot", "claudebot": "robots_claudebot", "perplexitybot": "robots_perplexitybot"}
    S["refusers_robots_match"] = sum(any(ref(r, k) and r[col[k]] == "disallowed" for k in AI3) for r in refusers)
    S["refusers_no_robots_rule"] = len(refusers) - S["refusers_robots_match"]
    S["refusers_named_allowed"] = sum(any(ref(r, k) and r[col[k]] == "named_allowed" for k in AI3) and not any(ref(r, k) and r[col[k]] == "disallowed" for k in AI3) for r in refusers)
    S["refusers_no_ai_rule_at_all"] = sum(r["robots_names_ai_crawlers"] in ("", "0") for r in refusers)
    S["robots_disallow_but_served"] = sum(any(r[col[k]] == "disallowed" and r["request_as_" + k] == "served" for k in AI3) for r in sv)
    S["claude_disallowed_but_served"] = sum(r["robots_claudebot"] == "disallowed" and r["request_as_claudebot"] == "served" for r in sv)
    br = [r for r in R if r["browser_style_request"].startswith("refused")]
    S["br_served_gptbot"] = sum(r["request_as_gptbot"] == "served" for r in br)
    S["br_served_all_ai"] = sum(all(r["request_as_" + k] == "served" for k in AI3) for r in br)
    S["br_served_gptbot_only"] = sum(r["request_as_gptbot"] == "served" and not any(r["request_as_" + k] == "served" for k in ["claudebot", "perplexitybot"]) for r in br)
    S["br_served_googlebot"] = sum(r["request_as_googlebot"] == "served" for r in br)
    S["br_served_none"] = sum(not any(r["request_as_" + k] == "served" for k in AI3 + CTRL) for r in br)
    S["br_patterns"] = [[" ".join(k), v] for k, v in C(tuple(r["request_as_" + k][:7] for k in AI3 + CTRL) for r in br).most_common()]
    S["sv_patterns"] = [[" ".join(k), v] for k, v in C(tuple(r["request_as_" + k][:7] for k in AI3 + CTRL) for r in sv).most_common()]
    # llms.txt
    L = C(r["llms_txt"] for r in R); S["llms_yes"], S["llms_robots_syntax"], S["llms_no"], S["llms_unreadable"] = L["yes"], L["robots_syntax"], L["no"], L["not_readable"]
    S["llms_answered"] = L["yes"] + L["robots_syntax"] + L["no"]; S["llms_second"] = sum(r.get("llms_txt_source") == "second_fetch" for r in R); S["llms_us_exit"] = sum(r.get("llms_txt_source") == "us_exit" for r in R)
    gen = C(r["llms_txt_generator"] for r in R if r["llms_txt"] == "yes"); S["llms_generators"] = dict(gen); S["llms_gen_stated"] = L["yes"] - gen["not stated"]
    sizes = sorted(int(r["llms_txt_bytes"]) for r in R if r["llms_txt"] == "yes" and r.get("llms_txt_source") in ("live", "us_exit") and r["llms_txt_bytes"])
    S["llms_sizes_n"] = len(sizes); S["llms_size_median"] = statistics.median(sizes) if sizes else 0; S["llms_size_min"] = sizes[0] if sizes else 0
    S["llms_over_50k"] = sum(int(r["llms_txt_bytes"]) > 50000 for r in R if r["llms_txt"] == "yes" and r["llms_txt_bytes"])
    S["llms_max"] = max([int(r["llms_txt_bytes"]) for r in R if r["llms_txt"] == "yes" and r["llms_txt_bytes"]] or [0])
    return S

if __name__ == "__main__":
    print(json.dumps(compute(sys.argv[1]), indent=1))
