#!/usr/bin/env python3
"""
Add a meet's relay leg splits, read from its Hy-Tek .cl2 files, to the relay splits file.

    python3 scripts/harvest/relay_splits_cl2.py <file.cl2> [...] [--team TVHS]

Each relay is an E0 row followed by its F0 (swimmer) and G0 (split) rows.
The G0 rows hold cumulative times; column 144 marks prelim (P) or final (F).
For every relay swim, the leg times come from the 50-yard cumulative times
(a 200 relay gives 4 legs, a 400 relay gives 8 50s), the same shape as
data/historical_splits/all_relay_splits.json.

A swim is added only when its legs add up to its official time to the
hundredth. Anything else is reported and skipped: a missing split is a gap,
a wrong one is a false statement. Running it twice adds nothing new.

Added 2026-11-08 for Aaryn's "Need times in relay record entries": the meet
imports had been writing relay times and swimmers but not their legs, so the
2026-27 relay records showed no leg times.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLITS = ROOT / 'data' / 'historical_splits' / 'all_relay_splits.json'
GRADE = {'09': 'Fr.', '10': 'So.', '11': 'Jr.', '12': 'Sr.', 'FR': 'Fr.', 'SO': 'So.', 'JR': 'Jr.', 'SR': 'Sr.'}
SEX = {'M': 'boys', 'F': 'girls'}
STROKE = {'6': 'Free Relay', '7': 'Medley Relay'}
T = re.compile(r'(?:(\d+):)?(\d{1,2}\.\d{2})')


def secs(t):
    m = T.fullmatch(t.strip().rstrip('Y'))
    return int(m.group(1) or 0) * 60 + float(m.group(2)) if m else None


def fmt(s):
    return f"{int(s // 60):02d}:{s % 60:05.2f}"


def col(line, a, b):
    return line[a - 1:b]


def relays(path, team):
    out, cur, r = [], None, None
    for line in open(path, encoding='latin-1'):
        rt = line[:2]
        if rt == 'C1':
            cur = col(line, 12, 17).strip()
        if cur != team:
            r = None
            continue
        if rt == 'E0':
            stroke = STROKE.get(col(line, 26, 26))
            mdy = col(line, 38, 45)
            r = None
            if stroke:
                r = dict(event=f"{int(col(line, 22, 25))} {stroke}", gender=SEX.get(col(line, 21, 21)),
                         yy=int(mdy[6:8]), month=int(mdy[:2]), swimmers=[], cum={'P': set(), 'F': set()},
                         times=[secs(x) for x in re.findall(r'\d*:?\d+\.\d\dY', line[44:])])
                out.append(r)
        elif r and rt == 'F0':
            name = col(line, 23, 50).strip()
            last, first = [x.strip() for x in name.split(',', 1)]
            g = re.search(r'\b(09|10|11|12|FR|SO|JR|SR)[MF]\b', line[50:80])
            r['swimmers'].append(f"{first} {last}" + (f" - {GRADE[g.group(1)]}" if g else ''))
        elif r and rt == 'G0':
            flag = col(line, 144, 144)
            if flag in r['cum']:
                for k in range(10):
                    s = secs(col(line, 64 + 8 * k, 71 + 8 * k)) if col(line, 64 + 8 * k, 71 + 8 * k).strip() else None
                    if s:
                        r['cum'][flag].add(round(s, 2))
    return out


def entries(path, team):
    added, skipped = [], []
    for r in relays(path, team):
        dist = int(r['event'].split()[0])
        legs_wanted = dist // 50 if dist == 400 else 4
        for flag, cum in r['cum'].items():
            if not cum:
                continue
            cum = sorted(cum)
            label = f"{r['gender']} {r['event']} {', '.join(r['swimmers'])} ({flag})"
            if len(cum) != legs_wanted or len(r['swimmers']) != 4:
                skipped.append(f"{label}: {len(cum)} cumulative splits, {len(r['swimmers'])} swimmers")
                continue
            total = round(cum[-1], 2)
            if not any(t is not None and abs(t - total) < 0.005 for t in r['times']):
                skipped.append(f"{label}: legs reach {fmt(total)}, not an official time {r['times']}")
                continue
            splits = [fmt(b - a) for a, b in zip([0.0] + cum, cum)]
            swimmers = r['swimmers'] if legs_wanted == 4 else [s for s in r['swimmers'] for _ in (0, 1)]
            yy = r['yy'] if r['month'] >= 7 else r['yy'] - 1
            medley = 'Medley' in r['event']
            added.append(dict(type=r['event'], year=f"{yy:02d}-{yy + 1:02d}", gender=r['gender'],
                              legs=['Back', 'Breast', 'Fly', 'Free'] if medley else
                              [f'Split {i + 1}' for i in range(legs_wanted)],
                              swimmers=swimmers, splits=splits, team='Relay Team'))
    return added, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('cl2', nargs='+')
    ap.add_argument('--team', default='TVHS')
    a = ap.parse_args()
    data = json.loads(SPLITS.read_text())
    seen = {(e['type'], tuple(e['swimmers']), tuple(e['splits'])) for g in data for e in data[g]}
    n = 0
    for p in a.cl2:
        added, skipped = entries(p, a.team)
        for s in skipped:
            print(f"  skipped {s}")
        for e in added:
            key = (e['type'], tuple(e['swimmers']), tuple(e['splits']))
            if key not in seen:
                seen.add(key)
                data.setdefault(e['gender'], []).append(e)
                n += 1
    SPLITS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"relay splits: {n} new swim(s) added to {SPLITS.relative_to(ROOT)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
