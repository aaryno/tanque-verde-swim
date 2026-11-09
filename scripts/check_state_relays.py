#!/usr/bin/env python3
"""
Guard: every State-meet relay on records/relay-records-{g}.md has the
swimmers the official results give it, for each year in data/state_history/.

Added 2026-11-08: the 2022 State relays on the lists came from a MaxPreps
harvest that swapped lineups between relays (e.g. the girls 1:43.75 200 Free
Relay listed Ryann Lightcap for Paisley White). The official AIA results
(data/state_history/2022.json) settled them. Order of swimmers is not checked;
membership and event are.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def problems():
    aliases = json.loads((ROOT / "data" / "swimmer_aliases.json").read_text())
    canon = lambda n: aliases.get(n.strip(), n.strip())
    t = lambda x: x.lstrip("0") if x.startswith("0") else x
    official = {}
    for f in sorted((ROOT / "data" / "state_history").glob("*.json")):
        d = json.loads(f.read_text())
        for s in d["swims"]:
            if s["relay"]:
                official.setdefault((s["gender"], t(s["time"]), d["year"]), []).append(s)
    out = []
    for g in ("boys", "girls"):
        ev = None
        for line in (ROOT / "records" / f"relay-records-{g}.md").read_text().splitlines():
            if line.startswith("## "):
                ev = line[3:].strip()
                continue
            c = [x.strip().strip("*").strip() for x in line.strip().strip("|").split("|")]
            if len(c) < 5 or "State" not in c[4] or not re.search(r"\d{4}", c[3]):
                continue
            year = int(re.search(r"(\d{4})", c[3]).group(1))
            if not (ROOT / "data" / "state_history" / f"{year}.json").exists():
                continue
            names = {canon(n) for n in c[2].split(",")}
            match = [o for o in official.get((g, t(c[1]), year), [])
                     if o["event"] == ev and set(o["swimmers"]) == names]
            if not match:
                got = official.get((g, t(c[1]), year))
                out.append(f"{g} {ev} {c[1]} ({year}): list has {sorted(names)}; official: "
                           + ("; ".join(f"{o['event']} {sorted(o['swimmers'])}" for o in got) if got else "no such swim"))
    return out


def main():
    p = problems()
    for x in p:
        print("  ❌", x)
    if not p:
        print("✅ State relays on the relay lists match the official results")
    return 1 if p else 0


if __name__ == "__main__":
    sys.exit(main())
