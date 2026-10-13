# AI Overview citation experiment: log

Dated notes on the experiment's pages. The arms are listed in [`README.md`](README.md).

## 2026-10-13: control page baseline, then control retired

The control page, [`law-firm-google-ads-faq/`](law-firm-google-ads-faq/), is being retitled and linked
under the new hub [`google-ads-for-law-firms/`](google-ads-for-law-firms/). After that change it is no
longer a formatting-only control. This entry records its state before the change.

### The page as it stood

| Item | Value |
| --- | --- |
| URL | `https://tools.copyfororiginals.com/law-firm-google-ads-faq/` |
| Published | 2026-10-05 (commit `632d029`) |
| Last content state | commit `2433840` (2026-10-06, navigation only); 8 days live at baseline |
| `<title>` | Google Ads for Law Firms: Conversion Rate, Target CPA, Broad Match and Negative Keywords |
| `<h1>` | Google Ads for law firms: five short answers |
| Internal links pointing to it | The root index card only. No other page linked to it. |
| Structured data | `Article`, `FAQPage` (5 questions), `BreadcrumbList` |
| Live check | Fetched 2026-10-13: served the title, H1 and five question H2s above |

### Search visibility on 2026-10-13

Each query was run once through Claude Code's web search tool. That tool is not Google's results page
and does not show AI Overviews, so "not returned" here means only that the page was absent from the
nine or ten results the tool returned.

| Query | Control page returned? | Any tools.copyfororiginals.com page? |
| --- | --- | --- |
| what is a good conversion rate for law firm Google Ads | No | No |
| how many conversions does Target CPA need law firm | No | No |
| should law firms use broad match keywords Google Ads | No | No |
| what negative keywords should a law firm use Google Ads | No | No |
| should a law firm use Maximize conversions or Target CPA | No | No |
| google ads for law firms | No | No |
| site:tools.copyfororiginals.com law firm google ads | No | No (the tool ignored the `site:` filter) |

Result: zero appearances in seven queries, eight days after publication.

### Not measured

These need a person with access, and should be exported before the retitle is deployed:

- Google Search Console: impressions, clicks and average position for the control URL, and whether it
  is indexed (URL Inspection).
- Google AI Overviews and AI Mode: whether the control URL is cited for the five questions.
- ChatGPT, Perplexity and Claude with search on: whether the control URL is cited for the five questions.

### What changed on 2026-10-13

- `<title>` and `<h1>` now lead with the questions instead of "Google Ads for Law Firms", so the page
  does not compete with the hub for that query.
- The page links up to the hub, and the hub links down to it.
- A one-line "Educational only, not legal advice" note was added under the byline.
- The five answers and the FAQPage text are unchanged.

The other arms (`ppc-gumball-rule/`, `ppc-no-conversions-study/`, `personal-injury-google-ads-budget/`)
keep their text. The hub links to the budget page, which other law firm pages already link to, and
does not link to the Gumball Rule page or the forum study.

## 2026-10-13: "gumball rule" name cross-check, and citation status at 8 days

Question: does a generally accepted "gumball rule" exist that conflicts with the PPC Gumball Rule?

### Result: no established "gumball rule" exists anywhere

Searched the exact phrases "gumball rule", "the gumball rule", "gumball principle", "gumball theory" and
"PPC Gumball Rule" through Claude Code's web search, Bing, Brave and Yahoo (Yahoo returned an error).
Nothing defines a gumball rule. What the word "gumball" does return, in order of volume:

| What | Meaning | Conflict with ours? |
| --- | --- | --- |
| *The Amazing World of Gumball* (cartoon) | Fan "rules", memes, wiki rules | No, but it drowns every "gumball rule" query |
| Gumball (gumball.fm) | Host-read podcast ad marketplace from Headgum | No, but it owns "gumball advertising" queries |
| Feige's gumball machines problem (Winkler, CACM 2009) | Probability puzzle about the chance of exceeding n gumballs from n machines | No, different math (expected value, not zero events) |
| Brandon Mulrenin, "red and blue gumball" analogy | Cold-call prospecting: most prospects are red gumballs, the rare blue one is a real opportunity, sort rather than persuade | No, it's compatible (rare gumball = conversion) but it has no stopping rule |
| Clairification "Gumball Theory" (2020) | Nonprofit fundraising: treating donors as disposable | No |

The r/PPC thread the page cites (30 comments, fetched via the Pullpush archive) uses "3x rule" for 95%
and "5x CPA rule" for 99% and never uses the word "gumball". So the name is ours alone and the math it
names is the thread's own rule of thumb plus the statistical rule of three. There is no competing
reading to reconcile. An answer engine asked "what is the gumball rule" today has no source and will
guess, which is the likely origin of any differing definition seen.

### Citation and indexing status, 2026-10-13 (8 days after publication)

| Check | Result |
| --- | --- |
| Claude web search, "PPC Gumball Rule" (exact) | Not returned |
| Claude web search, exact H1 of the rule page | Not returned |
| Claude web search, "how many clicks without a conversion is normal google ads" | Not returned |
| Claude web search, "how much should a personal injury law firm spend on google ads" | Not returned (rankings.io, Walker, Hennessey returned) |
| Bing `url:tools.copyfororiginals.com/ppc-gumball-rule/` | Not indexed (unrelated results) |
| Bing `url:https://www.copyfororiginals.com/about` | "No results", so Bing's coverage of the main domain is thin too, or the operator is unreliable |
| Brave `site:tools.copyfororiginals.com` | "Too few matches were found" |
| robots.txt | Allows all crawlers, sitemap declared |
| Rule page live | Yes, title and H1 served |

Not measured, needs a person with access: Google Search Console indexing for the three arm URLs, and
AI Overview / AI Mode / ChatGPT / Perplexity citations for the arm questions. Google indexing could not be
checked from this environment.

### Change on 2026-10-13: disambiguation line on the rule page

Added one paragraph to the "What is the PPC Gumball Rule?" section of `ppc-gumball-rule/` stating it is
the only gumball rule in advertising, coined October 5, 2026, unrelated to the Gumball podcast ad
marketplace, the cartoon, or Feige's gumball machines puzzle, and naming the "red and blue gumball"
prospecting analogy as the nearest relative (odds without a checkpoint). The same sentence, shortened, was
appended to the DefinedTerm description in the JSON-LD. The rule, tables, calculator and FAQ text are
unchanged. Modified dates and the sitemap lastmod bumped to 2026-10-13.

### Change on 2026-10-13: hub now links to the rule page

At Jesse's request, `google-ads-for-law-firms/` links to `ppc-gumball-rule/` in three places: the
budget section's 95% sentence, the "how can a firm tell if it's working" paragraph, and the guides table.
The rule page is therefore no longer an unlinked arm; only `ppc-no-conversions-study/` remains unlinked
from the law firm pages.

### Change on 2026-10-13: hub now links to the forum study

At Jesse's request, `google-ads-for-law-firms/` links to `ppc-no-conversions-study/` in the "how can a
firm tell if it's working" paragraph (the 3 of 62 and median 190 clicks figures) and in the guides table.
All three experiment arms are now linked from the hub; none of the arm pages' text changed.

### 2026-10-13: hub guides-table audit after the parallel sessions

Compared every law firm page in `sitemap.xml` against the links in `google-ads-for-law-firms/`. All
experiment arms and all pages added by the parallel sessions on October 13 were already linked, except
`law-firm-websites-ai-crawlers-study/`, which was in the index, README, llms.txt and sitemap but not the
hub. Added one guides-table row for it. The Gumball Rule (3 links) and forum study (2 links) survived
every rewrite and commit of the hub that day.
