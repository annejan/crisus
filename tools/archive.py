#!/usr/bin/env python3
"""Freeze the current front page as a closed crisis under /<slug>/.

The copy keeps every update and its anchors; its URLs (canonical, og:url,
JSON-LD, the update permalinks) move to https://crisus.nl/<slug>/, the live blog
gets a coverageEndTime and a banner says the crisis is closed. bump.py and feed.py
keep working on the front page only. Old links to https://crisus.nl/#u-... are sent
on to the archive by crisus.js.

Usage: tools/archive.py SLUG "closing text" [END-ISO]
       tools/archive.py php "PHP2Shell is gepatcht." 2026-10-23T22:00:00+02:00
"""

import re
import sys
from datetime import datetime
from pathlib import Path

site = Path(__file__).resolve().parent.parent / "site"
slug, closing = sys.argv[1], sys.argv[2]
end = sys.argv[3] if len(sys.argv) > 3 else datetime.now().astimezone().isoformat(timespec="seconds")
src = (site / "index.html").read_text(encoding="utf-8")
base = f"https://crisus.nl/{slug}/"

s = src
# Where the page lives
for a, b in [
    ('<meta property="og:url" content="https://crisus.nl/">', f'<meta property="og:url" content="{base}">'),
    ('<link rel="canonical" href="https://crisus.nl/">', f'<link rel="canonical" href="{base}">'),
    ('<link rel="alternate" hreflang="nl" href="https://crisus.nl/">', f'<link rel="alternate" hreflang="nl" href="{base}">'),
    ('<link rel="alternate" hreflang="x-default" href="https://crisus.nl/">', f'<link rel="alternate" hreflang="x-default" href="{base}">'),
    ('"url": "https://crisus.nl/",\n  "mainEntityOfPage": "https://crisus.nl/",',
     f'"url": "{base}",\n  "mainEntityOfPage": "{base}",'),
]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
s = s.replace('"url": "https://crisus.nl/#u-', f'"url": "{base}#u-')
# The live blog is over
a = '  "coverageStartTime":'
assert s.count(a) == 1
s = s.replace(a, f'  "coverageEndTime": "{end}",\n{a}', 1)
# Title and kicker say so
s = re.sub(r"<title>Crisus · ", "<title>Crisus (afgesloten) · ", s, count=1)
s, n = re.subn(r'<p class="kicker">Lopende crisus · ', '<p class="kicker">Afgesloten crisus · ', s, count=1)
assert n == 1
# The banner, right under <main>
banner = (f'  <p class="afgesloten"><strong>Deze crisus is afgesloten.</strong> {closing} '
          'Hieronder staat alles zoals het was, met alle updates. '
          '<a href="/" title="Crisus: de actuele stand">Naar de actuele stand</a>.</p>\n')
a = '<main id="inhoud" class="wrap">\n'
assert s.count(a) == 1
s = s.replace(a, a + banner, 1)
# The level is the one it ended on
s = s.replace('<h2 id="niveau">Huidig crisusniveau: ', '<h2 id="niveau">Crisusniveau bij het afsluiten: ', 1)

out = site / slug / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(s, encoding="utf-8")
print("archived to", out.relative_to(site.parent))
