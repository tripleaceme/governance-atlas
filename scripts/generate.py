#!/usr/bin/env python3
"""Generate one country page per record in data/countries.json.

Usage:  python3 scripts/generate.py

Pages listed in RICH (hand-written, fully verified layouts) are skipped.
Everything else gets a stub dossier: status, law, what-we-know summary,
and a contribution call — honest about what is and isn't verified yet.
Zero dependencies; safe to re-run (idempotent).
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RICH = {"nigeria", "kenya", "south-africa"}

STATUS_CHIP = {
    "a": '<span class="chip active">Active law</span>',
    "d": '<span class="chip">Bill / draft in progress</span>',
    "n": '<span class="chip">No comprehensive law</span>',
}
STATUS_LABEL = {"a": "Active law", "d": "Bill / draft in progress", "n": "No comprehensive law"}

SUMMARY = {
    "a": (
        "<p>{name} has an active comprehensive data protection law: <strong>{law}</strong>. "
        "A full plain-English dossier for this page — supervisory authority, DPO and registration "
        "requirements, breach deadlines, penalties, and links to official sources — is being "
        "prepared and verified against primary sources.</p>"
    ),
    "d": (
        "<p>{name} does not yet have a comprehensive data protection law in force, but "
        "legislation is in progress ({law}). Sector-specific rules or constitutional privacy "
        "rights may still apply in the meantime. This page will be expanded as the bill advances.</p>"
    ),
    "n": (
        "<p>No comprehensive data protection law has been identified for {name} yet. "
        "Sector-specific rules, cybercrime laws, or constitutional privacy rights may still "
        "apply. This page will be updated if that changes — corrections are welcome.</p>"
    ),
}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — Governance Atlas</title>
<meta name="description" content="Data protection law in {name}: {desc}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌍</text></svg>">
<link rel="stylesheet" href="../assets/styles.css">
</head>
<body>

<header class="site">
  <div class="wrap">
    <a class="logo" href="../index.html" title="GovernanceAtlas home">
      <div class="mark">Governance<span>Atlas</span></div>
      <div class="tag">Data protection law, by country</div>
    </a>
    <nav class="main">
      <a href="../index.html" class="active">Browse</a>
      <a href="../compare.html">Compare</a>
      <a href="../resources.html">Resources</a>
      <a href="../about.html">About</a>
    </nav>
  </div>
</header>

<div class="wrap">
  <div class="crumbs">
    <a href="../index.html">Home</a><span class="sep">›</span>
    <a href="../continents/{continent_slug}.html">{continent}</a><span class="sep">›</span>
    <span class="here">{name}</span>
  </div>

  <div class="hero">
    <div class="eyebrow">{continent}</div>
    <h1>{name}</h1>
    <p class="lawline">{lawline}</p>
    <div class="chips">
      {status_chip}
      {law_chip}
      <span class="chip verified">Awaiting verification</span>
    </div>
  </div>

  <div class="cols">
    <aside class="dossier">
      <h2>At a glance</h2>
      <dl style="margin:0">
        <div class="fact"><dt>Continent</dt><dd>{continent}</dd></div>
        <div class="fact"><dt>Status</dt><dd>{status_label}</dd></div>
        <div class="fact"><dt>Primary law</dt><dd>{law_or_dash}</dd></div>
        <div class="fact"><dt>Page status</dt><dd class="no">Stub — awaiting verification</dd></div>
      </dl>
    </aside>

    <article>
      <section>
        <h2>What we know</h2>
        <span class="readtime">Stub page · not legal advice</span>
        {summary}
        <p>For an example of what this page will become, see the completed
        <a href="nigeria.html">Nigeria dossier</a>.</p>
      </section>

      <section>
        <h2>Help verify this page</h2>
        <p>Governance Atlas is community-maintained. If you know {name}'s data protection
        landscape — the law, the regulator, official sources — a pull request with citations
        makes this page real.
        <a href="https://github.com/tripleaceme/governance-atlas" target="_blank" rel="noopener">Contribute on GitHub ↗</a></p>
      </section>

      <section>
        <h2>Compare</h2>
        <p class="comparecta"><a href="../compare.html">Open the comparison tool → see how verified countries compare side by side</a></p>
      </section>
    </article>
  </div>
</div>

<footer class="site">
  <div class="wrap">
    <div>GovernanceAtlas is a community-maintained reference. It is not legal advice — always verify against official sources.</div>
    <div class="credits">
      <a href="https://github.com/tripleaceme/governance-atlas" target="_blank" rel="noopener">Suggest a correction on GitHub ↗</a>
      <span>Developed by <a href="https://ayoadeabel.tech" target="_blank" rel="noopener">Ayoade Adegbite</a></span>
      <a class="li" href="https://www.linkedin.com/in/tripleaceme/" target="_blank" rel="noopener" aria-label="Ayoade Adegbite on LinkedIn">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.55C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.72C24 .77 23.2 0 22.22 0z"/></svg>
      </a>
    </div>
  </div>
</footer>

</body>
</html>
"""


def lawline(c):
    if c["status"] == "a":
        return f'Primary law: <strong>{c["law"]}</strong>. Full dossier coming — this page is awaiting verification against official sources.'
    if c["status"] == "d":
        return "No comprehensive law in force yet — data protection legislation is in progress."
    return "No comprehensive data protection law identified yet."


def desc(c):
    if c["status"] == "a":
        return f'{c["law"]} — status, and how it compares. Awaiting full verification.'
    if c["status"] == "d":
        return "a data protection bill is in progress. Status and updates."
    return "no comprehensive law identified yet. Status and updates."


def main():
    countries = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))
    outdir = ROOT / "countries"
    outdir.mkdir(exist_ok=True)
    written = skipped = 0
    for c in countries:
        if c["slug"] in RICH:
            skipped += 1
            continue
        law_chip = f'<span class="chip">{c["law"]}</span>' if c["law"] else ""
        html = TEMPLATE.format(
            name=c["name"],
            desc=desc(c),
            continent=c["continent"],
            continent_slug=c["continent_slug"],
            lawline=lawline(c),
            status_chip=STATUS_CHIP[c["status"]],
            law_chip=law_chip,
            status_label=STATUS_LABEL[c["status"]],
            law_or_dash=c["law"] or "—",
            summary=SUMMARY[c["status"]].format(name=c["name"], law=c["law"]),
        )
        (outdir / f'{c["slug"]}.html').write_text(html, encoding="utf-8")
        written += 1
    print(f"generated {written} stub pages, kept {skipped} hand-written pages")


if __name__ == "__main__":
    main()
