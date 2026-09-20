#!/usr/bin/env python3
"""Guard: is each relay record row's split breakdown attached to the right swim?

WHY THIS EXISTS
---------------
`generate_website.py` and `rebuild_relay_pages.py` both decorate a relay record
row (from records/relay-records-{boys,girls}.md) with a split breakdown taken
from data/historical_splits/all_relay_splits.json. Neither file records which
swim a splits entry belongs to beyond `type` and `year`, so both renderers match
on event type plus >= 3 overlapping swimmer names -- and then break the
resulting tie by POSITION IN THE LIST:

    generate_website.py:find_relay_splits      -> the FIRST candidate      (docs/records/overall.html)
    rebuild_relay_pages.py:find_splits_for_relay -> the first candidate at the
                                                   HIGHEST overlap         (docs/records/{boys,girls}-relays.html)

`harvest/harvest_all_relay_splits.py` writes the combined file in `YEARS` order,
which is newest-first, while the committed file is oldest-first. So a plain
re-harvest reorders the list and a different entry silently becomes "first" --
changing which year's swims are printed under a historical record. No relay time
and no rank moves, so nothing else in the build notices.

This checker makes that condition visible. It never edits a file and it never
changes what is rendered.

WHAT IT REPORTS
---------------
  ORDER_SENSITIVE  the pick changes when the candidate list is reversed, i.e.
                   re-harvesting would rewrite this row's published splits
  SUM_MISMATCH     the attached splits do not add up to the record's own time,
                   so they are demonstrably not this swim
  PAGE_DISAGREE    overall.html and the relay page attach DIFFERENT entries to
                   the same record row -- at most one of them can be right
  SEASON_MISMATCH  the attached entry's season is not the record date's season
  AMBIGUOUS        more than one candidate satisfied the match at all
  UNPARSEABLE      a candidate carries a split value that is not a time

The sum check is the load-bearing one: a relay's four legs must add to the
relay's own time, so it identifies the swim without needing a date or a meet in
the splits data.

Usage:
    python3 scripts/check_relay_split_attachment.py [--splits PATH] [--quiet]
                                                    [--only CODE[,CODE...]]

Exit 0 = no ORDER_SENSITIVE and no SUM_MISMATCH findings.
Exit 1 = at least one, i.e. the published split breakdowns are not pinned to the
         swims they describe and a re-harvest can move them.
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RECORDS_DIR = PROJECT_ROOT / 'records'
DEFAULT_SPLITS = PROJECT_ROOT / 'data' / 'historical_splits' / 'all_relay_splits.json'

# Only these three events are rendered with splits, by both renderers.
EVENTS = ['200 Medley Relay', '200 Free Relay', '400 Free Relay']
ROWS_PER_EVENT = 10          # both renderers stop at the top 10
TOLERANCE = 0.005            # times are published to 1/100s

MONTHS = {m: i + 1 for i, m in enumerate(
    'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}

CODES = ['ORDER_SENSITIVE', 'SUM_MISMATCH', 'PAGE_DISAGREE',
         'SEASON_MISMATCH', 'AMBIGUOUS', 'UNPARSEABLE']
FAILING = {'ORDER_SENSITIVE', 'SUM_MISMATCH'}


def strip_grade(name):
    """'Kent Olsson - So.' -> 'kent olsson'."""
    return re.sub(r'\s*-\s*(Fr|So|Jr|Sr)\.?$', '', name, flags=re.IGNORECASE).strip().lower()


def parse_time(raw):
    """'01:41.80' / '1:41.80' / '24.48' -> seconds, or None."""
    raw = (raw or '').strip().replace('00:', '', 1) if (raw or '').startswith('00:') else (raw or '').strip()
    if not raw:
        return None
    m = re.fullmatch(r'(?:(\d{1,3}):)?(\d{1,2}(?:\.\d{1,2})?)', raw)
    if not m:
        return None
    return int(m.group(1) or 0) * 60 + float(m.group(2))


def season_of(date_str):
    """'Oct 24, 2025' -> '25-26'. Seasons run Aug..Jul, so no single calendar
    year selects one (see the 2026-09-20 procedure proof, section 4c)."""
    m = re.fullmatch(r'([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})', (date_str or '').strip())
    if not m or m.group(1) not in MONTHS:
        return None
    month, year = MONTHS[m.group(1)], int(m.group(3))
    start = year if month >= 8 else year - 1
    return f"{start % 100:02d}-{(start + 1) % 100:02d}"


def entry_total(entry):
    """Sum of a splits entry's legs, or None if any leg is unparseable.

    400 Free Relay entries carry 8 legs (two 50s per swimmer); the sum is still
    the relay total, which is exactly what both renderers assume when they add
    adjacent pairs together for display.
    """
    total = 0.0
    for leg in entry.get('splits', []):
        secs = parse_time(leg)
        if secs is None:
            return None
        total += secs
    return total if entry.get('splits') else None


def parse_relay_records(path):
    """Yield (event, row dict) for the ranked rows of a relay records file.

    Deliberately mirrors rebuild_relay_pages.parse_relay_markdown so the checker
    sees the same rows the renderer does.
    """
    event = None
    counts = {}
    for line in path.read_text().splitlines():
        if line.startswith('## ') and 'Relay' in line:
            event = line[3:].strip()
            continue
        if not event or not line.startswith('|'):
            continue
        if line.startswith('| Rank') or line.startswith('|--'):
            continue
        parts = [p.strip().replace('**', '') for p in line.split('|')]
        if len(parts) < 6:
            continue
        try:
            rank = int(parts[1])
        except ValueError:
            continue
        counts[event] = counts.get(event, 0) + 1
        if counts[event] > ROWS_PER_EVENT:
            continue
        yield event, {'rank': rank, 'time': parts[2], 'participants': parts[3],
                      'date': parts[4], 'meet': parts[5]}


def candidates(splits_for_gender, event, participants):
    """Every splits entry the renderers would accept for this row, in list order.

    Returns [(index, overlap, entry)]. The >= 3 threshold and the event-type
    equality are both taken from the renderers unchanged -- this function must
    describe what they do, not what they should do.
    """
    wanted = {strip_grade(s) for s in participants.split(',')}
    out = []
    for i, entry in enumerate(splits_for_gender):
        if entry.get('type') != event:
            continue
        have = {strip_grade(s) for s in entry.get('swimmers', [])}
        overlap = len(wanted & have)
        if overlap >= 3:
            out.append((i, overlap, entry))
    return out


def pick_first(cands):
    """generate_website.py:find_relay_splits -- first candidate wins."""
    return cands[0] if cands else None


def pick_best(cands):
    """rebuild_relay_pages.py:find_splits_for_relay -- strictly-greater overlap
    wins, so among equals the first still wins."""
    best = None
    for c in cands:
        if best is None or c[1] > best[1]:
            best = c
    return best


def check(splits_path, only=None):
    """Return (findings, rows_examined, rows_with_splits)."""
    data = json.loads(Path(splits_path).read_text())
    findings = []
    rows = matched = 0

    def add(code, gender, event, row, detail):
        if only and code not in only:
            return
        findings.append({'code': code, 'gender': gender, 'event': event,
                         'rank': row['rank'], 'date': row['date'],
                         'time': row['time'], 'detail': detail})

    for gender in ('boys', 'girls'):
        pool = data.get(gender, [])
        md = RECORDS_DIR / f'relay-records-{gender}.md'
        if not md.exists():
            continue
        for event, row in parse_relay_records(md):
            if event not in EVENTS:
                continue
            rows += 1
            cands = candidates(pool, event, row['participants'])
            if not cands:
                continue          # renders with blank splits; honest, not a defect
            matched += 1

            first = pick_first(cands)
            best = pick_best(cands)
            rev = list(reversed(cands))
            first_rev, best_rev = pick_first(rev), pick_best(rev)

            if len(cands) > 1:
                add('AMBIGUOUS', gender, event, row,
                    f"{len(cands)} candidates matched (seasons "
                    f"{', '.join(c[2].get('year', '?') for c in cands)})")

            if first[0] != first_rev[0] or best[0] != best_rev[0]:
                add('ORDER_SENSITIVE', gender, event, row,
                    f"reversing the candidate list moves overall.html "
                    f"{first[2].get('year')}->{first_rev[2].get('year')} and the relay page "
                    f"{best[2].get('year')}->{best_rev[2].get('year')}")

            if first[0] != best[0]:
                add('PAGE_DISAGREE', gender, event, row,
                    f"overall.html attaches the {first[2].get('year')} entry, "
                    f"{gender}-relays.html attaches the {best[2].get('year')} entry")

            record_secs = parse_time(row['time'])
            for label, chosen in (('overall.html', first), (f'{gender}-relays.html', best)):
                total = entry_total(chosen[2])
                if total is None:
                    add('UNPARSEABLE', gender, event, row,
                        f"{label}: attached {chosen[2].get('year')} entry has a split "
                        f"that is not a time: {chosen[2].get('splits')}")
                elif record_secs is not None and abs(total - record_secs) > TOLERANCE:
                    add('SUM_MISMATCH', gender, event, row,
                        f"{label}: attached {chosen[2].get('year')} splits sum to "
                        f"{total:.2f}s but the record is {row['time']} ({record_secs:.2f}s)")

            want_season = season_of(row['date'])
            if want_season:
                for label, chosen in (('overall.html', first), (f'{gender}-relays.html', best)):
                    if chosen[2].get('year') != want_season:
                        add('SEASON_MISMATCH', gender, event, row,
                            f"{label}: attached a {chosen[2].get('year')} swim to a "
                            f"{want_season} record")
    return findings, rows, matched


def format_report(findings, rows, matched, splits_path):
    """A clearly-marked block, safe to drop into a build log."""
    lines = []
    lines.append('=' * 78)
    lines.append('RELAY SPLIT ATTACHMENT GUARD')
    lines.append(f'  splits file : {splits_path}')
    lines.append(f'  record rows : {rows} examined, {matched} matched a splits entry')
    lines.append('=' * 78)
    by_code = {}
    for f in findings:
        by_code.setdefault(f['code'], []).append(f)
    if not findings:
        lines.append('  no findings')
        return '\n'.join(lines)
    for code in CODES:
        group = by_code.get(code)
        if not group:
            continue
        lines.append(f'\n{code}  ({len(group)})')
        for f in group:
            lines.append(f"  {f['gender']:<5} {f['event']:<17} #{f['rank']:<2} "
                         f"{f['time']:>8}  {f['date']:<13} {f['detail']}")
    lines.append('')
    lines.append('-' * 78)
    lines.append('  ' + '  '.join(f'{c}={len(by_code.get(c, []))}' for c in CODES))
    lines.append('=' * 78)
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--splits', default=str(DEFAULT_SPLITS),
                    help='path to a combined relay splits JSON (default: the committed one)')
    ap.add_argument('--only', default=None,
                    help='comma-separated subset of ' + ','.join(CODES))
    ap.add_argument('--quiet', action='store_true',
                    help='print only the one-line summary')
    args = ap.parse_args()

    only = set(args.only.split(',')) if args.only else None
    if only and not only <= set(CODES):
        ap.error(f"unknown code(s): {', '.join(sorted(only - set(CODES)))}")

    findings, rows, matched = check(args.splits, only)
    failing = [f for f in findings if f['code'] in FAILING]

    if args.quiet:
        counts = {c: sum(1 for f in findings if f['code'] == c) for c in CODES}
        print('check_relay_split_attachment: ' +
              ' '.join(f'{c}={counts[c]}' for c in CODES))
    else:
        print(format_report(findings, rows, matched, args.splits))

    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main())
