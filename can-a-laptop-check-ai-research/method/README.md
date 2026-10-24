# Method files

| File | What it is |
| --- | --- |
| `prepare.py` | Writes `../planted.csv` and `../audit.csv` from the receipts repository (`bench/results/planted/` and the review of the agent-shopping research notes). |
| `build.py` | Writes `../index.html` from the two CSV files. The Swedish page is a translation of its output. |

The checker and the benchmark script (`bench/planted.py`) are in the receipts repository,
https://github.com/jbastide/receipts. The planted cases start from the graded claims in
`../../haiku-vs-sonnet-vs-opus-research-study/data.csv`.

Numbers on the page that are not in the CSV files are constants at the top of `build.py`:

- `REPRO_N`, `CONTROL_*`: receipts' reproduction of the model study's quote grades (`bench/model_study.py`).
- `REPORT_CLAIMS`, `REPORT_SOURCES`: the receipts run on `how-ai-agents-choose-products/research/synthesis.md`
  (112 claims, 87 links).
- `QUOTE_FIXES`, `EXTRA_FIXES`: from the correction of that file (pull request "Agent-shopping research
  notes: correct quotes and figures against sources"): 7 passages in quotation marks replaced by the
  sources' words, and 7 corrections found during the review outside the flagged items.

To repeat: `python3 prepare.py PATH_TO_RECEIPTS && python3 build.py YYYY-MM-DD`, then mirror any text
change in `sv/kan-en-laptop-granska-ai-research/`.
