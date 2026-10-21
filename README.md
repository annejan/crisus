# crisus.nl

**Centrale Registratie van Incidenten, Storingen en Uitgebreid Schouderophalen.**
A satire status page for big internet incidents, in the style of an outage page.
The jokes are ours; every fact comes from a source the page names.

First used live on 21 October 2026 for PHP2Shell (CVE-2026-109618 and
CVE-2026-109619), updated through the day and the night after.

## Layout

| Path | What |
|---|---|
| `site/` | The site as served: `index.html`, `over/`, `404.html`, `crisus.css`, `klok.js`, `feed.xml` (RSS), `sitemap.xml`, `og.png`, `.htaccess` (strict CSP, headers) |
| `tools/check.sh` | One round of source checks: news, php.net, distributions, Docker, offline sites |
| `tools/bump.py` | Set every "last updated" stamp at once and rebuild the feed |
| `tools/feed.py` | Build `site/feed.xml` from the updates list; gives every update a permalink id |
| `tools/og.py` | Render `site/og.png`, the link-preview image |
| `tools/check-html.py` | Check that tags nest properly |
| `tools/deploy.sh` | Copy `site/` to the web server |
| `skills/crisus-update/` | A Claude Code skill: how to run an update round, and the rules |

## A round, short

```
bash tools/check.sh                      # what changed?
$EDITOR site/index.html                  # add an update, refresh the fixed blocks
python3 -I tools/bump.py 23:00           # stamps + feed
python3 -I tools/check-html.py site/index.html
tools/deploy.sh index.html sitemap.xml feed.xml
```

The site is static on purpose: no PHP, no cookies, no trackers, nothing from third
parties. During a PHP crisis that is the joke and the point.

## License

[REUSE](https://reuse.software/) compliant, see `REUSE.toml`: the code and
configuration (`tools/`, `skills/`, CSS, JS, `.htaccess`) are MIT, the pages,
texts, feed and images are CC-BY-4.0. Quotes from news sources and advisories
are cited with a link to the source.

© 2026 Anne Jan Brouwer.
