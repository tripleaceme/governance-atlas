#!/usr/bin/env python3
"""Generate the three-domain Governance Atlas.

Usage:  python3 v2/scripts/generate.py

Reads:
  v2/data/countries.json           one record per country (shared by all domains)
  v2/data/domains/<domain>.json    researched detail per country, per domain

Writes, for each domain in domains.ORDER:
  v2/<domain>/index.html           domain home: search + world map
  v2/<domain>/countries.html       A–Z index
  v2/<domain>/compare.html         three-country comparison
  v2/<domain>/countries/<slug>.html
  v2/assets/<domain>-map.js        map dataset
  v2/assets/<domain>-compare.js    compare dataset

Country pages that have no researched entry render an honest "not yet
researched" page rather than 404ing, so the domain switcher always lands
somewhere sensible.
"""
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from domains import DOMAINS, ORDER, STATUS_LABEL, STATUS_CHIP  # noqa: E402

V2 = pathlib.Path(__file__).resolve().parent.parent
BASE = ""  # relative links while developing locally

LOGO = ('<svg class="logomark" width="36" height="36" viewBox="0 0 48 48" aria-hidden="true">'
        '<circle cx="24" cy="24" r="22" fill="none" stroke="var(--accent)" stroke-width="1" stroke-dasharray="2 3"/>'
        '<circle cx="24" cy="24" r="17" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<ellipse cx="24" cy="24" rx="8" ry="17" fill="none" stroke="currentColor" stroke-width="1.4"/>'
        '<line x1="7" y1="24" x2="41" y2="24" stroke="currentColor" stroke-width="1.4"/>'
        '<line x1="24" y1="7" x2="24" y2="41" stroke="currentColor" stroke-width="1.4"/>'
        '<circle cx="21" cy="27" r="2.4" fill="var(--accent)"/></svg>')

FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'>"
           "<circle cx='24' cy='24' r='22' fill='none' stroke='%23a23c2a' stroke-width='1.5' stroke-dasharray='2 3'/>"
           "<circle cx='24' cy='24' r='17' fill='none' stroke='%2322304a' stroke-width='2.5'/>"
           "<ellipse cx='24' cy='24' rx='8' ry='17' fill='none' stroke='%2322304a' stroke-width='1.6'/>"
           "<line x1='7' y1='24' x2='41' y2='24' stroke='%2322304a' stroke-width='1.6'/>"
           "<line x1='24' y1='7' x2='24' y2='41' stroke='%2322304a' stroke-width='1.6'/>"
           "<circle cx='21' cy='27' r='3' fill='%23a23c2a'/></svg>")


def esc(s):
    return html.escape(str(s), quote=True) if s not in (None, "") else ""


def head(title, desc, up):
    """up = relative prefix back to v2 root, e.g. '../' or '../../'"""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{up}assets/styles.css">
</head>
<body>'''


def switcher(active_domain, country_slug=None, up="../"):
    """Domain switcher.

    Keeps the country in context when switching between trackers. A guide area
    has no per-country pages, so it always lands on its own front page.
    """
    items = ""
    for key in ORDER:
        d = DOMAINS[key]
        if country_slug and d.get("kind") != "guide":
            target = f'{up}{key}/countries/{country_slug}.html'
        else:
            target = f'{up}{key}/index.html'
        cls = " on" if key == active_domain else ""
        items += f'      <a class="dbtn{cls}" href="{target}">{d["nav_label"]}</a>\n'
    return f'''<div class="domainbar">
  <div class="wrap">
    <span class="dlabel">Area</span>
    <nav class="dswitch">
{items}    </nav>
  </div>
</div>'''


def header(domain, up="../", active=""):
    d = DOMAINS[domain]

    def nav(page, label):
        cls = ' class="active"' if page == active else ""
        return f'<a href="{up}{domain}/{page}"{cls}>{label}</a>'

    # A guide has one page, so it offers no country index or compare tool.
    if d.get("kind") == "guide":
        own = "      " + nav("index.html", "Practices")
    else:
        own = ("      " + nav("index.html", "Atlas") + "\n"
               "      " + nav("countries.html", "Countries") + "\n"
               "      " + nav("compare.html", "Compare"))

    return f'''<header class="site">
  <div class="wrap">
    <a class="logo" href="{up}index.html" title="Governance Atlas home">
      {LOGO}
      <div>
        <div class="mark">Governance<span>·</span>Atlas</div>
        <div class="tag">{d["tagline"]}</div>
      </div>
    </a>
    <nav class="main">
{own}
      <a href="{up}learn.html">Learn</a>
      <a href="{up}resources.html">Resources</a>
      <a href="{up}templates.html">Templates</a>
      <a href="{up}about.html">About</a>
    </nav>
  </div>
</header>'''


def footer(up="../"):
    return f'''<footer class="site">
  <div class="wrap">
    <div>Governance Atlas is a reference tool, not legal advice. Laws change and the rules that apply depend on your organisation and its activities. Always check the official sources linked on each country page before relying on the information.</div>
    <div class="credits">
      <span>Developed by <a href="https://ayoadeabel.tech" target="_blank" rel="noopener">Ayoade Adegbite</a></span>
    </div>
  </div>
</footer>'''


# ── country page ───────────────────────────────────────────────────────────

def country_page(domain, c, d):
    cfg = DOMAINS[domain]
    name = c["name"]
    researched = bool(d)
    status = (d or {}).get("status", c["status"] if domain == "personal" else "n")

    if researched and d.get("law"):
        lede = f'Primary regulation: <strong>{esc(d["law"])}</strong>'
        if d.get("authority"):
            lede += f' — {esc(cfg["regulator_label"]).lower()}: {esc(d["authority"])}'
            if d.get("authority_acronym"):
                lede += f' ({esc(d["authority_acronym"])})'
        lede += "."
    elif researched and status == "d":
        lede = f'No comprehensive regulation in force yet — <strong>{esc(d.get("law") or "legislation")}</strong> is in progress.'
    elif researched:
        lede = f"No comprehensive {cfg['title'].lower()} regulation is in force."
    else:
        lede = (esc(name) + "&#39;s " + cfg["title"].lower() + " position has not been researched yet. "
                "This page is a placeholder so the regulation-area switcher always has somewhere to land.")

    chips = STATUS_CHIP[status] if researched else '<span class="chip">Not yet researched</span>'
    if researched and d.get("year"):
        chips += f'\n      <span class="chip">Enacted {d["year"]}</span>'

    facts = ""
    if researched:
        for key, label in cfg["fields"]:
            v = d.get(key)
            if key == "eu_adequacy":
                v = None if v is None else ("Yes" if v else "No")
            if key == "authority":
                v = d.get("authority_acronym") or d.get("authority")
            if v:
                facts += f'        <div class="fact"><dt>{esc(label)}</dt><dd>{esc(v)}</dd></div>\n'
    if not facts:
        facts = ('        <div class="fact"><dt>Regulation area</dt><dd>' + esc(cfg["label"]) + '</dd></div>\n'
                 '        <div class="fact"><dt>Status</dt><dd>Not yet researched</dd></div>\n')

    body = ""
    if researched and d.get("summary"):
        paras = "\n        ".join(f"<p>{esc(p)}</p>" for p in d["summary"])
        body += f'''      <section>
        <h2>Executive summary</h2>
        <span class="readtime">Compiled from public sources · not legal advice</span>
        {paras}
      </section>
'''
    else:
        nm, dt = esc(name), esc(cfg["title"].lower())
        bl = esc(cfg["blurb"][0].lower() + cfg["blurb"][1:])
        others = [k for k in ORDER if k != domain]
        # Sibling trackers have a page for this country; a guide only has a front page.
        tracked = [f'<a href="../../{k}/countries/{c["slug"]}.html">{DOMAINS[k]["label"].lower()}</a>'
                   for k in others if DOMAINS[k].get("kind") != "guide"]
        guides = [f'<a href="../../{k}/index.html">{DOMAINS[k]["label"].lower()} guide</a>'
                  for k in others if DOMAINS[k].get("kind") == "guide"]
        parts = []
        if tracked:
            parts.append(f'{nm}&#39;s ' + " or ".join(tracked) + " page")
        if guides:
            parts.append("the " + " or ".join(guides))
        links = ", or ".join(parts)
        body += f'''      <section>
        <h2>Not yet researched</h2>
        <p>We have not yet compiled {nm}&#39;s position on {dt}. This area covers {bl}</p>
        <p>In the meantime you can read {links}, or help by
        <a href="https://github.com/tripleaceme/governance-atlas" target="_blank" rel="noopener">contributing what you know</a>.</p>
      </section>
'''
    if researched and d.get("obligations"):
        items = "\n".join(
            f'          <li><span class="n">{i+1:02d}</span><div><b>{esc(o["title"])}</b> — {esc(o["text"])}</div></li>'
            for i, o in enumerate(d["obligations"]))
        body += f'''
      <section>
        <h2>Key obligations</h2>
        <ul class="obligations">
{items}
        </ul>
      </section>
'''
    if researched and d.get("sources"):
        cards = "\n".join(
            f'          <a class="source" href="{esc(s["url"])}" target="_blank" rel="noopener">'
            f'<span class="kind">{esc(s.get("kind") or "Reference")}</span>'
            f'<span class="t">{esc(s["title"])}</span> <span class="ext">↗</span></a>'
            for s in d["sources"])
        body += f'''
      <section>
        <h2>Official sources</h2>
        <div class="sources">
{cards}
        </div>
      </section>
'''

    title = f'{esc(name)} — {esc(cfg["title"])} — Governance Atlas'
    desc = esc(f'{cfg["title"]} in {name}: ' + ((d or {}).get("law") or "status, regulator and obligations") + ".")

    return f'''{head(title, desc, "../../")}

{switcher(domain, c["slug"], "../../")}
{header(domain, "../../", "countries.html")}

<div class="wrap">
  <div class="crumbs">
    <a href="../index.html">{esc(cfg["label"])}</a><span class="sep">›</span>
    <a href="../countries.html">Countries</a><span class="sep">›</span>
    <span class="here">{esc(name)}</span>
  </div>

  <div class="hero">
    <div class="plate">Plate {esc(c["code"])} · {esc(c["continent"])} · {esc(cfg["label"])}</div>
    <h1>{esc(name)}</h1>
    <p class="lawline">{lede}</p>
    <div class="chips">
      {chips}
    </div>
  </div>

  <div class="cols">
    <aside class="dossier">
      <h2>At a glance</h2>
      <dl style="margin:0">
{facts}      </dl>
    </aside>
    <article>
{body}
      <section>
        <h2>Compare</h2>
        <p class="comparecta"><a href="../compare.html">Compare {esc(name)} with other countries →</a></p>
      </section>
    </article>
  </div>
</div>

{footer("../../")}

</body>
</html>
'''


# ── guide area (one explanatory page, no per-country data) ─────────────────

def guide_page(domain):
    """Front page of a 'guide' area.

    The prose lives in content/<file> rather than in this module: it is long,
    it is edited like copy rather than like code, and keeping it out of an
    f-string avoids escaping every apostrophe and brace it contains.
    """
    cfg = DOMAINS[domain]
    body = (V2 / "content" / cfg["content"]).read_text(encoding="utf-8")

    shell = f'''{head(f'{esc(cfg["title"])} — Governance Atlas', esc(cfg["blurb"]), "../")}

{switcher(domain, None, "../")}
{header(domain, "../", "index.html")}

<div class="wrap">
  <div class="crumbs">
    <a href="../index.html">Home</a><span class="sep">›</span>
    <span class="here">{esc(cfg["label"])}</span>
  </div>

  <div class="hero">
    <div class="plate">{esc(cfg["hero_plate"])}</div>
    <h1>{esc(cfg["hero_h1"])}</h1>
    <p class="lawline">{cfg["hero_sub"]}</p>
  </div>

@@BODY@@
</div>

{footer("../")}

</body>
</html>
'''
    return shell.replace("@@BODY@@", body)


def intro(domain):
    """Optional explanatory block appended to a tracker's front page.

    Some areas need framing before a map of them means anything. General data
    is one: the regulation is patchy and differently named everywhere, so the
    page says what the field covers before showing which countries legislate
    parts of it.
    """
    name = DOMAINS[domain].get("intro")
    return "\n" + (V2 / "content" / name).read_text(encoding="utf-8") if name else ""


# ── domain home (search + map) ─────────────────────────────────────────────

def domain_home(domain, countries, details):
    cfg = DOMAINS[domain]
    counts = {"a": 0, "d": 0, "n": 0}
    for c in countries:
        d = details.get(c["slug"])
        s = (d or {}).get("status", c["status"] if domain == "personal" else "n")
        counts[s] = counts.get(s, 0) + 1
    researched = sum(1 for c in countries if details.get(c["slug"]))

    return f'''{head(f'{esc(cfg["title"])} — Governance Atlas', esc(cfg["blurb"]), "../")}

{switcher(domain, None, "../")}
{header(domain, "../", "index.html")}

<div class="wrap">
  <div class="hero ceremony">
    <div class="plate">{esc(cfg["label"])}</div>
    <h1 class="big">{cfg["hero_h1"]}</h1>
    <p class="lawline">{cfg["hero_sub"]}</p>
    <div class="ctarow">
      <a class="cta" href="#browse">Open the Atlas</a>
      <a class="cta ghost" href="../learn.html">New to data protection? Start here</a>
    </div>

    <div class="stats proof">
      <div class="stat"><div class="num">{len(countries)}</div><div class="lbl">Countries tracked</div></div>
      <div class="stat s-active"><div class="num">{counts["a"]}</div><div class="lbl">In force</div></div>
      <div class="stat s-draft"><div class="num">{counts["d"]}</div><div class="lbl">In progress</div></div>
      <div class="stat"><div class="num">{researched}</div><div class="lbl">Researched</div></div>
    </div>
  </div>

  <div class="contzone" id="browse">
    <h2 class="sect">Browse by continent</h2>
    <p class="sect-sub">{esc(cfg["blurb"])}</p>

    <div class="findrow">
      <div class="searchbig">
        <input type="search" id="homesearch" placeholder="Which country do you need? e.g. Nigeria, Germany, Brazil" aria-label="Search a country" autocomplete="off">
        <div class="sugg" id="homesugg"></div>
      </div>
    </div>

    <div class="browsebar">
      <div class="mapfilters" id="mapfilters"></div>
    </div>

    <div id="mapview">
      <div class="worldmap" id="worldmap" role="img" aria-label="World map of {esc(cfg["title"].lower())} status by country"></div>
      <div class="maplegend">
        <span><i class="dot a"></i> In force</span>
        <span><i class="dot d"></i> In progress</span>
        <span><i class="dot n"></i> No comprehensive regulation</span>
      </div>
      <div class="hoverbar" id="maphover">Hover a country or click to open its page.</div>
    </div>
  </div>
{intro(domain)}</div>

{footer("../")}

<script src="../assets/{domain}-map.js"></script>
<script src="../assets/atlas-map.js"></script>

</body>
</html>
'''


# ── A–Z index ──────────────────────────────────────────────────────────────

def index_page(domain, countries, details):
    cfg = DOMAINS[domain]
    groups = {}
    for c in sorted(countries, key=lambda x: x["name"]):
        groups.setdefault(c["name"][0].upper(), []).append(c)
    az = "".join(f'<a href="#L{k}">{k}</a>' for k in sorted(groups))
    blocks = ""
    for letter in sorted(groups):
        items = ""
        for c in groups[letter]:
            d = details.get(c["slug"])
            st = (d or {}).get("status", c["status"] if domain == "personal" else "n")
            law = (d or {}).get("law") or (STATUS_LABEL[st] if d else "Not yet researched")
            items += (f'        <a class="ccard" href="countries/{c["slug"]}.html">'
                      f'<span class="st {st}"></span><span class="nm">{esc(c["name"])}'
                      f'<span class="law">{esc(law)}</span></span><span class="go">→</span></a>\n')
        blocks += f'''    <div class="azgroup" id="L{letter}">
      <h3 class="sect" style="text-align:left">{letter}</h3>
      <div class="cgrid">
{items}      </div>
    </div>
'''
    idx_title = "All countries — " + esc(cfg["title"]) + " — Governance Atlas"
    idx_desc = esc("Every country's " + cfg["title"].lower() + " position, A to Z.")
    return f'''{head(idx_title, idx_desc, "../")}

{switcher(domain, None, "../")}
{header(domain, "../", "countries.html")}

<div class="wrap">
  <div class="crumbs"><a href="index.html">{esc(cfg["label"])}</a><span class="sep">›</span><span class="here">Countries</span></div>

  <div class="hero">
    <div class="plate">{esc(cfg["label"])}</div>
    <h1>All countries, A–Z</h1>
    <p class="lawline">{esc(cfg["blurb"])}</p>
  </div>

  <div class="indexzone">
    <div class="azbar" style="display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin-bottom:34px">{az}</div>
{blocks}  </div>
</div>

{footer("../")}

</body>
</html>
'''


# ── compare ────────────────────────────────────────────────────────────────

def compare_page(domain):
    cfg = DOMAINS[domain]
    rows = json.dumps(cfg["compare_rows"], ensure_ascii=False)
    return f'''{head(f'Compare — {esc(cfg["title"])} — Governance Atlas', esc(f'Compare {cfg["title"].lower()} requirements across countries.'), "../")}

{switcher(domain, None, "../")}
{header(domain, "../", "compare.html")}

<div class="wrap">
  <div class="crumbs"><a href="index.html">{esc(cfg["label"])}</a><span class="sep">›</span><span class="here">Compare</span></div>

  <div class="hero">
    <div class="plate">{esc(cfg["label"])}</div>
    <h1>Compare countries</h1>
    <p class="lawline">Pick up to three countries and compare their {esc(cfg["title"].lower())} requirements side by side.</p>
  </div>

  <div class="pickrow" style="display:flex;gap:12px;flex-wrap:wrap;margin:26px 0 22px">
    <div class="pick"><label for="sel0">Country 1</label><select id="sel0"></select></div>
    <div class="pick"><label for="sel1">Country 2</label><select id="sel1"></select></div>
    <div class="pick"><label for="sel2">Country 3</label><select id="sel2"></select></div>
  </div>

  <div class="tablewrap"><table id="cmptable"></table></div>
  <p class="sect-sub" style="margin-top:14px">The comparison is a starting point, not a legal assessment. Always check the official sources linked on each country's page.</p>
</div>

{footer("../")}

<script src="../assets/{domain}-compare.js"></script>
<script>
  const ROWS = {rows};
  const NAMES = Object.keys(DATA).sort();
  const sels = [0,1,2].map(i => document.getElementById("sel"+i));
  const DEFAULTS = NAMES.includes("Nigeria") ? ["Nigeria","Kenya","South Africa"] : NAMES.slice(0,3);
  sels.forEach((sel,i) => {{
    if (i === 2) sel.add(new Option("— none —",""));
    NAMES.forEach(n => sel.add(new Option(n + " (" + DATA[n].continent + ")", n)));
    sel.value = DEFAULTS[i] || ""; sel.addEventListener("change", render);
  }});
  function render() {{
    const chosen = sels.map(s => s.value).filter(Boolean);
    document.getElementById("cmptable").innerHTML =
      "<thead><tr><th>Requirement</th>" + chosen.map(n => "<th>"+n+"</th>").join("") + "</tr></thead><tbody>" +
      ROWS.map(([l,k]) => "<tr><td>"+l+"</td>" + chosen.map(n => "<td>"+(DATA[n][k] || "—")+"</td>").join("") + "</tr>").join("") + "</tbody>";
  }}
  render();
</script>

</body>
</html>
'''


# ── site home: pick a regulation area ──────────────────────────────────────

def site_home(countries, all_details):
    cards = ""
    for key in ORDER:
        cfg = DOMAINS[key]
        if cfg.get("kind") == "guide":
            state = cfg["card_state"]
        else:
            det = all_details[key]
            n = sum(1 for c in countries if det.get(c["slug"]))
            state = f"{n} of {len(countries)} researched" if n else "Not yet researched"
        cards += f'''      <a class="aud" href="{key}/index.html">
        <span class="who">{esc(state)}</span>
        <h3>{esc(cfg["title"])}</h3>
        <p>{esc(cfg["blurb"])}</p>
        <span class="go2">Open {esc(cfg["label"].lower())} →</span>
      </a>
'''
    return f'''{head("Governance Atlas — Data regulation, country by country",
                     "Personal data protection and general data regulation for every country, plus a practical guide to data security.", "")}

<header class="site">
  <div class="wrap">
    <a class="logo" href="index.html" title="Governance Atlas home">
      {LOGO}
      <div>
        <div class="mark">Governance<span>·</span>Atlas</div>
        <div class="tag">Data regulation, by country</div>
      </div>
    </a>
    <nav class="main">
      <a href="index.html" class="active">Atlas</a>
      <a href="learn.html">Learn</a>
      <a href="resources.html">Resources</a>
      <a href="about.html">About</a>
    </nav>
  </div>
</header>

<div class="wrap">
  <div class="hero ceremony">
    <div class="plate">The World</div>
    <h1 class="big">Data regulation, country by country.</h1>
    <p class="lawline">Three questions govern data: who may hold information about people, how that data must be protected, and where it is allowed to live. Pick the one you need.</p>
  </div>

  <div class="audzone">
    <h2 class="sect">Choose an area</h2>
    <p class="sect-sub">Two are tracked country by country, because the rules genuinely differ. The third is a practice guide, because the rules mostly do not.</p>
    <div class="audgrid">
{cards}    </div>
  </div>
</div>

{footer("")}

</body>
</html>
'''


def main():
    countries = json.loads((V2 / "data" / "countries.json").read_text(encoding="utf-8"))
    all_details = {}
    for key in ORDER:
        p = V2 / "data" / "domains" / f"{key}.json"
        all_details[key] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    total_pages = 0
    for key in ORDER:
        cfg, details = DOMAINS[key], all_details[key]
        ddir = V2 / key
        ddir.mkdir(parents=True, exist_ok=True)

        # A guide is a single page: no country pages, index, compare or datasets.
        if cfg.get("kind") == "guide":
            (ddir / "index.html").write_text(guide_page(key), encoding="utf-8")
            total_pages += 1
            continue

        (ddir / "countries").mkdir(parents=True, exist_ok=True)
        for c in countries:
            (ddir / "countries" / f'{c["slug"]}.html').write_text(
                country_page(key, c, details.get(c["slug"])), encoding="utf-8")
            total_pages += 1
        (ddir / "index.html").write_text(domain_home(key, countries, details), encoding="utf-8")
        (ddir / "countries.html").write_text(index_page(key, countries, details), encoding="utf-8")
        (ddir / "compare.html").write_text(compare_page(key), encoding="utf-8")
        total_pages += 3

        # map dataset: ISO2 -> [name, slug, status, continent_slug, law]
        mapdata = {}
        for c in countries:
            d = details.get(c["slug"])
            st = (d or {}).get("status", c["status"] if key == "personal" else "n")
            mapdata[c["code"]] = [c["name"], c["slug"], st, c["continent_slug"],
                                  (d or {}).get("law") or ("" if d else "Not yet researched")]
        (V2 / "assets" / f"{key}-map.js").write_text(
            "// generated — do not edit\nconst MAP_DATA = " + json.dumps(mapdata, ensure_ascii=False, sort_keys=True) + ";\n",
            encoding="utf-8")

        # compare dataset
        cmp = {}
        for c in countries:
            d = details.get(c["slug"])
            row = {"continent": c["continent"]}
            for _, dk in cfg["compare_rows"]:
                v = (d or {}).get(dk)
                if dk == "authority":
                    v = (d or {}).get("authority_acronym") or (d or {}).get("authority")
                row[dk] = v or ("—" if d else "Not yet researched")
            cmp[c["name"]] = row
        (V2 / "assets" / f"{key}-compare.js").write_text(
            "// generated — do not edit\nconst DATA = " + json.dumps(cmp, ensure_ascii=False, indent=1, sort_keys=True) + ";\n",
            encoding="utf-8")

    (V2 / "index.html").write_text(site_home(countries, all_details), encoding="utf-8")
    total_pages += 1

    print(f"generated {total_pages} pages across {len(ORDER)} areas")
    for key in ORDER:
        cfg = DOMAINS[key]
        if cfg.get("kind") == "guide":
            print(f"  {cfg['label']:<16} practice guide (no per-country data)")
        else:
            n = sum(1 for c in countries if all_details[key].get(c["slug"]))
            print(f"  {cfg['label']:<16} {n:>3}/{len(countries)} researched")


if __name__ == "__main__":
    main()
