"""Portfolio helpers: turn the free-text 'categoria' of each project into consistent filter chips."""
import re
from collections import Counter, defaultdict
from typing import Iterable

from django.utils.text import slugify

from .models import Project


MAX_FILTERS = 8


def _best_label(spellings: Counter) -> str:
    """Prefer 'Django' over 'DJANGO' when both exist; an acronym written only one way (AWS) stays as is."""
    return min(spellings, key=lambda s: (s.isupper(), -spellings[s], s))


def build_portfolio(projects: Iterable[Project]) -> tuple[list[Project], list[dict]]:
    """
    Attach `tags` ([{key, label}]) to every project and return the filter list,
    sorted by number of projects, so 'DJANGO' and 'Django' become one chip.
    """
    projects = list(projects)
    spellings: dict[str, Counter] = defaultdict(Counter)
    counts: Counter = Counter()
    for project in projects:
        for tag in project.tag_list:
            key = slugify(tag) or tag.lower()
            spellings[key][tag] += 1
            counts[key] += 1

    labels = {key: _best_label(spelling) for key, spelling in spellings.items()}
    for project in projects:
        keys = dict.fromkeys(slugify(t) or t.lower() for t in project.tag_list)
        project.tags = [{'key': key, 'label': labels[key]} for key in keys]
        project.initials = ''.join(w[0] for w in re.findall(r'\w+', project.title)[:2]).upper()

    filters = [  # top categories only, so the chip row stays short
        {'key': key, 'label': labels[key], 'count': count}
        for key, count in sorted(counts.items(), key=lambda kv: (-kv[1], labels[kv[0]].lower()))[:MAX_FILTERS]
    ]
    return projects, filters
