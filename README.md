# tools

Small, single-purpose static web tools. Every page is one HTML file with
vanilla JS that links the shared [`site.css`](site.css): no build step, no dependencies, no third-party requests.

## Contents

| Tool | Path | What it does |
| --- | --- | --- |
| Short-Form Script Pacing & Hook Timer | [`script-timer/`](script-timer/) | Times a short-form video script in real time, splits it into retention zones (3s / 15s / 30s / 60s), and grades the hook against first-sentence lengths measured in 132 top YouTube Shorts (green inside 3s, note to 5s, warning past 5s). Default pace is the measured 193 WPM median. |
| Keyword Triage (Google Ads keyword profitability checker) | [`keyword-triage/`](keyword-triage/) | Reads a Google Ads or Microsoft Ads keyword report (CSV, TSV or Excel) and sorts each keyword into Cut, Trim bids, Keep, Scale or Needs data against a target CPA or ROAS. A Content-Security-Policy blocks every request except the site's own stylesheet, so the report can't leave the browser. |
| Negative Keyword Finder (Google Ads search terms analyzer) | [`negative-keywords/`](negative-keywords/) | Reads a Google Ads or Microsoft Ads search terms report (CSV, TSV or Excel) and flags search terms that break two limits entered before upload (an unacceptable cost per conversion, and a spend limit with no conversions), recurring words (1- and 2-grams) that passed the spend limit without converting, and low-CTR terms to review. Copies them as exact- and phrase-match negatives. Same Content-Security-Policy as Keyword Triage. |
| Lead Gen Search Campaign Checklist | [`search-checklist/`](search-checklist/) | A laminated cockpit-style preflight checklist for Google Ads lead gen Search campaigns in five phases (account, campaign settings, bidding & budget, keywords & ads, after launch). Enter a target CPA and it sets the minimum daily budget at 3× the target CPA. Checks are saved in the browser. |
| Target CPA & ROAS Calculator | [`target-cpa-roas/`](target-cpa-roas/) | Walks a first-timer through setting a Google Ads target one question at a time: average sale and gross margin, then (for lead gen) a gut guess at how many leads become customers, checked against a count from records or a three-step leak estimate (real leads × reached × closed). Then the share of gross profit to spend on ads (slider, marks at 30/50/100%). Returns break-even and target CPA or ROAS, a split of one sale, a 3× daily budget for leads, and a weekly schedule of ≤15% steps from today's CPA or ROAS. No third-party requests. |
| PPC Troubleshooter | [`ppc-troubleshooter/`](ppc-troubleshooter/) | Pick a Google Ads problem (clicks but no conversions, a few expensive clicks, conversions that dropped after a good start, rising CPC, ads that barely show or spend), answer follow-up questions one at a time, and get ranked causes and fixes. Asks for your own cost per click (from the account, or Keyword Planner's top of page bid high range), not an industry average. Runs the luck math (chance of zero conversions, a binomial test for drops, budget tiers from CPC ÷ conversion rate) and shows it as a gumball-machine picture. Every cause is also written out in static HTML (cause → how it's spotted → fix), with a clicks × conversion-rate luck table, a daily budget × CPC table, and Google's status labels mapped to fixes. No third-party requests. |

## Guides

| Guide | Path | What it covers |
| --- | --- | --- |
| How much do legal marketing agencies charge? | [`how-much-do-legal-marketing-agencies-charge/`](how-much-do-legal-marketing-agencies-charge/) | Owner-reported law firm marketing fees from 312 coded r/LawFirm threads (2023–2026): SEO, Google Ads management and website builds (one figure per owner, de-duplicated by author), quotes owners turned down, cost per lead by channel, and a cost per signed case calculator. Vendor names are replaced with generic terms. Data as CSV. |
| Local Services Ads vs Google Ads for lawyers | [`local-services-ads-vs-google-ads-for-lawyers/`](local-services-ads-vs-google-ads-for-lawyers/) | Guide to the 2026 move of Local Services Ads into Google Ads (Performance Max with pay-per-lead goals; professional services listed for late 2026): what changes, a pre-migration checklist, Google’s credit rules mapped to the junk leads lawyers report, the 20-second missed-call rule, ranking factors, and a cost per signed case calculator (user’s own numbers only). Built from Google Help pages and 37 r/LawFirm threads with first-hand LSA accounts (2023–2026). |
| Law firm Google Ads agency scorecard | [`law-firm-google-ads-agency-scorecard/`](law-firm-google-ads-agency-scorecard/) | 12 checks a law firm owner can run in their own Google Ads account (Admin access, customer ID, Google’s exact cost, signed-case reporting, change history), each backed by Google’s third-party policy or by 188 r/LawFirm threads with first-hand owner accounts (312 coded, 2023–2026). Interactive color-coded scorer (2/1/0 points, three must-haves) that lists the questions to send the agency. Coded thread data as CSV. |
| Google Ads no conversions study | [`ppc-no-conversions-study/`](ppc-no-conversions-study/) | 62 coded Google Ads Community and r/PPC threads scored with the PPC Gumball Rule, with a CSV of the data. Original-research arm of the experiment. |
| The PPC Gumball Rule | [`ppc-gumball-rule/`](ppc-gumball-rule/) | Named rule of thumb: zero conversions after 3× expected cost per conversion is 95% unlikely to be luck. Lookup tables and a calculator. Part of the AI Overview citation experiment. |
| Personal injury Google Ads budget | [`personal-injury-google-ads-budget/`](personal-injury-google-ads-budget/) | Minimum monthly budget = 3 × expected cost per lead, with tables and a calculator. Commercial layer of the experiment. |
| Google Ads for law firms (hub) | [`google-ads-for-law-firms/`](google-ads-for-law-firms/) | Parent page for the law firm guides: cost per lead and minimum budget, Local Services Ads vs Search, the CallRail 82% figure traced to its December 2021 survey, five state positions on bidding on a competitor’s name, Google’s call recording rules, wasted searches, intake, and cost per signed case. Links to every law firm guide and tool. Educational only, not legal advice. |
| Can a law firm bid on a competitor’s name in Google Ads? | [`can-lawyers-bid-on-competitor-names-google-ads/`](can-lawyers-bid-on-competitor-names-google-ads/) | Spoke under the hub. Seven states’ positions on lawyers using a competing lawyer’s name as a keyword, each quoted from the opinion, ruling or rule (North Carolina, Ohio, Michigan, Texas, South Carolina, New Jersey, Florida), four court cases, Google’s Trademarks policy, a pre-bid checklist, and steps for a firm whose own name is being bid on. Educational only, not legal advice. |
| Personal injury Google Ads (hub) | [`personal-injury-google-ads/`](personal-injury-google-ads/) | Parent page for the personal injury pages: cost per lead and minimum budget (summarized, linking to the budget page), who advertises in Chicago, starter keywords and negative keywords, Local Services Ads, competitor names, what injury sites claim, intake, cost per signed case, and a clicks-without-a-lead table. Every figure comes from our own pages. Educational only, not legal advice. |
| Do 82% of law firms say Google Ads isn’t worth it? | [`82-percent-law-firms-paid-search-roi/`](82-percent-law-firms-paid-search-roi/) | Spoke under the hub. Traces the “82% of law firms say paid search isn’t worth it” figure to CallRail’s December 2021 survey (508 respondents, 82% of firms already running paid search agreed it is “too expensive to get good ROI”), sets it beside CallRail’s later surveys (97% in October 2022, 25% in December 2024), and quotes four published versions that drop the date, the base, the country or the meaning. |
| Personal injury lawyer leads (hub) | [`personal-injury-lawyer-leads/`](personal-injury-lawyer-leads/) | Buy leads or generate your own, compared by cost per signed case. Built on rows from the pricing study’s and scorecard’s open data files: owner-reported prices for bought leads, Local Services Ads and Search ads, five personal injury owners’ results from bought leads, 20 lead vendor threads (15 with junk leads), and one firm’s cost per signed case over three months. Quotes ABA Model Rule 7.2 and Comment 5 on paying for leads. Vendor names withheld. Educational only, not legal advice. |
| Five short answers for law firm Search campaigns | [`law-firm-google-ads-faq/`](law-firm-google-ads-faq/) | Conversion rate, Target CPA, broad match, negative keywords and bidding. Was the formatting-only control page for the experiment until October 13, 2026, when it was retitled and linked under the hub; the baseline is in [`experiment-log.md`](experiment-log.md). |
| Should AI fully manage your Google Ads campaigns? | [`should-ai-manage-google-ads/`](should-ai-manage-google-ads/) | Pros and cons of Google’s automation and AI agents in lead gen Search campaigns, with dated sources. AI suggests, a person approves. |
| Why healthcare PPC experience transfers to law firms | [`healthcare-ppc-for-law-firms/`](healthcare-ppc-for-law-firms/) | Bridge page for law firms: the Google Ads problems healthcare and legal share, side by side, and what doesn’t carry over. Not part of the experiment and doesn’t link to its arm pages. |
| How to write content that LLMs retrieve and cite | [`rag-friendly-content/`](rag-friendly-content/) | What answer engines do with a page, each AEO practice rated by evidence, and a 12-point checklist. |
| HIPAA-compliant conversion tracking for Google Ads | [`hipaa-google-ads-conversions/`](hipaa-google-ads-conversions/) | Healthcare tracking platforms, enterprise CDPs, server-side GTM, offline conversion imports and HIPAA call tracking compared by price, setup effort and fit for practices without IT staff, with dated sources and a section on what couldn't be verified. Educational only, not legal advice. |

## Service pages (Swedish and English)

Pages for Swedish companies. Each one exists twice, as separate static URLs: Swedish under `sv/`, English at the root.

| Page | Swedish | English | What it covers |
| --- | --- | --- | --- |
| Google Ads for lead generation in Sweden | [`sv/google-ads-leadgenerering/`](sv/google-ads-leadgenerering/) | [`google-ads-lead-generation-sweden/`](google-ads-lead-generation-sweden/) | Managed Google Ads for Swedish businesses from Tidaholm: stopping the bleeding, cleaning up a messy account, visibility, clicks without inquiries, digital marknadsföring, price, budget, in-person vs remote, consent and VAT. |
| Google Ads in the USA for Swedish companies | [`sv/google-ads-usa/`](sv/google-ads-usa/) | [`google-ads-usa-for-swedish-companies/`](google-ads-usa-for-swedish-companies/) | US lead generation from Sweden: differences from the Swedish market, where to start, test budgets, time zones and who answers, measurement, price. |
| English copywriting for Swedish companies | [`sv/engelsk-copywriting-usa/`](sv/engelsk-copywriting-usa/) | [`english-copywriting-for-swedish-companies/`](english-copywriting-for-swedish-companies/) | American English sales copy: Swedish habits in English text, translation vs copywriting, what a US buyer looks for, US advertising rules, price and process. |
| Swedish hub | [`sv/`](sv/) | the root index | Overview of the three services in Swedish, plus the tools described in Swedish. |

### Conventions for bilingual pages

- One static file per language, never a JavaScript toggle or `data-en` attributes: AI crawlers don't run
  JavaScript, so text swapped in by script is invisible to them.
- Swedish pages live under `sv/` with Swedish slugs and `<html lang="sv">`; the English page sits at the
  root with an English slug. `sv/` pages link the stylesheet as `../../site.css`.
- Each page links its counterpart with `<link rel="alternate" hreflang>` (sv, en, and x-default pointing at
  the English page) and with the visible `.lang-switch` in the `.pagebar` (both in `site.css`).
- The two versions carry the same facts, numbers, sources and dates. Change both in the same commit.
- Every question `<h2>`/`<h3>` and the paragraph under it is mirrored word for word in the FAQPage JSON-LD.
- Facts about the business (price, minimum fee, meeting area, managed ad spend) are repeated on all of
  these pages and in `llms.txt`; a change to one of them means a search across `sv/`, the three English
  pages, the index cards and `llms.txt`.

## Deploying

GitHub Pages serves this repo as-is from the default branch:

1. **Settings → Pages → Build and deployment → Source: _Deploy from a branch_**
2. Branch `main`, folder `/ (root)`, then Save.

Pages then serves:

- `https://jbastide.github.io/tools/` — the index
- `https://jbastide.github.io/tools/script-timer/` — the script timer
- `https://jbastide.github.io/tools/keyword-triage/` — the keyword triage tool
- `https://jbastide.github.io/tools/negative-keywords/` — the negative keyword finder

`.nojekyll` is present so files are served verbatim rather than passed through Jekyll.

> **Note:** GitHub Pages on a **private** repository requires a paid plan (Pro, Team, or
> Enterprise). On the free plan the repo has to be public for Pages to publish.

## Local preview

No build required — open the file directly, or serve the folder:

```sh
python3 -m http.server 8000
# then visit http://localhost:8000/script-timer/
```

## Conventions for adding a tool

- One directory per tool, containing a single `index.html`.
- Link the shared stylesheet with a relative path (`<link rel="stylesheet" href="../site.css">`) and keep
  only page-specific rules inline. Use its tokens (`--accent`, `--moss`, `--ochre`, `--red`, `--lake`,
  `--stone` and their `-bg` tints) instead of new hex colors. A page with a Content-Security-Policy needs
  `style-src 'self' 'unsafe-inline'` so the stylesheet can load.
- Keep it dependency-free. No CDNs. The only web fonts are the self-hosted ones in `fonts/`.
- Include a `<title>`, a meta description, and a `SoftwareApplication` JSON-LD block.
- Light and dark come from `site.css` via `prefers-color-scheme`; check both.
- Add a row to the table above, a card to the root `index.html`, and entries to `sitemap.xml` and `llms.txt`.

### Site style

`site.css` holds the look, and it is the same look as copyfororiginals.com: paper, ink and one
blaze-orange accent; Big Shoulders Display in heavy caps for headings and labels; Literata for reading;
square corners and thick black rules instead of rounded cards. The fonts are self-hosted in `fonts/`
(SIL Open Font License), so pages still make no third-party requests; tool pages allow them with
`font-src 'self'` in their Content-Security-Policy. Keep page-specific rules inline and built on the
tokens (`--ink`, `--accent`, `--panel`, `--line-strong`, `--display`, `--sans`).

### Writing tool pages so answer engines can read them

AI crawlers (ChatGPT, Claude, Perplexity) don't run JavaScript, so a tool page has to explain itself
in static HTML below the interactive part. See `keyword-triage/` for the pattern and
[`rag-friendly-content/`](rag-friendly-content/) for the evidence behind it.

- Open with one definitional sentence: "<Name> is a <category> that <does what> for <whom>."
- Use question-shaped `<h2>`s that match real searches ("How does X decide…"), and answer in the
  first sentence under each one.
- Make every section stand alone. Repeat the tool's name instead of "it", because sections are
  retrieved one at a time.
- Put every rule, threshold, default and formula from the JS into visible text, plus a worked
  example with real numbers. Run the example through the tool to confirm it matches.
- Use real `<table>`s with `<caption>`, `<thead>` and `<th>`, not div grids. Never put facts only in
  JS, images, `hidden` panels or JSON-LD.
- Show a visible "Last updated" date that matches `dateModified` in JSON-LD, and update it only for
  real changes.
- JSON-LD (`WebApplication`, `FAQPage`, `BreadcrumbList`) has to mirror visible text word for word.

Learned on the PPC Troubleshooter rebuild (October 2026), see `ppc-troubleshooter/` for the pattern:

- If the tool's verdicts, causes or fixes live in JavaScript, write them out as a static table per
  problem (cause → how it's spotted → what to do), copied from the JS wording. That content is
  invisible to crawlers otherwise, and it is usually the best content on the page.
- Phrase `<h2>`s the way beginners type them, not the way we describe the feature: "clicks but no
  conversions", "not spending", "dropped when I didn't change anything", "so high all of a sudden",
  "eligible but no impressions". Forum titles are numbers first, then a plea: "$500 spent, 539 clicks,
  0 conversions. Is this normal?" An H2 or FAQ that echoes that shape gets matched.
- Lead the `<title>` with the primary query; the `<h1>` can stay the broader question.
- Quote official labels verbatim (Google's status names and definitions) and verify each against
  the help page before publishing. Map label → meaning → fix in one table; nobody else does.
- Add a Sources section with URLs and the access date, and cite our own research pages with the
  specific number.
- Generate the FAQ from one list so the visible text and the FAQPage JSON-LD can't drift.
- Give wide tables `class="wide"` (min-width inside the `.tbl` scroller) so columns don't squash on
  phones; the page itself must never scroll sideways.
- Update `llms.txt` to state the page's new facts and numbers; answer engines read it first.
