#!/bin/bash
# One crisus.nl round: print the current state of every source, compactly.
S=$(mktemp -d); trap 'rm -rf "$S"' EXIT
pkg() { curl -s --max-time 30 "$1" | xz -dc 2>/dev/null | awk -v p="$2" '$0=="Package: "p{f=1} f&&/^Version:/{print $2;exit}'; }
txt() { python3 -I -c '
import sys,re,html
t=sys.stdin.read(); t=re.sub(r"<(script|style|nav|footer).*?</\1>","",t,flags=re.S|re.I); t=re.sub(r"<[^>]+>","\n",t); t=html.unescape(t)
print("\n".join(l.strip() for l in t.splitlines() if len(l.strip())>2))'; }
date +%H:%M
echo "== NOS (newest entries)"
curl -sL -A 'Mozilla/5.0' https://nos.nl/liveblog/2636066-websites-kwetsbaar-voor-softwarelek-rtl-nieuws-digid-en-mijnoverheid-uit-de-lucht | txt | awk '/Deel deze update/{n++} n>=1&&n<=4' | grep -v -E 'Deel deze update|opent in nieuw venster' | head -30
echo "== php.net"; curl -s 'https://www.php.net/releases/index.php?json&max=1&version=8' | grep -o '"[0-9.]*":{"announcement' | head -1; curl -s https://www.php.net/archive/2026.php | grep -o 'id="2026-1[0-2]-[0-9-]*"' | head -1
echo "== NCSC"; curl -sL -A 'Mozilla/5.0' https://advisories.ncsc.nl/ | txt | grep -m3 -i -E 'php|websitebericht'
echo "== Debian"; curl -s https://security-tracker.debian.org/tracker/CVE-2026-109618 | txt | tr '\n' ' ' | grep -o -E 'php8\.2 .{0,160}' | head -1; echo; echo "bookworm-security php8.2-cli: $(pkg http://security.debian.org/debian-security/dists/bookworm-security/main/binary-amd64/Packages.xz php8.2-cli)"; curl -s https://www.debian.org/security/ | grep -o 'DSA-[0-9-]* [^<]*' | head -3 | tr '\n' ';'; echo
echo "== Ubuntu"; for s in resolute noble stonking; do printf "%s: %s  " $s "$(pkg http://security.ubuntu.com/ubuntu/dists/$s-security/main/binary-amd64/Packages.xz php8.5-common)"; done; echo
echo "== Docker/Homebrew/RH/SUSE"
curl -s 'https://hub.docker.com/v2/repositories/library/php/tags?page_size=6&name=8.5.12' | python3 -I -c "import sys,json; print('docker',[r['name'] for r in json.load(sys.stdin).get('results',[])][:6])"
for tg in 8.5-apache 8.4-apache 8.4-fpm latest; do printf '%s %s  ' $tg "$(curl -s https://hub.docker.com/v2/repositories/library/php/tags/$tg | python3 -I -c 'import sys,json; print(json.load(sys.stdin).get("last_updated","?")[:16])')"; done; echo "(floating tags: 07:xx = still old)"
curl -s https://formulae.brew.sh/api/formula/php.json | python3 -I -c "import sys,json; print('brew',json.load(sys.stdin)['versions']['stable'])"
curl -s -o /dev/null -L -w 'rh %{http_code} ' https://access.redhat.com/security/cve/CVE-2026-109618; curl -s -o /dev/null -w 'suse %{http_code}\n' https://www.suse.com/security/cve/CVE-2026-109618.html
echo "== Node distro"; echo "debian trixie nodejs: $(pkg http://security.debian.org/debian-security/dists/trixie-security/main/binary-amd64/Packages.xz nodejs)  ubuntu resolute-security nodejs: $(pkg http://security.ubuntu.com/ubuntu/dists/resolute-security/main/binary-amd64/Packages.xz nodejs)"
echo "== sites"
for u in https://www.digid.nl/ https://mijn.overheid.nl/ https://www.ncsc.nl/ https://www.tweedekamer.nl/ https://www.knvb.nl/ https://www.kwf.nl/ https://www.amnesty.nl/; do
    c=$(curl -s -o "$S/b.html" -L --max-time 15 -A 'Mozilla/5.0' -w '%{http_code}' "$u"); printf '%-28s %s %s\n' "$u" "$c" "$(grep -o -i -m1 -E '<title>[^<]{0,50}' "$S/b.html" | head -1)"
done
echo "== elise thread (newest)"; curl -s -A 'Mozilla/5.0' https://fedi.katze.sh/api/v1/statuses/117478725808527006/context | python3 -I -c "
import sys,json,re,html
d=json.load(sys.stdin); s=[x for x in d.get('descendants',[]) if x['account']['acct']=='elise']
for x in s[-3:]: print(x['created_at'][:16], re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x['content'])))[:160])"
