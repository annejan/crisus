#!/bin/bash
# Deploy crisus.nl: everything in site/ to the static-sites root on the web box.
# Usage: tools/deploy.sh            (all files)
#        tools/deploy.sh index.html uk/index.html   (just these, paths relative to site/)
#        CRISUS_RSYNC=user@host: tools/deploy.sh ...   (rsync to a key that rrsync limits
#                                                        to the site directory; never deletes)
set -euo pipefail
cd "$(dirname "$0")/../site"
DEST=annejan.com:www/sites/crisus.nl
if [ -n "${CRISUS_RSYNC:-}" ]; then
    if [ $# -gt 0 ]; then files=("$@"); else
        files=(index.html 404.html crisus.css crisus.js favicon.svg og.png robots.txt sitemap.xml feed.xml .htaccess og-php.png
               over/index.html php/index.html en/index.html uk/index.html museum/index.html museum/oud museum/503)
    fi
    rsync -aR --chmod=D755,F644 "${files[@]}" "$CRISUS_RSYNC"
elif [ $# -gt 0 ]; then
    for f in "$@"; do scp -q "$f" "$DEST/$f"; done
else
    ssh annejan.com 'mkdir -p www/sites/crisus.nl/over www/sites/crisus.nl/museum/oud www/sites/crisus.nl/museum/503 www/sites/crisus.nl/php www/sites/crisus.nl/en www/sites/crisus.nl/uk'
    scp -q index.html 404.html crisus.css crisus.js favicon.svg og.png og-php.png robots.txt sitemap.xml feed.xml .htaccess "$DEST/"
    scp -q over/index.html "$DEST/over/index.html"
    for d in php en uk; do scp -q "$d/index.html" "$DEST/$d/index.html"; done
    scp -q museum/index.html "$DEST/museum/index.html"
    scp -q museum/oud/* "$DEST/museum/oud/"
    scp -q museum/503/* "$DEST/museum/503/"
fi
curl -s https://crisus.nl/ | grep -o 'laatst bijgewerkt[^<]*'
