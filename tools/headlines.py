#!/usr/bin/env python3
"""Headlines about the current crisus topics since the last update on the page.
Usage: python3 -I tools/headlines.py [--hours N]"""
import argparse, email.utils, html, re, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

FEEDS = {
    "Security.NL": "https://www.security.nl/rss/headlines.xml",
    "NOS Tech": "https://feeds.nos.nl/nosnieuwstech",
    "NOS": "https://feeds.nos.nl/nosnieuwsalgemeen",
    "Tweakers": "https://feeds.feedburner.com/tweakers/mixed",
    "NCSC": "https://advisories.ncsc.nl/rss/advisories",
    "heise": "https://www.heise.de/security/rss/news-atom.xml",
}
TOPICS = re.compile(r"\bphp|php2shell|pwnescape|gitlab|overheid\.nl|digid", re.I)
ATOM = "{http://www.w3.org/2005/Atom}"


def parse_date(s):
    if not s:
        return None
    try:
        return email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None


ap = argparse.ArgumentParser()
ap.add_argument("--hours", type=float)
a = ap.parse_args()
if a.hours:
    since = datetime.now(timezone.utc) - timedelta(hours=a.hours)
else:
    page = (Path(__file__).resolve().parent.parent / "site" / "index.html").read_text(encoding="utf-8")
    since = datetime.fromisoformat(re.search(r'"dateModified": "([^"]+)"', page).group(1))

rows = []
for name, url in FEEDS.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "crisus.nl headlines (+https://crisus.nl/)"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=25).read())
    except Exception as e:
        print(f"  ({name}: {type(e).__name__})")
        continue
    for it in root.iter("item"):
        title, link = it.findtext("title") or "", it.findtext("link") or ""
        d = parse_date(it.findtext("pubDate"))
        if d and d > since and TOPICS.search(title + " " + (it.findtext("description") or "")):
            rows.append((d, name, title, link))
    for it in root.iter(ATOM + "entry"):
        title = it.findtext(ATOM + "title") or ""
        el = it.find(ATOM + "link")
        d = parse_date(it.findtext(ATOM + "updated") or it.findtext(ATOM + "published"))
        if d and d > since and TOPICS.search(title + " " + (it.findtext(ATOM + "summary") or "")):
            rows.append((d, name, title, el.get("href") if el is not None else ""))

print(f"== headlines since {since.astimezone().strftime('%d-%m %H:%M')}")
for d, name, title, link in sorted(rows, reverse=True)[:20]:
    title = re.sub(r"\s+", " ", html.unescape(title)).strip()
    print(f"  {d.astimezone().strftime('%H:%M')} {name}: {title}\n         {link}")
if not rows:
    print("  (nothing new on these topics)")
