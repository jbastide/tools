"""Resumable sweep of whole subreddits from Arctic Shift, 2025-01-01 to now.

Writes raw/posts_<sub>.jsonl (one post per line, deduped by id) and appends
progress to raw/sweep.log. Re-running resumes from the last created_utc.
"""
import json, os, sys, time, urllib.request, urllib.error, urllib.parse, datetime

BASE = "https://arctic-shift.photon-reddit.com/api/"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "raw")
START = 1735689600  # 2025-01-01 UTC
SUBS = sys.argv[1:] or ["GoogleSearchConsole", "TechSEO", "bigseo", "agency", "PPC",
                        "SEO", "DigitalMarketing", "marketing"]
FIELDS = "id,subreddit,created_utc,title,selftext,num_comments,score,link_flair_text,url"


def log(msg):
    line = f"{datetime.datetime.utcnow().isoformat()}Z {msg}"
    print(line, flush=True)
    with open(os.path.join(RAW, "sweep.log"), "a") as f:
        f.write(line + "\n")


def exit_ip():
    try:
        return urllib.request.urlopen("https://api.ipify.org", timeout=15).read().decode()
    except Exception as e:
        return f"unknown ({e})"


def get(path, params):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    for attempt in range(30):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "aeo-research/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 400:
                raise RuntimeError(f"400 on {url}: {e.read()[:300]!r}")
            reset = e.headers.get("x-ratelimit-reset")
            wait = int(reset) + 2 if reset and reset.isdigit() else 20
            log(f"HTTP {e.code} on {url}; sleeping {wait}s")
            time.sleep(wait)
        except Exception as e:
            log(f"error {e!r} on {url}; sleeping 20s")
            time.sleep(20)
    raise RuntimeError("gave up on " + url)


def sweep(sub):
    path = os.path.join(RAW, f"posts_{sub}.jsonl")
    seen, last = set(), START
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                p = json.loads(line)
                seen.add(p["id"])
                last = max(last, p["created_utc"])
    if os.path.exists(path + ".done"):
        log(f"{sub}: already done ({len(seen)} posts)")
        return
    log(f"{sub}: start/resume at {last} with {len(seen)} posts")
    after = max(START, last - 1)
    with open(path, "a") as out:
        while True:
            d = get("posts/search", {"subreddit": sub, "sort": "asc", "after": after,
                                     "limit": 100, "fields": FIELDS})
            data = d.get("data") or []
            new = [p for p in data if p["id"] not in seen]
            for p in new:
                seen.add(p["id"])
                out.write(json.dumps(p) + "\n")
            out.flush()
            if not data:
                break
            mx = max(p["created_utc"] for p in data)
            if not new and mx <= after + 1:
                after = mx  # step past a tie
                if len(data) < 100:
                    break
                continue
            if len(data) < 100 and not new:
                break
            after = mx - 1 if new else mx
            if len(data) < 100 and new:
                # one more request will return 0 or only seen ids and end the loop
                pass
            log(f"{sub}: {len(seen)} posts, at {datetime.datetime.utcfromtimestamp(mx).date()}")
            time.sleep(3)
    open(path + ".done", "w").write(str(time.time()))
    log(f"{sub}: DONE {len(seen)} posts")


if __name__ == "__main__":
    log(f"run start; exit IP {exit_ip()}")
    for s in SUBS:
        ip = exit_ip()
        log(f"before {s}: exit IP {ip}")
        sweep(s)
    log(f"run end; exit IP {exit_ip()}")
