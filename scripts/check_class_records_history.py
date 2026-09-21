#!/usr/bin/env python3
"""Guard: data/class_records_history.json has no duplicate entries.

WHY THIS EXISTS
---------------
`class_records_history.json` is a flat append-only list that drives the "records
broken" section of every annual summary page. The 2026-09-20 procedure proof
established that nothing in this repository appends to it: the 2026-27 entry was
added by a one-off snippet that was never committed, and the file the docs call
a template (`scripts/add_2025_26_class_records.py`) both deletes correct rows and
invents self-referential ones. So the append path is whatever the next person
types, and nothing stops them typing it twice.

A double-append is invisible in review -- the file is 199 near-identical objects
and a duplicated one reads as just another record -- but it renders as the same
record broken twice on the annual page.

This checker never edits the file. If it finds duplicates it names them and
exits non-zero; removing them is a decision about published content and belongs
to the site's owner.

WHAT IT CHECKS
--------------
  DUPLICATE       the same (season, gender, event, grade, time) appears twice
  REGRADE         the same (season, gender, event, grade) appears twice at
                  different times -- one season cannot set one class record
                  twice in the history; the slower one is stale
  MISSING_FIELD   an entry is missing one of the required keys
  BAD_SEASON      season is not YYYY-YY
  SELF_PREVIOUS   `previous` names the same swimmer at the same time as the
                  record it replaced (the signature of the broken template)

Usage:  python3 scripts/check_class_records_history.py [--quiet] [--json]
Exit 0 = clean, 1 = problems found.
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
HISTORY_FILE = PROJECT_ROOT / 'data' / 'class_records_history.json'

REQUIRED = ('season', 'gender', 'event', 'grade', 'time', 'name', 'date', 'meet')
IDENTITY = ('season', 'gender', 'event', 'grade', 'time')
SLOT = ('season', 'gender', 'event', 'grade')


def describe(key, fields):
    return ' / '.join(f'{f}={key[i]!r}' for i, f in enumerate(fields))


def check(path):
    entries = json.loads(Path(path).read_text())
    problems = []

    if not isinstance(entries, list):
        return [('STRUCTURE', f'{path} is a {type(entries).__name__}, expected a list')], 0

    by_identity = collections.defaultdict(list)
    by_slot = collections.defaultdict(list)

    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            problems.append(('STRUCTURE', f'entry {i} is a {type(e).__name__}, expected an object'))
            continue
        missing = [f for f in REQUIRED if f not in e]
        if missing:
            problems.append(('MISSING_FIELD',
                             f'entry {i} is missing {", ".join(missing)}: {e}'))
        if 'season' in e and not re.fullmatch(r'\d{4}-\d{2}', str(e['season'])):
            problems.append(('BAD_SEASON', f'entry {i}: season {e["season"]!r} is not YYYY-YY'))
        prev = e.get('previous') or {}
        if isinstance(prev, dict) and prev.get('name') and prev.get('name') == e.get('name') \
                and prev.get('time') == e.get('time'):
            problems.append(('SELF_PREVIOUS',
                             f'entry {i}: {e.get("season")} {e.get("gender")} {e.get("grade")} '
                             f'{e.get("event")} lists itself as the previous record '
                             f'({e.get("name")} {e.get("time")})'))
        by_identity[tuple(e.get(f) for f in IDENTITY)].append(i)
        by_slot[tuple(e.get(f) for f in SLOT)].append(i)

    for key, idxs in sorted(by_identity.items(), key=lambda kv: str(kv[0])):
        if len(idxs) > 1:
            problems.append(('DUPLICATE',
                             f'{len(idxs)} identical entries at indexes {idxs}: '
                             f'{describe(key, IDENTITY)}'))

    for key, idxs in sorted(by_slot.items(), key=lambda kv: str(kv[0])):
        if len(idxs) > 1:
            times = [entries[i].get('time') for i in idxs]
            if len(set(times)) > 1:
                problems.append(('REGRADE',
                                 f'the same class record slot appears {len(idxs)} times at '
                                 f'indexes {idxs} with different times {times}: '
                                 f'{describe(key, SLOT)}'))

    return problems, len(entries)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--file', default=str(HISTORY_FILE))
    ap.add_argument('--quiet', action='store_true', help='one-line summary only')
    ap.add_argument('--json', action='store_true', help='machine-readable output')
    args = ap.parse_args()

    problems, count = check(args.file)
    by_code = collections.Counter(code for code, _ in problems)

    if args.json:
        print(json.dumps({'file': args.file, 'entries': count,
                          'problems': [{'code': c, 'detail': d} for c, d in problems]},
                         indent=2))
    elif args.quiet:
        print(f'check_class_records_history: {count} entries, '
              f'{len(problems)} problem(s)'
              + (' [' + ' '.join(f'{c}={n}' for c, n in sorted(by_code.items())) + ']'
                 if problems else ''))
    else:
        print('=' * 78)
        print('CLASS RECORDS HISTORY GUARD')
        print(f'  file    : {args.file}')
        print(f'  entries : {count}')
        print('=' * 78)
        if not problems:
            print(f'  no duplicate (season, gender, event, grade, time) tuples')
            print(f'  no repeated class-record slots, no self-referential previous entries')
        else:
            for code in sorted(by_code):
                print(f'\n{code}  ({by_code[code]})')
                for c, detail in problems:
                    if c == code:
                        print(f'  {detail}')
            print('\n' + '-' * 78)
            print('  These are NOT removed automatically. Deleting a published record')
            print("  entry is a decision about the site's content, not a lint fix.")
        print('=' * 78)

    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
