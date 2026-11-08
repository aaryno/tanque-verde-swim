#!/usr/bin/env python3
"""
Guard for the senior class page (generate_senior_page.py).

    python3 scripts/check_senior_page.py

Fails when:
  * a rostered senior has no card on the page, or the page has a card for
    someone not on the roster;
  * a senior's card would be empty -- every senior gets a meaningful card
    (Aaryn, 2026-11-08), so an empty one means the data lookup broke;
  * records are deduplicated: an Open record and the class record set by the
    same swim are two achievements. Regression case: Wade Olsson, Class of
    2027 -- 3 Open + 7 class = 10 (Senior 500 Free, Fr/So/Sr 100 Breast,
    So/Jr/Sr 200 IM, Open 500 Free/100 Breast/200 IM). Checked against the
    records file itself, so it stays true as records change.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from class_top10 import _tables  # noqa: E402
from senior_class_data import senior_class, roster  # noqa: E402
from generate_senior_page import senior_class_year  # noqa: E402

REPO = Path(__file__).resolve().parent.parent


def main():
    year = senior_class_year()
    names, _ = roster(year)
    c = senior_class(year)
    page = (REPO / "docs" / "seniors" / f"class-of-{year}.html").read_text()
    bad = []
    for g in ("boys", "girls"):
        if sorted(names[g]) != sorted(s["name"] for s in c[g]):
            bad.append(f"{g}: roster {sorted(names[g])} != cards {sorted(s['name'] for s in c[g])}")
        for s in c[g]:
            if f'id="{s["slug"]}"' not in page:
                bad.append(f"{s['name']}: no card on the page")
            if not s["highlights"] and not s["events"]:
                bad.append(f"{s['name']}: empty card")
            held = sum(1 for _, h, rows in _tables(REPO / "records" / f"records-{g}.md") if "Grade" in h
                       for r in rows if r[h.index("Athlete")] == s["name"])
            if held != len(s["records"]):
                bad.append(f"{s['name']}: records file has {held} record rows, card counts {len(s['records'])}")
    if page.count('class="sr-card"') != sum(len(names[g]) for g in names):
        bad.append(f"page has {page.count('class=\"sr-card\"')} cards for {sum(len(names[g]) for g in names)} seniors")
    for b in bad:
        print("⛔", b)
    if bad:
        return 1
    print(f"senior page: {sum(len(c[g]) for g in ('boys', 'girls'))} seniors, every card has content, records counted independently")
    return 0


if __name__ == "__main__":
    sys.exit(main())
