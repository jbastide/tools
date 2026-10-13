"""Fetch robots.txt, llms.txt and the homepage (4 user agents) for each firm site.
Usage: python3 -I fetch.py <firms.csv> <raw_dir> <out.json>"""
import csv, json, ssl, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

UAS = {
    "browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "gptbot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.3; +https://openai.com/gptbot)",
    "claudebot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "perplexitybot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
}
CTX = ssl.create_default_context()

def get(url, ua, limit=400_000):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,text/plain,*/*", "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            body = r.read(limit)
            return {"status": r.status, "final_url": r.geturl(), "ctype": r.headers.get("Content-Type", ""),
                    "server": r.headers.get("Server", ""), "cf_ray": bool(r.headers.get("CF-RAY")), "body": body}
    except urllib.error.HTTPError as e:
        body = b""
        try: body = e.read(limit)
        except Exception: pass
        return {"status": e.code, "final_url": url, "ctype": e.headers.get("Content-Type", ""),
                "server": e.headers.get("Server", ""), "cf_ray": bool(e.headers.get("CF-RAY")), "body": body}
    except Exception as e:
        return {"status": 0, "error": type(e).__name__ + ": " + str(e)[:120], "final_url": url, "ctype": "", "server": "", "cf_ray": False, "body": b""}

def one(row, raw_dir):
    d = row["website"].strip().lower()
    out = {"domain": d, "firm": row["firm"]}
    home = get("https://" + d + "/", UAS["browser"])
    if home["status"] == 0:
        home = get("https://www." + d + "/", UAS["browser"])
    base = home["final_url"].split("/", 3)
    base = base[0] + "//" + base[2] if len(base) > 2 else "https://" + d
    out["base"] = base
    out["home"] = {k: {kk: vv for kk, vv in home.items() if kk != "body"} | {"bytes": len(home["body"])} for k in ["browser"]}
    for name in ("robots.txt", "llms.txt"):
        time.sleep(0.5)
        r = get(base + "/" + name, UAS["browser"])
        open(f"{raw_dir}/{d}.{name}", "wb").write(r["body"])
        out[name] = {kk: vv for kk, vv in r.items() if kk != "body"} | {"bytes": len(r["body"])}
    for k in ("gptbot", "claudebot", "perplexitybot"):
        time.sleep(0.5)
        r = get(base + "/", UAS[k])
        out["home"][k] = {kk: vv for kk, vv in r.items() if kk != "body"} | {"bytes": len(r["body"])}
    return out

if __name__ == "__main__":
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(lambda r: one(r, sys.argv[2]), rows))
    json.dump({"fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "sites": res}, open(sys.argv[3], "w"), indent=1)
    print(len(res), "sites")
