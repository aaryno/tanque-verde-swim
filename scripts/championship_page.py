#!/usr/bin/env python3
"""
The State Championship meet page: a championship program first, a results
explorer underneath. Called by generate_meet_pages.build_meet for any meet
is_championship() accepts; every other meet keeps the regular meet page.

Aaryn, 2026-11-08: "The State Championship page should feel like a beautiful
digital championship program. A family should be proud to share it, every
swimmer should have a place in it, and serious swimming fans should still be
able to explore the complete results."

Sections, each shown only when the meet has something for it:
  hero          team places (with last year's), State titles, record honors,
                season bests, date and venue
  moments       every State title (individual and relay, gold), then 2nd and
                3rd places (silver, bronze); relays with all four swimmers
  team story    one short block per team, then the relays
  records       every record honor: new time, the time it beat, category, round
  breakthroughs biggest season-best drops, new all-time Top 10 places, finals
  hawks         every Tanque Verde swimmer in the results, alphabetical, each
                with their best swim and an expandable list of every swim
  seniors       the seniors' last State meet, reconciled with the senior page
  results       every timed swim by gender and event, finals and prelims apart,
                plus the swims the results list without a time (DQ, NS)

Everything comes from the meet file, the records and the relay lists. Words
like "silver" are colours here, not claims about medals.
"""
import json
import re
from datetime import datetime

from generate_landing_page import esc, to_secs, show_time

GRADE_WORD = {'Fr.': 'Freshman', 'So.': 'Sophomore', 'Jr.': 'Junior', 'Sr.': 'Senior',
              'FR': 'Freshman', 'SO': 'Sophomore', 'JR': 'Junior', 'SR': 'Senior'}
NUM = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
MEDLEY_LEGS = ['Back', 'Breast', 'Fly', 'Free']
EVENT_ORDER = ['200 Medley Relay', '200 Freestyle', '200 Individual Medley', '50 Freestyle', '100 Butterfly',
               '100 Freestyle', '500 Freestyle', '200 Free Relay', '100 Backstroke', '100 Breaststroke',
               '400 Free Relay']

ICONS = {
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    "medal": '<circle cx="12" cy="15" r="5"/><path d="M8.5 11.5 6 3h4l2 5 2-5h4l-2.5 8.5"/>',
    "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "relay": '<circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="7" r="2.5"/><path d="M3 20c0-3 2-5 4-5s4 2 4 5M13 20c0-3 2-5 4-5s4 2 4 5"/>',
    "cap": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5"/><path d="M22 9v6"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.5" cy="6" r="1"/><circle cx="3.5" cy="12" r="1"/><circle cx="3.5" cy="18" r="1"/>',
    "team": '<circle cx="12" cy="7" r="3"/><path d="M5 21c0-4 3-7 7-7s7 3 7 7"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
}


def icon(name, cls="sr-ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def ordinal(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def and_list(xs):
    xs = list(xs)
    if not xs:
        return ''
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def short_event(e):
    return (e.replace('Freestyle', 'Free').replace('Backstroke', 'Back').replace('Breaststroke', 'Breast')
             .replace('Butterfly', 'Fly').replace('Individual Medley', 'IM'))


def word(n):
    return NUM[n] if 0 <= n < len(NUM) else str(n)


def last_key(name):
    return (name.split()[-1].lower(), name.lower())


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def place_int(r):
    p = str(r.get('place') or '')
    return int(p) if p.isdigit() else None


def medal_class(place):
    return {1: 'gold', 2: 'silver', 3: 'bronze'}.get(place, '')


# ---------------------------------------------------------------- data

def relay_list(project_root, gender, event):
    """All rows of an event's all-time relay list: [(time, names, date, meet)]."""
    md = (project_root / 'records' / f"relay-records-{gender}.md").read_text().split('\n')
    try:
        i = md.index(f"## {event}")
    except ValueError:
        return []
    rows = []
    for line in md[i + 4:]:
        if not line.startswith('|'):
            break
        c = [x.strip().strip('*').strip() for x in line.strip().strip('|').split('|')]
        rows.append(c[1:5])
    return rows


def relay_rank(project_root, r):
    """(rank on the all-time list, the list's #1 row, the row it pushed down) for this swim, or (None, ...)."""
    rows = relay_list(project_root, r['gender'], r['event'])
    day = datetime.strptime(r['date'], '%m/%d/%Y').strftime('%b %d, %Y')
    for k, row in enumerate(rows, start=1):
        if to_secs(row[0]) == to_secs(r['time']) and row[2] == day:
            return k, rows[0], (rows[1] if k == 1 and len(rows) > 1 else None)
    return None, (rows[0] if rows else None), None


def collect(meet, recs, rrecs, sb, alltime, project_root):
    """Everything the page says, derived once."""
    ind, rel = meet['individual'], meet['relay']
    exc = meet.get('excluded', [])
    grade = {}
    for r in ind:
        grade.setdefault(r['athlete'], r['grade'])
    for x in exc:
        for n, g in zip(x.get('participants', []), x.get('grades', [])):
            grade.setdefault(n, g)
    gender = {r['athlete']: r['gender'] for r in ind}
    for r in rel + [x for x in exc if x['kind'] == 'relay']:
        for n in r['participants']:
            gender.setdefault(n, r['gender'])
    for x in exc:
        if x['kind'] == 'individual':
            gender.setdefault(x['athlete'], x['gender'])
    sb_by = {(r['athlete'], r['event']): r for r in sb}
    at_by = {(a['athlete'], a['event']): a for a in alltime}
    rec_by = {}
    for r in recs:
        rec_by.setdefault((r['name'], r['event']), []).append(r)
    rrec_by = {(r['gender'], r['event']): r for r in rrecs}
    relays = []
    for r in rel:
        rank, top, pushed = relay_rank(project_root, r)
        relays.append(dict(r, rank=rank, top=top, rec=rrec_by.get((r['gender'], r['event']))))
    finals = [r for r in ind if r.get('round', 'Final') == 'Final' and place_int(r)]
    return dict(ind=ind, relays=relays, exc=exc, grade=grade, gender=gender, sb=sb, sb_by=sb_by, at_by=at_by,
                rec_by=rec_by, recs=recs, rrecs=rrecs, finals=finals, alltime=alltime)


def rec_chips(d, athlete, event, time):
    """Record honors held by this exact swim: the Open record and the class record count separately."""
    out = []
    for r in d['rec_by'].get((athlete, event), []):
        if to_secs(r['time']) != to_secs(time):
            continue
        if r['open_prev']:
            out.append('<span class="sr-chip sr-gold">School record</span>')
        out.append(f'<span class="sr-chip">{GRADE_WORD[r["grade"]]} record</span>')
    return out


def honors_count(d):
    n = sum(1 + bool(r['open_prev']) for r in d['recs']) + len(d['rrecs'])
    return n, len(d['recs']) + len(d['rrecs'])


# ---------------------------------------------------------------- sections

def hero(meet, d, prior, prior_year, when, venue):
    ts = meet.get('team_scores') or {}
    teams = []
    for g in ('boys', 'girls'):
        x = ts.get(g)
        if not x:
            continue
        p = prior.get(g)
        sub = ''
        if p:
            if p['place'] == 1:
                sub = f'{prior_year} State champions'
            elif x['place'] < p['place']:
                sub = f'Up from {ordinal(p["place"])} in {prior_year}'
            elif x['place'] == p['place']:
                sub = f'{ordinal(p["place"])} in {prior_year} too'
            else:
                sub = f'{ordinal(p["place"])} in {prior_year}'
        teams.append(f'<div class="ch-team"><span class="ch-team-g">{g.title()}</span>'
                     f'<span class="ch-team-p">{ordinal(x["place"])}</span>'
                     f'<span class="ch-team-of">of {x["teams"]} teams &middot; {x["points"]:g} points</span>'
                     + (f'<span class="ch-team-s">{esc(sub)}</span>' if sub else '') + '</div>')
    titles = len([r for r in d['finals'] if place_int(r) == 1]) + len([r for r in d['relays'] if place_int(r) == 1])
    honors, swims = honors_count(d)
    stats = []
    if titles:
        stats.append((titles, f'State title{"s" if titles != 1 else ""}'))
    if honors:
        stats.append((honors, f'record honor{"s" if honors != 1 else ""} from {word(swims)} swim{"s" if swims != 1 else ""}'))
    if d['sb']:
        stats.append((len(d['sb']), f'season-best swim{"s" if len(d["sb"]) != 1 else ""}'))
    stat_html = ''.join(f'<div class="sr-stat"><span class="sr-stat-n">{n}</span><span class="sr-stat-l">{esc(l)}</span></div>'
                        for n, l in stats)
    title = 'A Championship Weekend for the Hawks'
    return f'''<section class="sr-hero ch-hero">
  <div class="container">
    <img src="/images/hawk-logo.svg" alt="" class="sr-hero-logo">
    <div class="sr-hero-eyebrow">{icon("medal")}{esc(meet["meet"])}</div>
    <h1 class="sr-hero-title">{title}</h1>
    <p class="ch-when">{when}{f' &middot; <span class="ch-venue">{icon("pin")}{esc(venue)}</span>' if venue else ''}</p>
    {f'<div class="ch-teams">{"".join(teams)}</div>' if teams else ''}
    {f'<div class="sr-stats">{stat_html}</div>' if stats else ''}
  </div>
</section>'''


def relay_lineup(r):
    legs = MEDLEY_LEGS if 'Medley' in r['event'] else [f'Leg {i}' for i in range(1, 5)]
    return '<ol class="ch-lineup">' + ''.join(
        f'<li><span class="ch-leg">{esc(l)}</span>{esc(n)}</li>' for l, n in zip(legs, r['participants'])) + '</ol>'


def relay_standing(r):
    """'School record — was 1:41.80 (2025)' or '#5 all-time'."""
    if r['rec']:
        p = r['rec']['previous']
        was = f' &middot; was {esc(p["time"])} ({esc(p["date"][-4:])})' if p else ''
        return f'<span class="sr-chip sr-gold">School record</span><span class="ch-was">{was.replace(" &middot; ", "")}</span>'
    if r['rank']:
        return f'<span class="sr-chip">#{r["rank"]} all-time</span>'
    return ''


def moments(d):
    """Every title, then 2nd and 3rd places. Individual swims of one swimmer sit side by side."""
    LABEL = {1: 'State champion', 2: 'State runner-up', 3: '3rd at State'}
    cards = []
    for pl in (1, 2, 3):
        inds = sorted((r for r in d['finals'] if place_int(r) == pl), key=lambda r: (last_key(r['athlete']), r['event']))
        rels = [r for r in d['relays'] if place_int(r) == pl]
        for r in inds:
            prelim = next((x for x in d['ind'] if x['athlete'] == r['athlete'] and x['event'] == r['event']
                           and x.get('round') == 'Prelim'), None)
            pre = (f'<span class="ch-pre">Prelims: {ordinal(prelim["place"])} in {esc(show_time(prelim["time"]))}</span>'
                   if prelim and place_int(prelim) else '')
            chips = ''.join(rec_chips(d, r['athlete'], r['event'], r['time']))
            cards.append((pl, 'ind', f'''<article class="ch-m ch-{medal_class(pl)} ch-m-ind">
  <div class="ch-m-l">{icon("medal")}{LABEL[pl]}</div>
  <div class="ch-m-ev">{esc(r["gender"].title())} {esc(short_event(r["event"]))}</div>
  <div class="ch-m-t">{esc(show_time(r["time"]))}</div>
  <div class="ch-m-who"><strong>{esc(r["athlete"])}</strong> <span>{esc(GRADE_WORD.get(r["grade"], ""))}</span></div>
  {f'<div class="ch-m-chips">{chips}</div>' if chips else ''}{pre}
</article>'''))
        for r in rels:
            cards.append((pl, 'rel', f'''<article class="ch-m ch-{medal_class(pl)} ch-m-rel">
  <div class="ch-m-l">{icon("medal")}{LABEL[pl]}</div>
  <div class="ch-m-ev">{esc(r["gender"].title())} {esc(r["event"])}</div>
  <div class="ch-m-t">{esc(show_time(r["time"]))}</div>
  {relay_lineup(r)}
  <div class="ch-m-chips">{relay_standing(r)}</div>
</article>'''))
    if not cards:
        return ''
    # group: each place's individual cards in a pair-friendly row, relay cards beside them
    html = []
    for pl in (1, 2, 3):
        mine = [c for c in cards if c[0] == pl]
        if not mine:
            continue
        ind = ''.join(h for _, k, h in mine if k == 'ind')
        rel = ''.join(h for _, k, h in mine if k == 'rel')
        html.append(f'<div class="ch-moments">{f"<div class=ch-m-pair>{ind}</div>" if ind else ""}{rel}</div>')
    n1 = sum(1 for c in cards if c[0] == 1)
    intro = (f'{word(n1).capitalize()} State title{"s" if n1 != 1 else ""}' if n1 else '') + \
            (', then the swims that reached the podium.' if len(cards) > n1 else '.')
    return f'<p class="ch-intro">{intro}</p>' + ''.join(html)


def team_story(meet, d, prior, prior_year):
    ts = meet.get('team_scores') or {}
    blocks = []
    for g in ('girls', 'boys'):
        x = ts.get(g)
        if not x:
            continue
        p = prior.get(g)
        titles = [r for r in d['finals'] if r['gender'] == g and place_int(r) == 1] + \
                 [r for r in d['relays'] if r['gender'] == g and place_int(r) == 1]
        top = x.get('top', [])
        ahead = x['points'] - top[x['place']][1] if x['place'] < len(top) else None
        behind = top[x['place'] - 2][1] - x['points'] if x['place'] >= 2 and len(top) >= x['place'] - 1 else None
        if p and p['place'] == 1:
            head = f"The {g}&rsquo; championship tradition"
            s = (f"Defending {prior_year} State champions, the {g} finished <strong>{ordinal(x['place'])}</strong> of "
                 f"{x['teams']} teams with {x['points']:g} points")
        elif p and x['place'] < p['place']:
            head = f"The {g}&rsquo; climb"
            s = (f"From {ordinal(p['place'])} in {prior_year}, the {g} climbed to <strong>{ordinal(x['place'])}</strong> "
                 f"of {x['teams']} teams with {x['points']:g} points")
        else:
            head = f"The {g}"
            s = f"The {g} finished <strong>{ordinal(x['place'])}</strong> of {x['teams']} teams with {x['points']:g} points"
            if p:
                s += f", after {ordinal(p['place'])} in {prior_year}"
        if titles:
            s += f" and {word(len(titles))} event title{'s' if len(titles) != 1 else ''}"
        s += '.'
        if ahead is not None and 0 < ahead <= 5:
            s += f" They finished only {ahead:g} point{'s' if ahead != 1 else ''} ahead of {ordinal(x['place'] + 1)}."
        elif behind is not None and 0 < behind <= 5:
            s += f" They were {behind:g} point{'s' if behind != 1 else ''} from {ordinal(x['place'] - 1)}."
        finals = len({(r['athlete'], r['event']) for r in d['finals'] if r['gender'] == g})
        if finals:
            s += f" {word(finals).capitalize()} individual swim{'s' if finals != 1 else ''} reached a final."
        blocks.append((head, s))
    rel = []
    for r in sorted(d['relays'], key=lambda r: (not r['rec'], place_int(r) or 99, r['rank'] or 99)):
        if not (r['rec'] or (place_int(r) or 99) <= 3 or (r['rank'] or 99) <= 3):
            continue
        what = (f"the school-record {r['gender']} {esc(r['event'])}" if r['rec'] else f"the {r['gender']} {esc(r['event'])}")
        bits = [f"{ordinal(place_int(r))} at State" if place_int(r) else '', f"{esc(show_time(r['time']))}"]
        if not r['rec'] and r['rank']:
            bits.append(f"#{r['rank']} in team history")
        rel.append(f"{what} ({', '.join(b for b in bits if b)})")
    if rel:
        s = f"{rel[0][0].upper()}{rel[0][1:]}" + (f"; {'; '.join(rel[1:-1])}" if len(rel) > 2 else '') + \
            (f"; and {rel[-1]}" if len(rel) > 1 else '') + '.'
        blocks.append(("Relay excellence", s))
    if not blocks:
        return ''
    return '<div class="ch-story">' + ''.join(
        f'<article class="ch-story-b"><h3>{h}</h3><p>{s}</p></article>' for h, s in blocks) + '</div>'


def records_section(d):
    rows = []
    for r in d['recs']:
        sw = next((x for x in d['ind'] if x['athlete'] == r['name'] and x['event'] == r['event']
                   and to_secs(x['time']) == to_secs(r['time'])), {})
        rnd = 'Finals' if sw.get('round', 'Final') == 'Final' else 'Prelims'
        honors = []
        if r['open_prev']:
            p = r['open_prev']
            honors.append(('School record', 'sr-gold', p))
        honors.append((f"{GRADE_WORD[r['grade']]} record", '', r['previous']))
        rows.append((0 if r['open_prev'] else 1, r['name'], short_event(r['event']), r['time'], rnd, honors,
                     GRADE_WORD[r['grade']], r['name']))
    for r in d['rrecs']:
        p = r['previous']
        prev = dict(time=p['time'], name=p['names'], date=p['date']) if p else None
        rows.append((0, ', '.join(r['participants']), f"{r['gender'].title()} {r['event']}", r['time'], 'Final',
                     [('School record', 'sr-gold', prev)], '', None))
    if not rows:
        return ''
    out = []
    def was(p, me):
        if not p:
            return ''
        if me and p['name'] == me:
            return f'<span class="ch-was">lowered own {esc(p["time"])} from {esc(p["date"][:3])} {esc(p["date"][-4:])}</span>'
        return f'<span class="ch-was">was {esc(p["time"])} &middot; {esc(p["name"])}, {esc(p["date"][-4:])}</span>'
    for _, who, ev, tm, rnd, honors, sub, me in sorted(rows, key=lambda x: (x[0], x[2])):
        hl = ''.join(f'<li><span class="sr-chip {cls}">{esc(lab)}</span>{was(p, me)}</li>' for lab, cls, p in honors)
        rl = 'Finals' if rnd.startswith('Final') else 'Prelims'
        out.append(f'''<article class="ch-rec">
  <div class="ch-rec-h"><span class="ch-rec-t">{esc(show_time(tm))}</span><span class="ch-rec-ev">{esc(ev)}</span></div>
  <div class="ch-rec-who">{f"<strong>{esc(who)}</strong> <span>{esc(sub)}</span>" if me else f"<span class=ch-rec-team>{esc(who)}</span>"}
  <span class="ch-rnd">{rl}</span></div>
  <ul class="ch-rec-l">{hl}</ul>
</article>''')
    honors, swims = honors_count(d)
    return (f'<p class="ch-intro">{word(honors).capitalize()} record honors from {word(swims)} swims. '
            f'A school record and a class record set by the same swim are two honors, and both count.</p>'
            f'<div class="ch-recs">{"".join(out)}</div>')


def breakthroughs(d):
    parts = []
    drops = sorted(d['sb'], key=lambda r: -r['drop'])
    if drops:
        top = drops[0]
        feat = f'''<article class="ch-feat">
  <div class="ch-feat-n">&minus;{top["drop"]:.2f}<small>s</small></div>
  <div><div class="ch-feat-l">Biggest season-best drop</div>
  <div class="ch-feat-w"><strong>{esc(top["athlete"])}</strong> &middot; {esc(short_event(top["event"]))} in {esc(show_time(top["time"]))}</div>
  <div class="ch-feat-s">faster than {esc(top["athlete"].split()[0])}&rsquo;s best earlier this season</div></div>
</article>'''
        rest = [r for r in drops[1:] if r['drop'] >= 1.0][:6]
        lis = ''.join(f'<li><span class="ch-drop">&minus;{r["drop"]:.2f}s</span> <strong>{esc(r["athlete"])}</strong> '
                      f'{esc(short_event(r["event"]))} <span class="sr-t">{esc(show_time(r["time"]))}</span></li>' for r in rest)
        parts.append(f'<div class="ch-bt"><h3 class="ch-h3">{icon("trend")}Season bests</h3>{feat}'
                     + (f'<ul class="ch-l">{lis}</ul>' if lis else '')
                     + f'<p class="ch-note">{word(len(drops)).capitalize()} swims at State were season bests; every one is marked SB in the results below.</p></div>')
    at = []
    for a in d['alltime']:
        b = a.get('before')
        if a['rank'] == 1:
            continue  # a #1 is a school record, told above
        if b is False:
            at.append((a['rank'], a, 'new to the list'))
        elif b and b[0] > a['rank'] and to_secs(b[1]) > to_secs(a['time']):
            at.append((a['rank'], a, f'up from #{b[0]} (was {show_time(b[1])})'))
    if at:
        lis = ''.join(f'<li><span class="sr-chip">#{a["rank"]} all-time</span> <strong>{esc(a["athlete"])}</strong> '
                      f'{esc(a["gender"])} {esc(short_event(a["event"]))} <span class="sr-t">{esc(show_time(a["time"]))}</span>'
                      f'<span class="ch-sub">{esc(msg)}</span></li>' for _, a, msg in sorted(at, key=lambda x: x[0]))
        parts.append(f'<div class="ch-bt"><h3 class="ch-h3">{icon("star")}Climbing the all-time Top 10</h3><ul class="ch-l">{lis}</ul></div>')
    fin = sorted((r for r in d['finals'] if 4 <= place_int(r) <= 8), key=lambda r: (place_int(r), r['event']))
    if fin:
        lis = ''.join(f'<li><span class="sr-chip">{ordinal(place_int(r))}</span> <strong>{esc(r["athlete"])}</strong> '
                      f'{esc(short_event(r["event"]))} <span class="sr-t">{esc(show_time(r["time"]))}</span></li>' for r in fin)
        parts.append(f'<div class="ch-bt"><h3 class="ch-h3">{icon("medal")}Top-8 finals</h3><ul class="ch-l">{lis}</ul></div>')
    return f'<div class="ch-bts">{"".join(parts)}</div>' if parts else ''


def swimmer_facts(d, who):
    """Every swim of one swimmer at the meet, and the headline for their card."""
    ind = [r for r in d['ind'] if r['athlete'] == who]
    rel = [r for r in d['relays'] if who in r['participants']]
    exc = [x for x in d['exc'] if (x['kind'] == 'relay' and who in x['participants']) or x.get('athlete') == who]
    titles = [short_event(r['event']) for r in ind if r.get('round', 'Final') == 'Final' and place_int(r) == 1] + \
             [short_event(r['event']) for r in rel if place_int(r) == 1]
    recs = [(r, rec_chips(d, who, r['event'], r['time'])) for r in ind]
    recs = [(r, c) for r, c in recs if c]
    fins = sorted((r for r in ind if r.get('round', 'Final') == 'Final' and place_int(r)), key=place_int)
    rels = sorted((r for r in rel if place_int(r)), key=place_int)
    sbs = sorted((d['sb_by'][(who, r['event'])] for r in ind if (who, r['event']) in d['sb_by']), key=lambda r: -r['drop'])
    sbs = list({r['event']: r for r in sbs}.values())
    if titles:
        head, gold, detail = f'State champion', 'gold', and_list(titles)
    elif recs:
        r, c = recs[0]
        head, gold, detail = ('School record' if 'School' in c[0] else re.sub('<[^>]+>', '', c[0])), 'gold', \
            f'{short_event(r["event"])} {show_time(r["time"])}'
    elif fins or rels:
        best = min(fins + rels, key=place_int)
        what = short_event(best['event'])
        head, gold, detail = (f'{ordinal(place_int(best))} at State', medal_class(place_int(best)),
                              f'{what} {show_time(best["time"])}')
    elif sbs:
        head, gold, detail = f'Season best &minus;{sbs[0]["drop"]:.2f}s', '', f'{short_event(sbs[0]["event"])} {show_time(sbs[0]["time"])}'
    elif ind:
        best = min(ind, key=lambda r: place_int(r) or 999)
        head, gold, detail = ('Swam at State', '', f'{short_event(best["event"])} {show_time(best["time"])}'
                              + (f' &middot; {ordinal(place_int(best))} in prelims' if place_int(best) and best.get('round') == 'Prelim' else ''))
    elif exc:
        head, gold, detail = 'Swam at State', '', f'{exc[0]["event"]} ({exc[0]["result"]})'
    else:
        head, gold, detail = 'Swam at State', '', ''
    return dict(ind=ind, rel=rel, exc=exc, head=head, gold=gold, detail=detail, sbs=sbs, recs=recs,
                n=len(ind) + len(rel) + len(exc))


def swim_rows(d, f, who):
    out = []
    for r in sorted(f['ind'], key=lambda r: (EVENT_ORDER.index(r['event']) if r['event'] in EVENT_ORDER else 99,
                                             r.get('round') != 'Prelim')):
        rnd = 'Final' if r.get('round', 'Final') == 'Final' else 'Prelims'
        pl = place_int(r)
        chips = rec_chips(d, who, r['event'], r['time'])
        sb = d['sb_by'].get((who, r['event']))
        if sb and to_secs(sb['time']) == to_secs(r['time']):
            chips.append(f'<span class="ch-sb">SB &minus;{sb["drop"]:.2f}</span>')
        out.append(f'<li><span class="ch-sw-ev">{esc(short_event(r["event"]))} <small>{rnd}</small></span>'
                   f'<span class="ch-sw-pl">{ordinal(pl) if pl else ""}</span><span class="sr-t">{esc(show_time(r["time"]))}</span>'
                   f'{"".join(chips)}</li>')
    for r in f['rel']:
        mates = [n for n in r['participants'] if n != who]
        out.append(f'<li><span class="ch-sw-ev">{esc(short_event(r["event"]))} <small>Final</small></span>'
                   f'<span class="ch-sw-pl">{ordinal(place_int(r)) if place_int(r) else ""}</span>'
                   f'<span class="sr-t">{esc(show_time(r["time"]))}</span>'
                   f'<span class="ch-sub">with {esc(and_list(mates))}</span></li>')
    for x in f['exc']:
        mates = [n for n in x.get('participants', []) if n != who]
        out.append(f'<li><span class="ch-sw-ev">{esc(short_event(x["event"]))}</span><span class="ch-sw-pl"></span>'
                   f'<span class="sr-chip sr-quiet">{esc(x["result"])}</span>'
                   + (f'<span class="ch-sub">with {esc(and_list(mates))}</span>' if mates else '') + '</li>')
    return '<ul class="ch-sw">' + ''.join(out) + '</ul>'


def hawks(d, senior_href):
    people = sorted(d['gender'], key=last_key)
    out = []
    for g in ('girls', 'boys'):
        cards = []
        for who in [p for p in people if d['gender'][p] == g]:
            f = swimmer_facts(d, who)
            gr = d['grade'].get(who, '')
            cap = (f'<a class="ch-cap" href="{senior_href(who)}" title="Senior">{icon("cap")}</a>' if gr == 'Sr.' and senior_href(who)
                   else (f'<span class="ch-cap">{icon("cap")}</span>' if gr == 'Sr.' else ''))
            cards.append(f'''<details class="ch-hawk{f" ch-hawk-{f['gold']}" if f['gold'] else ''}" id="hawk-{slug(who)}">
  <summary><span class="ch-hawk-n">{esc(who)}{cap}<a class="ch-hawk-link" href="#hawk-{slug(who)}" aria-label="Link to {esc(who)}">{icon("link")}</a></span><span class="ch-hawk-g">{esc(GRADE_WORD.get(gr, ''))}</span>
  <span class="ch-hawk-h">{f['head']}</span><span class="ch-hawk-d">{esc(f['detail']) if '&' not in f['detail'] else f['detail']}</span>
  <span class="ch-hawk-more">{f['n']} swim{'s' if f['n'] != 1 else ''}</span></summary>
  {swim_rows(d, f, who)}
</details>''')
        if cards:
            out.append(f'<h3 class="ch-h3">{g.title()} <span class="sr-count">{len(cards)}</span></h3><div class="ch-hawks">{"".join(cards)}</div>')
    n = len(people)
    timed = len({r['athlete'] for r in d['ind']} | {p for r in d['relays'] for p in r['participants']})
    note = f'{word(n).capitalize()} Tanque Verde swimmers are in the State results'
    if timed != n:
        only = sorted(set(people) - ({r['athlete'] for r in d['ind']} | {p for r in d['relays'] for p in r['participants']}), key=last_key)
        note += f'; {and_list(esc(x) for x in only)} swam only on a relay the results list as disqualified'
    return f'<p class="ch-intro">{note}. Tap a name for every swim.</p>' + ''.join(out)


def seniors(d, career, class_year, href):
    srs = sorted((w for w, g in d['grade'].items() if g == 'Sr.'), key=last_key)
    if not srs:
        return ''
    lis = []
    for w in srs:
        f = swimmer_facts(d, w)
        link = href(w)
        name = f'<a href="{link}">{esc(w)}</a>' if link else esc(w)
        lis.append(f'<li><span class="ch-sen-n">{icon("cap")}{name}</span>'
                   f'<span class="ch-sen-h">{f["head"]}{": " + f["detail"] if f["detail"] else ""}</span></li>')
    note = (f'{word(len(srs)).capitalize()} seniors swam at their last high-school State Championship.')
    extra = sorted(set(career) - set(srs), key=last_key)
    if career and extra:
        note += (f' The Class of {class_year} page counts {word(len(career))} seniors who swam at State during their careers: '
                 + and_list(f'{esc(w)} (State {and_list(career[w])})' for w in extra)
                 + (' swam at an earlier State meet' if len(extra) == 1 else ' swam at earlier State meets') + '.')
    page = f'/seniors/class-of-{class_year}.html'
    return (f'<div class="ch-seniors"><p class="ch-intro">{note}</p><ul class="ch-sen">{"".join(lis)}</ul>'
            f'<p><a class="ch-btn" href="{page}">{icon("cap")}Celebrate the Class of {class_year}</a></p></div>')


def results(d, meet):
    ev_order = lambda e: EVENT_ORDER.index(e) if e in EVENT_ORDER else 99  # noqa: E731
    blocks, idx, marked = [], [], set()
    for g in ('girls', 'boys'):
        evs = sorted({r['event'] for r in d['ind'] + d['relays'] + d['exc'] if r['gender'] == g}, key=ev_order)
        if not evs:
            continue
        idx.append(f'<a href="#res-{g}">{g.title()}</a>')
        eb = []
        for ev in evs:
            rows = []
            for rnd, label in (('Final', 'Final'), ('Prelim', 'Prelims')):
                rs = [r for r in d['ind'] if r['gender'] == g and r['event'] == ev and r.get('round', 'Final') == rnd]
                rs += [r for r in d['relays'] if r['gender'] == g and r['event'] == ev and rnd == 'Final']
                if not rs:
                    continue
                lis = []
                for r in sorted(rs, key=lambda r: (place_int(r) or 999, to_secs(r['time']))):
                    pl = place_int(r)
                    if 'participants' in r:
                        who = f'<span class="ch-r-who">{esc(", ".join(r["participants"]))}</span>'
                        chips = relay_standing(r)
                    else:
                        who = f'<span class="ch-r-who"><strong>{esc(r["athlete"])}</strong> <small>{esc(r["grade"])}</small></span>'
                        k = (r['athlete'], r['event'], to_secs(r['time']))
                        cs = [] if k in marked else rec_chips(d, r['athlete'], r['event'], r['time'])
                        once = k not in marked
                        marked.add(k)
                        sb = d['sb_by'].get((r['athlete'], r['event']))
                        if once and sb and to_secs(sb['time']) == to_secs(r['time']):
                            cs.append(f'<span class="ch-sb">SB &minus;{sb["drop"]:.2f}</span>')
                        a = d['at_by'].get((r['athlete'], r['event']))
                        if once and a and to_secs(a['time']) == to_secs(r['time']) and a['rank'] > 1:
                            cs.append(f'<span class="sr-chip">#{a["rank"]} all-time</span>')
                        chips = ''.join(cs)
                    lis.append(f'<li class="{"ch-" + medal_class(pl) if label == "Final" and pl and pl <= 3 else ""}">'
                               f'<span class="ch-r-pl">{ordinal(pl) if pl else "&ndash;"}</span>'
                               f'<span class="ch-r-t">{esc(show_time(r["time"]))}</span>{who}'
                               f'{f"<span class=ch-r-c>{chips}</span>" if chips else ""}</li>')
                rows.append(f'<div class="ch-r-round"><span class="ch-r-rl">{label}</span><ul>{"".join(lis)}</ul></div>')
            for x in (x for x in d['exc'] if x['gender'] == g and x['event'] == ev):
                who = ', '.join(x['participants']) if x['kind'] == 'relay' else x['athlete']
                rows.append(f'<div class="ch-r-round ch-r-exc"><span class="ch-r-rl">No time</span><ul><li>'
                            f'<span class="ch-r-pl">{esc(x["result"])}</span><span class="ch-r-t"></span>'
                            f'<span class="ch-r-who">{esc(who)}</span></li></ul></div>')
            eb.append(f'<details class="ch-ev" open><summary>{esc(ev)}</summary>{"".join(rows)}</details>')
        blocks.append(f'<section class="ch-res-g" id="res-{g}"><h3 class="ch-h3">{g.title()}</h3>{"".join(eb)}</section>')
    n = len(d['ind']) + len(d['relays'])
    nx = len(d['exc'])
    lead = (f'All {n} timed Tanque Verde swims'
            + (f', plus {word(nx)} listed without a time ({and_list(sorted({x["result"] for x in d["exc"]}))})' if nx else '')
            + '. Places are official: a final&rsquo;s place is the finish, a prelim place is the qualifying rank.')
    return (f'<p class="ch-intro">{lead}</p><nav class="ch-res-idx">{"".join(idx)}</nav>'
            f'<div class="ch-res">{"".join(blocks)}</div>')


NAV_JS = """<script>
(function(){
  function openFor(h){var t=h&&h.length>1&&document.getElementById(decodeURIComponent(h.slice(1)));if(t&&t.tagName==='DETAILS'){t.open=true;t.scrollIntoView();}}
  // Opening a swimmer's card puts it in the address bar (bookmarkable,
  // shareable); closing it takes it back out.
  document.querySelectorAll('details.ch-hawk[id]').forEach(function(d){d.addEventListener('toggle',function(){
    if(d.open&&location.hash!=='#'+d.id)history.replaceState(null,'','#'+d.id);
    else if(!d.open&&location.hash==='#'+d.id)history.replaceState(null,'',location.pathname+location.search);});});
  window.addEventListener('hashchange',function(){openFor(location.hash)});openFor(location.hash);
  window.addEventListener('load',function(){openFor(location.hash)});
  if(!('IntersectionObserver' in window))return;
  var links=document.querySelectorAll('.ch-nav a');
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;
    links.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+en.target.id);});});},
    {rootMargin:'-30% 0px -65% 0px'});
  document.querySelectorAll('.ch-sec').forEach(function(s){io.observe(s)});
})();
</script>"""


def page(meet, recs, rrecs, sb, alltime, prior, prior_year, when, venue, crumbs, source, project_root):
    d = collect(meet, recs, rrecs, sb, alltime, project_root)
    # the graduating class this meet's seniors belong to, and the senior page's own State count
    y, mo = int(meet['date'][:4]), int(meet['date'][5:7])
    class_year = y + 1 if mo >= 8 else y
    career, slugs = {}, {}
    try:
        from senior_class_data import senior_class
        c = senior_class(class_year)
        for s in c['boys'] + c['girls']:
            slugs[s['name']] = s['slug']
            if s['state_years']:
                career[s['name']] = [str(x) for x in s['state_years']]
    except Exception:  # an older season without a senior page
        pass
    page_exists = (project_root / 'docs' / 'seniors' / f'class-of-{class_year}.html').exists()

    def href(name):
        return f'/seniors/class-of-{class_year}.html#{slugs[name]}' if page_exists and name in slugs else ''

    secs = [
        ('moments', 'Moments', icon('medal'), 'Championship moments', moments(d)),
        ('story', 'Team story', icon('team'), 'The team story', team_story(meet, d, prior, prior_year)),
        ('records', 'Records', icon('star'), 'Records broken', records_section(d)),
        ('breakthroughs', 'Breakthroughs', icon('trend'), 'Breakthrough swims', breakthroughs(d)),
        ('hawks', 'Hawks', icon('team'), 'Hawks at State', hawks(d, href)),
        ('seniors', 'Seniors', icon('cap'), 'Senior sendoff', seniors(d, career, class_year, href) if page_exists or career else ''),
        ('results', 'Results', icon('list'), 'Complete results', results(d, meet)),
    ]
    secs = [s for s in secs if s[4]]
    nav = ''.join(f'<a href="#{sid}">{label}</a>' for sid, label, _, _, _ in secs)
    body = ''.join(f'<section class="ch-sec" id="{sid}"><h2 class="sr-h2">{ic}{title}</h2>{html}</section>'
                   for sid, _, ic, title, html in secs)
    return f'''<div class="sr-page ch-page">
{hero(meet, d, prior, prior_year, when, venue)}
<nav class="ch-nav" aria-label="Sections">{nav}</nav>
<div class="container sr-body ch-body">
  <div class="ch-crumbs">{crumbs}</div>
  {body}
  <section class="sr-about ch-source"><h2 class="sr-h2">About these results</h2>{source}</section>
</div>
</div>{NAV_JS}'''
