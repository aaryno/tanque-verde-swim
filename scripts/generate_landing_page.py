#!/usr/bin/env python3
"""
Generate the season landing page (docs/index.html).

Until 2026 this page was hand-maintained, which is why the Class of 2026 senior
recognition page it used to hold had no generator behind it. That page now lives
at docs/seniors/class-of-2026.html and stays hand-maintained; this script owns
docs/index.html and rebuilds it from data/season_2026-27.json.

Every fact on the page comes from that JSON or from records/records-boys.md.
Nothing here is typed in by hand, including the "oldest record" superlative --
see verify_oldest_record(), which recomputes it on every run and downgrades the
wording rather than printing a claim it cannot support.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_website import create_nav_html

SEASON = '2026-27'

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']
MONTH_NUM = {m[:3]: i + 1 for i, m in enumerate(MONTHS)}


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def parse_record_date(s):
    """'Oct 24, 2015' -> (2015, 10, 24). Returns None if unparseable."""
    m = re.match(r'([A-Z][a-z]{2})[a-z]*\s+(\d{1,2}),\s*(\d{4})', s.strip())
    if not m:
        return None
    return (int(m.group(3)), MONTH_NUM[m.group(1)], int(m.group(2)))


def collect_open_boys_records(records_dir):
    """Every standing boys OPEN record as (event, date_tuple, date_text, time, who).

    Individual OPEN records are the bold 'Open' grade row; relay records are the
    bold rank-1 row. Both files are the repo's source of truth. Every column the
    page names is read from the same row, so a record change moves the prose.
    """
    out = []

    ind = (records_dir / 'records-boys.md').read_text()
    event = None
    for line in ind.splitlines():
        h = re.match(r'^###\s+(.*)', line.strip())
        if h:
            event = h.group(1).strip()
            continue
        if not line.strip().startswith('|') or '**' not in line:
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 5 or cells[0].replace('*', '').strip() != 'Open':
            continue
        d = parse_record_date(cells[3].replace('*', ''))
        if d:
            out.append((event, d, cells[3].replace('*', '').strip(),
                        cells[1].replace('*', '').strip(),
                        cells[2].replace('*', '').strip()))

    rel = (records_dir / 'relay-records-boys.md').read_text()
    event = None
    for line in rel.splitlines():
        h = re.match(r'^##\s+(.*Relay.*)', line.strip())
        if h:
            event = h.group(1).strip()
            continue
        if not line.strip().startswith('|') or '**' not in line:
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 5 or cells[0].replace('*', '').strip() != '1':
            continue
        d = parse_record_date(cells[3].replace('*', ''))
        if d:
            out.append((event, d, cells[3].replace('*', '').strip(),
                        cells[1].replace('*', '').strip(),
                        cells[2].replace('*', '').strip()))

    return out


def verify_oldest_record(records_dir, milestone):
    """Was the record Kent broke the oldest-standing boys record before he broke it?

    Aaryn's phrasing was "the oldest men's swimming record". That is a claim, not
    a given, so it is recomputed here every build. Compare the broken record's
    date against every OTHER standing boys OPEN record (individual and relay).
    Returns (verdict, phrase, runner_up) where verdict is one of
    'oldest' / 'not-oldest' / 'unverifiable'.
    """
    broken_event = milestone['event']
    broken = parse_record_date(milestone['broke_open']['date'])
    if not broken:
        return ('unverifiable', 'a long-standing school record', None)

    others = [r for r in collect_open_boys_records(records_dir)
              if r[0] != broken_event]
    if not others:
        return ('unverifiable', 'a long-standing school record', None)

    others.sort(key=lambda r: r[1])
    runner_up = others[0]

    if broken < runner_up[1]:
        return ('oldest', 'the oldest record on the Tanque Verde boys books', runner_up)
    return ('not-oldest', 'one of the longest-standing records on the Tanque Verde boys books',
            runner_up)


def describe_record(rec):
    """A record row as '<event> &mdash; <time>, <swimmer>, <date>'.

    Every field comes from the same parsed row as the date, so naming the time
    and the swimmer cannot drift out of step with the records files.
    """
    event, _, date_text, time, who = rec
    return f'{esc(event)} &mdash; {esc(time)}, {esc(who)}, {esc(date_text)}'


def fmt_meet_date(start, end):
    """'2026-10-23','2026-10-24' -> 'Oct 23-24'; single day -> 'Thu, Oct 3'."""
    sy, sm, sd = (int(x) for x in start.split('-'))
    ey, em, ed = (int(x) for x in end.split('-'))
    mon = MONTHS[sm - 1][:3]
    if (sy, sm, sd) == (ey, em, ed):
        return f'{mon} {sd}'
    if (sy, sm) == (ey, em):
        return f'{mon} {sd}&ndash;{ed}'
    return f'{mon} {sd} &ndash; {MONTHS[em - 1][:3]} {ed}'


def schedule_rows(data, today):
    rows = []
    for m in data['schedule']['meets']:
        past = m['date_end'] < today
        badge = ('<span class="badge bg-secondary">Home</span>' if m['home']
                 else '<span class="badge bg-light text-dark">Away</span>')
        cls = ' class="text-muted"' if past else ''
        rows.append(
            f'''                        <tr{cls}>
                            <td class="text-nowrap"><strong>{fmt_meet_date(m['date_start'], m['date_end'])}</strong></td>
                            <td>{esc(m['name'])} {badge}<br><small class="text-muted">{esc(m['note'])}</small></td>
                            <td><small>{esc(m['venue'])}</small></td>
                        </tr>''')
    return '\n'.join(rows)


def senior_cards(names, gender_label):
    cards = []
    for n in names:
        cards.append(
            f'''                <div class="col-6 col-md-4">
                    <div class="card h-100 senior-card">
                        <div class="card-body">
                            <h5 class="card-title mb-1">{esc(n)}</h5>
                            <p class="mb-0"><small class="text-muted">{gender_label} &middot; Class of 2027</small></p>
                        </div>
                    </div>
                </div>''')
    return '\n'.join(cards)


def build_page(project_root):
    data = json.loads((project_root / 'data' / f'season_{SEASON}.json').read_text())
    records_dir = project_root / 'records'
    ms = data['milestone']
    verdict, phrase, runner_up = verify_oldest_record(records_dir, ms)

    sched = data['schedule']
    roster = data['roster']
    res = data['results_so_far']
    seniors_b = roster['seniors_boys']
    seniors_g = roster['seniors_girls']
    n_seniors = len(seniors_b) + len(seniors_g)
    today = datetime.now().strftime('%Y-%m-%d')

    broken_desc = (f"The open school record he took down &mdash; {esc(ms['broke_open']['time'])}, "
                   f"set by {esc(ms['broke_open']['name'])} on {esc(ms['broke_open']['date'])} &mdash;")
    if verdict == 'oldest':
        oldest_line = (
            f'''<p class="mb-0">{broken_desc} was <strong>{phrase}</strong>. '''
            f'''It had stood longer than any other boys school record, individual or relay. '''
            f'''The next-oldest still standing is the {describe_record(runner_up)}.</p>''')
    elif verdict == 'not-oldest':
        oldest_line = (
            f'''<p class="mb-0">{broken_desc} was <strong>{phrase}</strong>. '''
            f'''The oldest still standing is the {describe_record(runner_up)}.</p>''')
    else:
        oldest_line = f'<p class="mb-0">{broken_desc} had stood for more than a decade.</p>'

    nav_html = create_nav_html()

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tanque Verde High School Swimming &amp; Diving | {SEASON} Season</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="/css/style.css">

    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/images/favicon.png">
    <link rel="apple-touch-icon" href="/images/hawk-logo.png">
</head>
<body>
    {nav_html}

    <!-- Hero Section (Collapsible) -->
    <div class="hero-header" id="hero-header">
        <div class="hero-expanded" id="hero-expanded">
            <div class="container text-center">
                <img src="/images/hawk-logo.png" alt="Tanque Verde Hawks" class="hero-logo">
                <h1>Tanque Verde High School</h1>
                <h2>{SEASON} Swimming &amp; Diving</h2>
                <p class="subtitle">Tucson, Arizona | AIA Division III</p>
                <button class="hero-collapse-btn" id="hero-collapse-btn" title="Collapse header" onclick="document.getElementById('hero-header').classList.add('collapsed'); localStorage.setItem('hero-collapsed', 'true'); return false;">
                    <span>&#9650;</span>
                </button>
            </div>
        </div>
        <div class="hero-collapsed" id="hero-collapsed">
            <div class="container d-flex align-items-center justify-content-between flex-wrap">
                <div class="d-flex align-items-center hero-expand-trigger" style="cursor: pointer;" title="Click to expand">
                    <span class="hero-title-small">TVHS Swimming {SEASON}</span>
                </div>
                <div class="d-flex gap-2">
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                            Jump To
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item jump-to-link" href="#season">&#127946; The {SEASON} Season</a></li>
                            <li><a class="dropdown-item jump-to-link" href="#schedule">&#128197; Meet Schedule</a></li>
                            <li><a class="dropdown-item jump-to-link" href="#seniors">&#127891; Senior Class of 2027</a></li>
                            <li><a class="dropdown-item jump-to-link" href="#kent">&#127942; School Record: {esc(ms['swimmer'])}</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 1. Season Introduction -->
    <div class="container my-5" id="season">
        <div class="section-header" data-section="season">
            <h2 class="mb-0">&#127946; The {SEASON} Season</h2>
            <button class="section-toggle" data-target="season-content">
                <span class="toggle-icon">&#9660;</span>
            </button>
        </div>
        <div class="section-content" id="season-content">
            <p class="lead mb-3 mt-3">The Hawks are back in the water. The {SEASON} season opened on
            {fmt_meet_date(sched['meets'][0]['date_start'], sched['meets'][0]['date_end'])} and runs through
            the AIA Division III State Championship in November.</p>

            <div class="alert alert-warning">
                <strong>This season is just getting started.</strong>
                Results have been published from <strong>one meet</strong> so far &mdash; the
                {esc(res['latest_meet'])} on {fmt_meet_date(res['latest_meet_date'], res['latest_meet_date'])}.
                Every {SEASON} page on this site reflects that single meet, not a finished season,
                and will fill in as more results are posted.
            </div>

            <p class="mb-2">A few places to look while the season builds:</p>
            <ul class="mb-0">
                <li><a href="/top10/boys-{SEASON}.html">Boys {SEASON} Top 10</a> &middot;
                    <a href="/top10/girls-{SEASON}.html">Girls {SEASON} Top 10</a> &mdash; the fastest times swum so far this year</li>
                <li><a href="/annual/{SEASON}.html">{SEASON} season summary</a></li>
                <li><a href="/records/overall.html">All-time school records</a></li>
                <li><a href="/seniors/class-of-2026.html">Class of 2026 senior recognition</a> &mdash; last year's graduating class</li>
            </ul>
        </div>
    </div>

    <!-- 2. Meet Schedule -->
    <div class="container my-5" id="schedule">
        <div class="section-header" data-section="schedule">
            <h2 class="mb-0">&#128197; {SEASON} Meet Schedule</h2>
            <button class="section-toggle" data-target="schedule-content">
                <span class="toggle-icon">&#9660;</span>
            </button>
        </div>
        <div class="section-content" id="schedule-content">
            <p class="lead mb-3 mt-3">{len(sched['meets'])} meets, ending at the AIA Division III State Championship.
            Meets already swum are greyed out.</p>
            <div class="table-responsive">
                <table class="table table-sm align-middle table-schedule">
                    <thead>
                        <tr><th>Date</th><th>Meet</th><th>Where</th></tr>
                    </thead>
                    <tbody>
{schedule_rows(data, today)}
                    </tbody>
                </table>
            </div>
            <p class="mb-0"><small class="text-muted">Schedule from Tanque Verde High School's official
            {SEASON} Varsity Swim Schedule. Start times are not published for every meet &mdash;
            confirm with the coaching staff before travelling.</small></p>
        </div>
    </div>

    <!-- 3. Senior Class -->
    <div class="container my-5" id="seniors">
        <div class="section-header" data-section="seniors">
            <h2 class="mb-0">&#127891; Senior Class of 2027</h2>
            <button class="section-toggle" data-target="seniors-content">
                <span class="toggle-icon">&#9660;</span>
            </button>
        </div>
        <div class="section-content" id="seniors-content">
            <p class="lead mb-4 mt-3">{n_seniors} seniors are swimming their final season for the Hawks
            &mdash; {len(seniors_b)} on the boys team and {len(seniors_g)} on the girls team.</p>

            <h5 class="mb-3">Boys</h5>
            <div class="row g-3 mb-4">
{senior_cards(seniors_b, 'Boys')}
            </div>

            <h5 class="mb-3">Girls</h5>
            <div class="row g-3">
{senior_cards(seniors_g, 'Girls')}
            </div>

            <p class="mt-4 mb-0"><small class="text-muted">Seniors listed from the team's own
            {SEASON} roster, which states each swimmer's grade. Spelling follows the roster.
            A full senior recognition page will follow at the end of the season, as it did for the
            <a href="/seniors/class-of-2026.html">Class of 2026</a>.</small></p>
        </div>
    </div>

    <!-- 4. Kent Olsson school record -->
    <div class="container my-5" id="kent">
        <div class="section-header" data-section="kent">
            <h2 class="mb-0">&#127942; School Record: {esc(ms['swimmer'])}, {esc(ms['event'])}</h2>
            <button class="section-toggle" data-target="kent-content">
                <span class="toggle-icon">&#9660;</span>
            </button>
        </div>
        <div class="section-content" id="kent-content">
            <div class="alert alert-success mt-3">
                <h4 class="alert-heading mb-2">Congratulations, {esc(ms['swimmer'])}!</h4>
                <p class="mb-2">At the {esc(ms['meet'])} on {esc(ms['date'])}, {esc(ms['swimmer'])} swam the
                {esc(ms['event'])} in <span class="time"><strong>{esc(ms['time'])}</strong></span> &mdash;
                and broke <strong>two</strong> Tanque Verde records in the same swim.</p>
                {oldest_line}
            </div>

            <div class="row g-3">
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">&#127942; Open school record</h5>
                            <p class="mb-1"><span class="time"><strong>{esc(ms['time'])}</strong></span>
                                &nbsp;<span class="badge badge-pb pb-black">&minus;{esc(ms['broke_open']['margin'])}s</span></p>
                            <hr class="my-2">
                            <small class="text-muted">
                                <strong>Previous:</strong> {esc(ms['broke_open']['time'])} &mdash; {esc(ms['broke_open']['name'])}<br>
                                <span style="font-size: 0.85em;">{esc(ms['broke_open']['date'])} at {esc(ms['broke_open']['meet'])}</span>
                            </small>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">&#129352; {esc(ms['broke_class']['grade'])} class record</h5>
                            <p class="mb-1"><span class="time"><strong>{esc(ms['time'])}</strong></span>
                                &nbsp;<span class="badge badge-pb pb-black">&minus;{esc(ms['broke_class']['margin'])}s</span></p>
                            <hr class="my-2">
                            <small class="text-muted">
                                <strong>Previous:</strong> {esc(ms['broke_class']['time'])} &mdash; {esc(ms['broke_class']['name'])}<br>
                                <span style="font-size: 0.85em;">{esc(ms['broke_class']['date'])} at {esc(ms['broke_class']['meet'])}</span>
                            </small>
                        </div>
                    </div>
                </div>
            </div>

            <p class="mt-3 mb-0">He already owned the {esc(ms['already_held']['grade'])}
            {esc(ms['event'])} record &mdash; {esc(ms['already_held']['time'])}, set at the
            {esc(ms['already_held']['meet'])} on {esc(ms['already_held']['date'])}. As a
            {esc(ms['grade']).lower()}, he now holds the Freshman record, the Sophomore record and the
            Open record in the same event. See the
            <a href="/records/overall.html">all-time records</a> and the
            <a href="/records/boys-bygrade.html">boys records by grade</a>.</p>
        </div>
    </div>

    <!-- Footer -->
    <footer class="mt-5">
        <div class="container text-center">
            <div class="disclaimer mb-3">
                <small class="text-muted">
                    Results compiled from meets published on <a href="https://azpreps365.com" target="_blank">AZPreps365</a>
                    and <a href="https://maxpreps.com" target="_blank">MaxPreps</a> with limited data availability &mdash;
                    not necessarily a complete compilation of all records.
                    Contact <a href="mailto:aaryno@gmail.com">aaryno@gmail.com</a> with additional sources, errors, or corrections.
                </small>
            </div>
            <p class="mb-2">&copy; {datetime.now().year} Tanque Verde High School Swimming</p>
            <p class="mb-0">
                <small>
                    Generated on {datetime.now().strftime('%B %d, %Y')} |
                    <a href="https://github.com/aaryno/tanque-verde-swim">View on GitHub</a>
                </small>
            </p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        // Collapsible hero header
        const heroHeader = document.getElementById('hero-header');
        const heroCollapseBtn = document.getElementById('hero-collapse-btn');
        const heroExpandTrigger = document.querySelector('.hero-expand-trigger');

        if (heroHeader) {{
            if (localStorage.getItem('hero-collapsed') === 'true') {{
                heroHeader.classList.add('collapsed');
            }}
            if (heroCollapseBtn) {{
                heroCollapseBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    heroHeader.classList.add('collapsed');
                    localStorage.setItem('hero-collapsed', 'true');
                }});
            }}
            if (heroExpandTrigger) {{
                heroExpandTrigger.addEventListener('click', function(e) {{
                    e.preventDefault();
                    heroHeader.classList.remove('collapsed');
                    localStorage.setItem('hero-collapsed', 'false');
                    window.scrollTo({{ top: 0, behavior: 'smooth' }});
                }});
            }}
            window.addEventListener('scroll', function() {{
                const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
                if (currentScroll > 100 && !heroHeader.classList.contains('collapsed')) {{
                    heroHeader.classList.add('collapsed');
                    localStorage.setItem('hero-collapsed', 'true');
                }}
            }}, {{ passive: true }});
        }}

        // Collapsible sections
        document.querySelectorAll('.section-header').forEach(header => {{
            header.addEventListener('click', function(e) {{
                e.preventDefault();
                const toggleBtn = this.querySelector('.section-toggle');
                if (!toggleBtn) return;
                const content = document.getElementById(toggleBtn.dataset.target);
                if (content) {{
                    this.classList.toggle('collapsed');
                    content.classList.toggle('collapsed');
                }}
            }});
        }});

        // Smooth scroll for Jump To links
        document.querySelectorAll('.jump-to-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                e.preventDefault();
                const targetElement = document.getElementById(this.getAttribute('href').substring(1));
                if (targetElement) {{
                    const sectionHeader = targetElement.querySelector('.section-header');
                    const sectionContent = targetElement.querySelector('.section-content');
                    if (sectionHeader && sectionHeader.classList.contains('collapsed')) {{
                        sectionHeader.classList.remove('collapsed');
                        if (sectionContent) sectionContent.classList.remove('collapsed');
                    }}
                    const y = targetElement.getBoundingClientRect().top + window.pageYOffset - 160;
                    window.scrollTo({{top: y, behavior: 'smooth'}});
                }}
            }});
        }});
    }});
    </script>
</body>
</html>
'''


def main():
    project_root = Path(__file__).parent.parent
    out = project_root / 'docs' / 'index.html'
    data = json.loads((project_root / 'data' / f'season_{SEASON}.json').read_text())
    verdict, phrase, runner_up = verify_oldest_record(
        project_root / 'records', data['milestone'])
    print(f"  oldest-record check: {verdict} -> \"{phrase}\"")
    if runner_up:
        print(f"  next-oldest standing boys record: {runner_up[0]} "
              f"({runner_up[3]}, {runner_up[4]}, {runner_up[2]})")
    out.write_text(build_page(project_root))
    print(f"  ✓ {out}")


if __name__ == '__main__':
    main()
