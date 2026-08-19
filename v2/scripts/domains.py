"""Domain configuration for Governance Atlas v2.

Three areas of data regulation. Two of them differ enough between countries
to be worth tracking country by country; one does not.

    kind = "tracker"  a country-by-country area: map, A–Z index, compare tool,
                      and one page per country, driven by data/domains/<slug>.json
    kind = "guide"    a single explanatory page describing practice, built from
                      a content fragment in content/. No per-country claims.

Data security is a guide, not a tracker. In most countries there is no
free-standing "data security regulation" to point at — the duties are spread
across a cybersecurity act, sector rules from financial and telecoms
regulators, and the security article of the privacy law. Drawing a national
boundary around "data security" would mean inventing a distinction the source
material does not make. The practices, by contrast, are essentially the same
everywhere, so describing them once is both more honest and more useful.

Everything else about a tracker — page shape, map, compare tool, A–Z index —
is shared, so adding one means adding an entry here plus a data file in
data/domains/.
"""

DOMAINS = {
    "personal": {
        "slug": "personal",
        "kind": "tracker",
        "label": "Personal data",
        "nav_label": "Personal data",
        "title": "Personal data protection",
        "tagline": "Personal data protection, by country",
        "blurb": "Rules governing how organisations may collect, use, share, store and delete "
                 "information about identifiable people.",
        "regulator_label": "Data protection authority",
        "hero_h1": "Personal data protection regulations, country by country.",
        "hero_sub": "Clear summaries of the rules that govern <strong>personal data</strong> — how it may be "
                    "collected, used, shared and stored — with the official sources to help you verify them.",
        # (data key, panel label) — order defines the at-a-glance panel
        "fields": [
            ("law", "Regulation"),
            ("authority", "Authority"),
            ("dpo", "DPO required"),
            ("registration", "Registration"),
            ("breach", "Breach notification"),
            ("fine", "Maximum fine"),
            ("xborder", "Cross-border transfers"),
            ("children", "Children's data"),
            ("eu_adequacy", "EU adequacy"),
        ],
        "compare_rows": [
            ("Primary regulation", "law"), ("Supervisory authority", "authority"),
            ("DPO", "dpo"), ("Registration", "registration"),
            ("Breach deadline", "breach"), ("Maximum penalty", "fine"),
            ("Cross-border transfers", "xborder"), ("Children's data", "children"),
        ],
        "example": "Nigeria's NDPA 2023, supervised by the NDPC",
    },

    "security": {
        "slug": "security",
        "kind": "guide",
        "label": "Data security",
        "nav_label": "Data security",
        "title": "Data security practices",
        "tagline": "Data security practices, explained",
        "blurb": "How data is actually protected in practice: access, encryption, backups, vendors, "
                 "logging and incident response — the controls every regulator assumes you have.",
        "hero_plate": "Practices",
        "hero_h1": "Data security explained for everyone",
        "hero_sub": "A practical guide to protecting the data you hold — what the controls are, which "
                    "ones carry the most risk, who needs to be involved, and where to start.",
        # A guide is one page assembled from this fragment.
        "content": "security-practices.html",
        "card_state": "A practice guide",
        "example": "encryption, least privilege, backups, and an incident plan",
    },

    "general": {
        "slug": "general",
        "kind": "tracker",
        "label": "General data",
        "nav_label": "General data",
        "title": "General data regulation",
        "tagline": "Non-personal data regulation, by country",
        "blurb": "Rules treating data as an economic asset: residency and localisation, non-personal "
                 "and industrial data, open data, and emerging AI and data acts.",
        "regulator_label": "Ministry of ICT or digital economy",
        # Framing block appended to the front page. The field is too patchy to
        # be understood from a map alone, so the DAMA knowledge areas are used
        # to show what it covers before showing who legislates parts of it.
        "intro": "general-dama.html",
        "hero_h1": "General data regulation, country by country.",
        "hero_sub": "Where data must physically live, what may leave the country, and how non-personal "
                    "and industrial data may be shared or reused.",
        "fields": [
            ("law", "Regulation"),
            ("authority", "Authority"),
            ("localisation", "Data localisation"),
            ("non_personal", "Non-personal data rules"),
            ("cross_border", "Cross-border restrictions"),
            ("open_data", "Open data regime"),
            ("ai_rules", "AI or data act"),
            ("fine", "Maximum penalty"),
        ],
        "compare_rows": [
            ("Primary regulation", "law"), ("Authority", "authority"),
            ("Data localisation", "localisation"), ("Non-personal data", "non_personal"),
            ("Cross-border restrictions", "cross_border"), ("Maximum penalty", "fine"),
        ],
        "example": "the EU Data Act and Data Governance Act",
    },
}

ORDER = ["personal", "security", "general"]

STATUS_LABEL = {"a": "In force", "d": "In progress", "n": "No comprehensive regulation"}
STATUS_CHIP = {
    "a": '<span class="chip active">In force</span>',
    "d": '<span class="chip">In progress</span>',
    "n": '<span class="chip">No comprehensive regulation</span>',
}
