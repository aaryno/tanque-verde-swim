#!/usr/bin/env python3
"""
Save one meet's MaxPreps rows as a committed meet file.

    python3 scripts/harvest/harvest_maxpreps_season.py --season 26-27 --out /tmp/h.json
    python3 scripts/harvest/maxpreps_meet_file.py /tmp/h.json --date 2026-09-19

Writes data/meets/<YYYY-MM-DD>-<slug>.json in the same shape as
import_hytek_cl2.py, so every meet the team swims -- whichever source posted
it -- gets a meet page built from one kind of file.

What MaxPreps does not give, the file does not invent: no place, no entry
time, and no relay swimmers (`participants` is empty). Rows already in a
meet file are skipped by the season harvest's merge, so committing this file
does not double-count a swim.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harvest_maxpreps_season import clean_meet  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('harvest', help='JSON written by harvest_maxpreps_season.py --out')
    ap.add_argument('--date', required=True, help='meet date, YYYY-MM-DD')
    ap.add_argument('--out-dir', default=str(REPO / 'data' / 'meets'))
    a = ap.parse_args()

    h = json.loads(Path(a.harvest).read_text())
    d = datetime.strptime(a.date, '%Y-%m-%d')
    mdy = f'{d.month}/{d.day}/{d.year}'
    ind = [r for r in h['individual'] if r['date'] == mdy and r.get('source') == 'maxpreps']
    rel = [r for r in h['relay'] if r['date'] == mdy and r.get('source') == 'maxpreps']
    if not ind and not rel:
        sys.exit(f'no MaxPreps rows dated {mdy} in {a.harvest}')
    names = {clean_meet(r['meet'], r['date']) for r in ind + rel}
    if len(names) != 1:
        sys.exit(f'{mdy} holds more than one meet: {sorted(names)} -- one file per meet')
    meet = names.pop()
    if any(not r.get('grade') for r in ind):
        sys.exit('a row has no grade -- fix the roster before saving')

    doc = {
        'meet': meet, 'date': a.date, 'course': 'SCY',
        'team': {'code': 'AZTVHS', 'name': 'Tanque Verde High School'},
        'source': {'kind': 'maxpreps-stats', 'url': ind[0]['source_url'] if ind else rel[0]['source_url'],
                   'fetched_at': h['fetched_at']},
        'dropped': {},
        'individual': [{'event': r['event'], 'athlete': r['athlete'], 'grade': r['grade'], 'gender': r['gender'],
                        'time': r['time'], 'date': r['date'], 'round': r['round'], 'meet': meet}
                       for r in sorted(ind, key=lambda r: (r['gender'], r['event'], r['time']))],
        'relay': [{'event': r['event'], 'gender': r['gender'], 'time': r['time'], 'participants': [],
                   'date': r['date'], 'meet': meet}
                  for r in sorted(rel, key=lambda r: (r['gender'], r['event'], r['time']))],
    }
    slug = re.sub(r'[^a-z0-9]+', '-', meet.lower()).strip('-')
    out = Path(a.out_dir) / f'{a.date}-{slug}.json'
    out.write_text(json.dumps(doc, indent=2) + '\n')
    print(f'wrote {out.relative_to(REPO)}: {len(doc["individual"])} individual, {len(doc["relay"])} relay')


if __name__ == '__main__':
    main()
