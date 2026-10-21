#!/usr/bin/env python3
"""Render site/og.png (1200x630), the image link previews show.
Usage: python3 -I tools/og.py [--title T] [--sub S] [--versions V] [--level N]
Fonts: Noto Sans and Source Code Pro (openSUSE paths; pass --fonts DIR to change)."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--title", default="PHP Kwetsbaarheid")
ap.add_argument("--sub", default="Twee kritieke lekken. De patch is uit. Niet in paniek raken. Wel updaten.")
ap.add_argument("--label", default="Gefixt in")
ap.add_argument("--versions", default="8.5.12 · 8.4.27 · 8.3.36 · 8.2.35")
ap.add_argument("--level", type=int, default=2)
ap.add_argument("--tape", default="LET OP · CRISUS · BLIJF KALM · PATCH IS UIT · UPDATEN")
ap.add_argument("--sans", default="/usr/share/fonts/truetype/NotoSans")
ap.add_argument("--mono", default="/usr/share/fonts/texlive-sourcecodepro/SourceCodePro-Bold.otf")
a = ap.parse_args()

W, H = 1200, 630
Y, K, BG, MU, OR, WH = (255, 212, 0), (17, 17, 17), (250, 250, 247), (85, 85, 92), (194, 94, 0), (255, 255, 255)
B, R = a.sans + "-Bold.ttf", a.sans + "-Regular.ttf"
f = ImageFont.truetype

im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)

# warning tape with the motto on a yellow band
tape = Image.new("RGB", (W, 54), Y)
td = ImageDraw.Draw(tape)
for x in range(-60, W + 120, 60):
    td.polygon([(x, 0), (x + 30, 0), (x - 24, 54), (x - 54, 54)], fill=K)
im.paste(tape, (0, 0))
d.rectangle([0, 15, W, 39], fill=Y)
d.text((W // 2, 27), a.tape, font=f(B, 17), fill=K, anchor="mm")

# warning sign and word mark
x0, y0 = 70, 100
d.polygon([(x0 + 40, y0), (x0 + 80, y0 + 70), (x0, y0 + 70)], fill=Y, outline=K, width=6)
d.line([(x0 + 40, y0 + 24), (x0 + 40, y0 + 46)], fill=K, width=8)
d.ellipse([x0 + 35, y0 + 52, x0 + 45, y0 + 62], fill=K)
d.text((x0 + 105, y0 + 2), "CRISUS", font=f(B, 54), fill=K)
d.text((x0 + 107, y0 + 70), "Centrale Registratie van Incidenten, Storingen en Uitgebreid Schouderophalen", font=f(R, 20), fill=MU)

# headline
d.text((70, 230), a.title, font=f(B, 92), fill=K)
d.text((72, 350), a.sub, font=f(R, 30), fill=MU)

# versions on black, shrunk until they fit
d.rounded_rectangle([70, 420, 790, 560], radius=18, fill=K)
d.text((100, 440), a.label, font=f(R, 26), fill=(212, 212, 216))
s = 40
while d.textlength(a.versions, font=f(a.mono, s)) > 660:
    s -= 1
d.text((100, 480), a.versions, font=f(a.mono, s), fill=Y)

# crisis level
d.rounded_rectangle([820, 420, 1130, 560], radius=18, fill=WH, outline=K, width=4)
d.text((850, 440), "Crisusniveau", font=f(R, 26), fill=MU)
d.text((850, 474), f"{a.level} van 5", font=f(B, 52), fill=OR)

d.text((70, 590), "crisus.nl · satire, maar de feiten kloppen", font=f(R, 22), fill=MU)
out = Path(__file__).resolve().parent.parent / "site" / "og.png"
im.save(out, optimize=True)
print(out, im.size)
