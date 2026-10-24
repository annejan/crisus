#!/bin/bash
# Weather warnings for the Netherlands (KNMI, via Meteoalarm): the highest level per
# region and type, active or coming. Yellow = Moderate, orange = Severe, red = Extreme.
# The last line is "STORM: ORANJE ..." or "STORM: ROOD ..." when that is the case, so a
# round can see at a glance whether the weather turns into a crisis. Only land counts:
# the KNMI coastal waters (Texel, IJmuiden and so on) are often orange for days, so they
# get their own "ZEE: ..." line just above it.
# Usage: bash tools/storm.sh
set -uo pipefail
curl -s -m 20 https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-netherlands | python3 -I -c '
import re, sys, html
from datetime import datetime, timezone
t = sys.stdin.read()
now = datetime.now(timezone.utc)
rank = {"Minor": 0, "Moderate": 1, "Severe": 2, "Extreme": 3}
kleur = {1: "geel", 2: "ORANJE", 3: "ROOD"}
# Meteoalarm names the KNMI coastal waters after a place on the coast
SEA = {"Delfzijl", "Flushing", "Harlingen", "Hook of Holland", "IJmuiden", "IJsselmeer",
       "Marken", "Rottum", "Texel", "Zierikzee"}
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
for r, area, ev, on, ex in sorted(set(rows), key=lambda x: (x[1] in SEA, -x[0], x[1])):
    name = area + (" (zee)" if area in SEA else "")
    print(f"  {kleur[r]:6} {name:20} {ev:32} {on} -> {ex}")
def level(rs, label):
    if not rs:
        return f"{label}: geen"
    top = max(r[0] for r in rs)
    hit = sorted({r[1] for r in rs if r[0] == top})
    return f"{label}: {kleur[top]}" + (" in " + ", ".join(hit) if top >= 2 else "")
print(level([r for r in rows if r[1] in SEA], "ZEE"))
print(level([r for r in rows if r[1] not in SEA], "STORM"))
'
