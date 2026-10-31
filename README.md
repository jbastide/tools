# tools

Small, single-purpose static web tools. Every page is one HTML file with
vanilla JS that links the shared [`site.css`](site.css): no build step, no dependencies, and no third-party
requests unless a visitor accepts Google Analytics (see "Analytics and cookie consent").

## Contents

| Tool | Path | What it does |
| --- | --- | --- |
| Short-Form Script Pacing & Hook Timer | [`script-timer/`](script-timer/) | Times a short-form video script in real time, splits it into retention zones (3s / 15s / 30s / 60s), and grades the hook against first-sentence lengths measured in 132 top YouTube Shorts (green inside 3s, note to 5s, warning past 5s). Default pace is the measured 193 WPM median. |
| Keyword Triage (Google Ads keyword profitability checker) | [`keyword-triage/`](keyword-triage/) | Reads a Google Ads or Microsoft Ads keyword report (CSV, TSV or Excel) and sorts each keyword into Cut, Trim bids, Keep, Scale or Needs data against a target CPA or ROAS. A Content-Security-Policy blocks every request except the site's own stylesheet, so the report can't leave the browser. |
| Negative Keyword Finder (Google Ads search terms analyzer) | [`negative-keywords/`](negative-keywords/) | Reads a Google Ads or Microsoft Ads search terms report (CSV, TSV or Excel) and flags search terms that break two limits entered before upload (an unacceptable cost per conversion, and a spend limit with no conversions), recurring words (1- and 2-grams) that passed the spend limit without converting, and low-CTR terms to review. Copies them as exact- and phrase-match negatives. Same Content-Security-Policy as Keyword Triage. |
| Lead Gen Search Campaign Checklist | [`search-checklist/`](search-checklist/) | A laminated cockpit-style preflight checklist for Google Ads lead gen Search campaigns in five phases (account, campaign settings, bidding & budget, keywords & ads, after launch). Enter a target CPA and it sets the minimum daily budget at 3× the target CPA. Checks are saved in the browser. |
| Target CPA & ROAS Calculator | [`target-cpa-roas/`](target-cpa-roas/) | Walks a first-timer through setting a Google Ads target one question at a time: average sale and gross margin, then (for lead gen) a gut guess at how many leads become customers, checked against a count from records or a three-step leak estimate (real leads × reached × closed). Then the share of gross profit to spend on ads (slider, marks at 30/50/100%). Returns break-even and target CPA or ROAS, a split of one sale, a 3× daily budget for leads, and a weekly schedule of ≤15% steps from today's CPA or ROAS. No third-party requests. |
| PPC Troubleshooter | [`ppc-troubleshooter/`](ppc-troubleshooter/) | Pick a Google Ads problem (clicks but no conversions, a few expensive clicks, conversions that dropped after a good start, rising CPC, ads that barely show or spend), answer follow-up questions one at a time, and get ranked causes and fixes. Asks for your own cost per click (from the account, or Keyword Planner's top of page bid high range), not an industry average. Runs the luck math (chance of zero conversions, a binomial test for drops, budget tiers from CPC ÷ conversion rate) and shows it as a gumball-machine picture. Every cause is also written out in static HTML (cause → how it's spotted → fix), with a clicks × conversion-rate luck table, a daily budget × CPC table, and Google's status labels mapped to fixes. No third-party requests. |
| Can AI read my site? | [`can-ai-read-my-site/`](can-ai-read-my-site/) | Post (no inputs, so it loads `consent.js`) for the free open-source checker at github.com/jbastide/can-ai-read-my-site: page facts as a non-JavaScript crawler sees them, a server test against Googlebot and Bingbot over several rounds (the crawler study method), and robots.txt per RFC 9309. Names the other free access checkers. The tool itself lives in its own repo; `report-screenshot.jpg` is copied from its `docs/`. Swedish twin `sv/kan-ai-lasa-min-sajt/`. |

## Guides

| Guide | Path | What it covers |
| --- | --- | --- |
| How much do legal marketing agencies charge? | [`how-much-do-legal-marketing-agencies-charge/`](how-much-do-legal-marketing-agencies-charge/) | Owner-reported law firm marketing fees from 109 of 312 coded r/LawFirm threads (2023–2026; 145 owner reports): SEO, Google Ads management and website builds (one figure per owner, de-duplicated by author), quotes owners turned down, cost per lead by channel, and a cost per signed case calculator. Vendor names are replaced with generic terms. Data as CSV. |
| Local Services Ads vs Google Ads for lawyers | [`local-services-ads-vs-google-ads-for-lawyers/`](local-services-ads-vs-google-ads-for-lawyers/) | Guide to the 2026 move of Local Services Ads into Google Ads (Performance Max with pay-per-lead goals; professional services listed for late 2026): what changes, a pre-migration checklist, Google’s credit rules mapped to the junk leads lawyers report, the 20-second missed-call rule, ranking factors, and a cost per signed case calculator (user’s own numbers only). Built from Google Help pages and 37 r/LawFirm threads with first-hand LSA accounts (2023–2026). |
| Law firm Google Ads agency scorecard (choosing a Google Ads consultant) | [`law-firm-google-ads-agency-scorecard/`](law-firm-google-ads-agency-scorecard/) | Version 3 (October 31, 2026) is built around hiring a consultant: what consultants charge (five agencies’ published prices, each labelled as the agency’s own or as Searchbloom’s reading; 4 owners’ fees from the pricing study’s data file; no survey with a stated method), what a firm should own and see (Google’s third-party policy and help pages quoted), and whether a firm may pay a marketer a share of fees or per case (ABA Model Rules 5.4, 5.3(c), 7.2 with comments; New York, Illinois and South Carolina ethics opinions; North Carolina 5.4(a)(6); Michigan and Alabama 7.2; none addresses a percentage of ad spend). Then 12 checks a law firm owner can run in their own Google Ads account (Admin access, customer ID, Google’s exact cost, signed-case reporting, change history), each backed by Google’s third-party policy or by 188 r/LawFirm threads with first-hand owner accounts (312 coded, 2023–2026). Interactive color-coded scorer (2/1/0 points, three must-haves) that lists the questions to send the agency. Coded thread data as CSV. Educational only, not legal advice. |
| August 17 update or the Strait of Hormuz? | [`google-ads-august-17-update-vs-hormuz/`](google-ads-august-17-update-vs-hormuz/) | 3,173 r/PPC and r/googleads posts and about 39,600 comments (June–October 2026) screened via Arctic Shift; 123 first-hand Google Ads “it got worse” threads coded for metric, blamed cause and macro mentions (31 posters blame the August 17 bidding change, 44 counting replies; 1 blames the economy; 0 use the words Hormuz, gas prices or recession), with a monthly complaint-rate baseline from January 2025. Sets them beside Google’s help pages on the August 17 target-based bidding change, Amsive’s week-one and week-two data, EIA pump prices, CPI, Michigan and Conference Board confidence, the Fed, Beige Books, Angi, ServiceTitan, Home Depot, Lowe’s, The Trade Desk and the 2022 LocaliQ/Skai analog. Two-fingerprint table (rules of thumb), a six-step account test, and a revenue-side section. Every claim audited against sources after the first draft; verdict table on the page. Three CSVs. |
| Google Ads no conversions study | [`ppc-no-conversions-study/`](ppc-no-conversions-study/) | 62 coded Google Ads Community and r/PPC threads scored with the PPC Gumball Rule, with a CSV of the data. Original-research arm of the experiment. |
| Do law firm websites block AI crawlers? | [`law-firm-websites-ai-crawlers-study/`](law-firm-websites-ai-crawlers-study/) | robots.txt, llms.txt and homepage responses for 100 Chicago personal injury firm websites (version 2, October 13 and 14, 2026): 3 disallow an AI crawler in robots.txt; in five runs from Sweden, 13 of 78 refused a request carrying the name GPTBot, ClaudeBot or PerplexityBot every time, and 11 of those 13 served Googlebot’s and Bingbot’s names; three runs from a Chicago address agree. 42 of 92 publish an llms.txt. Both language versions are generated by `method/build_pages.py` from `data.csv` and checked by `method/check.py`; change the builder and rebuild, never the HTML. Version 1’s data is `pilot-three-runs.csv`. |
| Haiku, Sonnet or Opus for online research? | [`haiku-vs-sonnet-vs-opus-research-study/`](haiku-vs-sonnet-vs-opus-research-study/) | One research brief given to Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5, three runs each (October 13, 2026): all 593 quotes found word for word on the cited pages; 25 known facts found 19–23 (Haiku), 23–24 (Sonnet), 25 (Opus); 41 of 593 claims flagged by two blind AI graders as saying more than their quote; estimated cost per run $0.28, $1.07, $2.79. The page is generated by `method/build.py` from the CSV files, so edit the builder, not the HTML. Raw outputs in `runs/`, the discarded first attempt in `pilot/`, scripts and grading files in `method/`. Not part of the citation experiment. |
| Can a laptop check an AI research report? | [`can-a-laptop-check-ai-research/`](can-a-laptop-check-ai-research/) | Benchmark of receipts, an open-source checker for AI research reports run on local models (October 25, 2026): 340 planted cases from the model study's graded claims (Gemma 4 12B judge on a 16 GB MacBook Air: 222 of 235 damaged claims caught, 94 of 105 correct passed; MiniCheck and HHEM alone and combined), and an audit of the agent-shopping research notes (141 flagged items, 36 wrong or unsupported, corrected). The page is generated by `method/build.py` from `planted.csv` and `audit.csv`; `method/prepare.py` writes those from the receipts repository. Change the builder, not the HTML, and mirror text changes in `sv/`. |
| [`ai-visibility-measurement-reddit-study/`](ai-visibility-measurement-reddit-study/) | [`sv/ai-synlighet-matning-reddit-studie/`](sv/ai-synlighet-matning-reddit-studie/) |
| What can’t marketers measure about AI visibility? | [`ai-visibility-measurement-reddit-study/`](ai-visibility-measurement-reddit-study/) | Every post in seven marketing subreddits from January 1, 2025 to October 15, 2026 (200,753, Arctic Shift archive): posts naming AI search rose from 1.5% to 8.7% of all posts, posts about measuring it from 0.14% to 2.97%. 308 threads (9,190 comments) coded twice against one codebook (Sonnet first pass, Opus published pass; agreement 91–97%, kappa 0.65–0.91): Search Console’s AI data 60 threads, tool cost/accuracy 55, format claims 50, “just SEO” 47, no data from the assistants 45. 40 threads on Search Console’s generative AI report (praise 17, no queries 23, no clicks 18). All 971 quotes machine-checked. The page is generated by `method/build.py` from the CSV files; change the builder, not the HTML, and mirror text changes in `sv/`. Raw archive pull (130 MB) not committed. |
| Are free AI visibility checkers accurate? | [`free-ai-visibility-checkers-tested/`](free-ai-visibility-checkers-tested/) | Agent-run test (October 22 and 23, 2026; page published October 24), part 1 of the AI visibility tracker series: Claude in the built-in browser ran five free, no-signup checkers on 10 Chicago personal injury firms (every 10th row of the crawler study). Geoptie 2 rounds (score changed for 4 of 10 firms, 4 of 30 engine flips, Google engine empty in 20 of 20), Loamly 11 reports all 0% with 0 prompts tested, Semrush 6 of 10 firms (3 free checks a day), HubSpot and Rank Prompt no result for an agent. Ahrefs and Mangools not run (terms ask for no automated use; `runs/by-hand/STEPS.md` is for a person), plus Arobis, GeoBuddy, Honeyb, Howseen left out. Three Opus agent research runs in `runs/agent-research/`. Hand-written HTML; `method/analyze.py` rebuilds `data.csv` and `mentions.csv` from `runs/agent/`; terms quotes come from `method/terms-quotes.md`. Round-3 numbers go where the page has `<!-- R3 -->` comments. Swedish twin at `sv/gratis-ai-synlighetskontroller-testade/`; the two must change together. |
| Will AI agents make marketing disappear? | [`ai-shopping-agents-marketing-evidence/`](ai-shopping-agents-marketing-evidence/) | Evidence review (October 16, 2026) of a Forbes Tech Council post claiming marketing departments will disappear because AI agents will buy from AI. Every number in the article checked against its source (all real, none measures agent-completed purchases), then 26 claims about agentic commerce graded solid / mixed / conjecture / contradicted: adoption surveys (about 3% of transactions involve an agent; 6–11% would let one buy), lab studies on how agents choose (ACES, ABxLab, Magentic Marketplace: more swayed by badges, fabricated authority and position than people are), platform monetization (ChatGPT ads, Sponsored Agents, the retracted 4% checkout fee, Rufus sponsored products), the Amazon–Muse access fight (Ninth Circuit Comet ruling, Buy for Me, Williams-Sonoma terms, a 200-retailer blocking audit), subscription friction (Einav et al.), readiness surveys, and Muse’s adoption curve (6.6 million downloads in 29 days on a straight line). Hand-written HTML with a 26-row `claims.csv`; no builder. Swedish twin at `sv/ai-shoppingagenter-marknadsforing-bevis/` shares the CSV. |
| [`where-ai-search-goes-next/`](where-ai-search-goes-next/) | [`sv/vart-ar-ai-sokningen-pa-vag/`](sv/vart-ar-ai-sokningen-pa-vag/) |
| Where does AI search go next? | [`where-ai-search-goes-next/`](where-ai-search-goes-next/) | Analysis (October 16, 2026) following the Reddit measurement study: what Google, OpenAI, Microsoft, Amazon, Perplexity and Anthropic have shipped on AI-visibility measurement versus ads in AI answers (dated timeline), likely next moves, whether third-party trackers survive (platform terms, historical analogies, acquisitions), whether paid search gains and whether organic data is kept vague on purpose (evidence both ways), what measurement is due when (CMA December 3, 2026; DMA January 2027), how AI agents choose (ACES, Magentic, brand-tiebreaker studies), the brand-first psychology evidence, and eight takeaways. 113 figures and 80 of 83 quotations machine-checked against saved sources. Healthcare ads: Google help page still excludes healthcare inside AI Overviews; only a LinkedIn comment from the Ads Liaison confirms a US test in AI Mode. Hand-written HTML, no builder. |
| What decides whether an AI recommends you, and what to do about it | [`what-decides-ai-recommendations/`](what-decides-ai-recommendations/) | Synthesis of the seven October 2026 AI studies and guides and more than 200 sources: eight findings (research not buying; answers are sampled; ranking is not citation; crawler access; relevance and specifics beat layout; agents pick by spec then salience; third-party pages decide whether you are named; what can be measured), a four-gate model (readable, known, verifiable, preferred), seven steps in order, a what-not-to-pay-for list and a caveats box. Hand-written HTML, not generated. Swedish twin at `sv/vad-avgor-ai-rekommendationer/`; the two must change together. |
| What to do when ChatGPT or Google’s AI gets your company wrong | [`when-ai-gets-your-company-wrong/`](when-ai-gets-your-company-wrong/) | Guide (October 24, 2026) on wrong AI answers about companies: the two 2026 measurements (Seer Interactive’s self-audit, 2.8% wrong and 31.2% non-answers across six platforms, with a per-platform table; Reputation Age and Bubbling on 39 CAC 40 companies, 40% of figures wrong, with a per-indicator table), error types and causes, why assistants give non-answers, a channels table for ChatGPT, Google AI Overviews and AI Mode, Gemini, Copilot, Perplexity and Claude (none promises a correction), the Full Fact evidence on whether fixing a source fixes the answer, a dated law section (GDPR Recital 14 and Article 16, noyb; Walters, Keene, Starbuck, Wolf River; Munich, Aachen, Hamm), and a nine-step audit. 50 sources, all accessed October 24, 2026; vendors labelled. Hand-written HTML, no builder: edit `index.html` and mirror text changes in `sv/nar-ai-har-fel-om-ditt-foretag/`. |
| Do self-ranked "best X" lists get you recommended by AI? | [`self-promotional-listicles-ai-search/`](self-promotional-listicles-ai-search/) | Evidence review (October 24, 2026) of self-promotional listicles in AI answers and Google: citations vs recommendations (Peec about 11% of citations; Ray 69% of cited self-promoters left out of Google AI Overviews recommendations, 83% in September; Scrunch 4% to 7% recommendation lift, 39% vs 19% mentions, per-assistant table), where the 69% and 11% come from (side-by-side table), whether lists hand recommendations to rivals (Scrunch placebo tests), when listing yourself helps (Ahrefs experiment), the unconfirmed January 2026 drops with evidence both ways (Ray, Indig/SE Ranking 62% gaining, Grow and Convert), what Google's documents say, US/EU/Swedish comparative-advertising law (Telia v. Hi3G), eight keep/rewrite/retire steps and limits. 29 sources, every figure checked at source; vendors labelled. Swedish twin at `sv/egna-topplistor-ai-sokning/`; the two must change together. |
| Does AI search answer Swedish questions from Swedish sources? | [`does-ai-search-cite-local-language-sources/`](does-ai-search-cite-local-language-sources/) | Guide (October 24, 2026) to how AI search handles non-English questions, with Sweden as the case: which AI surfaces Swedes use (Internetstiftelsen 2026), ChatGPT's English fan-outs (Peec, about 78% of non-English sessions, no Swedish figure), citation language by engine for Swedish prompts (Temso: AI Overviews 85.1%, Copilot 60.4%, ChatGPT 57.4%, Grok 47.1%), why studies disagree (MaxAEO, Temso industry pages, Toronto preprint), the US default when models answer from memory (Location Not Found, ACL 2026), same-language preference and silent conflict resolution (Faux Polyglot, Stockholm University), machine-translated Reddit in Swedish AI answers (Peec: 71.6% on AI Overviews), Google's language and audience signals, eight publishing steps with an evidence-limits table, and gaps. 33 sources, all accessed October 24, 2026. Hand-written HTML, no builder. Swedish twin at `sv/citerar-ai-svenska-kallor/`; the two must change together. |
| The PPC Gumball Rule | [`ppc-gumball-rule/`](ppc-gumball-rule/) | Named rule of thumb: zero conversions after 3× expected cost per conversion is a sign something is wrong: a campaign converting as expected shows that only about 5% of the time. Lookup tables and a calculator. Part of the AI Overview citation experiment. |
| Law firm Google Ads budget guidelines, by practice area | [`law-firm-google-ads-budget/`](law-firm-google-ads-budget/) | Ten budget guidelines for any practice area (minimum 3 × cost per lead per campaign, daily budget = monthly ÷ 30.4, ceiling set by cost per signed case), Google’s budget rules quoted from its help pages, and original data: 278 coded figures from 106 r/LawFirm threads (2023–2026), including monthly Google Ads budgets from 24 owners ($433 to $30,000, median $5,000; 16 worked, 1 no difference, 7 no verdict), 26 budget recommendations and reported click costs. Since version 2 (October 31, 2026) it holds the former criminal defense, family law and estate planning budget pages as sections (`#criminal-defense`, `#family-law`, `#estate-planning`): LocaliQ’s medians for each (floor of about $304, $311 and $217 a month), owner tables from the agency pricing study’s data file, and small-budget odds. Calculator. Data as CSV. Spoke of the law firm hub. |
| Personal injury Google Ads budget | [`personal-injury-google-ads-budget/`](personal-injury-google-ads-budget/) | Minimum monthly budget = 3 × expected cost per lead, with tables and a calculator; links the budget guidelines for click costs reported on r/LawFirm. Commercial layer of the experiment. |
| Google Ads for law firms (hub) | [`google-ads-for-law-firms/`](google-ads-for-law-firms/) | Parent page for the law firm guides, rewritten October 31, 2026 so each section answers one question and links the spoke that goes deeper: does it work and what it costs (WordStream’s 2026 medians, $9.87 a click and $131.63 a lead, and owner-reported paid figures from the site’s data pages), how much to spend (3 × cost per lead), Local Services Ads vs Search and the move into Performance Max, agency or in-house, the CallRail 82% figure, seven state positions on bidding on a competitor’s name (New Jersey given only as its 2019 committee view), Google’s call recording rules and the 60-day retention for legal verticals in North America (from Google’s About Local Services data page), wasted searches, intake and offline conversion limits, and cost per signed case. Links to every law firm guide and tool. Educational only, not legal advice. |
| Can a law firm bid on a competitor’s name in Google Ads? | [`can-lawyers-bid-on-competitor-names-google-ads/`](can-lawyers-bid-on-competitor-names-google-ads/) | Spoke under the hub. Seven states’ positions on lawyers using a competing lawyer’s name as a keyword, each quoted from the opinion, ruling or rule (North Carolina, Ohio, Michigan, Texas, South Carolina, New Jersey, Florida), four court cases, Google’s Trademarks policy, a pre-bid checklist, and steps for a firm whose own name is being bid on. Educational only, not legal advice. |
| Personal injury Google Ads (hub) | [`personal-injury-google-ads/`](personal-injury-google-ads/) | Parent page for the personal injury pages: cost per lead and minimum budget (summarized, linking to the budget page), who advertises in Chicago, starter keywords and negative keywords, Local Services Ads, competitor names, what injury sites claim, intake, cost per signed case, and a clicks-without-a-lead table. Every figure comes from our own pages. Educational only, not legal advice. |
| Do 82% of law firms say Google Ads isn’t worth it? | [`82-percent-law-firms-paid-search-roi/`](82-percent-law-firms-paid-search-roi/) | Spoke under the hub. Traces the “82% of law firms say paid search isn’t worth it” figure to CallRail’s December 2021 survey (508 respondents, 82% of firms already running paid search agreed it is “too expensive to get good ROI”), sets it beside CallRail’s later surveys (97% in October 2022, 25% in December 2024), and quotes four published versions that drop the date, the base, the country or the meaning. |
| Personal injury lead cost (hub) | [`personal-injury-lawyer-leads/`](personal-injury-lawyer-leads/) | What a personal injury lead costs from bought leads, Local Services Ads and Google Search ads, each figure labelled by kind: lead vendors’ own published prices (PinPoint, Injury Lead Gen), vendor estimates (Best Case Leads, Retainer Reach, Rankings.io), benchmark medians with their samples (LocaliQ, WordStream) and owner-reported prices from the pricing study’s and scorecard’s open data files. Google’s Local Services Ads charging, credit and migration rules from its help pages. Cost per signed case from one firm’s three months of data; vendors’ figures only as worked examples. Five personal injury owners’ results from bought leads, 20 lead vendor threads (15 with junk leads). Quotes ABA Model Rule 7.2 and Comment 5 on paying for leads. Vendor names withheld in owner reports. Educational only, not legal advice. |
| Criminal defense, family law and estate planning Google Ads budgets (stubs) | [`criminal-defense-google-ads-budget/`](criminal-defense-google-ads-budget/), [`family-law-google-ads-budget/`](family-law-google-ads-budget/), [`estate-planning-google-ads-budget/`](estate-planning-google-ads-budget/) | Merged into the law firm budget guidelines on October 31, 2026. Each is a `noindex, follow` stub with a meta refresh to its section (`law-firm-google-ads-budget/#criminal-defense`, `#family-law`, `#estate-planning`), a canonical to the guidelines and a visible link; out of the sitemap and off the homepage. The Swedish twins (`sv/brottmal-`, `sv/familjeratt-`, `sv/arvsplanering-google-ads-budget/`) are stubs pointing to `sv/advokatbyra-google-ads-budget/`. The stubs carry no hreflang. |
| Five short answers for law firm Search campaigns | [`law-firm-google-ads-faq/`](law-firm-google-ads-faq/) | Conversion rate, Target CPA, broad match, negative keywords and bidding. Was the formatting-only control page for the experiment until October 13, 2026, when it was retitled and linked under the hub; the baseline is in [`experiment-log.md`](experiment-log.md). |
| Does Google record calls to law firms from its ads? | [`does-google-record-calls-to-law-firms/`](does-google-record-calls-to-law-firms/) | Spoke under the hub. Quotes Google’s help pages on call recording for Local Services Ads (all US and Canada calls through the forwarding number; 60-day retention in legal verticals) and Google Ads (on by default for AI-qualified call leads; 30-day playback; how to turn it off), who can listen, what callers hear, the Local Services provider terms and Call Ads Supplemental Terms, three places where Google’s own pages disagree, the July 1, 2026 default date (from a Google email quoted in trade press), and four bar publications: North Carolina (proposed 2021, withdrawn April 2022), Wisconsin (January 2021), Connecticut Informal Opinion 2013-08 and New York City Bar Formal Opinion 2026-2. Eight sources were added on October 13, 2026 from the AI research study’s runs. Every quotation was machine-checked against the source pages. Educational only, not legal advice. |
| How does a law firm track signed cases back to Google Ads clicks? | [`track-signed-cases-google-ads/`](track-signed-cases-google-ads/) | Spoke under the hub. Offline conversion imports for law firms from Google’s help pages: the click ID (GCLID), five setup steps, call conversion import, the 90-day upload limit (63 days for enhanced conversions for leads), what each method sends to Google about a client, and primary versus secondary conversions. Quotations machine-checked against the saved source pages. Educational only, not legal advice. |
| Lead generation for lawyers (hub) | [`lead-generation-for-lawyers/`](lead-generation-for-lawyers/) | All practice areas. Six lead sources compared; a table of owner complaints by channel from the scorecard’s 188 owner threads (lead vendors 15 of 20 junk leads, Local Services Ads 13 of 19, Google Search ads 5 of 13, SEO 17 of 39 no return); owner-reported cost per lead and monthly spend; a bought-leads section; cost per signed case; intake losses; ABA Model Rules 7.1, 7.2 and 7.3. Educational only, not legal advice. |
| Should AI fully manage your Google Ads campaigns? | [`should-ai-manage-google-ads/`](should-ai-manage-google-ads/) | Pros and cons of Google’s automation and AI agents in lead gen Search campaigns, with dated sources. AI suggests, a person approves. |
| Why healthcare PPC experience transfers to law firms | [`healthcare-ppc-for-law-firms/`](healthcare-ppc-for-law-firms/) | Bridge page for law firms: the Google Ads problems healthcare and legal share, side by side, and what doesn’t carry over. Not part of the experiment and doesn’t link to its arm pages. |
| How to write content that LLMs retrieve and cite | [`rag-friendly-content/`](rag-friendly-content/) | What answer engines do with a page, each AEO practice rated by evidence, and a 12-point checklist. |
| How AI agents choose products for consumers | [`how-ai-agents-choose-products/`](how-ai-agents-choose-products/) | Evidence review (version 1, October 17, 2026) of how ChatGPT, Perplexity, Gemini, Claude, Amazon Rufus and Copilot pick products: a six-stage decision model, a 21-row verdict table for Cialdini’s principles and the Kahneman, Thaler and Ariely nudges, the evidence for and against the “third-party wall”, and a tactics table split into measured, vendor-asserted and backfiring. 397 figures and quotations were checked against their cited pages by four Claude Opus passes (263 confirmed as written, 93 tightened, 17 re-pointed to the right source, 13 sourced or softened, 6 corrected, 5 unreachable); the per-claim CSVs are in `research/verification/`, the five research-thread notes in `research/notes/` and the synthesis in `research/synthesis.md`. Hand-written HTML, no builder: edit `index.html` and mirror text changes in `sv/`. Living document; bump the version line in the byline when revising. |
| HIPAA-compliant conversion tracking for Google Ads | [`hipaa-google-ads-conversions/`](hipaa-google-ads-conversions/) | Healthcare tracking platforms, enterprise CDPs, server-side GTM, offline conversion imports and HIPAA call tracking compared by price, setup effort and fit for practices without IT staff, with dated sources and a section on what couldn't be verified. Educational only, not legal advice. |
| How this site makes money | [`how-this-site-makes-money/`](how-this-site-makes-money/) | Disclosure page: client services pay for the site; guides that compare tools may carry affiliate links, each marked “paid link” with `rel="sponsored"`; rankings come before any affiliate program; the programs joined and any ads are listed with dates (none as of October 20, 2026). See "Ads and affiliate links" below. |

## Swedish and English

Every page exists twice, as two static URLs: English at the root, Swedish under `sv/`. The English
homepage is [`index.html`](index.html) and the Swedish homepage is [`sv/index.html`](sv/index.html); each
lists the same tools, services, studies and guides in its own language.

### Service pages for Swedish companies

| Page | Swedish | English | What it covers |
| --- | --- | --- | --- |
| Digital marketing services (overview) | [`sv/digital-marknadsforing/`](sv/digital-marknadsforing/) | [`digital-marketing-services-sweden/`](digital-marketing-services-sweden/) | The offer in one place: the four services, a table from common problems to the right page, key facts (location, meetings, prices, first step), the free tools and the contact section. The Swedish page is the "Tjänster" item in the Swedish top nav. Until October 13, 2026 this content lived at `sv/`. |
| Google Ads for lead generation in Sweden | [`sv/google-ads-leadgenerering/`](sv/google-ads-leadgenerering/) | [`google-ads-lead-generation-sweden/`](google-ads-lead-generation-sweden/) | Managed Google Ads for Swedish businesses from Tidaholm: stopping the bleeding, cleaning up a messy account, visibility, clicks without inquiries, digital marknadsföring, price, budget, in-person vs remote, consent and VAT. |
| Google Ads in the USA for Swedish companies | [`sv/google-ads-usa/`](sv/google-ads-usa/) | [`google-ads-usa-for-swedish-companies/`](google-ads-usa-for-swedish-companies/) | US lead generation from Sweden: differences from the Swedish market, where to start, test budgets, time zones and who answers, measurement, price. |
| English copywriting for Swedish companies | [`sv/engelsk-copywriting-usa/`](sv/engelsk-copywriting-usa/) | [`english-copywriting-for-swedish-companies/`](english-copywriting-for-swedish-companies/) | American English sales copy: Swedish habits in English text, translation vs copywriting, what a US buyer looks for, US advertising rules, price and process. |
| SEO and AEO for Swedish companies | [`sv/seo-sokmotoroptimering/`](sv/seo-sokmotoroptimering/) | [`seo-aeo-for-swedish-companies/`](seo-aeo-for-swedish-companies/) | Agentic frameworks for original, fact-based content from open sources: SEO vs AEO, why a company is invisible, the seven phases, who does what, the checking phase, examples from this site, pricing on request. |

### Where each page lives in Swedish

Tools keep their English product names and slugs under `sv/`. Guides and studies have Swedish slugs.

| English | Swedish |
| --- | --- |
| [`does-ai-search-cite-local-language-sources/`](does-ai-search-cite-local-language-sources/) | [`sv/citerar-ai-svenska-kallor/`](sv/citerar-ai-svenska-kallor/) |
| [`google-ads-lead-generation-sweden/`](google-ads-lead-generation-sweden/) | [`sv/google-ads-leadgenerering/`](sv/google-ads-leadgenerering/) |
| [`google-ads-usa-for-swedish-companies/`](google-ads-usa-for-swedish-companies/) | [`sv/google-ads-usa/`](sv/google-ads-usa/) |
| [`english-copywriting-for-swedish-companies/`](english-copywriting-for-swedish-companies/) | [`sv/engelsk-copywriting-usa/`](sv/engelsk-copywriting-usa/) |
| [`self-promotional-listicles-ai-search/`](self-promotional-listicles-ai-search/) | [`sv/egna-topplistor-ai-sokning/`](sv/egna-topplistor-ai-sokning/) |
| [`seo-aeo-for-swedish-companies/`](seo-aeo-for-swedish-companies/) | [`sv/seo-sokmotoroptimering/`](sv/seo-sokmotoroptimering/) |
| [`digital-marketing-services-sweden/`](digital-marketing-services-sweden/) | [`sv/digital-marknadsforing/`](sv/digital-marknadsforing/) |
| [`script-timer/`](script-timer/) | [`sv/script-timer/`](sv/script-timer/) |
| [`script-timer/study/`](script-timer/study/) | [`sv/script-timer/studie/`](sv/script-timer/studie/) |
| [`keyword-triage/`](keyword-triage/) | [`sv/keyword-triage/`](sv/keyword-triage/) |
| [`negative-keywords/`](negative-keywords/) | [`sv/negative-keywords/`](sv/negative-keywords/) |
| [`search-checklist/`](search-checklist/) | [`sv/search-checklist/`](sv/search-checklist/) |
| [`target-cpa-roas/`](target-cpa-roas/) | [`sv/target-cpa-roas/`](sv/target-cpa-roas/) |
| [`ppc-troubleshooter/`](ppc-troubleshooter/) | [`sv/ppc-troubleshooter/`](sv/ppc-troubleshooter/) |
| [`ppc-gumball-rule/`](ppc-gumball-rule/) | [`sv/ppc-gumball-rule/`](sv/ppc-gumball-rule/) |
| [`82-percent-law-firms-paid-search-roi/`](82-percent-law-firms-paid-search-roi/) | [`sv/82-procent-advokatbyraer-betald-sok/`](sv/82-procent-advokatbyraer-betald-sok/) |
| [`ai-shopping-agents-marketing-evidence/`](ai-shopping-agents-marketing-evidence/) | [`sv/ai-shoppingagenter-marknadsforing-bevis/`](sv/ai-shoppingagenter-marknadsforing-bevis/) |
| [`can-lawyers-bid-on-competitor-names-google-ads/`](can-lawyers-bid-on-competitor-names-google-ads/) | [`sv/far-advokater-bjuda-pa-konkurrenters-namn-google-ads/`](sv/far-advokater-bjuda-pa-konkurrenters-namn-google-ads/) |
| [`chicago-personal-injury-lead-gen-study/`](chicago-personal-injury-lead-gen-study/) | [`sv/chicago-personskador-leadgenerering-studie/`](sv/chicago-personskador-leadgenerering-studie/) |
| [`does-google-record-calls-to-law-firms/`](does-google-record-calls-to-law-firms/) | [`sv/spelar-google-in-samtal-till-advokatbyraer/`](sv/spelar-google-in-samtal-till-advokatbyraer/) |
| [`google-ads-august-17-update-vs-hormuz/`](google-ads-august-17-update-vs-hormuz/) | [`sv/google-ads-17-augusti-eller-hormuz/`](sv/google-ads-17-augusti-eller-hormuz/) |
| [`google-ads-for-law-firms/`](google-ads-for-law-firms/) | [`sv/google-ads-for-advokatbyraer/`](sv/google-ads-for-advokatbyraer/) |
| [`haiku-vs-sonnet-vs-opus-research-study/`](haiku-vs-sonnet-vs-opus-research-study/) | [`sv/haiku-sonnet-opus-researchstudie/`](sv/haiku-sonnet-opus-researchstudie/) |
| [`can-a-laptop-check-ai-research/`](can-a-laptop-check-ai-research/) | [`sv/kan-en-laptop-granska-ai-research/`](sv/kan-en-laptop-granska-ai-research/) |
| [`healthcare-ppc-for-law-firms/`](healthcare-ppc-for-law-firms/) | [`sv/vard-ppc-for-advokatbyraer/`](sv/vard-ppc-for-advokatbyraer/) |
| [`hipaa-google-ads-conversions/`](hipaa-google-ads-conversions/) | [`sv/hipaa-google-ads-konverteringar/`](sv/hipaa-google-ads-konverteringar/) |
| [`how-ai-agents-choose-products/`](how-ai-agents-choose-products/) | [`sv/hur-ai-agenter-valjer-produkter/`](sv/hur-ai-agenter-valjer-produkter/) |
| [`how-much-do-legal-marketing-agencies-charge/`](how-much-do-legal-marketing-agencies-charge/) | [`sv/vad-tar-marknadsforingsbyraer-for-advokater-betalt/`](sv/vad-tar-marknadsforingsbyraer-for-advokater-betalt/) |
| [`how-this-site-makes-money/`](how-this-site-makes-money/) | [`sv/sa-tjanar-sajten-pengar/`](sv/sa-tjanar-sajten-pengar/) |
| [`law-firm-google-ads-agency-scorecard/`](law-firm-google-ads-agency-scorecard/) | [`sv/advokatbyra-google-ads-byra-poangkort/`](sv/advokatbyra-google-ads-byra-poangkort/) |
| [`law-firm-google-ads-budget/`](law-firm-google-ads-budget/) | [`sv/advokatbyra-google-ads-budget/`](sv/advokatbyra-google-ads-budget/) |
| [`law-firm-google-ads-faq/`](law-firm-google-ads-faq/) | [`sv/advokatbyra-google-ads-fragor/`](sv/advokatbyra-google-ads-fragor/) |
| [`law-firm-websites-ai-crawlers-study/`](law-firm-websites-ai-crawlers-study/) | [`sv/advokatbyraers-webbplatser-ai-sokrobotar-studie/`](sv/advokatbyraers-webbplatser-ai-sokrobotar-studie/) |
| [`lead-generation-for-lawyers/`](lead-generation-for-lawyers/) | [`sv/leadgenerering-for-advokater/`](sv/leadgenerering-for-advokater/) |
| [`local-services-ads-vs-google-ads-for-lawyers/`](local-services-ads-vs-google-ads-for-lawyers/) | [`sv/local-services-ads-eller-google-ads-for-advokater/`](sv/local-services-ads-eller-google-ads-for-advokater/) |
| [`personal-injury-google-ads-budget/`](personal-injury-google-ads-budget/) | [`sv/personskador-google-ads-budget/`](sv/personskador-google-ads-budget/) |
| [`personal-injury-google-ads/`](personal-injury-google-ads/) | [`sv/personskador-google-ads/`](sv/personskador-google-ads/) |
| [`personal-injury-lawyer-leads/`](personal-injury-lawyer-leads/) | [`sv/leads-for-personskadeadvokater/`](sv/leads-for-personskadeadvokater/) |
| [`ppc-no-conversions-study/`](ppc-no-conversions-study/) | [`sv/google-ads-inga-konverteringar-studie/`](sv/google-ads-inga-konverteringar-studie/) |
| [`rag-friendly-content/`](rag-friendly-content/) | [`sv/innehall-som-llm-hamtar-och-citerar/`](sv/innehall-som-llm-hamtar-och-citerar/) |
| [`what-decides-ai-recommendations/`](what-decides-ai-recommendations/) | [`sv/vad-avgor-ai-rekommendationer/`](sv/vad-avgor-ai-rekommendationer/) |
| [`free-ai-visibility-checkers-tested/`](free-ai-visibility-checkers-tested/) | [`sv/gratis-ai-synlighetskontroller-testade/`](sv/gratis-ai-synlighetskontroller-testade/) |
| [`can-ai-read-my-site/`](can-ai-read-my-site/) | [`sv/kan-ai-lasa-min-sajt/`](sv/kan-ai-lasa-min-sajt/) |
| [`should-ai-manage-google-ads/`](should-ai-manage-google-ads/) | [`sv/ska-ai-skota-google-ads/`](sv/ska-ai-skota-google-ads/) |
| [`track-signed-cases-google-ads/`](track-signed-cases-google-ads/) | [`sv/spara-tecknade-arenden-google-ads/`](sv/spara-tecknade-arenden-google-ads/) |
| [`when-ai-gets-your-company-wrong/`](when-ai-gets-your-company-wrong/) | [`sv/nar-ai-har-fel-om-ditt-foretag/`](sv/nar-ai-har-fel-om-ditt-foretag/) |

### Conventions for bilingual pages

- One static file per language, never a JavaScript toggle or `data-en` attributes: AI crawlers don't run
  JavaScript, so text swapped in by script is invisible to them.
- Swedish pages live under `sv/` with `<html lang="sv">` and link the stylesheet one level further up
  (`../../site.css`). The English page sits at the root.
- Each page links its counterpart with `<link rel="alternate" hreflang>` (sv, en, and x-default pointing at
  the English page) and with the visible `.lang-switch`, which is the last item in the `.site-nav` on every
  page. A Swedish page has a self-referencing canonical.
- The top nav is in the page's language. On Swedish pages "Tjänster" goes to `sv/digital-marknadsforing/`
  and "Verktyg" to `sv/`; the other items go to copyfororiginals.com, which is in English.
- Links on a Swedish page go to Swedish pages. Data files, scripts and run folders are not duplicated: a
  Swedish study links to the files in the English page's folder (`../../<english-slug>/data.csv`).
- The two versions carry the same facts, numbers, sources and dates, and the same HTML structure: same
  tags, same `id`s (the translated guides and tools keep the English `id`s so anchors match). Change both
  in the same commit. One page is generated (`haiku-vs-sonnet-vs-opus-research-study/` by its
  `method/build.py`): its Swedish page is a translation of the output, so a rebuild that changes text
  means the same edit in `sv/`.
- Word-for-word quotations from English-language sources stay in English on the Swedish page, wrapped in
  `<span lang="en">`, usually followed by a short Swedish gloss that starts with "ungefär:". They were
  checked against the sources in English; a translated quotation would no longer be one.
- Google Ads interface labels and tool names stay in English on Swedish pages. Dollar amounts are written
  `5&nbsp;000 USD`. In the tools, numbers printed by JavaScript keep the script's own formatting (`$5,000`).
- In the tools' JavaScript only the text shown to the user is translated. Ids, keys, CSS classes, report
  column names and the regular expressions that recognise uploaded reports are identical in both versions.
- Every question `<h2>`/`<h3>` and the paragraph under it is mirrored word for word in the FAQPage JSON-LD.
- Swedish pages carry no note about how the Swedish text was produced.
- Facts about the business (price, minimum fee, meeting area, managed ad spend) are repeated on the
  service pages in both languages, both homepages and `llms.txt`; a change to one of them means a search
  across all of them.
- A new page needs both versions, a card on both homepages, two `sitemap.xml` entries and its `llms.txt`
  entry.

## Analytics and cookie consent

[`consent.js`](consent.js) is the only script shared by every page. It shows a cookie banner (English, or Swedish
when `<html lang="sv">`) with equal Accept and Decline buttons and loads Google Analytics 4 (`G-443BVCGXJ1`,
the same property as copyfororiginals.com) only after Accept. Nothing is requested from Google before that.

- Consent Mode v2 defaults are all denied; Accept updates `analytics_storage` only. No ads signals on this site.
- The choice is stored for 180 days in the first-party cookie `cfo_consent` (`granted`/`denied`) on
  `.copyfororiginals.com`. Squarespace's `ss_performanceCookiesAllowed` is host-only on copyfororiginals.com,
  so the subdomain can't read it and asks again.
- Any link to `#cookie-settings` reopens the banner. Changing a granted choice to Decline deletes the `_ga*`
  cookies on the tools host and on `.copyfororiginals.com`.
- gtag.js loads only on `tools.copyfororiginals.com`. Local copies and the github.io mirror show the banner
  and set the consent cookie but never send hits.
- After Accept, `consent.js` adds a Content-Security-Policy that only lets requests go to Google Analytics
  hosts, because the Google tag also has the Google Ads account as a destination.
- **Rule: a page where visitors type, paste or upload data never includes `consent.js` and never loads
  Google Analytics.** That is the 18 pages with a Content-Security-Policy (upload tools and calculator guides)
  plus the PPC Gumball Rule, the personal injury budget calculator and the Script Timer, in both
  languages. Their footer text ("No tracking") stays as it was, and their "Cookie settings" link goes to the
  language homepage's `#cookie-settings`.
- Every footer ends with `<p class="legal">` (or `<span class="legal">` in the tools' flex footers): the
  privacy policy link and "Cookie settings" ("Integritetspolicy" and "Cookieinställningar" on Swedish pages).
  A new page with no inputs adds `<script src="../consent.js"></script>` (path like `site.css`) before `</body>`.
  The page builders in `method/` emit both. The two homepages also link the disclosure page in that line.

## Ads and affiliate links

Guides may carry affiliate links, and later ads; the rules and the list of programs joined are on
[`how-this-site-makes-money/`](how-this-site-makes-money/) and its Swedish twin. As of October 20, 2026 the
site has no affiliate links and no ads.

- **Never on input pages.** A page where visitors type, paste or upload data carries no ads and no affiliate
  links, the same pages the consent rule above keeps free of Google Analytics. Their "No tracking" footer
  stays true.
- **Ranking before programs.** A comparison's ranking is set from its data before joining any affiliate
  program, and a commission never changes it. Tools without a program get the same depth.
- **Mark every link.** Each affiliate link carries `rel="sponsored noopener"` and is followed by the words
  "paid link" ("betald länk" on Swedish pages), the label the FTC calls adequate right next to the link;
  "affiliate link" alone may not tell readers we're paid:
  `<a href="https://…" rel="sponsored noopener">Otterly</a> (paid link)`.
- **Disclose at the top.** A page with affiliate links opens with this block under the byline:

  ```html
  <p class="scope"><b>This page contains paid links.</b> If you buy through a link marked “paid link”, we may earn a commission at no cost to you. The ranking was set from the data before we joined any affiliate program. <a href="../how-this-site-makes-money/">How this site makes money</a>.</p>
  ```

  ```html
  <p class="scope"><b>Sidan innehåller betalda länkar.</b> Om du köper via en länk märkt ”betald länk” kan vi få en provision, utan extra kostnad för dig. Rangordningen bestämdes utifrån data innan vi gick med i något affiliateprogram. <a href="../sa-tjanar-sajten-pengar/">Så tjänar sajten pengar</a>.</p>
  ```

- **Disclose in the footer.** Its footer's first line reads:

  ```html
  <p>Static page. Google Analytics only if you accept cookies. Contains paid links, each marked; see <a href="../how-this-site-makes-money/">how this site makes money</a>. Made by <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a>.</p>
  ```

  ```html
  <p>Statisk sida. Google Analytics bara om du godkänner cookies. Innehåller betalda länkar, var och en märkt; se <a href="../sa-tjanar-sajten-pengar/">så tjänar sajten pengar</a>. Av <a href="https://copyfororiginals.com" rel="noopener">Copy for Originals</a>.</p>
  ```

- **When a program is joined,** add its row (program, date joined, what it pays) to the table on both
  disclosure pages, change their "None" answers, and update both pages' "Last updated" date.
- **Display ads are not set up.** Before any ad loads: `consent.js` must ask for advertising consent
  separately (today it grants `analytics_storage` only, and its CSP allows Google Analytics hosts only);
  Google's ad network needs a Google-certified consent tool for EEA and UK visitors; the privacy policy on
  copyfororiginals.com needs an ads section; and the disclosure pages' "Are there ads" answer changes first.

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
- Add the Swedish version under `sv/` (see "Conventions for bilingual pages") and its card on `sv/index.html`.

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
