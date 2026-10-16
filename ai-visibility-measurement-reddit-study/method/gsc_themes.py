"""Group the AI-coded GSC Generative AI report points into themes (keyword rules on the
coder's point label + quote) and count distinct threads per theme. Writes gsc_report_themes.csv."""
import json, os, re, csv, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v = json.load(open(os.path.join(ROOT, "raw", "verified_quotes.json")))["verified"]
g = [q for q in v if q["category"] == "GSC_REPORT"]
THEMES = [
    ("No clicks / CTR (impressions only)", r"no click|impressions only|without click|no clicks|missing click|clicks/ctr|want.*click|clicks, ctr|impressions with no|impressions without|impressions alone|half the story|abysmal|popup shown but no clicks|no queries, clicks"),
    ("No query / prompt data", r"no query|query data|queries|prompt|keyword|intent|what prompted|which exact|grounding"),
    ("Uneven rollout: missing, region-limited or disappeared", r"(?<!feature )rollout|rolled out|roll out(?! query)|not (yet )?available (for|in)|not appearing|not seeing|don.t have|disappeared|only for one|subset|\\buk\\b|some properties|low.impression|sufficient data|by site|data center|us first|40-50 days|netherlands|denmark|can.t wait for us"),
    ("Not actionable / vanity or directional only", r"actionable|vanity|useless|use case|what to do|what do i do|directional|hint|diagnostic|too basic|barely useful|not very helpful|noise|not enough|hasn.t changed|coverage signal|no value"),
    ("Can't connect to traffic, conversions or revenue", r"traffic or conversions|conversion|revenue|visit|roi|attribution|leads"),
    ("Ambiguous definitions: AIO+AI Mode combined, position as a block, what counts as an impression", r"combined|combines|ai mode as well|block|position|show more|impression.*cited|cited as a source|links vs mentions|citation link|filtered view|counted in the normal|lumped"),
    ("Data limits: history from 18 May, row cap, no API, logging anomaly", r"may 18|18th may|1,000-row|row cap|no api|anomaly|logging"),
    ("Bing Webmaster Tools does it better (grounding queries)", r"bing"),
    ("Praised: first separate view of AI visibility, page/country/device breakdown", r"^(praised|welcomed|useful|free and useful|claimed useful|historical|page-level|first real|drill-down|report shows|impressions, pages|tracking as a single|used as a source|mentioned as a source|reveals|no prompt insights, but|useful but)"),
]
th = collections.defaultdict(set); ex = collections.defaultdict(list)
for q in g:
    s = (q["point"] or "") + " || " + q["quote"]
    for name, rx in THEMES:
        if re.search(rx, q["point"] or "" if rx.startswith("^") else s, re.I):
            th[name].add(q["thread"]); ex[name].append(q)
with open(os.path.join(ROOT, "gsc_report_themes.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["theme", "threads", "thread_ids"])
    for name, _ in THEMES:
        w.writerow([name, len(th[name]), ";".join(sorted(th[name]))])
        print(len(th[name]), name)
print("threads with any GSC report point:", len({q["thread"] for q in g}))

import sys
if len(sys.argv) > 1:
    for name, _ in THEMES:
        print("\n##", name)
        for q in ex[name]:
            print(" ", q["thread"], "|", q["point"], "|", q["quote"][:110])
