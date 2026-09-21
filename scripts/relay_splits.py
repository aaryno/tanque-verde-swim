#!/usr/bin/env python3
"""
Choose the split breakdown to show under a relay record -- or none.

    select_entry(splits_data, gender, event, participants, time_str) -> entry | None

The splits file (data/historical_splits/all_relay_splits.json) carries a season,
the four swimmers and their legs, but no meet, no date and no total. Several
entries routinely match the same relay team. Until 2026-09-21 the two renderers
picked among them by list order (generate_website.py: first match) and by name
overlap (rebuild_relay_pages.py: best overlap -- it even parsed the record time
and then never used it), so the Overall Records page showed the boys 200 Medley
Relay record (1:41.80) with legs summing to 1:45.73: a different swim.

The rule here is arithmetic, not order:

  1. at least 3 of the 4 swimmers match, compared through the explicit alias
     table (data/swimmer_aliases.json) -- the raw harvest file is left as
     harvested, so a misspelled name in it still matches its canonical form;
  2. the legs add up to the record time, to the hundredth;
  3. exactly one distinct set of legs passes 1 and 2.

Anything else -- no candidate sums, or two different split sets both sum --
returns None and the record is shown WITHOUT splits. No splits is a gap; wrong
splits under a school record are a false statement.

scripts/check_relay_split_attachment.py stays the independent auditor; this
reuses its time parsing and tolerance so the two cannot disagree about what
"adds up" means.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_relay_split_attachment import entry_total, parse_time, TOLERANCE  # noqa: E402

_ALIASES = json.loads((Path(__file__).resolve().parent.parent / "data" / "swimmer_aliases.json").read_text())


def _canon(name):
    name = re.sub(r"\s*-\s*(Fr|So|Jr|Sr)\.?$", "", name.replace("**", ""), flags=re.IGNORECASE).strip()
    return _ALIASES.get(name, name).lower()


def select_entry(splits_data, gender, event, participants, time_str):
    target = parse_time(time_str.replace("**", ""))
    if target is None:
        return None
    wanted = {_canon(p) for p in participants.split(",")}
    passing = []
    for entry in splits_data.get(gender, []):
        if entry.get("type") != event:
            continue
        have = {_canon(s) for s in entry.get("swimmers", [])}
        if len(wanted & have) < 3:
            continue
        total = entry_total(entry)
        if total is not None and abs(total - target) <= TOLERANCE:
            passing.append(entry)
    if len({tuple(e.get("splits", [])) for e in passing}) == 1:
        return passing[0]
    return None
