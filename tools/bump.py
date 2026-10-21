#!/usr/bin/env python3
"""Set every "last updated" stamp on crisus.nl to HH:MM on a day (default: today):
the visible kicker, its <time datetime>, article:modified_time, the JSON-LD
dateModified and the sitemap lastmod, then rebuild feed.xml.
Usage: python3 -I bump.py 20:15 [2026-10-22]"""
import json, re, sys
from pathlib import Path

from datetime import date
hhmm = sys.argv[1]
assert re.fullmatch(r"[0-2]\d:[0-5]\d", hhmm), "use HH:MM [YYYY-MM-DD]"
day = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today()
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]
label = f"{day.day} {MAANDEN[day.month - 1]}"
iso = f"{day.isoformat()}T{hhmm}:00+02:00"
d = Path(__file__).resolve().parent.parent / "site"
page = d / "index.html"
t = page.read_text(encoding="utf-8")

subs = [
    (r'<time datetime="[0-9-]+T[0-9:]+\+0[12]:00">laatst bijgewerkt [0-9]+ [a-z]+, [0-9:]+</time>',
     f'<time datetime="{iso}">laatst bijgewerkt {label}, {hhmm}</time>'),
    (r'<meta property="article:modified_time" content="[^"]+">',
     f'<meta property="article:modified_time" content="{iso}">'),
    (r'"dateModified": "[^"]+"', f'"dateModified": "{iso}"'),
]
for pat, new in subs:
    t, n = re.subn(pat, new, t)
    assert n == 1, f"expected one match for {pat!r}, got {n}"
ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', t, re.S).group(1)
json.loads(ld)
page.write_text(t, encoding="utf-8")

sm = d / "sitemap.xml"
s, n = re.subn(r"(<loc>https://crisus.nl/</loc><lastmod>)[^<]+", rf"\g<1>{iso}", sm.read_text(encoding="utf-8"))
assert n == 1
sm.write_text(s, encoding="utf-8")
print("bumped to", iso)

import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "feed.py"), run_name="__main__")
