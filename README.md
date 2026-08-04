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
├── continents/              One page per continent: stats, tile map, regional
│   ├── africa.html            frameworks (Malabo, ECOWAS, SADC, EAC…),
│   ├── europe.html            searchable country index
│   ├── asia.html
│   ├── north-america.html
│   ├── south-america.html
│   └── oceania.html
├── countries/               One page per country: at-a-glance dossier, executive
│   ├── nigeria.html           summary, key obligations, official sources,
│   ├── kenya.html             comparison table
│   └── south-africa.html
└── README.md
```

Adding a country = adding one file to `countries/` (using `nigeria.html` as the template) and registering it in the `PAGES` map on the home page and its continent page.

> ⚠️ All legal statuses, dates, and figures in the mockup are **illustrative placeholders**. Every fact must be verified against official sources before launch.

## Planned architecture

- **Data as code**: one YAML file per country (`data/countries/nigeria.yaml`) holding structured facts (law, authority, DPO requirement, fines, sources, `last_verified`, …) plus the executive summary. The YAML is the database; contributors submit PRs to correct it.
- **Static site generation**: a build step renders each YAML file into a country page using one template. Comparison tables, continent stats, and a JSON API (`/api/countries/nigeria.json`) are all generated from the same data.
- **Hosting**: GitHub Pages.

## Roadmap

- [x] Mockup of the three screens
- [x] Split into real pages (home / continent / country)
- [ ] Define the country YAML schema
- [ ] First three verified country files: Nigeria, Kenya, South Africa
- [ ] Static site generator (YAML → pages) so country pages are generated, not hand-written
- [ ] Africa launch (~15–20 countries)
- [ ] Search & filters ("DPO required", adequacy status)
- [ ] More continents, JSON API, resources/tools directory
