#!/usr/bin/env python3
"""
Senior class celebration page: docs/seniors/class-of-<year>.html.

    python3 scripts/generate_senior_page.py                 # the current class
    python3 scripts/generate_senior_page.py --class 2026 --out /tmp/x.html   # any class, as a preview

Celebrates EVERY graduating senior (Aaryn, 2026-11-08: "celebrate the class
first, the individuals second, and their records and statistics as the
supporting story"):

  * a class hero: how many seniors, boys and girls, and class-wide
    accomplishments -- only those the data supports;
  * one card per senior, same layout and prominence for everyone, boys and
    girls each in alphabetical order by last name (never ranked by prestige);
  * on each card, achievements in order of prestige -- State, school records,
    class records, all-time Top 10, class Top 10, improvement -- and their
    strongest events; records count independently (an Open record and the
    Senior record set by the same swim are two achievements);
  * an expandable career section: records, every event's progression by
    grade, State results and relays, each with its meet and date.

The facts come from scripts/senior_class_data.py, which derives them from the
published record files; nothing is hand-entered and nothing is inferred. The
page says what its sources cover, so a gap reads as a gap, not as a swimmer
who did nothing.

The class year follows the newest data/season_*.json, so the nav's Seniors
link moves to the next class when the next season file is added.
"""

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from class_top10 import GRADES, seconds  # noqa: E402
from senior_class_data import senior_class, GRADE_NAME, ordinal, and_list  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
e = html.escape


def current_season():
    path = sorted((REPO / "data").glob("season_*.json"))[-1]
    return json.loads(path.read_text())


def senior_class_year():
    """2026-27 -> 2027. Used by the nav so Seniors always points at this year's class."""
    return int("20" + current_season()["season"].split("-")[1])


def senior_href():
    """Nav target for Seniors -- always the current senior class."""
    return f"/seniors/class-of-{senior_class_year()}.html"


# One small, coherent icon set (stroke icons, currentColor) in place of emoji.
ICONS = {
    "cap": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5"/><path d="M22 9v6"/>',
    "medal": '<circle cx="12" cy="15" r="5"/><path d="M8.5 11.5 6 3h4l2 5 2-5h4l-2.5 8.5"/>',
    "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "rank": '<path d="M5 20V12M12 20V5M19 20v-6"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "wave": '<path d="M2 15c2.5 0 2.5-2 5-2s2.5 2 5 2 2.5-2 5-2 2.5 2 5 2"/><path d="M2 19c2.5 0 2.5-2 5-2s2.5 2 5 2 2.5-2 5-2 2.5 2 5 2"/><circle cx="15" cy="6" r="2"/><path d="M5 11l5-4 3 3"/>',
    "relay": '<circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="7" r="2.5"/><path d="M3 20c0-3 2-5 4-5s4 2 4 5M13 20c0-3 2-5 4-5s4 2 4 5"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
}
ABBR = {"FR": "Fr.", "SO": "So.", "JR": "Jr.", "SR": "Sr."}
TIER_ICON = {1: "medal", 2: "star", 3: "star", 4: "rank", 5: "rank", 6: "trend"}


def icon(name, cls="sr-ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def spark(ev):
    """A restrained progression line over FR..SR, faster = higher. Needs 3+ seasons."""
    pts = [(i, seconds(ev["by_grade"][c]["time"])) for i, (c, _) in enumerate(GRADES) if c in ev["by_grade"]]
    if len(pts) < 3:
        return ""
    lo, hi = min(t for _, t in pts), max(t for _, t in pts)
    span = (hi - lo) or 1
    w, h, pad = 96, 28, 3
    xy = [(pad + i * (w - 2 * pad) / 3, pad + (t - lo) / span * (h - 2 * pad)) for i, t in pts]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2"/>' for x, y in xy)
    return (f'<svg class="sr-spark" viewBox="0 0 {w} {h}" role="img" aria-label="Season bests, faster is higher">'
            f'<polyline points="{line}"/>{dots}</svg>')


def chips(ev):
    out = []
    kinds = ev["records"]
    if "Open" in kinds:
        out.append('<span class="sr-chip sr-gold">School record</span>')
    if ev["alltime"] and "Open" not in kinds:
        out.append(f'<span class="sr-chip">#{ev["alltime"]["rank"]} all-time</span>')
    return "".join(out)


def highlight_li(h):
    tier, gold, title, detail = h
    return (f'<li class="sr-hl{" sr-hl-gold" if gold else ""}">{icon(TIER_ICON[tier])}'
            f'<span><strong>{e(title)}</strong> <span class="sr-hl-d">{e(detail)}</span></span></li>')


def best_rows(s, n=3):
    rows = []
    for ev in s["strongest"][:n]:
        rows.append(f'<li><span class="sr-ev">{e(ev["short"])}</span>'
                    f'<span class="sr-t">{e(ev["career"]["time"])}</span>{chips(ev)}</li>')
    return f'<ul class="sr-best">{"".join(rows)}</ul>' if rows else ""


def records_block(s):
    if not s["records"]:
        return ""
    n_open, n_cls = len(s["open_records"]), len(s["class_records"])
    parts = []
    if n_open:
        parts.append(f"{n_open} school")
    if n_cls:
        parts.append(f"{n_cls} class")
    total = n_open + n_cls
    out = [f'<h4 class="sr-h4">{icon("star")}Records <span class="sr-count">{total} record'
           f'{"s" if total != 1 else ""} &middot; {" &middot; ".join(parts)}</span></h4>']
    if s["open_records"]:
        out.append('<ul class="sr-list">' + "".join(
            f'<li><span class="sr-chip sr-gold">School record</span> {e(r["event"])} '
            f'<span class="sr-t">{e(r["time"])}</span><span class="sr-src">{e(r["meet"])} &middot; {e(r["date"])}</span></li>'
            for r in s["open_records"]) + "</ul>")
    if s["class_records"]:
        out.append('<p class="sr-note">Class records &mdash; the fastest ever swum by a Tanque Verde '
                   'freshman, sophomore, junior or senior &mdash; are marked in each event&rsquo;s progression below.</p>')
    return "".join(out)


def progression_block(s):
    if not s["events"]:
        return ""
    heads = "".join(f"<th>{ABBR[c].rstrip('.')}</th>" for c, _ in GRADES)
    rows = []
    for ev in s["events"]:
        cells = []
        for c, _ in GRADES:
            o = ev["by_grade"].get(c)
            if not o:
                cells.append('<td class="sr-none">&ndash;</td>')
                continue
            marks = []
            if c in ev["records"]:
                marks.append(f'<span class="sr-mark" title="{GRADE_NAME[c]} class record">{ABBR[c]} record</span>')
            if "Open" in ev["records"] and o is ev["career"]:
                marks.append('<span class="sr-mark sr-gold" title="School record">School record</span>')
            if ev["classes"].get(c) and c not in ev["records"]:
                marks.append(f'<span class="sr-mark sr-green" title="#{ev["classes"][c]["rank"]} fastest ever as a {GRADE_NAME[c].lower()}">#{ev["classes"][c]["rank"]} {ABBR[c]}</span>')
            best = " sr-cb" if o is ev["career"] else ""
            cells.append(f'<td class="{best.strip()}"><span class="sr-t" title="{e(o["meet"])}, {e(o["date"])}">'
                         f'{e(o["time"])}</span>{"".join(marks)}</td>')
        cb = ev["career"]
        note = f'Career best {e(cb["time"])} &middot; {e(cb["meet"])}, {e(cb["date"])}'
        if ev["drop"] > 0:
            note += f' &middot; {ev["drop"]:.2f}s faster than {GRADE_NAME[ev["first"]["grade"]].lower()} year'
        if ev["alltime"]:
            note += f' &middot; #{ev["alltime"]["rank"]} all-time'
        rows.append(f'<tr><th scope="row">{e(ev["short"])}{spark(ev)}</th>{"".join(cells)}</tr>'
                    f'<tr class="sr-prov"><td colspan="5">{note}</td></tr>')
    return (f'<h4 class="sr-h4">{icon("trend")}Events &amp; progression</h4>'
            f'<p class="sr-note">Best time each season, by grade. The highlighted time is the career best.</p>'
            f'<div class="sr-tbl-wrap"><table class="sr-prog"><thead><tr><th>Event</th>{heads}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def state_block(s):
    if not s["state_meets"]:
        return ""
    out = [f'<h4 class="sr-h4">{icon("medal")}State Championships</h4>']
    for m in s["state_meets"]:
        mine = [x for x in s["state"] if x["year"] == m["year"]]
        if not m["swam"]:
            continue
        link = (f'<a href="{m["page"]}">{e(m["meet"])}</a>' if m["page"] else
                f'<a href="{e(m["source"])}" rel="noopener">{e(m["meet"])}</a>' if m["source"] else e(m["meet"]))
        team = ""
        if m["team"]:
            t = m["team"]
            team = (f'<span class="sr-chip sr-gold">{s["gender"].title()} team: State champions</span>'
                    if t["place"] == 1 else
                    f'<span class="sr-chip">{s["gender"].title()} team: {ordinal(t["place"])}</span>')
        items = []
        for x in mine:
            if x["final"] and x["place"] == 1:
                where, gold = "State champion", " sr-gold"
            elif x["final"] and x["place"]:
                where, gold = f'{ordinal(x["place"])} at State', " sr-gold" if x["place"] <= 3 else ""
            else:
                where, gold = (f'{ordinal(x["place"])} in prelims' if x["place"] else "Prelims"), " sr-quiet"
            mates = f'<span class="sr-src">with {e(and_list(x["mates"]))}</span>' if x.get("mates") else ""
            items.append(f'<li><span class="sr-chip{gold}">{e(where)}</span> {e(x["short"])} '
                         f'<span class="sr-t">{e(x["time"])}</span>{mates}</li>')
        grade = GRADE_NAME[m["grade"]].lower()
        out.append(f'<p class="sr-state-y"><strong>{m["year"]}</strong> &middot; as a {grade} &middot; {link} {team}</p>'
                   f'<ul class="sr-list">{"".join(items)}</ul>')
    return "".join(out)


def relay_block(s):
    if not s["relays"]:
        return ""
    items = []
    for r in s["relays"]:
        label = "School record" if r["rank"] == 1 else f'#{r["rank"]} all-time'
        gold = " sr-gold" if r["rank"] == 1 else ""
        more = f' &middot; on {r["count"]} of the list&rsquo;s times' if r["count"] > 1 else ""
        items.append(f'<li><span class="sr-chip{gold}">{label}</span> {e(r["event"])} '
                     f'<span class="sr-t">{e(r["time"])}</span>'
                     f'<span class="sr-src">with {e(and_list(r["mates"]))} &middot; {e(r["meet"])}, {e(r["date"])}{more}</span></li>')
    return (f'<h4 class="sr-h4">{icon("relay")}Relays <span class="sr-count">best place on the all-time relay lists</span></h4>'
            f'<ul class="sr-list">{"".join(items)}</ul>')


def card(s, year):
    hl = s["highlights"]
    shown = hl[:2]
    rest = hl[2:]
    more = ""
    if rest:
        more = (f'<h4 class="sr-h4">{icon("medal")}All highlights</h4><ul class="sr-hls">'
                + "".join(highlight_li(h) for h in hl) + "</ul>")
    detail = "".join([more, records_block(s), state_block(s), progression_block(s), relay_block(s)])
    if not shown and not s["events"]:
        body = ('<p class="sr-note">No individual swims for this senior are in our posted results yet. '
                'That is a gap in our records, not in a senior&rsquo;s career.</p>')
    else:
        body = (f'<ul class="sr-hls">{"".join(highlight_li(h) for h in shown)}</ul>' if shown else "") + best_rows(s)
    g = "Boys" if s["gender"] == "boys" else "Girls"
    return f'''<article class="sr-card" id="{s["slug"]}">
  <header class="sr-card-h">
    <div class="sr-eyebrow">{icon("cap", "sr-ico sr-cap")}Class of {year} &middot; {g}</div>
    <h3 class="sr-name">{e(s["name"])}</h3>
    <a class="sr-anchor" href="#{s["slug"]}" aria-label="Link to {e(s["name"])}">{icon("link")}</a>
  </header>
  {body}
  {f'<details class="sr-more"><summary>Career, records &amp; progression</summary><div class="sr-more-b">{detail}</div></details>' if detail else ''}
</article>'''


def class_stats(c):
    """Class-wide accomplishments, each counted from the cards' own facts."""
    everyone = c["boys"] + c["girls"]
    titles = {(s["gender"], x["year"], x["event"]) for s in everyone for x in s["state"]
              if x["final"] and x["place"] == 1}
    team_titles = {(s["gender"], m["year"]) for s in everyone for m in s["team_titles"]}
    school = {(s["gender"], r["event"]) for s in everyone for r in s["open_records"]}
    school |= {(s["gender"], r["event"]) for s in everyone for r in s["relays"] if r["rank"] == 1}
    class_recs = sum(len(s["class_records"]) for s in everyone)
    at_state = sum(1 for s in everyone if s["state"])
    alltime = sum(1 for s in everyone if any(ev["alltime"] for ev in s["events"]))
    stats = [(len(team_titles), "State team title", "State team titles"),
             (len(titles), "State event title", "State event titles"),
             (len(school), "school record held", "school records held"),
             (class_recs, "class record", "class records"),
             (at_state, "senior who swam at State", "seniors who swam at State"),
             (alltime, "senior on the all-time Top 10", "seniors on the all-time Top 10")]
    return [(n, one if n == 1 else many) for n, one, many in stats if n]


def coverage(c):
    season, meets = c["season"], c["season_meets"]
    first = int(season[:4]) - 3
    parts = []
    if meets:
        status = ("The season is complete" if c["season_complete"] else
                  "The season is still in progress, so this page will grow")
        parts.append(f"{status}. Senior-season swims include every posted result from "
                     f"{e(and_list(meets))}. Dual-meet results are not included.")
        parts.append(f"Earlier seasons ({first}-{(first + 1) % 100:02d} to {int(season[:4]) - 1}-{int(season[:4]) % 100:02d}) "
                     "come from each season&rsquo;s team Top 10 lists. "
                     "A swim that did not make its season&rsquo;s Top 10 is not in our files, so a missing time is a gap "
                     "in our records, not in a swimmer&rsquo;s career.")
        hist = sorted(p.stem for p in (REPO / "data" / "state_history").glob("*.json"))
        parts.append("State places, relay lineups and team finishes come from the official meet results: "
                     f"the posted {e(and_list([m for m in meets if 'state' in m.lower()]) or 'State')} results"
                     + (f", and the AIA results for {and_list(hist)}" if hist else "") + ".")
    else:
        parts.append("Career swims come from each season&rsquo;s team Top 10 lists. A swim that did not make its "
                     "season&rsquo;s Top 10 is not in our files, so a missing time is a gap in our records, not in a "
                     "swimmer&rsquo;s career. State places are not in our files for this class.")
    if c["roster_source"] == "top10":
        parts.append("This class&rsquo;s list of seniors is taken from swimmers listed as seniors on that season&rsquo;s "
                     "Top 10 lists; a senior who never made a Top 10 list is missing from this page. "
                     "Corrections are welcome.")
    legend = ("<strong>School record</strong>: fastest ever by a Tanque Verde swimmer. "
              "<strong>Class record</strong>: fastest ever by a Tanque Verde freshman, sophomore, junior or senior. "
              "<strong>All-time Top 10</strong>: one of the ten fastest Tanque Verde swimmers ever in the event. "
              "<strong>Class Top 10</strong> (e.g. &ldquo;#4 junior&rdquo;): among the ten fastest ever in that grade. "
              "<strong>Career best</strong>: the swimmer&rsquo;s fastest time in our files.")
    return " ".join(f"<p>{p}</p>" for p in parts) + f"<p>{legend}</p>"


def page(c):
    year = c["year"]
    nb, ng = len(c["boys"]), len(c["girls"])
    total = nb + ng
    words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
             "twelve", "thirteen", "fourteen", "fifteen"]
    tw = words[total] if total < len(words) else str(total)
    stats = "".join(f'<div class="sr-stat"><span class="sr-stat-n">{n}</span><span class="sr-stat-l">{e(l)}</span></div>'
                    for n, l in class_stats(c))
    roll = "".join(f'<a href="#{s["slug"]}">{e(s["name"])}</a>' for s in c["boys"] + c["girls"])
    sections = []
    for g, label in (("boys", "Boys"), ("girls", "Girls")):
        if c[g]:
            sections.append(f'<section class="sr-sec"><h2 class="sr-h2">{label} <span>{len(c[g])}</span></h2>'
                            f'<div class="sr-grid">{"".join(card(s, year) for s in c[g])}</div></section>')
    others = sorted(int(p.stem.split("-")[-1]) for p in (REPO / "docs" / "seniors").glob("class-of-*.html"))
    others = [y for y in others if y != year]
    other_links = " &middot; ".join(f'<a href="/seniors/class-of-{y}.html">Class of {y}</a>' for y in others)
    return f'''<div class="sr-page">
<section class="sr-hero">
  <div class="container">
    <img src="/images/hawk-logo.svg" alt="" class="sr-hero-logo">
    <div class="sr-hero-eyebrow">{icon("cap", "sr-ico")}Tanque Verde Swimming</div>
    <h1 class="sr-hero-title">Senior Class of {year}</h1>
    <p class="sr-hero-msg">Congratulations to our {tw} graduating seniors. Thank you for every race, every relay
    and every early practice &mdash; and for the team you leave behind.</p>
    <p class="sr-hero-count"><span>{total} seniors</span><span>{nb} boys</span><span>{ng} girls</span></p>
    {f'<div class="sr-stats">{stats}</div>' if stats else ''}
  </div>
</section>
<div class="container sr-body">
  <nav class="sr-roll" aria-label="The class">{roll}</nav>
  {"".join(sections)}
  <section class="sr-about"><h2 class="sr-h2">About this page</h2>{coverage(c)}</section>
  {f'<p class="sr-others">Other classes: {other_links}</p>' if other_links else ''}
</div>
</div>'''


def build(year=None, out=None):
    from generate_website import create_html_page
    year = year or senior_class_year()
    c = senior_class(year)
    for s in c["boys"] + c["girls"]:
        for w in s["warnings"]:
            print(f"  ⚠️  {s['name']}: {w}")
    out = Path(out) if out else REPO / "docs" / "seniors" / f"class-of-{year}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(create_html_page(f"Senior Class of {year}", page(c), page_type="senior"))
    print(f"✅ wrote {out} ({len(c['boys']) + len(c['girls'])} seniors)")
    return c


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--class", dest="year", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    build(a.year, a.out)
