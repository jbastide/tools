"""Fetch a URL once, cache it, and return normalised page text."""
import hashlib, html, json, os, re, subprocess, sys, unicodedata

CACHE = os.environ.get("OSINT_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache"))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")

def fetch_url(url):
    """Returns (status, content_type, path). English help pages are requested with hl=en."""
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    body, meta = os.path.join(CACHE, key + ".body"), os.path.join(CACHE, key + ".json")
    if os.path.exists(meta):
        m = json.load(open(meta))
        return m["status"], m["ctype"], body
    target = url
    if "support.google.com" in url and "hl=" not in url:
        target = url.split("#")[0] + ("&" if "?" in url else "?") + "hl=en"
    out = subprocess.run(
        ["curl", "-sL", "-m", "40", "--compressed", "-A", UA,
         "-H", "Accept-Language: en-US,en;q=0.9",
         "-o", body, "-w", "%{http_code}\t%{content_type}", target],
        capture_output=True, text=True).stdout
    status, _, ctype = out.partition("\t")
    json.dump({"url": url, "fetched": target, "status": status, "ctype": ctype}, open(meta, "w"))
    return status, ctype, body

def reddit_text(url):
    """Reddit refuses plain requests, so a thread is read from the Arctic Shift archive instead."""
    m = re.search(r"reddit\.com/r/[^/]+/comments/([a-z0-9]+)", url)
    if not m:
        return "000", ""
    tid, parts = m.group(1), []
    for api in (f"https://arctic-shift.photon-reddit.com/api/posts/ids?ids={tid}",
                f"https://arctic-shift.photon-reddit.com/api/comments/search?link_id={tid}&limit=100"):
        status, _, body = fetch_url(api)
        if status != "200":
            return status, ""
        try:
            for item in json.load(open(body)).get("data", []):
                parts += [str(item.get(k, "")) for k in ("title", "selftext", "body")]
        except Exception:
            return "000", ""
    return "200", "\n".join(parts)

def norm(s):
    """Case-fold, straighten quotes and dashes, collapse whitespace."""
    s = unicodedata.normalize("NFKC", html.unescape(s))
    for a, b in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("‑", "-"), (" ", " "), ("​", "")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()

def loose(s):
    """Letters and digits only: ignores spacing, punctuation and case."""
    return re.sub(r"[^a-z0-9]+", "", norm(s))

def words(s):
    return re.findall(r"[a-z0-9]+", norm(s))

def page_text(url):
    if "reddit.com/" in url:
        return reddit_text(url)
    status, ctype, body = fetch_url(url)
    if not os.path.exists(body):
        return status, ""
    raw = open(body, "rb").read()
    if raw[:5] == b"%PDF-" or "pdf" in ctype:
        txt = subprocess.run(["pdftotext", "-layout", body, "-"], capture_output=True, text=True).stdout
        return status, txt
    t = raw.decode("utf-8", "replace")
    if t.lstrip()[:1] in "{[":          # JSON endpoints: keep every string value
        return status, t.replace("\\n", " ").replace('\\"', '"')
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return status, html.unescape(t)

if __name__ == "__main__":
    st, tx = page_text(sys.argv[1])
    print(st, len(tx)); print(re.sub(r"\s+", " ", tx)[:int(sys.argv[2]) if len(sys.argv) > 2 else 600])
