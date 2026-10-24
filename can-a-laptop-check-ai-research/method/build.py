"""Build ../index.html from ../planted.csv and ../audit.csv, so no number on the page is typed by hand.
The Swedish page at sv/kan-en-laptop-granska-ai-research/ is a translation of this output: after a rebuild
that changes text or numbers, make the same change there by hand.

Usage: python3 build.py [YYYY-MM-DD]   (after prepare.py; the date is the publication date)
"""
import csv, html, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
rd = lambda name: list(csv.DictReader(open(os.path.join(ROOT, name), encoding="utf-8")))
PLANTED, AUDIT = rd("planted.csv"), rd("audit.csv")
DATE = sys.argv[1] if len(sys.argv) > 1 else "2026-10-25"
MONTHS = "January February March April May June July August September October November December".split()
LONGDATE = f"{MONTHS[int(DATE[5:7]) - 1]} {int(DATE[8:])}, {DATE[:4]}"
e = html.escape
REPO = "https://github.com/jbastide/receipts"
URL = "https://tools.copyfororiginals.com/can-a-laptop-check-ai-research/"
SV = "https://tools.copyfororiginals.com/sv/kan-en-laptop-granska-ai-research/"

# Numbers from our earlier study, reproduced by receipts (bench/model_study.py in the receipts repository)
REPRO_N, CONTROL_N, CONTROL_SWAP, CONTROL_CROSS = 593, 588, 0, 22

# ---- planted benchmark --------------------------------------------------------------------------
cases = [r for r in PLANTED if r["counted"] == "True"]
KINDS = ["number", "negation", "swap", "overclaim"]
KIND_NAME = {"number": "A number changed", "negation": "A verb negated", "swap": "Checked against another site’s page",
             "overclaim": "An invented fact added"}
n_orig = sum(r["kind"] == "original" for r in cases)
n_kind = {k: sum(r["kind"] == k for r in cases) for k in KINDS}
n_def = sum(n_kind.values())
dropped = sum(r["counted"] == "False" for r in PLANTED)

def flagged(r, col):
    return r[col] != "supported"

METHODS = [("MiniCheck (770M checker model)", lambda r: flagged(r, "minicheck"), ["minicheck"]),
           ("HHEM-2.1-Open (checker model)", lambda r: flagged(r, "hhem"), ["hhem"]),
           ("Gemma 4 12B as judge", lambda r: flagged(r, "judge"), ["judge"]),
           ("Gemma 4 12B judge, dense claims split", lambda r: flagged(r, "judge_split"), ["judge_split"]),
           ("MiniCheck or the judge flags it", lambda r: flagged(r, "minicheck") or flagged(r, "judge"), ["minicheck", "judge"])]

def seconds(cols):
    """Mean seconds per claim over every case; the split run reused whole-claim timings for short claims."""
    return f"{sum(float(r[c + '_seconds'] or 0) for r in PLANTED for c in cols) / len(PLANTED):.1f}"

def score(fn):
    passed = sum(not fn(r) for r in cases if r["kind"] == "original")
    caught = {k: sum(fn(r) for r in cases if r["kind"] == k) for k in KINDS}
    return passed, caught, sum(caught.values())

S = {name: score(fn) for name, fn, _ in METHODS}
J_PASS, J_KIND, J_ALL = S["Gemma 4 12B as judge"]
M_PASS, M_KIND, M_ALL = S["MiniCheck (770M checker model)"]
H_PASS, H_KIND, H_ALL = S["HHEM-2.1-Open (checker model)"]

def sort_state(r):
    """How the report files a claim with MiniCheck and the judge: pass, check by hand, or flagged."""
    score_ = float(r["minicheck_score"] or 0)
    j = r["judge"]
    disagree = (j == "supported" and score_ < 0.5) or (j == "not_supported" and score_ >= 0.5)
    return "hand" if disagree else ("clean" if j == "supported" else "flagged")

SORT = {grp: Counter(sort_state(r) for r in cases if (r["kind"] == "original") == grp) for grp in (True, False)}

def pct(a, b, dec=0):
    return f"{100 * a / b:.{dec}f}%"

# ---- the real report --------------------------------------------------------------------------------
REV = Counter(r["review"] for r in AUDIT)
N_AUDIT = len(AUDIT)
N_BAD = REV["wrong"] + REV["unsupported"]
N_FIXED = sum(r["corrected"] == "True" for r in AUDIT)
N_QUOTES_BAD = sum(r["kind"] == "quote" for r in AUDIT)
# Facts about the real report and its correction, from the receipts run on the notes and the correction
# commit (see method/README.md); they are not in the two CSV files.
REPORT_CLAIMS, REPORT_SOURCES = 112, 87
QUOTE_FIXES = 7          # passages in quotation marks replaced by the source's own words
EXTRA_FIXES = 7          # errors found during the review outside the flagged items
REV_ROWS = [("correct", "Correct: the source says it"), ("wrong", "Wrong: the source says something different"),
            ("unsupported", "Not in any source the claim cites"), ("other_source", "Right, but on another page the claim cites"),
            ("author_analysis", "The report’s own reasoning, not a sourced fact"), ("cannot_check", "Source could not be read")]

# ---- FAQ ------------------------------------------------------------------------------------------
faq = [
 ("Can a small AI model on a laptop check whether a research report’s sources support it?",
  f"Mostly, if it is used as a judge rather than as the last word. In a Copy for Originals test, Gemma 4 12B running on a MacBook Air with 16 GB of memory caught {J_ALL} of {n_def} claims we had deliberately damaged ({pct(J_ALL, n_def)}) and passed {J_PASS} of {n_orig} correct ones ({pct(J_PASS, n_orig)}), at about ten seconds a claim. Paired with a smaller checker model, {SORT[False]['clean']} of the {n_def} damaged claims got through without a flag."),
 ("How do you check the quotes in an AI research report?",
  f"Fetch every cited page and look for each quoted passage in it, ignoring spacing, punctuation and case. That needs no AI model. Copy for Originals’ checker reproduced all {REPRO_N} quote grades from an earlier study this way, and when one word in each quote was replaced, none of {CONTROL_N} damaged quotes was accepted. A quote that is on the page can still fail to support the claim made with it, so the claim needs a second check."),
 ("What errors does an automated check find in real research?",
  f"In our own published research notes on how AI shopping agents choose products, the checker flagged {N_AUDIT} items. A source-by-source review found {N_BAD} of them wrong or not in any cited source: paraphrases inside quotation marks, a range reported as +19.75 to +23.38 points that the paper gives as +13.0 to +37.9, a finding reported as no effect that the paper reports as statistically significant. {REV['correct']} were correct. The checker narrowed where to look; it did not decide."),
]
faq_ld = ",\n        ".join(
    '{"@type": "Question", "name": %s,\n         "acceptedAnswer": {"@type": "Answer", "text": %s}}' % (json.dumps(q, ensure_ascii=False), json.dumps(a, ensure_ascii=False))
    for q, a in faq)
faq_html = "\n".join(f"  <h3>{e(q)}</h3>\n  <p>{e(a)}</p>" for q, a in faq)

DESC = (f"Copy for Originals built an open-source checker for AI research reports that runs on a laptop. "
        f"A 12B model caught {J_ALL} of {n_def} planted errors and passed {pct(J_PASS, n_orig)} of correct claims. "
        f"In our own published research notes it led us to {N_BAD} wrong or unsupported claims. Data included.")

def method_rows():
    out = []
    for name, _, cols in METHODS:
        p, k, a = S[name]
        cells = [f"{p} of {n_orig}"] + [f"{k[x]} of {n_kind[x]}" for x in KINDS] + [f"{a} of {n_def} ({pct(a, n_def)})", seconds(cols)]
        out.append(f'      <tr><th scope="row">{e(name)}</th>' + "".join(f'<td class="n">{c}</td>' for c in cells) + "</tr>")
    return "\n".join(out)

def review_rows():
    return "\n".join(f'      <tr><th scope="row">{e(label)}</th><td class="n">{REV[key]}</td></tr>' for key, label in REV_ROWS)

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Can a Laptop Check an AI Research Report? {n_def} Planted Errors and One Real Report ({DATE[:4]} Study)</title>
<meta name="description" content="{e(DESC)}">
<meta name="author" content="Copy for Originals">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="index,follow,max-snippet:-1">
<link rel="canonical" href="{URL}">
<link rel="alternate" hreflang="sv" href="{SV}">
<link rel="alternate" hreflang="en" href="{URL}">
<link rel="alternate" hreflang="x-default" href="{URL}">
<meta property="og:type" content="article">
<meta property="og:url" content="{URL}">
<meta property="og:site_name" content="Copy for Originals">
<meta property="og:title" content="Can a laptop check an AI research report? {n_def} planted errors and one real report">
<meta property="og:description" content="A 12B model on a 16 GB laptop caught {pct(J_ALL, n_def)} of planted errors. In our own published research notes it found {N_BAD} wrong or unsupported claims.">
<meta property="article:published_time" content="{DATE}">
<meta property="article:modified_time" content="{DATE}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%A7%BE%3C/text%3E%3C/svg%3E">
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
      "headline": "Can a laptop check an AI research report? {n_def} planted errors and one real report",
      "description": {json.dumps(DESC, ensure_ascii=False)},
      "url": "{URL}",
      "inLanguage": "en",
      "datePublished": "{DATE}",
      "dateModified": "{DATE}",
      "author": {{"@id": "https://copyfororiginals.com/#org"}},
      "publisher": {{"@id": "https://copyfororiginals.com/#org"}},
      "about": ["AI research agents", "Fact-checking", "Local language models", "Citation verification", "Content marketing"],
      "isBasedOn": {{"@id": "{URL}#data"}},
      "breadcrumb": {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{"@type": "ListItem", "position": 1, "name": "Tools", "item": "https://tools.copyfororiginals.com/"}},
          {{"@type": "ListItem", "position": 2, "name": "Can a laptop check an AI research report?", "item": "{URL}"}}
        ]
      }}
    }},
    {{
      "@type": "Dataset",
      "@id": "{URL}#data",
      "name": "Planted-error benchmark and real-report audit for a local AI research checker (Copy for Originals, {DATE[:4]})",
      "description": "planted.csv: {len(PLANTED)} claims ({n_orig} correct, the rest deliberately damaged) with the verdicts of two checker models and a local judge. audit.csv: {N_AUDIT} items the checker flagged in Copy for Originals’ research notes on AI shopping agents, with the result of a source-by-source review.",
      "creator": {{"@id": "https://copyfororiginals.com/#org"}},
      "datePublished": "{DATE}",
      "license": "https://creativecommons.org/licenses/by/4.0/",
      "distribution": [{{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "{URL}planted.csv"}},
                       {{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "{URL}audit.csv"}}]
    }},
    {{
      "@type": "SoftwareSourceCode",
      "@id": "{URL}#code",
      "name": "receipts",
      "codeRepository": "{REPO}",
      "programmingLanguage": "Python",
      "license": "https://www.apache.org/licenses/LICENSE-2.0"
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
pre{{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px;font-size:14px}}
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
    <li><a href="https://www.copyfororiginals.com/faq">FAQs</a></li>
    <li><a href="https://www.copyfororiginals.com/contact">Contact</a></li>
  </ul>
  <ul class="lang-switch" aria-label="Language"><li><a href="../sv/kan-en-laptop-granska-ai-research/" hreflang="sv" lang="sv">Svenska</a></li><li><span aria-current="true">English</span></li></ul>
</nav>
<div class="wrap">

<nav class="crumbs" aria-label="Breadcrumb"><a href="../">&larr; All tools</a></nav>

<header>
  <p class="kicker"><a href="https://copyfororiginals.com/">Copy for Originals</a> · Original research</p>
  <h1>Can a laptop check an AI research report? {n_def} planted errors and one real report</h1>
  <p class="lede">AI research tools now write a sourced report in minutes. Checking whether the sources say what the report says still takes a person most of a day. We built a checker that does the first pass on an ordinary laptop, with nothing sent to an AI company, and published it as open source. We tested it on {len(cases)} claims, {n_def} of them damaged on purpose, and then pointed it at research notes of our own that were already on this site. It caught most of the planted errors. In our own notes it led us to {N_BAD} claims that were wrong or not in their sources, and we have corrected them.</p>
  <p class="byline">By <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a> · Published <time datetime="{DATE}">{LONGDATE}</time> · <a href="planted.csv">Benchmark data (CSV)</a> · <a href="audit.csv">Audit data (CSV)</a> · <a href="{REPO}" rel="noopener">Code</a></p>
  <div class="stats">
    <div class="stat"><b>{J_ALL} of {n_def}</b><span>planted errors caught by a 12B model on a 16 GB laptop ({pct(J_ALL, n_def)})</span></div>
    <div class="stat"><b>{J_PASS} of {n_orig}</b><span>correct claims passed by the same model ({pct(J_PASS, n_orig)})</span></div>
    <div class="stat"><b>{N_BAD}</b><span>wrong or unsupported claims found in our own published research notes</span></div>
  </div>
</header>

<section id="findings">
  <h2>What did the test find?</h2>
  <ol class="check">
    <li><b>Checking quotes needs no AI model.</b> The checker fetches every cited page and looks for each quoted passage. It gave the same grade as our earlier study to all {REPRO_N} quotes, and when one word in each quote was replaced it accepted none of {CONTROL_N}.</li>
    <li><b>A 12B model on a laptop is a usable judge.</b> Gemma 4 12B, running on a MacBook Air with 16 GB of memory, caught {J_ALL} of {n_def} planted errors and passed {J_PASS} of {n_orig} correct claims, at about ten seconds a claim.</li>
    <li><b>The smallest checker models are fast but not enough alone.</b> MiniCheck caught {M_ALL} of {n_def} errors in under a second each, but rejected {n_orig - M_PASS} of {n_orig} correct claims. HHEM missed {n_kind['negation'] - H_KIND['negation']} of {n_kind['negation']} negated claims.</li>
    <li><b>Used together, few errors slip through.</b> When the report shows the judge’s verdict and sends disagreements to a person, {SORT[False]['clean']} of {n_def} planted errors passed without a flag. The price is that a reader checks about one claim in four by hand.</li>
    <li><b>On a real report it narrows the search; it does not decide.</b> In our research notes on how AI shopping agents choose products, it flagged {N_AUDIT} items. Checked against the sources one by one, {N_BAD} were wrong or not in any cited source, {REV['other_source']} were right but cited to the wrong page, and {REV['correct']} were correct.</li>
    <li><b>The errors were the kind a careful reader misses.</b> Paraphrases inside quotation marks, a range quoted as +19.75 to +23.38 points that the paper gives as +13.0 to +37.9, and a finding reported as no effect that the paper calls statistically significant.</li>
  </ol>
</section>

<section id="what">
  <h2>What does the checker do?</h2>
  <p>It reads a report from ChatGPT, Claude, Gemini, Perplexity or an open-source research agent, fetches every page the report cites, and keeps a copy of each. Then it runs three checks.</p>
  <ol class="check">
    <li><b>Quotes.</b> Is each quoted passage on the page it cites, word for word, edited, or missing? This is plain text matching, no model.</li>
    <li><b>Links.</b> Does each link work? For a dead link, the Wayback Machine tells a page that moved from one that may never have existed.</li>
    <li><b>Support.</b> Does the page back the claim? The checker picks the page sentences closest to the claim, a small checker model scores them, and a local chat model reads them and answers supported, partly or not supported. It names the sentences it relied on by number; it never writes a quotation itself. Long claims with several figures are split into single facts first, and each fact is checked on its own.</li>
  </ol>
  <p>Everything runs on the user’s own machine or servers, with any model behind an OpenAI-compatible endpoint (llama.cpp, Ollama, vLLM, LM Studio). The code is at <a href="{REPO}" rel="noopener">github.com/jbastide/receipts</a> under the Apache 2.0 licence.</p>
</section>

<section id="planted">
  <h2>How well does it catch errors?</h2>
  <p>We started from {n_orig} claims in our <a href="../haiku-vs-sonnet-vs-opus-research-study/">earlier study of AI research runs</a> that two graders had accepted and whose quotes were on the cited page. Each was checked as written, where it should pass, and in up to four damaged versions, where it should be flagged: one number changed, the first verb negated, the claim checked against a page from another website, or an invented fact added (“according to a 2019 survey of 4,000 law firms”). {dropped} negations of claims that were already negative made nonsense and are left out.</p>
  <div class="tablewrap">
  <table class="wide">
    <caption>Correct claims passed and damaged claims caught, by method (Copy for Originals, {LONGDATE}; MacBook Air, Apple M5, 16 GB)</caption>
    <thead><tr><th scope="col">Method</th><th scope="col" class="n">Correct passed</th>""" + "".join(f'<th scope="col" class="n">{KIND_NAME[k]}</th>' for k in KINDS) + f"""<th scope="col" class="n">All errors caught</th><th scope="col" class="n">Seconds per claim</th></tr></thead>
    <tbody>
{method_rows()}
    </tbody>
  </table>
  </div>
  <p>Splitting long claims into single facts made no difference here, because each planted error sits in one fact. It matters on real reports, where one sentence can carry five figures and the reader needs to know which one fails.</p>
  <div class="tablewrap">
  <table>
    <caption>How the report files claims when MiniCheck and the judge are used together</caption>
    <thead><tr><th scope="col"></th><th scope="col" class="n">Passed</th><th scope="col" class="n">Check by hand</th><th scope="col" class="n">Flagged</th></tr></thead>
    <tbody>
      <tr><th scope="row">{n_orig} correct claims</th><td class="n">{SORT[True]['clean']}</td><td class="n">{SORT[True]['hand']}</td><td class="n">{SORT[True]['flagged']}</td></tr>
      <tr><th scope="row">{n_def} damaged claims</th><td class="n">{SORT[False]['clean']}</td><td class="n">{SORT[False]['hand']}</td><td class="n">{SORT[False]['flagged']}</td></tr>
    </tbody>
  </table>
  </div>
</section>

<section id="real">
  <h2>What did it find in a real report?</h2>
  <p>We ran it on the research notes behind our page <a href="../how-ai-agents-choose-products/">How AI agents choose products</a>: {REPORT_CLAIMS} claims citing {REPORT_SOURCES} sources, most of them academic papers. The checker flagged {N_QUOTES_BAD} quotes that were not on their pages and {N_AUDIT - N_QUOTES_BAD} facts with figures it could not confirm. Each flagged item was then checked against its source, reading the paper or page itself.</p>
  <div class="tablewrap">
  <table>
    <caption>The {N_AUDIT} flagged items after review against the sources</caption>
    <thead><tr><th scope="col">Result</th><th scope="col" class="n">Items</th></tr></thead>
    <tbody>
{review_rows()}
    </tbody>
  </table>
  </div>
  <p>So roughly one flag in four pointed at a real problem. That is the honest description of what a local checker does with dense research prose today: it cannot tell a missed sentence from a missing fact, but it turns a reading of {REPORT_SOURCES} sources into a list of {N_AUDIT} places to look. Some of what it found:</p>
  <ul>
    <li>{QUOTE_FIXES} passages in quotation marks were not the source’s words. One <a href="https://arxiv.org/html/2509.25609v2" rel="noopener">paper</a> says user profiles act “more like categorical switches or thresholds”; our notes had them “act as switches that override other cues”.</li>
    <li>A defence that “left social-proof effects of +19.75 to +23.38 points intact” left them at +13.0 to +37.9 across the seven models in the <a href="https://arxiv.org/html/2502.01349v2" rel="noopener">paper’s table</a>.</li>
    <li>Two negative-framing cues reported as having no effect were, in the <a href="https://arxiv.org/html/2509.25609v2" rel="noopener">paper</a>, “both statistically significantly effective”.</li>
    <li>A crawl-to-referral ratio of 38,000:1 was right, but cited to a page with different, later numbers; it is <a href="https://blog.cloudflare.com/crawlers-click-ai-bots-training/" rel="noopener">Cloudflare’s own July 2025 figure</a> (38,065.7 for Anthropic).</li>
  </ul>
  <p>The published page had been checked before it went live and already used the sources’ wording. The research notes behind it had not. We corrected them: {N_FIXED} edits from the flagged items and {EXTRA_FIXES} more found while reviewing them. Afterwards every quote in the notes was on its cited page.</p>
</section>

<section id="limits">
  <h2>What are the limits?</h2>
  <ul>
    <li>The planted errors are mechanical. Real mistakes are subtler, so the catch rates above are a ceiling, not a promise.</li>
    <li>On the real report we only know about the errors it flagged. Errors it passed as supported were not counted.</li>
    <li>The judge reads the sentences that best match the claim, not the whole page. A claim drawn from a table or another part of the page can be marked unsupported.</li>
    <li>One judge model, one machine, one run. Results with other models will differ; the checker is built so you can measure your own.</li>
    <li>The review of the real report was done with the help of AI agents and spot-checked: every quote they relied on was matched against the source page by script.</li>
  </ul>
</section>

<section id="run">
  <h2>How do I run it on my own reports?</h2>
  <p>On a Mac or Linux machine with <a href="https://docs.astral.sh/uv/" rel="noopener">uv</a> installed and a local model server running:</p>
  <pre><code>git clone {REPO}
cd receipts
uv sync --extra support
uv run receipts check report.md --judge-url http://127.0.0.1:8080/v1</code></pre>
  <p>It writes a readable report, a JSON file and a CSV. The quote and link checks work without any model: <code>uv run receipts check report.md</code>.</p>
</section>

<section id="faq">
  <h2>Questions</h2>
{faq_html}
</section>

<section id="method">
  <h2>Data and method</h2>
  <ul>
    <li><a href="planted.csv">planted.csv</a>: all {len(PLANTED)} planted cases, the claim as checked, the page, and each method’s verdict and score.</li>
    <li><a href="audit.csv">audit.csv</a>: the {N_AUDIT} items flagged in our research notes, the review result, the source passage and whether the notes were corrected.</li>
    <li><a href="method/prepare.py">method/prepare.py</a> writes both files from the checker’s benchmark output; <a href="method/build.py">method/build.py</a> writes this page from them.</li>
    <li>Models: MiniCheck-Flan-T5-Large, HHEM-2.1-Open, Gemma 4 12B instruction-tuned (QAT, 4-bit) on llama.cpp. The benchmark script is <code>bench/planted.py</code> in the code repository.</li>
  </ul>
</section>

<footer>
  <p>Static page. Google Analytics only if you accept cookies. Made by <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a>.</p>
  <p class="legal"><a href="https://www.copyfororiginals.com/privacy-policy" rel="noopener">Privacy policy</a> · <a href="#cookie-settings">Cookie settings</a></p>
</footer>
</div>
<script src="../consent.js"></script>
</body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
print(f"wrote index.html: judge {J_ALL}/{n_def} caught, {J_PASS}/{n_orig} passed; audit {N_BAD} bad of {N_AUDIT}")
