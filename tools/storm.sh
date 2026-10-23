#!/bin/bash
# Weather warnings for the Netherlands (KNMI, via Meteoalarm): the highest level per
# region and type, active or coming. Yellow = Moderate, orange = Severe, red = Extreme.
# The last line is "STORM: ORANJE ..." or "STORM: ROOD ..." when that is the case, so a
# round can see at a glance whether the weather turns into a crisis.
# Usage: bash tools/storm.sh
set -uo pipefail
curl -s -m 20 https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-netherlands | python3 -I -c '
import re, sys, html
from datetime import datetime, timezone
t = sys.stdin.read()
now = datetime.now(timezone.utc)
rank = {"Minor": 0, "Moderate": 1, "Severe": 2, "Extreme": 3}
kleur = {1: "geel", 2: "ORANJE", 3: "ROOD"}
rows = []
for e in re.findall(r"<entry>(.*?)</entry>", t, re.S):
    g = lambda k: html.unescape((re.search(r"<cap:" + k + r">([^<]*)", e) or [None, ""])[1]).strip()
    sev, exp = g("severity"), g("expires")
    if sev not in rank or rank[sev] < 1:
        continue
    try:
        if exp and datetime.fromisoformat(exp) < now:
            continue
    except ValueError:
        pass
    rows.append((rank[sev], g("areaDesc"), g("event"), g("onset")[:16], exp[:16]))
if not rows:
    print("geen waarschuwingen"); print("STORM: geen"); sys.exit()
for r, area, ev, on, ex in sorted(set(rows), key=lambda x: (-x[0], x[1])):
    print(f"  {kleur[r]:6} {area:20} {ev:32} {on} -> {ex}")
top = max(r[0] for r in rows)
hit = sorted({a for r, a, *_ in rows if r == top})
print(f"STORM: {kleur[top]}" + (" in " + ", ".join(hit) if top >= 2 else ""))
'
