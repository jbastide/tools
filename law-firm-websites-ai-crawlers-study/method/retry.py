"""Retry sites the first pass couldn't read, using curl. Usage: python3 -I retry.py <fetch.json> <raw_dir>"""
import json, subprocess, sys, time, importlib.util, os
spec = importlib.util.spec_from_file_location("fetch", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch.py"))
fetch = importlib.util.module_from_spec(spec); spec.loader.exec_module(fetch)

def cget(url, ua, body_path=None):
    hp = body_path or "/dev/null"
    r = subprocess.run(["curl", "-s", "-L", "-m", "25", "--compressed", "-A", ua, "-H", "Accept-Language: en-US,en;q=0.9",
                        "-H", "Accept: text/html,text/plain,*/*", "-o", hp, "-D", "-",
                        "-w", "\n@@%{http_code} %{url_effective} %{size_download}", url], capture_output=True, text=True, errors="replace")
    head, _, tail = r.stdout.rpartition("\n@@")
    parts = tail.split(" ")
    hdr = {}
    for line in head.split("\r\n\r\n")[-2 if head.endswith("\r\n\r\n") else -1].splitlines():
        if ":" in line:
            k, v = line.split(":", 1); hdr[k.strip().lower()] = v.strip()
    return {"status": int(parts[0]) if parts[0].isdigit() else 0, "final_url": parts[1] if len(parts) > 1 else url,
            "ctype": hdr.get("content-type", ""), "server": hdr.get("server", ""), "cf_ray": "cf-ray" in hdr,
            "bytes": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0}

d = json.load(open(sys.argv[1])); raw = sys.argv[2]
n = 0
for s in d["sites"]:
    if "curl" in s: continue
    if s["home"]["browser"]["status"] == 200 and s["robots.txt"]["status"] in (200, 404): continue
    dom = s["domain"]
    home = cget("https://" + dom + "/", fetch.UAS["browser"])
    if home["status"] == 0: home = cget("https://www." + dom + "/", fetch.UAS["browser"])
    b = home["final_url"].split("/", 3); base = b[0] + "//" + b[2] if len(b) > 2 else "https://" + dom
    new = {"domain": dom, "firm": s["firm"], "base": base, "client": "curl", "home": {"browser": home}}
    for name in ("robots.txt", "llms.txt"):
        time.sleep(0.5); new[name] = cget(base + "/" + name, fetch.UAS["browser"], f"{raw}/{dom}.{name}.curl")
    for k in ("gptbot", "claudebot", "perplexitybot"):
        time.sleep(0.5); new["home"][k] = cget(base + "/", fetch.UAS[k])
    s["first_pass"] = {"home": s["home"], "robots.txt": s["robots.txt"], "llms.txt": s["llms.txt"]}
    better = (new["home"]["browser"]["status"] == 200) or (new["robots.txt"]["status"] == 200 and s["robots.txt"]["status"] != 200)
    print(dom, "urllib", s["home"]["browser"]["status"], s["robots.txt"]["status"], "| curl", new["home"]["browser"]["status"], new["robots.txt"]["status"], new["llms.txt"]["status"],
          [new["home"][k]["status"] for k in ("gptbot", "claudebot", "perplexitybot")], "USE" if better else "")
    s["curl"] = new
    if better:
        for k in ("base", "client", "home", "robots.txt", "llms.txt"): s[k] = new[k]
        for name in ("robots.txt", "llms.txt"):
            if os.path.exists(f"{raw}/{dom}.{name}.curl"): os.replace(f"{raw}/{dom}.{name}.curl", f"{raw}/{dom}.{name}")
        n += 1
json.dump(d, open(sys.argv[1], "w"), indent=1); print(n, "replaced")
