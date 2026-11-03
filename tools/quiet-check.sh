#!/bin/bash
# SPDX-FileCopyrightText: 2026 Anne Jan Brouwer
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Pre-check for the hourly round, as the unit's ExecCondition:
#   exit 0: something changed, run the round (claude -p /crisus-ronde);
#   exit 1: the sources say what they said at the last full round, skip it.
# check.sh still runs either way, so "laatste controle" on the front page stays
# current (it deploys controle.js itself when CRISUS_RSYNC is set).
#
# What counts is the output of check.sh and php-deep.sh without what changes
# every hour without being news: the clock, "since" stamps, the CVE radar (new
# CVEs every hour) and Docker's tag times. A full round runs at least every
# QUIET_MAX hours anyway, so the CVE radar is still read and a round that failed
# (out of credit, say) cannot hide a change for long.
# Usage: tools/quiet-check.sh   (QUIET_MAX=3 by default)
cd "$(dirname "$0")/.." || exit 0
STATE="$HOME/.local/state/crisus-quiet"
mkdir -p "$(dirname "$STATE")"
max=${QUIET_MAX:-3}

sources=$( { timeout 300 bash tools/check.sh; timeout 300 bash tools/php-deep.sh; } 2>&1 )
# Anything that went wrong: run the round, it reads the sources itself.
[ -n "$sources" ] || exit 0
digest=$(printf '%s\n' "$sources" | awk '
  /^[0-2][0-9]:[0-5][0-9]$/ { next }                 # check.sh: the time
  /^== headlines since / { print "== headlines"; next }
  /^== php-deep since / { print "== php-deep"; next }
  /^== CVE:/ { skip = 1; next }                       # the CVE radar: new every hour
  /^== / { skip = 0 }
  skip { next }
  /^[0-9a-z.]+-(apache|fpm) 20[0-9][0-9]-/ { next }  # Docker floating tag times
  { print }' | sha256sum | cut -d" " -f1)

now=$(date +%s)
read -r last_digest last_full 2>/dev/null < "$STATE"
if [ "$digest" = "$last_digest" ] && [ -n "$last_full" ] &&
   [ $((now - last_full)) -lt $((max * 3600)) ]; then
	echo "quiet-check: nothing new since $(date -d "@$last_full" +%H:%M), round skipped"
	exit 1
fi
echo "$digest $now" > "$STATE"
echo "quiet-check: sources changed (or ${max} h passed), round runs"
exit 0
