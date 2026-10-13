# Rule used by both blind graders

Each grader read `blind_review.txt`: all 593 claims in shuffled order, each with its quote and the
website it came from, and no model or run label. `blind.py` makes that file and `blind_map.csv` maps
each blind ID back to its run. Every quote had already passed the machine check, so the graders
judged one thing: does the quote, read on its own, back up the claim?

- **OK**: the quote shows the main thing the claim asserts. Source details in the claim (who wrote
  it, on which site or page, when) do not need to appear in the quote. A statement that something is
  absent ("legal services are not named") or a clearly marked inference is OK when the quote shows
  the positive part it rests on. A general gloss or paraphrase of the quoted words is OK.
- **PART**: the quote shows one fact in the claim, but the claim also states another specific fact of
  substance that the quote does not show: a second rule, an exception, a condition, a step in a path,
  a number, or listed items.
- **NOT**: the quote, read on its own, does not show the claim's main assertion. Examples: the quote
  is cut off before the operative words, or it is about something else.

Grader 1 was the Claude Opus 5.5 session that ran the study (`grader1.json`). Grader 2 was a separate
Claude Sonnet 5.5 agent given this rule (`grader2.json`). Items not listed in a file were graded OK.
The page counts a claim as flagged when both graders marked it PART or NOT.
