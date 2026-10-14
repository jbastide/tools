"""Build the English page and its Swedish twin from data.csv. Every number comes from stats.compute() and compare().
Usage: python3 -I build_pages.py <data.csv> <english index.html> <swedish index.html>"""
import csv, datetime, html, importlib.util, json, os, sys

spec = importlib.util.spec_from_file_location("stats", os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.py"))
stats = importlib.util.module_from_spec(spec); spec.loader.exec_module(stats)

BASE = "https://tools.copyfororiginals.com/"
EN_SLUG, SV_SLUG = "law-firm-websites-ai-crawlers-study/", "sv/advokatbyraers-webbplatser-ai-sokrobotar-studie/"
EN_URL, SV_URL = BASE + EN_SLUG, BASE + SV_SLUG
PUB, UPD = datetime.date(2026, 10, 13), datetime.date(2026, 10, 14)
VERSION = "2"
AI3, CTRL = stats.AI3, stats.CTRL
LABEL = {"gptbot": "GPTBot", "claudebot": "ClaudeBot", "perplexitybot": "PerplexityBot", "googlebot": "Googlebot", "bingbot": "Bingbot"}
SV_MONTHS = ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"]


def d_en(d): return f"{d.strftime('%B')} {d.day}, {d.year}"
def d_sv(d): return f"{d.day} {SV_MONTHS[d.month - 1]} {d.year}"
def iso(s): return datetime.date.fromisoformat(s)
def pct_en(a, b): return f"{int(a * 100 / b + 0.5)}%"
def pct_sv(a, b): return f"{int(a * 100 / b + 0.5)}&nbsp;%"
def pct_sv_t(a, b): return f"{int(a * 100 / b + 0.5)} %"
def kb_en(n): return f"{n / 1000:.1f} KB" if n < 1_000_000 else f"about {n / 1_000_000:.0f} MB"
def kb_sv(n): return (f"{n / 1000:.1f} KB" if n < 1_000_000 else f"omkring {n / 1_000_000:.0f} MB").replace(".", ",")
def join(items, word): return items[0] if len(items) == 1 else ", ".join(items[:-1]) + f" {word} " + items[-1]
def cap(s): return s[0].upper() + s[1:]


def compare(main_csv):
    """Second location: the Chicago runs are stored in the chicago_* columns of the same CSV."""
    R = list(csv.DictReader(open(main_csv, encoding="utf-8")))
    refset = lambda r, pre: {k for k in AI3 if r[pre + "request_as_" + k].startswith("refused")}
    X = {}
    cs = [r for r in R if r["chicago_browser_style_request"] == "served"]
    X["M"] = len(cs); X["br"] = sum(r["chicago_browser_style_request"].startswith("refused") for r in R)
    ref = [r for r in cs if refset(r, "chicago_")]; X["N"] = len(ref)
    X["K"] = sum(all(r["chicago_request_as_" + k] == "served" for k in CTRL) for r in ref)
    both = [r for r in R if r["browser_style_request"] == "served" and r["chicago_browser_style_request"] == "served"]
    X["both"] = len(both); X["same"] = sum(refset(r, "") == refset(r, "chicago_") for r in both)
    X["refboth"] = sum(bool(refset(r, "") and refset(r, "chicago_")) for r in both)
    X["names"] = {k: sum(r["chicago_request_as_" + k].startswith("refused") for r in cs) for k in AI3 + CTRL}
    return X


def common(S):
    nm = S["names"]; g = lambda k, o: nm[k].get(o, 0)
    order = sorted(AI3, key=lambda k: (-g(k, "refused"), k))
    return nm, g, order


def ld_graph(lang, url, headline, desc, ds_name, ds_desc, faq, crumbs):
    org = {"@id": "https://copyfororiginals.com/#org"}
    art = {"@type": "Article", "@id": url + "#article", "headline": headline, "description": desc, "url": url, "inLanguage": lang,
           "datePublished": PUB.isoformat(), "dateModified": UPD.isoformat(), "author": org, "publisher": org,
           "about": ["robots.txt", "llms.txt", "AI crawlers", "Law firm marketing"] if lang == "en" else ["robots.txt", "llms.txt", "AI-sökrobotar", "Marknadsföring för advokatbyråer"],
           "isBasedOn": {"@id": url + "#data"},
           "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}}
    ds = {"@type": "Dataset", "@id": url + "#data", "name": ds_name, "description": ds_desc, "creator": org, "datePublished": PUB.isoformat(),
          "license": "https://creativecommons.org/licenses/by/4.0/",
          "distribution": {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": EN_URL + "data.csv"}}
    fq = {"@type": "FAQPage", "@id": url + "#faq",
          "mainEntity": [{"@type": "Question", "name": html.unescape(q), "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a)}} for q, a in faq]}
    if lang == "sv": ds["inLanguage"] = "sv"; fq["inLanguage"] = "sv"
    return json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": "https://copyfororiginals.com/#org", "name": "Copy for Originals", "url": "https://copyfororiginals.com"}, art, ds, fq]},
        ensure_ascii=False, indent=2)


STYLE = """<style>
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:28px 0 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px}
.stat b{display:block;font:700 clamp(30px,6vw,40px)/1 var(--display);letter-spacing:-.03em;font-variant-numeric:tabular-nums;margin-bottom:6px}
.stat span{font-size:14.5px;color:var(--muted);line-height:1.4}
</style>"""
ICON = """<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%A4%96%3C/text%3E%3C/svg%3E">"""
HREFLANG = f"""<link rel="alternate" hreflang="sv" href="{SV_URL}">
<link rel="alternate" hreflang="en" href="{EN_URL}">
<link rel="alternate" hreflang="x-default" href="{EN_URL}">"""


def build_en(S, X):
    n, M, N, K = S["n"], S["base_served"], S["ai_refusers"], S["ctrl_both_served"]
    nm, g, order = common(S)
    rgo, rbi = g("googlebot", "refused"), g("bingbot", "refused")
    refused_list = f"{g(order[0], 'refused')} refused {LABEL[order[0]]}, {g(order[1], 'refused')} refused {LABEL[order[1]]} and {g(order[2], 'refused')} refused {LABEL[order[2]]}"
    la, ly, lr, ln, lu = S["llms_answered"], S["llms_yes"], S["llms_robots_syntax"], S["llms_no"], S["llms_unreadable"]
    gen = S["llms_generators"]; yoast = gen.get("Yoast SEO", 0)
    gen_items = [f"Yoast SEO in {yoast}"] + [f"{k} in {v}" for k, v in sorted(gen.items(), key=lambda x: (-x[1], x[0])) if k not in ("not stated", "Yoast SEO")]
    codes = S["refuser_codes"]
    code_txt = f"403 “Forbidden” responses at {codes.get('403', 0)} sites and 429 “Too Many Requests” at {codes.get('429', 0)}" + (f", and a mix of both at {codes['403+429']}" if codes.get("403+429") else "")
    left, br = S["base_left_out"], S["base_refused"]; other = left - br
    dl = S["disallow_lists"]; DATES = "October 13 and 14, 2026"
    use = {"GPTBot": "OpenAI, training", "OAI-SearchBot": "OpenAI, ChatGPT search", "ChatGPT-User": "OpenAI, fetches for a user’s question",
           "ClaudeBot": "Anthropic, training", "Claude-SearchBot": "Anthropic, search", "Claude-User": "Anthropic, fetches for a user’s question",
           "PerplexityBot": "Perplexity, search", "Google-Extended": "Google, a robots.txt token for Gemini training and grounding", "CCBot": "Common Crawl, an open web archive"}
    robots_rows = "\n".join(f'      <tr><th scope="row">{t["name"]}</th><td>{use[t["name"]]}</td><td class="n">{t["named"]}</td><td class="n">{t["disallowed"]}</td></tr>' for t in S["robots_table"])
    name_rows = "\n".join(f'      <tr><th scope="row">{LABEL[k]}</th><td>{"AI crawler" if k in AI3 else "Search crawler (control)"}</td><td class="n">{g(k, "served")}</td>'
                          f'<td class="n">{g(k, "refused")} ({pct_en(g(k, "refused"), M)})</td><td class="n">{g(k, "mixed")}</td></tr>' for k in AI3 + CTRL)
    bo = S["base_other"]
    other_txt = (f", and {other} couldn’t be reached" if set(bo) == {"unreachable"} else f", and {other} could not be reached or gave mixed answers") if other else ""
    title = f"Do Law Firm Websites Block AI Crawlers? robots.txt, Firewalls and llms.txt at {n} Chicago Injury Firms (2026 Study)"
    lede = (f"Copy for Originals checked the websites of {n} Chicago personal injury law firms on {DATES}. Only {S['robots_disallow_any']} disallow an AI crawler in robots.txt. "
            f"But {N} of the {M} sites that could be tested refused a request carrying the name GPTBot, ClaudeBot or PerplexityBot every time, "
            f"and {K} of those {N} served the same request under Googlebot’s and Bingbot’s names.")
    desc = (f"Copy for Originals checked {n} Chicago personal injury law firm websites on {DATES}. Only {S['robots_disallow_any']} disallow an AI crawler in robots.txt, "
            f"but {N} of {M} testable sites refused a request carrying the name GPTBot, ClaudeBot or PerplexityBot in all five runs, and {K} of those {N} served the same request "
            f"under Googlebot’s and Bingbot’s names. {ly} of {la} publish an llms.txt file. Data included.")
    faq = [
        ("Do law firm websites block AI crawlers like GPTBot and ClaudeBot?",
         f"Few do it in robots.txt, and more do it at the server. In a Copy for Originals study of {n} Chicago personal injury law firm websites on {DATES}, "
         f"{S['robots_disallow_any']} disallowed at least one AI crawler in robots.txt. Of the {M} sites that could be tested at the server, {N} refused a request carrying the name "
         f"GPTBot, ClaudeBot or PerplexityBot in all five runs: {refused_list}."),
        ("Do websites that refuse AI crawlers also refuse Googlebot?",
         f"Mostly not. In the Copy for Originals study, {K} of the {N} law firm websites that refused a request carrying an AI crawler’s name served the same request every time "
         f"when it carried Googlebot’s or Bingbot’s name. Across all {M} sites tested, {rgo} refused Googlebot’s name and {rbi} refused Bingbot’s name."),
        ("Can a website block AI crawlers without saying so in robots.txt?",
         f"Yes. A firewall, a hosting company or a security plugin can refuse a crawler before the website itself answers, and robots.txt does not change. In the Copy for Originals "
         f"study, {S['refusers_no_robots_rule']} of the {N} law firm websites that refused a request carrying an AI crawler’s name had no robots.txt rule against that crawler, and "
         f"{S['refusers_named_allowed']} of them named the refused crawler in robots.txt without disallowing it."),
        ("How many law firm websites have an llms.txt file?",
         f"{ly} of {la}, or {pct_en(ly, la)}, in the Copy for Originals study of Chicago personal injury law firm websites on {DATES}. Another {lr} of the {la} answered the llms.txt address "
         f"with a file written in robots.txt syntax, which the llms.txt proposal does not define, and {ln} had no file. Of the {ly} files, {yoast} said they were generated by Yoast SEO."),
    ]
    ld = ld_graph("en", EN_URL, f"Do law firm websites block AI crawlers? robots.txt, firewalls and llms.txt at {n} Chicago injury firms", desc,
                  f"AI crawler access at {n} Chicago personal injury law firm websites (Copy for Originals, 2026)",
                  (f"One row per website for {n} Chicago personal injury law firms, checked {DATES}: where the robots.txt file was read, which AI crawlers it names and disallows, "
                   f"any Content-Signal line, whether an llms.txt file exists and what generated it, and how the homepage answered a browser-style request and requests carrying "
                   f"the names GPTBot, ClaudeBot, PerplexityBot, Googlebot and Bingbot in five runs from Sweden and three runs from Chicago."),
                  faq, [("Tools", BASE), ("Law firm websites and AI crawlers study", EN_URL)])
    faq_html = "\n".join(f"  <h3>{q}</h3>\n  <p>{a}</p>" for q, a in faq)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<meta name="author" content="Copy for Originals">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="index,follow,max-snippet:-1">
<link rel="canonical" href="{EN_URL}">
{HREFLANG}
<meta property="og:type" content="article">
<meta property="og:url" content="{EN_URL}">
<meta property="og:site_name" content="Copy for Originals">
<meta property="og:title" content="Do law firm websites block AI crawlers? A study of {n} Chicago injury firms">
<meta property="og:description" content="{S['robots_disallow_any']} of {n} block an AI crawler in robots.txt. {N} of {M} refuse one at the server, and {K} of those serve Googlebot’s name. {ly} of {la} publish an llms.txt file.">
<meta property="article:published_time" content="{PUB.isoformat()}">
<meta property="article:modified_time" content="{UPD.isoformat()}">
{ICON}
<script type="application/ld+json">
{ld}
</script>
<link rel="stylesheet" href="../site.css">
{STYLE}
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
  <ul class="lang-switch" aria-label="Language"><li><a href="../{SV_SLUG}" hreflang="sv" lang="sv">Svenska</a></li><li><span aria-current="true">English</span></li></ul>
</nav>
<div class="wrap">

<nav class="crumbs" aria-label="Breadcrumb"><a href="../">&larr; All tools</a></nav>

<header>
  <p class="kicker"><a href="https://copyfororiginals.com/">Copy for Originals</a> · Original research</p>
  <h1>Do law firm websites block AI crawlers?</h1>
  <p class="lede">{lede}</p>
  <p class="byline">By <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a> · Published <time datetime="{PUB.isoformat()}">{d_en(PUB)}</time> · Last updated <time datetime="{UPD.isoformat()}">{d_en(UPD)}</time> · Version {VERSION} · <a href="data.csv">Download the data (CSV)</a></p>
  <p class="scope"><b>Educational only, not legal advice.</b> This study describes public files and server responses. Whether a firm should let AI crawlers read its site is the firm’s own decision.</p>
  <div class="stats">
    <div class="stat"><b>{S['robots_disallow_any']} of {n}</b><span>disallow at least one AI crawler in robots.txt</span></div>
    <div class="stat"><b>{N} of {M}</b><span>refused a request carrying an AI crawler’s name, in all five runs</span></div>
    <div class="stat"><b>{K} of {N}</b><span>of those served the same request under Googlebot’s and Bingbot’s names</span></div>
    <div class="stat"><b>{ly} of {la}</b><span>publish an llms.txt file</span></div>
  </div>
</header>

<section id="findings">
  <h2>What did the study find?</h2>
  <ol class="check">
    <li><b>Almost no firm blocks AI crawlers in robots.txt.</b> {S['robots_named_any']} of {n} robots.txt files name an AI crawler at all, and {S['robots_disallow_any']} disallow one. Only {S['robots_disallow_gpt_and_claude']} disallows both GPTBot and ClaudeBot.</li>
    <li><b>The refusals happen at the server, where robots.txt doesn’t show them.</b> {N} of {M} sites answered a browser-style request but refused a request carrying the name GPTBot, ClaudeBot or PerplexityBot every time. {S['refusers_no_robots_rule']} of the {N} have no robots.txt rule against the crawler they refused.</li>
    <li><b>The refusals are aimed at AI crawlers, not at crawlers in general.</b> {K} of the {N} sites served the same request every time when it carried Googlebot’s or Bingbot’s name.</li>
    <li><b>{LABEL[order[0]]}’s name was refused most often.</b> {cap(refused_list)}.</li>
    <li><b>llms.txt is common, and often automatic.</b> {ly} of {la} sites publish one. {S['llms_gen_stated']} of the {ly} say which plugin wrote the file, and {yoast} of those say Yoast SEO. Another {lr} sites answer the llms.txt address with robots.txt-style rules that the llms.txt proposal doesn’t define.</li>
  </ol>
</section>

<section id="robots">
  <h2>How many law firm websites block AI crawlers in robots.txt?</h2>
  <p>{S['robots_disallow_any']} of {n}. Each of the {n} sites has a robots.txt file, and {S['robots_no_mention']} of them don’t mention an AI crawler. Of the {S['robots_named_any']} that do, {S['robots_named_not_disallowing']} name crawlers without disallowing any of them.</p>
  <div class="tablewrap">
  <table>
    <caption>AI crawlers named and disallowed in the robots.txt files of {n} Chicago personal injury law firm websites (Copy for Originals, {d_en(PUB)})</caption>
    <thead><tr><th scope="col">Crawler name</th><th scope="col">Company and stated use</th><th scope="col" class="n">Sites naming it</th><th scope="col" class="n">Sites disallowing it</th></tr></thead>
    <tbody>
{robots_rows}
    </tbody>
  </table>
  </div>
  <p>“Disallowing” means the group of rules that names the crawler contains <code>Disallow: /</code> with no <code>Allow: /</code>. No site disallowed every crawler with a wildcard rule.</p>
  <p>The three firms that disallow an AI crawler did it three different ways:</p>
  <ul>
    <li><b>One disallows {len(dl[0][1])} of the 15 AI crawler names the study checked,</b> including GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot and PerplexityBot. The file gives the reason in a comment: “Disallow AI training crawlers (added 2026-04-24 to stop CPU saturation).”</li>
    <li><b>One disallows ClaudeBot and seven other names</b> (anthropic-ai, Google-Extended, Applebot-Extended, CCBot, Bytespider, meta-externalagent and Amazonbot) but has no rule for GPTBot.</li>
    <li><b>One disallows GPTBot and meta-externalagent</b> and lets ClaudeBot and OAI-SearchBot in under ordinary rules.</li>
  </ul>
  <p>{S['signal_total']} of the {S['robots_same_day']} files read on {d_en(PUB)} carry a <code>Content-Signal</code> line, the format Cloudflare published on September 24, 2025. {S['signal_train_yes']} say <code>search=yes, ai-input=yes, ai-train=yes</code>, and {S['signal_train_no']} says <code>search=yes, ai-input=yes, ai-train=no</code>. Three of the files that say yes to training are identical apart from the site’s address, which points to one website platform writing the line for its law firm customers.</p>
</section>

<section id="server">
  <h2>Do law firm websites block AI crawlers at the server instead?</h2>
  <p>Yes, more often than in robots.txt. {N} of {M} sites ({pct_en(N, M)}) served the homepage to a browser-style request but refused the same request when it carried an AI crawler’s name. Each site was asked five times per name, at least three minutes apart and in a different order each time, and “refused” here means refused all five times.</p>
  <div class="tablewrap">
  <table class="wide">
    <caption>How {M} law firm homepages answered a request carrying a crawler’s name, five runs (Copy for Originals, {d_en(UPD)})</caption>
    <thead><tr><th scope="col">Name in the request</th><th scope="col">Kind</th><th scope="col" class="n">Served all 5 times</th><th scope="col" class="n">Refused all 5 times</th><th scope="col" class="n">Mixed</th></tr></thead>
    <tbody>
{name_rows}
    </tbody>
  </table>
  </div>
  <p>{S['served_all_five_names']} of the {M} sites served all five names every time. {N} refused at least one AI crawler’s name every time. The refusals were {code_txt}. {S['refusers_cloudflare']} of the {N} sites sit behind Cloudflare.</p>
  <h3>Do these sites refuse Googlebot’s name too?</h3>
  <p>Mostly not. {K} of the {N} sites that refused an AI crawler’s name served the same request every time when it carried Googlebot’s or Bingbot’s name. {S['ctrl_any_refused']} refused a search crawler’s name as well{f", and {S['ctrl_unclear']} gave mixed answers" if S['ctrl_unclear'] else ""}.</p>
  <p>This matters for reading the result. A site that checks whether a visitor really is the crawler it claims to be would turn away a request falsely carrying Googlebot’s name. {K} sites did not, so an identity check is an unlikely explanation there. Those sites treat an AI crawler’s name as a reason to refuse.</p>
  <p>Across all {M} sites, {rgo} refused Googlebot’s name every time and {rbi} refused Bingbot’s. {(f"{S['bing_only_refusers']} sites refused Bingbot’s name while serving the three AI names and Googlebot’s." if S['bing_only_refusers'] == S['ctrl_only_refusers'] else f"{S['ctrl_only_refusers']} sites refused a search crawler’s name while serving all three AI names.")}</p>
  <h3>Does robots.txt show these server blocks?</h3>
  <p>No. Only {S['refusers_robots_match']} of the {N} sites has a robots.txt rule against a crawler it refused. {S['refusers_no_ai_rule_at_all']} have no AI crawler rule at all. {S['refusers_named_allowed']} name the refused crawler in robots.txt without disallowing it, so the file reads as an invitation and the server turns the visitor away.</p>
  <p>It also runs the other way. {S['claude_disallowed_but_served']} sites disallow ClaudeBot in robots.txt and served the ClaudeBot-named request every time. RFC 9309, the robots.txt standard, says its rules “are not a form of access authorization.” The file states what the site asks of a crawler, and the crawler decides whether to comply.</p>
  <h3>Does the result hold from a US address?</h3>
  <p>Largely, yes. Three more runs on {d_en(PUB)} went out through a VPN exit in Chicago with the same six requests. {X['M']} sites could be tested from there and {X['both']} from both places. {X['same']} of those {X['both']} landed in the same place from both: refusing the same AI crawler names, or none. {X['refboth']} refused at least one AI crawler’s name from both places. From Chicago, {X['K']} of the {X['N']} sites that refused an AI crawler’s name served Googlebot’s and Bingbot’s names every time.</p>
  <h3>What does a refusal mean for the real crawler?</h3>
  <p>It doesn’t prove the real crawler is refused. The study’s requests came from ordinary internet connections, not from OpenAI’s, Anthropic’s or Perplexity’s own addresses. A refusal in this table means the site treats the crawler’s name differently from a browser, and the Googlebot comparison shows that at most of these sites the name is what triggers it. Only the site’s own server logs show what the real crawler receives.</p>
  <h3>What about the {left} sites left out of this test?</h3>
  <p>{br} sites refused the browser-style request in every run{other_txt}, so there was nothing to compare against. Most of the {br} run bot protection that turned away a script calling itself a browser: a Cloudflare challenge page at some, a plain 403 at others.</p>
  <p>{S['br_served_gptbot']} of those {br} served the page when the same request carried the name GPTBot. {S['br_served_all_ai']} served all three AI names. {S['br_served_gptbot_only']} served GPTBot’s name and refused ClaudeBot’s and PerplexityBot’s. On these sites a crawler’s name alone was enough to get past a block that stopped an ordinary request.</p>
</section>

<section id="llms-txt">
  <h2>How many law firm websites have an llms.txt file?</h2>
  <p>{ly} of {la}, or {pct_en(ly, la)}. An llms.txt file is a markdown file at the root of a site, proposed on September 3, 2024 to help AI tools use the site.</p>
  <div class="tablewrap">
  <table>
    <caption>What {la} law firm websites returned at /llms.txt (Copy for Originals, {d_en(PUB)})</caption>
    <thead><tr><th scope="col">Result</th><th scope="col" class="n">Sites</th></tr></thead>
    <tbody>
      <tr><th scope="row">A markdown llms.txt file</th><td class="n">{ly} ({pct_en(ly, la)})</td></tr>
      <tr><th scope="row">A file written in robots.txt syntax</th><td class="n">{lr} ({pct_en(lr, la)})</td></tr>
      <tr><th scope="row">No file</th><td class="n">{ln} ({pct_en(ln, la)})</td></tr>
    </tbody>
  </table>
  </div>
  <p>{lu} of the {n} sites didn’t give a readable answer for this address and are left out.</p>
  <p><b>Who wrote the files.</b> {S['llms_gen_stated']} of the {ly} files name the software that generated them: {join(gen_items, 'and')}. Yoast says its file is “generated and refreshed automatically” once the feature is switched on. The other {gen.get('not stated', 0)} files don’t say how they were made.</p>
  <p><b>How big they are.</b> Among the {S['llms_sizes_n']} files read directly, the median is about {kb_en(S['llms_size_median'])} and the smallest is {kb_en(S['llms_size_min'])}. {S['llms_over_50k']} files are over 50 KB, and the largest is {kb_en(S['llms_max'])}.</p>
  <p><b>The robots.txt-style files.</b> {lr} sites answer the llms.txt address with lines such as <code>User-agent: *</code> and <code>Allow: /</code>. Six of them serve the identical 65-byte file, which includes the line <code>Disallow-Training: /</code>. The llms.txt proposal describes a markdown file with a title and links. It doesn’t define access rules, so nothing in the proposal says a crawler should act on these lines.</p>
</section>

<section id="check-your-site">
  <h2>How can a law firm check whether its own website blocks AI crawlers?</h2>
  <ol class="check">
    <li><b>Read your robots.txt.</b> Open <code>yourfirm.com/robots.txt</code> and search for GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot and PerplexityBot. A <code>User-agent</code> line naming one of them, followed by <code>Disallow: /</code>, asks that crawler to stay out.</li>
    <li><b>Ask about the firewall.</b> Ask whoever runs your hosting, your Cloudflare account or your security plugin whether a bot rule refuses AI crawlers. {S['refusers_no_robots_rule']} of the {N} refusals in this study don’t appear in robots.txt.</li>
    <li><b>Ask for the server logs.</b> Ask for log lines containing those crawler names and the status code each one got. A 200 means the crawler received the page. A 403 or 429 means it didn’t. This is the only check that sees the real crawler.</li>
    <li><b>Decide training and search separately.</b> OpenAI says GPTBot crawls content that may be used to train its models and OAI-SearchBot surfaces websites in ChatGPT’s search features. Anthropic says ClaudeBot collects content that could contribute to training and Claude-SearchBot improves search results. A firm can refuse one and allow the other.</li>
    <li><b>Open your llms.txt.</b> If <code>yourfirm.com/llms.txt</code> exists, it should be markdown that starts with a <code>#</code> title and lists your pages. If it starts with <code>User-agent</code>, it isn’t in the format the proposal describes.</li>
  </ol>
  <p>For what answer engines do with a page once they can read it, see <a href="../rag-friendly-content/">how to write content that LLMs retrieve and cite</a>. The firms in this study come from the <a href="../chicago-personal-injury-lead-gen-study/">Chicago personal injury lead generation study</a>.</p>
</section>

<section id="method">
  <h2>How was the study done?</h2>
  <ol class="check">
    <li><b>Sample:</b> the {n} websites listed for Chicago personal injury firms in version 4 of the Copy for Originals Chicago study.</li>
    <li><b>robots.txt and llms.txt:</b> each file was requested on {d_en(PUB)} with a Chrome-style user agent. {S['robots_live']} robots.txt files were read that way. {S['robots_second'] + S['robots_us_exit']} more were refused and then read the same day by another route: {S['robots_second']} through a web fetch service and {S['robots_us_exit']} through the Chicago address described below. The last {S['robots_archived']} were read from the most recent Internet Archive copy, captured between {d_en(iso(S['archive_first']))} and {d_en(iso(S['archive_last']))}; none of those {S['robots_archived']} names an AI crawler. {S['llms_second'] + S['llms_us_exit']} llms.txt answers came by the same two routes.</li>
    <li><b>Reading the rules:</b> rules were grouped by <code>User-agent</code> line as RFC 9309 describes. A crawler counts as disallowed when a group naming it contains <code>Disallow: /</code> or <code>Disallow: /*</code> and no <code>Allow: /</code>. Fifteen AI crawler names were checked; the table shows nine.</li>
    <li><b>Server test:</b> each homepage was requested with a Chrome-style user agent and with user agents containing <code>GPTBot/1.4</code>, <code>ClaudeBot/1.0</code>, <code>PerplexityBot/1.0</code>, <code>Googlebot/2.1</code> and <code>bingbot/2.0</code>. There were five runs on {d_en(UPD)} from one home internet connection in Sweden, at least three minutes apart, with the six requests in a different order each run. The exit address was checked before and after every run. A site counts as testable when the browser-style request returned 200 in all five runs ({M} sites). A name counts as refused when it got a 403 or 429 in all five runs, and as mixed when the runs disagreed.</li>
    <li><b>Second location:</b> three runs with the same six requests on {d_en(PUB)} through a commercial VPN exit in Chicago. They are reported separately and are not part of the {M}-site table.</li>
    <li><b>llms.txt:</b> a 200 response counts as a file when it isn’t an HTML page. Files starting with <code>User-agent</code> were counted separately.</li>
  </ol>
  <p>Every site and every response code is in the <a href="data.csv">data file</a>, and the collection scripts are in the <a href="https://github.com/jbastide/tools/tree/main/law-firm-websites-ai-crawlers-study/method" rel="noopener">method folder on GitHub</a>.</p>
</section>

<section id="limits">
  <h2>Limitations</h2>
  <ul>
    <li><b>The test request is not the real crawler.</b> It carried the crawler’s name from an ordinary connection. The Googlebot and Bingbot comparison makes an identity check unlikely at {K} of the {N} refusing sites, but only server logs settle it.</li>
    <li><b>{left} sites could not be tested at the server.</b> {br} refused the browser-style request in every run{other_txt}. From the Chicago address {X['br']} sites refused it, so a US address of that kind did not help. A US home connection is untested.</li>
    <li><b>One city, one practice area, two days.</b> {n} Chicago personal injury firms on {DATES}. Treat percentages as directional.</li>
    <li><b>{S['robots_archived']} robots.txt files are archive copies,</b> the oldest from {d_en(iso(S['archive_first']))}. Those sites may have changed their rules since.</li>
    <li><b>Homepage only.</b> A site may treat inner pages differently.</li>
    <li><b>Who set the rule is unknown.</b> A refusal may come from the firm, its agency, its hosting company or a default setting nobody chose.</li>
    <li><b>Not legal advice.</b> The study says nothing about whether a firm should allow or refuse AI crawlers.</li>
  </ul>
</section>

<section id="faq">
  <h2>FAQ</h2>
{faq_html}
</section>

<section id="sources">
  <h2>Sources</h2>
  <p>All read on {d_en(PUB)}.</p>
  <ul class="sources">
    <li>OpenAI, “Overview of OpenAI Crawlers.” <a href="https://developers.openai.com/api/docs/bots" rel="noopener">developers.openai.com/api/docs/bots</a></li>
    <li>Anthropic, “Does Anthropic crawl data from the web, and how can site owners block the crawler?” <a href="https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler" rel="noopener">support.claude.com</a></li>
    <li>Perplexity, “Perplexity Crawlers.” <a href="https://docs.perplexity.ai/guides/bots" rel="noopener">docs.perplexity.ai/guides/bots</a></li>
    <li>Cloudflare, “Giving users choice with Cloudflare’s new Content Signals Policy,” September 24, 2025. <a href="https://blog.cloudflare.com/content-signals-policy/" rel="noopener">blog.cloudflare.com</a></li>
    <li>Jeremy Howard, “The /llms.txt file, v2,” first published September 3, 2024. <a href="https://llmstxt.org/" rel="noopener">llmstxt.org</a></li>
    <li>Yoast, llms.txt feature page. <a href="https://yoast.com/features/llms-txt/" rel="noopener">yoast.com/features/llms-txt</a></li>
    <li>Google, “Google’s common crawlers” (Google-Extended). <a href="https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers" rel="noopener">developers.google.com</a></li>
    <li>Common Crawl, “Frequently asked questions” (CCBot). <a href="https://commoncrawl.org/faq" rel="noopener">commoncrawl.org/faq</a></li>
    <li>RFC 9309, “Robots Exclusion Protocol,” September 2022. <a href="https://www.rfc-editor.org/rfc/rfc9309.html" rel="noopener">rfc-editor.org</a></li>
    <li>Internet Archive Wayback Machine, robots.txt captures for {S['robots_archived']} sites. <a href="https://web.archive.org/" rel="noopener">web.archive.org</a></li>
    <li>Copy for Originals, “Chicago personal injury lead generation: an OSINT study of 100 law firms.” <a href="../chicago-personal-injury-lead-gen-study/">tools.copyfororiginals.com</a></li>
  </ul>
  <p>How to cite: Copy for Originals, “Do law firm websites block AI crawlers?,” version {VERSION}, {d_en(UPD)}, {EN_URL}. Data licensed CC BY 4.0.</p>
  <p>Change log: version 1, {d_en(PUB)}, used three runs and no control names and reported 15 of 78 sites refusing an AI crawler’s name. Version 2, {d_en(UPD)}, reran the server test with five spaced runs from one connection, added Googlebot and Bingbot as control names, added three runs from a Chicago address as a second location, and read {S['robots_second'] + S['robots_us_exit']} robots.txt files by a second route in place of older archive copies. Version 1’s data is kept as <a href="pilot-three-runs.csv">pilot-three-runs.csv</a>.</p>
</section>

<footer>
  <p>Static page. No scripts, no tracking. Educational only, not legal advice. Made by <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a>.</p>
</footer>
</div>
</body>
</html>
"""


def build_sv(S, X):
    n, M, N, K = S["n"], S["base_served"], S["ai_refusers"], S["ctrl_both_served"]
    nm, g, order = common(S)
    rgo, rbi = g("googlebot", "refused"), g("bingbot", "refused")
    refused_list = f"{g(order[0], 'refused')} avvisade {LABEL[order[0]]}, {g(order[1], 'refused')} avvisade {LABEL[order[1]]} och {g(order[2], 'refused')} avvisade {LABEL[order[2]]}"
    la, ly, lr, ln, lu = S["llms_answered"], S["llms_yes"], S["llms_robots_syntax"], S["llms_no"], S["llms_unreadable"]
    gen = S["llms_generators"]; yoast = gen.get("Yoast SEO", 0)
    gen_items = [f"Yoast SEO i {yoast}"] + [f"{k} i {v}" for k, v in sorted(gen.items(), key=lambda x: (-x[1], x[0])) if k not in ("not stated", "Yoast SEO")]
    codes = S["refuser_codes"]
    code_txt = (f"403 <span lang=\"en\">“Forbidden”</span> (åtkomst nekad) på {codes.get('403', 0)} webbplatser och 429 <span lang=\"en\">“Too Many Requests”</span> (för många förfrågningar) på {codes.get('429', 0)}"
                + (f", och en blandning av båda på {codes['403+429']}" if codes.get("403+429") else ""))
    left, br = S["base_left_out"], S["base_refused"]; other = left - br
    dl = S["disallow_lists"]; DATES = "13 och 14 oktober 2026"
    use = {"GPTBot": "OpenAI, träning", "OAI-SearchBot": "OpenAI, sökning i ChatGPT", "ChatGPT-User": "OpenAI, hämtar sidor när en användare ställer en fråga",
           "ClaudeBot": "Anthropic, träning", "Claude-SearchBot": "Anthropic, sökning", "Claude-User": "Anthropic, hämtar sidor när en användare ställer en fråga",
           "PerplexityBot": "Perplexity, sökning", "Google-Extended": "Google, en token i robots.txt för träning och förankring (grounding) av Gemini", "CCBot": "Common Crawl, ett öppet webbarkiv"}
    robots_rows = "\n".join(f'      <tr><th scope="row">{t["name"]}</th><td>{use[t["name"]]}</td><td class="n">{t["named"]}</td><td class="n">{t["disallowed"]}</td></tr>' for t in S["robots_table"])
    name_rows = "\n".join(f'      <tr><th scope="row">{LABEL[k]}</th><td>{"AI-sökrobot" if k in AI3 else "Sökmotorns sökrobot (kontroll)"}</td><td class="n">{g(k, "served")}</td>'
                          f'<td class="n">{g(k, "refused")} ({pct_sv_t(g(k, "refused"), M)})</td><td class="n">{g(k, "mixed")}</td></tr>' for k in AI3 + CTRL)
    bo = S["base_other"]
    other_txt = (f", och {other} gick inte att nå" if set(bo) == {"unreachable"} else f", och {other} gick inte att nå eller gav blandade svar") if other else ""
    title = f"Blockerar advokatbyråers webbplatser AI-sökrobotar? robots.txt, brandväggar och llms.txt hos {n} personskadebyråer i Chicago (studie 2026)"
    lede = (f"Copy for Originals granskade webbplatserna för {n} personskadebyråer i Chicago den {DATES}. Bara {S['robots_disallow_any']} förbjuder en AI-sökrobot i robots.txt. "
            f"Men {N} av de {M} webbplatser som gick att testa avvisade varje gång en förfrågan med namnet GPTBot, ClaudeBot eller PerplexityBot, "
            f"och {K} av dessa {N} släppte igenom samma förfrågan under Googlebots och Bingbots namn.")
    desc = (f"Copy for Originals granskade webbplatserna för {n} personskadebyråer i Chicago den {DATES}. Bara {S['robots_disallow_any']} förbjuder en AI-sökrobot i robots.txt, "
            f"men {N} av {M} testbara webbplatser avvisade en förfrågan med namnet GPTBot, ClaudeBot eller PerplexityBot i alla fem körningarna, och {K} av dessa {N} släppte igenom "
            f"samma förfrågan under Googlebots och Bingbots namn. {ly} av {la} publicerar en llms.txt-fil. Data ingår.")
    faq = [
        ("Blockerar advokatbyråers webbplatser AI-sökrobotar som GPTBot och ClaudeBot?",
         f"Få gör det i robots.txt, fler gör det på servern. I en studie som Copy for Originals gjorde av webbplatserna för {n} personskadebyråer i Chicago den {DATES} förbjöd "
         f"{S['robots_disallow_any']} minst en AI-sökrobot i robots.txt. Av de {M} webbplatser som gick att testa på servern avvisade {N} en förfrågan med namnet GPTBot, ClaudeBot "
         f"eller PerplexityBot i alla fem körningarna: {refused_list}."),
        ("Avvisar webbplatser som stänger ute AI-sökrobotar också Googlebot?",
         f"Oftast inte. I studien från Copy for Originals släppte {K} av de {N} advokatbyråer vars webbplatser avvisade en förfrågan med en AI-sökrobots namn igenom samma förfrågan "
         f"varje gång den bar Googlebots eller Bingbots namn. Av alla {M} testade webbplatser avvisade {rgo} Googlebots namn och {rbi} Bingbots namn."),
        ("Kan en webbplats blockera AI-sökrobotar utan att det syns i robots.txt?",
         f"Ja. En brandvägg, ett webbhotell eller ett säkerhetstillägg kan avvisa en sökrobot innan själva webbplatsen svarar, och robots.txt ändras inte. I studien från Copy for "
         f"Originals hade {S['refusers_no_robots_rule']} av de {N} advokatbyråer vars webbplatser avvisade en förfrågan med en AI-sökrobots namn ingen regel i robots.txt mot just den "
         f"sökroboten, och {S['refusers_named_allowed']} av dem nämnde den avvisade sökroboten i robots.txt utan att förbjuda den."),
        ("Hur många advokatbyråer har en llms.txt-fil?",
         f"{ly} av {la}, eller {pct_sv(ly, la)}, i Copy for Originals studie av personskadebyråers webbplatser i Chicago den {DATES}. Ytterligare {lr} av de {la} svarade på "
         f"llms.txt-adressen med en fil i robots.txt-syntax, något som förslaget till llms.txt inte definierar, och {ln} hade ingen fil. Av de {ly} filerna uppgav {yoast} att de "
         f"hade genererats av Yoast SEO."),
    ]
    ld = ld_graph("sv", SV_URL, f"Blockerar advokatbyråers webbplatser AI-sökrobotar? robots.txt, brandväggar och llms.txt hos {n} personskadebyråer i Chicago", desc,
                  f"AI-sökrobotars åtkomst till webbplatserna för {n} personskadebyråer i Chicago (Copy for Originals, 2026)",
                  (f"En rad per webbplats för {n} personskadebyråer i Chicago, granskade den {DATES}: var robots.txt-filen lästes, vilka AI-sökrobotar den nämner och förbjuder, "
                   f"eventuell Content-Signal-rad, om det finns en llms.txt-fil och vad som genererade den, och hur startsidan svarade på en förfrågan i webbläsarstil och på "
                   f"förfrågningar med namnen GPTBot, ClaudeBot, PerplexityBot, Googlebot och Bingbot i fem körningar från Sverige och tre körningar från Chicago."),
                  faq, [("Verktyg", BASE + "sv/"), ("Studie: advokatbyråers webbplatser och AI-sökrobotar", SV_URL)])
    faq_html = "\n".join(f"  <h3>{q}</h3>\n  <p>{a}</p>" for q, a in faq)
    E = "../../" + EN_SLUG
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(html.unescape(desc), quote=True)}">
<meta name="author" content="Copy for Originals">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="index,follow,max-snippet:-1">
<link rel="canonical" href="{SV_URL}">
{HREFLANG}
<meta property="og:type" content="article">
<meta property="og:url" content="{SV_URL}">
<meta property="og:site_name" content="Copy for Originals">
<meta property="og:locale" content="sv_SE">
<meta property="og:locale:alternate" content="en_US">
<meta property="og:title" content="Blockerar advokatbyråers webbplatser AI-sökrobotar? En studie av {n} personskadebyråer i Chicago">
<meta property="og:description" content="{S['robots_disallow_any']} av {n} förbjuder en AI-sökrobot i robots.txt. {N} av {M} avvisar en på servern, och {K} av dem släpper igenom Googlebots namn. {ly} av {la} publicerar en llms.txt-fil.">
<meta property="article:published_time" content="{PUB.isoformat()}">
<meta property="article:modified_time" content="{UPD.isoformat()}">
{ICON}
<script type="application/ld+json">
{ld}
</script>
<link rel="stylesheet" href="../../site.css">
{STYLE}
</head>
<body>
<nav class="site-nav" aria-label="Copy for Originals">
  <a class="site-nav-brand" href="https://www.copyfororiginals.com/">Copy for Originals</a>
  <ul>
    <li><a href="https://www.copyfororiginals.com/" hreflang="en">Hem</a></li>
    <li><a href="https://www.copyfororiginals.com/thoughts" hreflang="en">Tankar</a></li>
    <li><a href="https://tools.copyfororiginals.com/sv/digital-marknadsforing/">Tjänster</a></li>
    <li><a href="https://tools.copyfororiginals.com/sv/" aria-current="true">Verktyg</a></li>
    <li><a href="https://www.copyfororiginals.com/about" hreflang="en">Om</a></li>
    <li><a href="https://www.copyfororiginals.com/faq" hreflang="en">Vanliga frågor</a></li>
    <li><a href="https://www.copyfororiginals.com/contact" hreflang="en">Kontakt</a></li>
  </ul>
  <ul class="lang-switch" aria-label="Språk"><li><span aria-current="true">Svenska</span></li><li><a href="{E}" hreflang="en" lang="en">English</a></li></ul>
</nav>
<div class="wrap">

<nav class="crumbs" aria-label="Sökväg"><a href="../">&larr; Alla verktyg</a></nav>

<header>
  <p class="kicker"><a href="https://copyfororiginals.com/">Copy for Originals</a> · Egen undersökning</p>
  <h1>Blockerar advokatbyråers webbplatser AI-sökrobotar?</h1>
  <p class="lede">{lede}</p>
  <p class="byline">Av <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a> · Publicerad <time datetime="{PUB.isoformat()}">{d_sv(PUB)}</time> · Senast uppdaterad <time datetime="{UPD.isoformat()}">{d_sv(UPD)}</time> · Version {VERSION} · <a href="{E}data.csv">Ladda ner data (CSV)</a></p>
  <p class="scope"><b>Endast i utbildningssyfte, inte juridisk rådgivning.</b> Studien beskriver offentliga filer och svar från servrar. Om en advokatbyrå ska släppa in AI-sökrobotar på sin webbplats avgör byrån själv.</p>
  <div class="stats">
    <div class="stat"><b>{S['robots_disallow_any']} av {n}</b><span>förbjuder minst en AI-sökrobot i robots.txt</span></div>
    <div class="stat"><b>{N} av {M}</b><span>avvisade en förfrågan med en AI-sökrobots namn i alla fem körningarna</span></div>
    <div class="stat"><b>{K} av {N}</b><span>av dem släppte igenom samma förfrågan under Googlebots och Bingbots namn</span></div>
    <div class="stat"><b>{ly} av {la}</b><span>publicerar en llms.txt-fil</span></div>
  </div>
</header>

<section id="findings">
  <h2>Vad visade studien?</h2>
  <ol class="check">
    <li><b>Nästan ingen advokatbyrå blockerar AI-sökrobotar i robots.txt.</b> {S['robots_named_any']} av {n} robots.txt-filer nämner över huvud taget någon AI-sökrobot, och {S['robots_disallow_any']} förbjuder någon. Bara {S['robots_disallow_gpt_and_claude']} förbjuder både GPTBot och ClaudeBot.</li>
    <li><b>Avvisningarna sker på servern, där robots.txt inte visar dem.</b> {N} av {M} webbplatser svarade på en förfrågan i webbläsarstil men avvisade varje gång en förfrågan med namnet GPTBot, ClaudeBot eller PerplexityBot. {S['refusers_no_robots_rule']} av de {N} saknar en regel i robots.txt mot den sökrobot de avvisade.</li>
    <li><b>Avvisningarna riktar sig mot AI-sökrobotar, inte mot sökrobotar i allmänhet.</b> {K} av de {N} webbplatserna släppte igenom samma förfrågan varje gång den bar Googlebots eller Bingbots namn.</li>
    <li><b>Namnet {LABEL[order[0]]} avvisades oftast.</b> {cap(refused_list)}.</li>
    <li><b>llms.txt är vanligt och skapas ofta automatiskt.</b> {ly} av {la} webbplatser publicerar en sådan fil. {S['llms_gen_stated']} av de {ly} anger vilket tillägg som skrev filen, och {yoast} av dem anger Yoast SEO. Ytterligare {lr} webbplatser svarar på llms.txt-adressen med regler i robots.txt-stil, som förslaget till llms.txt inte definierar.</li>
  </ol>
</section>

<section id="robots">
  <h2>Hur många advokatbyråer blockerar AI-sökrobotar i robots.txt?</h2>
  <p>{S['robots_disallow_any']} av {n}. Alla {n} webbplatser har en robots.txt-fil, och {S['robots_no_mention']} av dem nämner ingen AI-sökrobot. Av de {S['robots_named_any']} som gör det nämner {S['robots_named_not_disallowing']} sökrobotar utan att förbjuda någon av dem.</p>
  <div class="tablewrap">
  <table>
    <caption>AI-sökrobotar som nämns och förbjuds i robots.txt-filerna på webbplatserna för {n} personskadebyråer i Chicago (Copy for Originals, {d_sv(PUB)})</caption>
    <thead><tr><th scope="col">Sökrobotens namn</th><th scope="col">Företag och uppgivet syfte</th><th scope="col" class="n">Webbplatser som nämner den</th><th scope="col" class="n">Webbplatser som förbjuder den</th></tr></thead>
    <tbody>
{robots_rows}
    </tbody>
  </table>
  </div>
  <p>Med ”förbjuder” menas att den regelgrupp som nämner sökroboten innehåller <code>Disallow: /</code> utan <code>Allow: /</code>. Ingen webbplats förbjöd alla sökrobotar med en regel med jokertecken.</p>
  <p>De tre advokatbyråer som förbjuder en AI-sökrobot gör det på tre olika sätt:</p>
  <ul>
    <li><b>En förbjuder {len(dl[0][1])} av de 15 namn på AI-sökrobotar som studien kontrollerade,</b> bland dem GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot och PerplexityBot. Filen anger skälet i en kommentar: <span lang="en">“Disallow AI training crawlers (added 2026-04-24 to stop CPU saturation).”</span> (ungefär: ”Förbjud AI-sökrobotar som samlar in träningsdata (tillagt 2026-04-24 för att stoppa överbelastning av processorn)”).</li>
    <li><b>En förbjuder ClaudeBot och sju andra namn</b> (anthropic-ai, Google-Extended, Applebot-Extended, CCBot, Bytespider, meta-externalagent och Amazonbot) men har ingen regel för GPTBot.</li>
    <li><b>En förbjuder GPTBot och meta-externalagent</b> men släpper in ClaudeBot och OAI-SearchBot enligt de vanliga reglerna.</li>
  </ul>
  <p>{S['signal_total']} av de {S['robots_same_day']} filer som lästes den {d_sv(PUB)} har en <code>Content-Signal</code>-rad, det format som Cloudflare publicerade den 24 september 2025. {S['signal_train_yes']} lyder <code>search=yes, ai-input=yes, ai-train=yes</code>, och {S['signal_train_no']} lyder <code>search=yes, ai-input=yes, ai-train=no</code>. Tre av filerna som säger ja till träning är identiska bortsett från webbplatsens adress, vilket tyder på att en och samma webbplattform skriver raden åt sina kunder bland advokatbyråerna.</p>
</section>

<section id="server">
  <h2>Blockerar advokatbyråer AI-sökrobotar på servern i stället?</h2>
  <p>Ja, oftare än i robots.txt. {N} av {M} webbplatser ({pct_sv(N, M)}) skickade startsidan till en förfrågan i webbläsarstil men avvisade samma förfrågan när den bar en AI-sökrobots namn. Varje webbplats fick fem förfrågningar per namn, med minst tre minuters mellanrum och i ny ordning varje gång, och ”avvisade” betyder här att alla fem avvisades.</p>
  <div class="tablewrap">
  <table class="wide">
    <caption>Hur startsidorna hos {M} advokatbyråer svarade på en förfrågan med en sökrobots namn, fem körningar (Copy for Originals, {d_sv(UPD)})</caption>
    <thead><tr><th scope="col">Namn i förfrågan</th><th scope="col">Slag</th><th scope="col" class="n">Släpptes igenom alla 5 gångerna</th><th scope="col" class="n">Avvisades alla 5 gångerna</th><th scope="col" class="n">Blandat</th></tr></thead>
    <tbody>
{name_rows}
    </tbody>
  </table>
  </div>
  <p>{S['served_all_five_names']} av de {M} webbplatserna släppte igenom alla fem namnen varje gång. {N} avvisade minst en AI-sökrobots namn varje gång. Avvisningarna var {code_txt}. {S['refusers_cloudflare']} av de {N} webbplatserna ligger bakom Cloudflare.</p>
  <h3>Avvisar de här webbplatserna också Googlebots namn?</h3>
  <p>Oftast inte. {K} av de {N} webbplatser som avvisade en AI-sökrobots namn släppte igenom samma förfrågan varje gång den bar Googlebots eller Bingbots namn. {S['ctrl_any_refused']} avvisade också en sökmotorrobots namn{f", och {S['ctrl_unclear']} gav blandade svar" if S['ctrl_unclear'] else ""}.</p>
  <p>Det här är viktigt för hur resultatet ska läsas. En webbplats som kontrollerar att en besökare verkligen är den sökrobot den utger sig för att vara skulle visa bort en förfrågan som felaktigt bär Googlebots namn. {K} webbplatser gjorde inte det, så en identitetskontroll är en osannolik förklaring där. De webbplatserna behandlar en AI-sökrobots namn som ett skäl att avvisa.</p>
  <p>Av alla {M} webbplatser avvisade {rgo} Googlebots namn varje gång och {rbi} Bingbots. {(f"{S['bing_only_refusers']} webbplatser avvisade Bingbots namn men släppte igenom de tre AI-namnen och Googlebots." if S['bing_only_refusers'] == S['ctrl_only_refusers'] else f"{S['ctrl_only_refusers']} webbplatser avvisade en sökmotorrobots namn men släppte igenom alla tre AI-namnen.")}</p>
  <h3>Syns de här serverblockeringarna i robots.txt?</h3>
  <p>Nej. Bara {S['refusers_robots_match']} av de {N} webbplatserna har en regel i robots.txt mot en sökrobot som den avvisade. {S['refusers_no_ai_rule_at_all']} har ingen regel alls för AI-sökrobotar. {S['refusers_named_allowed']} nämner den avvisade sökroboten i robots.txt utan att förbjuda den, så filen ser ut som en inbjudan medan servern visar bort besökaren.</p>
  <p>Det fungerar också åt andra hållet. {S['claude_disallowed_but_served']} webbplatser förbjuder ClaudeBot i robots.txt men släppte ändå igenom förfrågan med ClaudeBots namn varje gång. RFC 9309, standarden för robots.txt, säger att reglerna <span lang="en">“are not a form of access authorization.”</span> (ungefär: ”inte är någon form av åtkomstbehörighet”). Filen anger vad webbplatsen begär av en sökrobot, och sökroboten avgör själv om den rättar sig efter det.</p>
  <h3>Håller resultatet från en amerikansk adress?</h3>
  <p>I stort sett, ja. Tre extra körningar den {d_sv(PUB)} gick ut via en VPN-utgång i Chicago med samma sex förfrågningar. {X['M']} webbplatser gick att testa därifrån och {X['both']} från båda platserna. {X['same']} av de {X['both']} hamnade på samma sätt från båda: de avvisade samma namn på AI-sökrobotar, eller inga alls. {X['refboth']} avvisade minst en AI-sökrobots namn från båda platserna. Från Chicago släppte {X['K']} av de {X['N']} webbplatser som avvisade en AI-sökrobots namn igenom Googlebots och Bingbots namn varje gång.</p>
  <h3>Vad betyder en avvisning för den riktiga sökroboten?</h3>
  <p>Den bevisar inte att den riktiga sökroboten avvisas. Studiens förfrågningar kom från vanliga internetuppkopplingar, inte från OpenAI:s, Anthropics eller Perplexitys egna adresser. En avvisning i tabellen betyder att webbplatsen behandlar sökrobotens namn annorlunda än en webbläsare, och jämförelsen med Googlebot visar att det på de flesta av de här webbplatserna är namnet som utlöser avvisningen. Bara webbplatsens egna serverloggar visar vad den riktiga sökroboten får.</p>
  <h3>Hur är det med de {left} webbplatser som hölls utanför testet?</h3>
  <p>{br} webbplatser avvisade förfrågan i webbläsarstil i varje körning{other_txt}, så det fanns inget att jämföra med. De flesta av de {br} har ett botskydd som visade bort ett skript som utgav sig för att vara en webbläsare: en utmaningssida från Cloudflare på en del, ett enkelt 403-svar på andra.</p>
  <p>{S['br_served_gptbot']} av de {br} skickade sidan när samma förfrågan bar namnet GPTBot. {S['br_served_all_ai']} släppte igenom alla tre AI-namnen. {S['br_served_gptbot_only']} släppte igenom GPTBots namn men avvisade ClaudeBots och PerplexityBots. På de här webbplatserna räckte enbart sökrobotens namn för att ta sig förbi en spärr som stoppade en vanlig förfrågan.</p>
</section>

<section id="llms-txt">
  <h2>Hur många advokatbyråer har en llms.txt-fil?</h2>
  <p>{ly} av {la}, eller {pct_sv(ly, la)}. En llms.txt-fil är en markdown-fil i webbplatsens rot, föreslagen den 3 september 2024 för att hjälpa AI-verktyg att använda webbplatsen.</p>
  <div class="tablewrap">
  <table>
    <caption>Vad {la} advokatbyråers webbplatser svarade på /llms.txt (Copy for Originals, {d_sv(PUB)})</caption>
    <thead><tr><th scope="col">Resultat</th><th scope="col" class="n">Webbplatser</th></tr></thead>
    <tbody>
      <tr><th scope="row">En llms.txt-fil i markdown</th><td class="n">{ly} ({pct_sv_t(ly, la)})</td></tr>
      <tr><th scope="row">En fil i robots.txt-syntax</th><td class="n">{lr} ({pct_sv_t(lr, la)})</td></tr>
      <tr><th scope="row">Ingen fil</th><td class="n">{ln} ({pct_sv_t(ln, la)})</td></tr>
    </tbody>
  </table>
  </div>
  <p>{lu} av de {n} webbplatserna gav inget läsbart svar på den här adressen och är inte medräknade.</p>
  <p><b>Vem som skrev filerna.</b> {S['llms_gen_stated']} av de {ly} filerna anger vilken programvara som genererade dem: {join(gen_items, 'och')}. Enligt Yoast är filen <span lang="en">“generated and refreshed automatically”</span> (ungefär: ”genereras och uppdateras automatiskt”) när funktionen väl är påslagen. De övriga {gen.get('not stated', 0)} filerna säger inget om hur de kom till.</p>
  <p><b>Hur stora de är.</b> Bland de {S['llms_sizes_n']} filer som lästes direkt är medianen omkring {kb_sv(S['llms_size_median'])} och den minsta {kb_sv(S['llms_size_min'])}. {S['llms_over_50k']} filer är större än 50 KB, och den största är {kb_sv(S['llms_max'])}.</p>
  <p><b>Filerna i robots.txt-stil.</b> {lr} webbplatser svarar på llms.txt-adressen med rader som <code>User-agent: *</code> och <code>Allow: /</code>. Sex av dem skickar exakt samma fil på 65 byte, som innehåller raden <code>Disallow-Training: /</code>. Förslaget till llms.txt beskriver en markdown-fil med en rubrik och länkar. Det definierar inga åtkomstregler, så ingenting i förslaget säger att en sökrobot ska rätta sig efter de här raderna.</p>
</section>

<section id="check-your-site">
  <h2>Hur kan en advokatbyrå kontrollera om den egna webbplatsen blockerar AI-sökrobotar?</h2>
  <ol class="check">
    <li><b>Läs din robots.txt.</b> Öppna <code>yourfirm.com/robots.txt</code> och sök efter GPTBot, OAI-SearchBot, ClaudeBot, Claude-SearchBot och PerplexityBot. En <code>User-agent</code>-rad som nämner någon av dem, följd av <code>Disallow: /</code>, ber den sökroboten att hålla sig borta.</li>
    <li><b>Fråga om brandväggen.</b> Fråga den som sköter ditt webbhotell, ditt Cloudflare-konto eller ditt säkerhetstillägg om någon botregel avvisar AI-sökrobotar. {S['refusers_no_robots_rule']} av de {N} avvisningarna i studien syns inte i robots.txt.</li>
    <li><b>Be om serverloggarna.</b> Be om de loggrader som innehåller sökrobotarnas namn och vilken statuskod var och en fick. 200 betyder att sökroboten fick sidan. 403 eller 429 betyder att den inte fick den. Det är den enda kontrollen som ser den riktiga sökroboten.</li>
    <li><b>Ta ställning till träning och sökning var för sig.</b> Enligt OpenAI hämtar GPTBot innehåll som kan användas för att träna företagets modeller, medan OAI-SearchBot gör webbplatser synliga i ChatGPT:s sökfunktioner. Enligt Anthropic samlar ClaudeBot in innehåll som kan bidra till träning, medan Claude-SearchBot förbättrar sökresultaten. En advokatbyrå kan avvisa den ena och släppa in den andra.</li>
    <li><b>Öppna din llms.txt.</b> Om <code>yourfirm.com/llms.txt</code> finns ska den vara markdown som börjar med en <code>#</code>-rubrik och listar dina sidor. Börjar den med <code>User-agent</code> följer den inte det format som förslaget beskriver.</li>
  </ol>
  <p>Vad svarsmotorerna gör med en sida när de väl kan läsa den beskriver vi i guiden om <a href="../innehall-som-llm-hamtar-och-citerar/">hur du skriver innehåll som LLM:er hämtar och citerar</a>. Advokatbyråerna i studien kommer från <a href="../chicago-personskador-leadgenerering-studie/">studien om leadgenerering för personskadebyråer i Chicago</a>.</p>
</section>

<section id="method">
  <h2>Hur gjordes studien?</h2>
  <ol class="check">
    <li><b>Urval:</b> de {n} webbplatser för personskadebyråer i Chicago som listas i version 4 av Copy for Originals Chicagostudie.</li>
    <li><b>robots.txt och llms.txt:</b> varje fil hämtades den {d_sv(PUB)} med en user agent i Chrome-stil. {S['robots_live']} robots.txt-filer lästes på det sättet. Ytterligare {S['robots_second'] + S['robots_us_exit']} avvisade förfrågan och lästes samma dag på annan väg: {S['robots_second']} via en hämtningstjänst på webben och {S['robots_us_exit']} via adressen i Chicago som beskrivs nedan. De sista {S['robots_archived']} lästes från den senaste kopian i Internet Archive, sparad mellan {d_sv(iso(S['archive_first']))} och {d_sv(iso(S['archive_last']))}; ingen av de {S['robots_archived']} nämner någon AI-sökrobot. {S['llms_second'] + S['llms_us_exit']} svar om llms.txt kom samma två vägar.</li>
    <li><b>Tolkning av reglerna:</b> reglerna grupperades efter <code>User-agent</code>-rad enligt RFC 9309. En sökrobot räknas som förbjuden när en grupp som nämner den innehåller <code>Disallow: /</code> eller <code>Disallow: /*</code> och ingen <code>Allow: /</code>. Femton namn på AI-sökrobotar kontrollerades; tabellen visar nio.</li>
    <li><b>Servertest:</b> varje startsida hämtades med en user agent i Chrome-stil och med user agents som innehöll <code>GPTBot/1.4</code>, <code>ClaudeBot/1.0</code>, <code>PerplexityBot/1.0</code>, <code>Googlebot/2.1</code> och <code>bingbot/2.0</code>. Det blev fem körningar den {d_sv(UPD)} från en vanlig bredbandsuppkoppling i Sverige, med minst tre minuters mellanrum och de sex förfrågningarna i ny ordning varje körning. Utgångsadressen kontrollerades före och efter varje körning. En webbplats räknas som testbar när förfrågan i webbläsarstil gav svaret 200 i alla fem körningarna ({M} webbplatser). Ett namn räknas som avvisat när det fick 403 eller 429 i alla fem körningarna, och som blandat när körningarna gav olika svar.</li>
    <li><b>Andra plats:</b> tre körningar med samma sex förfrågningar den {d_sv(PUB)} via en kommersiell VPN-utgång i Chicago. De redovisas för sig och ingår inte i tabellen med {M} webbplatser.</li>
    <li><b>llms.txt:</b> ett 200-svar räknas som en fil när det inte är en HTML-sida. Filer som börjar med <code>User-agent</code> räknades för sig.</li>
  </ol>
  <p>Alla webbplatser och alla svarskoder finns i <a href="{E}data.csv">datafilen</a>, och skripten för insamlingen finns i <a href="https://github.com/jbastide/tools/tree/main/law-firm-websites-ai-crawlers-study/method" rel="noopener">metodmappen på GitHub</a>.</p>
</section>

<section id="limits">
  <h2>Begränsningar</h2>
  <ul>
    <li><b>Testförfrågan är inte den riktiga sökroboten.</b> Den bar sökrobotens namn men kom från en vanlig uppkoppling. Jämförelsen med Googlebot och Bingbot gör en identitetskontroll osannolik hos {K} av de {N} webbplatser som avvisade, men bara serverloggar kan avgöra saken.</li>
    <li><b>{left} webbplatser gick inte att testa på servern.</b> {br} avvisade förfrågan i webbläsarstil i varje körning{other_txt}. Från adressen i Chicago avvisade {X['br']} webbplatser den, så en amerikansk adress av det slaget hjälpte inte. En vanlig amerikansk bredbandsuppkoppling är inte testad.</li>
    <li><b>En stad, ett rättsområde, två dagar.</b> {n} personskadebyråer i Chicago den {DATES}. Se procentsatserna som en fingervisning.</li>
    <li><b>{S['robots_archived']} robots.txt-filer är arkivkopior,</b> den äldsta från {d_sv(iso(S['archive_first']))}. De webbplatserna kan ha ändrat sina regler sedan dess.</li>
    <li><b>Bara startsidan.</b> En webbplats kan behandla undersidor annorlunda.</li>
    <li><b>Vem som satte regeln är okänt.</b> En avvisning kan komma från advokatbyrån, dess marknadsföringsbyrå, dess webbhotell eller en standardinställning som ingen har valt.</li>
    <li><b>Inte juridisk rådgivning.</b> Studien säger ingenting om huruvida en advokatbyrå bör släppa in eller avvisa AI-sökrobotar.</li>
  </ul>
</section>

<section id="faq">
  <h2>Vanliga frågor</h2>
{faq_html}
</section>

<section id="sources">
  <h2>Källor</h2>
  <p>Samtliga lästa den {d_sv(PUB)}.</p>
  <ul class="sources">
    <li>OpenAI, ”Overview of OpenAI Crawlers”. <a href="https://developers.openai.com/api/docs/bots" rel="noopener">developers.openai.com/api/docs/bots</a></li>
    <li>Anthropic, ”Does Anthropic crawl data from the web, and how can site owners block the crawler?” <a href="https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler" rel="noopener">support.claude.com</a></li>
    <li>Perplexity, ”Perplexity Crawlers”. <a href="https://docs.perplexity.ai/guides/bots" rel="noopener">docs.perplexity.ai/guides/bots</a></li>
    <li>Cloudflare, ”Giving users choice with Cloudflare’s new Content Signals Policy”, 24 september 2025. <a href="https://blog.cloudflare.com/content-signals-policy/" rel="noopener">blog.cloudflare.com</a></li>
    <li>Jeremy Howard, ”The /llms.txt file, v2”, först publicerad 3 september 2024. <a href="https://llmstxt.org/" rel="noopener">llmstxt.org</a></li>
    <li>Yoast, sidan om funktionen llms.txt. <a href="https://yoast.com/features/llms-txt/" rel="noopener">yoast.com/features/llms-txt</a></li>
    <li>Google, ”Google’s common crawlers” (Google-Extended). <a href="https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers" rel="noopener">developers.google.com</a></li>
    <li>Common Crawl, ”Frequently asked questions” (CCBot). <a href="https://commoncrawl.org/faq" rel="noopener">commoncrawl.org/faq</a></li>
    <li>RFC 9309, ”Robots Exclusion Protocol”, september 2022. <a href="https://www.rfc-editor.org/rfc/rfc9309.html" rel="noopener">rfc-editor.org</a></li>
    <li>Internet Archive Wayback Machine, sparade kopior av robots.txt för {S['robots_archived']} webbplatser. <a href="https://web.archive.org/" rel="noopener">web.archive.org</a></li>
    <li>Copy for Originals, ”Leadgenerering för personskadebyråer i Chicago: en OSINT-studie av 100 advokatbyråer”. <a href="../chicago-personskador-leadgenerering-studie/">tools.copyfororiginals.com</a></li>
  </ul>
  <p>Så citerar du sidan: Copy for Originals, ”Blockerar advokatbyråers webbplatser AI-sökrobotar?”, version {VERSION}, {d_sv(UPD)}, {EN_URL}. Data under licensen CC BY 4.0.</p>
  <p>Versionshistorik: version 1, {d_sv(PUB)}, använde tre körningar utan kontrollnamn och redovisade att 15 av 78 webbplatser avvisade en AI-sökrobots namn. Version 2, {d_sv(UPD)}, gjorde om servertestet med fem körningar med mellanrum från en och samma uppkoppling, lade till Googlebot och Bingbot som kontrollnamn, lade till tre körningar från en adress i Chicago som en andra plats och läste {S['robots_second'] + S['robots_us_exit']} robots.txt-filer på annan väg i stället för äldre arkivkopior. Datan från version 1 finns kvar som <a href="{E}pilot-three-runs.csv">pilot-three-runs.csv</a>.</p>
</section>

<footer>
  <p>Statisk sida. Inga skript, ingen spårning. Endast i utbildningssyfte, inte juridisk rådgivning. Av <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a>.</p>
</footer>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    S = stats.compute(sys.argv[1]); X = compare(sys.argv[1])
    open(sys.argv[2], "w", encoding="utf-8").write(build_en(S, X))
    open(sys.argv[3], "w", encoding="utf-8").write(build_sv(S, X))
    print("built", sys.argv[2], sys.argv[3])
