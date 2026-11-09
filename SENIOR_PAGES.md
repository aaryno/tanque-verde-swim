# Senior class pages — the formula

How `docs/seniors/class-of-<year>.html` is made, so every graduating class gets
the same page. First built for the Class of 2027 (PRs #31 and #32,
2026-11-08). Aaryn: "Love the way that page turned out - we need to save that
formula!"

This file is the authoritative procedure. The code carries the detail; this
file says what the page promises and how to make one.

## What the page promises

The success test, from the brief: *a parent opens the page, finds their
senior, feels proud of what their swimmer contributed, and shares it with
family — whether or not their swimmer holds a school record.* Celebrate the
class first, the individuals second, and records and statistics as the
supporting story.

1. **Class hero first.** Count of seniors (boys / girls) and class-wide
   accomplishments the data supports: State team titles, State event titles,
   school records held, class records, seniors who swam at State, seniors on
   the all-time Top 10.
2. **One card per senior, same layout for everyone.** Boys and girls
   sections, each alphabetical by last name. Never rank seniors by prestige.
3. **Achievements in prestige order** on each card: State (titles, team
   title, podium, finals, swam at State) → school (Open) records → class
   records → all-time Top 10 → class Top 10 → most improved event → senior
   season meets.
4. **Records count independently.** An Open record and the class record set
   by the same swim are two achievements. Regression case: Wade Olsson,
   Class of 2027, 10 records = 3 Open + 3 Senior + 1 Junior + 2 Sophomore +
   1 Freshman.
5. **Expandable career section** per card, which never repeats the collapsed
   highlights. Section links (Progression · Records · State · Relays; empty ones
   omitted) over four sections:
   - **Progression**, the centerpiece: one row per event with Fr / So / Jr / Sr
     columns, the career best highlighted, class records and class ranks marked,
     the change since the first season, and for 3+ seasons a chart on one
     zero-based "% faster than the first season" scale per card. "–" means no
     time in our files, never "did not swim".
   - **Records & rankings**: every school and class record with meet and date,
     all-time Top 10, class Top 10.
   - **State Championships**: year tiles, then each year with grade, team
     finish, individual swims and relays (with teammates) kept apart.
   - **Relays**: school relay records and places on the all-time lists.
   On desktop an open card spans the row.
   **Permalinks:** opening a card's career section puts `#<slug>` in the address
   bar (closing takes it out), and each section heading links to `#<slug>-<section>`;
   loading either opens the card and scrolls to it. The home page's senior cards
   link to `#<slug>`. The State page's swimmer cards work the same way (`#hawk-<slug>`).
6. **Every senior gets a meaningful card.** Non-record holders get the same
   treatment: strongest events, improvement, State appearances, meets.
7. **No fabrication.** Every fact is derived from the published files; a gap
   in the sources is a gap, never "did not happen". The page carries a
   coverage statement saying which seasons and sources it covers.
8. **Wording.** "State champion" for 1st, "State podium" for 2nd–3rd,
   "Nth at State" for other finals. Do not say "medal" until the AIA medal
   places are verified.
9. **Look.** Green and white with subtle gold, SVG stroke icons (no emoji),
   tabular numbers, no photos, works on phone (390px) and desktop.

## Where the facts come from

| Source | Gives |
|---|---|
| `records/records-{g}.md` | Open and class records, current holders |
| `records/relay-records-{g}.md` | relay lists; #1 is the record |
| `records/top10-{g}-alltime.md`, `class_top10.class_lists()` | all-time and class Top 10 |
| `records/top10-{g}-{season}.md` | each season's bests — the career history before 2026-27 |
| `data/meets/*.json` | every swim of Hy-Tek-imported meets (2026-27 on), incl. State |
| `data/state_history/<year>.json` | TV at earlier State meets: places, relay lineups, team finish |
| `data/season_*.json` | the roster (current class only) |

An earlier class has no roster file; its roster is the swimmers listed as SR in
that season's Top 10 lists, and the page says so.

## Code

- `scripts/senior_class_data.py` — derives each senior's facts. Run
  `python3 scripts/senior_class_data.py <YEAR>` to print every card's content
  and read it before rendering.
- `scripts/generate_senior_page.py` — renders the page. `--class YEAR --out PATH`
  makes a preview of any class without touching the live page.
- `scripts/check_senior_page.py` — the guard: roster vs cards, no empty card,
  record counts match `records-{g}.md`. `generate_website.py` refuses to build
  if it fails.
- `scripts/harvest/state_history.py` — adds a past State meet from its official
  Hy-Tek results PDF (see its docstring for three-column PDFs and
  `--team-scores`). Keep the PDFs in `~/workspaces/tv-swim/incoming/state-history/`.
- CSS: the "Senior class celebration page" section of `docs/css/style.css`
  (`.page-senior`, `.sr-*`).

## Making a page for a class

1. **State history.** For each of the class's four seasons, make sure
   `data/state_history/<year>.json` exists (the current season comes from
   `data/meets`). Missing → find the official results (AIA, or the PDFs
   SwimSwam posts), harvest them, and spot-check against the records files
   (a relay record's time and swimmers should match).
2. **Read the facts.** `python3 scripts/senior_class_data.py <YEAR>`. Check
   names (never merge on similarity — siblings share last names), grades, and
   any warnings.
3. **Preview.** `python3 scripts/generate_senior_page.py --class <YEAR> --out /tmp/c.html`,
   then screenshot desktop and phone width (390px via an iframe wrapper;
   headless Chrome will not go narrower than ~500px).
4. **Publish** with the usual routine: branch, BOARD announce with the rollback
   sha, PR, merge, poll the live page until it shows the change, BOARD receipt.
   A hand-built page already live (e.g. Class of 2026) is replaced only with
   Aaryn's go-ahead.

## Every class

`generate_website.py` builds a page for every class from `FIRST_CLASS` (2024, in
`generate_senior_page.py`) through the current seniors, and
`check_senior_page.py` guards each one. Classes 2024-2026 were added on
2026-11-08 (Aaryn: "Can we do this for the class of 2026, 2025, 2024, as
well?"), replacing the hand-built Class of 2026 page.

The coverage note names the State meets with official results and the ones
without. A State relay on the relay lists must match the official lineup
(`check_state_relays.py`).

## Open

- Official results for the 2020 and 2021 State meets (Classes of 2024 and
  2025). 2021 is on Meet Mobile and SwimCloud only; 2020 was a virtual meet.
