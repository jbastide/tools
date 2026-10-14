"""Build ../index.html from the CSV files, so no number on the page is typed by hand.
The Swedish page at sv/haiku-sonnet-opus-researchstudie/ is a translation of this output: after a rebuild that
changes text or numbers, make the same change there by hand.

Usage: python3 build.py   (after analyze.py)
"""
import csv, html, json, os, statistics as st
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
rd = lambda *p: list(csv.DictReader(open(os.path.join(ROOT, *p), encoding="utf-8")))
RUNS, DATA, FACTS, SRC = rd("runs.csv"), rd("data.csv"), rd("facts.csv"), rd("sources.csv")
PILOT, PDATA = rd("pilot", "runs.csv"), rd("pilot", "data.csv")
CONTROL = json.load(open(os.path.join(HERE, "control.json")))
TIERS = ("haiku", "sonnet", "opus")
NAME = {"haiku": "Haiku 5.5", "sonnet": "Sonnet 5.5", "opus": "Opus 5.5"}
e = html.escape

def tier(rows, t):
    return [r for r in rows if r["run"].startswith(t)]
def nums(rows, k, f=float):
    return [f(r[k]) for r in rows]
def span(vals, money=False, dec=0):
    lo, hi = min(vals), max(vals)
    fmt = (lambda v: f"${v:.2f}") if money else (lambda v: f"{v:.{dec}f}")
    return fmt(lo) if lo == hi else f"{fmt(lo)} to {fmt(hi)}"
def listed(vals):
    v = [f"{x:.0f}" for x in vals]
    return ", ".join(v[:-1]) + " and " + v[-1]
def found(vals, total):
    """'19, 23 and 22 of 25', or 'all 25 each time' when every run found everything."""
    return f"all {total} each time" if min(vals) == max(vals) == total else f"{listed(vals)} of {total}"
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
def word(n, cap=False):
    w = WORDS[n] if 0 <= n < 10 else str(n)
    return w.capitalize() if cap else w
def cover(n, total):
    return f"all {total}" if n == total else f"{n} of {total}"
def pct(a, b):
    return f"{100 * a / b:.1f}%"
def usd(v):
    return f"${v:.2f}"

T = {}
for t in TIERS:
    rs = tier(RUNS, t)
    ds = [d for d in DATA if d["model"] == t]
    T[t] = dict(
        runs=rs, n=len(ds), claims=nums(rs, "claims"), pages=nums(rs, "pages_cited"),
        key=nums(rs, "key_facts_found"), extra=nums(rs, "extra_finds"),
        cost=nums(rs, "cost_est_usd"), mins=nums(rs, "minutes"), tools=nums(rs, "tool_calls"),
        search=nums(rs, "searches_run"), fees=nums(rs, "cost_search_fees_usd"),
        tokcost=[float(r["cost_input_side_usd"]) + float(r["cost_output_est_usd"]) for r in rs],
        peak=nums(rs, "peak_context_tokens"), over=nums(rs, "responses_over_100k"), resp=nums(rs, "model_responses"),
        leads=nums(rs, "leads"), nf=nums(rs, "not_found"),
        g1=sum(d["grader1"] != "OK" for d in ds), g2=sum(d["grader2"] != "OK" for d in ds),
        both=sum(d["grader1"] != "OK" and d["grader2"] != "OK" for d in ds),
        either=sum(d["grader1"] != "OK" or d["grader2"] != "OK" for d in ds),
        grp=Counter(d["source_group"] for d in ds),
        key_union=sum(1 for f in FACTS if f["list"] == "key" and int(f[t + "_runs"]) > 0),
        key_all=sum(1 for f in FACTS if f["list"] == "key" and int(f[t + "_runs"]) == 3),
        x_union=sum(1 for f in FACTS if f["list"] == "extra" and int(f[t + "_runs"]) > 0),
        x_all=sum(1 for f in FACTS if f["list"] == "extra" and int(f[t + "_runs"]) == 3),
    )
N = len(DATA)
VERB = sum(d["quote_grade"] == "verbatim" for d in DATA)
PN, PVERB = len(PDATA), sum(d["quote_grade"] == "verbatim" for d in PDATA)
KEYN = sum(f["list"] == "key" for f in FACTS)
XN = sum(f["list"] == "extra" for f in FACTS)
BOTH = sum(T[t]["both"] for t in TIERS)
EITHER = sum(T[t]["either"] for t in TIERS)
G1, G2 = sum(T[t]["g1"] for t in TIERS), sum(T[t]["g2"] for t in TIERS)
agree = N - (G1 - BOTH) - (G2 - BOTH)
po = agree / N
pe = (G1 / N) * (G2 / N) + (1 - G1 / N) * (1 - G2 / N)
KAPPA = (po - pe) / (1 - pe)
mean = lambda t, k: st.mean(T[t][k])
C = {t: mean(t, "cost") for t in TIERS}
PAGES = len(SRC)
ONE = sum(s["runs_citing"] == "1" for s in SRC)
NINE = sum(s["runs_citing"] == "9" for s in SRC)
DATE_RUNS = sorted({d["run"] for d in DATA if "X01" in d["extra_finds"].split()})
REDDIT_RUNS = sorted({d["run"] for d in DATA if d["host"] == "reddit.com"})
REDDIT_N = sum(d["host"] == "reddit.com" for d in DATA)
THREAD_RUNS = sorted({d["run"] for d in DATA if d["source_group"] == "Thread or post"})
BLOCKED = sum(int(r["searches_refused_site_blocked"]) for r in RUNS)
CAPREF = sum(int(r["searches_refused_by_cap"]) for r in RUNS)
PCAP = [r["run"] for r in PILOT if int(r["searches_refused_by_cap"]) > 0]
PSEARCH = sum(int(r["web_search_calls"]) if "web_search_calls" in r else 0 for r in PILOT)
TOTAL_COST = sum(float(r["cost_est_usd"]) for r in RUNS)
PILOT_COST = sum(float(r["cost_est_usd"]) for r in PILOT)
slow = max(RUNS, key=lambda r: float(r["minutes"]))
haiku_base = []      # Haiku token cost had every request been under 100,000 tokens
for r in T["haiku"]["runs"]:
    haiku_base.append((int(r["input_tokens"]) * 0.10 + int(r["cache_write_tokens"]) * 0.125
                       + int(r["cache_read_tokens"]) * 0.01 + int(r["visible_output_tokens_est"]) * 0.50) / 1e6)

def run_table():
    out = []
    for r in RUNS:
        t = r["run"].split("-")[0]
        out.append(f'<tr><th scope="row">{NAME[t]}, run {r["run"][-1]}</th><td class="n">{r["claims"]}</td>'
                   f'<td class="n">{r["pages_cited"]}</td><td class="n">{r["key_facts_found"]}</td>'
                   f'<td class="n">{r["extra_finds"]}</td><td class="n">{r["flagged_by_both"]}</td>'
                   f'<td class="n">{usd(float(r["cost_est_usd"]))}</td><td class="n">{float(r["minutes"]):.0f}</td></tr>')
    return "\n      ".join(out)

def fact_rows(which, only_partial=False):
    out = []
    for f in FACTS:
        if f["list"] != which:
            continue
        trip = (f["haiku_runs"], f["sonnet_runs"], f["opus_runs"])
        if only_partial and trip == ("3", "3", "3"):
            continue
        out.append(f'<tr><th scope="row">{e(f["fact"])}</th><td class="n">{trip[0]}</td><td class="n">{trip[1]}</td><td class="n">{trip[2]}</td></tr>')
    return "\n      ".join(out)

def grade_rows():
    out = []
    for t in TIERS:
        v = T[t]
        out.append(f'<tr><th scope="row">{NAME[t]}</th><td class="n">{v["n"]}</td><td class="n">{v["g1"]}</td>'
                   f'<td class="n">{v["g2"]}</td><td class="n">{v["both"]} ({pct(v["both"], v["n"])})</td></tr>')
    out.append(f'<tr><th scope="row">All nine runs</th><td class="n">{N}</td><td class="n">{G1}</td><td class="n">{G2}</td>'
               f'<td class="n">{BOTH} ({pct(BOTH, N)})</td></tr>')
    return "\n      ".join(out)

def cost_rows():
    out = []
    for t in TIERS:
        v = T[t]
        out.append(f'<tr><th scope="row">{NAME[t]}</th><td class="n">{mean(t, "tools"):.0f}</td><td class="n">{mean(t, "search"):.0f}</td>'
                   f'<td class="n">{mean(t, "peak") / 1000:.0f}K</td><td class="n">{usd(mean(t, "tokcost"))}</td>'
                   f'<td class="n">{usd(mean(t, "fees"))}</td><td class="n">{usd(C[t])}</td><td class="n">{span(v["mins"])}</td></tr>')
    return "\n      ".join(out)

def mix_rows():
    out = []
    for t in TIERS:
        g = T[t]["grp"]
        out.append(f'<tr><th scope="row">{NAME[t]}</th><td class="n">{g["Google"]}</td><td class="n">{g["Bar"]}</td>'
                   f'<td class="n">{g["Thread or post"]}</td><td class="n">{g["Trade press, blog or other"]}</td><td class="n">{T[t]["n"]}</td></tr>')
    return "\n      ".join(out)

def pilot_rows():
    out = []
    for t in TIERS:
        rs = tier(PILOT, t)
        out.append(f'<tr><th scope="row">{NAME[t]}</th><td class="n">{listed(nums(rs, "claims"))}</td>'
                   f'<td class="n">{listed(nums(rs, "key_facts_found"))}</td><td class="n">{listed(nums(T[t]["runs"], "key_facts_found"))}</td></tr>')
    return "\n      ".join(out)

def raw_links():
    return ", ".join(f'<a href="runs/{r["run"]}.json">{NAME[r["run"].split("-")[0]].split()[0]} {r["run"][-1]}</a>' for r in RUNS)

H, S, O = T["haiku"], T["sonnet"], T["opus"]
three_haiku = sum(H["cost"])
faq = [
 ("Can a cheap AI model do online research without making up quotes?",
  f"In this test, yes. Copy for Originals gave the same research brief to Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 three times each on October 13, 2026. All {N} quotes the nine runs returned were found word for word on the pages they cited, including all {H['n']} from Haiku, the cheapest model. The brief required a copied quote and a page address for every claim and said each quote would be checked by a script."),
 ("When is Claude Opus worth the cost as a research agent?",
  f"When the brief runs once and nothing may be missed. In the Copy for Originals test, every Opus 5.5 run found all {KEYN} known facts, Sonnet 5.5 runs found {span(S['key'])}, and Haiku 5.5 runs found {span(H['key'])}. Opus also cited about twice as many pages as Haiku and had the lowest share of claims that said more than their quote showed ({pct(O['both'], O['n'])}, against {pct(S['both'], S['n'])} for Sonnet and {pct(H['both'], H['n'])} for Haiku). An Opus run cost an estimated {usd(C['opus'])} at list prices, against {usd(C['haiku'])} for Haiku."),
 ("How do you stop an AI research agent from inventing sources?",
  f"Require evidence that a script can check. In the Copy for Originals test, each claim had to carry the page address and a passage copied character for character, and the brief said every quote would be machine-checked. A separate script then fetched each page and looked for the quote. It found {VERB} of {N}. A second check is still needed, because {BOTH} of the {N} claims ({pct(BOTH, N)}) said more than their quote showed."),
]
faq_ld = ",\n        ".join(
    '{"@type": "Question", "name": %s,\n         "acceptedAnswer": {"@type": "Answer", "text": %s}}' % (json.dumps(q, ensure_ascii=False), json.dumps(a, ensure_ascii=False))
    for q, a in faq)
faq_html = "\n".join(f"  <h3>{e(q)}</h3>\n  <p>{e(a)}</p>" for q, a in faq)

URL = "https://tools.copyfororiginals.com/haiku-vs-sonnet-vs-opus-research-study/"
DESC = (f"Copy for Originals gave one online research brief to Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5, three runs each, on October 13, 2026. "
        f"All {N} quotes were on the cited pages word for word. Haiku found {span(H['key'])} of {KEYN} known facts for about {usd(C['haiku'])} a run; "
        f"Opus found all {KEYN} every time for about {usd(C['opus'])}. Data and scripts included.")

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Haiku vs Sonnet vs Opus for Online Research: 9 Runs, {N} Quotes Checked (2026 Study)</title>
<meta name="description" content="{e(DESC)}">
<meta name="author" content="Copy for Originals">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="index,follow,max-snippet:-1">
<link rel="canonical" href="{URL}">
<link rel="alternate" hreflang="sv" href="https://tools.copyfororiginals.com/sv/haiku-sonnet-opus-researchstudie/">
<link rel="alternate" hreflang="en" href="{URL}">
<link rel="alternate" hreflang="x-default" href="{URL}">
<meta property="og:type" content="article">
<meta property="og:url" content="{URL}">
<meta property="og:site_name" content="Copy for Originals">
<meta property="og:title" content="Haiku, Sonnet or Opus for online research? One brief, nine runs, {N} checked quotes">
<meta property="og:description" content="{VERB} of {N} quotes were on the cited page. Haiku found {span(H['key'])} of {KEYN} known facts, Opus all {KEYN}. An Opus run cost about {C['opus'] / C['haiku']:.0f} times a Haiku run.">
<meta property="article:published_time" content="2026-10-13">
<meta property="article:modified_time" content="2026-10-13">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%94%8E%3C/text%3E%3C/svg%3E">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Organization",
      "@id": "https://copyfororiginals.com/#org",
      "name": "Copy for Originals",
      "url": "https://copyfororiginals.com"
    }},
    {{
      "@type": "Article",
      "@id": "{URL}#article",
      "headline": "Haiku, Sonnet or Opus for online research? One brief, nine runs, {N} checked quotes",
      "description": {json.dumps(DESC, ensure_ascii=False)},
      "url": "{URL}",
      "inLanguage": "en",
      "datePublished": "2026-10-13",
      "dateModified": "2026-10-13",
      "author": {{"@id": "https://copyfororiginals.com/#org"}},
      "publisher": {{"@id": "https://copyfororiginals.com/#org"}},
      "about": ["AI research agents", "Claude Haiku 5.5", "Claude Sonnet 5.5", "Claude Opus 5.5", "Open-source intelligence", "Content marketing"],
      "isBasedOn": {{"@id": "{URL}#data"}},
      "breadcrumb": {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{"@type": "ListItem", "position": 1, "name": "Tools", "item": "https://tools.copyfororiginals.com/"}},
          {{"@type": "ListItem", "position": 2, "name": "Haiku vs Sonnet vs Opus research study", "item": "{URL}"}}
        ]
      }}
    }},
    {{
      "@type": "Dataset",
      "@id": "{URL}#data",
      "name": "Nine AI research runs on one brief: {N} claims with checked quotes (Copy for Originals, 2026)",
      "description": "One row per claim returned by nine research runs (three each on Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5) on October 13, 2026: the claim, the quote, the page cited, whether a script found the quote on that page, which of {KEYN} known facts and {XN} further findings it covers, and two blind grades of whether the quote supports the claim. Per-run token use, tool calls, estimated cost and time are in runs.csv.",
      "creator": {{"@id": "https://copyfororiginals.com/#org"}},
      "datePublished": "2026-10-13",
      "license": "https://creativecommons.org/licenses/by/4.0/",
      "distribution": {{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "{URL}data.csv"}}
    }},
    {{
      "@type": "FAQPage",
      "@id": "{URL}#faq",
      "mainEntity": [
        {faq_ld}
      ]
    }}
  ]
}}
</script>
<link rel="stylesheet" href="../site.css">
<style>
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:28px 0 0}}
.stat{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px}}
.stat b{{display:block;font:700 clamp(30px,6vw,40px)/1 var(--display);letter-spacing:-.03em;font-variant-numeric:tabular-nums;margin-bottom:6px}}
.stat span{{font-size:14.5px;color:var(--muted);line-height:1.4}}
</style>
</head>
<body>
<nav class="site-nav" aria-label="Copy for Originals">
  <a class="site-nav-brand" href="https://www.copyfororiginals.com/">Copy for Originals</a>
  <ul>
    <li><a href="https://www.copyfororiginals.com/">Home</a></li>
    <li><a href="https://www.copyfororiginals.com/thoughts">Thoughts</a></li>
    <li><a href="https://www.copyfororiginals.com/digital-marketing-services">Services</a></li>
    <li><a href="https://tools.copyfororiginals.com/" aria-current="true">Tools</a></li>
    <li><a href="https://www.copyfororiginals.com/about">About</a></li>
    <li><a href="https://www.copyfororiginals.com/faqs">FAQs</a></li>
    <li><a href="https://www.copyfororiginals.com/contact">Contact</a></li>
  </ul>
  <ul class="lang-switch" aria-label="Language"><li><a href="../sv/haiku-sonnet-opus-researchstudie/" hreflang="sv" lang="sv">Svenska</a></li><li><span aria-current="true">English</span></li></ul>
</nav>
<div class="wrap">

<nav class="crumbs" aria-label="Breadcrumb"><a href="../">&larr; All tools</a></nav>

<header>
  <p class="kicker"><a href="https://copyfororiginals.com/">Copy for Originals</a> · Original research</p>
  <h1>Haiku, Sonnet or Opus for online research? One brief, nine runs, {N} checked quotes</h1>
  <p class="lede">A marketing team that wants original research can now send an AI model out to read the web for about a quarter, or for about three dollars. We wanted to know what the extra money buys. So we wrote one research brief, gave it to three Claude models three times each, and had a script open every page they cited and look for every sentence they quoted. None of the {N} quotes was made up. The gaps were elsewhere: in what the cheap model never found, in claims that said a little more than their quotes, and in one website that shut all three models out.</p>
  <p class="byline">By <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a> · Published <time datetime="2026-10-13">October 13, 2026</time> · <a href="data.csv">Download the {N} claims (CSV)</a></p>
  <p class="scope"><b>Educational only, not legal advice.</b> The research topic was Google’s recording of calls to law firms. This page reports how three AI models researched it. It does not say what a firm should do.</p>
  <div class="stats">
    <div class="stat"><b>{VERB} of {N}</b><span>quotes found word for word on the page cited, across all three models</span></div>
    <div class="stat"><b>{KEYN} of {KEYN}</b><span>known facts found by every Opus run. Sonnet runs found {span(S['key'])}, Haiku runs {span(H['key'])}</span></div>
    <div class="stat"><b>{usd(C['haiku'])} → {usd(C['opus'])}</b><span>estimated cost of one run, Haiku to Opus, at list prices</span></div>
  </div>
</header>

<section id="findings">
  <h2>What did the study find?</h2>
  <ol class="check">
    <li><b>No model made up a quote.</b> A script fetched every cited page and looked for the quote. It found {VERB} of {N}. The brief warned each model that its quotes would be checked by machine, and every run reported checking its own work first.</li>
    <li><b>The cheapest model found most of the known facts, but different ones each time.</b> Haiku runs found {found(H['key'], KEYN)}. Only {H['key_all']} facts turned up in all three Haiku runs, though the three together covered {cover(H['key_union'], KEYN)}. Sonnet runs found {listed(S['key'])}. Opus runs found {found(O['key'], KEYN)}.</li>
    <li><b>The extra money bought breadth.</b> An Opus run returned about {mean('opus', 'claims'):.0f} claims from {span(O['pages'])} pages. A Sonnet run returned about {mean('sonnet', 'claims'):.0f} from {span(S['pages'])}, and a Haiku run about {mean('haiku', 'claims'):.0f} from {span(H['pages'])}.</li>
    <li><b>A real quote is not always enough.</b> Two blind graders both flagged {BOTH} of {N} claims as saying more than their quote showed: {pct(H['both'], H['n'])} of Haiku’s, {pct(S['both'], S['n'])} of Sonnet’s and {pct(O['both'], O['n'])} of Opus’s.</li>
    <li><b>A blocked website stopped every model.</b> Reddit refused the search tool in all nine runs. One Opus run found a side door and spent {float(slow['minutes']):.0f} minutes at it. No run invented a thread.</li>
    <li><b>An Opus run cost about {C['opus'] / C['haiku']:.0f} times a Haiku run.</b> Estimated at list prices: {usd(C['haiku'])} for Haiku, {usd(C['sonnet'])} for Sonnet, {usd(C['opus'])} for Opus. Search fees were about half of Haiku’s cost.</li>
    <li><b>The setup mattered as much as the model.</b> Our first attempt failed twice in ways no model caused: nine runs shared one cap of 200 searches, and three of them saved files on top of each other.</li>
  </ol>
</section>

<section id="brief">
  <h2>What was the assignment?</h2>
  <p>We picked a question we already knew the answer to. Earlier the same day we had published <a href="../does-google-record-calls-to-law-firms/">a guide to whether Google records calls to law firms from its ads</a>, with every quotation checked against its source. That gave us {KEYN} facts a good researcher ought to come back with.</p>
  <p>The brief asked ten questions. Does Google record calls from Local Services Ads? From Google Ads? What does the caller hear? How long are recordings kept? Who can listen? Can a firm switch it off? What have state bars said? What do lawyers say about it in public threads?</p>
  <p>It also set rules, and they are the heart of the test. One fact per claim. Every claim carries the address of the page and a passage copied from it character for character, 300 characters at most, with no ellipses and no stitching. Anything the model could not quote exactly goes in a separate list of leads. Anything it looked for and could not find goes in another list. And one sentence we suspected would matter: <i>“Every quote will be machine-checked against the page at that URL.”</i></p>
  <p>Each model got the brief three times, as nine separate agents with a search tool, a page-fetching tool and a command line. The three models were Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5, the small, middle and large models in Anthropic’s Claude 5.5 family. The <a href="method/brief.md">full brief</a> is published with the data.</p>
</section>

<section id="quotes">
  <h2>Did any model make up a quote?</h2>
  <p>No. The fear with AI research is the invented source: a confident sentence in quotation marks that nobody ever wrote. We went looking for one {N} times and did not find it.</p>
  <p>The check was a script, not a second opinion from a model. It fetched each cited page, stripped out the markup, and searched for the whole quote, forgiving only spacing, punctuation and capital letters. All {H['n']} Haiku quotes were there. So were all {S['n']} from Sonnet and all {O['n']} from Opus.</p>
  <p>A checker that passes everything deserves suspicion, so we tested it. We swapped a single word in each of {CONTROL['quotes_tested']} quotes and ran it again. It accepted {'none' if CONTROL['accepted_after_one_word_replaced'] == 0 else CONTROL['accepted_after_one_word_replaced']}.</p>
  <p>The models did not get there by luck. Told that a machine would check them, they checked themselves. “Every claim quote was machine-checked as a verbatim substring of the page text I fetched,” one Haiku run reported. An Opus run wrote that every quote “was re-fetched live and matched exactly (96 of 96).” All nine runs said something similar.</p>
  <p>That sentence in the brief appears to have done real work. We did not run the brief without it, so we cannot say how much.</p>
</section>

<section id="coverage">
  <h2>What did the cheapest model miss?</h2>
  <p>Not the hard facts. The easy ones, at random.</p>
  <p>Opus came back with all {KEYN} known facts in each of its three runs. Sonnet came back with {listed(S['key'])}. Haiku came back with {listed(H['key'])}. A fact counts as found when a run quoted a passage that states it.</p>
  <p>One Haiku run never cited the Google help page that says, in so many words, that all Local Services calls through the forwarding number are recorded. Every quote it did report was real. A writer working from that run alone would have been missing the first fact on the topic and would have had no way to know it.</p>
  <p>The other two Haiku runs found that page. This is the pattern that matters more than the averages. Only {H['key_all']} of the {KEYN} facts appeared in all three Haiku runs, against {S['key_all']} for Sonnet and {O['key_all']} for Opus. But put side by side, the three Haiku runs covered {cover(H['key_union'], KEYN)}. The cheap model was not weak so much as uneven, and unevenness is something a second and third run can fix.</p>
  <div class="tablewrap">
  <table class="wide">
    <caption>Known facts that at least one run missed, with the number of runs out of 3 that found each (Copy for Originals, October 13, 2026). The other {sum(1 for f in FACTS if f['list'] == 'key' and (f['haiku_runs'], f['sonnet_runs'], f['opus_runs']) == ('3', '3', '3'))} of {KEYN} were found by all nine runs.</caption>
    <thead><tr><th scope="col">Known fact</th><th scope="col" class="n">Haiku</th><th scope="col" class="n">Sonnet</th><th scope="col" class="n">Opus</th></tr></thead>
    <tbody>
      {fact_rows('key', only_partial=True)}
    </tbody>
  </table>
  </div>
</section>

<section id="breadth">
  <h2>What did the extra money buy?</h2>
  <p>Reading. Opus cited roughly twice as many pages as Haiku and came back with roughly twice as many claims: about {mean('opus', 'claims'):.0f} a run, against {mean('sonnet', 'claims'):.0f} for Sonnet and {mean('haiku', 'claims'):.0f} for Haiku.</p>
  <p>The extra claims were not padding. Once the results were in, we listed {XN} findings that went beyond our {KEYN} known facts. Opus runs returned {listed(O['extra'])} of them. Sonnet runs returned {listed(S['extra'])}, and Haiku runs {listed(H['extra'])}.</p>
  <p>Some of those findings were news to us. Our guide says Google’s help pages give no date for the day call recording became the default in Google Ads. That is still true of the help pages. But {word(len(DATE_RUNS))} runs found the date anyway, July 1, 2026, in trade coverage of an email Google sent to advertisers. No Haiku run did. We have since read those sources ourselves and added them to the guide.</p>
  <p>The Opus runs also noticed when Google disagreed with itself. A help page says that with recording on, “all calls will be recorded and evaluated by AI.” The terms an advertiser accepts say Google may record “a sample” of calls. All three Opus runs quoted both. Deciding which one governs is not a research task, and none of the models pretended it was.</p>
  <p>Price did not settle everything. All three Haiku runs found a 2013 Connecticut bar opinion on an advertising service that records calls. Only one Sonnet run and one Opus run did. A single Haiku run was the only one of the nine to quote a 2026 New York City Bar opinion on recording calls with prospective clients.</p>
  <p>Taken together the nine runs cited {PAGES} different pages. {ONE} of those were cited by one run only. Just {word(NINE)} were cited by all nine. Whatever model you use, a single run is one researcher’s afternoon, not the last word. The full list of {XN} findings is in <a href="#tables">the tables below</a>.</p>
</section>

<section id="support">
  <h2>Is a real quote enough?</h2>
  <p>Not quite. A quote can be genuine and still not say what the sentence above it claims.</p>
  <p>So we ran a second check. All {N} claims were shuffled, stripped of any sign of which model wrote them, and read against their quotes by two graders working from the same written rule. A claim was flagged when it stated a second fact of substance that its quote did not carry, or when the quote did not show the claim’s main point.</p>
  <p>Both graders flagged {BOTH} claims, about one in {N / BOTH:.0f}. For Haiku the share was {pct(H['both'], H['n'])}, for Sonnet {pct(S['both'], S['n'])}, for Opus {pct(O['both'], O['n'])}.</p>
  <div class="tablewrap">
  <table>
    <caption>Claims flagged as saying more than their quote showed, by two blind graders (Copy for Originals, October 13, 2026)</caption>
    <thead><tr><th scope="col">Model</th><th scope="col" class="n">Claims</th><th scope="col" class="n">Flagged by grader 1</th><th scope="col" class="n">Flagged by grader 2</th><th scope="col" class="n">Flagged by both</th></tr></thead>
    <tbody>
      {grade_rows()}
    </tbody>
  </table>
  </div>
  <p>Most of the flags were the same small sin: two facts in one sentence and a quote for only one. A Sonnet run wrote that a business hears “Call from Google” when a call comes in, though call forwarding or an internet phone line can stop the message playing. Its quote covered the first half. The second half is true, and it is on the same page, and nothing in the quote shows it.</p>
  <p>A few were quotes cut too short. A Haiku run claimed that recordings are not available for health care categories and offered, as proof, the words “available for health care verticals.” Those words are on Google’s page. So is the “aren’t” in front of them, which the quote left out.</p>
  <p>Two cautions. The graders were AI models, and they agreed with each other on {agree} of {N} claims ({pct(agree, N)}), which is good but is not a human read. And the gap between runs of one model was as wide as the gap between models: by run, the share flagged by both graders ran from {min(int(r['flagged_by_both']) / int(r['claims']) for r in RUNS) * 100:.0f}% to {max(int(r['flagged_by_both']) / int(r['claims']) for r in RUNS) * 100:.0f}%, and the two worst were one Haiku run and one Sonnet run.</p>
</section>

<section id="threads">
  <h2>Why couldn’t any of them find the threads?</h2>
  <p>Because the door was locked, and a better model does not pick locks.</p>
  <p>The ninth question asked for up to eight public threads in which lawyers or their marketers talk about the recording first-hand. The obvious place is Reddit. Reddit refused the search tool in every one of the nine runs, {BLOCKED} refusals in all, and it turns away plain page requests too. “Reddit was blocked in every route I tried,” a Sonnet run reported.</p>
  <p>Only {word(len(THREAD_RUNS))} of the nine runs returned a quote from any thread or post at all: from Reddit, from LinkedIn, or from a small forum for local search marketers. {word(len(REDDIT_RUNS), True)} run got into Reddit. An Opus run worked out that the site’s feed addresses still answered, read threads through them between rate-limit refusals, and took {float(slow['minutes']):.0f} minutes where its siblings took 15. It came back with {REDDIT_N} Reddit quotes and an honest verdict on them: “I found no public thread where a lawyer or law firm staffer discusses Google recording these calls.”</p>
  <p>That honesty was the most reassuring thing in the study. No run invented a thread to fill the hole. Every run filed between {min(H['nf'] + S['nf'] + O['nf']):.0f} and {max(H['nf'] + S['nf'] + O['nf']):.0f} items under “not found,” and between {min(H['leads'] + S['leads'] + O['leads']):.0f} and {max(H['leads'] + S['leads'] + O['leads']):.0f} under leads it could not confirm, as the brief had asked.</p>
  <p>For our own thread studies we do not ask a model to search Reddit. A script reads a public archive of it. When the source is closed to the tools, the fix is access, not a bigger model.</p>
</section>

<section id="pilot">
  <h2>What went wrong the first time?</h2>
  <p>The numbers on this page come from our second attempt. The first one taught us more than we wanted.</p>
  <p>We had started all nine runs at once. Eight minutes in, an Opus run asked for a search and got back a sentence we had never seen: “Web search was not performed: this turn’s web search budget is used up (limit: 200 WebSearch calls per turn, shared by every agent in it).” The nine runs had made 202 search calls between them. Calls 201 and 202 both belonged to Opus runs, the slowest of the nine, which were still searching after the cheaper models had stopped. Our test of whether the expensive model is worth it had quietly handicapped the expensive model.</p>
  <p>The second problem came from one of the runs. A Sonnet run noted at the end of its report that “the scratchpad is shared with other agents, and someone else’s build.py replaced mine mid-run.” All three Sonnet runs had saved their working files in the same folder under the same short names. Their quotes still passed against the live pages. But three runs that can read each other’s files are not three independent runs.</p>
  <p>Neither failure was a model’s doing, and both would have skewed the comparison. So we ran everything again. Each run got a private folder, and the runs were started in two groups so that neither group could reach the cap. The logs of the second set show no search refused by the cap and no run touching another’s folder.</p>
  <p>The first set is published as a pilot. Its results were close to the second, which is some comfort: Haiku runs found {listed(nums(tier(PILOT, 'haiku'), 'key_facts_found'))} of the {KEYN} known facts, Sonnet runs {listed(nums(tier(PILOT, 'sonnet'), 'key_facts_found'))}, Opus runs {listed(nums(tier(PILOT, 'opus'), 'key_facts_found'))}. And all {PN} of its quotes were on the page.</p>
</section>

<section id="cost">
  <h2>What did each run cost?</h2>
  <p>About {usd(C['haiku'])} for Haiku, {usd(C['sonnet'])} for Sonnet and {usd(C['opus'])} for Opus, estimated at Anthropic’s list prices. Haiku and Sonnet runs took about {mean('haiku', 'mins'):.0f} and {mean('sonnet', 'mins'):.0f} minutes. Opus runs took {span(O['mins'])}.</p>
  <div class="tablewrap">
  <table class="wide">
    <caption>Average per run by model, three runs each (Copy for Originals, October 13, 2026). Costs are estimates at list prices.</caption>
    <thead><tr><th scope="col">Model</th><th scope="col" class="n">Tool calls</th><th scope="col" class="n">Searches run</th><th scope="col" class="n">Largest prompt, tokens</th><th scope="col" class="n">Token cost</th><th scope="col" class="n">Search fees</th><th scope="col" class="n">Est. cost</th><th scope="col" class="n">Minutes</th></tr></thead>
    <tbody>
      {cost_rows()}
    </tbody>
  </table>
  </div>
  <p>Two things in that table surprised us.</p>
  <p><b>The searches cost as much as the cheap model.</b> Anthropic lists web search at $10 per 1,000 searches, a cent each. Every run made {min(H['search'] + S['search'] + O['search']):.0f} to {max(H['search'] + S['search'] + O['search']):.0f} of them, whatever the model. That fee was {100 * mean('haiku', 'fees') / C['haiku']:.0f}% of a Haiku run’s cost and {100 * mean('opus', 'fees') / C['opus']:.0f}% of an Opus run’s.</p>
  <p><b>Haiku’s low price has a ceiling.</b> Haiku 5.5 costs five times as much on any request whose prompt is longer than 100,000 tokens. Search results and page text pushed every Haiku run past that line, to about {mean('haiku', 'peak') / 1000:.0f},000. {sum(H['over']):.0f} of {sum(H['resp']):.0f} Haiku requests paid the higher rate. Kept under the line, a run’s token cost would have been about {usd(st.mean(haiku_base))}, not {usd(mean('haiku', 'tokcost'))}.</p>
  <p>Even so, three Haiku runs cost less than one Sonnet run. The three together came to an estimated {usd(three_haiku)} and covered {cover(H['key_union'], KEYN)} known facts and {H['x_union']} of the {XN} further findings. One Sonnet run cost about {usd(C['sonnet'])} and covered {span(S['key'])} and {span(S['extra'])}. One Opus run cost about {usd(C['opus'])} and covered {span(O['key'])} and {span(O['extra'])}.</p>
  <p>These are estimates. The logs record what each model read to the token. They do not record a final count of what it wrote, so that part is estimated from the visible text, and the model’s private reasoning is not counted. On a subscription the bill would look different again.</p>
</section>

<section id="when">
  <h2>So which model should do your research?</h2>
  <p>On this evidence, the cheap one can gather, as long as a script checks its quotes and you run it more than once. The expensive one earns its price when the research runs once, when nothing can be missed, and when nobody will read the claims against the quotes afterward.</p>
  <div class="tablewrap">
  <table class="wide">
    <caption>What this test supports, by situation</caption>
    <thead><tr><th scope="col">Situation</th><th scope="col">What held up</th><th scope="col">Evidence from the nine runs</th></tr></thead>
    <tbody>
      <tr><th scope="row">Gather quoted facts from known kinds of sources, with a script checking the quotes</th><td>Haiku</td><td>{H['n']} of {H['n']} Haiku quotes were on the cited page.</td></tr>
      <tr><th scope="row">Cover the main facts on a small budget</th><td>Haiku, run three times and merged</td><td>Three runs together covered {cover(H['key_union'], KEYN)} for about {usd(three_haiku)}. One run alone covered {span(H['key'])}.</td></tr>
      <tr><th scope="row">Cover the main facts in a single run</th><td>Sonnet or Opus</td><td>Sonnet runs covered {span(S['key'])} of {KEYN}, Opus runs {span(O['key'])}.</td></tr>
      <tr><th scope="row">Find what nobody listed in advance: terms, older pages, sources that disagree</th><td>Opus</td><td>Opus runs returned {span(O['extra'])} of {XN} further findings, Sonnet {span(S['extra'])}, Haiku {span(H['extra'])}.</td></tr>
      <tr><th scope="row">Claims go to the writer with no second check against the quotes</th><td>Opus</td><td>Both graders flagged {pct(O['both'], O['n'])} of Opus claims, {pct(S['both'], S['n'])} of Sonnet’s and {pct(H['both'], H['n'])} of Haiku’s.</td></tr>
      <tr><th scope="row">The source blocks the tools</th><td>No model. Fix the access.</td><td>{word(9 - len(REDDIT_RUNS), True)} of nine runs got nothing from Reddit. The one that did took {float(slow['minutes']):.0f} minutes.</td></tr>
    </tbody>
  </table>
  </div>
  <p>This was one topic on one day with three runs per model. Take the table as a place to start your own test, not as a ranking.</p>
</section>

<section id="workflow">
  <h2>How should a marketing team set this up?</h2>
  <p>Split the job in two. Cheap models gather quoted facts. A script checks the quotes. The best model you have reads the checked facts and does the thinking and the writing. Each step below comes from something that happened in this study.</p>
  <ol class="check">
    <li><b>Write the questions down.</b> Ten numbered questions let us score every run question by question. “Research this topic” cannot be scored.</li>
    <li><b>Ask for one fact per claim.</b> Most of the {BOTH} flagged claims had packed two facts behind one quote.</li>
    <li><b>Require the page address and a copied quote, and say a script will check it.</b> All {N} quotes passed. Then actually run the script. Ours is under 200 lines.</li>
    <li><b>Ask for a list of what was not found.</b> Every run kept one. It is how we know Reddit was locked and not empty.</li>
    <li><b>Give each run its own folder.</b> In our first attempt three runs saved pages under the same names and overwrote each other.</li>
    <li><b>Count the searches before you launch.</b> Our tool allowed 200 across all runs started together. Nine runs at about 22 each used them up.</li>
    <li><b>Run the cheap model more than once and merge.</b> Three Haiku runs agreed on only {H['key_all']} of {KEYN} known facts and covered {cover(H['key_union'], KEYN)} between them.</li>
    <li><b>Read each claim against its quote before writing.</b> A second model did this for all {N} claims in under two minutes and agreed with the first grader on {pct(agree, N)} of them.</li>
    <li><b>Reach locked sources another way.</b> An archive, an export or an official data feed beats a stronger model that cannot open the page.</li>
    <li><b>Keep the judgment with your best model.</b> The gathering runs brought back Google pages that contradict each other. Deciding which one is current is the writer’s job.</li>
  </ol>
  <p>For what answer engines do with the finished page, see <a href="../rag-friendly-content/">how to write content that LLMs retrieve and cite</a>. For a study built on public files alone, see <a href="../law-firm-websites-ai-crawlers-study/">do law firm websites block AI crawlers?</a></p>
</section>

<section id="tables">
  <h2>What are the full numbers?</h2>
  <div class="tablewrap">
  <table class="wide">
    <caption>Nine research runs on one brief (Copy for Originals, October 13, 2026). Known facts are out of {KEYN}, further findings out of {XN}. Cost is an estimate at list prices.</caption>
    <thead><tr><th scope="col">Run</th><th scope="col" class="n">Claims</th><th scope="col" class="n">Pages cited</th><th scope="col" class="n">Known facts</th><th scope="col" class="n">Further findings</th><th scope="col" class="n">Claims flagged by both graders</th><th scope="col" class="n">Est. cost</th><th scope="col" class="n">Minutes</th></tr></thead>
    <tbody>
      {run_table()}
    </tbody>
  </table>
  </div>
  <div class="tablewrap">
  <table class="wide">
    <caption>Further findings beyond the {KEYN} known facts, with the number of runs out of 3 that returned each (Copy for Originals, October 13, 2026). The list was written after the runs.</caption>
    <thead><tr><th scope="col">Finding</th><th scope="col" class="n">Haiku</th><th scope="col" class="n">Sonnet</th><th scope="col" class="n">Opus</th></tr></thead>
    <tbody>
      {fact_rows('extra')}
    </tbody>
  </table>
  </div>
  <div class="tablewrap">
  <table>
    <caption>Where each model’s claims came from, three runs combined</caption>
    <thead><tr><th scope="col">Model</th><th scope="col" class="n">Google pages and terms</th><th scope="col" class="n">Bar publications</th><th scope="col" class="n">Threads and posts</th><th scope="col" class="n">Trade press, blogs, other</th><th scope="col" class="n">All claims</th></tr></thead>
    <tbody>
      {mix_rows()}
    </tbody>
  </table>
  </div>
  <div class="tablewrap">
  <table>
    <caption>Pilot runs against the final runs (Copy for Originals, October 13, 2026). Known facts are out of {KEYN}.</caption>
    <thead><tr><th scope="col">Model</th><th scope="col" class="n">Claims per run, pilot</th><th scope="col" class="n">Known facts, pilot</th><th scope="col" class="n">Known facts, final</th></tr></thead>
    <tbody>
      {pilot_rows()}
    </tbody>
  </table>
  </div>
</section>

<section id="method">
  <h2>How was the study done?</h2>
  <ol class="check">
    <li><b>Models:</b> Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5, three runs each, on October 13, 2026. The logs record the model IDs claude-haiku-5-5, claude-sonnet-5-5 and claude-opus-5-5.</li>
    <li><b>Setup:</b> each run was a separate agent started from Claude Code 2.1.295 with default settings. Each had web search, web fetch and a shell, and no view of the other runs. All nine got the same brief, word for word, apart from the folder name.</li>
    <li><b>Quote check:</b> a script fetched every cited page once and looked for each quote, ignoring spacing, punctuation and letter case. Reddit threads were read from the Arctic Shift archive.</li>
    <li><b>Known facts:</b> {KEYN} facts from our published guide to the topic, each tied to the passage that states it. The list was written before any run finished. After the runs we read every miss and added seven alternative passages and one website match, so that a fact quoted from a different page still counts.</li>
    <li><b>Further findings:</b> {XN} findings outside the known facts, listed after reading the results and matched by passage or by website.</li>
    <li><b>Claim against quote:</b> all {N} claims were shuffled and stripped of their model labels. Grader 1 was the Claude Opus 5.5 session that ran the study. Grader 2 was a separate Claude Sonnet 5.5 agent given the same written rule. No person graded.</li>
    <li><b>Cost:</b> token counts come from each run’s log and prices from Anthropic’s pricing page, including $10 per 1,000 web searches and Haiku’s higher rate over 100,000 prompt tokens.</li>
    <li><b>Audit:</b> the logs were searched for any run opening our own site, the answer list or another run’s folder. None did.</li>
  </ol>
  <p>The data files are <a href="data.csv">data.csv</a> (one row per claim), <a href="runs.csv">runs.csv</a>, <a href="facts.csv">facts.csv</a> and <a href="sources.csv">sources.csv</a>. The brief, the grading rule, both graders’ verdicts and every script are listed in <a href="method/README.md">method/README.md</a>.</p>
  <p>Raw outputs as the models wrote them: {raw_links()}. Pilot: <a href="pilot/runs.csv">pilot/runs.csv</a> and <a href="pilot/data.csv">pilot/data.csv</a>.</p>
</section>

<section id="limits">
  <h2>Limitations</h2>
  <ul>
    <li><b>One topic, one day, three runs per model.</b> A gap of a few points between two models is inside the gap between two runs of the same model.</li>
    <li><b>The known facts came from our own guide,</b> which a Claude session researched earlier the same day. A model could find true facts outside that list. Those are counted as further findings, on a list written after the results were in.</li>
    <li><b>The graders are AI models,</b> and they are the same models as two of the three tested. They could not see which model wrote a claim. No person checked their verdicts.</li>
    <li><b>The quote check has limits.</b> It shows that the words are on the page. It does not show that the page is right or up to date. Several runs flagged Google help pages that contradict each other.</li>
    <li><b>Cost is an estimate</b> at list prices. Output tokens were estimated and hidden reasoning was not counted, so true costs are somewhat higher, most of all for Opus.</li>
    <li><b>The tools shaped the result.</b> Another setup, with a Reddit archive or a different search tool, would give different thread results.</li>
    <li><b>The brief was a careful one.</b> We did not test a loose brief, or a brief without the warning that quotes would be checked.</li>
    <li><b>Model versions change.</b> These results describe three models as they ran on October 13, 2026.</li>
    <li><b>Not legal advice.</b> Nothing here says whether a firm should accept recorded calls.</li>
  </ul>
</section>

<section id="faq">
  <h2>FAQ</h2>
{faq_html}
</section>

<section id="sources">
  <h2>Sources</h2>
  <p>All read on October 13, 2026.</p>
  <ul class="sources">
    <li>Anthropic, “Pricing” (model prices, cache prices, web search fee, Haiku 5.5 prices over 100,000 prompt tokens). <a href="https://platform.claude.com/docs/en/about-claude/pricing" rel="noopener">platform.claude.com/docs/en/about-claude/pricing</a></li>
    <li>Copy for Originals, “Does Google record calls to law firms from its ads?” (the source of the {KEYN} known facts). <a href="../does-google-record-calls-to-law-firms/">tools.copyfororiginals.com</a></li>
    <li>Arctic Shift, public archive of Reddit posts and comments, used to check Reddit quotes. <a href="https://arctic-shift.photon-reddit.com/" rel="noopener">arctic-shift.photon-reddit.com</a></li>
    <li>The {PAGES} pages the nine runs cited are listed with their addresses in <a href="sources.csv">sources.csv</a>.</li>
  </ul>
  <p>How to cite: Copy for Originals, “Haiku, Sonnet or Opus for online research? One brief, nine runs, {N} checked quotes,” October 13, 2026, {URL}. Data licensed CC BY 4.0.</p>
</section>

<footer>
  <p>Static page. No scripts, no tracking. Educational only, not legal advice. Made by <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a>.</p>
</footer>
</div>
</body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
print("index.html written:", len(page), "bytes;", N, "claims;", "cost of 9 runs", usd(TOTAL_COST), "pilot", usd(PILOT_COST))
