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
                                   grade_tables, meet_highlights, highlights_html,
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


def long_date(iso):
    d = datetime.strptime(iso, '%Y-%m-%d')
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
    """Records broken at each meet, keyed by meet date (ISO)."""
    by_day = {m['date']: m for m in meets}
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
        out.setdefault(iso, []).append(dict(e, open_prev=open_prev, open_prev_href=link(open_prev),
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


def meet_notes(near, alltime, drops):
    """Plain sentences about the meet's other swims: near-records (with an
    all-time rank folded in), new top-5 all-time swims, the biggest drops."""
    rank = {(a['athlete'], a['event']): a['rank'] for a in alltime}
    said, notes = set(), []
    for n in near[:3]:
        r = rank.get((n['athlete'], n['event']))
        notes.append(f"<strong>{esc(n['athlete'])}</strong> came within {n['gap']:.2f}s of the "
                     f"{esc(n['label'])} {esc(n['event'])} record with <span class=\"time\">"
                     f"{esc(show_time(n['time']))}</span>" + (f", now #{r} all-time." if r else '.'))
        said.add((n['athlete'], n['event']))
    for a in alltime:
        if 1 < a['rank'] <= 5 and (a['athlete'], a['event']) not in said:
            notes.append(f"<strong>{esc(a['athlete'])}</strong>'s <span class=\"time\">{esc(a['time'])}</span> "
                         f"in the {esc(a['event'])} is now #{a['rank']} all-time.")
            said.add((a['athlete'], a['event']))
    for d in drops[:2]:
        ex = ' in an exhibition swim' if d.get('place') == 'Ex.' else ''
        notes.append(f"<strong>{esc(d['athlete'])}</strong> dropped {d['drop']:.2f}s in the "
                     f"{esc(d['event'])}{ex}, from {esc(show_time(d['seed']))} to "
                     f"<span class=\"time\">{esc(show_time(d['time']))}</span>.")
    return notes


def story(meet, recs, season, project_root, near, alltime=(), drops=()):
    """The meet's lead story: headline, one paragraph, and links to the meets it
    continues or is continued by. Derived from the records; the season file adds
    only the facts records cannot know (who is whose brother, the oldest-record
    claim, re-verified at build)."""
    first = lambda n: n.split()[0]  # noqa: E731
    his = lambda r: 'his' if r['gender'] == 'boys' else 'her'  # noqa: E731
    day = datetime.strptime(meet['date'], '%Y-%m-%d')
    opens = [r for r in recs if r['open_prev']]
    sequel = next((r for r in opens if r['open_prev_href'] and r['open_prev']['name'] != r['name']), None)
    links = []
    def also(rest, r0):
        bits = []
        for r in rest:
            if r['open_prev'] and r['open_prev']['name'] == r['name']:
                bits.append(f"lowered {his(r0)} own {esc(r['event'])} record to <span class=\"time\">{esc(r['time'])}</span>")
            elif r['open_prev']:
                bits.append(f"broke the {esc(r['event'])} school record with <span class=\"time\">{esc(r['time'])}</span>")
            else:
                bits.append(f"set a {GRADE_WORD[r['grade']]} {esc(r['event'])} record of <span class=\"time\">{esc(r['time'])}</span>")
        return f" {his(r0).replace('his', 'He').replace('her', 'She')} also {' and '.join(bits)}." if bits else ''
    if sequel:
        r, p = sequel, sequel['open_prev']
        rel = relation_of(season, r)
        oldest, _, _ = oldest_verdict(season, project_root, dict(name=p['name'], event=r['event'], time=p['time']))
        what = 'the oldest record on the boys books' if oldest else f"the {esc(r['event'])} school record"
        under5 = (', the first 500 under five minutes in the team\'s records'
                  if r['event'] == '500 Freestyle' and to_secs(r['time']) < 300 <= to_secs(p['time']) else '')
        rest = [x for x in recs if x is not r and x['name'] == r['name']]
        lede = (f"{gap_words(hist_date(p['date']), day)} after {esc(p['name'])} broke {what} in the "
                f"{esc(r['event'])}, {f'{his(r)} {esc(rel)} ' if rel else ''}<strong>{esc(r['name'])}</strong>, "
                f"a {GRADE_WORD[r['grade']].lower()}, swam <span class=\"time\"><strong>{esc(r['time'])}</strong></span> "
                f"&mdash; {to_secs(p['time']) - to_secs(r['time']):.2f} seconds under {esc(first(p['name']))}'s "
                f"mark{under5}.{also(rest, r)}")
        links.append(f'<a href="{r["open_prev_href"]}">&larr; Part 1: {esc(first(p["name"]))} at the {esc(p["meet"])}</a>')
        return dict(headline=f"First {esc(first(p['name']))}, then {esc(first(r['name']))}", lede=lede, links=links,
                    more=meet_notes(near, alltime, drops))
    if opens:
        r, p = opens[0], opens[0]['open_prev']
        oldest, phrase, runner_up = oldest_verdict(season, project_root, r)
        head = (f"{esc(r['name'])} breaks the oldest {r['gender']} record" if oldest
                else f"{esc(r['name'])} sets the {esc(r['event'])} school record")
        lede = (f"{GRADE_WORD[r['grade']]} <strong>{esc(r['name'])}</strong> swam the {esc(r['event'])} in "
                f"<span class=\"time\"><strong>{esc(r['time'])}</strong></span>, breaking {esc(p['name'])}'s "
                f"{esc(p['time'])} from {esc(p['date'])}"
                + (f" &mdash; <strong>{phrase}</strong>. The next-oldest still standing is the "
                   f"{describe_record(runner_up)}." if oldest else '.')
                + f" It is also the new {GRADE_WORD[r['grade']]} record.")
        b = r['broken_by']
        if b:
            rel = next((f['relation'] for f in season.get('milestone_followups', [])
                        if f['swimmer'] == b['name'] and f['broke_open']['name'] == r['name'] and f.get('relation')), None)
            lede += (f" It stood {gap_words(day, hist_date(b['date'])).lower()}: on {esc(b['date'])} "
                     f"{f'{his(r)} {esc(rel)} ' if rel else ''}{esc(b['name'])} lowered it to "
                     f"<span class=\"time\">{esc(b['time'])}</span>.")
            if r['broken_by_href']:
                links.append(f'<a href="{r["broken_by_href"]}">Part 2: {esc(first(b["name"]))} at the {esc(b["meet"])} &rarr;</a>')
        return dict(headline=head, lede=lede, links=links, more=meet_notes(near, alltime, drops))
    if recs:
        items = ', '.join(f"{esc(r['name'])} ({GRADE_WORD[r['grade']]} {esc(r['event'])}, "
                          f"<span class=\"time\">{esc(r['time'])}</span>)" for r in recs)
        n = len(recs)
        return dict(headline=f"{n} class record{'s' if n != 1 else ''} at the {esc(meet['meet'])}",
                    lede=f"New grade records: {items}.", links=links, more=meet_notes(near, alltime, drops))
    notes = meet_notes(near, alltime, drops)
    if notes:
        if near:
            head = f"{esc(near[0]['athlete'])} {near[0]['gap']:.2f}s from a record"
        elif alltime:
            head = f"{esc(alltime[0]['athlete'])} moves to #{alltime[0]['rank']} all-time"
        else:
            head = f"{esc(drops[0]['athlete'])} drops {drops[0]['drop']:.2f}s"
        return dict(headline=head, lede=' '.join(notes[:2]), links=links, more=notes[2:])
    return None


def record_card(rec, extras):
    who = esc(rec['name'])
    grade = GRADE_WORD[rec['grade']]
    items = []
    if rec['open_prev']:
        p = rec['open_prev']
        where = (f'<a href="{p_href}">{esc(p["meet"])}</a>' if (p_href := rec['open_prev_href'])
                 else esc(p.get('meet', '')))
        items.append(f"<li><strong>School record</strong> &mdash; beat {esc(p['time'])} by "
                     f"{to_secs(p['time']) - to_secs(rec['time']):.2f}s ({esc(p['name'])}, {esc(p['date'])}, {where})</li>")
    p = rec['previous']
    items.append(f"<li><strong>{grade} record</strong> &mdash; beat {esc(p['time'])} by "
                 f"{to_secs(p['time']) - to_secs(rec['time']):.2f}s ({esc(p['name'])}, {esc(p['date'])})</li>")
    if rec['broken_by']:
        b = rec['broken_by']
        where = f'<a href="{rec["broken_by_href"]}">{esc(b["meet"])}</a>' if rec['broken_by_href'] else esc(b['meet'])
        items.append(f"<li>Broken again on {esc(b['date'])} by <strong>{esc(b['name'])}</strong>, "
                     f"<span class=\"time\">{esc(b['time'])}</span>, at {where}</li>")
    extra = ''.join(f'<p class="mb-0 mt-2">{x}</p>' for x in extras)
    return f'''<div class="story-card mb-3">
  <div class="kicker">{esc(rec['gender'].title())} &middot; {esc(rec['event'])}</div>
  <h4 class="mt-1 mb-2">{who} <span class="time">{esc(rec['time'])}</span></h4>
  <ul class="mb-0">{''.join(items)}</ul>{extra}
</div>'''


def place_label(pl):
    """'#3' for a scoring place; 'Ex.' (exhibition) passes through as written."""
    if not pl:
        return ''
    return f'<small class="res-pl">{esc(pl if pl == "Ex." else "#" + pl)}</small>'


def results_tables(meet):
    """Compact per-event lists, folded under one <details>. Tables are not used:
    the site's phone CSS turns every table row into a tall card."""
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
        for r in ind:
            who = f"{esc(r['athlete'])} <small class=\"text-muted\">{esc(r['grade'])}</small>"
            events.setdefault(r['event'], []).append((to_secs(r['time']), r['time'], who, r.get('place')))
        blocks = []
        for ev in sorted(events, key=order):
            rows = ''.join(f'<div class="res-row"><span class="time">{esc(show_time(t))}</span>'
                           f'<span class="res-who">{who}</span>'
                           f'{place_label(pl)}</div>'
                           for _, t, who, pl in sorted(events[ev]))
            blocks.append(f'<div class="res-event"><div class="res-ev">{esc(ev)}</div>{rows}</div>')
        out.append(f'<h5 class="mt-3">{g.title()} <small class="text-muted">{len(ind)} swims, '
                   f'{len(rel)} relays</small></h5>' + ''.join(blocks))
    n = len(meet['individual']) + len(meet['relay'])
    return (f'<details class="meet-results"><summary><strong>All Hawks results</strong> '
            f'<span class="text-muted">({n})</span></summary>' + '\n'.join(out) + '</details>')


def source_line(meet):
    s = meet['source']
    if s['kind'] == 'hytek-sdif-cl2':
        return f"Results from the meet's official Hy-Tek results file ({esc(s['file'])})."
    return (f'Results from <a href="{esc(s["url"])}" target="_blank">MaxPreps</a>. MaxPreps does not list '
            f'places, entry times or relay swimmers.')


STYLE = '''<style>
.story-card{border-left:4px solid #2d6a35;background:#f4f9f4;border-radius:6px;padding:12px 14px}
.story-lead{background:#2d6a35;color:#fff;border-radius:8px;padding:14px 16px}
.story-lead a{color:#d8f0d8}
.story-lead .time{color:#fff}
.kicker{font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;color:#2d6a35;font-weight:700}
.meet-nav{display:flex;justify-content:space-between;gap:8px;font-size:.9rem}
.meet-nav a,.crumbs a{text-decoration:none}
.meet-results summary{font-size:1.15rem;padding:.5rem 0;cursor:pointer}
.res-event{margin:.6rem 0}.res-ev{font-weight:700;font-size:.9rem;color:#2d6a35;border-bottom:1px solid #dee2e6}
.res-row{display:flex;gap:.6rem;align-items:baseline;padding:.15rem 0;font-size:.95rem}
.res-row .time{min-width:4.5rem}.res-who{flex:1}.res-pl{color:#888}
</style>'''


def build_meet(meet, meets, recs, season, project_root):
    from generate_website import create_html_page
    sched = {m['date_start']: m for m in season['schedule']['meets']}.get(meet['date'], {})
    i = meets.index(meet)
    prev_a = (f'<a href="{meets[i - 1]["href"]}">&lsaquo; {esc(meets[i - 1]["meet"])}</a>' if i > 0 else '<span></span>')
    next_a = (f'<a href="{meets[i + 1]["href"]}">{esc(meets[i + 1]["meet"])} &rsaquo;</a>' if i + 1 < len(meets) else '<span></span>')
    where = ' &middot; '.join(x for x in (esc(sched.get('venue', '')),) if x)
    records = ''
    if recs:
        records = ('<h3 class="mt-4">&#127942; Records broken</h3>\n' +
                   '\n'.join(record_card(r, []) for r in recs))
    near, alltime, drops = meet_highlights(project_root, meet)
    _, hl = highlights_html(meet, near, alltime, drops)
    st = story(meet, recs, season, project_root, near, alltime, drops)
    meet['story'] = st
    lead = ''
    if st:
        lead = (f'<div class="story-lead mb-3"><h3 class="mb-2">{st["headline"]}</h3>'
                f'<p class="mb-2">{st["lede"]}</p>'
                + (f'<p class="mb-2">Also at this meet: {" ".join(st["more"])}</p>' if st['more'] else '')
                + ''.join(f'<div class="small">{lk}</div>' for lk in st['links']) + '</div>')
    hl_block = f'<h3 class="mt-4">&#9889; Highlights</h3>\n{hl}' if hl else ''
    content = f'''{STYLE}
<div class="container py-4">
  <div class="crumbs mb-2"><a href="/#schedule">&larr; {esc(season['season'])} schedule</a></div>
  <h2 class="mb-0">{esc(meet['meet'])}</h2>
  <p class="text-muted mb-2">{long_date(meet['date'])}{' &middot; ' + where if where else ''}</p>
  <div class="meet-nav mb-3">{prev_a}{next_a}</div>
  {lead}
  {records}
  {hl_block}
  <div class="mt-4">{results_tables(meet)}</div>
  <p class="mt-4 small text-muted">{source_line(meet)}</p>
</div>'''
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
