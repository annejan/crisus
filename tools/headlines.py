#!/usr/bin/env python3
"""Headlines about the current crisus topics since the last update on the page.
Usage: python3 -I tools/headlines.py [--hours N]"""
import argparse, email.utils, html, re, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

FEEDS = {
    # Dutch news and the NCSC
    "Security.NL": "https://www.security.nl/rss/headlines.xml",
    "NOS Tech": "https://feeds.nos.nl/nosnieuwstech",
    "NOS": "https://feeds.nos.nl/nosnieuwsalgemeen",
    "Tweakers": "https://feeds.feedburner.com/tweakers/mixed",
    "NCSC": "https://advisories.ncsc.nl/rss/advisories",
    # International security press
    "heise": "https://www.heise.de/security/rss/news-atom.xml",
    "The Register": "https://www.theregister.com/security/headlines.atom",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "SecurityWeek": "https://www.securityweek.com/feed/",
    "Help Net Security": "https://www.helpnetsecurity.com/feed/",
    # CERTs and governments
    "CISA": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "CERT-FR": "https://www.cert.ssi.gouv.fr/feed/",
    "CERT-Bund": "https://wid.cert-bund.de/content/public/securityAdvisory/rss",
    # Vendors and distributions
    "Ubuntu USN": "https://ubuntu.com/security/notices/rss.xml",
    "Fortinet": "https://filestore.fortinet.com/fortiguard/rss/ir.xml",
    "Cisco": "https://sec.cloudapps.cisco.com/security/center/psirtrss20/CiscoSecurityAdvisory.xml",
    "AWS": "https://aws.amazon.com/security/security-bulletins/rss/feed/",
    "Cloudflare": "https://blog.cloudflare.com/rss/",
    "FreeBSD": "https://vuxml.freebsd.org/freebsd/rss.xml",
    "Gentoo": "https://security.gentoo.org/glsa/feed.rss",
    # Researchers and the PHP project itself
    "watchTowr": "https://labs.watchtowr.com/rss/",
    "Wiz": "https://www.wiz.io/feed/rss.xml",
    "php.announce": ("https://news-web.php.net/group.php?group=php.announce&format=rss", r"secur|release|cve"),
    "externals": ("https://externals.io/rss", r"secur|cve|vulnerab|exploit|php2shell|bailout|double.free|use.after"),
}
TOPICS = re.compile(r"\bphp|php2shell|tcp2shell|claude code|2\.1\.313|98432|mptcp|binance|bybit|brotli|http2shell|node2shell|111497|pwnescape|gitlab|overheid\.nl|digid|qnap|synology|pan-os|palo alto|fortinet|emudhra", re.I)
ATOM = "{http://www.w3.org/2005/Atom}"


def parse_date(s):
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)   # some feeds leave out the zone


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
    url, topics = (url[0], re.compile(url[1], re.I)) if isinstance(url, tuple) else (url, TOPICS)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; crisus.nl headlines; +https://crisus.nl/)"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=25).read())
    except Exception as e:
        print(f"  ({name}: {type(e).__name__})")
        continue
    for it in root.iter("item"):
        title, link = it.findtext("title") or "", it.findtext("link") or ""
        d = parse_date(it.findtext("pubDate"))
        if d and d > since and topics.search(title + " " + (it.findtext("description") or "")):
            rows.append((d, name, title, link))
    for it in root.iter(ATOM + "entry"):
        title = it.findtext(ATOM + "title") or ""
        el = it.find(ATOM + "link")
        d = parse_date(it.findtext(ATOM + "updated") or it.findtext(ATOM + "published"))
        if d and d > since and topics.search(title + " " + (it.findtext(ATOM + "summary") or "")):
            rows.append((d, name, title, el.get("href") if el is not None else ""))

print(f"== headlines since {since.astimezone().strftime('%d-%m %H:%M')}")
per_feed = {}
shown = []
for row in sorted(rows, reverse=True):          # at most 4 per feed: CERT-Bund updates a dozen at once
    per_feed[row[1]] = per_feed.get(row[1], 0) + 1
    if per_feed[row[1]] <= 4:
        shown.append(row)
for d, name, title, link in shown[:25]:
    title = re.sub(r"\s+", " ", html.unescape(title)).strip()
    print(f"  {d.astimezone().strftime('%H:%M')} {name}: {title}\n         {link}")
if not rows:
    print("  (nothing new on these topics)")
