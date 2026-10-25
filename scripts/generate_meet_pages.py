#!/usr/bin/env python3
"""
One page per meet: docs/meets/<YYYY-MM-DD>-<slug>.html.

Every committed data/meets/*.json inside the season gets a page, and the
landing page links to it from the schedule and from its short "latest meet"
teaser. That is the archive: a meet's story stays on its own page after the
home page moves on to the next meet.

Nothing on a meet page is typed in:
  * records broken  -- data/class_records_history.json entries dated that day.
    The Open record each one beat is the fastest history entry (or one it
    replaced) dated before the meet, so a record broken twice in a season
    links both ways: "beat Kent's 5:03.13 from the Canyon del Oro Classic",
    and on Kent's page, "broken again Oct 17 by Wade Olsson".
  * extra lines from data/season_<season>.json `milestone` / `milestone_followups`
    (the oldest-record claim, re-verified at build; who is whose brother).
  * highlights -- generate_landing_page.meet_highlights, the same derivation
    the home page used.
  * results -- the meet file itself.

Refuses to build when a meet file and the records disagree: a meet swim
faster than the current Open record in records/records-*.md, or a history
entry dated at a meet that the meet file does not contain.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_landing_page import (MONTHS, esc, to_secs, show_time,  # noqa: E402
                                   grade_tables, meet_highlights, meet_days, best_swims, fmt_meet_date,
                                   verify_oldest_record, describe_record, check_followups)

REPO = Path(__file__).resolve().parent.parent
GRADE_WORD = {'FR': 'Freshman', 'SO': 'Sophomore', 'JR': 'Junior', 'SR': 'Senior',
              'Fr.': 'Freshman', 'So.': 'Sophomore', 'Jr.': 'Junior', 'Sr.': 'Senior'}
EVENT_ORDER = ['200 Medley Relay', '200 Freestyle', '200 Individual Medley', '50 Freestyle', '100 Butterfly',
               '100 Freestyle', '500 Freestyle', '200 Free Relay', '100 Backstroke', '100 Breaststroke',
               '400 Free Relay']


def hist_date(s):
    """History dates are 'Oct 17, 2026' or, for old rows, just 'Nov 2007'."""
    for fmt in ('%b %d, %Y', '%b %Y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(f'unreadable record date {s!r}')


def long_date(iso, end=None):
    """'Sat, Oct 17, 2026'; a two-day meet reads 'Fri–Sat, Oct 23–24, 2026'."""
    d = datetime.strptime(iso, '%Y-%m-%d')
    if end and end != iso:
        e = datetime.strptime(end, '%Y-%m-%d')
        return f"{d.strftime('%a')}&ndash;{e.strftime('%a')}, {fmt_meet_date(iso, end)}, {e.year}"
    return f"{d.strftime('%a')}, {MONTHS[d.month - 1][:3]} {d.day}, {d.year}"


def short_date(d):
    return f'{MONTHS[d.month - 1][:3]} {d.day}'


def season_meets(project_root, season):
    out = []
    for path in sorted((project_root / 'data' / 'meets').glob('*.json')):
        doc = json.loads(path.read_text())
        if season['season_start'] <= doc['date'] <= season['season_end']:
            doc['slug'] = path.stem
            doc['href'] = f'/meets/{path.stem}.html'
            out.append(doc)
    return out


def records_at(history, meets):
    """Records broken at each meet, keyed by the meet's (first) date, ISO. A
    prelims/finals meet owns every one of its days."""
    by_day = {d: m for m in meets for d in meet_days(m)}
    out = {}
    for e in history:
        day = hist_date(e['date'])
        iso = day.strftime('%Y-%m-%d')
        if iso not in by_day:
            continue
        same = [x for x in history if x['gender'] == e['gender'] and x['event'] == e['event']]
        prior = [x for x in same if hist_date(x['date']) < day]
        prior += [x['previous'] for x in same if x.get('previous') and hist_date(x['previous']['date']) < day]
        best = min(prior, key=lambda x: to_secs(x['time'])) if prior else None
        open_prev = best if best and to_secs(e['time']) < to_secs(best['time']) else None
        later = sorted((x for x in same if hist_date(x['date']) > day and to_secs(x['time']) < to_secs(e['time'])),
                       key=lambda x: hist_date(x['date']))
        def link(rec):
            if not rec:
                return None
            d = hist_date(rec['date']).strftime('%Y-%m-%d')
            m = by_day.get(d)
            return m['href'] if m and m['meet'] == rec.get('meet') else None
        out.setdefault(by_day[iso]['date'], []).append(dict(e, open_prev=open_prev, open_prev_href=link(open_prev),
                                            broken_by=later[0] if later else None,
                                            broken_by_href=link(later[0]) if later else None))
    return out


def check_meet(meet, recs, project_root):
    """A meet file must agree with the records before its page is published."""
    have = {(r['athlete'], r['event'], to_secs(r['time'])) for r in meet['individual']}
    for e in recs:
        if (e['name'], e['event'], to_secs(e['time'])) not in have:
            sys.exit(f"{meet['slug']}: class_records_history has {e['name']} {e['event']} {e['time']} "
                     f"on {e['date']} but the meet file does not -- fix one of them")
    tables = {g: grade_tables(project_root / 'records', g) for g in ('boys', 'girls')}
    for r in meet['individual']:
        rec = tables[r['gender']].get(r['event'], {}).get('Open')
        if rec and to_secs(r['time']) < to_secs(rec[0]):
            sys.exit(f"{meet['slug']}: {r['athlete']} {r['event']} {r['time']} beats the Open record "
                     f"{rec[0]} in records/records-{r['gender']}.md -- update the records first")


WORDS = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six']


def gap_words(d1, d2):
    days = (d2 - d1).days
    if days % 7 == 0 and 0 < days <= 42:
        return f"{WORDS[days // 7]} week{'s' if days > 7 else ''}"
    return f'{days} days'


def relation_of(season, rec):
    """'older brother' etc., from the season file -- never guessed from surnames."""
    for f in season.get('milestone_followups', []):
        if (f['swimmer'], f['event'], f['time']) == (rec['name'], rec['event'], rec['time']) and f.get('relation'):
            return f['relation']
    return None


def oldest_verdict(season, project_root, rec):
    ms = season.get('milestone')
    if ms and (ms['swimmer'], ms['event'], ms['time']) == (rec['name'], rec['event'], rec['time']):
        verdict, phrase, runner_up = verify_oldest_record(project_root / 'records', ms)
        return verdict == 'oldest', phrase, runner_up
    return False, None, None


ORD = {1: '1st', 2: '2nd', 3: '3rd'}


def ordinal(n):
    return ORD.get(n, f'{n}th')


def short_event(e):
    return (e.replace('Freestyle', 'Free').replace('Backstroke', 'Back').replace('Breaststroke', 'Breast')
             .replace('Butterfly', 'Fly').replace('Individual Medley', 'IM'))


def t(x):
    return f'<span class="time">{esc(show_time(x))}</span>'


def names_list(names):
    names = [f'<strong>{esc(n)}</strong>' for n in names]
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]


def per_swimmer(items):
    """[(athlete, sort_key, html)] -> [(athlete, html joined)] in first-seen order of
    each swimmer's best item. One line per swimmer, so one swimmer's three great
    swims take one line and leave room for everyone else."""
    by, order = {}, []
    for who, key, html in sorted(items, key=lambda x: x[1]):
        if who not in by:
            by[who] = []
            order.append(who)
        by[who].append(html)
    return [(who, '; '.join(by[who])) for who in order]


def top_swims(meet, meets, recs, near, alltime, drops):
    """The meet's top swims, by priority: records, top-8 places, season bests,
    'knocking on the door', drops from entry time, all-time Top 10. Each is
    compressed to one line per swimmer."""
    ex = lambda r: ' <small class="text-muted">(exhibition)</small>' if r.get('place') == 'Ex.' else ''  # noqa: E731
    cats = []
    # 1. records
    items = []
    for r in recs:
        bits = []
        if r['open_prev']:
            p = r['open_prev']
            bits.append(f"school record (was {esc(p['time'])}, {esc(p['name'])}, {esc(p['date'][-4:])})")
        p = r['previous']
        bits.append(f"{GRADE_WORD[r['grade']]} record (was {esc(p['time'])}, {esc(p['name'])}, {esc(p['date'][-4:])})")
        html = f"{esc(short_event(r['event']))} {t(r['time'])}: {' and '.join(bits)}"
        if r['broken_by']:
            b = r['broken_by']
            where = f'<a href="{r["broken_by_href"]}">{esc(b["meet"])}</a>' if r['broken_by_href'] else esc(b['meet'])
            html += f" &mdash; broken again {esc(b['date'][:6].strip(','))} by {esc(b['name'])} at {where}"
        items.append((r['name'], 0, html))
    cats.append(('records', '&#127942; Records', '', per_swimmer(items)))
    # 2. places -- finals places only; a prelim place is a qualifying rank, not a finish
    items = [(r['athlete'], int(r['place']), f"{ordinal(int(r['place']))} {esc(short_event(r['event']))} {t(r['time'])}")
             for r in meet['individual'] if r.get('round', 'Final') == 'Final'
             and str(r.get('place', '')).isdigit() and 1 <= int(r['place']) <= 8]
    cats.append(('places', '&#129351; Top-8 finishes', '', per_swimmer(items)))
    # 3. season bests: faster than the swimmer's earlier swims this season
    earlier = {}
    for m in meets:
        if m['date'] < meet['date']:
            for r in m['individual']:
                k = (r['athlete'], r['event'])
                earlier[k] = min(earlier.get(k, 1e9), to_secs(r['time']))
    sb = []
    for r in best_swims(meet):
        k = (r['athlete'], r['event'])
        if k in earlier and to_secs(r['time']) < earlier[k]:
            sb.append(dict(r, drop=earlier[k] - to_secs(r['time'])))
    items = [(r['athlete'], -r['drop'], f"{esc(short_event(r['event']))} {t(r['time'])} "
              f"<span class=\"badge badge-pb pb-black\">&minus;{r['drop']:.2f}s</span>{ex(r)}") for r in sb]
    cats.append(('season-bests', '&#9201;&#65039; Season bests', 'Faster than their earlier swims this season.',
                 per_swimmer(items)))
    # 4. knocking on the door
    items = [(n['athlete'], n['gap'] / to_secs(n['rec_time']),
              f"{esc(short_event(n['event']))} {t(n['time'])}, <strong>{n['gap']:.2f}s</strong> off the "
              f"{esc(n['label'])} record ({esc(n['rec_time'])}, {esc(n['rec_who'])}, {esc(n['rec_date'][-4:])})")
             for n in near]
    cats.append(('knocking', '&#128064; Knocking on the door', 'Within a couple of percent of a Tanque Verde record.',
                 per_swimmer(items)))
    # 5. drops from entry time, for swims with no earlier swim this season to compare
    items = [(d['athlete'], -d['pct'], f"{esc(short_event(d['event']))} {esc(show_time(d['seed']))} &rarr; {t(d['time'])} "
              f"<span class=\"badge badge-pb pb-black\">&minus;{d['drop']:.2f}s</span>{ex(d)}")
             for d in drops if (d['athlete'], d['event']) not in earlier]
    cats.append(('drops', '&#9889; Big drops from entry time',
                 "Entry times are what the coach entered, not verified best times.", per_swimmer(items)))
    # 6. all-time Top 10
    items = [(a['athlete'], a['rank'], f"#{a['rank']} {esc(a['gender'])} {esc(short_event(a['event']))} {t(a['time'])}")
             for a in alltime if a['rank'] > 1]
    cats.append(('alltime', '&#128200; New on the all-time Top 10', '', per_swimmer(items)))
    return [c for c in cats if c[3]], sb


def summary_sentence(meet, cats, sb, skip=()):
    """One sentence that spreads the credit: wins, then season bests, then the
    swimmers knocking on the door -- leaving out whoever the headline is about."""
    parts, named = [], set(skip)
    wins = [(r['athlete'], r['event']) for r in meet['individual']
            if r.get('place') == '1' and r.get('round', 'Final') == 'Final' and r['athlete'] not in skip]
    if wins:
        parts.append(' and '.join(f'<strong>{esc(a)}</strong> won the {esc(short_event(e))}' for a, e in wins))
    if sb:
        lead = max(sb, key=lambda r: r['drop'])
        named.add(lead['athlete'])
        parts.append(f"{len(sb)} swims were season bests, led by <strong>{esc(lead['athlete'])}</strong> "
                     f"(&minus;{lead['drop']:.2f}s, {esc(short_event(lead['event']))})")
    knock = [who for key, _, _, lines in cats if key == 'knocking' for who, _ in lines if who not in named]
    if knock and len(parts) < 2:
        parts.append(f"{names_list(knock[:3])} {'is' if len(knock[:3]) == 1 else 'are'} knocking on the door of records")
    if not parts:
        return ''
    s = ', and '.join(parts[:2])
    return s[0].upper() + s[1:] + '.'


def story(meet, recs, season, project_root, cats, sb):
    """Headline, a one-sentence `short` for the home page, the full `lede`, and
    links to the meets the story continues. Derived from the records; the season
    file adds only what records cannot know (who is whose brother; the
    oldest-record claim, re-verified at build)."""
    first = lambda n: n.split()[0]  # noqa: E731
    his = lambda r: 'his' if r['gender'] == 'boys' else 'her'  # noqa: E731
    day = datetime.strptime(meet['date'], '%Y-%m-%d')
    opens = [r for r in recs if r['open_prev']]
    sequel = next((r for r in opens if r['open_prev_href'] and r['open_prev']['name'] != r['name']), None)
    links = []
    def also(rest, r0, short=False):
        bits = []
        for r in rest:
            ev = short_event(r['event']) if short else r['event']
            if r['open_prev'] and r['open_prev']['name'] == r['name']:
                bits.append(f"lowered {his(r0)} own {esc(ev)} record" + ('' if short else f" to {t(r['time'])}"))
            elif r['open_prev']:
                bits.append(f"broke the {esc(ev)} school record" + ('' if short else f" with {t(r['time'])}"))
            else:
                bits.append(f"set a {GRADE_WORD[r['grade']]} {esc(ev)} record" + ('' if short else f" of {t(r['time'])}"))
        return bits
    if sequel:
        r, p = sequel, sequel['open_prev']
        day = hist_date(r['date'])
        rel = relation_of(season, r)
        oldest, _, _ = oldest_verdict(season, project_root, dict(name=p['name'], event=r['event'], time=p['time']))
        what = 'the oldest record on the boys books' if oldest else f"the {esc(r['event'])} school record"
        under5 = (', the first 500 under five minutes in the team\'s records'
                  if r['event'] == '500 Freestyle' and to_secs(r['time']) < 300 <= to_secs(p['time']) else '')
        rest = [x for x in recs if x is not r and x['name'] == r['name']]
        more = also(rest, r)
        lede = (f"{gap_words(hist_date(p['date']), day)} after {esc(p['name'])} broke {what} in the "
                f"{esc(r['event'])}, {f'{his(r)} {esc(rel)} ' if rel else ''}<strong>{esc(r['name'])}</strong>, "
                f"a {GRADE_WORD[r['grade']].lower()}, swam <strong>{t(r['time'])}</strong> "
                f"&mdash; {to_secs(p['time']) - to_secs(r['time']):.2f} seconds under {esc(first(p['name']))}'s "
                f"mark{under5}." + (f" {'He' if r['gender'] == 'boys' else 'She'} also {' and '.join(more)}." if more else ''))
        short_more = also(rest, r, short=True)
        short = (f"{gap_words(hist_date(p['date']), day)} after {esc(p['name'])} broke "
                 f"{'the oldest boys record' if oldest else 'the ' + esc(short_event(r['event'])) + ' record'}, "
                 f"{f'{his(r)} {esc(rel)} ' if rel else ''}<strong>{esc(r['name'])}</strong> took it with "
                 f"{t(r['time'])}" + (f" &mdash; and {' and '.join(short_more)}." if short_more else '.'))
        links.append(f'<a href="{r["open_prev_href"]}">&larr; Part 1: {esc(first(p["name"]))} at the {esc(p["meet"])}</a>')
        return dict(headline=f"First {esc(first(p['name']))}, then {esc(first(r['name']))}", lede=lede, short=short,
                    links=links, about={r['name']})
    if opens:
        r, p = opens[0], opens[0]['open_prev']
        day = hist_date(r['date'])
        oldest, phrase, runner_up = oldest_verdict(season, project_root, r)
        head = (f"{esc(r['name'])} breaks the oldest {r['gender']} record" if oldest
                else f"{esc(r['name'])} sets the {esc(r['event'])} school record")
        lede = (f"{GRADE_WORD[r['grade']]} <strong>{esc(r['name'])}</strong> swam the {esc(r['event'])} in "
                f"<strong>{t(r['time'])}</strong>, breaking {esc(p['name'])}'s {esc(p['time'])} from {esc(p['date'])}"
                + (f" &mdash; <strong>{phrase}</strong>. The next-oldest still standing is the "
                   f"{describe_record(runner_up)}." if oldest else '.')
                + f" It is also the new {GRADE_WORD[r['grade']]} record.")
        more = also([x for x in recs if x is not r and x['name'] == r['name']], r)
        if more:
            lede += f" {'He' if r['gender'] == 'boys' else 'She'} also {' and '.join(more)}."
        for x in (x for x in recs if x['name'] != r['name']):
            q = x['open_prev'] or x['previous']
            what = 'school' if x['open_prev'] else GRADE_WORD[x['grade']]
            lede += (f" {GRADE_WORD[x['grade']]} <strong>{esc(x['name'])}</strong> set a new {what} "
                     f"{esc(x['event'])} record of {t(x['time'])}, breaking {esc(q['name'])}'s {esc(q['time'])} "
                     f"from {esc(q['date'][-4:])}.")
        short = (f"{GRADE_WORD[r['grade']]} <strong>{esc(r['name'])}</strong> swam the {esc(short_event(r['event']))} in "
                 f"{t(r['time'])}, breaking a school record from {esc(p['date'][-4:])}"
                 + (" &mdash; the oldest on the boys books." if oldest else '.'))
        b = r['broken_by']
        if b:
            rel = next((f['relation'] for f in season.get('milestone_followups', [])
                        if f['swimmer'] == b['name'] and f['broke_open']['name'] == r['name'] and f.get('relation')), None)
            lede += (f" It stood {gap_words(day, hist_date(b['date'])).lower()}: on {esc(b['date'])} "
                     f"{f'{his(r)} {esc(rel)} ' if rel else ''}{esc(b['name'])} lowered it to {t(b['time'])}.")
            if r['broken_by_href']:
                links.append(f'<a href="{r["broken_by_href"]}">Part 2: {esc(first(b["name"]))} at the {esc(b["meet"])} &rarr;</a>')
        return dict(headline=head, lede=lede, short=short, links=links, about={r['name']})
    if recs:
        who = sorted({r['name'] for r in recs})
        items = ', '.join(f"{esc(r['name'])} ({GRADE_WORD[r['grade']]} {esc(short_event(r['event']))}, {t(r['time'])})" for r in recs)
        n = len(recs)
        return dict(headline=f"{n} class record{'s' if n != 1 else ''} at the {esc(meet['meet'])}",
                    lede=f"New class records: {items}.", short=f"New class records for {names_list(who)}.",
                    links=links, about=set(who))
    # No records: the headline goes to a win, then the biggest season best, then the closest near-record.
    wins = [r for r in meet['individual'] if r.get('place') == '1' and r.get('round', 'Final') == 'Final']
    knock = [lines for key, _, _, lines in cats if key == 'knocking']
    if wins:
        w = wins[0]
        head = f"{esc(w['athlete'])} wins the {esc(short_event(w['event']))}"
    elif sb:
        w = max(sb, key=lambda r: r['drop'])
        head = f"{esc(w['athlete'])} drops {w['drop']:.2f}s"
    elif knock:
        head = f"{esc(knock[0][0][0])} knocking on the door of a record"
    else:
        return None
    s = summary_sentence(meet, cats, sb)
    return dict(headline=head, lede=s, short=s, links=links, about=set())


def place_label(pl):
    """'#3' for a scoring place; 'Ex.' (exhibition) passes through as written."""
    if not pl:
        return ''
    return f'<small class="res-pl">{esc(pl if pl == "Ex." else "#" + pl)}</small>'


def results_html(meet):
    """Compact per-event lists. Tables are not used: the site's phone CSS turns
    every table row into a tall card."""
    def order(e):
        return EVENT_ORDER.index(e) if e in EVENT_ORDER else 99
    out = []
    for g in ('girls', 'boys'):
        ind = [r for r in meet['individual'] if r['gender'] == g]
        rel = [r for r in meet['relay'] if r['gender'] == g]
        if not ind and not rel:
            continue
        events = {}
        for r in rel:
            who = ', '.join(esc(p) for p in r['participants']) or '<span class="text-muted">swimmers not listed</span>'
            events.setdefault(r['event'], []).append((to_secs(r['time']), r['time'], who, r.get('place')))
        two = any(r.get('round') == 'Prelim' for r in ind)
        for r in ind:
            who = f"{esc(r['athlete'])} <small class=\"text-muted\">{esc(r['grade'])}</small>"
            if two:
                who += f" <small class=\"text-muted\">{'prelim' if r.get('round') == 'Prelim' else 'final'}</small>"
            events.setdefault(r['event'], []).append((to_secs(r['time']), r['time'], who, r.get('place')))
        blocks = []
        for ev in sorted(events, key=order):
            rows = ''.join(f'<div class="res-row"><span class="time">{esc(show_time(tm))}</span>'
                           f'<span class="res-who">{who}</span>{place_label(pl)}</div>'
                           for _, tm, who, pl in sorted(events[ev]))
            blocks.append(f'<div class="res-event"><div class="res-ev">{esc(ev)}</div>{rows}</div>')
        out.append(f'<h5 class="mt-3">{g.title()} <small class="text-muted">{len(ind)} swims, '
                   f'{len(rel)} relays</small></h5>' + ''.join(blocks))
    return '\n'.join(out)


def source_line(meet):
    s = meet['source']
    if s['kind'] == 'hytek-sdif-cl2':
        return f"Results from the meet's official Hy-Tek results file ({esc(s['file'])})."
    return (f'Results from <a href="{esc(s["url"])}" target="_blank">MaxPreps</a>. MaxPreps does not list '
            f'places, entry times or relay swimmers.')


STYLE = '''<style>
.story-lead{background:#2d6a35;color:#fff;border-radius:8px;padding:14px 16px}
.story-lead a{color:#d8f0d8}
.story-lead .time{color:#fff}
.meet-nav{display:flex;justify-content:space-between;gap:8px;font-size:.9rem}
.meet-nav a,.crumbs a{text-decoration:none}
.meet-jump{display:flex;gap:8px;flex-wrap:wrap;margin:.25rem 0 1rem}
.meet-jump a{border:1px solid #2d6a35;color:#2d6a35;border-radius:999px;padding:.2rem .8rem;text-decoration:none;font-size:.9rem}
details.msec{margin-bottom:1rem}
details.msec>summary{list-style:none;background:#2d6a35;color:#fff;border-radius:8px;padding:.6rem 1rem;
  font-weight:700;font-size:1.15rem;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
details.msec>summary::-webkit-details-marker{display:none}
details.msec>summary::after{content:"\\25BC";font-size:.8rem;transition:transform .2s}
details.msec:not([open])>summary::after{transform:rotate(-90deg)}
details.msec>.msec-body{padding:.75rem .25rem 0}
.cat h5{margin:.9rem 0 .3rem}.cat ul{padding-left:1.1rem;margin-bottom:.3rem}.cat li{margin:.2rem 0}
.res-event{margin:.6rem 0}.res-ev{font-weight:700;font-size:.9rem;color:#2d6a35;border-bottom:1px solid #dee2e6}
.res-row{display:flex;gap:.6rem;align-items:baseline;padding:.15rem 0;font-size:.95rem}
.res-row .time{min-width:4.5rem}.res-who{flex:1}.res-pl{color:#888}
</style>'''

JUMP_JS = '''<script>
document.querySelectorAll('.meet-jump a').forEach(function (a) {
  a.addEventListener('click', function () { var d = document.querySelector(a.hash); if (d) d.open = true; });
});
if (location.hash) { var d = document.querySelector(location.hash); if (d && d.tagName === 'DETAILS') d.open = true; }
</script>'''


def section(sid, title, body, is_open=True):
    return (f'<details class="msec" id="{sid}"{" open" if is_open else ""}><summary>{title}</summary>'
            f'<div class="msec-body">{body}</div></details>')


def build_meet(meet, meets, recs, season, project_root):
    from generate_website import create_html_page
    sched = {m['date_start']: m for m in season['schedule']['meets']}.get(meet['date'], {})
    i = meets.index(meet)
    prev_a = (f'<a href="{meets[i - 1]["href"]}">&lsaquo; {esc(meets[i - 1]["meet"])}</a>' if i > 0 else '<span></span>')
    next_a = (f'<a href="{meets[i + 1]["href"]}">{esc(meets[i + 1]["meet"])} &rsaquo;</a>' if i + 1 < len(meets) else '<span></span>')
    where = esc(sched.get('venue', ''))
    near, alltime, drops = meet_highlights(project_root, meet)
    cats, sb = top_swims(meet, meets, recs, near, alltime, drops)
    st = story(meet, recs, season, project_root, cats, sb)
    summary = summary_sentence(meet, cats, sb, skip=st['about'] if st else ())
    if st:
        st['summary'] = summary if summary != st['lede'] else ''
    meet['story'] = st
    secs = []
    if st:
        body = (f'<div class="story-lead"><h3 class="mb-2">{st["headline"]}</h3><p class="mb-2">{st["lede"]}</p>'
                + (f'<p class="mb-2">{st["summary"]}</p>' if st['summary'] else '')
                + ''.join(f'<div class="small">{lk}</div>' for lk in st['links']) + '</div>')
        secs.append(('story', '&#128214; The story', body, True))
    if cats:
        body = ''.join(f'<div class="cat"><h5>{title}</h5>' + (f'<p class="small text-muted mb-1">{intro}</p>' if intro else '')
                       + '<ul>' + ''.join(f'<li><strong>{esc(who)}</strong> &mdash; {html}</li>' for who, html in lines)
                       + '</ul></div>' for _, title, intro, lines in cats)
        secs.append(('top-swims', '&#11088; Top swims', body, True))
    n = len(meet['individual']) + len(meet['relay'])
    secs.append(('results', f'&#128203; Full results ({n})', results_html(meet), False))
    jump = ''.join(f'<a href="#{sid}">{title.split(" ", 1)[1].split(" (")[0]}</a>' for sid, title, _, _ in secs)
    content = f'''{STYLE}
<div class="container py-4">
  <div class="crumbs mb-2"><a href="/#schedule">&larr; {esc(season['season'])} schedule</a></div>
  <h2 class="mb-0">{esc(meet['meet'])}</h2>
  <p class="text-muted mb-2">{long_date(meet['date'], meet.get('date_end'))}{' &middot; ' + where if where else ''}</p>
  <div class="meet-nav mb-2">{prev_a}{next_a}</div>
  <nav class="meet-jump">{jump}</nav>
  {''.join(section(*s) for s in secs)}
  <p class="mt-4 small text-muted">{source_line(meet)}</p>
</div>
{JUMP_JS}'''
    out = project_root / 'docs' / 'meets' / f"{meet['slug']}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(create_html_page(f"{meet['meet']} ({short_date(datetime.strptime(meet['date'], '%Y-%m-%d'))})", content))
    return out


def build_all(project_root=REPO, season=None):
    """Write every meet page; return [(meet, records broken)] oldest first."""
    if season is None:
        season = json.loads(max((project_root / 'data').glob('season_*.json')).read_text())
    check_followups(project_root / 'records', season.get('milestone_followups', []))
    history = json.loads((project_root / 'data' / 'class_records_history.json').read_text())
    meets = season_meets(project_root, season)
    by_day = records_at(history, meets)
    built = []
    for m in meets:
        recs = by_day.get(m['date'], [])
        check_meet(m, recs, project_root)
        out = build_meet(m, meets, recs, season, project_root)
        print(f'  ✓ {out.relative_to(project_root)} ({len(recs)} record{"s" if len(recs) != 1 else ""})')
        built.append((m, recs))
    return built


if __name__ == '__main__':
    build_all()
