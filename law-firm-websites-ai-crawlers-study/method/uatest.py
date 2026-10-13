"""Repeat the homepage user-agent test with curl. Usage: python3 -I uatest.py <fetch.json> <out.json> <order,comma,separated>"""
import json, subprocess, sys, time, os, importlib.util
from concurrent.futures import ThreadPoolExecutor
spec = importlib.util.spec_from_file_location("fetch", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch.py"))
fetch = importlib.util.module_from_spec(spec); spec.loader.exec_module(fetch)
order = sys.argv[3].split(",")

def cget(url, ua):
    r = subprocess.run(["curl", "-s", "-L", "-m", "25", "--compressed", "-A", ua, "-H", "Accept-Language: en-US,en;q=0.9",
                        "-H", "Accept: text/html,text/plain,*/*", "-o", "/dev/null",
                        "-w", "%{http_code} %{size_download} %{url_effective}", url], capture_output=True, text=True, errors="replace")
    p = r.stdout.split(" ")
    return {"status": int(p[0]) if p and p[0].isdigit() else 0, "bytes": int(p[1]) if len(p) > 1 and p[1].isdigit() else 0, "final_url": p[2] if len(p) > 2 else ""}

def one(s):
    out = {"domain": s["domain"]}
    for k in order:
        out[k] = cget(s["base"] + "/", fetch.UAS[k]); time.sleep(1.0)
    return out

d = json.load(open(sys.argv[1]))
with ThreadPoolExecutor(12) as ex: res = list(ex.map(one, d["sites"]))
json.dump({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "order": order, "sites": res}, open(sys.argv[2], "w"), indent=1)
print(sys.argv[2], len(res))
