#!/usr/bin/env python3
"""Generate v2 country pages, the A–Z index, and the compare dataset.

Usage:  python3 v2/scripts/generate.py

Reads the SAME data as v1 (data/countries.json + data/details.json) so both
designs always show identical facts — only the presentation differs, which
is what makes an A/B design test meaningful.

Outputs:
  v2/countries/<slug>.html
  v2/countries.html            (A–Z index)
  v2/assets/compare-data.js
"""
import html
import json
import pathlib

V2 = pathlib.Path(__file__).resolve().parent.parent
ROOT = V2.parent

STATUS_LABEL = {"a": "Active law", "d": "Bill in progress", "n": "No comprehensive law"}
STATUS_PILL = {
    "a": '<span class="pill ok">Active law</span>',
    "d": '<span class="pill warn">Bill in progress</span>',
    "n": '<span class="pill">No comprehensive law</span>',
}

CURATED = {
    "Nigeria": {"law": "NDPA 2023", "authority": "NDPC", "dpo": "Yes — major importance", "reg": "Yes — major importance", "breach": "72 hours", "fine": "₦10m or 2% of turnover", "xborder": "Adequacy or safeguards", "children": "Under 18"},
    "Kenya": {"law": "DPA 2019", "authority": "ODPC", "dpo": "Designation encouraged", "reg": "Yes — mandatory", "breach": "72 hours", "fine": "KES 5m or 1% of turnover", "xborder": "Safeguards + proof to ODPC", "children": "Under 18"},
    "South Africa": {"law": "POPIA 2013", "authority": "Information Regulator", "dpo": "Information Officer — mandatory", "reg": "IO registration only", "breach": "As soon as reasonably possible", "fine": "R10m or 10 years prison", "xborder": "Adequacy, consent, or contract", "children": "Under 18"},
}

FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'>"
           "<rect width='48' height='48' rx='13' fill='%236D5AE6'/>"
           "<circle cx='24' cy='24' r='13' fill='none' stroke='white' stroke-width='2.4'/>"
           "<ellipse cx='24' cy='24' rx='6' ry='13' fill='none' stroke='white' stroke-width='2'/>"
           "<line x1='11' y1='24' x2='37' y2='24' stroke='white' stroke-width='2'/></svg>")

LOGO_SVG = ('<svg width="36" height="36" viewBox="0 0 48 48" aria-hidden="true">'
            '<rect width="48" height="48" rx="13" fill="#6D5AE6"/>'
            '<circle cx="24" cy="24" r="13" fill="none" stroke="#fff" stroke-width="2.4"/>'
            '<ellipse cx="24" cy="24" rx="6" ry="13" fill="none" stroke="#fff" stroke-width="2"/>'
            '<line x1="11" y1="24" x2="37" y2="24" stroke="#fff" stroke-width="2"/></svg>')


def chrome(prefix, active, v1path):
    """Shared banner + header + nav. prefix is '' or '../'."""
    def nav(page, label):
        cls = ' class="active"' if page == active else ""
        return f'<a href="{prefix}{page}"{cls}>{label}</a>'
    return f'''<div class="vbanner">Design&nbsp;B — <b>Bright</b>. <a href="{prefix}../{v1path}">Switch to Design&nbsp;A (Meridian) →</a></div>

<header class="site" id="sitehead">
  <div class="wrap">
    <a class="logo" href="{prefix}index.html">
      {LOGO_SVG}
      <span class="mark">Governance<span>Atlas</span></span>
    </a>
    <nav class="main">
      {nav("countries.html", "Countries")}
      {nav("compare.html", "Compare")}
      {nav("learn.html", "Learn")}
      {nav("resources.html", "Resources")}
      {nav("about.html", "About")}
      <a class="navcta" href="{prefix}countries.html">Find your country</a>
    </nav>
  </div>
</header>'''


def footer(prefix=""):
    return f'''<footer class="site">
  <div class="wrap">
    <div class="fgrid">
      <div class="fbrand">
        <div class="mark">Governance<span>Atlas</span></div>
        <p>Data protection law for every country, in plain English. Community-maintained and open source.</p>
      </div>
      <div class="flinks">
        <a href="{prefix}countries.html">Countries</a>
        <a href="{prefix}compare.html">Compare</a>
        <a href="{prefix}learn.html">Learn</a>
        <a href="{prefix}resources.html">Resources</a>
        <a href="{prefix}about.html">About</a>
      </div>
    </div>
    <div class="fbase">
      <span>Governance Atlas is a reference tool, not legal advice. Laws change and the rules that apply depend on your organisation and its activities. Always check the official sources linked on each country page before relying on the information.</span>
      <span>Developed by <a href="https://ayoadeabel.tech" target="_blank" rel="noopener">Ayoade Adegbite</a></span>
    </div>
  </div>
</footer>'''


def head(title, desc, prefix=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Governance Atlas">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://tripleaceme.github.io/governance-atlas/v2/assets/og-image.png">
<meta property="og:image:secure_url" content="https://tripleaceme.github.io/governance-atlas/v2/assets/og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://tripleaceme.github.io/governance-atlas/v2/assets/og-image.png">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body>'''


STICKY_JS = '''<script>
  const head = document.getElementById("sitehead");
  addEventListener("scroll", () => head.classList.toggle("stuck", scrollY > 8));
</script>'''


def esc(s):
    return html.escape(str(s), quote=True) if s else ""


def gfact(label, value, sub=None):
    if not value:
        return ""
    s = f'<span class="sub">{esc(sub)}</span>' if sub else ""
    return f'      <div class="gfact"><dt>{esc(label)}</dt><dd>{esc(value)}{s}</dd></div>\n'


def country_page(c, d):
    name, cont = c["name"], c["continent"]
    status = (d or {}).get("status", c["status"])
    law = (d or {}).get("law") or c["law"]
    auth = (d or {}).get("authority")
    acro = (d or {}).get("authority_acronym")

    if status == "a" and law:
        lede = f'Primary law: <strong>{esc(law)}</strong>'
        if auth:
            lede += f' — supervised by {esc(auth)}' + (f' ({esc(acro)})' if acro else "")
        lede += "."
    elif status == "d":
        lede = f'No comprehensive law in force yet — <strong>{esc(law or "legislation")}</strong> is in progress.'
    else:
        lede = "No comprehensive data protection law is in force yet."

    pills = STATUS_PILL[status]
    if (d or {}).get("year"):
        pills += f'\n      <span class="pill">Enacted {d["year"]}</span>'
    if (d or {}).get("eu_adequacy"):
        pills += '\n      <span class="pill ok">EU adequacy</span>'
    conf = (d or {}).get("confidence", "")
    if conf:
        pills += f'\n      <span class="pill warn">{"Researched Aug 2026 · pending review" if conf == "high" else "Preliminary research"}</span>'

    adequacy = None if (d or {}).get("eu_adequacy") is None else ("Yes" if d["eu_adequacy"] else "No")
    facts = (
        gfact("Law", law or "—")
        + gfact("Regulator", acro or auth, sub=(auth if acro else None) or (d or {}).get("authority_url"))
        + gfact("DPO", (d or {}).get("dpo"))
        + gfact("Registration", (d or {}).get("registration"))
        + gfact("Breach deadline", (d or {}).get("breach"))
        + gfact("Maximum fine", (d or {}).get("fine"))
        + gfact("Cross-border transfers", (d or {}).get("xborder"))
        + gfact("Children's data", (d or {}).get("children"))
        + gfact("EU adequacy", adequacy)
    )

    body = ""
    if d and d.get("summary"):
        paras = "\n        ".join(f"<p>{esc(p)}</p>" for p in d["summary"])
        body += f'''      <section>
        <h2>The short version</h2>
        <span class="readtime">Compiled from public sources · not legal advice</span>
        {paras}
      </section>
'''
    else:
        body += f'''      <section>
        <h2>The short version</h2>
        <p>A full brief for {esc(name)} is still being prepared.</p>
      </section>
'''
    if d and d.get("obligations"):
        items = "\n".join(
            f'          <li><span class="n">{i+1:02d}</span><div><b>{esc(o["title"])}</b> — {esc(o["text"])}</div></li>'
            for i, o in enumerate(d["obligations"]))
        body += f'''
      <section>
        <h2>What you actually have to do</h2>
        <ul class="obl">
{items}
        </ul>
      </section>
'''
    if d and d.get("sources"):
        cards = "\n".join(
            f'          <a class="src" href="{esc(s["url"])}" target="_blank" rel="noopener">'
            f'<span class="k">{esc(s.get("kind") or "Reference")}</span>'
            f'<span class="t">{esc(s["title"])}</span></a>'
            for s in d["sources"])
        body += f'''
      <section>
        <h2>Sources</h2>
        <div class="srcs">
{cards}
        </div>
      </section>
'''
    if d and d.get("notes"):
        body += f'''
      <section>
        <p style="color:var(--ink-faint);font-size:.94rem"><em>Note: {esc(d["notes"])}</em></p>
      </section>
'''

    title = f'{esc(name)}' + (f' — {esc(law)}' if law else "") + ' — Governance Atlas'
    desc = esc(f'Data protection law in {name}: ' + (law or "status and landscape") + " — plain-English brief, obligations and official sources.")

    return f'''{head(title, desc, "../")}

{chrome("../", "countries.html", "countries/" + c["slug"] + ".html")}

<section class="pagehead">
  <div class="wrap">
    <div class="crumbs">
      <a href="../index.html">Home</a><span>›</span>
      <a href="../countries.html">Countries</a><span>›</span>
      <span class="here">{esc(name)}</span>
    </div>
    <h1>{esc(name)}</h1>
    <p class="lede">{lede}</p>
    <div class="pills">
      {pills}
    </div>
  </div>
</section>

<div class="wrap">
  <div class="cols">
    <aside class="glance">
      <h2>At a glance</h2>
      <dl style="margin:0">
{facts}      </dl>
    </aside>
    <article>
{body}
      <section>
        <h2>Compare {esc(name)}</h2>
        <p>See how {esc(name)} lines up against any other country — DPO rules, deadlines, penalties and transfer requirements, side by side.</p>
        <a class="btn" href="../compare.html" style="font-size:.94rem;padding:13px 30px">Open the comparison tool</a>
      </section>
    </article>
  </div>
</div>

{footer("../")}
{STICKY_JS}

</body>
</html>
'''


def index_page(countries, details):
    groups = {}
    for c in sorted(countries, key=lambda x: x["name"]):
        groups.setdefault(c["name"][0].upper(), []).append(c)
    az = "".join(f'<a href="#L{k}">{k}</a>' for k in sorted(groups))
    blocks = ""
    for letter in sorted(groups):
        items = ""
        for c in groups[letter]:
            d = details.get(c["slug"]) or {}
            st = d.get("status", c["status"])
            law = d.get("law") or c["law"] or STATUS_LABEL[st]
            items += (f'        <a class="azitem" href="countries/{c["slug"]}.html">'
                      f'<span class="st {st}"></span>'
                      f'<span class="nm">{esc(c["name"])}<span class="law">{esc(law)}</span></span></a>\n')
        blocks += f'''    <div class="azgroup" id="L{letter}">
      <h3>{letter}</h3>
      <div class="azgrid">
{items}      </div>
    </div>
'''
    return f'''{head("All countries — Governance Atlas", "Every country's data protection law, A to Z — 194 plain-English briefs with regulators, deadlines, penalties and official sources.")}

{chrome("", "countries.html", "countries.html")}

<section class="pagehead">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span>›</span><span class="here">Countries</span></div>
    <h1>All countries, A–Z</h1>
    <p class="lede">Every country on Earth has a brief — including the ones with no comprehensive law yet. Green means a law is in force, amber means a bill is in progress, grey means neither.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="azbar">{az}</div>
{blocks}  </div>
</section>

{footer()}
{STICKY_JS}

</body>
</html>
'''


def main():
    countries = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))
    dpath = ROOT / "data" / "details.json"
    details = json.loads(dpath.read_text(encoding="utf-8")) if dpath.exists() else {}

    outdir = V2 / "countries"
    outdir.mkdir(parents=True, exist_ok=True)
    compare = {}
    for c in countries:
        d = details.get(c["slug"])
        (outdir / f'{c["slug"]}.html').write_text(country_page(c, d), encoding="utf-8")
        if c["name"] in CURATED:
            compare[c["name"]] = {"continent": c["continent"], **CURATED[c["name"]]}
        elif d:
            compare[c["name"]] = {
                "continent": c["continent"], "law": d.get("law") or STATUS_LABEL[d["status"]],
                "authority": d.get("authority_acronym") or d.get("authority") or "—",
                "dpo": d.get("dpo") or "—", "reg": d.get("registration") or "—",
                "breach": d.get("breach") or "—", "fine": d.get("fine") or "—",
                "xborder": d.get("xborder") or "—", "children": d.get("children") or "—",
            }
        else:
            ph = "Not researched yet"
            compare[c["name"]] = {"continent": c["continent"], "law": c["law"] or STATUS_LABEL[c["status"]],
                                  "authority": ph, "dpo": ph, "reg": ph, "breach": ph, "fine": ph, "xborder": ph, "children": ph}

    (V2 / "countries.html").write_text(index_page(countries, details), encoding="utf-8")
    (V2 / "assets" / "compare-data.js").write_text(
        "// Generated by v2/scripts/generate.py — do not edit by hand.\n"
        "const DATA = " + json.dumps(compare, ensure_ascii=False, indent=2, sort_keys=True) + ";\n",
        encoding="utf-8")

    print(f"v2: {len(countries)} country pages, A–Z index, {len(compare)} compare records")


if __name__ == "__main__":
    main()
