"""Negative control for the quote checker: damage every quote and confirm it is no longer accepted.

Test 1 replaces one word in each quote. Test 2 checks each quote against a page it was not taken from.
Usage: python3 control.py   (after verify.py; reads claims_checked.csv, writes control.json)
"""
import csv, json, os, random
from pagetext import page_text, loose, words
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, "claims_checked.csv"))))
random.seed(7)
pages = {}
def text(u):
    if u not in pages:
        pages[u] = loose(page_text(u)[1])
    return pages[u]
swap = cross = n = 0
for r in rows:
    w = r["quote"].split()
    if len(w) < 6:
        continue
    n += 1
    w[random.randrange(1, len(w) - 1)] = "zebra"
    swap += loose(" ".join(w)) in text(r["url"])
    other = random.choice([x for x in rows if x["url"] != r["url"]])
    cross += loose(other["quote"]) in text(r["url"])
out = {"quotes_tested": n, "accepted_after_one_word_replaced": swap, "accepted_against_a_different_page": cross}
json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1); print(out)
