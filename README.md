# tools

Small, single-purpose static web tools. Every page is self-contained: one HTML file with
inline CSS and vanilla JS, no build step, no dependencies, no network requests at runtime.

## Contents

| Tool | Path | What it does |
| --- | --- | --- |
| Short-Form Script Pacing & Hook Timer | [`script-timer/`](script-timer/) | Times a short-form video script in real time, splits it into retention zones (3s / 15s / 30s / 60s), and grades the hook against first-sentence lengths measured in 132 top YouTube Shorts (green inside 3s, note to 5s, warning past 5s). Default pace is the measured 193 WPM median. |
| Keyword Triage (Google Ads keyword profitability checker) | [`keyword-triage/`](keyword-triage/) | Reads a Google Ads or Microsoft Ads keyword report (CSV, TSV or Excel) and sorts each keyword into Cut, Trim bids, Keep, Scale or Needs data against a target CPA or ROAS. A Content-Security-Policy blocks every network request, so the report can't leave the browser. |

## Guides

| Guide | Path | What it covers |
| --- | --- | --- |
| How to write content that LLMs retrieve and cite | [`rag-friendly-content/`](rag-friendly-content/) | What answer engines do with a page, each AEO practice rated by evidence, and a 12-point checklist. |

## Deploying

GitHub Pages serves this repo as-is from the default branch:

1. **Settings → Pages → Build and deployment → Source: _Deploy from a branch_**
2. Branch `main`, folder `/ (root)`, then Save.

Pages then serves:

- `https://jbastide.github.io/tools/` — the index
- `https://jbastide.github.io/tools/script-timer/` — the script timer
- `https://jbastide.github.io/tools/keyword-triage/` — the keyword triage tool

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
- Keep it dependency-free. No CDNs — they can be blocked by ad blockers or go down.
- Include a `<title>`, a meta description, and a `SoftwareApplication` JSON-LD block.
- Support light and dark via `prefers-color-scheme`.
- Add a row to the table above, a card to the root `index.html`, and entries to `sitemap.xml` and `llms.txt`.

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
