# Method files

Scripts and codebook behind “Useful diagnostic, terrible KPI”: what 200,753 Reddit posts say about measuring AI visibility (October 16, 2026). All ran on October 15, 2026 from an ordinary Swedish home connection against the Arctic Shift archive of Reddit (`https://arctic-shift.photon-reddit.com/api/`). The raw pull (about 130 MB of posts and comments) is not committed; the scripts rebuild it.

Pipeline, in order:

| Step | Script | What it does |
| --- | --- | --- |
| 1 | `sweep.py` | Lists every post from 2025-01-01 in each subreddit (`posts/search?subreddit=…&sort=asc&after=…&limit=100`), resumable, about 20 requests a minute. |
| 2 | `verify.py` | Compares local monthly counts with the archive’s own `aggregate` endpoint per subreddit and month. They matched for every month. |
| 3 | `filter.py` | Matches title and body against the term list (AEO, GEO, generative/answer engine, AI Overview(s), AI Mode, AI/LLM visibility, AI search, AI/LLM traffic, ChatGPT, Perplexity), the “core” rule (not matched only by ChatGPT or Perplexity), the measurement rule and the selection rules. Writes `monthly_counts.csv`. |
| 4 | `comments.py` | Pulls all comments for the selected threads (`comments/search?link_id=…`). |
| 5 | `dump_threads.py` | Writes readable thread dumps batched by size for the coders. |
| 6 | `CODEBOOK.txt` | The twelve problems, the relevance and healthcare flags, the Search Console report points, and the quote rules the coders followed. |
| 7 | `analyze.py` | Merges the coders’ JSON, checks every quote as an exact substring of the archived post or comment, writes `threads.csv` and the verified quotes (published as `quotes.csv`). |
| 8 | `gsc_themes.py` | Groups the coders’ points about Search Console’s generative AI report into nine themes by keyword rules; writes `gsc_report_themes.csv`. |
| 9 | `build.py` | Builds `../index.html` from the CSV files. Every number and quotation on the page comes from them. |

Coding was done twice with the same codebook: a first pass by Claude Sonnet 5.5 agents (`../first-pass/threads.csv`) and the published pass by Claude Opus 5.5 agents told to count a problem only when a participant discusses it in substance (`../threads.csv`). `../agreement.csv` holds percent agreement and Cohen’s kappa per problem. No person coded.

Data license: CC BY 4.0.
