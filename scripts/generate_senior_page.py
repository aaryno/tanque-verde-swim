#!/usr/bin/env python3
"""
The current senior class page: docs/seniors/class-of-<year>.html.

    python3 scripts/generate_senior_page.py

The class year and the seniors come from the newest data/season_*.json, so the
page -- and the nav's 🎓 link, via senior_class_year() -- move on to the next
class when the next season file is added. Nothing here is hand-edited.

Built only from what is correct today:
  * class records each senior currently holds (records/records-*.md), and
  * their swims so far this season (records/top10-*-<season>.md), each marked
    with its all-time and all-time-senior rank where it has one.

It deliberately has no career "first swim -> best swim" section like the Class
of 2026 page. Career history comes from the season Top 10 lists, and 2025-26
has none yet -- so a career section would show stale bests for last year's
juniors. Better absent than wrong about real people. Add it once 2025-26 is
restored.
"""

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from class_top10 import _tables, class_lists, EVENTS, GRADES  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RECORDS = REPO / "records"


def current_season():
    path = sorted((REPO / "data").glob("season_*.json"))[-1]
    return json.loads(path.read_text())


def senior_class_year():
    """2026-27 -> 2027. Used by the nav so 🎓 always points at this year's class."""
    return int("20" + current_season()["season"].split("-")[1])


def records_held(name, gender):
    held = []
    for event, header, rows in _tables(RECORDS / f"records-{gender}.md"):
        if "Grade" not in header:
            continue
        for r in rows:
            if r[header.index("Athlete")] == name:
                held.append((event, r[header.index("Grade")], r[header.index("Time")]))
    return held


def season_swims(name, gender, season):
    swims = []
    path = RECORDS / f"top10-{gender}-{season}.md"
    if not path.exists():
        return swims
    for event, header, rows in _tables(path):
        for r in rows:
            if r[header.index("Athlete")] == name:
                swims.append({"event": event, "time": r[header.index("Time")],
                              "date": r[header.index("Date")], "meet": r[header.index("Meet")]})
    order = {e: i for i, e in enumerate(EVENTS)}
    return sorted(swims, key=lambda s: order.get(s["event"], 99))


def rank_in(rows, name, time):
    for i, r in enumerate(rows, 1):
        if r["athlete"] == name and r["time"] == time:
            return i
    return None


def alltime_rows(gender):
    out = {}
    for event, header, rows in _tables(RECORDS / f"top10-{gender}-alltime.md"):
        out[event] = [{"athlete": r[header.index("Athlete")], "time": r[header.index("Time")]}
                      for r in rows]
    return out


def card(name, gender, season, alltime, seniors_top10):
    e = html.escape
    held = records_held(name, gender)
    swims = season_swims(name, gender, season)
    parts = [f'<div class="col-12 col-md-6 col-lg-4"><div class="card h-100 senior-card"><div class="card-body">',
             f'<h5 class="card-title mb-1">{e(name)}</h5>',
             f'<p class="mb-2"><small class="text-muted">{gender.title()} &middot; Class of {senior_class_year()}</small></p>']
    if held:
        parts.append('<div class="mb-2">' + " ".join(
            f'<span class="badge bg-warning text-dark me-1 mb-1">🏆 {e(g)} {e(ev)} {e(t)}</span>'
            for ev, g, t in held) + '</div>')
    if swims:
        parts.append('<ul class="list-unstyled mb-0 small">')
        for s in swims:
            badges = []
            r = rank_in(alltime.get(s["event"], []), name, s["time"])
            if r:
                badges.append(f'<span class="badge bg-success ms-1">#{r} all-time</span>')
            r = rank_in(seniors_top10.get(s["event"], []), name, s["time"])
            if r:
                badges.append(f'<span class="badge bg-secondary ms-1">#{r} senior</span>')
            parts.append(f'<li class="mb-1">{e(s["event"])}: <strong>{e(s["time"])}</strong>{"".join(badges)}'
                         f'<br><small class="text-muted">{e(s["meet"])} &middot; {e(s["date"])}</small></li>')
        parts.append('</ul>')
    else:
        parts.append('<p class="small text-muted mb-0">No individual swims posted yet this season.</p>')
    parts.append('</div></div></div>')
    return "\n".join(parts)


def build():
    from generate_website import create_html_page
    data = current_season()
    season, year = data["season"], senior_class_year()
    roster = data["roster"]
    meets = data.get("results_so_far", {}).get("meets_with_results", 0)
    sections = []
    for gender, key in (("boys", "seniors_boys"), ("girls", "seniors_girls")):
        names = roster.get(key, [])
        if not names:
            continue
        alltime = alltime_rows(gender)
        seniors_top10 = class_lists(gender)["SR"]
        sections.append(f'<h3 class="mt-4 mb-3">{gender.title()}</h3><div class="row g-3">' +
                        "\n".join(card(n, gender, season, alltime, seniors_top10) for n in names) +
                        '</div>')
    total = len(roster.get("seniors_boys", [])) + len(roster.get("seniors_girls", []))
    intro = (f'<div class="alert alert-light border">{total} seniors. Swims so far this season '
             f'&mdash; {meets} meet{"s" if meets != 1 else ""} with posted results, so this is a running '
             f'snapshot, not a final season. 🏆 marks a class record the swimmer currently holds.</div>')
    content = (f'<div class="container py-4"><h2 class="mb-3">🎓 Senior Class of {year}</h2>'
               f'{intro}{"".join(sections)}'
               f'<p class="mt-4 small"><a href="/seniors/class-of-{year - 1}.html">Class of {year - 1} &rarr;</a></p></div>')
    out = REPO / "docs" / "seniors" / f"class-of-{year}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(create_html_page(f"Senior Class of {year}", content))
    print(f"✅ wrote {out.relative_to(REPO)} ({total} seniors)")


if __name__ == "__main__":
    build()


def senior_href():
    """Nav target for 🎓 -- always the current senior class."""
    return f"/seniors/class-of-{senior_class_year()}.html"
