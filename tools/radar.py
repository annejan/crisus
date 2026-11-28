#!/usr/bin/env python3
"""Keep "Op de radar" on the front page in step with itself.

Each radar item says its state once, in a pill (see skills/crisus-update/SKILL.md,
"Op de radar"). From that this script:
- sets the pill's colour and the item's class="rood" (red is "Wordt misbruikt" and
  nothing else: the colour follows the state, never the hand);
- rebuilds the short list above the items, between the radarlijst markers;
- prints what a round should look at: an item without a date or review date, a
  state that is not on the list, an item past its review date, more than 20 items.

Usage: python3 -I tools/radar.py            rewrite site/index.html, print the notes
       python3 -I tools/radar.py --check    print only the notes, change nothing
bump.py runs it before it stamps the page. A page without the new radar markup
(a crisis page, an archive) is left alone.
"""
import html
import re
import sys
from datetime import date
from pathlib import Path

# State -> pill colour, most urgent first. The order is also the order on the page.
STATES = {
    "Wordt misbruikt": "red",
    "Misbruik gemeld": "orange",
    "Nog geen fix": "orange",
    "Fix nog niet overal": "orange",
    "Fix beschikbaar": "geel",
    "Datalek": "geel",
    "Opgelost": "green",
    "Terug": "green",
}
MAX_ITEMS = 20
START, END = "  <!-- radarlijst: gemaakt door tools/radar.py, niet met de hand wijzigen -->\n", "  <!-- /radarlijst -->\n"

check_only = "--check" in sys.argv[1:]
page = Path(__file__).resolve().parent.parent / "site" / "index.html"
text = page.read_text(encoding="utf-8")

m = re.search(r'  <ul class="radar kaarten">\n(.*?)  </ul>\n', text, re.S)
if not m:
    sys.exit(0)  # no radar in the new markup on this page
items = re.findall(r"    <li\b[^>]*>.*?\n    </li>\n", m.group(1), re.S)
notes, rows, out = [], [], []
if len(items) != len(re.findall(r"^    <li\b", m.group(1), re.M)) or "".join(items).strip() != m.group(1).strip():
    notes.append("markup: every item is '    <li ...>' up to '    </li>' on a line of its own, with nothing between items")
today = date.today().isoformat()
for item in items:
    head = re.match(r"    <li\b([^>]*)>", item).group(1)
    ident = re.search(r'\bid="([^"]+)"', head)
    title = re.search(r'<h3><a href="#[^"]*"[^>]*>(.*?)</a>', item, re.S)
    name = html.unescape(re.sub(r"<[^>]+>", "", title.group(1))) if title else (ident.group(1) if ident else "?")
    if not ident or not title or f'href="#{ident.group(1)}"' not in item:
        notes.append(f"{name}: needs an id and a title that links to it")
        out.append(item)
        continue
    stand = re.search(r'<p class="stand"><span class="pill[^"]*">([^<]+)</span>(.*?)</p>', item, re.S)
    when = re.search(r'<time datetime="(\d{4}-\d\d-\d\d)">([^<]+)</time>', item)
    review = re.search(r'\bdata-herzien="(\d{4}-\d\d-\d\d)"', head)
    if not stand:
        notes.append(f"{name}: no state line (<p class=\"stand\"><span class=\"pill\">...)")
        out.append(item)
        continue
    state, action = stand.group(1).strip(), re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", stand.group(2))).strip()
    colour = STATES.get(state)
    if colour is None:
        notes.append(f"{name}: state {state!r} is not on the list ({', '.join(STATES)})")
        colour = "geel"
    if not when:
        notes.append(f"{name}: no date (<time datetime=\"YYYY-MM-DD\"> in the title line)")
    if not review:
        notes.append(f"{name}: no review date (data-herzien=\"YYYY-MM-DD\")")
    elif review.group(1) <= today:
        notes.append(f"{name}: review date {review.group(1)} has come: still true, still needed?")
    # The colour follows the state.
    new_head = re.sub(r'\s*\bclass="[^"]*"', "", head)
    if colour == "red":
        new_head = re.sub(r'(\bid="[^"]+")', r'\1 class="rood"', new_head, count=1)
    item = item.replace(f"<li{head}>", f"<li{new_head}>", 1)
    item = re.sub(r'<p class="stand"><span class="pill[^"]*">', f'<p class="stand"><span class="pill {colour}">', item, count=1)
    out.append(item)
    detail = " · ".join(x for x in (html.escape(action, quote=False), when.group(2) if when else "") if x)
    rows.append(
        f'    <li><b><a href="#{ident.group(1)}" title="Naar {html.escape(name)} op de radar">{title.group(1)}</a></b>'
        f'<span class="pill {colour}">{html.escape(state, quote=False)}</span><em>{detail}</em></li>\n'
    )

order = [list(STATES).index(s) for s in re.findall(r'<p class="stand"><span class="pill[^"]*">([^<]+)</span>', "".join(out)) if s in STATES]
if order != sorted(order):
    notes.append("order: the most urgent state goes first (" + ", ".join(STATES) + ")")
if len(items) > MAX_ITEMS:
    notes.append(f"{len(items)} items: more than {MAX_ITEMS}, drop the oldest quiet ones first")

board = START + '  <ul class="status radarlijst" aria-label="De radar in het kort">\n' + "".join(rows) + "  </ul>\n" + END
new = text[: m.start(1)] + "".join(out) + text[m.end(1):]
if START in new:
    new = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: board, new, count=1, flags=re.S)
else:
    new = new.replace('  <ul class="radar kaarten">\n', board + '  <ul class="radar kaarten">\n', 1)

for n in notes:
    print("radar:", n)
if not check_only and new != text:
    page.write_text(new, encoding="utf-8")
    print(f"radar: {len(rows)} items, list rebuilt")
