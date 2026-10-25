#!/usr/bin/env python3
"""
Import one meet's Hy-Tek results and rebuild everything derived from it.

    python3 scripts/import_meet.py RESULTS.cl2 --meet "Arena High School Classic"
    python3 scripts/import_meet.py RESULTS.cl2 --meet "Southern Arizona Regional Qualifier" \\
        --finals-date 2026-10-24          # prelims/finals meet

The procedure (IMPORT_MEET.md) in one command. Safe to re-run: every step
rewrites its output whole, so running it twice gives the same tree.

  1. import_hytek_cl2.py   .cl2 -> data/meets/<date>-<slug>.json
  2. REPORT                what this meet breaks: school (Open) and class records
                           in records/records-*.md, and where its relays land in
                           records/relay-records-*.md. Those three files and
                           data/class_records_history.json are the hand-kept
                           sources of truth -- this prints what to change in
                           them; it does not change them.
  3. season file           data/season_<season>.json results_so_far, from the
                           meet files
  4. season harvest        MaxPreps + every meet file -> records/top10-*-<season>.md
  5. apply_aliases.py      canonical names in every list
  6. build_alltime_top10.py
  7. build_season_summary.py
  8. generate_website.py   renders docs/ and runs the guards; a stale record
                           (class_top10), stale all-time list, stale summary or
                           a meet swim faster than the books stops the build

With --report-only it stops after step 2. If the report lists record changes,
make them (IMPORT_MEET.md § Records) and run this again; step 8 refuses to
build until the books agree with the meet file.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / 'scripts'
GRADE = {'Fr.': 'Freshman', 'So.': 'Sophomore', 'Jr.': 'Junior', 'Sr.': 'Senior'}


def run(*cmd):
    print(f"\n$ {' '.join(str(c) for c in cmd)}", flush=True)
    r = subprocess.run([sys.executable, *map(str, cmd)], cwd=ROOT)
    if r.returncode:
        sys.exit(f"stopped: {Path(str(cmd[0])).name} exited {r.returncode}")


def secs(t):
    p = t.strip('*').split(':')
    return sum(float(x) * 60 ** i for i, x in enumerate(reversed(p)))


def tables(path):
    """### / ## headed markdown tables -> {event: [row dict]}."""
    out, ev, hdr = {}, None, None
    for line in path.read_text().splitlines():
        m = re.match(r'^#{2,3} (.+)$', line.strip())
        if m:
            ev = m.group(1).strip()
            continue
        if line.startswith('|') and ev and not set(line) <= set('|-: '):
            cells = [c.strip().strip('*').strip() for c in line.strip().strip('|').split('|')]
            if cells[0] in ('Rank', 'Grade'):
                hdr = cells
                continue
            out.setdefault(ev, []).append(dict(zip(hdr, cells)))
    return out


def report(doc):
    """Print every record and relay-list change this meet calls for."""
    aliases = json.loads((ROOT / 'data' / 'swimmer_aliases.json').read_text())
    changes = 0
    print(f"\n=== {doc['meet']}: what it changes in the books")
    for g in ('boys', 'girls'):
        rec = tables(ROOT / 'records' / f'records-{g}.md')
        rel = tables(ROOT / 'records' / f'relay-records-{g}.md')
        best = {}
        for r in doc['individual']:
            if r['gender'] != g:
                continue
            k = (aliases.get(r['athlete'], r['athlete']), r['event'])
            if k not in best or secs(r['time']) < secs(best[k]['time']):
                best[k] = r
        for (who, ev), r in sorted(best.items(), key=lambda x: (x[0][1], x[0][0])):
            rows = {x['Grade']: x for x in rec.get(ev, [])}
            for label in (GRADE[r['grade']], 'Open'):
                cur = rows.get(label)
                if cur and secs(r['time']) < secs(cur['Time']):
                    changes += 1
                    print(f"  RECORD  {g} {ev} {label}: {who} {r['time']} ({r['round']} {r['date']}) "
                          f"-- was {cur['Time']} {cur['Athlete']} {cur['Date']}")
        for r in doc['relay']:
            if r['gender'] != g:
                continue
            lst = rel.get(r['event'], [])
            day = datetime.strptime(r['date'], '%m/%d/%Y').strftime('%b %d, %Y')
            if any(secs(x['Time']) == secs(r['time']) and x['Date'] == day for x in lst):
                print(f"  ok      {g} {r['event']} {r['time']} is already on the relay list")
                continue
            rank = 1 + sum(secs(x['Time']) < secs(r['time']) for x in lst)
            if rank <= len(lst):
                changes += 1
                print(f"  RELAY   {g} {r['event']} {r['time']} would be #{rank} of {len(lst)} "
                      f"[{', '.join(r['participants'])}]")
    if not changes:
        print("  nothing: no record and no relay-list change")
    return changes


def season_for(date):
    for f in sorted((ROOT / 'data').glob('season_*.json')):
        s = json.loads(f.read_text())
        if s['season_start'] <= date <= s['season_end']:
            return f, s
    sys.exit(f"no data/season_*.json covers {date}")


def meets_in(season):
    out = []
    for p in sorted((ROOT / 'data' / 'meets').glob('*.json')):
        d = json.loads(p.read_text())
        if season['season_start'] <= d['date'] <= season['season_end']:
            out.append(d)
    return out


def when(d):
    a = datetime.strptime(d['date'], '%Y-%m-%d')
    e = datetime.strptime(d.get('date_end', d['date']), '%Y-%m-%d')
    return f"{a:%b} {a.day}" + (f"-{e.day}" if e != a else '') + f", {e.year}"


def update_season_file(path, season, meets):
    raw = path.read_text()
    kinds = {'hytek-sdif-cl2': 'Hy-Tek results file', 'maxpreps-stats': 'MaxPreps /stats/'}
    listed = '; '.join(f"{m['meet']} ({when(m)}, {kinds.get(m['source']['kind'], m['source']['kind'])})" for m in meets)
    season['results_so_far'] = {
        '_note': f"Written by scripts/import_meet.py from data/meets/. Meets included: {listed}. "
                 "Dual meets are not included. Do not imply a complete season.",
        'meets_with_results': len(meets),
        'latest_meet': meets[-1]['meet'],
        'latest_meet_date': meets[-1]['date'],
    }
    path.write_text(json.dumps(season, indent=2, ensure_ascii=False) + "\n")
    print(f"\nupdated {path.relative_to(ROOT)} results_so_far: {len(meets)} meets, latest {meets[-1]['meet']}")
    return raw != path.read_text()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('cl2')
    ap.add_argument('--meet', required=True, help='meet name as the records should show it')
    ap.add_argument('--finals-date', help='YYYY-MM-DD, for a meet with prelims')
    ap.add_argument('--report-only', action='store_true', help='import + report, then stop')
    a = ap.parse_args()

    cmd = [S / 'harvest' / 'import_hytek_cl2.py', Path(a.cl2).resolve(), '--meet', a.meet]
    if a.finals_date:
        cmd += ['--finals-date', a.finals_date]
    run(*cmd)
    slug = re.sub(r'[^a-z0-9]+', '-', a.meet.lower()).strip('-')
    doc = next(json.loads(p.read_text()) for p in sorted((ROOT / 'data' / 'meets').glob(f'*-{slug}.json'), reverse=True))
    changes = report(doc)
    if a.report_only:
        return

    sf, season = season_for(doc['date'])
    meets = meets_in(season)
    update_season_file(sf, season, meets)
    last = max(m.get('date_end', m['date']) for m in meets)
    last = datetime.strptime(last, '%Y-%m-%d')
    s0, s1 = (datetime.strptime(season[k], '%Y-%m-%d') for k in ('season_start', 'season_end'))
    words = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
    note = (f"⚠️ Season in progress. Covers {words[len(meets)]} meets swum through {last:%b} {last.day}, {last.year} "
            f"({', '.join(m['meet'] for m in meets)}); dual-meet results are not included. The {season['season']} season "
            f"runs {s0:%b} {s0.day}, {s0.year} – {s1:%b} {s1.day}, {s1.year}. Not a final season list.")
    slug_season = f"{season['season'][2:4]}-{season['season'][5:7]}"
    run(S / 'harvest' / 'harvest_maxpreps_season.py', '--season', slug_season, '--write-top10', 'records',
        '--in-progress-note', note, '--out', '/dev/null')
    run(S / 'apply_aliases.py')
    run(S / 'build_alltime_top10.py')
    run(S / 'build_season_summary.py')
    run(S / 'generate_website.py')
    print(f"\n✅ {doc['meet']} imported and the site rebuilt. {changes} record/relay change(s) were reported above --"
          " confirm each is in records/ and data/class_records_history.json before you publish.")


if __name__ == '__main__':
    main()
