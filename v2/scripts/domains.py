"""Domain configuration for Governance Atlas v2.

Three separate bodies of regulation, each with its own regulator, its own
obligations, and therefore its own at-a-glance fields. Everything else about
a domain — page shape, map, compare tool, A–Z index — is shared, so adding a
domain means adding an entry here plus a data file in data/domains/.
"""

DOMAINS = {
    "personal": {
        "slug": "personal",
        "label": "Personal data",
        "nav_label": "Personal data",
        "title": "Personal data protection",
        "tagline": "Personal data protection, by country",
        "blurb": "Rules governing how organisations may collect, use, share, store and delete "
                 "information about identifiable people.",
        "regulator_label": "Data protection authority",
        "hero_h1": "Personal data protection regulations, country by country, in plain English.",
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
        "label": "Data security",
        "nav_label": "Data security",
        "title": "Data security",
        "tagline": "Data security regulation, by country",
        "blurb": "Rules on protecting systems and data from attack: incident reporting, critical "
                 "infrastructure duties, and minimum security standards.",
        "regulator_label": "National CERT or cyber agency",
        "hero_h1": "Data security regulation, country by country, in plain English.",
        "hero_sub": "What each country requires when systems are attacked or data is exposed — who you "
                    "must tell, how fast, and what standards apply.",
        "fields": [
            ("law", "Regulation"),
            ("authority", "Authority"),
            ("incident_deadline", "Incident reporting"),
            ("critical_infrastructure", "Critical infrastructure"),
            ("standards", "Mandated standards"),
            ("sector_rules", "Sector duties"),
            ("fine", "Maximum penalty"),
            ("breach_overlap", "Overlap with privacy law"),
        ],
        "compare_rows": [
            ("Primary regulation", "law"), ("Authority", "authority"),
            ("Incident reporting", "incident_deadline"), ("Critical infrastructure", "critical_infrastructure"),
            ("Mandated standards", "standards"), ("Maximum penalty", "fine"),
        ],
        "example": "Nigeria's Cybercrimes Act 2015 (amended 2024), with ngCERT",
    },

    "general": {
        "slug": "general",
        "label": "General data",
        "nav_label": "General data",
        "title": "General data regulation",
        "tagline": "Non-personal data regulation, by country",
        "blurb": "Rules treating data as an economic asset: residency and localisation, non-personal "
                 "and industrial data, open data, and emerging AI and data acts.",
        "regulator_label": "Ministry of ICT or digital economy",
        "hero_h1": "General data regulation, country by country, in plain English.",
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
