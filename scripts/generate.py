#!/usr/bin/env python3
"""Generate country pages + the compare dataset from the data files.

Usage:  python3 scripts/generate.py

Inputs:
  data/countries.json  canonical base record per country (slug, name, code,
                       continent, status a/d/n, law)
  data/details.json    optional researched details keyed by slug (authority,
                       dpo, breach, fine, summary, obligations, sources, …)

Outputs:
  countries/<slug>.html   full dossier when details exist, honest stub when not
                          (slugs in RICH are hand-written and never overwritten)
  assets/compare-data.js  compare-tool dataset covering every country

Zero dependencies; safe to re-run (idempotent).
"""
import html
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

# Curated compare entries for the hand-written pages (never researched).
CURATED_COMPARE = {
    "Nigeria": {"continent": "Africa", "law": "NDPA 2023", "authority": "NDPC", "dpo": "Yes — major importance", "reg": "Yes — major importance", "breach": "72 hours", "fine": "₦10m or 2% of turnover", "xborder": "Adequacy or safeguards", "children": "Under 18"},
    "Kenya": {"continent": "Africa", "law": "DPA 2019", "authority": "ODPC", "dpo": "Designation encouraged", "reg": "Yes — mandatory", "breach": "72 hours", "fine": "KES 5m or 1% of turnover", "xborder": "Safeguards + proof to ODPC", "children": "Under 18"},
    "South Africa": {"continent": "Africa", "law": "POPIA 2013", "authority": "Information Regulator", "dpo": "Information Officer — mandatory", "reg": "IO registration only", "breach": "As soon as reasonably possible", "fine": "R10m or 10 years prison", "xborder": "Adequacy, consent, or contract", "children": "Under 18"},
}

PAGE_SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Governance Atlas</title>
<meta name="description" content="{meta_desc}">
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
      <a href="../learn.html">Learn</a>
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
      {chips}
    </div>
  </div>

  <div class="cols">
    <aside class="dossier">
      <h2>At a glance</h2>
      <dl style="margin:0">
{facts}
      </dl>
    </aside>

    <article>
{article}
      <section>
        <h2>Help improve this page</h2>
        <p>Governance Atlas is community-maintained. Corrections and official sources for {name} are always welcome —
        <a href="https://github.com/tripleaceme/governance-atlas" target="_blank" rel="noopener">contribute on GitHub ↗</a></p>
      </section>

      <section>
        <h2>Compare</h2>
        <p class="comparecta"><a href="../compare.html">Open the comparison tool → see how {name} compares side by side</a></p>
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


def esc(s):
    return html.escape(str(s), quote=True) if s else ""


def fact(label, value, sub=None, cls=""):
    if not value:
        return ""
    sub_html = f'<span class="sub">{esc(sub)}</span>' if sub else ""
    dd_cls = f' class="{cls}"' if cls else ""
    return f'        <div class="fact"><dt>{esc(label)}</dt><dd{dd_cls}>{esc(value)}{sub_html}</dd></div>\n'


# ── Stub rendering (no researched details yet) ─────────────────────────────

def stub_lawline(c):
    if c["status"] == "a":
        return f'Primary law: <strong>{esc(c["law"])}</strong>. Full dossier coming — this page is awaiting verification against official sources.'
    if c["status"] == "d":
        return "No comprehensive law in force yet — data protection legislation is in progress."
    return "No comprehensive data protection law identified yet."


def render_stub(c):
    summaries = {
        "a": f'<p>{esc(c["name"])} has an active comprehensive data protection law: <strong>{esc(c["law"])}</strong>. A full plain-English dossier for this page is being prepared and verified against primary sources.</p>',
        "d": f'<p>{esc(c["name"])} does not yet have a comprehensive data protection law in force, but legislation is in progress ({esc(c["law"])}). This page will be expanded as the bill advances.</p>',
        "n": f'<p>No comprehensive data protection law has been identified for {esc(c["name"])} yet. Sector-specific rules, cybercrime laws, or constitutional privacy rights may still apply.</p>',
    }
    facts = (
        fact("Continent", c["continent"])
        + fact("Status", STATUS_LABEL[c["status"]])
        + fact("Primary law", c["law"] or "—")
        + fact("Page status", "Stub — awaiting research", cls="no")
    )
    article = f"""      <section>
        <h2>What we know</h2>
        <span class="readtime">Stub page · not legal advice</span>
        {summaries[c["status"]]}
        <p>For an example of a completed page, see the
        <a href="nigeria.html">Nigeria dossier</a>.</p>
      </section>
"""
    chips = STATUS_CHIP[c["status"]]
    if c["law"]:
        chips += f'\n      <span class="chip">{esc(c["law"])}</span>'
    chips += '\n      <span class="chip verified">Awaiting research</span>'
    return PAGE_SHELL.format(
        title=esc(c["name"]), meta_desc=esc(f'Data protection law in {c["name"]} — status and updates.'),
        continent=esc(c["continent"]), continent_slug=c["continent_slug"], name=esc(c["name"]),
        lawline=stub_lawline(c), chips=chips, facts=facts, article=article,
    )


# ── Full dossier rendering (researched details) ────────────────────────────

def full_lawline(c, d):
    auth = d.get("authority")
    if d["status"] == "a" and d.get("law"):
        line = f'Primary law: <strong>{esc(d["law"])}</strong>'
        if auth:
            line += f" — supervised by {esc(auth)}"
            if d.get("authority_acronym"):
                line += f' ({esc(d["authority_acronym"])})'
        return line + "."
    if d["status"] == "d":
        return f'No comprehensive law in force yet — <strong>{esc(d.get("law") or "data protection legislation")}</strong> is in progress.'
    return "No comprehensive data protection law is in force."


def render_full(c, d):
    conf = d.get("confidence", "low")
    verified_chip = "Researched Aug 2026 · pending review" if conf == "high" else "Preliminary research · Aug 2026"

    chips = STATUS_CHIP[d["status"]]
    if d.get("year"):
        chips += f'\n      <span class="chip">Enacted {d["year"]}</span>'
    if d.get("eu_adequacy"):
        chips += '\n      <span class="chip active">EU adequacy</span>'
    chips += f'\n      <span class="chip verified">{verified_chip}</span>'

    adequacy = None if d.get("eu_adequacy") is None else ("Yes" if d["eu_adequacy"] else "No")
    facts = (
        fact("Law", d.get("law") or "—")
        + fact("Authority", d.get("authority_acronym") or d.get("authority"),
               sub=(d.get("authority") if d.get("authority_acronym") else None) or d.get("authority_url"))
        + fact("DPO", d.get("dpo"))
        + fact("Registration", d.get("registration"))
        + fact("Breach notification", d.get("breach"))
        + fact("Max fine", d.get("fine"))
        + fact("Cross-border transfers", d.get("xborder"))
        + fact("Children's data", d.get("children"))
        + fact("EU adequacy", adequacy, cls=("yes" if adequacy == "Yes" else "no") if adequacy else "")
    )

    paragraphs = "\n        ".join(f"<p>{esc(p)}</p>" for p in d.get("summary", []))
    article = f"""      <section>
        <h2>Executive summary</h2>
        <span class="readtime">Compiled from public sources · not legal advice</span>
        {paragraphs}
      </section>
"""
    obligations = d.get("obligations") or []
    if obligations:
        items = "\n".join(
            f'          <li><span class="n">{i + 1:02d}</span><div><b>{esc(o["title"])}</b> — {esc(o["text"])}</div></li>'
            for i, o in enumerate(obligations)
        )
        article += f"""
      <section>
        <h2>Key obligations</h2>
        <ul class="obligations">
{items}
        </ul>
      </section>
"""
    sources = d.get("sources") or []
    if sources:
        cards = "\n".join(
            f'          <a class="source" href="{esc(s["url"])}" target="_blank" rel="noopener">'
            f'<span class="kind">{esc(s.get("kind") or "Reference")}</span>'
            f'<span class="t">{esc(s["title"])}</span> <span class="ext">↗</span></a>'
            for s in sources
        )
        article += f"""
      <section>
        <h2>Sources</h2>
        <div class="sources">
{cards}
        </div>
      </section>
"""
    if d.get("notes"):
        article += f"""
      <section>
        <p class="sect-sub"><em>Note: {esc(d["notes"])}</em></p>
      </section>
"""
    return PAGE_SHELL.format(
        title=esc(c["name"]) + (f' — {esc(d["law"])}' if d.get("law") else ""),
        meta_desc=esc(f'Data protection law in {c["name"]}: ' + (d.get("law") or "status, landscape, and sources") + " — plain-English summary, obligations, and official sources."),
        continent=esc(c["continent"]), continent_slug=c["continent_slug"], name=esc(c["name"]),
        lawline=full_lawline(c, d), chips=chips, facts=facts, article=article,
    )


# ── Compare dataset ────────────────────────────────────────────────────────

def compare_entry(c, d):
    if c["name"] in CURATED_COMPARE:
        return CURATED_COMPARE[c["name"]]
    ph = "Awaiting research"
    if d:
        return {
            "continent": c["continent"],
            "law": d.get("law") or STATUS_LABEL[d["status"]],
            "authority": d.get("authority_acronym") or d.get("authority") or "—",
            "dpo": d.get("dpo") or "—", "reg": d.get("registration") or "—",
            "breach": d.get("breach") or "—", "fine": d.get("fine") or "—",
            "xborder": d.get("xborder") or "—", "children": d.get("children") or "—",
        }
    return {
        "continent": c["continent"], "law": c["law"] or STATUS_LABEL[c["status"]],
        "authority": ph, "dpo": ph, "reg": ph, "breach": ph, "fine": ph, "xborder": ph, "children": ph,
    }


def main():
    countries = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))
    details_path = ROOT / "data" / "details.json"
    details = json.loads(details_path.read_text(encoding="utf-8")) if details_path.exists() else {}

    outdir = ROOT / "countries"
    outdir.mkdir(exist_ok=True)
    full = stub = 0
    compare = {}
    for c in countries:
        d = details.get(c["slug"])
        compare[c["name"]] = compare_entry(c, d)
        if c["slug"] in RICH:
            continue
        if d and d.get("summary"):
            (outdir / f'{c["slug"]}.html').write_text(render_full(c, d), encoding="utf-8")
            full += 1
        else:
            (outdir / f'{c["slug"]}.html').write_text(render_stub(c), encoding="utf-8")
            stub += 1

    compare_js = (
        "// Generated by scripts/generate.py — do not edit by hand.\n"
        "const DATA = " + json.dumps(compare, ensure_ascii=False, indent=2, sort_keys=True) + ";\n"
    )
    (ROOT / "assets" / "compare-data.js").write_text(compare_js, encoding="utf-8")
    print(f"generated {full} full dossiers, {stub} stubs, kept {len(RICH)} hand-written pages")
    print(f"compare dataset: {len(compare)} countries → assets/compare-data.js")


if __name__ == "__main__":
    main()
