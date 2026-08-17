#!/usr/bin/env python3
"""Point every absolute URL on the site at a new base.

Usage:
    python3 scripts/set_base_url.py https://governance-atlas.pages.dev/
    python3 scripts/set_base_url.py https://atlas.example.com/ --dry-run

Canonical links, og:url and og:image are absolute by necessity — crawlers and
WhatsApp reject relative ones — so moving host means rewriting them across
every page. This also updates both generators, so regenerated country pages
keep the new base.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CURRENT_RE = re.compile(r'https://[a-z0-9.-]+(?:\.github\.io|\.pages\.dev|\.[a-z]{2,})(?:/governance-atlas)?/')

TARGETS = [
    *ROOT.glob("*.html"),
    *ROOT.glob("continents/*.html"),
    *ROOT.glob("countries/*.html"),
    ROOT / "scripts" / "generate.py",
]


def current_base():
    """Read the base currently used by the home page's canonical link."""
    t = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<link rel="canonical" href="(https://[^"]+?/)[^/"]*"', t)
    return m.group(1) if m else None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        cur = current_base()
        print(f"current base: {cur}")
        sys.exit(1)

    new = sys.argv[1]
    if not new.startswith("https://"):
        sys.exit("base URL must start with https://")
    if not new.endswith("/"):
        new += "/"
    dry = "--dry-run" in sys.argv

    old = current_base()
    if not old:
        sys.exit("could not detect the current base URL from index.html")
    if old == new:
        print(f"already using {new}")
        return

    changed = hits = 0
    for p in TARGETS:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        n = t.count(old)
        if not n:
            continue
        hits += n
        if not dry:
            p.write_text(t.replace(old, new), encoding="utf-8")
        changed += 1

    verb = "would update" if dry else "updated"
    print(f"{old}\n  → {new}\n{verb} {hits} URLs across {changed} files")
    if not dry:
        print("\nRemember: og:image is absolute too, so social previews now serve from the new host.")


if __name__ == "__main__":
    main()
