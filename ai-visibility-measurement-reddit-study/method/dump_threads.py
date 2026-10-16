"""Write readable thread dumps for coding, batched by size: coding/batch_<prefix>NN.txt.

Only threads whose comments are downloaded and that are not yet in any batch are dumped,
so it can be run again as more comments arrive. coding/manifest.json maps batch -> ids.
Each comment is labelled with its id so coders can cite the exact source of a quote.
"""
import json, os, glob, datetime, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(ROOT, "coding")
PREFIX = sys.argv[1]
MAXCH = int(sys.argv[2]) if len(sys.argv) > 2 else 120000
MAXN = int(sys.argv[3]) if len(sys.argv) > 3 else 999

posts = {}
for f in glob.glob(os.path.join(RAW, "posts_*.jsonl")):
    for l in open(f):
        p = json.loads(l); posts[p["id"]] = p
sel = json.load(open(os.path.join(RAW, "selected_ids.json")))
os.makedirs(OUT, exist_ok=True)
mpath = os.path.join(OUT, "manifest.json")
manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
done = {i for ids in manifest.values() for i in ids}


def render(pid):
    p = posts[pid]
    d = datetime.datetime.utcfromtimestamp(p["created_utc"]).date()
    s = (f"\n=========== THREAD {pid} | r/{p['subreddit']} | {d} | {p.get('num_comments')} comments\n"
         f"TITLE: {p['title']}\n[post] {p.get('selftext') or ''}\n")
    for c in json.load(open(os.path.join(RAW, "comments", f"{pid}.json"))):
        body = c.get("body") or ""
        if body in ("[deleted]", "[removed]"):
            continue
        cd = datetime.datetime.utcfromtimestamp(c["created_utc"]).date()
        s += f"[c:{c['id']} {cd}] {body}\n"
    return s


ready = [i for i in sel if i not in done and os.path.exists(os.path.join(RAW, "comments", f"{i}.json"))]
batches, cur, size = [], [], 0
for pid in ready:
    r = render(pid)
    if cur and (size + len(r) > MAXCH or len(cur) >= MAXN):
        batches.append(cur); cur, size = [], 0
    cur.append((pid, r)); size += len(r)
if cur:
    batches.append(cur)
for n, b in enumerate(batches):
    name = f"batch_{PREFIX}{n:02d}"
    with open(os.path.join(OUT, name + ".txt"), "w") as fh:
        fh.write("".join(r for _, r in b))
    manifest[name] = [pid for pid, _ in b]
    print(name, len(b), sum(len(r) for _, r in b))
json.dump(manifest, open(mpath, "w"), indent=1)
print("not ready:", len([i for i in sel if i not in done and i not in ready]))
