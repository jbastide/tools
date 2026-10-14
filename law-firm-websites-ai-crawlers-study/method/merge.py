"""Assemble data.csv: files from the October 13 pass, server-test runs from October 14 (Sweden), and the three
Chicago runs from October 13 as chicago_* columns.
Usage: python3 -I merge.py <oct13.json> <oct14.json> <raw_dir> <wayback.json> <fetch2.json> <work_dir> <out data.csv>"""
import copy, csv, json, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
o13, o14, raw, wb, f2, work, out = sys.argv[1:8]
A = json.load(open(o13)); B = {s["domain"]: s for s in json.load(open(o14))["sites"]}
main = copy.deepcopy(A); main["runs_meta"] = json.load(open(o14))["runs_meta"]
chi = copy.deepcopy(A); chi["runs_meta"] = A["runs_meta"][2:5]
for s, c in zip(main["sites"], chi["sites"]):
    s["runs"] = B[s["domain"]]["runs"]; c["runs"] = c["runs"][2:5]
json.dump(main, open(f"{work}/main.json", "w")); json.dump(chi, open(f"{work}/chicago.json", "w"))
for name in ("main", "chicago"):
    subprocess.run(["python3", "-I", f"{here}/analyze_us.py", f"{work}/{name}.json", raw, wb, f"{work}/{name}.csv", f"{work}/{name}_meta.json", f2], check=True)
M = list(csv.DictReader(open(f"{work}/main.csv", encoding="utf-8"))); C = {r["website"]: r for r in csv.DictReader(open(f"{work}/chicago.csv", encoding="utf-8"))}
keys = ["browser_style_request"] + [f"request_as_{k}" for k in ("gptbot", "claudebot", "perplexitybot", "googlebot", "bingbot")] + ["run_statuses_browser_gptbot_claudebot_perplexitybot_googlebot_bingbot"]
for r in M:
    for k in keys: r["chicago_" + k] = C[r["website"]][k]
w = csv.DictWriter(open(out, "w", newline="", encoding="utf-8"), fieldnames=list(M[0].keys())); w.writeheader(); w.writerows(M)
print(len(M), "rows ->", out, "| main runs:", len(main["runs_meta"]), "| chicago runs:", len(chi["runs_meta"]))
