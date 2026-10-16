"""Compare local monthly post counts with Arctic Shift's server-side monthly aggregate.

The aggregate bins by Europe/Stockholm month starts (e.g. 2024-12-31T23:00Z), so local
posts are binned the same way here. Writes raw/verify.csv and prints mismatches.
"""
import json, os, sys, glob, time, csv, datetime, collections
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import get, RAW  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
rows = []
for f in sorted(glob.glob(os.path.join(RAW, "posts_*.jsonl"))):
    sub = os.path.basename(f)[6:-6]
    local = collections.Counter()
    for l in open(f):
        ts = json.loads(l)["created_utc"]
        local[datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m")] += 1
    # quarterly windows: the full-range aggregate times out on big subs
    data = []
    starts = [f"{y}-{m:02d}-01" for y in (2025, 2026) for m in (1, 4, 7, 10)] + ["2027-01-01"]
    for a, b in zip(starts, starts[1:]):
        if a > "2026-10-16":
            break
        # ISO dates are read as UTC; epoch values returned no data. Buckets are UTC months
        # labelled with the Stockholm-time start (2024-12-31T23:00Z = January).
        d = get("posts/search/aggregate", {"aggregate": "created_utc", "frequency": "month",
                                           "subreddit": sub, "after": a, "before": min(b, "2026-10-15")})
        data += d.get("data") or []
        time.sleep(3)
    server = collections.Counter()
    for r in data:
        dt = datetime.datetime.fromisoformat(r["created_utc"].replace("Z", "+00:00")).astimezone(TZ)
        server[dt.strftime("%Y-%m")] += int(r["count"])
    for m in sorted(set(local) | set(server)):
        rows.append([sub, m, local.get(m, 0), server.get(m, 0)])
        if local.get(m, 0) != server.get(m, 0):
            print("MISMATCH", sub, m, local.get(m, 0), server.get(m, 0))
    print(sub, "local", sum(local.values()), "server", sum(server.values()))
with open(os.path.join(RAW, "verify.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["subreddit", "month_utc", "local", "server"]); w.writerows(rows)
