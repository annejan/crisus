#!/usr/bin/env python3
"""Write site/controle.js: when the last round looked and whether it found news. The
front page shows it next to "laatst bijgewerkt"; the file is not in git, so a quiet
hour needs no commit. Deploy it with: tools/deploy.sh controle.js
Usage: python3 -I controle.py [HH:MM] [--nieuws]   (default: now, Europe/Amsterdam)"""
import json, re, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

args = [a for a in sys.argv[1:] if a != "--nieuws"]
now = datetime.now(ZoneInfo("Europe/Amsterdam"))
if args:
    assert re.fullmatch(r"[0-2]\d:[0-5]\d", args[0]), "use [HH:MM] [--nieuws]"
    h, m = map(int, args[0].split(":"))
    now = now.replace(hour=h, minute=m)
stamp = {"at": now.replace(second=0, microsecond=0).isoformat(), "nieuws": "--nieuws" in sys.argv}
out = Path(__file__).resolve().parent.parent / "site" / "controle.js"
out.write_text(f"window.crisusControle = {json.dumps(stamp)};\n", encoding="utf-8")
print("controle", stamp["at"], "nieuws" if stamp["nieuws"] else "niets nieuws")
