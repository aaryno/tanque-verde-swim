#!/usr/bin/env python3
"""The season lists the site's navigation menus are built from.

Three scripts render the same two dropdowns -- "Top 10 by Year" and "Summary by
Year" -- into every page:

    generate_website.py      records/*, top10/*
    generate_annual_pages.py annual/*
    rebuild_relay_pages.py   records/{boys,girls}-relays.html

Until now each kept its own copy of the list, and they drifted: after 2026-27 was
added, `generate_website.py` and `generate_annual_pages.py` derived it from the
committed sources (PR #1) while `rebuild_relay_pages.py` still carried an
18-season literal that stopped at 2024-25. The result was a Top-10 page that
existed, returned HTTP 200 and was linked from 16 of 119 pages.

Deriving from the filesystem is the rule PR #1 established: a season is linked
exactly when the file that produces its page is committed, so the menu can never
point at a page that was not built, and a new season needs no edit here.
"""

import re
from pathlib import Path

RECORDS_DIR = Path(__file__).parent.parent / 'records'

SEASON_RE = re.compile(r'\d{4}-\d{2}')


def _season_key(season):
    return int(season.split('-')[0])


def seasons_with_top10(records_dir=None):
    """Seasons whose top-10 pages exist, oldest first.

    Both genders are required: the menu links the boys page and the gender
    toggle rewrites the same href to the girls page, so a season with only one
    committed file would render a broken link for the other gender.
    """
    records_dir = Path(records_dir) if records_dir else RECORDS_DIR
    boys = {f.name[len('top10-boys-'):-len('.md')]
            for f in records_dir.glob('top10-boys-*.md')}
    girls = {f.name[len('top10-girls-'):-len('.md')]
             for f in records_dir.glob('top10-girls-*.md')}
    return sorted((s for s in boys & girls if SEASON_RE.fullmatch(s)), key=_season_key)


def seasons_with_annual(records_dir=None):
    """Seasons whose annual summary pages exist, oldest first."""
    records_dir = Path(records_dir) if records_dir else RECORDS_DIR
    seasons = {f.name[len('annual-summary-'):-len('.md')]
               for f in records_dir.glob('annual-summary-*.md')}
    return sorted((s for s in seasons if SEASON_RE.fullmatch(s)), key=_season_key)


DATA_DIR = Path(__file__).parent.parent / 'data'


def season_complete(season):
    """True once the season's State championship results are imported.

    `season` is a data/season_<season>.json document. The championship is the
    schedule's meet named '... State Championship'; it counts as done when a
    data/meets/*.json file carries that meet name. Derived from committed files,
    not from today's date, so a rebuild is reproducible.
    """
    state = [m['name'] for m in season['schedule']['meets'] if 'State Championship' in m['name']]
    if not state:
        return False
    import json
    names = {json.loads(p.read_text())['meet'] for p in (DATA_DIR / 'meets').glob('*.json')}
    return state[-1] in names


def in_progress_seasons():
    """Seasons with a data/season_*.json whose State meet is not imported yet."""
    import json
    out = []
    for p in sorted(DATA_DIR.glob('season_*.json')):
        doc = json.loads(p.read_text())
        if not season_complete(doc):
            out.append(doc['season'])
    return out
