"""Full collection pass: robots.txt, llms.txt, then repeated homepage requests under six user agents.
Usage: python3 -I collect.py <firms.csv> <raw_dir> <tmp_dir> <out.json> [runs=5] [gap_seconds=180]"""
import csv, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

UAS = {
    "browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "gptbot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.4; +https://openai.com/gptbot",
    "claudebot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "perplexitybot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
}
ORDERS = [
    ["browser", "gptbot", "claudebot", "perplexitybot", "googlebot", "bingbot"],
    ["googlebot", "perplexitybot", "browser", "bingbot", "claudebot", "gptbot"],
    ["claudebot", "bingbot", "gptbot", "browser", "googlebot", "perplexitybot"],
    ["bingbot", "googlebot", "perplexitybot", "claudebot", "gptbot", "browser"],
    ["perplexitybot", "browser", "googlebot", "gptbot", "bingbot", "claudebot"],
    ["gptbot", "claudebot", "bingbot", "googlebot", "browser", "perplexitybot"],
]

def cget(url, ua, body_path):
    r = subprocess.run(["curl", "-s", "-L", "-m", "30", "--compressed", "-A", ua, "-H", "Accept-Language: en-US,en;q=0.9",
                        "-H", "Accept: text/html,text/plain,*/*", "-o", body_path, "-D", "-",
                        "-w", "\n@@%{http_code} %{size_download} %{url_effective}", url], capture_output=True, text=True, errors="replace")
    head, _, tail = r.stdout.rpartition("\n@@")
    p = tail.split(" ")
    blocks = [b for b in head.replace("\r\n", "\n").split("\n\n") if b.strip()]
    hdr = {}
    for line in (blocks[-1] if blocks else "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1); hdr[k.strip().lower()] = v.strip()
    return {"status": int(p[0]) if p and p[0].isdigit() else 0, "bytes": int(p[1]) if len(p) > 1 and p[1].isdigit() else 0,
            "final_url": p[2] if len(p) > 2 else url, "ctype": hdr.get("content-type", ""), "server": hdr.get("server", ""),
            "cf_ray": "cf-ray" in hdr, "cf_mitigated": hdr.get("cf-mitigated", "")}

def snippet(path):
    try: t = open(path, "rb").read(60000).decode("utf-8", "replace")
    except OSError: return ""
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S | re.I); t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:240]

def files(row, raw, tmp):
    d = row["website"].strip().lower(); out = {"domain": d, "firm": row["firm"]}
    tp = f"{tmp}/{d}.tmp"
    home = cget("https://" + d + "/", UAS["browser"], tp)
    if home["status"] == 0: home = cget("https://www." + d + "/", UAS["browser"], tp)
    b = home["final_url"].split("/", 3); out["base"] = b[0] + "//" + b[2] if len(b) > 2 and b[2] else "https://" + d
    for name in ("robots.txt", "llms.txt"):
        time.sleep(1.0); out[name] = cget(out["base"] + "/" + name, UAS["browser"], f"{raw}/{d}.{name}")
    return out

def one_run(site, order, tmp):
    res = {}
    for k in order:
        tp = f"{tmp}/{site['domain']}.{k}.html"
        r = cget(site["base"] + "/", UAS[k], tp)
        if r["status"] != 200 or r["bytes"] < 6000: r["snippet"] = snippet(tp)
        res[k] = r; time.sleep(1.5)
    return res

if __name__ == "__main__":
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8"))); raw, tmp, outp = sys.argv[2], sys.argv[3], sys.argv[4]
    nruns = int(sys.argv[5]) if len(sys.argv) > 5 else 5; gap = int(sys.argv[6]) if len(sys.argv) > 6 else 180
    stamp = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = {"started_utc": stamp(), "user_agents": UAS, "runs_meta": []}
    with ThreadPoolExecutor(10) as ex: sites = list(ex.map(lambda r: files(r, raw, tmp), rows))
    for s in sites: s["runs"] = []
    out["sites"] = sites; json.dump(out, open(outp, "w"), indent=1); print("files done", stamp(), flush=True)
    def exit_ip():
        r = subprocess.run(["curl", "-s", "-m", "15", "https://ipinfo.io/json"], capture_output=True, text=True)
        try: j = json.loads(r.stdout); return {"ip": j.get("ip"), "city": j.get("city"), "country": j.get("country"), "org": j.get("org")}
        except Exception: return {"error": r.stdout[:80]}
    first = exit_ip(); out["exit_start"] = first; print("exit", first, flush=True)
    for i in range(nruns):
        time.sleep(gap if i else 20)
        before = exit_ip()
        if before.get("ip") != first.get("ip"):
            out["aborted"] = {"before_run": i + 1, "exit": before}; json.dump(out, open(outp, "w"), indent=1); print("ABORT: exit changed", before, flush=True); sys.exit(2)
        order = ORDERS[i % len(ORDERS)]; t0 = stamp()
        with ThreadPoolExecutor(10) as ex: res = list(ex.map(lambda s: one_run(s, order, tmp), sites))
        for s, r in zip(sites, res): s["runs"].append(r)
        after = exit_ip()
        out["runs_meta"].append({"run": i + 1, "order": order, "started_utc": t0, "ended_utc": stamp(), "exit_before": before, "exit_after": after})
        if after.get("ip") != first.get("ip"):
            json.dump(out, open(outp, "w"), indent=1); print("ABORT: exit changed during run", i + 1, after, flush=True); sys.exit(2)
        json.dump(out, open(outp, "w"), indent=1); print("run", i + 1, "done", stamp(), flush=True)
    out["ended_utc"] = stamp(); json.dump(out, open(outp, "w"), indent=1); print("all done", flush=True)
