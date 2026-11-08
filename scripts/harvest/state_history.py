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
TEAM = r"(?:Tanque Verde High School|TVHS)"
EVENT = re.compile(r"(?:Event\s+\d+|#\d+)\s+(Boys|Girls|Men|Women)\s+(\d+)\s+Yard\s+([A-Za-z ]+?)\)?\s*$")
TIME = re.compile(r"\bJ?(\d+:\d\d\.\d\d|\d?\d\.\d\d)\b|\b(DQ|NS|SCR|DFS)\b")
STROKE = {"Freestyle": "Freestyle", "Free": "Freestyle", "Backstroke": "Backstroke", "Back": "Backstroke",
          "Breaststroke": "Breaststroke", "Breast": "Breaststroke", "Butterfly": "Butterfly", "Fly": "Butterfly",
          "IM": "Individual Medley", "Individual Medley": "Individual Medley"}
NAME = re.compile(r"([A-Z][A-Za-z'\-]+(?: [A-Z][A-Za-z'\-]+)*, [A-Z][A-Za-z'\-.]+(?: [A-Z][A-Za-z'\-.]+)*)")


def canon(last_first):
    last, first = [x.strip() for x in last_first.split(",", 1)]
    n = f"{first} {last}"
    return ALIASES.get(n, n)


def event_name(dist, stroke):
    stroke = stroke.strip()
    if "Relay" in stroke:
        kind = "Medley" if "Medley" in stroke else "Free"
        return f"{dist} {kind} Relay", True
    if stroke not in STROKE:
        return None, False
    return f"{dist} {STROKE[stroke]}", False


def parse(lines):
    swims, problems = [], []
    gender = event = None
    relay = False
    section = "TF"
    i = 0
    while i < len(lines):
        line = lines[i]
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
            if relay:
                m = re.search(r"(?:^|\s)\*?(\d+|---)\s+" + TEAM + r"\s+(?:[A-Z]\s+)?(.*)$", line)
                if m:
                    times = [a or b for a, b in TIME.findall(m.group(2))]
                    names = []
                    for nxt in lines[i + 1:i + 4]:
                        if EVENT.search(nxt) or re.search(TEAM, nxt):
                            break
                        names += [canon(n) for n in NAME.findall(re.sub(r"\d\)", " ", nxt))]
                        if len(names) >= 4:
                            break
                    if len(names) != 4 or not times:
                        problems.append(f"{gender} {event}: relay line unreadable: {line.strip()} -> {names}")
                    else:
                        swims.append(dict(gender=gender, event=event, relay=True, round=section,
                                          place=None if m.group(1) == "---" else int(m.group(1)),
                                          time=times[-1], swimmers=names))
            else:
                m = re.search(r"\*?(\d+|---)\s+\*?" + NAME.pattern + r"\s+(?:(\d{2})\s+)?" + TEAM + r"\s+(.*)$", line)
                if not m:
                    problems.append(f"{gender} {event}: unreadable: {line.strip()}")
                else:
                    times = [a or b for a, b in TIME.findall(m.group(4))]
                    if not times:
                        problems.append(f"{gender} {event}: no time: {line.strip()}")
                    else:
                        swims.append(dict(gender=gender, event=event, relay=False, round=section,
                                          place=None if m.group(1) == "---" else int(m.group(1)),
                                          athlete=canon(m.group(2)), grade=m.group(3), time=times[-1]))
        i += 1
    return swims, problems


def team_places(lines):
    out, gender = {}, None
    for line in lines:
        m = re.search(r"(Men|Women) - Team Rankings", line)
        if m:
            gender = "boys" if m.group(1) == "Men" else "girls"
            continue
        m = re.search(r"(\d+)\.\s+Tanque Verde High School\s+([\d.]+)", line)
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
    ap.add_argument("--team-scores", help="JSON for team places when the file has none, with its source")
    a = ap.parse_args()
    swims, problems, teams = [], [], {}
    for t in a.txt:
        lines = Path(t).read_text(errors="ignore").splitlines()
        s, p = parse(lines)
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
    doc = {"year": a.year, "meet": a.meet, "date": a.date,
           "source": {"urls": a.source,
                      "files": [{"file": Path(f).name, "sha256": hashlib.sha256(Path(f).read_bytes()).hexdigest()}
                                for f in a.pdf]},
           "rounds": {"A": "championship final", "B": "consolation final", "P": "prelims only",
                      "TF": "timed final"},
           "team_scores": teams, "swims": uniq}
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
