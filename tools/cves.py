#!/usr/bin/env python3
"""New CVEs with a high score, from the official CVE list (CVEProject/cvelistV5).
The NVD scores only a few of them these days, so this reads the score the CNA itself
gave, and the CISA ADP enrichment (score and SSVC exploitation) where there is one.
Usage: python3 -I tools/cves.py [--hours N] [--min SCORE]   (default: 1.25 hours, 7.0)"""
import argparse, gzip, json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

DELTALOG = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/deltaLog.json"
CVSS = ("cvssV4_0", "cvssV3_1", "cvssV3_0", "cvssV2_0")

ap = argparse.ArgumentParser()
ap.add_argument("--hours", type=float, default=1.25)  # an hourly round, with some overlap
ap.add_argument("--min", type=float, default=7.0)
args = ap.parse_args()


def get(url):
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "crisus.nl"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
        return json.loads(gzip.decompress(body) if r.headers.get("Content-Encoding") == "gzip" else body)


# The delta log (the last 30 days, gzipped about 2 MB): every CVE that is new since the cutoff
cut = datetime.now(timezone.utc) - timedelta(hours=args.hours)
new = {}
for delta in get(DELTALOG):
    if datetime.fromisoformat(delta["fetchTime"].replace("Z", "+00:00")) >= cut:
        for c in delta.get("new", []):
            new[c["cveId"]] = c["githubLink"]


def score(rec):
    """The highest base score from the CNA and the ADPs, with where it came from, and
    the SSVC exploitation that CISA gives (none, poc, active)."""
    best, src, exploit = 0.0, "", ""
    cna = rec["containers"].get("cna", {})
    for who, cont in [("CNA", cna)] + [(a.get("providerMetadata", {}).get("shortName", "ADP"), a)
                                         for a in rec["containers"].get("adp", [])]:
        for m in cont.get("metrics", []):
            for k in CVSS:
                s = m.get(k, {}).get("baseScore")
                if s and s > best:
                    best, src = s, f"{who} {k[4:].replace('_', '.')}"
            for o in [m.get("other", {})]:
                if o.get("type") == "ssvc":
                    for opt in o.get("content", {}).get("options", []):
                        exploit = opt.get("Exploitation", exploit)
    aff = (cna.get("affected") or [{}])[0]
    what = f"{aff.get('vendor', '?')} {aff.get('product', '?')}"
    title = cna.get("title") or next((d["value"] for d in cna.get("descriptions", []) if d.get("lang", "").startswith("en")), "")
    return best, src, exploit, what, " ".join(title.split())[:110]


def fetch(item):
    cve, url = item
    try:
        return (cve,) + score(get(url))
    except Exception as e:  # one broken record should not stop the list
        return (cve, 0.0, f"error: {e}", "", "", "")


with ThreadPoolExecutor(8) as pool:
    rows = list(pool.map(fetch, new.items()))

high = sorted((r for r in rows if r[1] >= args.min), key=lambda r: -r[1])
crit = sum(1 for r in rows if r[1] >= 9.0)
print(f"== CVE: {len(rows)} new in {args.hours:g} h, {crit} critical (>= 9.0), "
      f"{len(high)} at >= {args.min:g}, {sum(1 for r in rows if not r[1])} without a score")
for cve, s, src, exploit, what, title in high:
    flag = f"  EXPLOITATION: {exploit.upper()}" if exploit in ("active", "poc") else ""
    print(f"{s:4.1f} {cve:<17} {what[:40]:<40} {title}  [{src}]{flag}")
