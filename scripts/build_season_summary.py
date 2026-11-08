#!/usr/bin/env python3
"""
Render records/annual-summary-<season>.md for a season in progress, from the
committed meet files -- so a meet import does not hand-edit the summary.

    python3 scripts/build_season_summary.py            # newest data/season_*.json
    python3 scripts/build_season_summary.py --check    # exit 1 if the file is stale

Every number is derived:
  * swims, swimmers, grades, active swimmers, season bests -- every individual
    swim in data/meets/*.json dated inside the season (both rounds of a
    prelims/finals meet; DQs and no-swims were dropped at import). Names go
    through data/swimmer_aliases.json.
  * records broken -- data/class_records_history.json entries this season that
    beat the school (Open) record standing before them. Class-only records are
    not listed here; the annual page shows those from the history file itself.
  * meet schedule / places -- the season file's schedule (venue town).

Only the opening note is prose, and it is a template.
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_seasons import season_complete  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GRADE = {'Fr.': 'FR', 'So.': 'SO', 'Jr.': 'JR', 'Sr.': 'SR'}
GRADE_NAME = {'FR': 'Freshman', 'SO': 'Sophomore', 'JR': 'Junior', 'SR': 'Senior'}
SHORT = {'Freestyle': 'FR', 'Backstroke': 'BK', 'Breaststroke': 'BR', 'Butterfly': 'FL', 'Individual Medley': 'IM'}
BEST_EVENTS = [('50 Free', '50 Freestyle'), ('100 Free', '100 Freestyle'), ('200 Free', '200 Freestyle'),
               ('500 Free', '500 Freestyle'), ('100 Back', '100 Backstroke'), ('100 Breast', '100 Breaststroke'),
               ('100 Fly', '100 Butterfly'), ('200 IM', '200 Individual Medley')]
WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']


def secs(t):
    p = t.split(':')
    return sum(float(x) * 60 ** i for i, x in enumerate(reversed(p)))


def show(t):
    """'00:26.48' -> '26.48'; '01:52.37' -> '1:52.37'."""
    m, s = t.split(':') if ':' in t else ('0', t)
    return f"{int(m)}:{s}" if int(m) else s


def hist_date(s):
    for fmt in ('%b %d, %Y', '%b %Y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(s)


def nice(d):
    return d.strftime('%b %d, %Y')

EV_SHORT = {'Freestyle': 'Free', 'Backstroke': 'Back', 'Breaststroke': 'Breast', 'Butterfly': 'Fly',
            'Individual Medley': 'IM'}


def short_ev(e):
    d, s = e.split(' ', 1)
    return f"{d} {EV_SHORT.get(s, s)}"


def fmt(t):
    """'00:58.30' -> '58.30', '01:05.75' -> '1:05.75'."""
    t = t.lstrip('0').lstrip(':')
    return t.lstrip('0') if t.startswith('0') and ':' in t else t


def and_list(xs):
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def relay_records_in(root, lo, hi):
    """Relays at #1 on records/relay-records-*.md, swum inside the season."""
    out = []
    for g in ('boys', 'girls'):
        ev = None
        for line in (root / 'records' / f'relay-records-{g}.md').read_text().splitlines():
            if line.startswith('## '):
                ev, first = line[3:].strip(), True
            elif line.startswith('|') and ev and first and not line.startswith(('| Rank', '|--', '|-')):
                first = False
                c = [x.strip().strip('*').strip() for x in line.strip().strip('|').split('|')]
                d = hist_date(c[3])
                if lo <= f"{d:%Y-%m-%d}" <= hi:
                    out.append(dict(gender=g, event=ev, time=fmt(c[1]), names=c[2]))
    return out


def review(root, season, meets, swims, history, broken):
    """'Season in Review', written only once the State meet is imported. Every
    sentence is derived from the meet files, the records lists and the roster."""
    lo, hi = season['season_start'], season['season_end']
    state = next((m for m in meets if 'State Championship' in m['meet']), None)
    out = ["## 🌟 Season in Review", ""]
    # 1. State
    if state:
        fin = [r for r in state['individual'] if r.get('round', 'Final') == 'Final' and r.get('place', '').isdigit()]
        titles = [r for r in fin if r['place'] == '1']
        rtitles = [r for r in state['relay'] if r.get('place') == '1']
        top8 = [r for r in fin if 2 <= int(r['place']) <= 8] + \
               [r for r in state['relay'] if r.get('place', '').isdigit() and 2 <= int(r['place']) <= 8]
        won = defaultdict(list)
        for r in titles:
            won[r['athlete']].append(f"{short_ev(r['event'])} {fmt(r['time'])}")
        champs = [f"**{w}** ({and_list(evs)})" for w, evs in won.items()]
        n_titles = len(titles) + len(rtitles)
        champs += [f"the **{r['gender']} {r['event']}** ({fmt(r['time'])})" for r in rtitles]
        s = f"**At State ({state['meet']}).** "
        if champs:
            s += f"Tanque Verde won {WORDS[n_titles]} state title{'s' if n_titles > 1 else ''}: {and_list(champs)}. "
        s += (f"{WORDS[len(top8)].capitalize()} more finals swims finished in the top eight."
              if top8 else '')
        out += [f"- {s.strip()}"]
    # 2. Records
    school_events = {(e['gender'], e['event']) for _, e, _ in broken}
    rrel = relay_records_in(root, lo, hi)
    cls = [e for e in history if e['season'] == season['season']]
    holders = Counter(e['name'] for e in cls)
    s = (f"**Records.** School records fell {WORDS[len(broken)] if len(broken) < len(WORDS) else len(broken)} "
         f"times in {WORDS[len(school_events)]} individual events")
    now = {}
    for _, e, _ in broken:
        now[(e['gender'], e['event'])] = e
    held = defaultdict(list)
    for e in now.values():
        held[e['name']].append(short_ev(e['event']))
    s += ' (' + '; '.join(f"{n} now holds the {and_list(evs)}" for n, evs in held.items()) + ')' 
    if rrel:
        s += ', and ' + and_list([f"the {r['gender']} {r['event']} set a new school record of {r['time']}"
                                  for r in rrel])
    s += (f". Class records fell {len(cls)} times, to "
          + and_list([f"{n} ({c})" for n, c in holders.most_common()]) + '.')
    out += [f"- {s}"]
    # 3. Most improved: each swimmer's best at their first meet in an event vs
    # their season best at a later meet. Swims from one meet are not compared.
    by = defaultdict(list)
    for x in swims:
        by[(x['athlete'], x['event'])].append(x)
    imp = []
    for (who, ev), xs in by.items():
        days = sorted({x['date'] for x in xs}, key=lambda d: datetime.strptime(d, '%m/%d/%Y'))
        if len(days) < 2:
            continue
        first = min((x for x in xs if x['date'] == days[0]), key=lambda x: secs(x['time']))
        later = min((x for x in xs if x['date'] != days[0]), key=lambda x: secs(x['time']))
        drop = secs(first['time']) - secs(later['time'])
        if drop > 0:
            imp.append((drop / secs(first['time']), drop, who, ev, first, later))
    imp.sort(reverse=True)
    seen, top = set(), []
    for x in imp:
        if x[2] not in seen:
            seen.add(x[2])
            top.append(x)
        if len(top) == 5:
            break
    if top:
        out += ["- **Most improved.** The biggest drops from a swimmer's first meet in an event to their best "
                "later in the season (one event per swimmer):"]
        out += [f"  - **{w}** — {short_ev(ev)} {fmt(f['time'])} → {fmt(l['time'])} "
                f"(−{d:.2f}s, {pct * 100:.1f}%)" for pct, d, w, ev, f, l in top]
    # 4. Seniors
    r = season.get('roster', {})
    sen = r.get('seniors_boys', []) + r.get('seniors_girls', [])
    if sen:
        year = int(season['season'][:4]) + 1
        out += [f"- **Seniors.** Thank you to the Class of {year}: {and_list(sen)}. "
                f"[Senior page](/seniors/class-of-{year}.html)."]
    return out + ["", "---", ""]


def render(root, season, today):
    aliases = json.loads((root / 'data' / 'swimmer_aliases.json').read_text())
    lo, hi = season['season_start'], season['season_end']
    meets = []
    for path in sorted((root / 'data' / 'meets').glob('*.json')):
        doc = json.loads(path.read_text())
        if lo <= doc['date'] <= hi:
            doc['file'] = path.name
            meets.append(doc)
    town = {}
    for m in season['schedule']['meets']:
        town[m['date_start']] = m['venue'].split(',')[-1].strip()
    swims = []
    for m in meets:
        for r in m['individual']:
            swims.append(dict(r, athlete=aliases.get(r['athlete'], r['athlete']), g=GRADE[r['grade']]))

    # records broken: history entries this season that beat the Open record before them
    history = json.loads((root / 'data' / 'class_records_history.json').read_text())
    broken = []
    for e in history:
        if e['season'] != season['season']:
            continue
        day = hist_date(e['date'])
        same = [x for x in history if x['gender'] == e['gender'] and x['event'] == e['event']]
        prior = [x for x in same if hist_date(x['date']) < day]
        prior += [x['previous'] for x in same if x.get('previous') and hist_date(x['previous']['date']) < day]
        best = min(prior, key=lambda x: secs(x['time'])) if prior else None
        if best is None or secs(e['time']) < secs(best['time']):
            broken.append((day, e, best))
    broken.sort(key=lambda x: x[0])

    n_meets = len(meets)
    done = season_complete(season)
    names = ', '.join(f"the {m['meet']} ({hist_date(nice(datetime.strptime(m['date'], '%Y-%m-%d'))).strftime('%b')} "
                      f"{int(m['date'][8:])}{'-' + str(int(m['date_end'][8:])) if m.get('date_end') else ''})"
                      for m in meets)
    names = names.rsplit(', ', 1)
    names = ' and '.join(names) if len(names) == 2 else names[0]
    sources = []
    for m in meets:
        if m['source']['kind'] == 'hytek-sdif-cl2':
            rounds = (' -- prelims and finals, every swim of both rounds' if m.get('date_end') else '')
            sources.append(f"{m['meet']} swims come from the meet's own Hy-Tek results file (`data/meets/{m['file']}`){rounds}")
        else:
            sources.append(f"{m['meet']} swims come from the MaxPreps \"Best Times by Event\" tables (`data/meets/{m['file']}`)")
    t_lo = datetime.strptime(lo, '%Y-%m-%d')
    t_hi = datetime.strptime(hi, '%Y-%m-%d')
    out = [f"# {season['season']} Season Summary", "## Tanque Verde High School Swimming", "",
           f"**Generated:** {today:%B %d, %Y}".replace(' 0', ' '), "",
           *(["> **Season complete.**",
               f"> This summary covers the **{WORDS[n_meets]}** meets with posted results: {names}. "
               "Dual-meet results are not included."] if done else
             ["> ⚠️ **SEASON IN PROGRESS — NOT A FINAL SUMMARY.**",
              f"> The {season['season']} season runs {t_lo:%b} {t_lo.day}, {t_lo.year} through {t_hi:%b} {t_hi.day}, {t_hi.year}. "
              f"As of {today:%b} {today.day}, {today.year} this summary",
              f"> covers **{WORDS[n_meets]}** meets: {names}. Dual-meet results are not included. "
              "Every number below is a running count."]), ">",
           "> **How the counts are made.** " + '. '.join(sources) + ". DQs and no-swims are excluded.",
           "", "---", "",
           *(review(root, season, meets, swims, history, broken) if done else []),
           "## Season Overview", "",
           f"**Total Swims:** {len(swims)}",
           f"**Swimmers:** {len({s['athlete'] for s in swims})}",
           f"**Meets Attended:** {n_meets}", "", "### Participation by Gender"]
    by_g = Counter(s['gender'] for s in swims)
    out += [f"- **Boys:** {by_g['boys']} swims", f"- **Girls:** {by_g['girls']} swims", "", "### Participation by Grade"]
    by_gr = Counter(s['g'] for s in swims)
    out += [f"- **{GRADE_NAME[g]}:** {by_gr[g]} swims" for g in GRADE_NAME]
    out += ["", "---", "", "## Meet Schedule", "", "| Date | Meet |", "|------|------|"]
    for m in meets:
        d = datetime.strptime(m['date'], '%Y-%m-%d')
        out.append(f"| {nice(d)} | {m['meet']} ({town.get(m['date'], '')}, AZ) |")
    out += ["", "---", "", "## 🏆 Records Broken", ""]
    for day, e, prev in broken:
        dist, stroke = e['event'].split(' ', 1)
        where = next((f" ({town.get(m['date'], '')}, AZ)" for m in meets if m['meet'] == e['meet']), '')
        out += [f"**{e['gender'].title()} {dist} {SHORT[stroke]} SCY**",
                f"- **NEW:** {e['time']} - {e['name']} ({e['grade']})",
                f"- *Previous:* {prev['time']} - {prev['name']}" if prev else "- *Previous:* None",
                f"- *Date:* {e['date']} at {e['meet']}{where}", ""]
    out += ["", "---", "", "## Season Best Times", "",
            "| Event | Boys Time | Boys Swimmer | Girls Time | Girls Swimmer |",
            "|-------|----------:|--------------|-----------:|---------------|"]
    for label, ev in BEST_EVENTS:
        cells = [label]
        for g in ('boys', 'girls'):
            pool = [s for s in swims if s['gender'] == g and s['event'] == ev]
            if pool:
                b = min(pool, key=lambda s: secs(s['time']))
                cells += [show(b['time']), f"{b['athlete']} ({b['g']})"]
            else:
                cells += ['-', '-']
        out.append('| ' + ' | '.join(cells) + ' |')
    out += ["", "---", "", "## Active Swimmers", ""]
    for g in ('boys', 'girls'):
        out += [f"### {g.title()}", ""]
        count, grade = Counter(), {}
        for s in swims:
            if s['gender'] == g:
                count[s['athlete']] += 1
                grade[s['athlete']] = s['g']
        groups = defaultdict(list)
        for n in count:
            groups[grade[n]].append(n)
        for gr in GRADE_NAME:
            if groups[gr]:
                out += [f"**{gr}:**"] + [f"- {n} ({count[n]} swims)" for n in sorted(groups[gr])] + [""]
    out += ["---", "",
            f"*Generated: {today:%B} {today.day}, {today.year} — "
            f"{'season complete' if done else 'season in progress'}, {n_meets} meets included "
            "(dual meets not included).*"]
    return '\n'.join(out) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--season-file', help='data/season_<season>.json (default: newest)')
    ap.add_argument('--today', help='YYYY-MM-DD for the "as of" date (default: today, or the file\'s own with --check)')
    ap.add_argument('--check', action='store_true', help='compare with the committed file instead of writing')
    a = ap.parse_args()
    sf = Path(a.season_file) if a.season_file else max((ROOT / 'data').glob('season_*.json'))
    season = json.loads(sf.read_text())
    out = ROOT / 'records' / f"annual-summary-{season['season']}.md"
    if a.today:
        today = datetime.strptime(a.today, '%Y-%m-%d')
    elif a.check and out.exists():
        line = next(l for l in out.read_text().splitlines() if l.startswith('**Generated:**'))
        today = datetime.strptime(line.split('**Generated:**')[1].strip(), '%B %d, %Y')
    else:
        today = datetime.now()
    text = render(ROOT, season, today)
    if a.check:
        if not out.exists() or out.read_text() != text:
            sys.exit(f"{out.relative_to(ROOT)} is stale -- run: python3 scripts/build_season_summary.py")
        print(f"✅ {out.relative_to(ROOT)} matches the meet files")
        return
    out.write_text(text)
    print(f"wrote {out.relative_to(ROOT)}: {len(text.splitlines())} lines")


if __name__ == '__main__':
    main()
