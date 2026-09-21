#!/usr/bin/env python3
"""
Guard: the all-time Top 10 lists must reflect every published season list.

WHY THIS EXISTS
---------------
On 2026-09-20 tanqueverdeswim.org published a contradiction: /annual/2026-27.html
announced Kent Olsson's 5:03.13 as a new school record while
/top10/boys-alltime.html still showed 5:04.10 at #1 and Kent at #2 with an older
swim. Nothing was wrong with the website generator -- it faithfully rendered
records/top10-{gender}-alltime.md, which had been frozen for a long time because
scripts/build_alltime_top10.py was anchored on scripts/ and silently found zero
season files on every run.

The failure was silent in both directions: the rebuild never ran, and nothing
ever checked that it had. This guard closes the second half. It recomputes the
all-time lists in memory from the published season files and refuses to let a
stale list through.

It deliberately imports the ranking logic from build_alltime_top10 rather than
reimplementing it, so the checker and the builder cannot disagree about what
"top 10" means.

Exit 0 = current. Exit 1 = stale, and the report names the missing swims.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_alltime_top10 import (  # noqa: E402
    load_aliases,
    extract_events_from_file,
    build_alltime_top10,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
RECORDS_DIR = REPO_ROOT / "records"
ALIASES = REPO_ROOT / "data" / "swimmer_aliases.json"


def _key(entry):
    """Identity of a row for comparison: swimmer + time, ignoring provenance."""
    return (entry.get("athlete", "").strip(), entry.get("time", "").strip())


def check_gender(gender, aliases):
    """Return a list of human-readable staleness complaints for one gender."""
    alltime_path = RECORDS_DIR / f"top10-{gender}-alltime.md"
    if not alltime_path.exists():
        return [f"{alltime_path.relative_to(REPO_ROOT)} does not exist"]

    season_files = [
        f for f in sorted(RECORDS_DIR.glob(f"top10-{gender}-*.md"))
        if "alltime" not in f.name
    ]

    # Same inputs the builder uses: every season list, plus the existing
    # all-time file (which preserves swims from seasons that predate the
    # per-season markdown).
    collected = {}
    for filepath in season_files + [alltime_path]:
        for event, entries in extract_events_from_file(filepath, aliases).items():
            collected.setdefault(event, []).extend(entries)

    published = extract_events_from_file(alltime_path, aliases)

    problems = []
    for event, entries in sorted(collected.items()):
        expected = build_alltime_top10(entries, limit=10)
        actual = published.get(event, [])
        missing = [e for e in expected if _key(e) not in {_key(a) for a in actual}]
        for e in missing:
            rank = expected.index(e) + 1
            problems.append(
                f"{gender} {event}: #{rank} {e.get('time')} "
                f"{e.get('athlete')} ({e.get('date')}) is not on the all-time list"
            )
    return problems


def main():
    aliases = load_aliases(ALIASES)
    problems = []
    for gender in ("boys", "girls"):
        problems.extend(check_gender(gender, aliases))

    if not problems:
        print("✅ all-time Top 10 lists are current with every published season list")
        return 0

    print("❌ THE ALL-TIME TOP 10 LISTS ARE STALE")
    print()
    print(f"{len(problems)} swim(s) belong on the all-time lists but are missing.")
    print("Publishing now would put the site in contradiction with itself:")
    print()
    for p in problems:
        print(f"  • {p}")
    print()
    print("Fix, from the repo root:")
    print("    python3 scripts/build_alltime_top10.py")
    print("    python3 scripts/generate_website.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
