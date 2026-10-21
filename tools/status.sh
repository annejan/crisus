#!/bin/bash
# Check every site on the crisus.nl status board by its content and compare with
# tools/status-expect.txt. Prints every site, and "CHANGED" where the state differs.
# Exit 0: nothing changed, 1: something changed.
cd "$(dirname "$0")"
S=$(mktemp -d); trap 'rm -rf "$S"' EXIT
changed=0
while read -r host want; do
    case $host in ''|\#*) continue;; esac
    rm -f "$S/b"; c=$(curl -sL --max-time 15 -A 'Mozilla/5.0 (X11; Linux x86_64) Chrome/130' -w '%{http_code}' -o "$S/b" "https://$host/")
    got=$(python3 -I - "$S/b" "$c" <<'PY'
import re, html, sys
code = sys.argv[2]
try:
    t = open(sys.argv[1], encoding="utf8", errors="replace").read()
except FileNotFoundError:
    t = ""
s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style).*?</\1>", "", t, flags=re.S))))
title = re.search(r"<title[^>]*>([^<]*)", t, re.I)
title = html.unescape(title.group(1)) if title else ""
notice = re.search(r"(?i)onderhoud|tijdelijk|niet beschikbaar|zo terug|offline|maintenance", title) or \
    re.search(r"(?i)we zijn zo terug|dringende beveiligingsupdate|beveiligingsprobleem|php-beveiligingsupdate|kritieke kwetsbaarheid|tijdelijk (niet|offline)|preventief offline|onderhoudsmodus|vindt er onderhoud plaats|in onderhoud|wegens onderhoud|veiligheidsrisico", s)
print("out" if code in ("000", "500", "502", "503") or notice else "up", (notice.group(0) if notice else "")[:30])
PY
)
    state=${got%% *}; why=${got#* }
    flag=""; [ "$state" != "$want" ] && { flag="CHANGED (page says $want)"; changed=1; }
    printf '%-30s %s %-4s %-28s %s\n' "$host" "$c" "$state" "$why" "$flag"
done < status-expect.txt
exit $changed
