"""Structured data (JSON-LD) for the public landing page."""
import json
from typing import Any, Dict

from django.conf import settings

_SCRIPT_ESCAPES = {ord('<'): '\\u003C', ord('>'): '\\u003E', ord('&'): '\\u0026'}

SAME_AS = [
    "https://github.com/hernandezpalo83",
    "https://www.linkedin.com/in/javier-hernandez-martin-6473b321/",
]


def home_structured_data(home_data: Dict[str, Any]) -> str:
    """Person + WebSite graph built from the landing data, safe to print inside a <script>."""
    site = settings.SITE_URL
    info = home_data.get('info')
    brand = getattr(settings, 'PERSONAL_BRAND', {})

    person: Dict[str, Any] = {
        "@type": "Person",
        "@id": f"{site}/#person",
        "name": "Javier Hernández Martin",
        "url": f"{site}/",
        "jobTitle": "Technical Product Manager",
        "worksFor": {"@type": "Organization", "name": "Sandav Consultores SL"},
        "address": {"@type": "PostalAddress", "addressLocality": "Madrid", "addressCountry": "ES"},
        "sameAs": SAME_AS + ([info.credly_url] if info and getattr(info, "credly_url", "") else []),
    }
    if brand.get("PROFILE_PICTURE"):
        person["image"] = brand["PROFILE_PICTURE"]
    if info and info.bio:
        person["description"] = info.bio[:300]

    skills = [s.name for s in home_data.get('skills', []) if s.name]
    if skills:
        person["knowsAbout"] = skills

    schools = sorted({e.institution for e in home_data.get('education', []) if e.institution})
    if schools:
        person["alumniOf"] = [{"@type": "EducationalOrganization", "name": n} for n in schools]

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            person,
            {
                "@type": "WebSite",
                "@id": f"{site}/#website",
                "url": f"{site}/",
                "name": "HernandezPalo",
                "inLanguage": "es-ES",
                "publisher": {"@id": f"{site}/#person"},
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False).translate(_SCRIPT_ESCAPES)
