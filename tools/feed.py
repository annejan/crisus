#!/usr/bin/env python3
"""Build feed.xml (RSS 2.0) from the updates list in index.html.
Every <li> in <ol class="updates"> (the open list and the older one) becomes an item; each gets a stable
id="u-YYYYMMDD-HHMM" (added to index.html if missing) for its permalink.
Usage: python3 -I feed.py   (bump.py runs it too)"""
import email.utils, html, re
from datetime import datetime
from pathlib import Path

d = Path(__file__).resolve().parent.parent / "site"
page = d / "index.html"
t = page.read_text(encoding="utf-8")

OPEN = 5   # the newest five stay open; the rest go into <details class="oud">
MAIN, OLD = '<ol class="updates" aria-labelledby="updates">', '<ol class="updates oud">'


def span(marker):
    """Where the list after marker starts and ends, or None."""
    if marker not in t:
        return None
    a = t.index(marker) + len(marker)
    return a, t.index("</ol>", a)


def top_items(ol):
    """The top-level <li> items (nested <ul><li> stay inside their parent)."""
    items, depth, start = [], 0, None
    for m in re.finditer(r"<(/?)(li|ul|ol)\b[^>]*>", ol):
        closing, tag = m.group(1), m.group(2)
        if tag == "li" and not closing and depth == 0:
            start = m.start()
        if tag in ("ul", "ol"):
            depth += -1 if closing else 1
        if tag == "li" and closing and depth == 0 and start is not None:
            items.append(ol[start:m.end()])
            start = None
    return items


main = span(MAIN)
old = span(OLD)
lis = top_items(t[main[0]:main[1]]) + (top_items(t[old[0]:old[1]]) if old else [])

done, entries = [], []
for li in lis:
    when = re.search(r'<time datetime="([^"]+)">([^<]*)</time>', li)
    iso, label = when.group(1), when.group(2)
    dt = datetime.fromisoformat(iso if "T" in iso else iso + "T12:00+02:00")
    uid = "u-" + dt.strftime("%Y%m%d-%H%M")
    if not re.match(r'<li id="', li):
        li = li.replace("<li>", f'<li id="{uid}">', 1)
    else:
        uid = re.match(r'<li id="([^"]+)"', li).group(1)
    body = re.sub(r"^<li[^>]*>\s*<time[^>]*>[^<]*</time>\s*", "", li)
    body = re.sub(r"</li>$", "", body).strip()
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()
    first = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    title = f"{label} · {first[:110] + ('…' if len(first) > 110 else '')}"
    body = body.replace('href="#', 'href="https://crisus.nl/#')
    entries.append((uid, title, dt, body))
    done.append(li)


def block(items, indent):
    return "".join(f"\n{indent}{li}" for li in items) + f"\n{indent[:-2]}"


if old:   # write the later list first, so the earlier offsets stay valid
    t = t[:old[0]] + block(done[OPEN:], "      ") + t[old[1]:]
    t = t[:main[0]] + block(done[:OPEN], "    ") + t[main[1]:]
else:
    t = t[:main[0]] + block(done, "    ") + t[main[1]:]
page.write_text(t, encoding="utf-8")

def x(s): return html.escape(s, quote=False)
newest = max(e[2] for e in entries)
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', "<channel>",
       "  <title>Crisus · PHP Kwetsbaarheid</title>",
       "  <link>https://crisus.nl/</link>",
       '  <atom:link href="https://crisus.nl/feed.xml" rel="self" type="application/rss+xml"/>',
       "  <description>De updates van crisus.nl: satire, maar de feiten kloppen.</description>",
       "  <language>nl</language>",
       f"  <lastBuildDate>{email.utils.format_datetime(newest)}</lastBuildDate>"]
for uid, title, dt, body in entries:
    out += ["  <item>",
            f"    <title>{x(title)}</title>",
            f"    <link>https://crisus.nl/#{uid}</link>",
            f'    <guid isPermaLink="true">https://crisus.nl/#{uid}</guid>',
            f"    <pubDate>{email.utils.format_datetime(dt)}</pubDate>",
            f"    <description><![CDATA[{body}]]></description>",
            "  </item>"]
out += ["</channel>", "</rss>", ""]
(d / "feed.xml").write_text("\n".join(out), encoding="utf-8")
print(f"feed.xml: {len(entries)} items, newest {newest.isoformat()}")
