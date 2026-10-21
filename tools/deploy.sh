#!/bin/bash
# Deploy crisus.nl: everything in site/ to the static-sites root on the web box.
# Usage: tools/deploy.sh            (all files)
#        tools/deploy.sh index.html sitemap.xml feed.xml   (just these)
set -euo pipefail
cd "$(dirname "$0")/../site"
DEST=annejan.com:www/sites/crisus.nl
if [ $# -gt 0 ]; then
    scp -q "$@" "$DEST/"
else
    ssh annejan.com 'mkdir -p www/sites/crisus.nl/over'
    scp -q index.html 404.html crisus.css klok.js favicon.svg og.png robots.txt sitemap.xml feed.xml .htaccess "$DEST/"
    scp -q over/index.html "$DEST/over/index.html"
fi
curl -s https://crisus.nl/ | grep -o 'laatst bijgewerkt[^<]*'
