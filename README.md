# Governance Atlas

**Every data protection law on Earth, in plain English.**

An open reference for data protection and privacy law by country — executive summaries you can take into a meeting, at-a-glance obligations, side-by-side comparisons, and links to every official source. Think *caniuse.com, but for privacy laws*.

Developed by [Ayoade Adegbite](https://ayoadeabel.tech) · [LinkedIn](https://www.linkedin.com/in/tripleaceme/)

## Current state

A static multi-page site — no build step, no dependencies. Open `index.html` in a browser and navigate normally.

```text
governance-atlas/
├── index.html               Home — rotating world dossier card (one country per
│                            continent), country search, continent cards, changelog
├── compare.html             Compare tool — pick up to 3 countries, side-by-side table
├── resources.html           Governance stack — open-source tools, templates, learning
├── about.html               Mission, data methodology, disclaimer, credits
├── assets/
│   └── styles.css           Shared design system (light + dark theme)
├── data/
│   └── countries.json       Canonical data — one record per country (194 total)
├── scripts/
│   └── generate.py          Renders data/countries.json → countries/*.html stubs
├── continents/              One page per continent: stats, tile map, regional
│   ├── africa.html            frameworks (Malabo, ECOWAS, GDPR, APEC…),
│   └── …                      searchable country index (6 pages)
├── countries/               One page per country — ALL 194 countries:
│   ├── nigeria.html           · 3 verified hand-written dossiers
│   ├── kenya.html               (Nigeria, Kenya, South Africa)
│   ├── south-africa.html      · 191 generated stubs marked
│   └── … (191 more)             "Awaiting verification"
└── README.md
```

## How country pages work

- `data/countries.json` is the canonical dataset. Country page filenames derive
  from the country name via a shared slugify rule implemented identically in
  `scripts/generate.py` (Python) and on the map/search pages (JS) — so links
  never need a registry.
- Regenerate stubs after editing the data: `python3 scripts/generate.py`
  (zero dependencies, idempotent, skips the hand-written pages).
- To promote a stub to a full dossier: replace the generated file with a
  hand-written page modeled on `nigeria.html` and add its slug to `RICH`
  in `scripts/generate.py`.

> ⚠️ All legal statuses, dates, and figures in the mockup are **illustrative placeholders**. Every fact must be verified against official sources before launch.

## Planned architecture

- **Data as code**: one YAML file per country (`data/countries/nigeria.yaml`) holding structured facts (law, authority, DPO requirement, fines, sources, `last_verified`, …) plus the executive summary. The YAML is the database; contributors submit PRs to correct it.
- **Static site generation**: a build step renders each YAML file into a country page using one template. Comparison tables, continent stats, and a JSON API (`/api/countries/nigeria.json`) are all generated from the same data.
- **Hosting**: GitHub Pages.

## Roadmap

- [x] Mockup of the three screens
- [x] Split into real pages (home / continent / country)
- [x] Canonical dataset (`data/countries.json`) + generator (`scripts/generate.py`)
- [x] Pages for all 194 countries (3 verified dossiers + 191 stubs)
- [ ] Verify country data against official sources (Nigeria, Kenya, South Africa first)
- [ ] Promote stubs to full dossiers, continent by continent (Africa first)
- [ ] Africa launch (~15–20 countries)
- [ ] Search & filters ("DPO required", adequacy status)
- [ ] More continents, JSON API, resources/tools directory
