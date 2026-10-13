# Method files

Everything needed to re-check the study, apart from the run logs.

| File | What it is |
| --- | --- |
| `brief.md` | The brief every run received. `{FOLDER}` was replaced with a private folder path. |
| `brief-pilot.md` | The brief used in the pilot. It differs in rule 1, rule 8 and the last section. |
| `key.json` | The 25 known facts and the passages that count as stating each one. |
| `extras.json` | The 28 further findings, listed after the runs, matched by passage or website. |
| `pagetext.py` | Fetches a page once, caches it and returns its text. Reads Reddit threads from the Arctic Shift archive. |
| `verify.py` | Looks for every quote on the page it cites and matches claims to `key.json`. |
| `control.py`, `control.json` | Negative control: one word replaced in each quote, then checked again. |
| `blind.py`, `blind_map.csv` | Shuffles the claims and removes run labels for the graders. |
| `grader-rubric.md`, `grader1.json`, `grader2.json` | The grading rule and both graders' verdicts. |
| `usage.py`, `usage.csv` | Token use, tool calls, searches and estimated cost per run, read from the run logs. |
| `analyze.py` | Joins all of the above into `../data.csv`, `../runs.csv`, `../facts.csv` and `../sources.csv`. |
| `build.py` | Writes `../index.html` from the CSV files. |

To repeat the checks on the published outputs:

```
python3 verify.py      # fetches the cited pages; needs curl and pdftotext
python3 control.py
python3 analyze.py
python3 build.py
```

Pages change, so a later run of `verify.py` may not find every quote.

Not published: the run logs that `usage.py` reads. They hold the full tool traffic of each agent.
`usage.csv` is the output of that script. Its two audit columns list any tool call that mentioned
our own site or a path outside the run's folder. The three Opus rows show our domain name because
those runs checked their own output for it before finishing.

Cost columns are estimates at Anthropic's list prices on October 13, 2026. The logs record input,
cache-write and cache-read tokens for every response. They do not record a final output count, so
output tokens are estimated from visible text at 3.5 characters per token, and hidden reasoning is
not counted. Web searches are priced at $0.01 each.
