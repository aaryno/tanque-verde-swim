# Guards and fixes from the procedure proof

**Date:** 2026-09-20 (rebased onto `dcc2aa8` 2026-09-21)
**Order:** d88253b8-ee14-48af-8abc-a867329c9fc1
**Branch:** `worker/tv-swim-guards-and-fixes-2026-09-20`, branched from `9db90b6`, rebased onto `origin/main` = `dcc2aa8`
**Spec:** `git show 7eea78cb:artifacts/2026-09-20-procedure-proof.md`
**Not done, by instruction:** no merge, no push to `main`, no publish, no BOARD claim, and no record value, swimmer name, time, date or meet changed.

---

## VERDICT

Three guards built and demonstrated firing. One fix shipped. **One fix deliberately
NOT shipped**, because building the guard proved the published data is already wrong
and correcting it would change what the site says — which is Aaryn's call, not mine.

| # | Item | Outcome |
|---|------|---------|
| ⭐ Guard 1 | relay split mis-attachment | **guard shipped; deterministic re-attachment STOPPED — see §STOP** |
| Guard 1b | harvester emits a stable order | **shipped**, proven byte-identical to the committed file |
| Guard 2 | `class_records_history.json` duplicates | **shipped**; current file is clean (199 entries, 0 problems) |
| Guard 3 | extend the markdown linter | **shipped** — one cheap assertion, 0 new problems |
| ⭐ Fix 1 | orphaned 2026-27 Top-10 pages | **shipped** — reachable from 71/71 non-archive pages |

---

## ⛔ STOP — the deterministic re-attachment is not shipped, and here is why

The order said: make the attachment deterministic, but if the deterministic result
changes any published split or badge, **stop and report with evidence**. It does.
Measured, not argued.

### The independent test

`data/historical_splits/all_relay_splits.json` carries no date and no meet — only
`type`, `year` and swimmer names — so season alone cannot disambiguate: **9 record
rows have between 2 and 6 candidate entries inside their own season.** A team swims
the same relay lineup at many meets in one season.

But a relay's legs must add up to the relay's own time. That is a checksum on the
attachment that needs no extra data, and it is decisive:

```
for 51 record rows that got splits attached, how many candidates sum to the record time?
   exactly one : 41      <- a unique, verifiable identity exists
          none :  9
 more than one :  1
```

### What that test says about the live site

```
rows examined                                              60
rows that got a split breakdown attached                   51
attached splits that do NOT sum to the record's own time   47
    on docs/records/overall.html                           34
    on docs/records/{boys,girls}-relays.html               13
the two pages attach DIFFERENT entries to the same record  24 rows
```

**All three boys relay school records on `docs/records/overall.html` are showing a
different swim's splits right now**, and the relay page shows the correct one for the
same record:

| school record | record | splits published on overall.html sum to | splits published on boys-relays.html sum to |
|---|---:|---:|---:|
| 200 Medley Relay | 1:41.80 (101.80s) | **105.73s (+3.93)** | 101.80s (exact) |
| 200 Free Relay | 1:30.45 (90.45s) | **95.01s (+4.56)** | 90.45s (exact) |
| 400 Free Relay | 3:20.60 (200.60s) | **209.49s (+8.89)** | 200.60s (exact) |

Both pages are live. At most one can be right, and the sum says which.

**So a correct deterministic rule exists and I did not apply it.** Applying it would
rewrite the split breakdown on ~34 rows of `overall.html` and ~13 rows of the relay
pages — published content, on a site where merging to `main` *is* publishing (the
proof confirmed `source.branch=main`, `source.path=/docs`, no CI, no gate).

**This is Aaryn's decision.** The guard makes it visible and reproducible; it does not
make it for him. `python3 scripts/check_relay_split_attachment.py` prints all 47 rows
with the arithmetic.

---

## ⭐ Guard 1 — the relay split mis-attachment

### What it detects

`scripts/check_relay_split_attachment.py`, stdlib only, never edits a file, exits
non-zero on `ORDER_SENSITIVE` or `SUM_MISMATCH`.

| code | meaning | count on the committed tree |
|---|---|---:|
| `ORDER_SENSITIVE` | the pick changes if the candidate list is reversed — a re-harvest would rewrite this row | **48** |
| `SUM_MISMATCH` | attached splits do not add to the record's own time | 43 |
| `PAGE_DISAGREE` | `overall.html` and the relay page attach different entries to one record | 24 |
| `SEASON_MISMATCH` | attached a swim from a different season than the record's date | 28 |
| `AMBIGUOUS` | more than one candidate matched at all | 48 |
| `UNPARSEABLE` | a candidate carries an empty split value | 4 |

It models **both** renderers, because they do not agree with each other:
`generate_website.py:find_relay_splits` takes the **first** candidate;
`rebuild_relay_pages.py:find_splits_for_relay` takes the first at the **highest**
overlap. That difference alone is the source of the 24 `PAGE_DISAGREE` rows.

### Proof that it fires on the reordered input

The order forbids running `harvest_all_relay_splits.py` against the repo tree, so the
post-re-harvest file was reconstructed from the committed data by regrouping it into
the harvester's own `YEARS` order — same entries, same multiset, newest-season-first.
No network call, no harvester run.

```
$ python3 scripts/check_relay_split_attachment.py --quiet
ORDER_SENSITIVE=48 SUM_MISMATCH=43 PAGE_DISAGREE=24 SEASON_MISMATCH=28 AMBIGUOUS=48 UNPARSEABLE=4   exit 1

$ python3 scripts/check_relay_split_attachment.py --splits /tmp/g2/reordered_splits.json --quiet
ORDER_SENSITIVE=48 SUM_MISMATCH=44 PAGE_DISAGREE=18 SEASON_MISMATCH=27 AMBIGUOUS=48 UNPARSEABLE=1   exit 1
```

Read those two lines together — that is the whole defect in one measurement.
`ORDER_SENSITIVE` and `AMBIGUOUS` are **identical at 48**: the structural finding is
order-independent, which is what makes it a usable guard. Every other count **moves**,
because the reorder changed which swim got attached. The guard is stable; the render
is not.

And the render really does move. Rendered in a scratch `git archive` copy, never in
the repo tree:

```
$ diff -r docs-from-committed-splits docs-from-reordered-splits
3 files differ: records/boys-relays.html, records/girls-relays.html, records/overall.html
26 changed rows
```

Concrete, from `docs/records/overall.html`:

```
200 Medley Relay 1:41.80   committed : 28.05 | 27.24 | 25.96 | 24.48      (sums to 105.73 — wrong)
                           re-harvest: 28.12 | 27.30 | 24.56 | 21.82      (sums to 101.80 — exact)

200 Free Relay 1:43.71     committed : 26.69 | 27.73 | 25.96 | 26.08
                           re-harvest: 19.67 | 16.08 | 25.86 | 42.10      <- 16.08 for a 50 free
```

No relay time and no rank changes in either direction, which is exactly why nothing
else in the build notices.

### What was fixed (safely)

`harvest_all_relay_splits.py` now sorts its output season-ascending
(`in_stable_order`). The committed combined file already **is** stable-sorted
ascending with within-season order matching the per-season files, so:

```
re-sorted YEARS-order data == committed all_relay_splits.json, byte for byte: True
```

The reorder hazard is closed without moving a single published split. This does **not**
make the attachment correct — the match is still ambiguous, which is what the checker
reports.

Also fixed: `generate_website.py` read the splits file at a **CWD-relative** path.
Running the generator from anywhere but the repo root rendered every relay split blank
and exited 0. It is now anchored to the project root and raises if the file is missing.

---

## Guard 2 — `class_records_history.json` duplicate protection

`scripts/check_class_records_history.py`, stdlib, never edits the file.

Checks `DUPLICATE` (same `season, gender, event, grade, time`), `REGRADE` (same class
record slot twice at different times), `SELF_PREVIOUS` (a `previous` block naming the
record it replaced — the signature of the broken `add_2025_26_class_records.py`
template), `MISSING_FIELD`, `BAD_SEASON`.

### Current state of the committed file — reported, not changed

```
$ python3 scripts/check_class_records_history.py
  entries : 199
  no duplicate (season, gender, event, grade, time) tuples
  no repeated class-record slots, no self-referential previous entries
exit 0
```

**Clean. Nothing was removed and nothing needed to be.** This holds against the file
exactly as committed on `dcc2aa8`; `data/class_records_*.json` was not regenerated.

### Proof that it detects

```
A. append the 2026-27 entry twice (what a re-run of an uncommitted snippet does)
   DUPLICATE (1)  2 identical entries at indexes [198, 199]:
     season='2026-27' / gender='boys' / event='500 Freestyle' / grade='SO' / time='5:03.13'
   exit 1

B. the broken-template signature
   REGRADE (1)       same slot twice at different times ['5:03.13', '5:07.85']
   SELF_PREVIOUS (1) entry 199 lists itself as the previous record (Kent Olsson 5:07.85)
   exit 1
```

---

## Guard 3 — the linter extension

Cheap, and it fell straight out of Guard 1: **a relay row must name four distinct
swimmers.** Both renderers decide which swim to print by counting how many of a row's
participant names overlap a splits entry, with three of four enough to win — so a row
naming three swimmers, or naming one twice, silently changes the attachment. Pure table
structure, one block in the existing rank-table check.

```
$ python3 scripts/validate_records.py
validate_records: 287 tables OK          exit 0
```

**Linter count against `origin/main` (`dcc2aa8`): 0 problems. This branch: 0 problems.
Zero new problems.** The baseline of 3 quoted in the order was against `9db90b6`; PRs
#4 and #5 fixed all three while this work was queued, so there was nothing left for me
to leave alone.

Proof it fires — injecting a three-name row and a row listing Eli Stott twice into a
scratch copy raises the count to 5 and names both rows:

```
relay-records-boys.md: [200 Medley Relay] rank 9: 3 participants, expected 4: 'Nicholas Spilotro, Titan Flint, Eli Stott'
relay-records-boys.md: [200 Medley Relay] rank 10: swimmer listed twice in one relay: Eli Stott
```

---

## ⭐ Fix 1 — the orphaned 2026-27 Top-10 pages

### Why the nav was inconsistent

Three scripts render the same two dropdowns onto every page, and each kept its own
copy of the season list:

| script | Top 10 by Year | Summary by Year |
|---|---|---|
| `generate_website.py` | derived (PR #1) | 15-season literal |
| `generate_annual_pages.py` | derived (PR #1) | from the `SEASONS` literal |
| `rebuild_relay_pages.py` | **18-season literal, stops at 2024-25** | **14-season literal, stops at 2025-26** |

PR #1 fixed two of three. PR #6 later added 🏅 Class Top 10 and 🎓 Seniors to all
three navs but did not touch the season literals, so the relay pages stayed behind.

`scripts/site_seasons.py` now holds the derivation and all three import it. A season
is linked exactly when the file that produces its page is committed — PR #1's rule —
so the menu can never link a page that was not built, and a new season needs no edit.
2025-26 stays absent from the Top-10 menu for the right reason: its source files do
not exist. (Another worker is adding them under order 20d998e2; when they land, the
menu picks 2025-26 up with no code change. Those files were not touched here.)

### Result

```
non-archive pages audited: 71
  🏅 Class Top 10     present on 71/71
  🎓 Seniors          present on 71/71
  2026-27 Top-10      present on 71/71     (was 69/71)
  2026-27 Summary     present on 71/71     (was 69/71)
```

The 58 pages under `docs/archive/` are a frozen Dec-2025 snapshot that no script
generates and none were touched. `docs/index.html` is hand-maintained and was already
in sync with both derived lists — it remains the only hand-maintained nav on the site.

---

## VALIDATION

### Determinism — green

```
$ python3 scripts/generate_website.py && python3 scripts/rebuild_relay_pages.py   # twice
diff -r run1 run2  ->  BYTE-IDENTICAL
```

### Full `docs/` diff, every line classified

```
 docs/records/boys-relays.html  | 2 ++
 docs/records/girls-relays.html | 2 ++
 2 files changed, 4 insertions(+), 0 deletions(-)

  1  + <li><a class="dropdown-item" href="/top10/boys-2026-27.html">2026-27</a></li>    nav, intended
  1  + <li><a class="dropdown-item" href="/top10/girls-2026-27.html">2026-27</a></li>   nav, intended
  2  + <li><a class="dropdown-item" href="/annual/2026-27.html">2026-27</a></li>        nav, intended
```

**Zero removed lines. Zero added or removed files. No footer-year or "Generated on"
churn.** No record value, split, badge, rank, name, time, date or meet changed —
verified by the diff being 4 lines long and all four being `<li>` nav links.

### Guards

```
check_alltime_current                exit 0
class_top10                          exit 0
apply_aliases --check                exit 0
check_class_records_history          exit 0
validate_records                     exit 0   (287 tables OK)
check_relay_split_attachment         exit 1   <- reporting the defect it exists to find
```

`check_relay_split_attachment` is advisory in the build: `generate_website.py` prints
its report to **stderr** in a `!!!`-banner block and continues, because the site must
stay generatable while the underlying question is open. It exits non-zero standalone,
which is what a gate should call.

### Harvester

`harvest_all_relay_splits.py` was **not** run against the repo tree, per the order.
The stable-order claim was verified arithmetically against the committed file, and the
render comparison was done in a `git archive` scratch copy whose output was never
committed.

---

## Conflicts hit in the rebase, and how each was resolved

Rebased `--onto origin/main 9db90b6` with the `docs/` commit dropped and regenerated
afterwards, as instructed.

| # | File | Conflict | Resolution |
|---|---|---|---|
| 1 | `scripts/generate_website.py` | my `import subprocess` against main's new `import os` / `sys.path.insert` / `senior_href` header | kept both; main's `sys.path.insert(0, scripts/)` makes my `from site_seasons import ...` work from any CWD, so it is strictly better than what I branched from |
| 2 | `scripts/validate_records.py` | my relay participant-count block landed on the same lines as PR #5's new one-per-athlete duplicate check | **kept both** — they are independent and target disjoint tables (`one_per_athlete` for top-10 lists, `'Participants' in header` for relay tables). Main's block first, mine after |
| 3 | `scripts/generate_annual_pages.py`, `scripts/rebuild_relay_pages.py` | none — git auto-merged. Verified by audit rather than trust: 🏅 and 🎓 are present in all three generators and on 71/71 rendered pages |
| 4 | `docs/` | dropped commit `9307e3d` entirely and re-rendered. Main's `docs/` was already in sync with its sources, so the regeneration produced only my own 4 nav lines |

Guard 1's counts shifted slightly across the rebase (`SUM_MISMATCH` 42→43,
`PAGE_DISAGREE` 27→24, `UNPARSEABLE` 3→4) because PR #5 canonicalized swimmer names in
`records/relay-records-*.md`, which changes the name-overlap matching. The conclusion
is unchanged and `ORDER_SENSITIVE=48` is identical before and after.

---

## Found and NOT changed — Aaryn's decisions

1. **The 47 wrong split attachments now live on the site**, including all three boys
   relay school records on `docs/records/overall.html`. A correct rule exists (§STOP).
   Fixing it changes published content. **Not mine to decide.**
2. **`overall.html` and the relay pages use different tie-breaks** — first-wins versus
   highest-overlap — so they can disagree about the same record, and on 24 rows they
   do. Making them agree is the same decision as (1).
3. **9 record rows have no splits entry that sums to their time**, and 4 candidate
   entries carry empty split values (a 20-21 girls 400 Free Relay entry has four blank
   legs). That is missing source data, not a rendering bug; re-harvesting those seasons
   is a data decision.
4. **`data/historical_splits/{boys,girls}_relay_splits.json` are committed in the old
   newest-first order** and differ from the combined file's ordering. Nothing reads
   them, so the render is unaffected and I left them alone; the next harvest will
   rewrite them in the new stable order.
5. **`scripts/add_2025_26_class_records.py` is still documented as a template** in
   `claude.md` and still has the `if '2025' in date` calendar-year gate. Guard 2 now
   detects its output, but the script itself is untouched — the proof lists fixing it
   as open build work.
6. **`claude.md` documents the `class_records_history.json` swimmer field as
   `swimmer`; the file uses `name`.** Doc-only drift, not changed.
7. **A pre-existing `SyntaxWarning`** on `generate_website.py`'s
   `markdown_to_html_table` docstring (`"\s"` in a non-raw string). Cosmetic, prints on
   every build, out of scope — left alone.

---

*Every number above is the output of a command run in this sandbox. Nothing is
projected. The harvester was never run against the repo tree, and no file under
`records/`, `data/` or `docs/` carries a changed record value.*
