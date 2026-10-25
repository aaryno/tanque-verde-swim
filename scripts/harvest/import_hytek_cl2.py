#!/usr/bin/env python3
"""
Turn one Hy-Tek meet-results export (.cl2, SDIF v3) into a committed meet file.

    python3 scripts/harvest/import_hytek_cl2.py RESULTS.cl2 --meet "Arena High School Classic"
    python3 scripts/harvest/import_hytek_cl2.py RESULTS.cl2 --meet "Southern Arizona Regional Qualifier" \
        --finals-date 2026-10-24      # a prelims/finals meet swum over two days

Writes data/meets/<YYYY-MM-DD>-<slug>.json holding Tanque Verde's swims from
that meet. harvest_maxpreps_season.py --write-top10 merges every data/meets/
file for its season into the season Top 10, so a meet that MaxPreps never
posts (or posts late) is not lost when the MaxPreps harvest is re-run.

Why a meet file rather than editing records/top10-*.md by hand: the season
lists are rendered whole from their sources. A hand edit would be erased by
the next harvest; a source file is merged into every harvest.

What it reads, and what it refuses to guess:
  * D0 (individual) and E0/F0 (relay + its four legs) for one team code.
  * Both rounds of a prelims/finals meet, one row per swim, each with its own
    `round` ('Prelim' / 'Final'), date and place. A prelim swim is an official
    swim -- records and season bests have always counted them -- and a swimmer
    who misses the final has no other time. A timed-final meet (no prelim
    column) gives exactly one 'Final' row per swim, as before. DQ / NS /
    scratch rows are dropped and counted -- a DQ is not a time.
  * The .cl2 carries one date per individual swim: the PRELIM day. The finals
    day is not in the file, so a meet with prelims needs --finals-date; it is
    refused, not guessed (finals are often, but not always, the next day). It
    must fall inside the meet's own B1 start/end dates. Relay rows carry their
    own date and use it.
  * Grade is the meet file's class code (FR/SO/JR/SR), verbatim. The season
    harvest cross-checks it against the MaxPreps roster and stops on a
    mismatch.
  * Names are "Last, First" in SDIF and are written "First Last". No alias or
    similarity matching happens here -- apply_aliases.py owns identity.
  * Only short-course-yards swims (course code Y) are kept; the records are SCY.
  * The entry ("seed") time is kept as `seed`. It is whatever the coach
    entered -- often a season best, sometimes a club time or an estimate --
    so it measures a drop from entry, not a verified personal best.

The source file's name and SHA-256 are recorded, so a row can always be traced
to the exact file it came from.
"""
import argparse, hashlib, json, re, sys
from datetime import datetime
from pathlib import Path

STROKE = {'1': 'Freestyle', '2': 'Backstroke', '3': 'Breaststroke', '4': 'Butterfly',
          '5': 'Individual Medley', '6': 'Free Relay', '7': 'Medley Relay'}
GRADE = {'FR': 'Fr.', 'SO': 'So.', 'JR': 'Jr.', 'SR': 'Sr.'}
SEX = {'M': 'boys', 'F': 'girls'}
TIME = re.compile(r'^(?:(\d+):)?(\d{1,2}\.\d{2})Y$')


def col(line, a, b):
    """1-indexed inclusive SDIF column slice."""
    return line[a - 1:b].strip()


def mmss(t):
    """'1:04.09Y' -> '01:04.09' (the harvester's sortable form); None if not a SCY time."""
    m = TIME.match(t)
    if not m:
        return None
    return f"{int(m.group(1) or 0):02d}:{float(m.group(2)):05.2f}"


def first_last(n):
    last, first = [x.strip() for x in n.split(',', 1)]
    return f"{first} {last}"



def place(raw):
    """Finals place. 0 marks an exhibition swim, written 'Ex.' (Aaryn, 2026-10-19).
    The swim still happened and its time stands; it just did not score."""
    return 'Ex.' if raw.strip() in ('0', '00', '000') else raw.strip()

def parse(path, team):
    rows, relays, dropped, team_name, cur, relay = [], [], [], None, None, None
    meet_days = None
    for line in open(path, encoding='latin-1'):
        rt = line[:2]
        if rt == 'B1':
            meet_days = (col(line, 122, 129), col(line, 130, 137))
        if rt == 'C1':
            cur = col(line, 12, 17)
            if cur == team:
                team_name = col(line, 18, 47)
        if cur != team:
            continue
        if rt == 'D0':
            ev = f"{int(col(line, 68, 71))} {STROKE[col(line, 72, 72)]}"
            who = first_last(col(line, 12, 39))
            def swim(t, rnd, pl):
                return dict(event=ev, athlete=who, grade=GRADE.get(col(line, 64, 65), ''),
                            gender=SEX[col(line, 67, 67)], time=t, date=col(line, 81, 88),
                            round=rnd, place=place(pl), seed=mmss(col(line, 89, 97)))
            pre, fin = col(line, 98, 106), col(line, 116, 124)
            if pre:
                if mmss(pre):
                    rows.append(swim(mmss(pre), 'Prelim', col(line, 133, 135)))
                else:
                    dropped.append(f"{who} {ev} prelim: {pre}")
            if fin:
                if mmss(fin):
                    rows.append(swim(mmss(fin), 'Final', col(line, 136, 138)))
                else:
                    dropped.append(f"{who} {ev}{' final' if pre else ''}: {fin}")
            if not pre and not fin:
                dropped.append(f"{who} {ev}: no time")
        elif rt == 'E0':
            raw = re.findall(r'(\d*:?\d+\.\d\dY|DQY|NSY)', line[44:])[-1]
            ev = f"{int(col(line, 22, 25))} {STROKE[col(line, 26, 26)]}"
            relay = dict(event=ev, letter=col(line, 12, 12), gender=SEX[col(line, 21, 21)],
                         time=mmss(raw), raw_time=raw, day=col(line, 38, 45), participants=[])
            relays.append(relay)
        elif rt == 'F0' and relay is not None:
            relay['participants'].append(first_last(col(line, 23, 50)))
    kept = []
    for r in relays:
        label = f"{r['gender']} {r['letter']} {r['event']}: {r['raw_time']}"
        if not r['time']:
            dropped.append(label)
        elif len(r['participants']) != 4:
            dropped.append(f"{label} has {len(r['participants'])} named legs, not 4")
        else:
            r.pop('raw_time'); kept.append(r)
    return team_name, rows, kept, dropped, meet_days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cl2')
    ap.add_argument('--meet', required=True, help="meet name as records/*.md should show it")
    ap.add_argument('--team', default='AZTVHS', help="SDIF team code (default AZTVHS)")
    ap.add_argument('--out-dir', default='data/meets')
    ap.add_argument('--finals-date', help="YYYY-MM-DD the finals were swum; required when the file has prelims")
    a = ap.parse_args()

    team_name, rows, relays, dropped, meet_days = parse(a.cl2, a.team)
    if not rows:
        sys.exit(f"no {a.team} swims in {a.cl2}")
    dates = {r['date'] for r in rows}
    if len(dates) != 1:
        sys.exit(f"expected one prelim/timed-final date on individual swims, found {sorted(dates)}")
    day = datetime.strptime(dates.pop(), '%m%d%Y')
    finals = day
    if any(r['round'] == 'Prelim' for r in rows):
        if not a.finals_date:
            sys.exit("this file has prelim swims; pass --finals-date YYYY-MM-DD (the .cl2 does not say when finals were swum)")
        finals = datetime.strptime(a.finals_date, '%Y-%m-%d')
        lo, hi = (datetime.strptime(d, '%m%d%Y') for d in meet_days)
        if not (lo <= day <= finals <= hi):
            sys.exit(f"--finals-date {a.finals_date} is outside the meet's own dates {lo:%Y-%m-%d}..{hi:%Y-%m-%d} "
                     f"or before the prelims ({day:%Y-%m-%d})")
    elif a.finals_date:
        sys.exit("--finals-date given, but this file has no prelim swims")
    us = lambda d: f"{d.month}/{d.day}/{d.year}"  # noqa: E731
    for r in rows:
        r['date'] = us(finals if r['round'] == 'Final' else day)
        r['meet'] = a.meet
    for r in relays:
        r["date"] = us(datetime.strptime(r.pop("day"), "%m%d%Y"))
        r['meet'] = a.meet
    last = max([finals] + [datetime.strptime(r['date'], '%m/%d/%Y') for r in relays])
    slug = re.sub(r'[^a-z0-9]+', '-', a.meet.lower()).strip('-')
    out = Path(a.out_dir) / f"{day:%Y-%m-%d}-{slug}.json"
    doc = {
        'meet': a.meet,
        'date': f"{day:%Y-%m-%d}",
        **({'date_end': f"{last:%Y-%m-%d}"} if last != day else {}),
        'course': 'SCY',
        'team': {'code': a.team, 'name': team_name},
        'source': {'kind': 'hytek-sdif-cl2', 'file': Path(a.cl2).name,
                   'sha256': hashlib.sha256(Path(a.cl2).read_bytes()).hexdigest()},
        'dropped': dropped,
        'individual': rows,
        'relay': relays,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"wrote {out}: {len(rows)} individual, {len(relays)} relay; dropped {len(dropped)}")
    for d in dropped:
        print(f"  dropped: {d}")


if __name__ == '__main__':
    main()
