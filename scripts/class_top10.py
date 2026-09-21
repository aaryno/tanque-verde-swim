#!/usr/bin/env python3
"""
Class Top 10: the fastest Tanque Verde swims ever swum AS a freshman, sophomore,
junior or senior, per event. The #1 of each list is the class record.

    python3 scripts/class_top10.py     # check the class records against the lists

DERIVED, NEVER COMMITTED. generate_website.py builds these pages from the
published lists on every render, so there is no intermediate file for a season
update to forget -- the lesson of the all-time lists, which went stale for
years because their source had to be rebuilt by hand.

Inputs (all already canonicalized by apply_aliases.py):
  records/top10-{gender}-*.md   every season list plus all-time; the Year
                                column is the swimmer's grade on the day
  records/records-{gender}.md   the official class records, merged in so a
                                record from before the season lists still
                                appears at #1

One entry per swimmer per list, at their fastest. Limitation, stated rather
than hidden: a swim that missed its own season's top 10 is not in the inputs,
so a deep list can omit it. #1 is unaffected -- the record is merged directly.

The check: if a published swim is faster than the official class record for
its grade, the record page is stale -- a class record was set and never
written down. That is refused, the same way a stale all-time list is.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECORDS = REPO / "records"

GRADES = [("FR", "Freshman"), ("SO", "Sophomore"), ("JR", "Junior"), ("SR", "Senior")]
EVENTS = ["50 Freestyle", "100 Freestyle", "200 Freestyle", "500 Freestyle",
          "100 Backstroke", "100 Breaststroke", "100 Butterfly", "200 Individual Medley"]


def _plain(s):
    return re.sub(r"[*_`]", "", s).strip()


def seconds(t):
    t = _plain(t)
    try:
        if ":" in t:
            m, s = t.split(":", 1)
            return int(m) * 60 + float(s)
        return float(t)
    except ValueError:
        return float("inf")


def _tables(path):
    """Yield (event, header, rows) for every markdown table under a heading."""
    event, header, rows = None, None, []
    for line in path.read_text(encoding="utf-8").split("\n") + [""]:
        h = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if line.startswith("|"):
            cells = [_plain(c) for c in line.strip().strip("|").split("|")]
            if header is None:
                header = cells
            elif not set("".join(cells)) <= set("-: "):
                rows.append(cells)
            continue
        if header is not None:
            yield event, header, rows
            header, rows = None, []
        if h:
            event = h.group(1)


def official_records(gender):
    """{(event, 'SO'): row} from records-{gender}.md; Open rows are skipped."""
    by_name = {name: code for code, name in GRADES}
    out = {}
    for event, header, rows in _tables(RECORDS / f"records-{gender}.md"):
        if "Grade" not in header:
            continue
        for r in rows:
            code = by_name.get(r[header.index("Grade")])
            if code:
                out[(event, code)] = {
                    "time": r[header.index("Time")], "athlete": r[header.index("Athlete")],
                    "year": code, "date": r[header.index("Date")], "meet": r[header.index("Meet")],
                }
    return out


def class_lists(gender):
    """{grade_code: {event: [row, ...]}} -- best swim per athlete, fastest first."""
    swims = {}  # (grade, event, athlete) -> row
    def offer(event, row):
        k = (row["year"], event, row["athlete"])
        if k not in swims or seconds(row["time"]) < seconds(swims[k]["time"]):
            swims[k] = row
    for path in sorted(RECORDS.glob(f"top10-{gender}-*.md")):
        for event, header, rows in _tables(path):
            if event not in EVENTS or "Year" not in header:
                continue
            for r in rows:
                year = r[header.index("Year")]
                if year in dict(GRADES):
                    offer(event, {"time": r[header.index("Time")], "athlete": r[header.index("Athlete")],
                                  "year": year, "date": r[header.index("Date")],
                                  "meet": r[header.index("Meet")]})
    for (event, code), row in official_records(gender).items():
        offer(event, row)
    lists = {code: {} for code, _ in GRADES}
    for (code, event, _), row in swims.items():
        lists[code].setdefault(event, []).append(row)
    for code in lists:
        for event in lists[code]:
            lists[code][event] = sorted(lists[code][event], key=lambda r: seconds(r["time"]))[:10]
    return lists


def to_markdown(gender, code):
    name = dict(GRADES)[code]
    lists = class_lists(gender)[code]
    out = [f"# {gender.title()} {name} Top 10", ""]
    for event in EVENTS:
        rows = lists.get(event)
        if not rows:
            continue
        out += [f"## {event}", "", "| Rank | Time | Athlete | Year | Date | Meet |",
                "|-----:|-----:|---------|------|------|------|"]
        out += [f"| {i} | {r['time']} | {r['athlete']} | {r['year']} | {r['date']} | {r['meet']} |"
                for i, r in enumerate(rows, 1)]
        out.append("")
    return "\n".join(out)


def stale_records():
    """Published swims faster than the official class record for their grade."""
    problems = []
    for gender in ("boys", "girls"):
        official = official_records(gender)
        for code, events in class_lists(gender).items():
            for event, rows in events.items():
                rec = official.get((event, code))
                top = rows[0]
                if rec and seconds(top["time"]) < seconds(rec["time"]):
                    problems.append(
                        f"{gender} {dict(GRADES)[code]} {event}: {top['time']} {top['athlete']} "
                        f"({top['date']}) beats the recorded class record {rec['time']} {rec['athlete']}")
                if not rec:
                    problems.append(f"{gender} {dict(GRADES)[code]} {event}: no class record on file, "
                                    f"fastest published swim is {top['time']} {top['athlete']}")
    return problems


def main():
    problems = stale_records()
    if not problems:
        print("✅ every class record matches the fastest published swim for its grade")
        return 0
    print("❌ CLASS RECORDS ARE STALE")
    print()
    for p in problems:
        print(f"  • {p}")
    print()
    print("Update records/records-{boys,girls}.md, then regenerate the site.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
