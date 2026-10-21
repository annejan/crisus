#!/usr/bin/env python3
"""Check that the tags in an HTML file nest properly. Usage: tools/check-html.py site/index.html"""
import sys
from html.parser import HTMLParser

VOID = {"meta", "link", "br", "img", "input", "hr", "circle", "path", "source"}


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.errors.append((tag, self.getpos()))


bad = 0
for f in sys.argv[1:] or ["site/index.html"]:
    p = P()
    p.feed(open(f, encoding="utf-8").read())
    if p.errors or p.stack:
        bad = 1
        print(f, "errors", p.errors[:5], "unclosed", p.stack[:5])
    else:
        print(f, "ok")
sys.exit(bad)
