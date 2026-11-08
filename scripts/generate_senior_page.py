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


GRADE_ORDER = [c for c, _ in GRADES]


def fmt_drop(d):
    return f"{d:.2f}s" if d < 60 else f"{int(d // 60)}:{d % 60:05.2f}"


def chart_scale(s):
    """One vertical scale for every chart on a card: percent faster than the
    swimmer's first season in that event, from 0 up to the card's largest drop
    rounded up to 5%. A shared, zero-based scale keeps a 2% drop from looking
    as steep as a 14% one."""
    top = max([e["drop_pct"] for e in s["events"] if len(e["by_grade"]) >= 3] or [0])
    return max(5, -(-int(top + 0.999) // 5) * 5)


def prog_chart(ev, scale):
    """Season bests over Fr..Sr, faster = higher, every point labelled with its
    time. Only for events with 3+ seasons; one or two points are no story."""
    seen = [c for c in GRADE_ORDER if c in ev["by_grade"]]
    if len(seen) < 3:
        return ""
    first = seconds(ev["by_grade"][seen[0]]["time"])
    pct = {c: (first - seconds(ev["by_grade"][c]["time"])) / first * 100 for c in seen}
    lo = min(0, min(pct.values()))
    W, H, T, B = 400, 116, 22, 20
    x = {c: W * (0.125 + 0.25 * i) for i, c in enumerate(GRADE_ORDER)}

    def y(p):
        return T + (scale - p) / ((scale - lo) or 1) * (H - T - B)

    parts = [f'<line class="sr-ax" x1="0" x2="{W}" y1="{y(0):.1f}" y2="{y(0):.1f}"/>',
             f'<line class="sr-grid-l" x1="0" x2="{W}" y1="{y(scale):.1f}" y2="{y(scale):.1f}"/>',
             f'<text class="sr-ax-t" x="1" y="{y(0) - 3:.1f}">0%</text>',
             f'<text class="sr-ax-t" x="1" y="{y(scale) - 3:.1f}">{scale}% faster</text>']
    for a, b in zip(seen, seen[1:]):
        gap = GRADE_ORDER.index(b) - GRADE_ORDER.index(a) > 1
        parts.append(f'<line class="sr-pl{" sr-pl-gap" if gap else ""}" x1="{x[a]:.1f}" y1="{y(pct[a]):.1f}" '
                     f'x2="{x[b]:.1f}" y2="{y(pct[b]):.1f}"/>')
    for c in seen:
        o = ev["by_grade"][c]
        cb = o is ev["career"]
        parts.append(f'<circle class="sr-pt{" sr-pt-cb" if cb else ""}" cx="{x[c]:.1f}" cy="{y(pct[c]):.1f}" r="{4 if cb else 3}"/>'
                     f'<text class="sr-pt-t{" sr-pt-cbt" if cb else ""}" x="{x[c]:.1f}" y="{y(pct[c]) - 8:.1f}" '
                     f'text-anchor="middle">{e(o["time"])}</text>')
    label = (f'{ev["short"]} season bests: '
             + ", ".join(f'{GRADE_NAME[c].lower()} {ev["by_grade"][c]["time"]}' for c in seen)
             + (f'; {ev["drop_pct"]:.1f}% faster than the first season' if ev["drop"] > 0 else ""))
    return (f'<svg class="sr-chart" viewBox="0 0 {W} {H}" role="img" aria-label="{e(label)}">'
            f'<title>{e(label)}</title>{"".join(parts)}</svg>')


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


def where(o):
    return f'{e(o["meet"])}, {e(o["date"])}' if o.get("meet") else e(o.get("date", ""))


def sec_head(s, key, ic, title, count=""):
    return (f'<h4 class="sr-h4 sr-sec-h" id="{s["slug"]}-{key}">{icon(ic)}{title}'
            f'{f" <span class=sr-count>{count}</span>" if count else ""}</h4>')


def prog_events(s):
    """The four-year stories first (most seasons), then by strength."""
    return sorted(s["events"], key=lambda ev: (-len(ev["by_grade"]), ev["strength"]))


def progression_section(s):
    if not s["events"]:
        return ""
    scale = chart_scale(s)
    multi = [ev for ev in s["events"] if len(ev["by_grade"]) >= 2 and ev["drop_pct"] >= 1.0]
    most = max(multi, key=lambda ev: ev["drop_pct"]) if multi else None
    heads = "".join(f'<span>{ABBR[c]}</span>' for c in GRADE_ORDER)
    rows = []
    for ev in prog_events(s):
        seen = [c for c in GRADE_ORDER if c in ev["by_grade"]]
        cells = []
        for c in GRADE_ORDER:
            o = ev["by_grade"].get(c)
            gl = f'<span class="visually-hidden">{GRADE_NAME[c]}: </span>'
            if not o:
                cells.append(f'<div class="sr-c sr-none">{gl}<span title="No {GRADE_NAME[c].lower()} time in our files">&ndash;</span>'
                             f'<span class="visually-hidden">no time in our files</span></div>')
                continue
            marks = []
            if "Open" in ev["records"] and o is ev["career"]:
                marks.append('<span class="sr-mark sr-gold">School record</span>')
            if c in ev["records"]:
                marks.append(f'<span class="sr-mark">{ABBR[c]} record</span>')
            elif ev["classes"].get(c):
                marks.append(f'<span class="sr-mark sr-green" title="#{ev["classes"][c]["rank"]} fastest ever as a '
                             f'{GRADE_NAME[c].lower()}">#{ev["classes"][c]["rank"]} {ABBR[c]}</span>')
            cb = o is ev["career"]
            cells.append(f'<div class="sr-c{" sr-cb" if cb else ""}">{gl}<span class="sr-t" title="{e(o["meet"])}, {e(o["date"])}">'
                         f'{e(o["time"])}</span>{"<span class=visually-hidden> (career best)</span>" if cb else ""}'
                         f'{"".join(marks)}</div>')
        if len(seen) >= 2 and ev["drop"] > 0:
            since = ABBR[ev["first"]["grade"]]
            chg = (f'<span class="sr-drop">&minus;{fmt_drop(ev["drop"])}</span>'
                   f'<span class="sr-drop-p">{ev["drop_pct"]:.1f}% since {since}</span>')
        elif len(seen) >= 2:
            chg = f'<span class="sr-drop-p">Fastest as a {ABBR[ev["career"]["grade"]].rstrip(".").lower()}.</span>'
        else:
            chg = ""
        tags = ""
        if ev is most:
            tags += '<span class="sr-chip">Most improved</span>'
        if ev["alltime"] and "Open" not in ev["records"]:
            tags += f'<span class="sr-chip sr-quiet">#{ev["alltime"]["rank"]} all-time</span>'
        chart = prog_chart(ev, scale)
        if len(seen) >= 3:
            prov = ('<details class="sr-when"><summary>Meets &amp; dates</summary><ul>'
                    + "".join(f'<li><span>{ABBR[c]}</span> <b>{e(ev["by_grade"][c]["time"])}</b> {where(ev["by_grade"][c])}</li>'
                              for c in seen) + "</ul></details>")
        else:
            prov = '<p class="sr-when-i">' + " &middot; ".join(
                f'{ABBR[c]} {where(ev["by_grade"][c])}' for c in seen) + "</p>"
        rows.append(f'<div class="sr-er{" sr-er-story" if chart else ""}">'
                    f'<div class="sr-er-n"><span class="sr-ev-n">{e(ev["short"])}</span>{tags}</div>'
                    f'<div class="sr-er-c">{"".join(cells)}</div>'
                    f'<div class="sr-er-d">{chg}</div>'
                    f'<div class="sr-er-v">{chart}{prov}</div></div>')
    n = len(s["events"])
    note = ("Each season&rsquo;s best time. The highlighted time is the career best. "
            "&ldquo;&ndash;&rdquo; means no time in our files for that season, not that there was no swim.")
    if any(len(ev["by_grade"]) >= 3 for ev in s["events"]):
        note += f" Charts show how much faster than the first season, all on the same 0&ndash;{scale}% scale; higher is faster."
    return (f'<section class="sr-sub" data-sec="prog">{sec_head(s, "prog", "trend", "Progression", f"{n} event" + ("s" if n != 1 else ""))}'
            f'<p class="sr-note">{note}</p>'
            f'<div class="sr-pg"><div class="sr-er sr-er-h" aria-hidden="true"><div class="sr-er-n">Event</div>'
            f'<div class="sr-er-c">{heads}</div><div class="sr-er-d">Change</div></div>{"".join(rows)}</div></section>')


def ev_key(name):
    from class_top10 import EVENTS
    return EVENTS.index(name) if name in EVENTS else 99


def records_section(s, shown):
    groups = []
    if s["open_records"]:
        groups.append(("School records", "".join(
            f'<li><span class="sr-chip sr-gold">School record</span> {e(r["event"])} <span class="sr-t">{e(r["time"])}</span>'
            f'<span class="sr-src">{where(r)}</span></li>' for r in s["open_records"])))
    if s["class_records"]:
        rows = sorted(s["class_records"], key=lambda r: (ev_key(r["event"]), GRADE_ORDER.index(r["kind"])))
        groups.append(("Class records", "".join(
            f'<li><span class="sr-chip">{GRADE_NAME[r["kind"]]} record</span> {e(r["event"])} <span class="sr-t">{e(r["time"])}</span>'
            f'<span class="sr-src">{where(r)}</span></li>' for r in rows)))
    at = sorted((ev for ev in s["events"] if ev["alltime"] and "Open" not in ev["records"]), key=lambda ev: ev["alltime"]["rank"])
    if at:
        groups.append(("All-time Top 10", "".join(
            f'<li><span class="sr-chip">#{ev["alltime"]["rank"]} all-time</span> {e(ev["event"])} '
            f'<span class="sr-t">{e(ev["alltime"]["time"])}</span></li>' for ev in at)))
    cls = sorted(((r["rank"], c, ev) for ev in s["events"] for c, r in ev["classes"].items() if c not in ev["records"]),
                 key=lambda x: (x[0], ev_key(x[2]["event"])))
    if cls:
        groups.append(("Class Top 10", "".join(
            f'<li><span class="sr-chip sr-quiet">#{rk} {GRADE_NAME[c].lower()}</span> {e(ev["event"])} '
            f'<span class="sr-t">{e(ev["classes"][c]["time"])}</span></li>' for rk, c, ev in cls)))
    other = [h for h in s["highlights"] if h[0] == 6 and h[2] not in ("Most improved event", "Swam at State") and h not in shown]
    if other:
        groups.append(("Also", "".join(f'<li><strong>{e(h[2])}</strong> {e(h[3])}</li>' for h in other)))
    if not groups:
        return ""
    total = len(s["records"])
    count = (f'{total} record{"s" if total != 1 else ""} &middot; {len(s["open_records"])} school &middot; '
             f'{len(s["class_records"])} class') if total else ""
    body = "".join(f'<h5 class="sr-h5">{t}</h5><ul class="sr-list">{li}</ul>' for t, li in groups)
    return f'<section class="sr-sub" data-sec="rec">{sec_head(s, "rec", "star", "Records &amp; rankings", count)}{body}</section>'


def state_label(x):
    if x["final"] and x["place"] == 1:
        return "State champion", " sr-gold"
    if x["final"] and x["place"]:
        return f'{ordinal(x["place"])} at State', " sr-gold" if x["place"] <= 3 else ""
    return (f'{ordinal(x["place"])} in prelims' if x["place"] else "Prelims"), " sr-quiet"


def state_section(s):
    meets = sorted((m for m in s["state_meets"] if m["swam"]), key=lambda m: m["year"])
    if not meets:
        return ""
    tiles, years = [], []
    for m in meets:
        mine = [x for x in s["state"] if x["year"] == m["year"]]
        fin = sorted((x for x in mine if x["final"] and x["place"]), key=lambda x: x["place"])
        titles = sum(1 for x in fin if x["place"] == 1)
        if titles:
            best = f'{titles} title{"s" if titles > 1 else ""}'
        elif fin:
            best = f'Best {ordinal(fin[0]["place"])}'
        else:
            best = "Prelims"
        gold = bool(titles or (fin and fin[0]["place"] <= 3) or (m["team"] and m["team"]["place"] == 1))
        anchor = f'{s["slug"]}-state-{m["year"]}'
        team_t = '<span class="sr-tile-x">Team champions</span>' if m["team"] and m["team"]["place"] == 1 else ""
        tiles.append(f'<a class="sr-tile{" sr-tile-gold" if gold else ""}" href="#{anchor}"><b>{m["year"]}</b>'
                     f'<span>{ABBR[m["grade"]]}</span><span class="sr-tile-r">{best}</span>{team_t}</a>')
        link = (f'<a href="{m["page"]}">{e(m["meet"])}</a>' if m["page"] else
                f'<a href="{e(m["source"])}" rel="noopener">{e(m["meet"])}</a>' if m["source"] else e(m["meet"]))
        team = ""
        if m["team"]:
            t = m["team"]
            pts = f' &middot; {t["points"]} pts' if t.get("points") is not None else ""
            team = (f'<span class="sr-chip sr-gold">{s["gender"].title()} team: State champions{pts}</span>'
                    if t["place"] == 1 else
                    f'<span class="sr-chip sr-quiet">{s["gender"].title()} team: {ordinal(t["place"])}{pts}</span>')
        ind = [x for x in mine if not x["relay"]]
        rel = [x for x in mine if x["relay"]]

        def li(x):
            lab, gold = state_label(x)
            mates = f'<span class="sr-src">with {e(and_list(x["mates"]))}</span>' if x.get("mates") else ""
            return (f'<li><span class="sr-chip{gold}">{e(lab)}</span> {e(x["short"])} '
                    f'<span class="sr-t">{e(x["time"])}</span>{mates}</li>')
        rows = ""
        if ind:
            rows += f'<h5 class="sr-h5">Individual</h5><ul class="sr-list">{"".join(li(x) for x in ind)}</ul>'
        if rel:
            rows += f'<h5 class="sr-h5">Relays</h5><ul class="sr-list">{"".join(li(x) for x in rel)}</ul>'
        years.append(f'<div class="sr-sy" id="{anchor}"><p class="sr-state-y"><strong>{m["year"]}</strong> '
                     f'&middot; {GRADE_NAME[m["grade"]].lower()} year &middot; {link}</p>'
                     f'{f"<p class=sr-state-team>{team}</p>" if team else ""}{rows}</div>')
    n = len(meets)
    return (f'<section class="sr-sub" data-sec="state">{sec_head(s, "state", "medal", "State Championships", f"{n} meet" + ("s" if n != 1 else ""))}'
            f'<nav class="sr-tiles" aria-label="State meets by year">{"".join(tiles)}</nav>{"".join(years)}</section>')


def relay_section(s):
    if not s["relays"]:
        return ""
    groups = []
    rec = [r for r in s["relays"] if r["rank"] == 1]
    top = sorted((r for r in s["relays"] if r["rank"] != 1), key=lambda r: r["rank"])

    def li(r):
        label = "School record" if r["rank"] == 1 else f'#{r["rank"]} all-time'
        gold = " sr-gold" if r["rank"] == 1 else ""
        more = f' &middot; on {r["count"]} of the list&rsquo;s times' if r["count"] > 1 else ""
        return (f'<li><span class="sr-chip{gold}">{label}</span> {e(r["event"])} <span class="sr-t">{e(r["time"])}</span>'
                f'<span class="sr-src">with {e(and_list(r["mates"]))}</span>'
                f'<span class="sr-src">{where(r)}{more}</span></li>')
    if rec:
        groups.append(("School relay records", "".join(li(r) for r in rec)))
    if top:
        groups.append(("On the all-time relay lists", "".join(li(r) for r in top)))
    body = "".join(f'<h5 class="sr-h5">{t}</h5><ul class="sr-list">{x}</ul>' for t, x in groups)
    n = len(s["relays"])
    return (f'<section class="sr-sub" data-sec="relay">{sec_head(s, "relay", "relay", "Relays", f"{n} on the all-time lists")}'
            f'<p class="sr-note">Each relay&rsquo;s best place on the team&rsquo;s all-time lists.</p>{body}</section>')


SEC_LABEL = {"prog": "Progression", "rec": "Records", "state": "State", "relay": "Relays"}


def card(s, year):
    hl = s["highlights"]
    shown = hl[:2]
    secs = [(k, html_) for k, html_ in (("prog", progression_section(s)), ("rec", records_section(s, shown)),
                                         ("state", state_section(s)), ("relay", relay_section(s))) if html_]
    detail = ""
    if secs:
        nav = "".join(f'<a href="#{s["slug"]}-{k}">{SEC_LABEL[k]}</a>' for k, _ in secs)
        detail = (f'<nav class="sr-secnav" aria-label="{e(s["name"])}: career sections">{nav}</nav>'
                  + "".join(h for _, h in secs))
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


# Keeps the open card's section links in step with what is on screen, and
# opens a card when a link points into it. Works without it: the links are
# plain anchors.
SECNAV_JS = """<script>
(function(){
  function openFor(h){var t=h&&document.getElementById(h.slice(1));var d=t&&t.closest('details.sr-more');if(d&&!d.open){d.open=true;t.scrollIntoView();}}
  window.addEventListener('hashchange',function(){openFor(location.hash)});openFor(location.hash);
  if(!('IntersectionObserver' in window))return;
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;
    var card=en.target.closest('.sr-card');card.querySelectorAll('.sr-secnav a').forEach(function(a){
      a.classList.toggle('on',a.getAttribute('href')==='#'+en.target.querySelector('.sr-sec-h').id);});});},
    {rootMargin:'-45% 0px -50% 0px'});
  document.querySelectorAll('.sr-sub').forEach(function(s){io.observe(s)});
})();
</script>"""


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
             (at_state, "senior who swam at State in their career", "seniors who swam at State in their careers"),
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
</div>{SECNAV_JS}'''


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
