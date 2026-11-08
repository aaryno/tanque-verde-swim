#!/usr/bin/env python3
"""
Everything the senior class page says about one graduating class, derived from
the published record files. Nothing here is hand-entered.

    python3 scripts/senior_class_data.py [CLASS_YEAR]   # print what each senior's card will say

Sources, and what each can and cannot tell us:

  records/records-{g}.md            school (Open) and class records, current holders
  records/relay-records-{g}.md      the team's all-time relay lists; #1 is the record
  records/top10-{g}-alltime.md      all-time Top 10
  class_top10.class_lists()         fastest ever swum as a FR / SO / JR / SR
  records/top10-{g}-{season}.md     each season's team Top 10. A swimmer's career
                                    history comes from here, so a swim that missed
                                    its season's team Top 10 is not known to us.
  data/meets/*.json                 every posted swim of the meets imported from
                                    Hy-Tek (2026-27 on), including State places.

A gap in these sources is a gap, not a lack of achievement: the page says what
it covers and never turns "not in our files" into "did not happen".

The roster: the current class comes from data/season_*.json (MaxPreps roster,
stated grades). An earlier class, which has no roster file, is derived from the
swimmers listed as SR in that season's Top 10 lists -- complete only for
swimmers who made a Top 10 list, and labelled that way on the page.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from class_top10 import _tables, class_lists, EVENTS, GRADES, seconds  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RECORDS = REPO / "records"
DATA = REPO / "data"

GRADE_CODE = {"Freshman": "FR", "Sophomore": "SO", "Junior": "JR", "Senior": "SR", "Open": "Open",
              "Fr.": "FR", "So.": "SO", "Jr.": "JR", "Sr.": "SR"}
GRADE_NAME = dict(GRADES)
SHORT = {"50 Freestyle": "50 Free", "100 Freestyle": "100 Free", "200 Freestyle": "200 Free",
         "500 Freestyle": "500 Free", "100 Backstroke": "100 Back", "100 Breaststroke": "100 Breast",
         "100 Butterfly": "100 Fly", "200 Individual Medley": "200 IM"}
RELAY_SHORT = {"200 Medley Relay": "200 Medley Relay", "200 Free Relay": "200 Free Relay",
               "400 Free Relay": "400 Free Relay"}


def tidy(t):
    """'00:58.11' / '01:04.09' / '58.11' -> '58.11' / '1:04.09'."""
    t = re.sub(r"[*_]", "", str(t)).strip()
    if ":" in t:
        m, s = t.split(":", 1)
        return s if int(m) == 0 else f"{int(m)}:{s}"
    return t


def nice_date(d):
    """Accepts 'Oct 24, 2026' or '11/7/2026' -> 'Oct 24, 2026'."""
    for f in ("%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            x = datetime.strptime(d, f)
            return f"{x:%b} {x.day}, {x.year}"
        except ValueError:
            pass
    return d


def date_key(d):
    for f in ("%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(d, f)
        except ValueError:
            pass
    return datetime.min


def career_seasons(year):
    """Class of 2027 -> [('2023-24','FR'), ('2024-25','SO'), ('2025-26','JR'), ('2026-27','SR')]."""
    return [(f"{y - 1}-{y % 100:02d}", code) for y, (code, _) in zip(range(year - 3, year + 1), GRADES)]


def season_file(season):
    p = DATA / f"season_{season}.json"
    return json.loads(p.read_text()) if p.exists() else None


def roster(year):
    """{'boys': [...], 'girls': [...]}, plus where it came from."""
    season = career_seasons(year)[-1][0]
    sf = season_file(season)
    if sf and sf.get("roster"):
        r = sf["roster"]
        return ({"boys": list(r.get("seniors_boys", [])), "girls": list(r.get("seniors_girls", []))},
                "roster")
    out = {}
    for g in ("boys", "girls"):
        names = set()
        p = RECORDS / f"top10-{g}-{season}.md"
        if p.exists():
            for _, header, rows in _tables(p):
                if "Year" in header:
                    names |= {r[header.index("Athlete")] for r in rows if r[header.index("Year")] == "SR"}
        out[g] = sorted(names)
    return out, "top10"


def last_name_key(name):
    parts = name.split()
    return (parts[-1].lower(), name.lower())


def meet_docs(season):
    sf = season_file(season)
    docs = []
    for p in sorted((DATA / "meets").glob("*.json")):
        d = json.loads(p.read_text())
        if sf and not (sf["season_start"] <= d["date"] <= sf["season_end"]):
            continue
        if not sf:
            y0 = int(season[:4])
            if not (f"{y0}-08-01" <= d["date"] <= f"{y0 + 1}-07-31"):
                continue
        d["_page"] = f"/meets/{p.stem}.html"
        docs.append(d)
    return docs


def senior(name, gender, year, ctx):
    """One senior's facts. ctx carries the per-gender lists, loaded once."""
    s = {"name": name, "gender": gender, "slug": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
         "warnings": []}
    expected = dict(career_seasons(year))

    # 1. Season bests per event, from the season Top 10 lists and the posted meets.
    obs = []  # (event, season, grade, time, date, meet)
    for season, code in career_seasons(year):
        p = RECORDS / f"top10-{gender}-{season}.md"
        if p.exists():
            for event, header, rows in _tables(p):
                if event not in EVENTS or "Year" not in header:
                    continue
                for r in rows:
                    if r[header.index("Athlete")] != name:
                        continue
                    if r[header.index("Year")] != code:
                        s["warnings"].append(f"{season} {event}: listed as {r[header.index('Year')]}, expected {code}")
                        continue
                    obs.append(dict(event=event, season=season, grade=code, time=tidy(r[header.index("Time")]),
                                    date=nice_date(r[header.index("Date")]), meet=r[header.index("Meet")]))
        for d in ctx["meets"].get(season, []):
            for x in d.get("individual", []):
                if x["athlete"] == name and x.get("gender") == gender and x["event"] in EVENTS:
                    obs.append(dict(event=x["event"], season=season, grade=code, time=tidy(x["time"]),
                                    date=nice_date(x["date"]), meet=d["meet"]))
    # Records are observations too: a record swim is always in the history.
    records = []
    for event, header, rows in _tables(RECORDS / f"records-{gender}.md"):
        if "Grade" not in header:
            continue
        for r in rows:
            if r[header.index("Athlete")] != name:
                continue
            code = GRADE_CODE.get(r[header.index("Grade")], r[header.index("Grade")])
            rec = dict(event=event, kind=code, time=tidy(r[header.index("Time")]),
                       date=nice_date(r[header.index("Date")]), meet=r[header.index("Meet")])
            records.append(rec)
            if code in expected.values():
                season = next(se for se, c in expected.items() if c == code)
                obs.append(dict(event=event, season=season, grade=code, time=rec["time"],
                                date=rec["date"], meet=rec["meet"]))
    order = {e: i for i, e in enumerate(EVENTS)}
    grade_order = {c: i for i, (c, _) in enumerate(GRADES)}
    records.sort(key=lambda r: (order.get(r["event"], 99), r["kind"] == "Open", grade_order.get(r["kind"], 9)))
    s["records"] = records
    s["open_records"] = [r for r in records if r["kind"] == "Open"]
    s["class_records"] = [r for r in records if r["kind"] != "Open"]

    best = {}  # (event, grade) -> obs
    for o in obs:
        k = (o["event"], o["grade"])
        if k not in best or seconds(o["time"]) < seconds(best[k]["time"]):
            best[k] = o
    events = {}
    for (event, grade), o in best.items():
        events.setdefault(event, {})[grade] = o
    s["events"] = []
    for event in sorted(events, key=lambda e: order.get(e, 99)):
        by_grade = events[event]
        career = min(by_grade.values(), key=lambda o: seconds(o["time"]))
        seq = [by_grade[c] for c, _ in GRADES if c in by_grade]
        first = seq[0]
        drop = seconds(first["time"]) - seconds(career["time"]) if career is not first else 0.0
        rec_kinds = [r["kind"] for r in records if r["event"] == event]
        top = ctx["alltime_top1"].get(event)
        s["events"].append(dict(
            event=event, short=SHORT.get(event, event), by_grade=by_grade, career=career, first=first,
            drop=round(drop, 2), drop_pct=(drop / seconds(first["time"]) * 100) if drop > 0 else 0.0,
            records=rec_kinds,
            strength=(seconds(career["time"]) / seconds(top)) if top else 9.0,
            alltime=ctx["alltime"].get((event, name)),
            classes={c: ctx["class_rank"].get((c, event, name)) for c, _ in GRADES
                     if ctx["class_rank"].get((c, event, name))}))
    s["strongest"] = sorted(s["events"], key=lambda e: e["strength"])

    # 2. State, from the posted State meet(s).
    state = []
    for season, _ in career_seasons(year):
        for d in ctx["meets"].get(season, []):
            if "state" not in d["meet"].lower():
                continue
            mine = {}
            for x in d.get("individual", []):
                if x["athlete"] == name and x.get("gender") == gender:
                    k = x["event"]
                    if k not in mine or x.get("round") == "Final":
                        mine[k] = x
            for ev, x in mine.items():
                state.append(dict(event=ev, short=SHORT.get(ev, ev), relay=False, round=x.get("round"),
                                  place=x.get("place"), time=tidy(x["time"]), meet=d["meet"], page=d["_page"],
                                  year=d["date"][:4]))
            for r in d.get("relay", []):
                if name in r.get("participants", []) and r.get("gender") == gender:
                    state.append(dict(event=r["event"], short=r["event"], relay=True, round="Final",
                                      place=r.get("place"), time=tidy(r["time"]), meet=d["meet"],
                                      page=d["_page"], year=d["date"][:4],
                                      mates=[p for p in r["participants"] if p != name]))
    def pl(x):
        try:
            return int(x["place"])
        except (TypeError, ValueError):
            return 99
    s["state"] = sorted(state, key=lambda x: (pl(x) if x["round"] == "Final" else 50 + pl(x), x["relay"]))
    # Years they swam at State, from any listed swim (a positive record only; see module doc).
    s["state_years"] = sorted({o["date"][-4:] for o in obs if "state" in o["meet"].lower()})

    # 3. Relays on the all-time relay lists.
    relays = []
    for event, rows in ctx["relays"].items():
        mine = [(int(r["rank"]), r) for r in rows if name in r["participants"]]
        if mine:
            rank, r = min(mine, key=lambda x: x[0])
            relays.append(dict(event=event, rank=rank, time=tidy(r["time"]), date=nice_date(r["date"]),
                               meet=r["meet"], mates=[p for p in r["participants"] if p != name],
                               count=len(mine)))
    s["relays"] = sorted(relays, key=lambda r: r["rank"])

    # 4. Posted meets this (senior) season.
    sr_season = career_seasons(year)[-1][0]
    s["meets_this_season"] = sorted({d["meet"] for d in ctx["meets"].get(sr_season, [])
                                     for x in d.get("individual", []) + d.get("relay", [])
                                     if x.get("athlete") == name or name in x.get("participants", [])})
    s["seasons_listed"] = sorted({o["season"] for o in obs})
    s["highlights"] = highlights(s)
    return s


def ordinal(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def and_list(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def highlights(s):
    """Ordered by prestige: (tier, gold, title, detail). Tier 1 is the most prestigious."""
    out = []
    titles = [x for x in s["state"] if x["round"] == "Final" and str(x["place"]) == "1"]
    if titles:
        out.append((1, True, "State champion" if len(titles) == 1 else f"{len(titles)}× State champion",
                    and_list(x["short"] for x in titles)))
    finals = [x for x in s["state"] if x["round"] == "Final" and str(x["place"]) != "1"
              and str(x["place"]).isdigit()]
    if finals:
        out.append((1, False, "State finals", and_list(f"{ordinal(x['place'])} {x['short']}" for x in finals)))
    prelim_only = [x for x in s["state"] if x["round"] != "Final"]
    if prelim_only and not finals and not titles:
        out.append((1, False, "Swam at State", and_list(x["short"] for x in prelim_only)))
    if s["open_records"]:
        out.append((2, True, "School record" + ("s" if len(s["open_records"]) > 1 else ""),
                    and_list(f"{SHORT.get(r['event'], r['event'])} {r['time']}" for r in s["open_records"])))
    relay_recs = [r for r in s["relays"] if r["rank"] == 1]
    if relay_recs:
        out.append((2, True, "School relay record" + ("s" if len(relay_recs) > 1 else ""),
                    and_list(r["event"] for r in relay_recs)))
    if s["class_records"]:
        n = len(s["class_records"])
        out.append((3, False, f"{n} class record" + ("s" if n > 1 else ""),
                    and_list(f"{GRADE_NAME[r['kind']]} {SHORT.get(r['event'], r['event'])}" for r in s["class_records"])))
    at = sorted((e for e in s["events"] if e["alltime"]), key=lambda e: e["alltime"]["rank"])
    if at:
        out.append((4, False, "All-time Top 10", and_list(f"#{e['alltime']['rank']} {e['short']}" for e in at)))
    rel10 = [r for r in s["relays"] if 1 < r["rank"] <= 10]
    if rel10:
        out.append((4, False, "All-time relay Top 10", and_list(f"#{r['rank']} {r['event']}" for r in rel10)))
    cls = []
    for e in s["events"]:
        if e["classes"]:
            c, r = min(e["classes"].items(), key=lambda kv: kv[1]["rank"])
            cls.append((r["rank"], f"#{r['rank']} {GRADE_NAME[c].lower()} {e['short']}"))
    if cls and not at:
        out.append((5, False, "Class Top 10", and_list(t for _, t in sorted(cls)[:3])))
    imp = sorted((e for e in s["events"] if e["drop_pct"] >= 1.0), key=lambda e: -e["drop_pct"])
    if imp:
        e = imp[0]
        out.append((6, False, "Most improved event",
                    f"{e['short']}: {e['first']['time']} as a {GRADE_NAME[e['first']['grade']].lower()} "
                    f"to {e['career']['time']} as a {GRADE_NAME[e['career']['grade']].lower()}"))
    if s["meets_this_season"] and len(out) < 3:
        out.append((6, False, "Senior season", "swam at " + and_list(s["meets_this_season"])))
    if s["state_years"] and not s["state"]:
        out.append((6, False, "Swam at State", and_list(s["state_years"])))
    return out


def context(gender, year):
    ctx = {"meets": {se: meet_docs(se) for se, _ in career_seasons(year)}}
    ctx["alltime"], ctx["alltime_top1"] = {}, {}
    for event, header, rows in _tables(RECORDS / f"top10-{gender}-alltime.md"):
        for r in rows:
            k = (event, r[header.index("Athlete")])
            if k not in ctx["alltime"]:
                ctx["alltime"][k] = dict(rank=int(r[header.index("Rank")]), time=tidy(r[header.index("Time")]))
        if rows:
            ctx["alltime_top1"][event] = rows[0][header.index("Time")]
    ctx["class_rank"] = {}
    for code, lists in class_lists(gender).items():
        for event, rows in lists.items():
            for i, r in enumerate(rows, 1):
                ctx["class_rank"].setdefault((code, event, r["athlete"]), dict(rank=i, time=tidy(r["time"])))
    ctx["relays"] = {}
    for event, header, rows in _tables(RECORDS / f"relay-records-{gender}.md"):
        if "Participants" not in header:
            continue
        ctx["relays"][event] = [dict(rank=r[header.index("Rank")], time=r[header.index("Time")],
                                     participants=[p.strip() for p in r[header.index("Participants")].split(",")],
                                     date=r[header.index("Date")], meet=r[header.index("Meet")]) for r in rows]
    return ctx


def senior_class(year):
    names, source = roster(year)
    out = {"year": year, "roster_source": source, "boys": [], "girls": []}
    for g in ("boys", "girls"):
        ctx = context(g, year)
        out[g] = [senior(n, g, year, ctx) for n in sorted(names[g], key=last_name_key)]
    sr_season = career_seasons(year)[-1][0]
    sf = season_file(sr_season)
    out["season"] = sr_season
    out["season_meets"] = [d["meet"] for d in sorted(meet_docs(sr_season), key=lambda d: d["date"])]
    out["season_complete"] = None
    if sf:
        from site_seasons import season_complete
        out["season_complete"] = season_complete(sf)
    return out


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2027
    c = senior_class(year)
    print(f"Class of {year}: roster from {c['roster_source']}; season {c['season']} complete={c['season_complete']}")
    for g in ("boys", "girls"):
        for s in c[g]:
            print(f"\n{s['name']} ({g}) — {len(s['records'])} records "
                  f"({len(s['open_records'])} Open, {len(s['class_records'])} class); seasons {s['seasons_listed']}")
            for t, gold, title, detail in s["highlights"]:
                print(f"  T{t}{'*' if gold else ' '} {title}: {detail}")
            print("  strongest:", ", ".join(f"{e['short']} {e['career']['time']}" for e in s["strongest"][:3]))
            for w in s["warnings"]:
                print("  WARN", w)
