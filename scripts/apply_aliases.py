#!/usr/bin/env python3
"""
Apply the swimmer alias table to EVERY published list, and deduplicate.

    python3 scripts/apply_aliases.py           # rewrite records/*.md in place
    python3 scripts/apply_aliases.py --check   # report only; exit 1 if anything would change

Identity comes only from data/swimmer_aliases.json -- an explicit table a human
maintains one entry at a time. There is deliberately no fuzzy matching: on this
team the Radomsky sisters and brothers, the Alitiem sisters, the Caballero
brothers and the Lightcap siblings all have near-identical names and are
different swimmers. A similarity threshold would merge real athletes.

What it does, per file type under records/ (plus name-only canonicalization of
the JSON under data/ that feeds rendered pages):

  top10-*.md (individual, incl. all-time)
      Canonicalize every athlete name, keep each swimmer's FASTEST row, sort by
      time, re-rank 1..n. A top-10 holds each swimmer once.
  relay-records-*.md
      Canonicalize every participant name. Drop only EXACT duplicates (same
      time, date and set of swimmers) -- the same four swimmers can legitimately
      hold two different rows. Sort by time, re-rank.
  records-*.md, annual-summary-*.md
      Canonicalize names only.

Removing a duplicate cannot backfill the slot: the swimmer who would be next
is not in the markdown, and the raw per-swim data lives outside this repo. A
deduplicated list may therefore be shorter than 10. That is the honest result.

Idempotent: a second run changes nothing, so --check passing means the lists
are clean.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RECORDS = REPO / "records"
ALIASES = json.loads((REPO / "data" / "swimmer_aliases.json").read_text())

# Only real remappings; identity entries need no replacement. Longest first so
# a longer variant is never shadowed by a shorter one.
_VARIANTS = sorted((v for v, c in ALIASES.items() if v != c), key=len, reverse=True)
_NAME_RE = (re.compile(r"(?<![A-Za-z])(" + "|".join(map(re.escape, _VARIANTS)) + r")(?![A-Za-z])")
            if _VARIANTS else None)


def canon_text(text):
    """Replace every known misspelling, as a whole name, anywhere in text."""
    return _NAME_RE.sub(lambda m: ALIASES[m.group(1)], text) if _NAME_RE else text


def seconds(t):
    # Record rows are rendered bold (**01:41.80**). Strip markup before parsing,
    # or a bold row reads as unparseable, sorts as infinitely slow, and the
    # record-holder lands at the bottom of the list.
    t = re.sub(r"[*_`]", "", t).strip()
    try:
        if ":" in t:
            m, s = t.split(":", 1)
            return int(m) * 60 + float(s)
        return float(t)
    except ValueError:
        return float("inf")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def fmt(row):
    return "| " + " | ".join(row) + " |"


def rewrite_table(header, rows, kind):
    """Return the table's data rows after dedupe/sort/re-rank for its kind."""
    if kind not in ("individual", "relay") or "Rank" not in header or "Time" not in header:
        return rows, []
    ri, ti = header.index("Rank"), header.index("Time")
    notes = []
    ordered = sorted(rows, key=lambda r: seconds(r[ti]))  # stable: ties keep order
    kept, seen = [], {}
    for r in ordered:
        if kind == "individual":
            key = r[header.index("Athlete")]
        else:
            people = frozenset(p.strip() for p in r[header.index("Participants")].split(","))
            key = (r[ti], r[header.index("Date")], people)
        if key in seen:
            notes.append(f"dropped {r[ti]} {r[header.index('Athlete') if kind == 'individual' else header.index('Participants')]}"
                         f" (duplicate of kept {seen[key]})")
            continue
        seen[key] = r[ti]
        kept.append(r)
    for i, r in enumerate(kept, 1):
        # Keep the rank cell's decoration (a bold record row stays bold).
        m = re.match(r"^(\D*)\d+(\D*)$", r[ri])
        r[ri] = f"{m.group(1)}{i}{m.group(2)}" if m else str(i)
    return kept, notes


def process(path):
    name = path.name
    kind = ("individual" if name.startswith("top10-") else
            "relay" if name.startswith("relay-records-") else "names")
    original = path.read_text(encoding="utf-8")
    lines = canon_text(original).split("\n")
    out, notes, i, event = [], [], 0, None
    while i < len(lines):
        ln = lines[i]
        h = re.match(r"^#{2,3}\s+(.+?)\s*$", ln)
        if h:
            event = h.group(1)
        is_header = (ln.startswith("|") and i + 1 < len(lines)
                     and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]))
        if not is_header:
            out.append(ln); i += 1; continue
        header = cells(ln)
        out += [ln, lines[i + 1]]
        i += 2
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            rows.append(cells(lines[i])); i += 1
        before = [fmt(r) for r in rows]
        kept, n = rewrite_table(header, [list(r) for r in rows], kind)
        after = [fmt(r) for r in kept]
        out += after if after != before else [l for l in lines[i - len(rows):i]]
        notes += [f"[{event}] {x}" for x in n]
    result = "\n".join(out)
    return original, result, notes


def process_json(path):
    """Canonicalize names inside a JSON data file. Text-level on purpose: a
    load/dump round-trip would reformat the whole file; this changes only the
    misspelled names and leaves every other byte alone."""
    original = path.read_text(encoding="utf-8")
    return original, canon_text(original), []


# JSON that feeds rendered pages: annual summaries, relay and class-record
# history, and the season landing page. swimmer_aliases.json is the table
# itself and must never be rewritten by it.
DATA = REPO / "data"
JSON_SOURCES = sorted(p for p in DATA.glob("*.json") if p.name != "swimmer_aliases.json")


def main():
    check = "--check" in sys.argv
    changed = 0
    targets = [(p, process) for p in sorted(RECORDS.glob("*.md"))] + \
              [(p, process_json) for p in JSON_SOURCES]
    for path, fn in targets:
        original, result, notes = fn(path)
        if result == original:
            continue
        changed += 1
        print(f"{'would change' if check else 'rewrote'}: {path.relative_to(REPO)}")
        for n in notes:
            print(f"    {n}")
        if not check:
            path.write_text(result, encoding="utf-8")
    if check and changed:
        print(f"\n❌ {changed} file(s) carry known misspellings or duplicate swimmers.")
        print("Fix, from the repo root:  python3 scripts/apply_aliases.py")
        return 1
    print(f"✅ aliases applied to every list ({changed} file(s) {'need changes' if check else 'rewritten'})"
          if not check else "✅ every list is canonical and deduplicated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
