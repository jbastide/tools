"""Pull every comment for the threads in raw/selected_ids.json (resumable).

Writes raw/comments/<id>.json = list of comments (body, created_utc, score, id, parent_id).
"""
import json, os, sys, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep import get, log, exit_ip, RAW  # noqa: E402

FIELDS = "id,link_id,parent_id,body,created_utc,score"


def pull(pid):
    out = os.path.join(RAW, "comments", f"{pid}.json")
    if os.path.exists(out):
        return
    seen, rows, after = set(), [], 1104537600  # 2005-01-01
    while True:
        d = get("comments/search", {"link_id": pid, "sort": "asc", "after": after,
                                    "limit": 100, "fields": FIELDS})
        data = d.get("data") or []
        new = [c for c in data if c["id"] not in seen]
        for c in new:
            seen.add(c["id"]); rows.append(c)
        time.sleep(3)
        if len(data) < 100 or not new:
            break
        after = max(c["created_utc"] for c in data) - 1
    with open(out, "w") as fh:
        json.dump(rows, fh)
    log(f"comments {pid}: {len(rows)}")


if __name__ == "__main__":
    os.makedirs(os.path.join(RAW, "comments"), exist_ok=True)
    sel = json.load(open(os.path.join(RAW, "selected_ids.json")))
    log(f"comments run start; {len(sel)} threads; exit IP {exit_ip()}")
    for i, pid in enumerate(sel):
        pull(pid)
    log(f"comments run end; exit IP {exit_ip()}")
