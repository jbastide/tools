"""Checks before publishing. Usage: python3 -I check.py <en.html> <sv.html> <data.csv> <llms_raw_dir>"""
import collections, csv, hashlib, html, json, os, re, sys
from html.parser import HTMLParser
en, sv = open(sys.argv[1], encoding="utf-8").read(), open(sys.argv[2], encoding="utf-8").read()
R = list(csv.DictReader(open(sys.argv[3], encoding="utf-8"))); raw = sys.argv[4]; ok = True
def fail(msg):
    global ok; ok = False; print("FAIL", msg)
class P(HTMLParser):
    VOID = {"meta", "link", "br", "img", "hr", "input"}
    def __init__(s): super().__init__(); s.st = []; s.err = []; s.seq = []; s.skip = 0
    def handle_starttag(s, t, a):
        d = dict(a)
        if d.get("class") == "lang-switch": s.skip = 1
        elif t == "ul" and s.skip: s.skip += 1
        # the language switch and added <span lang="en"> around English quotations may differ between languages
        if not s.skip and not (t == "span" and d.get("lang") == "en"): s.seq.append((t, d.get("id"), d.get("class")))
        if t not in s.VOID: s.st.append(t)
    def handle_endtag(s, t):
        if t == "ul" and s.skip: s.skip -= 1
        if not s.st or s.st[-1] != t: s.err.append(t)
        else: s.st.pop()
pe, ps = P(), P(); pe.feed(en); ps.feed(sv)
for name, p in (("en", pe), ("sv", ps)):
    if p.err or p.st: fail(f"{name} unbalanced {p.err[:3]} {p.st}")
body = lambda p: [x for x in p.seq if x[0] not in ("meta", "link")]
if body(pe) != body(ps):
    for i, (a, b) in enumerate(zip(body(pe), body(ps))):
        if a != b: fail(f"tag sequence differs at {i}: {a} vs {b}"); break
    else: fail(f"tag count differs {len(body(pe))} vs {len(body(ps))}")
for name, s in (("en", en), ("sv", sv)):
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    faq = [g for g in ld["@graph"] if g["@type"] == "FAQPage"][0]["mainEntity"]
    sec = s[s.find('<section id="faq">'):s.find('<section id="sources">')]
    vis = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", sec, re.S)
    strip = lambda t: html.unescape(re.sub(r"<[^>]+>", "", t))
    if len(vis) != len(faq) or any(q["name"] != strip(a) or q["acceptedAnswer"]["text"] != strip(b) for q, (a, b) in zip(faq, vis)): fail(f"{name} FAQ JSON-LD differs from visible text")
    if re.search(r"\{[A-Za-z_]|None|\[\[", s.split("</head>")[1]): fail(f"{name} has a leftover placeholder")
def nums(s):
    t = html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", s, flags=re.S))
    t = re.sub(r"\(ungefär:.*?”\)", " ", t).replace(",", ".")  # Swedish glosses of English quotations
    return collections.Counter(re.findall(r"\d+(?:\.\d+)?", t))
ne, ns = nums(en), nums(sv)
if ne != ns: fail(f"numbers differ: only en {dict(ne - ns)} only sv {dict(ns - ne)}")
# claims written into the prose
rs = [r for r in R if r["llms_txt"] == "robots_syntax"]
h = collections.Counter()
for r in rs:
    p = f"{raw}/{r['website']}.llms.txt"
    if os.path.exists(p):
        b = open(p, "rb").read(); h[(len(b), hashlib.md5(b).hexdigest(), b"Disallow-Training" in b)] += 1
top = h.most_common(1)[0] if h else ((0, "", False), 0)
if not (top[0][0] == 65 and top[0][2] and top[1] == 6): fail(f"identical 65-byte llms claim: {h}")
sig = [r["website"] for r in R if "ai-train=yes" in r["robots_content_signal"]]
bodies = collections.Counter()
for d in sig:
    for suf in (".robots.txt", ".robots.txt.fetch2", ".robots.txt.usexit"):
        p = f"{raw}/{d}{suf}"
        if os.path.exists(p) and (suf != ".robots.txt" or [x for x in R if x["website"] == d][0]["robots_txt_source"] == "live"):
            bodies[re.sub(re.escape(d.split('.')[0]), "X", open(p, encoding="utf-8", errors="replace").read().strip())] += 1; break
if max(bodies.values() or [0]) != 3: fail(f"three identical Content-Signal files claim: {list(bodies.values())}")
dis = {r["website"]: set(r["robots_ai_crawlers_disallowed"].split(";")) for r in R if r["robots_ai_crawlers_disallowed"]}
want = [{"ClaudeBot", "anthropic-ai", "Google-Extended", "Applebot-Extended", "CCBot", "Bytespider", "meta-externalagent", "Amazonbot"}, {"GPTBot", "meta-externalagent"}]
for w in want:
    if w not in dis.values(): fail(f"disallow list claim {sorted(w)} not found")
br = [r for r in R if r["browser_style_request"].startswith("refused")]
kinds = collections.Counter("challenge" if "Just a moment" in r["refusal_page_text"] or "Attention Required" in r["refusal_page_text"] else "403" if "403" in r["refusal_page_text"] else "other" for r in br)
if kinds["challenge"] == 0 or kinds["403"] == 0 or kinds["other"] > len(br) / 2: fail(f"bot protection description: {dict(kinds)}")
print("refusal pages of baseline-refused sites:", dict(kinds))
print("ALL CHECKS PASSED" if ok else "CHECKS FAILED")
