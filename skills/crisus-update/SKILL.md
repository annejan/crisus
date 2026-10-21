---
name: crisus-update
description: Run one update round for crisus.nl, the satire status page for big internet incidents (facts from sources, dry Dutch jokes). Use when asked to update crisus.nl, to run the hourly or night round, or to start a new crisus for a fresh incident.
---

# crisus.nl update round

crisus.nl is a static satire site ("Centrale Registratie van Incidenten, Storingen
en Uitgebreid Schouderophalen") in the style of an outage status page. Satire, but
every fact comes from a source that the page names. Repo: this one. The site lives
in `site/`, the tooling in `tools/`.

## A round

1. **Check the sources.** `bash tools/check.sh` prints NOS, php.net, NCSC, Debian,
   Ubuntu, Docker (including the floating tags), Homebrew, Red Hat, SUSE, Node and a
   sample of sites that went offline. For a site that seems back, read its content,
   not only the title: maintenance pages often keep a normal title.
2. **Only with real news**, add an item at the top of `<ol class="updates">` in
   `site/index.html`: `<li>` without an id (`feed.py` adds it), a `<time>` with the
   publish time, the facts from the source, and one dry Dutch joke. In a quiet hour:
   skip, change nothing.
3. **Update the fixed blocks**, one by one, so nothing is stale: the tape, the lead,
   the clock text, the crisis level (and `og:description`), the facts under "Wat is er
   aan de hand?", "Wat moet u doen?", the "Stand per platform, HH:MM" heading and every
   row, every row of the status board, and the sources list.
4. `python3 -I tools/bump.py HH:MM [YYYY-MM-DD]` sets every "last updated" stamp
   (visible, `<time datetime>`, `article:modified_time`, JSON-LD, sitemap) and rebuilds
   `site/feed.xml`.
5. Check the HTML nesting (see `tools/check-html.py`), then publish on the hour:
   `tools/deploy.sh index.html sitemap.xml feed.xml`.
6. Crisis level or fixed versions changed? `python3 -I tools/og.py --level N --versions "..."`
   and deploy `og.png` too. CSS changed? Raise `?v=` in `index.html`, `over/index.html`
   and `404.html` and deploy those with `crisus.css`.

## Rules

- Satire, but facts are right and sourced. Corrections are visible: `<del>` plus a
  timestamped correction, never a silent fix.
- Never say which of the owner's own servers are (un)patched.
- No exploit repos or exploit code, not even as a link.
- Real people: no he/she pronouns unless known; write around it ("de onderzoeker").
- Dutch without a comma before "en". Plain status labels: "Fix beschikbaar",
  "Nog geen fix", "Nu installeren", "Update beschikbaar", "Terug", "Preventief uit",
  "Deels", "Onduidelijk", "Herstarten". No shorthand like "Pakket er".
- No government (Rijksoverheid) house style. The footer says it is satire and to call 112.
- Strict CSP (`site/.htaccess`): no inline `<style>` or `<script>`, no `style=""`
  attributes. Styles go in `crisus.css`, the only script is `klok.js`.

## A new crisus

Copy the page structure (tape, crisus level, facts, "Wat moet u doen?", per-platform
status, status board, updates, sources, archive). Move the old incident to the
"Eerdere crisussen" archive. Reset the feed: the old items can stay, they keep their
ids.
