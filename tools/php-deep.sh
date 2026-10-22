#!/bin/bash
# The deeper PHP check: where news about PHP2Shell, or the next PHP bug, shows up first.
# Prints only what is new since the given time (default: the last 26 hours).
# Usage: tools/php-deep.sh [ISO-time, e.g. 2026-10-22T21:00:00Z]
SINCE=${1:-$(date -u -d '26 hours ago' +%Y-%m-%dT%H:%M:%SZ)}
echo "== php-deep since $SINCE"

echo "-- php-src security advisories"
gh api 'repos/php/php-src/security-advisories?per_page=10&sort=published&direction=desc' \
  --jq ".[] | select(.published_at > \"$SINCE\") | \"\(.published_at[:16]) \(.ghsa_id) \(.cve_id) \(.severity) | \(.summary)\"" 2>&1 | head -10

echo "-- php-src release tags (newest final release per branch)"
gh api 'repos/php/php-src/git/matching-refs/tags/php-8.' --paginate --jq '.[].ref' 2>/dev/null | sed 's#refs/tags/##' \
  | grep -E '^php-8\.[2-5]\.[0-9]+$' | sort -V | awk -F. '{last[$1"."$2]=$0} END {for (b in last) print last[b]}' | sort -V | tr '\n' ' '; echo

echo "-- php-src commits on the release branches (security-looking subjects)"
for br in PHP-8.2 PHP-8.3 PHP-8.4 PHP-8.5; do
  gh api "repos/php/php-src/commits?sha=$br&since=$SINCE&per_page=50" \
    --jq ".[] | \"$br \(.commit.committer.date[:16]) \(.sha[:10]) \(.commit.message | split(\"\n\")[0])\"" 2>/dev/null \
    | grep -i -E 'cve|ghsa|secur|overflow|use.after|double.free|uaf|oob|out.of.bounds|bailout|memory|corrupt|fix gh-' | head -5
done

echo "-- php.net news (newest)"
curl -s https://www.php.net/archive/2026.php | grep -o -E 'id="2026-[0-9-]+"|<h2 class="newstitle">[^<]*<a[^>]*>[^<]+' | sed 's/<[^>]*>//g' | head -4 | tr '\n' ' '; echo

echo "-- CISA KEV"
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | python3 -I -c '
import json, sys
d = json.load(sys.stdin)
hits = [v for v in d["vulnerabilities"] if v["cveID"] in ("CVE-2026-109618", "CVE-2026-109619")]
print(" | ".join(v["cveID"] + " added " + v["dateAdded"] for v in hits) or "PHP2Shell not on KEV (yet)")'

echo "-- oss-security (today, PHP)"
curl -s "https://www.openwall.com/lists/oss-security/$(date +%Y/%m/%d)/" | python3 -I -c '
import sys,re,html
for t in re.findall(r"<a href=\"\d+\">([^<]+)</a>", sys.stdin.read()):
    t=html.unescape(t)
    if re.search(r"(?i)\bphp\b|php2shell|10961[89]", t): print("  ", t)'

echo "-- vendor advisories mentioning PHP2Shell"
curl -s https://security.paloaltonetworks.com/rss.xml | grep -o -E '<title>[^<]*(PHP|10961[89])[^<]*' | sed 's/<title>/  paloalto: /' | head -3

echo "-- @elise (newest posts, any thread)"
id=$(curl -s 'https://fedi.katze.sh/api/v1/accounts/lookup?acct=elise' | python3 -I -c 'import json,sys; print(json.load(sys.stdin)["id"])' 2>/dev/null)
[ -n "$id" ] && curl -s "https://fedi.katze.sh/api/v1/accounts/$id/statuses?limit=5&exclude_reblogs=true" | python3 -I -c "
import json,sys,re,html
for s in json.load(sys.stdin):
    if s['created_at'] > '$SINCE': print('  ', s['created_at'][:16], re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s['content'])))[:200])"
