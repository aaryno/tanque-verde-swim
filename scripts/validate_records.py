#!/usr/bin/env python3
"""Structural linter for the hand-maintained markdown in records/.

records/*.md is the source of truth and is edited by hand, so the failure mode
is a malformed table rather than a bad computation. This checks only structure
and internal consistency -- it never judges whether a time is correct, and it
never rewrites a file.

Checks:
  * rank tables (top10-*.md, relay-records-*.md): ranks are contiguous 1..N
  * rank tables: (time, date, participants) is unique within a table
  * rank tables: times are non-decreasing down the ranks
  * grade tables (records-*.md): grade labels are known and not repeated
  * grade tables: the Open row matches the fastest grade row in that event
  * every table: time and date parse
             ('22.43r' = relay leadoff; 'Nov 2007' and '2013-14' are accepted
              coarse dates; an all-em-dash row is a deliberate no-data marker)

Usage:  python3 scripts/validate_records.py [--quiet]
Exit 0 = clean, 1 = problems found.
"""

import json
import re
import sys
from pathlib import Path

RECORDS_DIR = Path(__file__).parent.parent / 'records'
ALIASES_PATH = Path(__file__).parent.parent / 'data' / 'swimmer_aliases.json'


def load_aliases():
    """Explicit, hand-adjudicated name map. Deliberately NOT fuzzy matching.

    Near-duplicate names are frequently different people -- the Radomsky and
    Alitiem sisters, the Radomsky and Caballero brothers, the Lightcap
    siblings all score as near-identical and are distinct swimmers. Any
    similarity heuristic merges real athletes into one. So identity comes only
    from this table, which a human maintains one entry at a time.
    """
    try:
        return json.loads(ALIASES_PATH.read_text())
    except Exception:
        return {}


ALIASES = load_aliases()


def canonical(name):
    return ALIASES.get(name.strip(), name.strip())
GRADES = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Open']
MONTHS = {m: i + 1 for i, m in enumerate(
    'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}

problems = []


def problem(path, event, msg):
    problems.append(f"{path.name}: [{event}] {msg}")


def parse_time(raw):
    """'1:41.80' / '01:41.80' / '59.61' / '22.43r' -> seconds, or None.

    A trailing 'r' marks a relay-leadoff time, which counts as an individual
    swim and appears in the all-time lists.
    """
    m = re.fullmatch(r'(?:(\d{1,2}):)?(\d{1,2}(?:\.\d{1,2})?)r?', raw.strip())
    if not m:
        return None
    return int(m.group(1) or 0) * 60 + float(m.group(2))


def parse_date(raw):
    """'Nov 08, 2025' or the day-less 'Nov 2007' used for older meets."""
    raw = raw.strip()
    m = re.fullmatch(r'([A-Z][a-z]{2}) (\d{1,2}), (\d{4})', raw)
    if m and m.group(1) in MONTHS:
        return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
    m = re.fullmatch(r'([A-Z][a-z]{2}) (\d{4})', raw)
    if m and m.group(1) in MONTHS:
        return (int(m.group(2)), MONTHS[m.group(1)], 0)
    m = re.fullmatch(r'(\d{4})-\d{2}', raw)
    if m:
        return (int(m.group(1)), 0, 0)   # season-only, seen on relay leadoffs
    return None


def cells(line):
    return [c.strip().strip('*').strip() for c in line.strip().strip('|').split('|')]


def is_rule(row):
    return all(set(c) <= set('-: ') for c in row if c)


def read_tables(path, heading):
    """Yield (event, header cells, [row cells]) for each table under `heading`.

    Column layout differs between files -- top10-*.md carries a Year column that
    relay-records-*.md does not -- so callers index by header name, never by
    position.
    """
    event, header, rows = None, None, []
    for line in path.read_text().splitlines():
        m = re.match(heading + r' (.+)$', line.strip())
        if m:
            if event:
                yield event, header, rows
            event, header, rows = m.group(1), None, []
            continue
        if event and line.strip().startswith('|'):
            row = cells(line)
            if is_rule(row):
                continue
            if row[0] in ('Rank', 'Grade'):
                header = row
                continue
            if all(c in ('\u2014', '-', '') for c in row[1:]):
                continue  # deliberate "no swim recorded this season" placeholder
            rows.append(row)
    if event:
        yield event, header, rows


def column(header, row, name):
    """Value of column `name` in `row`, or None if this table has no such column."""
    if not header or name not in header:
        return None
    i = header.index(name)
    return row[i] if i < len(row) else None


def check_rank_table(path, event, header, rows, one_per_athlete=False):
    if not rows or not header:
        return
    ranks, seen, prev_t = [], {}, None
    by_athlete = {}
    for row in rows:
        if len(row) != len(header):
            problem(path, event,
                    f"row has {len(row)} columns, header has {len(header)}: {row}")
            continue
        rank = column(header, row, 'Rank')
        time_s = column(header, row, 'Time')
        who = column(header, row, 'Athlete') or column(header, row, 'Participants')
        date_s = column(header, row, 'Date')
        if not rank.isdigit():
            problem(path, event, f"rank {rank!r} is not a number")
            continue
        ranks.append(int(rank))
        t = parse_time(time_s)
        if t is None:
            problem(path, event, f"rank {rank}: unparseable time {time_s!r}")
        elif prev_t is not None and t < prev_t:
            problem(path, event, f"rank {rank}: time {time_s} is faster than the rank above it")
        if t is not None:
            prev_t = t
        if parse_date(date_s) is None:
            problem(path, event, f"rank {rank}: unparseable date {date_s!r}")
        if one_per_athlete and who:
            # A top-10 list holds each swimmer once, at their best time. Two
            # rows for one athlete means the same person is split across two
            # spellings -- which both wastes a slot and hides whoever should
            # hold it. Compare canonical names so a known alias is caught.
            c = canonical(who)
            if c in by_athlete:
                prev_rank, prev_who = by_athlete[c]
                if prev_who.strip() == who.strip():
                    # Identical spelling twice: a duplicated row, not an alias.
                    remedy = ("duplicated row -- one must be removed and the "
                              "list re-ranked")
                    detail = f"{who!r}"
                else:
                    remedy = ("two spellings of one swimmer -- already mapped "
                              "in data/swimmer_aliases.json, so the source "
                              "markdown still needs the rows merged")
                    detail = f"{prev_who!r} / {who!r} -> {c!r}"
                problem(path, event,
                        f"ranks {prev_rank} and {rank} are the same athlete "
                        f"({detail}): {remedy}")
            else:
                by_athlete[c] = (rank, who)

        key = (time_s, date_s, who)
        if key in seen:
            problem(path, event,
                    f"duplicate entry at ranks {seen[key]} and {rank}: {time_s} / {date_s} / {who}")
        else:
            seen[key] = rank
    if ranks and ranks != list(range(1, len(ranks) + 1)):
        problem(path, event, f"ranks are not contiguous 1..{len(ranks)}: {ranks}")


def check_grade_table(path, event, header, rows):
    if not rows or not header:
        return
    seen, by_grade = set(), {}
    for row in rows:
        if len(row) != len(header):
            problem(path, event,
                    f"row has {len(row)} columns, header has {len(header)}: {row}")
            continue
        grade = column(header, row, 'Grade')
        time_s = column(header, row, 'Time')
        who = column(header, row, 'Athlete')
        date_s = column(header, row, 'Date')
        if grade not in GRADES:
            problem(path, event, f"unknown grade {grade!r}")
            continue
        if grade in seen:
            problem(path, event, f"grade {grade} appears more than once")
        seen.add(grade)
        t = parse_time(time_s)
        if t is None:
            problem(path, event, f"{grade}: unparseable time {time_s!r}")
        if parse_date(date_s) is None:
            problem(path, event, f"{grade}: unparseable date {date_s!r}")
        if t is not None:
            by_grade[grade] = (t, time_s, who)
    if 'Open' in by_grade:
        others = {g: v for g, v in by_grade.items() if g != 'Open'}
        if others:
            fastest = min(others.values())
            if abs(by_grade['Open'][0] - fastest[0]) > 1e-9:
                problem(path, event,
                        f"Open is {by_grade['Open'][1]} ({by_grade['Open'][2]}) but the fastest "
                        f"grade row is {fastest[1]} ({fastest[2]})")


def main():
    quiet = '--quiet' in sys.argv
    checked = 0
    for path in sorted(RECORDS_DIR.glob('top10-*.md')) + \
            sorted(RECORDS_DIR.glob('relay-records-*.md')):
        for event, header, rows in read_tables(path, r'^#{2,3}'):
            if rows:
                check_rank_table(path, event, header, rows,
                                 one_per_athlete=path.name.startswith('top10-'))
                checked += 1
    for path in sorted(RECORDS_DIR.glob('records-*.md')):
        for event, header, rows in read_tables(path, r'^#{2,3}'):
            if rows:
                check_grade_table(path, event, header, rows)
                checked += 1
    if problems:
        print(f"validate_records: {len(problems)} problem(s) across {checked} tables\n")
        for p in problems:
            print(f"  {p}")
        return 1
    if not quiet:
        print(f"validate_records: {checked} tables OK")
    return 0


if __name__ == '__main__':
    sys.exit(main())
