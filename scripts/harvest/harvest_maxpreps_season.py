#!/usr/bin/env python3
"""
Harvest ATTRIBUTED individual results for one season from MaxPreps.

Companion to harvest_all_relay_splits.py, which reads the same /stats/ page but
takes only the relay split windows -- those carry no date and no meet name.
This script reads the "Best Times by Event" tables on that page instead, and
every row there carries Name / Date / Meet / Round / Time.

That attribution is the whole point. records/*.md tables have a Date column and
a Meet column, so a time with no date and no meet name cannot be written into
them. Division leaderboards (azpreps365) are season-to-date standings and do not
carry either, which is why they are useful for cross-checking a time but not for
sourcing a record.

Two further reasons this reads MaxPreps rather than a leaderboard:

  * Best Times by Event lists flat-start swims in the individual events. A
    division leaderboard mixes in relay lead-off splits under the same event
    name, and whether a lead-off counts as an individual record is an open
    question in this repo (data/leadoff_exclusions.json exists but no active
    script reads it). Sourcing from here sidesteps that question entirely.
  * The page is server-rendered, so stdlib urlopen is enough -- no playwright.

URLs match harvest_all_relay_splits.py:
  boys:  https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/{season}/stats/
  girls: https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/girls/fall/{season}/stats/

Usage:
    python3 scripts/harvest/harvest_maxpreps_season.py --season 26-27
    python3 scripts/harvest/harvest_maxpreps_season.py --season 26-27 --out /tmp/x.json

Writes JSON to stdout (or --out). It never writes into records/ or data/ --
turning these rows into record tables is a reviewed, human step.
"""

import argparse
import html as htmllib
import json
import re
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# "RELAY" in the event name is what the record generators use to split
# individual from relay swims (generate_hs_records.py:194). Same rule here, so
# relay rows land in a separate bucket instead of being silently mixed in.
RELAY_RE = re.compile(r'relay', re.I)

# MaxPreps event label -> the "### <name>" heading used in records/*.md.
# Anything not in this map is still harvested, under its MaxPreps label, and
# flagged unmapped -- better a visible unknown than a silent drop.
EVENT_MAP = {
    '50 Free': '50 Freestyle',
    '100 Free': '100 Freestyle',
    '200 Free': '200 Freestyle',
    '500 Free': '500 Freestyle',
    '100 Back': '100 Backstroke',
    '100 Breast': '100 Breaststroke',
    '100 Fly': '100 Butterfly',
    '200 Individual Medley': '200 Individual Medley',
}


def get_url(gender, season):
    base = "https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming"
    if gender == 'boys':
        return f"{base}/fall/{season}/stats/"
    return f"{base}/girls/fall/{season}/stats/"


def roster_url(gender, season):
    base = "https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming"
    if gender == 'boys':
        return f"{base}/fall/{season}/roster/"
    return f"{base}/girls/fall/{season}/roster/"


def fetch(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8', errors='replace')
    except (HTTPError, URLError) as e:
        print(f"  fetch failed {url}: {e}", file=sys.stderr)
        return None


def strip_tags(s):
    return htmllib.unescape(re.sub(r'(?s)<[^>]+>', '', s)).strip()


def parse_grades(html):
    """Athlete -> grade ('Fr.'/'So.'/'Jr.'/'Sr.') from the roster page.

    The Best Times tables carry no grade, but a class record is by definition
    per-grade, so the grade has to come from somewhere. The roster is the
    team's own statement of it for this season.
    """
    grades = {}
    for row in re.findall(r'(?s)<tr[^>]*>(.*?)</tr>', html):
        tds = re.findall(r'(?s)<td[^>]*>(.*?)</td>', row)
        if len(tds) < 2:
            continue
        # Locate both fields by content, not by column index: the roster table
        # leads with an empty jersey-number cell for swimming but not for every
        # sport, so positions shift.
        name = ''
        for td in tds:
            a = re.search(r'(?s)<a[^>]*\bclass="[^"]*\bname\b[^"]*"[^>]*>(.*?)</a>', td)
            if a:
                name = strip_tags(a.group(1))
                break
        grade = next((strip_tags(td) for td in tds
                      if re.fullmatch(r'(Fr|So|Jr|Sr)\.', strip_tags(td))), '')
        if name and grade:
            grades[name] = grade
    return grades


def parse_best_times(html, gender, season, fetched_at):
    """Rows of the 'Best Times by Event' tables, one dict per swim."""
    start = html.find('Best Times by Event')
    if start == -1:
        return []
    body = html[start:]

    rows = []
    # Each event is an <h4>label</h4> followed by one <table>.
    for m in re.finditer(r'(?s)<h4>(.*?)</h4>.*?<table[^>]*>(.*?)</table>', body):
        event_raw = strip_tags(m.group(1))
        table = m.group(2)
        for tr in re.findall(r'(?s)<tr[^>]*>(.*?)</tr>', table):
            def cell(cls):
                c = re.search(r'(?s)<td class="[^"]*\b%s\b[^"]*">(.*?)</td>' % cls, tr)
                return strip_tags(c.group(1)) if c else ''

            name = cell('name')
            t = cell('time')
            if not name or not t:
                continue
            rows.append({
                'event_source': event_raw,
                'event': EVENT_MAP.get(event_raw, event_raw),
                'event_mapped': event_raw in EVENT_MAP,
                'is_relay': bool(RELAY_RE.search(event_raw)),
                'athlete': name,
                'date': cell('date'),
                'meet': cell('opponent'),
                'round': cell('round'),
                'time': t,
                'gender': gender,
                'season': season,
                'source': 'maxpreps',
                'source_url': get_url(gender, season),
                'fetched_at': fetched_at,
            })
    return rows


# Event order used by records/top10-*.md, so a regenerated file diffs cleanly
# against the committed one.
TOP10_EVENT_ORDER = [
    '50 Freestyle', '100 Freestyle', '200 Freestyle', '500 Freestyle',
    '100 Backstroke', '100 Breaststroke', '100 Butterfly',
    '200 Individual Medley',
]

GRADE_BADGE = {'Fr.': 'FR', 'So.': 'SO', 'Jr.': 'JR', 'Sr.': 'SR'}


def display_time(t):
    """'00:22.53' -> '22.53', '05:03.13' -> '5:03.13' (records/*.md style)."""
    t = t.strip()
    m = re.fullmatch(r'(\d{1,2}):(\d{2}(?:\.\d+)?)', t)
    if not m:
        return t
    mins = int(m.group(1))
    return m.group(2) if mins == 0 else f"{mins}:{m.group(2)}"


def display_date(d):
    """'9/19/2026' -> 'Sep 19, 2026'."""
    try:
        return datetime.strptime(d.strip(), '%m/%d/%Y').strftime('%b %d, %Y')
    except ValueError:
        return d.strip()


# MaxPreps meet label -> the name records/*.md already uses for that meet.
#
# Same job as EVENT_MAP, one level up: MaxPreps calls the AIA state meet
# "Division III - State Swim & Dive", but every committed row for it -- back
# through 2007 -- reads "<year> D-3 AIA State Championship". Writing the
# MaxPreps label would put the same meet in the repo under two names, and the
# season and all-time lists would then disagree about where a swim was swum.
#
# Deliberately explicit and deliberately small: an unlisted meet passes through
# under its own (city-stripped) name rather than being guessed at. Keys are
# matched AFTER the trailing "(City, ST)" is stripped.
MEET_ALIASES = {
    'Division III - State Swim & Dive': '{year} D-3 AIA State Championship',
}


def clean_meet(m, date=''):
    """Drop the trailing '(City, ST)' that MaxPreps appends, then alias.

    records/*.md overwhelmingly stores the bare meet name -- the committed
    rows read 'Canyon del Oro Classic', not 'Canyon del Oro Classic (Oro
    Valley, AZ)'. Matching that keeps the same meet from appearing as two
    different strings across seasons.

    `date` supplies {year} for an alias that names its year, so the 2025 and
    2026 state meets stay distinguishable instead of collapsing into one label.
    """
    bare = re.sub(r'\s*\([^)]*\)\s*$', '', m.strip()).strip()
    tmpl = MEET_ALIASES.get(bare)
    if not tmpl:
        return bare
    year = ''
    try:
        year = str(datetime.strptime(date.strip(), '%m/%d/%Y').year)
    except ValueError:
        pass
    if '{year}' in tmpl and not year:
        # Without a year the alias would render a meet called "{year} D-3 ...".
        # Keeping the source label is wrong but visible; that is the better of
        # the two failures.
        print(f"  meet alias needs a year but date is {date!r}: keeping {bare!r}",
              file=sys.stderr)
        return bare
    return tmpl.format(year=year)


def season_label(season):
    """'26-27' -> '2026-27'."""
    a, b = season.split('-')
    return f"20{a}-{b}"


def render_top10(rows, gender, season, in_progress_note):
    """Season top-10 markdown for one gender, fastest first per event.

    Whole-file render from the harvested rows: re-running replaces the file
    rather than appending to it, so the file cannot accumulate duplicates.

    NO ROUND FILTER, and that is deliberate. "Best Times by Event" already
    holds exactly one row per swimmer per event -- their season best -- and the
    Round cell says which round that best happened to be swum in. Dropping the
    Preliminary rows would therefore not prefer a final over a prelim; it would
    delete the swimmer's season best outright and leave the event blank for
    them. Measured on 2025-26: 30 of 105 swims are Preliminary, and they
    include three records the repo already publishes -- Kent Olsson 100 Back
    59.71, Jackson Eftekhar 100 Fly 54.41 and Isla Cerepak 100 Free 58.02, all
    committed in records/records-*.md as class records. A finals-only list
    would contradict the records page on its first render.
    """
    label = season_label(season)
    out = [f"# {gender.title()} Top 10 - {label} Season",
           "## Tanque Verde High School Swimming",
           "",
           f"**Generated:** {datetime.now(timezone.utc).strftime('%B %d, %Y')}",
           ""]
    if in_progress_note:
        out += [f"> {in_progress_note}", ""]
    out += ["---", ""]

    by_event = {}
    for r in rows:
        by_event.setdefault(r['event'], []).append(r)

    events = ([e for e in TOP10_EVENT_ORDER if e in by_event]
              + sorted(e for e in by_event if e not in TOP10_EVENT_ORDER))
    for event in events:
        # One row per swimmer (their best), fastest first, capped at 10.
        best = {}
        for r in sorted(by_event[event], key=lambda x: x['time']):
            best.setdefault(r['athlete'], r)
        ranked = sorted(best.values(), key=lambda x: x['time'])[:10]
        out += [f"## {event}", "",
                "| Rank | Time | Athlete | Year | Date | Meet |",
                "|-----:|-----:|---------|------|------|------|"]
        for i, r in enumerate(ranked, 1):
            out.append(
                f"| {i} | {display_time(r['time'])} | {r['athlete']} | "
                f"{GRADE_BADGE.get(r['grade'], '')} | {display_date(r['date'])} | "
                f"{clean_meet(r['meet'], r['date'])} |")
        out += ["", "---", ""]
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--season', required=True,
                    help="MaxPreps season slug, e.g. 26-27")
    ap.add_argument('--out', help="write JSON here instead of stdout")
    ap.add_argument('--write-top10', metavar='RECORDS_DIR',
                    help="also render records/top10-{boys,girls}-<season>.md "
                         "into RECORDS_DIR. Writes ONLY those two files, only "
                         "for this season -- it never touches records-*.md, "
                         "relay-records-*.md or any other season.")
    ap.add_argument('--in-progress-note', default='',
                    help="blockquote note to put at the top of the rendered "
                         "top-10 files, e.g. a partial-season warning")
    args = ap.parse_args()

    fetched_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    out = {
        'season': args.season,
        'fetched_at': fetched_at,
        'individual': [],
        'relay': [],
        'unmapped_events': [],
        'missing_grade': [],
    }

    for gender in ('boys', 'girls'):
        stats = fetch(get_url(gender, args.season))
        if not stats:
            continue
        grades = parse_grades(fetch(roster_url(gender, args.season)) or '')
        for row in parse_best_times(stats, gender, args.season, fetched_at):
            if row['is_relay']:
                # No participant names on these rows -- the relay page names
                # only "Relay Team" -- so they cannot fill a Participants
                # column. Kept for the report, not for records/.
                out['relay'].append(row)
                continue
            row['grade'] = grades.get(row['athlete'], '')
            if not row['grade']:
                out['missing_grade'].append(f"{gender}/{row['athlete']}")
            if not row['event_mapped']:
                out['unmapped_events'].append(f"{gender}/{row['event_source']}")
            out['individual'].append(row)
        time.sleep(0.5)

    out['unmapped_events'] = sorted(set(out['unmapped_events']))
    out['missing_grade'] = sorted(set(out['missing_grade']))

    if args.write_top10:
        from pathlib import Path
        rd = Path(args.write_top10)
        for gender in ('boys', 'girls'):
            rows = [r for r in out['individual'] if r['gender'] == gender]
            if not rows:
                print(f"  no {gender} rows -- not writing a top-10 file",
                      file=sys.stderr)
                continue
            target = rd / f"top10-{gender}-{season_label(args.season)}.md"
            target.write_text(
                render_top10(rows, gender, args.season, args.in_progress_note))
            print(f"  wrote {target} ({len(rows)} swims)", file=sys.stderr)

    text = json.dumps(out, indent=2)
    if args.out:
        with open(args.out, 'w') as f:
            f.write(text)
        print(f"wrote {len(out['individual'])} individual, "
              f"{len(out['relay'])} relay rows to {args.out}", file=sys.stderr)
    else:
        print(text)


if __name__ == '__main__':
    main()
