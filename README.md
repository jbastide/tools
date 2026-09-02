# tools

Small, single-purpose static web tools. Every page is self-contained: one HTML file with
inline CSS and vanilla JS, no build step, no dependencies, no network requests at runtime.

## Contents

| Tool | Path | What it does |
| --- | --- | --- |
| Short-Form Script Pacing & Hook Timer | [`script-timer/`](script-timer/) | Times a short-form video script in real time, splits it into retention zones (3s / 15s / 30s / 60s), and warns when the hook runs past three seconds. |

## Deploying

GitHub Pages serves this repo as-is from the default branch:

1. **Settings → Pages → Build and deployment → Source: _Deploy from a branch_**
2. Branch `main`, folder `/ (root)`, then Save.

Pages then serves:

- `https://jbastide.github.io/tools/` — the index
- `https://jbastide.github.io/tools/script-timer/` — the script timer

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
- Add a row to the table above and a card to the root `index.html`.
