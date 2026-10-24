# By-hand runs: Ahrefs and Mangools

Both sites' terms ban automated use (Ahrefs terms cl. 4.4(j); Mangools terms §9), so a person runs these
two checkers in their own browser. The agent only reads the files saved here. Runs from this folder are
labelled "run by a person" on the page.

## Rounds

Three rounds, each on a different day, at least 24 hours apart (for example October 22, 23 and 24, 2026).
One round = the 10 firms below in Ahrefs, then the same 10 in Mangools: 20 checks, about 30 to 40 minutes.

## The 10 firms

Enter the name exactly as written in the "Name to enter" column.

| ID | Name to enter | Website (only if a tool asks for a domain) |
| --- | --- | --- |
| F01 | Malman Law | malmanlaw.com |
| F02 | 844SeeMike | 844seemike.com |
| F03 | Flanagan Injury Law Group | windycityinjury.com |
| F04 | Disparti Law Group | dispartilaw.com |
| F05 | The Horwitz Law Group | chicago-personal-injury-lawyers.us |
| F06 | McCreadyLaw | mccreadylaw.com |
| F07 | Anesi Ozmon | anesilaw.com |
| F08 | Postman Law | postmanlaw.com |
| F09 | Saks, Robinson & Rittenberg | cookcountyinjurylaw.com |
| F10 | Rundio Injury Law | rundiolaw.com |

## Ahrefs free AI visibility checker

URL: https://ahrefs.com/ai-visibility-checker (https://ahrefs.com/free-ai-visibility redirects or is the old address)

1. Enter the firm's name from the table. If it asks for a domain, use the website column. If it asks for a
   country or location, choose United States. Leave every other option at its default.
2. Note the time you clicked, and the time the result finished loading.
3. When the result is complete, save it twice:
   - `Cmd+P` → "Save as PDF" → `ahrefs_F01_r1.pdf` (the PDF keeps all the text, which is what gets transcribed)
   - a screenshot of the top of the result (`Cmd+Shift+4`) → `ahrefs_F01_r1.png`
4. If a section has tabs (ChatGPT, Gemini, Perplexity, Copilot, AI Overviews, AI Mode), click through each one
   and save one PDF per tab: `ahrefs_F01_r1_chatgpt.pdf`, `ahrefs_F01_r1_gemini.pdf`, and so on.
5. If it shows a signup wall, a limit message or a CAPTCHA, screenshot it (`ahrefs_F01_r1_wall.png`), note it
   in the log, and stop that tool for the day. Don't solve the CAPTCHA just to keep going: write down that it
   appeared.

## Mangools AI Search Grader

URL: https://mangools.com/ai-search-grader

1. Decide once per round: signed in to the free Mangools account (all 7 models) or logged out (3 models).
   Use the same choice every round if you can, and put it in the log's `signed_in` column.
2. "Your brand (product or service)": the firm's name from the table.
   "Description (niche)": `Personal injury law firm in Chicago, Illinois` (same text for all 10 firms;
   don't use "Autosuggest").
3. Click "Grade My Brand" and note the start and end times.
4. Save `Cmd+P` → "Save as PDF" → `mangools_F01_r1.pdf`, plus a screenshot of the score and the prompts table →
   `mangools_F01_r1.png`. If there's a per-model view, save one PDF per model: `mangools_F01_r1_chatgpt.pdf`, etc.
5. If it shows a limit ("usage is limited" on the logged-out tier), screenshot it as `mangools_F01_r1_wall.png`,
   note it in the log, and carry on the next day.

## Where to save and how to name files

Save everything in this folder:
`/Users/jesse/dev/tools/.claude/worktrees/eager-chandrasekhar-a7bfc4/free-ai-visibility-checkers-tested/runs/by-hand/`

Pattern: `<tool>_<firm ID>_r<round>[_<model or wall>].<pdf|png>`, for example `mangools_F07_r2.pdf`.

## Log

Fill in one row per check in `log.csv` in this folder (rows are pre-filled): date (YYYY-MM-DD), start time
(HH:MM, your local time), minutes from click to finished result, signed in (yes/no), any limit or wall seen,
and notes. A rough note in a text file is fine too: `notes_r1.txt`.
