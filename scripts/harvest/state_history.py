#!/usr/bin/env python3
"""
Tanque Verde's results at past AIA State Championships, from the official
Hy-Tek results PDFs, into data/state_history/<year>.json.

    python3 scripts/harvest/state_history.py <year> <results.txt> [...] --meet NAME --date YYYY-MM-DD \
        --source URL [--source URL] [--pdf file.pdf ...]

Input is the PDF's text (pdftotext -layout). A three-column Hy-Tek PDF (2024)
must be cut into its columns first, so that each column reads top to bottom:

    for p in $(seq 1 N); do
      pdftotext -layout -f $p -l $p -x 0   -y 0 -W 202 -H 792 in.pdf - >> cols.txt
      pdftotext -layout -f $p -l $p -x 202 -y 0 -W 200 -H 792 in.pdf - >> cols.txt
      pdftotext -layout -f $p -l $p -x 402 -y 0 -W 210 -H 792 in.pdf - >> cols.txt
    done

Kept, for TV only: every individual swim with its round (A final, B final,
prelims) and place, every relay with its place and four swimmers, and the
team's place and points when the file has team rankings.

Places are the official ones printed in the file. Nothing is inferred: a swim
whose line cannot be read is reported and left out, never guessed.

Added 2026-11-08 on Aaryn's direction that the senior page list achievements
from past years -- "previous year state championship team title in 2025,
plus some were on a winning relay and had other state medals".
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "state_history"
ALIASES = json.loads((ROOT / "data" / "swimmer_aliases.json").read_text())
TEAM = r"(?:Tanque Verde(?: High School| HS)?|TVHS)"
GRADES = {"FR": "09", "SO": "10", "JR": "11", "SR": "12"}
EVENT = re.compile(r"(?:Event\s+\d+|#\d+)\s+(Boys|Girls|Men|Women)\s+(\d+)\s+Yard\s+([A-Za-z ]+?)\)?\s*$")
TIME = re.compile(r"\bJ?(\d+:\d\d\.\d\d|\d?\d\.\d\d)\b|\b(DQ|NS|SCR|DFS)\b")
STROKE = {"Freestyle": "Freestyle", "Free": "Freestyle", "Backstroke": "Backstroke", "Back": "Backstroke",
          "Breaststroke": "Breaststroke", "Breast": "Breaststroke", "Butterfly": "Butterfly", "Fly": "Butterfly",
          "IM": "Individual Medley", "Individual Medley": "Individual Medley"}
# "Last, First [Middle]". Older files put a letter grade right after the name
# ("Kappler, Samantha SO"), so a grade is never taken as a name word; a middle
# initial is read but dropped (canon).
_W = r"(?!(?:FR|SO|JR|SR)\b)[A-Z][A-Za-z'\-.]*"
NAME = re.compile(r"([A-Z][A-Za-z'\-]+(?: [A-Z][A-Za-z'\-]+)*,\s+" + _W + r"(?: " + _W + r")*)")


def canon(last_first):
    last, first = [x.strip() for x in last_first.split(",", 1)]
    words = first.split()
    while len(words) > 1 and re.fullmatch(r"[A-Z]\.?", words[-1]):
        words.pop()  # middle initial
    n = f"{' '.join(words)} {last}"
    return ALIASES.get(n, n)


def event_name(dist, stroke):
    stroke = stroke.strip()
    if "Relay" in stroke:
        kind = "Medley" if "Medley" in stroke else "Free"
        return f"{dist} {kind} Relay", True
    if stroke not in STROKE:
        return None, False
    return f"{dist} {STROKE[stroke]}", False


def round_by_columns(listing, n_times, place, lanes):
    """Round from the listing a row sits in and how many times it carries, for
    files whose "A - Final" / "B - Final" headings do not survive text
    extraction (2007-2009). In the finals listing ("Prelim Time  Finals Time") a
    row with both times swam a final -- A for places 1..lanes, B after; a row
    with one time swam prelims only. Every row of the prelims listing ("Seed
    Time  Prelim Time") is a prelim swim."""
    if listing == "F":
        if n_times >= 2 and place:
            return "A" if place <= lanes else "B"
        return "P"
    return listing


def parse(lines, lanes=None, relays_without_names=False):
    swims, problems = [], []
    gender = event = None
    relay = False
    section = "TF"
    listing = "TF"
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.search(r"Prelim Time\s+Finals Time", line):
            listing = "F"
        elif re.search(r"Seed Time\s+Prelim Time", line):
            listing = "P"
        elif re.search(r"Seed Time\s+Finals Time", line):
            listing = "TF"
        m = EVENT.search(line)
        if m:
            g = {"Boys": "boys", "Men": "boys", "Girls": "girls", "Women": "girls"}[m.group(1)]
            ev, rel = event_name(m.group(2), m.group(3))
            cont = "..." in line
            if not cont or (ev, g) != (event, gender):
                gender, event, relay = g, ev, rel
                if not cont:
                    section = "TF"
            if cont:
                s = line.split("...")[0].strip()
                section = {"A - Final": "A", "B - Final": "B", "Preliminaries": "P"}.get(s, section)
            i += 1
            continue
        st = re.sub(r"^\S?\s+", "", line).strip() if re.match(r"^\S\s{2,}", line) else line.strip()
        if st in ("A - Final", "B - Final", "Preliminaries"):
            section = {"A - Final": "A", "B - Final": "B", "Preliminaries": "P"}[st]
            i += 1
            continue
        if event and re.search(TEAM, line):
            if len(re.findall(TEAM, line)) > 1 or re.search(r"Team (?:Rankings|Scores)", line):
                i += 1
                continue  # a team-score line ("13  Tanque Verde High School  Tanque Verde High School  63")
            if relay:
                m = re.search(r"(?:^|\s)\*?(\d+|---)\s+" + TEAM + r"\s+(?:'?[A-Z]'?\s+)?(.*)$", line)
                if m:
                    times = [a or b for a, b in TIME.findall(m.group(2))]
                    names = []
                    for nxt in lines[i + 1:i + 4]:
                        if EVENT.search(nxt) or re.search(TEAM, nxt):
                            break
                        names += [canon(n) for n in NAME.findall(re.sub(r"\d\)", " ", nxt))]  # grade words never match NAME
                        if len(names) >= 4:
                            break
                    if (len(names) != 4 or not times) and not (relays_without_names and not names and times):
                        problems.append(f"{gender} {event}: relay line unreadable: {line.strip()} -> {names}")
                    else:
                        place = None if m.group(1) == "---" else int(m.group(1))
                        rnd = round_by_columns(listing, len(re.findall(r"\d+:\d\d\.\d\d|\d?\d\.\d\d", m.group(2))),
                                               place, lanes) if lanes else section
                        swims.append(dict(gender=gender, event=event, relay=True, round=rnd,
                                          place=place, time=times[-1], swimmers=names))
                        if not lanes and listing == "F" and rnd in ("A", "B") and len(times) >= 2 \
                                and re.fullmatch(r"\d+:\d\d\.\d\d|\d?\d\.\d\d", times[-2]):
                            swims.append(dict(gender=gender, event=event, relay=True, round="P", place=None,
                                              time=times[-2], swimmers=names, inline=True))
            else:
                m = re.search(r"\*?(\d+|---)\s+\*?" + NAME.pattern + r"\s+(?:(\d{2}|FR|SO|JR|SR)\s+)?" + TEAM + r"\b\s*(.*)$", line)
                if not m:
                    problems.append(f"{gender} {event}: unreadable: {line.strip()}")
                else:
                    times = [a or b for a, b in TIME.findall(m.group(4))]
                    if not times:
                        problems.append(f"{gender} {event}: no time: {line.strip()}")
                    else:
                        place = None if m.group(1) == "---" else int(m.group(1))
                        rnd = round_by_columns(listing, len(re.findall(r"\d+:\d\d\.\d\d|\d?\d\.\d\d", m.group(4))),
                                               place, lanes) if lanes else section
                        swims.append(dict(gender=gender, event=event, relay=False, round=rnd,
                                          place=place,
                                          athlete=canon(m.group(2)), grade=GRADES.get(m.group(3), m.group(3)),
                                          time=times[-1]))
                        # Older layouts (2010-2021) print a finalist's prelim and final on one
                        # row ("Prelim Time  Finals Time"); keep the prelim swim too. The row
                        # gives no prelim place. (2007-2009 list prelims separately: --lanes.)
                        if not lanes and listing == "F" and rnd in ("A", "B") and len(times) >= 2 \
                                and re.fullmatch(r"\d+:\d\d\.\d\d|\d?\d\.\d\d", times[-2]):
                            swims.append(dict(gender=gender, event=event, relay=False, round="P", place=None,
                                              athlete=canon(m.group(2)), grade=GRADES.get(m.group(3), m.group(3)),
                                              time=times[-2], inline=True))
        i += 1
    # An inline prelim is kept only when the file has no prelims listing of its
    # own for that swim (2025 has both; 2023 only the inline one).
    def key(x):
        return (x["gender"], x["event"], x.get("athlete") or tuple(x["swimmers"]), x["time"])
    listed = {key(x) for x in swims if x["round"] == "P" and not x.get("inline")}
    swims = [x for x in swims if not (x.get("inline") and key(x) in listed)]
    for x in swims:
        x.pop("inline", None)
    return swims, problems


def team_places(lines):
    """TV's place and points per gender from the file's team scores. Three
    layouts: "Men - Team Rankings" with "13. Tanque Verde High School 63"
    (one or two columns), and "Boys - Team Scores" with the team named twice
    ("13  Tanque Verde High School  Tanque Verde High School  63"). Combined
    boys+girls tables are skipped. The last table in the file wins, so an
    interim "Through Event 25" table is overridden by the final one."""
    out, gender = {}, None
    for line in lines:
        m = re.search(r"\b(Men|Women|Boys|Girls)\b[ -]*Team (?:Rankings|Scores)", line)
        if m:
            gender = "boys" if m.group(1) in ("Men", "Boys") else "girls"
            continue
        if re.search(r"Combined Team Scores", line):
            gender = None
            continue
        m = (re.search(r"(\d+)\.\s+" + TEAM + r"\s+([\d.]+)(?:\s|$)", line)
             or re.search(r"^\s*(\d+)\s+" + TEAM + r"\s+" + TEAM + r"\s+([\d.]+)\s*$", line))
        if m and gender:
            pts = float(m.group(2))
            out[gender] = {"place": int(m.group(1)), "points": int(pts) if pts == int(pts) else pts}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("year", type=int)
    ap.add_argument("txt", nargs="+")
    ap.add_argument("--meet", required=True)
    ap.add_argument("--date", required=True, help="final day, YYYY-MM-DD")
    ap.add_argument("--source", action="append", required=True)
    ap.add_argument("--pdf", action="append", default=[])
    ap.add_argument("--lanes", type=int, help="final heat size; set it when the round headings are unreadable "
                    "(2007-2009) so the round comes from the listing and the places instead (round_by_columns)")
    ap.add_argument("--relays-without-names", action="store_true",
                    help="the file prints relays with no swimmers (2018): keep them with an empty lineup")
    ap.add_argument("--note", action="append", default=[],
                    help="a known gap in this file, shown with the State coverage (e.g. finals only)")
    ap.add_argument("--team-scores", help="JSON for team places when the file has none, with its source")
    a = ap.parse_args()
    swims, problems, teams = [], [], {}
    for t in a.txt:
        lines = Path(t).read_text(errors="ignore").splitlines()
        s, p = parse(lines, a.lanes, a.relays_without_names)
        swims += s
        problems += p
        teams.update(team_places(lines))
    # One entry per swim: the same swim can appear twice in a file (e.g. a
    # column repeated at a page break).
    seen, uniq = set(), []
    for s in swims:
        k = json.dumps(s, sort_keys=True)
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    # A DQ, scratch or no-show is not a swim: keep it out of the swims, like the
    # meet importer does, but on file. (2026-11-09: a 2017 relay DQ showed on the
    # Class of 2021 page as "Prelims ... DQ".)
    excluded = [x for x in uniq if not re.fullmatch(r"\d+:\d\d\.\d\d|\d?\d\.\d\d", x["time"])]
    uniq = [x for x in uniq if x not in excluded]
    doc = {"year": a.year, "meet": a.meet, "date": a.date,
           "source": {"urls": a.source,
                      "files": [{"file": Path(f).name, "sha256": hashlib.sha256(Path(f).read_bytes()).hexdigest()}
                                for f in a.pdf]},
           "rounds": {"A": "championship final", "B": "consolation final", "P": "prelims only",
                      "TF": "timed final"},
           "team_scores": teams, "swims": uniq}
    if a.note:
        doc["notes"] = a.note
    if excluded:
        doc["excluded"] = [dict(x, result=x.pop("time")) for x in excluded]
    if a.team_scores:
        doc["team_scores"].update(json.loads(a.team_scores))
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{a.year}.json"
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    for p in problems:
        print("  ⚠️ ", p)
    print(f"{out.relative_to(ROOT)}: {len(uniq)} TV swims, team {teams}, {len(problems)} unreadable line(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
