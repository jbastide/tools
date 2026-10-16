"""Build ../index.html from the CSV files, so no number on the page is typed by hand.

Inputs (all in the study folder): monthly_counts.csv, threads.csv, quotes.csv, gsc_report_themes.csv,
agreement.csv, first-pass/threads.csv. Every quotation on the page is looked up by thread id and source
in quotes.csv, where each one was already checked character for character against the Reddit archive.
The Swedish page at sv/ai-synlighet-matning-reddit-studie/ is a translation of this output: after a rebuild
that changes text or numbers, make the same change there.

Usage: python3 build.py
"""
import csv, html, json, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
rd = lambda *p: list(csv.DictReader(open(os.path.join(ROOT, *p), encoding="utf-8")))
MONTHLY, THREADS, QUOTES, THEMES, AGREE = (rd("monthly_counts.csv"), rd("threads.csv"), rd("quotes.csv"),
                                           rd("gsc_report_themes.csv"), rd("agreement.csv"))
FIRST = rd("first-pass", "threads.csv")
e = html.escape

URL = "https://tools.copyfororiginals.com/ai-visibility-measurement-reddit-study/"
SV = "https://tools.copyfororiginals.com/sv/ai-synlighet-matning-reddit-studie/"
PUB = "2026-10-16"
PUB_TXT = "October 16, 2026"
SWEEP = "October 15, 2026"

CATS = [  # code, short name, one-line meaning
    ("GSC_AI_DATA", "Search Console and AI Overviews", "AI Overview and AI Mode data mixed into Search Console, and the new generative AI report"),
    ("TOOL_COST_ACCURACY", "Tool cost and accuracy", "AI visibility trackers are expensive, disagree, or rest on synthetic prompts"),
    ("FORMAT_CLAIMS", "Content-format claims", "Claims, or rebuttals, that direct answers, FAQs or tables get cited"),
    ("AEO_IS_SEO", "“It’s just SEO”", "Scepticism that AEO or GEO differs from SEO"),
    ("NO_LLM_DATA", "No data from the chat assistants", "ChatGPT, Gemini, Claude and Perplexity publish no query or citation data"),
    ("NONDETERMINISM", "Answers change between runs", "The same prompt gives different answers by session, place or model version"),
    ("PROMPT_SELECTION", "Which prompts to track", "How many prompts, which ones, synthetic or real, long tail or head terms"),
    ("CLIENT_PRESSURE", "Client and boss pressure", "Clients and leadership demand AI visibility reports"),
    ("REVENUE_ROI", "Can’t tie it to revenue", "No path from AI visibility to leads, sales or return"),
    ("GA4_ATTRIBUTION", "Analytics and dark traffic", "GA4 doesn’t separate AI traffic; referrers go missing"),
    ("FAN_OUT", "Query fan-out", "AI systems expand one question into many searches"),
    ("TRAFFIC_LOSS_DIAG", "Diagnosing lost clicks", "Hard to prove that AI Overviews caused a traffic drop"),
]
CODE2NAME = {c: n for c, n, _ in CATS}

# ---------- numbers ----------
ALL = [r for r in MONTHLY if r["subreddit"] == "ALL"]
BYSUB = [r for r in MONTHLY if r["subreddit"] not in ("ALL", "GoogleSearchConsole")]
TOTAL = sum(int(r["total_posts"]) for r in ALL)
BROAD = sum(int(r["aeo_posts_broad"]) for r in ALL)
CORE = sum(int(r["aeo_posts_core"]) for r in ALL)
MEAS = sum(int(r["aeo_measurement_posts"]) for r in ALL)
def share(r, k):
    return 100 * int(r[k]) / int(r["total_posts"])
FIRST_M, LAST_FULL, LAST_PART = ALL[0], ALL[-2], ALL[-1]
PEAK_FULL = max(ALL[:-1], key=lambda r: share(r, "aeo_posts_broad"))
MEAS_FOLD = share(LAST_FULL, "aeo_measurement_posts") / share(FIRST_M, "aeo_measurement_posts")
SUBS = defaultdict(lambda: [0, 0, 0, 0])
for r in BYSUB:
    s = SUBS[r["subreddit"]]
    s[0] += int(r["total_posts"]); s[1] += int(r["aeo_posts_broad"]); s[2] += int(r["aeo_posts_core"]); s[3] += int(r["aeo_measurement_posts"])
SUBS = dict(sorted(SUBS.items(), key=lambda kv: -kv[1][1] / kv[1][0]))
NSUBS = len(SUBS)
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
import statistics
MEDIAN_CATS = int(statistics.median(len([c for c in t["categories"].split(";") if c]) for t in THREADS if t["relevant"] == "True"))

N_THREADS = len(THREADS)
REL = [t for t in THREADS if t["relevant"] == "True"]
N_REL = len(REL)
N_COMMENTS = sum(int(t["comments_in_archive"] or 0) for t in THREADS)  # comments actually pulled and read
HC = [t for t in THREADS if t["healthcare"] == "True"]
CAT_N = Counter()
for t in THREADS:
    for c in t["categories"].split(";"):
        if c:
            CAT_N[c] += 1
assert set(CAT_N) <= {c for c, _, _ in CATS}
RANKED = sorted(CATS, key=lambda x: -CAT_N[x[0]])
N_QUOTES = len(QUOTES)
assert all(q["quote"] for q in QUOTES)
GSC_THREADS = len({q["thread"] for q in QUOTES if q["category"] == "GSC_REPORT"})
THEME_N = {t["theme"]: int(t["threads"]) for t in THEMES}
def theme(prefix):
    k = [t for t in THEME_N if t.startswith(prefix)]
    assert len(k) == 1, prefix
    return THEME_N[k[0]]
T_CLICKS, T_QUERY, T_ROLLOUT, T_ACTION, T_PRAISE, T_BING, T_DEF, T_LIMITS, T_REV = (
    theme("No clicks"), theme("No query"), theme("Uneven rollout"), theme("Not actionable"), theme("Praised"),
    theme("Bing"), theme("Ambiguous"), theme("Data limits"), theme("Can't connect"))
FIRST_REL = sum(t["relevant"] == "True" for t in FIRST)
AG = {r["category"]: r for r in AGREE}
KAPPAS = [float(AG[c]["kappa"]) for c, _, _ in CATS]
AGREES = [float(AG[c]["agreement_pct"]) for c, _, _ in CATS]
FIRST_ONLY = sum(int(AG[c]["first_only"]) for c, _, _ in CATS)
PUB_ONLY = sum(int(AG[c]["published_only"]) for c, _, _ in CATS)
REL_2025 = sum(t["date"] < "2026" for t in REL)
REL_SUBS = Counter(t["subreddit"] for t in REL)
SEL = Counter()
for t in THREADS:
    for r in t["selection_reason"].split(";"):
        SEL[r] += 1
N_TOP60 = SEL["top60_measurement_by_comments"]
N_GSC_SEL = SEL["gsc_and_ai_since_2026"]
N_PROMPT_SEL = SEL["top30_prompt_topic"]
N_HC_SEL = SEL["top20_healthcare"]
MIN_TOP60_COMMENTS = min(int(t["num_comments"]) for t in THREADS if "top60" in t["selection_reason"])

def pct(x, d=1):
    return f"{x:.{d}f}%"
def n(x):
    return f"{x:,}"

# ---------- quotes ----------
QI = {(q["thread"], q["source"], q["category"]): q for q in QUOTES}
QANY = {}
for q in QUOTES:
    QANY.setdefault((q["thread"], q["source"]), q)
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def date_txt(d):
    y, m, dd = d.split("-")
    return f"{MONTHS[int(m) - 1]} {int(dd)}, {y}"
def quote(thread, source, category=None):
    q = QI.get((thread, source, category)) if category else QANY.get((thread, source))
    assert q, (thread, source, category)
    assert q["promo"] == "0", ("promotional quote picked", thread, source)
    return (f'<blockquote><p>{e(q["quote"])}</p>'
            f'<footer>r/{e(q["subreddit"])}, {date_txt(q["date"])} · <a href="{e(q["permalink"])}" rel="noopener nofollow">thread</a></footer></blockquote>')

# ---------- tables ----------
def monthly_table():
    rows = []
    for r in ALL:
        y, m = r["month"].split("-")
        label = f"{MONTHS[int(m) - 1][:3]} {y}" + (" (to the 15th)" if r is LAST_PART else "")
        rows.append(f'<tr><th scope="row">{label}</th><td class="n">{n(int(r["total_posts"]))}</td>'
                    f'<td class="n">{n(int(r["aeo_posts_broad"]))}</td><td class="n">{pct(share(r, "aeo_posts_broad"))}</td>'
                    f'<td class="n">{n(int(r["aeo_measurement_posts"]))}</td><td class="n">{pct(share(r, "aeo_measurement_posts"), 2)}</td></tr>')
    return f'''<div class="tablewrap"><table class="wide">
    <caption>Posts about AI search and about measuring it, as a share of all posts in {WORDS[NSUBS]} marketing subreddits, by month (Arctic Shift archive, swept {SWEEP}). “AI search” means the post names AEO, GEO, generative or answer engines, AI Overviews, AI Mode, AI visibility, AI search or traffic, ChatGPT or Perplexity. “Measurement” adds a tracking, reporting or attribution term and excludes posts that only name ChatGPT or Perplexity.</caption>
    <thead><tr><th scope="col">Month</th><th scope="col" class="n">All posts</th><th scope="col" class="n">AI search</th><th scope="col" class="n">Share</th><th scope="col" class="n">Measurement</th><th scope="col" class="n">Share</th></tr></thead>
    <tbody>{"".join(rows)}</tbody></table></div>'''

def sub_table():
    rows = []
    for s, v in SUBS.items():
        rows.append(f'<tr><th scope="row">r/{e(s)}</th><td class="n">{n(v[0])}</td><td class="n">{pct(100 * v[1] / v[0])}</td>'
                    f'<td class="n">{pct(100 * v[3] / v[0], 2)}</td><td class="n">{REL_SUBS.get(s, 0)}</td></tr>')
    return f'''<div class="tablewrap"><table class="wide">
    <caption>The {NSUBS} subreddits, January 1, 2025 to {SWEEP}: posts, share about AI search, share about measuring it, and the number of threads from each that were read and judged relevant.</caption>
    <thead><tr><th scope="col">Subreddit</th><th scope="col" class="n">Posts</th><th scope="col" class="n">AI search</th><th scope="col" class="n">Measurement</th><th scope="col" class="n">Threads read, relevant</th></tr></thead>
    <tbody>{"".join(rows)}</tbody></table></div>'''

def cat_table():
    rows = []
    for c, name, meaning in RANKED:
        rows.append(f'<tr><th scope="row">{name}</th><td>{e(meaning)}</td><td class="n">{CAT_N[c]}</td></tr>')
    return f'''<div class="tablewrap"><table class="wide">
    <caption>Measurement problems raised in {N_THREADS} Reddit threads ({n(N_COMMENTS)} comments), coded by Claude Opus 5.5 against a fixed codebook. A thread counts once per problem when at least one participant discusses it in substance. {N_REL} threads were judged relevant; the rest are counted as raising nothing.</caption>
    <thead><tr><th scope="col">Problem</th><th scope="col">What people describe</th><th scope="col" class="n">Threads</th></tr></thead>
    <tbody>{"".join(rows)}</tbody></table></div>'''

def theme_table():
    rows = []
    for t in sorted(THEMES, key=lambda t: -int(t["threads"])):
        rows.append(f'<tr><th scope="row">{e(t["theme"])}</th><td class="n">{t["threads"]}</td></tr>')
    return f'''<div class="tablewrap"><table>
    <caption>What {GSC_THREADS} threads said about Search Console’s generative AI report, grouped by theme. A thread can appear under several themes.</caption>
    <thead><tr><th scope="col">Theme</th><th scope="col" class="n">Threads</th></tr></thead>
    <tbody>{"".join(rows)}</tbody></table></div>'''

def agree_table():
    rows = []
    for c, name, _ in RANKED:
        a = AG[c]
        rows.append(f'<tr><th scope="row">{name}</th><td class="n">{a["first_pass_threads"]}</td><td class="n">{a["published_threads"]}</td>'
                    f'<td class="n">{a["agreement_pct"]}%</td><td class="n">{a["kappa"]}</td></tr>')
    a = AG["RELEVANT"]
    rows.append(f'<tr><th scope="row">Thread judged relevant at all</th><td class="n">{a["first_pass_threads"]}</td><td class="n">{a["published_threads"]}</td>'
                f'<td class="n">{a["agreement_pct"]}%</td><td class="n">{a["kappa"]}</td></tr>')
    return f'''<div class="tablewrap"><table class="wide">
    <caption>The same {N_THREADS} threads coded twice against the same codebook: a first pass by Claude Sonnet 5.5 agents and the published pass by Claude Opus 5.5 agents told to count only substantive discussion. Agreement is the share of threads where both passes made the same call; kappa is Cohen’s kappa.</caption>
    <thead><tr><th scope="col">Problem</th><th scope="col" class="n">First pass</th><th scope="col" class="n">Published</th><th scope="col" class="n">Agreement</th><th scope="col" class="n">Kappa</th></tr></thead>
    <tbody>{"".join(rows)}</tbody></table></div>'''

# ---------- text ----------
TITLE = "“Useful diagnostic, terrible KPI”: what 200,753 Reddit posts say about measuring AI visibility"
assert n(TOTAL) == "200,753", TOTAL
SEO_TITLE = f"Measuring AI Visibility: What {n(TOTAL)} Reddit Posts Say (2026 Study)"
DESC = (f"Copy for Originals read every post in {WORDS[NSUBS]} marketing subreddits from January 2025 to {SWEEP} ({n(TOTAL)} posts). "
        f"Posts about AI search rose from {pct(share(FIRST_M, 'aeo_posts_broad'))} to {pct(share(LAST_FULL, 'aeo_posts_broad'))} of all posts; posts about measuring it rose about {MEAS_FOLD:.0f}-fold. "
        f"{N_THREADS} threads were coded for the problems people hit: Search Console’s AI data ({CAT_N['GSC_AI_DATA']} threads), tool accuracy ({CAT_N['TOOL_COST_ACCURACY']}), no data from the chat assistants ({CAT_N['NO_LLM_DATA']}). "
        f"{N_QUOTES} quotes checked against the archive. Data and scripts included.")
LEDE = (f"In the spring of 2026 a marketer confessed on Reddit that when a vice president asked for a monthly AI visibility report, they “seriously considered just making the numbers up.” "
        f"The confession got laughs because everyone in the thread had the same problem. We wanted to know how common it was. So we pulled every post from {WORDS[NSUBS]} marketing subreddits since January 2025, "
        f"{n(TOTAL)} of them, and counted how often the conversation turned to AI search, and how often to measuring it. Then we read {N_THREADS} threads where people tried. "
        f"The share of posts about AI search grew from one in {round(100 / share(FIRST_M, 'aeo_posts_broad'))} to one in {round(100 / share(LAST_FULL, 'aeo_posts_broad'))}. "
        f"The share about measuring it grew about {MEAS_FOLD:.0f}-fold. And the people trying to measure it describe the same handful of walls, in roughly the same order.")

FAQ = [
    ("How many marketers are asking about AI search on Reddit?",
     f"More every month. Across {n(TOTAL)} posts in {WORDS[NSUBS]} marketing subreddits, the share that named AI search (AEO, GEO, AI Overviews, ChatGPT and similar terms) rose from "
     f"{pct(share(FIRST_M, 'aeo_posts_broad'))} in January 2025 to {pct(share(LAST_FULL, 'aeo_posts_broad'))} in September 2026, and {pct(share(LAST_PART, 'aeo_posts_broad'))} in the first half of October. "
     f"In r/TechSEO and r/bigseo it is now more than one post in ten. Posts specifically about measuring or reporting AI visibility rose about {MEAS_FOLD:.0f}-fold, from "
     f"{pct(share(FIRST_M, 'aeo_measurement_posts'), 2)} to {pct(share(LAST_FULL, 'aeo_measurement_posts'), 2)} of all posts."),
    ("What is the hardest part of measuring AI visibility, according to practitioners?",
     f"Of {N_THREADS} Reddit threads coded by Copy for Originals, the problem raised most often was Google Search Console’s handling of AI Overviews and AI Mode ({CAT_N['GSC_AI_DATA']} threads), "
     f"followed by the cost and accuracy of AI visibility tools ({CAT_N['TOOL_COST_ACCURACY']}), claims about which content formats get cited ({CAT_N['FORMAT_CLAIMS']}), "
     f"the view that AEO is just SEO renamed ({CAT_N['AEO_IS_SEO']}), and the absence of any first-party data from ChatGPT, Gemini, Claude or Perplexity ({CAT_N['NO_LLM_DATA']}). "
     f"Answers that change between runs ({CAT_N['NONDETERMINISM']} threads) and the choice of which prompts to track ({CAT_N['PROMPT_SELECTION']}) follow close behind."),
    ("What do practitioners think of Search Console’s generative AI report?",
     f"Useful but thin. Of {GSC_THREADS} threads that discussed the report, {T_PRAISE} welcomed it as the first separate view of AI visibility from Google, "
     f"{T_QUERY} complained that it has no query or prompt data, {T_CLICKS} that it shows impressions but no clicks, {T_ROLLOUT} that it reached some sites and not others, "
     f"and {T_ACTION} that it changes no decisions. The compressed verdict from one thread was “useful diagnostic, terrible kpi.” {T_BING} threads said Bing Webmaster Tools, which shows the search phrases Copilot actually ran, does it better."),
]

# ---------- page ----------
def stat(b, s):
    return f'<div class="stat"><b>{b}</b><span>{s}</span></div>'

def section_problems():
    out = []
    def block(code, intro, picks):
        out.append(f'<h3>{CODE2NAME[code]} <span class="count">({CAT_N[code]} threads)</span></h3>')
        out.append(f"<p>{intro}</p>")
        for p in picks:
            out.append(quote(*p))
    block("GSC_AI_DATA",
          f"The most common complaint is about the one tool everyone already has. Until June 2026, impressions from AI Overviews sat inside Search Console’s ordinary totals with no way to separate them, "
          f"and every link in an AI Overview was given the same position. The new generative AI report, discussed below, fixed the first problem for impressions only.",
          [("1vhnryb", "c:p2cc4y2", "GSC_AI_DATA"), ("1vqyhav", "post", "GSC_AI_DATA")])
    block("TOOL_COST_ACCURACY",
          "The tools that sell a solution draw nearly as many threads as the gap they fill. The recurring objections: the prompts are synthetic, the answers come from an API that doesn’t behave like the app, two tools disagree, and the price is hard to justify to a client.",
          [("1n319y9", "c:nbbqdg1"), ("1sethst", "c:ofc4t4q"), ("1qcaofa", "c:nzjg26j")])
    block("FORMAT_CLAIMS",
          "Threads about measurement keep turning into threads about tactics, and the tactic most often proposed is a format: answer first, add an FAQ, use a table, add schema. Most of these claims are offered as experience, and some participants push back.",
          [("1wtxgx6", "c:pcyoih1"), ("1rd7frn", "c:o737ahl")])
    block("AEO_IS_SEO",
          "A large minority doubts that there is anything new to measure. The sharpest version of the argument concedes one point: whether a brand appears at all is worth tracking, and the rest is packaging.",
          [("1upn9p3", "c:ow1fvx9"), ("1m0iegj", "c:n3acy72")])
    block("NO_LLM_DATA",
          "For ChatGPT, Gemini, Claude and Perplexity there is nothing to open. No query report, no impression count, no equivalent of Search Console. Everything downstream, from the tools to the dashboards, is an estimate built on that absence.",
          [("1s45fli", "c:ockp5st"), ("1nddelu", "c:ndh76ra")])
    block("NONDETERMINISM",
          "Ask the same question twice and the answer changes. Practitioners who have tried to track a position in an AI answer describe giving up, and those who kept going describe averaging many runs.",
          [("1vg54co", "c:p1zu3a1"), ("1v8vxyk", "c:p0a5oq9")])
    block("PROMPT_SELECTION",
          "If there is no data on what people ask, someone has to decide which questions to track, and that decision shapes every number that follows. The threads describe shortlists of twenty to fifty buyer-intent prompts, built from sales calls or Search Console, and a shared unease about who picks them.",
          [("1vhr4k9", "c:p2rudhq"), ("1nkh6ux", "c:neyewoa"), ("1x29ltx", "c:pf0j0en")])
    block("CLIENT_PRESSURE",
          "The demand for a number comes from above. Clients ask why they are not in ChatGPT; boards want to be kept calm; the person in the middle has a report to deliver and no data to put in it.",
          [("1tpwpne", "c:ooc0vkc"), ("1t2ez3t", "c:ojt6tnj"), ("1rw6ujr", "c:oaxwnvq")])
    block("REVENUE_ROI",
          "Even where visibility can be counted, the path from an AI answer to a sale is dark. The threads treat AI search like an awareness channel: real, probably valuable, and resistant to the attribution models that run the rest of the budget.",
          [("1qjlnbc", "c:o22fbkc"), ("1t40v9h", "c:ojzmgi2")])
    block("GA4_ATTRIBUTION",
          "Some AI visits do arrive, and analytics files many of them as direct traffic. The workarounds people trade are a referral filter for the AI domains, a UTM check, and the oldest instrument in marketing: asking the customer how they heard of you.",
          [("1t2ez3t", "post"), ("1sepe9p", "c:og2qduz")])
    block("FAN_OUT",
          "A smaller group has noticed that an AI assistant answers one question by running several searches of its own, and that those background searches, not the user’s prompt, decide which pages it reads. The point is raised both as a tactic and as another thing nobody can see.",
          [("1vg54co", "c:p20fndo"), ("1rm2mpb", "c:o8ytm0b")])
    block("TRAFFIC_LOSS_DIAG",
          "The pattern is familiar by now: rankings hold, impressions rise, clicks fall. Proving that an AI Overview did it is harder than noticing it, and some participants warn against blaming AI for every drop.",
          [("1qcq17b", "post"), ("1jpzf88", "c:ml8ljos")])
    return "\n".join(out)

def section_gsc():
    return f"""
  <p>Google announced the “Search Generative AI performance reports” on June 3, 2026, first for a subset of sites and, from August 31, for every site. The report shows how often a site’s pages appeared in AI Overviews and AI Mode, by page, country, device and day. It shows nothing else: no clicks, no click-through rate, no queries, no split between the two features, and no API. Those are Google’s own terms, from its help pages, and they match what practitioners found when the report reached them.</p>
  <p>{GSC_THREADS} of the threads we read discussed the report itself. The reaction divides neatly into relief and disappointment, often in the same comment.</p>
  {theme_table()}
  <p>The relief first. For two years the only view of AI visibility on Google was inference, and here was a number from Google.</p>
  {quote("1tvnxy1", "c:opibbo6", "GSC_REPORT")}
  {quote("1vm9bv6", "c:p3f1r35", "GSC_REPORT")}
  {quote("1vn6ko5", "c:p3fspu2", "GSC_REPORT")}
  <p>Then the disappointment, which has two parts. The report shows that a page appeared, but not for what question or with what result.</p>
  {quote("1vhfhva", "c:p2qzobr", "GSC_REPORT")}
  {quote("1w4snhv", "post", "GSC_REPORT")}
  {quote("1u1wj0v", "c:oqtvb3y", "GSC_REPORT")}
  <p>And a number that only goes up as Google shows more AI features is a poor measure of anyone’s work. The comment that gave this study its title made the point in four words; the post it answered made it at length.</p>
  {quote("1vm5c3p", "post", "GSC_REPORT")}
  {quote("1vm5c3p", "c:p394vyy", "GSC_REPORT")}
  {quote("1vkjak8", "c:p2yflyb", "GSC_REPORT")}
  <p>{T_BING} threads pointed across the street. Bing Webmaster Tools has shown Copilot citations since February 2026, together with a sample of the “grounding queries,” the search phrases the AI actually ran before it answered. Google shows no equivalent.</p>
  {quote("1u698ul", "post", "GSC_REPORT")}
  {quote("1upn9p3", "c:ow2t0pn", "GSC_REPORT")}
  <p>One thing may change. On June 3, 2026 the UK Competition and Markets Authority required Google to give publishers AI impressions, clicks and click-through rate “fully disaggregated from other elements of general search,” through “a commonly accessible platform, such as Google Search Console,” within six months. That falls in early December 2026. Whether the same data reaches sites outside the UK is not stated.</p>"""

def section_health():
    return f"""
  <p>Almost nobody. Health terms appear in about one in a hundred of the posts about AI search, and {len(HC)} of the {N_THREADS} threads we read were about a healthcare business. That is a gap rather than a finding, and it matters for two reasons. Health is the industry where Google shows AI Overviews most often, at least in Conductor’s benchmark of ten industries, where they appeared on 48.7% of page-one health queries. And the sources those answers cite are rarely individual practices: in Google’s AI Overviews the most-cited health pages are news and health publishers, and in ChatGPT, Gemini and Perplexity, directories such as WebMD and Vitals account for 52.6% of healthcare citations, according to Yext. Both measurements come from vendors that sell visibility tools.</p>
  <p>Where health does come up, the setting is local. A dental practice watches a competitor get named for “best dental clinic in my area” and asks how; the replies say ordinary local SEO. Another thread notices the thing that makes local measurement hard in the first place.</p>
  {quote("1swy9g8", "c:oinef82")}
  {quote("1w4snhv", "post", "NONDETERMINISM")}"""

def page():
    faq_html = "\n".join(f"  <h3>{e(q)}</h3>\n  <p>{e(a)}</p>" for q, a in FAQ)
    faq_ld = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": "https://copyfororiginals.com/#org", "name": "Copy for Originals", "url": "https://copyfororiginals.com"},
            {"@type": "Article", "@id": URL + "#article", "headline": TITLE, "description": DESC, "url": URL, "inLanguage": "en",
             "datePublished": PUB, "dateModified": PUB,
             "author": {"@id": "https://copyfororiginals.com/#org"}, "publisher": {"@id": "https://copyfororiginals.com/#org"},
             "about": ["Answer engine optimization", "AI visibility measurement", "Google Search Console", "AI Overviews", "Reddit", "Open-source intelligence"],
             "isBasedOn": {"@id": URL + "#data"},
             "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Tools", "item": "https://tools.copyfororiginals.com/"},
                 {"@type": "ListItem", "position": 2, "name": "AI visibility measurement Reddit study", "item": URL}]}},
            {"@type": "Dataset", "@id": URL + "#data",
             "name": f"AI search and measurement talk in {WORDS[NSUBS]} marketing subreddits, 2025–2026 (Copy for Originals)",
             "description": f"Monthly counts of posts about AI search and about measuring it in {WORDS[NSUBS]} marketing subreddits from January 1, 2025 to {SWEEP} ({n(TOTAL)} posts), {N_THREADS} coded threads with the measurement problems each raises, {N_QUOTES} supporting quotes checked against the Arctic Shift archive, themes of feedback on Google Search Console’s generative AI report, and the agreement between two AI coding passes.",
             "creator": {"@id": "https://copyfororiginals.com/#org"}, "datePublished": PUB,
             "license": "https://creativecommons.org/licenses/by/4.0/",
             "distribution": [
                 {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": URL + "monthly_counts.csv"},
                 {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": URL + "threads.csv"},
                 {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": URL + "quotes.csv"}]},
            {"@type": "FAQPage", "@id": URL + "#faq", "mainEntity": faq_ld},
        ]}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(SEO_TITLE)}</title>
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
<meta property="og:title" content="{e(TITLE)}">
<meta property="og:description" content="{e(f'Posts about AI search went from {pct(share(FIRST_M, "aeo_posts_broad"))} to {pct(share(LAST_FULL, "aeo_posts_broad"))} of all posts in {WORDS[NSUBS]} marketing subreddits; posts about measuring it rose about {MEAS_FOLD:.0f}-fold. {N_THREADS} threads coded, {N_QUOTES} quotes checked.')}">
<meta property="article:published_time" content="{PUB}">
<meta property="article:modified_time" content="{PUB}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%94%8E%3C/text%3E%3C/svg%3E">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
<link rel="stylesheet" href="../site.css">
<style>
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:28px 0 0}}
.stat{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px}}
.stat b{{display:block;font:700 clamp(30px,6vw,40px)/1 var(--display);letter-spacing:-.03em;font-variant-numeric:tabular-nums;margin-bottom:6px}}
.stat span{{font-size:14.5px;color:var(--muted);line-height:1.4}}
h3 .count{{font-weight:400;color:var(--muted);font-size:.85em}}
blockquote footer{{font-size:13.5px;color:var(--muted);margin-top:6px}}
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
  <ul class="lang-switch" aria-label="Language"><li><a href="../sv/ai-synlighet-matning-reddit-studie/" hreflang="sv" lang="sv">Svenska</a></li><li><span aria-current="true">English</span></li></ul>
</nav>
<div class="wrap">

<nav class="crumbs" aria-label="Breadcrumb"><a href="../">&larr; All tools</a></nav>

<header>
  <p class="kicker"><a href="https://copyfororiginals.com/">Copy for Originals</a> · Original research</p>
  <h1>{e(TITLE)}</h1>
  <p class="lede">{e(LEDE)}</p>
  <p class="byline">By <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a> · Published <time datetime="{PUB}">{PUB_TXT}</time> · <a href="threads.csv">Download the {N_THREADS} coded threads (CSV)</a> · <a href="quotes.csv">the {N_QUOTES} quotes (CSV)</a> · <a href="monthly_counts.csv">the monthly counts (CSV)</a></p>
  <p class="scope"><b>How to read the counts.</b> The threads were coded by AI agents against a written codebook, twice, and the stricter pass is published; the agreement between the two passes is reported below. Every quotation was checked character for character against the Reddit archive. Quotes are shown without usernames. Counts describe the threads we selected, not Reddit as a whole.</p>
  <div class="stats">
    {stat(f"{pct(share(FIRST_M, 'aeo_posts_broad'))} → {pct(share(LAST_FULL, 'aeo_posts_broad'))}", f"share of all posts in {WORDS[NSUBS]} marketing subreddits that mention AI search, January 2025 to September 2026")}
    {stat(f"{MEAS_FOLD:.0f}×", f"growth in the share of posts about measuring AI visibility, from {pct(share(FIRST_M, 'aeo_measurement_posts'), 2)} to {pct(share(LAST_FULL, 'aeo_measurement_posts'), 2)}")}
    {stat(f"{CAT_N[RANKED[0][0]]} of {N_THREADS}", f"threads raised the most common problem: {RANKED[0][1]}")}
    {stat(f"{N_QUOTES} of {N_QUOTES}", "supporting quotes found word for word in the archive")}
  </div>
</header>

<section id="findings">
  <h2>What did the study find?</h2>
  <ol class="check">
    <li><b>The conversation is growing fast.</b> Posts that mention AI search rose from {pct(share(FIRST_M, 'aeo_posts_broad'))} of all posts in January 2025 to {pct(share(LAST_FULL, 'aeo_posts_broad'))} in September 2026, peaking at {pct(share(PEAK_FULL, 'aeo_posts_broad'))} in {MONTHS[int(PEAK_FULL['month'][5:]) - 1]} {PEAK_FULL['month'][:4]}. In the technical SEO forums it is now more than one post in ten.</li>
    <li><b>Measurement is growing faster.</b> Posts about tracking, reporting or attributing AI visibility rose about {MEAS_FOLD:.0f}-fold as a share of all posts, from {pct(share(FIRST_M, 'aeo_measurement_posts'), 2)} to {pct(share(LAST_FULL, 'aeo_measurement_posts'), 2)}.</li>
    <li><b>The most common wall is Google’s own data.</b> {CAT_N['GSC_AI_DATA']} of {N_THREADS} threads struggled with how Search Console handles AI Overviews and AI Mode. The new generative AI report drew praise in {T_PRAISE} threads and the complaint that it has no query data in {T_QUERY}, no clicks in {T_CLICKS}.</li>
    <li><b>The tools are nearly as contested as the gap.</b> {CAT_N['TOOL_COST_ACCURACY']} threads questioned the cost or accuracy of AI visibility trackers: synthetic prompts, API answers that differ from the app, tools that disagree, prices from $99 to $400 a month and up.</li>
    <li><b>There is no data from the assistants themselves.</b> {CAT_N['NO_LLM_DATA']} threads said so outright. {CAT_N['NONDETERMINISM']} described answers that change between runs, and {CAT_N['PROMPT_SELECTION']} debated which prompts to track, with one participant noting that the right choice of prompts can make any dashboard look good.</li>
    <li><b>The number is wanted from above.</b> {CAT_N['CLIENT_PRESSURE']} threads described clients, bosses or boards demanding an AI visibility report; {CAT_N['REVENUE_ROI']} said nobody could tie the visibility to revenue.</li>
    <li><b>Two models, one codebook, a stricter answer.</b> A first coding pass by Claude Sonnet 5.5 judged {FIRST_REL} threads relevant; the published Opus 5.5 pass, told to count only substantive discussion, judged {N_REL}. The two agreed on {min(AGREES):.0f}% to {max(AGREES):.0f}% of threads per problem, and almost every disagreement was the first pass counting something the second did not.</li>
  </ol>
</section>

<section id="growth">
  <h2>How fast is the AI search conversation growing?</h2>
  <p>We pulled every post from {WORDS[NSUBS]} marketing subreddits between January 1, 2025 and {SWEEP} from the Arctic Shift archive, {n(TOTAL)} posts in all, and matched each against a list of terms: AEO, GEO, generative or answer engine, AI Overviews, AI Mode, AI visibility, AI search, AI or LLM traffic, ChatGPT, Perplexity. {n(BROAD)} posts matched, {pct(100 * BROAD / TOTAL)} of the total. A stricter count that drops posts matched only by the name ChatGPT or Perplexity gives {n(CORE)}. Adding a tracking, reporting or attribution term to the strict count gives {n(MEAS)} posts about measurement.</p>
  <p>The shares tell the story better than the counts, because the subreddits themselves shrank and grew over the period, and one of them changed its posting rules in July 2025. In January 2025, one post in {round(100 / share(FIRST_M, 'aeo_posts_broad'))} mentioned AI search. In September 2026, one in {round(100 / share(LAST_FULL, 'aeo_posts_broad'))} did. The measurement share rose from {pct(share(FIRST_M, 'aeo_measurement_posts'), 2)} to {pct(share(LAST_FULL, 'aeo_measurement_posts'), 2)}, which is the {MEAS_FOLD:.0f}-fold figure in the summary.</p>
  {monthly_table()}
  <p>The technical forums lead. In r/TechSEO and r/bigseo more than one post in ten mentions AI search; in r/marketing and r/PPC it is about one in fifty. Measurement follows the same gradient.</p>
  {sub_table()}
</section>

<section id="problems">
  <h2>What can’t marketers measure?</h2>
  <p>Counting posts shows that people are talking. To learn what they are stuck on, we read {N_THREADS} threads with {n(N_COMMENTS)} comments: the {N_TOP60} measurement threads with the most comments (the smallest had {MIN_TOP60_COMMENTS}), every thread since January 2026 that mentioned Search Console near a reference to AI ({N_GSC_SEL}), the {N_PROMPT_SEL} most-discussed threads about choosing prompts, and the {N_HC_SEL} most-discussed threads that mentioned healthcare. Two sets of AI agents coded each thread against the same written list of twelve problems. {N_REL} threads turned out to be about measuring AI visibility at all; the rest were news digests, removed posts or ordinary Search Console questions.</p>
  <p>The table ranks the twelve problems by the number of threads in which someone discussed them in substance. A thread can raise several; the median relevant thread raised {WORDS[MEDIAN_CATS]}.</p>
  {cat_table()}
  <p>What follows is the texture behind the counts: for each problem, how people describe it in their own words. The quotes were chosen to be representative and were checked against the archive; promotional comments were excluded.</p>
  {section_problems()}
</section>

<section id="gsc">
  <h2>What do practitioners say about Search Console’s generative AI report?</h2>
  {section_gsc()}
</section>

<section id="health">
  <h2>Who is talking about healthcare?</h2>
  {section_health()}
</section>

<section id="coding">
  <h2>How much did the coding depend on the coder?</h2>
  <p>Counts like these depend on judgment, and we wanted to know how much. So the same {N_THREADS} threads were coded twice against the same codebook. The first pass used Claude Sonnet 5.5 agents. The second, which is the one published above, used Claude Opus 5.5 agents with one added instruction: count a problem only when a participant discusses it in substance, not when a keyword passes by.</p>
  <p>The two passes agreed on {min(AGREES):.0f}% to {max(AGREES):.0f}% of threads per problem, with Cohen’s kappa between {min(KAPPAS):.2f} and {max(KAPPAS):.2f}. The disagreements ran one way. Across the twelve problems, the first pass counted {FIRST_ONLY} thread-problem pairs that the second did not, and the second counted {PUB_ONLY} that the first did not. The first pass also judged {FIRST_REL} threads relevant against {N_REL}. The ranking of problems is nearly the same in both passes; the counts in the first are {round(100 * (sum(int(AG[c]['first_pass_threads']) for c, _, _ in CATS) / sum(int(AG[c]['published_threads']) for c, _, _ in CATS) - 1))}% higher overall. Readers who want the looser count can rebuild it from <a href="first-pass/threads.csv">first-pass/threads.csv</a>.</p>
  {agree_table()}
  <p>Every quote both passes produced was checked by script against the archived post or comment: all {N_QUOTES} quotes from the published pass matched exactly, as did all 1,204 from the first.</p>
</section>

<section id="method">
  <h2>How was the study done?</h2>
  <ol class="check">
    <li><b>Source:</b> the Arctic Shift archive of Reddit, read through its public API on {SWEEP} from an ordinary Swedish home connection. Reddit itself blocks automated reading. The archive’s own monthly counts were compared with ours for every subreddit and month, and they match.</li>
    <li><b>Scope:</b> every post from January 1, 2025 to {SWEEP} in r/SEO, r/bigseo, r/TechSEO, r/DigitalMarketing, r/marketing, r/PPC and r/agency: {n(TOTAL)} posts. r/GoogleSearchConsole was also swept and had one post in the period.</li>
    <li><b>Term matching:</b> title and body, case-insensitive, against the term list above. “GEO” counts only in capitals, or in lower case when the post also mentions AI or LLMs and is not about geographic targeting, because “geo” is everyday advertising shorthand. In the forums where moderators remove most post bodies (74% in r/SEO, 61% in r/marketing), removed posts were matched on title alone.</li>
    <li><b>Thread selection:</b> four rules, described above, chose {N_THREADS} threads. Comments were pulled for each: {n(N_COMMENTS)} in all.</li>
    <li><b>Coding:</b> a written codebook with twelve problems, a relevance flag, a healthcare flag and a list of specific points about Search Console’s generative AI report (<a href="method/CODEBOOK.txt">method/CODEBOOK.txt</a>). Each thread was coded by a Claude Sonnet 5.5 agent and, independently and without sight of the first pass, by a Claude Opus 5.5 agent told to count only substantive discussion. The Opus pass is published. No person coded.</li>
    <li><b>Quote check:</b> every quote the coders supplied was required to be an exact, contiguous substring of one archived post or comment. A script checked all of them. Quotes from comments the coders flagged as promotional are excluded from this page.</li>
    <li><b>Themes:</b> the coders’ points about the generative AI report were grouped into nine themes by keyword rules (<a href="method/gsc_themes.py">method/gsc_themes.py</a>), counting distinct threads.</li>
    <li><b>Agreement:</b> percent agreement and Cohen’s kappa between the two passes, per problem, over all {N_THREADS} threads.</li>
  </ol>
  <p>The data files are <a href="monthly_counts.csv">monthly_counts.csv</a>, <a href="threads.csv">threads.csv</a> (one row per coded thread), <a href="quotes.csv">quotes.csv</a> (one row per checked quote, with its permalink), <a href="gsc_report_themes.csv">gsc_report_themes.csv</a>, <a href="agreement.csv">agreement.csv</a> and <a href="first-pass/threads.csv">first-pass/threads.csv</a>. The scripts that swept the archive, filtered, pulled comments, batched threads for coding, verified quotes and built this page are in <a href="method/">method/</a>. The raw archive pull (about 130 MB) is not published; the scripts rebuild it.</p>
</section>

<section id="limits">
  <h2>Limitations</h2>
  <ul>
    <li><b>The threads were selected, not sampled.</b> Long threads and threads mentioning Search Console near AI were favoured, so the counts describe those {N_THREADS} threads, not Reddit as a whole. Long threads also collect more problems.</li>
    <li><b>The coding is by AI agents.</b> Two passes with the same codebook differed by {round(100 * (sum(int(AG[c]['first_pass_threads']) for c, _, _ in CATS) / sum(int(AG[c]['published_threads']) for c, _, _ in CATS) - 1))}% in total count, almost all in one direction. The published counts are the stricter ones. No person coded a sample for comparison.</li>
    <li><b>The term list defines the trend.</b> A post about “Google’s AI answers” without any listed term is not counted. The share figures are a floor.</li>
    <li><b>Most post bodies are gone.</b> Moderators had removed the body of 44% to 74% of posts in six of the seven subreddits by the time of the sweep. Those posts were matched on title only, which also lowers the shares.</li>
    <li><b>Reddit is not the market.</b> These forums skew toward SEO practitioners and agencies, and undisclosed promotion is common. Flagged promotional quotes were excluded; unflagged promotion surely remains.</li>
    <li><b>“Just SEO” and the format claims are the most interpretive codes,</b> and the two passes agreed on them least often after the revenue code.</li>
    <li><b>The subreddits changed under us.</b> r/marketing’s daily post count fell by about four fifths on July 25, 2025, and r/TechSEO’s roughly doubled from February 2026. Shares normalise for this; counts do not.</li>
  </ul>
</section>

<section id="faq">
  <h2>FAQ</h2>
{faq_html}
</section>

<section id="sources">
  <h2>Sources</h2>
  <p>Reddit threads are cited by permalink under each quote and in <a href="quotes.csv">quotes.csv</a>. The archive and the Google, Bing and CMA documents below were read on October 15, 2026.</p>
  <ul class="sources">
    <li>Arctic Shift, public archive of Reddit posts and comments. <a href="https://arctic-shift.photon-reddit.com/" rel="noopener">arctic-shift.photon-reddit.com</a></li>
    <li>Google Search Central, “Introducing the Search Generative AI performance reports,” June 3, 2026, with the note that the reports reached all sites on August 31, 2026. <a href="https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports" rel="noopener">developers.google.com</a></li>
    <li>Google Search Console Help, “Generative AI performance report (Search)” (impressions by page, country, device and date; no query dimension). <a href="https://support.google.com/webmasters/answer/16984139" rel="noopener">support.google.com</a></li>
    <li>Google Search Console Help, “Performance report: AI features” (one position for every link in an AI Overview; an AI Mode follow-up counts as a new query). <a href="https://support.google.com/webmasters/answer/7042828" rel="noopener">support.google.com</a></li>
    <li>Bing Webmaster Blog, “Introducing AI Performance in Bing Webmaster Tools (Public Preview),” February 10, 2026 (grounding queries as “a sample of overall citation activity”). <a href="https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview" rel="noopener">blogs.bing.com</a></li>
    <li>Conductor, “Health Care Industry: 2026 AEO / GEO Benchmarks” (AI Overviews on 48.7% of page-one health queries, the highest of ten industries; news articles the most-cited page type), last updated April 14, 2026. Conductor sells AI visibility software. <a href="https://www.conductor.com/academy/health-care-aeo-geo-benchmarks/" rel="noopener">conductor.com</a></li>
    <li>Yext, “86% of AI Citations Come from Brand-Managed Sources” (6.8 million citations across ChatGPT, Gemini and Perplexity; healthcare listings 52.6%), October 9, 2025. Yext sells listings management. <a href="https://yext.com/about/news-media/ai-citations-release" rel="noopener">yext.com</a></li>
    <li>Competition and Markets Authority, Publisher conduct requirements: interpretative notes and notice, June 3, 2026. <a href="https://assets.publishing.service.gov.uk/media/6a1ec397050971fbebf3bd42/_Publisher_CR_Interpretative_Notes_.pdf" rel="noopener">Interpretative notes (PDF)</a>, <a href="https://assets.publishing.service.gov.uk/media/6a1ec73a59fb7a60f827f64e/Publisher_CR_Notice.pdf" rel="noopener">Notice (PDF)</a></li>
  </ul>
  <p>How to cite: Copy for Originals, “{e(TITLE)},” {PUB_TXT}, {URL}. Data licensed CC BY 4.0.</p>
</section>

<footer>
  <p>Static page. No scripts, no tracking. Made by <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a>.</p>
</footer>
</div>
</body>
</html>
"""

out = page()
with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
    fh.write(out)
print("wrote index.html", len(out), "bytes;", N_THREADS, "threads,", N_REL, "relevant,", N_QUOTES, "quotes")
