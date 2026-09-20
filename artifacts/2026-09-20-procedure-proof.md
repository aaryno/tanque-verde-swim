# End-to-end update procedure — proof run

**Date:** 2026-09-20
**Order:** b7c3c707-b954-43c4-a253-c78f5f47d48c
**Base:** `9db90b6` (merge of PR #1 and PR #2 into `main`)
**Where this ran:** `/tmp/proof-b7c3c707*` — scratch copies made with `git archive HEAD | tar -x`.
Nothing in `records/`, `data/` or `docs/` in the repo was modified. No PR, no merge, no push to `main`, no publish.

---

## VERDICT

**(B) PROVEN EXCEPT FOR NAMED LINKS.**

Six of the seven links run today, from the repo alone, with the commands recorded below.
**One link does not exist: there is no command in this repository that writes a harvested
result into `records/records-{boys,girls}.md` or into `data/class_records_history.json`.**
Tonight's 500 Freestyle record row was a hand edit, and the `class_records_history.json`
entry was a one-off snippet that is not in the repo. Both are confirmed below by running
every candidate script and recording how each one fails.

Two further defects were found by running things rather than reasoning about them, and both
are live on tanqueverdeswim.org right now:

* **Re-running the relay-splits harvester silently attaches the wrong swims to historical
  relay records.** The prior assessment predicted duplication; duplication is refuted, and
  what actually happens is worse and quieter. 23 lines across 3 pages, including
  `docs/records/overall.html`.
* **The committed `docs/` is stale against its own sources.** Regenerating adds a 2026-27
  Top-10 nav link to 43 pages that the live site does not currently have.

---

## Link-by-link

| # | Link | Command | Ran? | Exit | Produced | Repeatable from the repo alone? |
|---|------|---------|------|------|----------|--------------------------------|
| 1 | PROVISION | `python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt && ./.venv/bin/playwright install chromium` | yes | **0** | Python 3.14.5; pandas 3.0.6, playwright 1.63.0, beautifulsoup4 4.15.0, requests 2.34.2, pdfplumber 0.11.10; chromium installed | **Yes** |
| 2 | HARVEST RELAY SPLITS | `python3 scripts/harvest/harvest_all_relay_splits.py` | yes | **0** | 463 relays over 15 seasons (`26-27: B=3 G=6`); 18 JSON files | **Yes**, with a re-run hazard — see §Re-run safety |
| 3 | HARVEST RESULTS (URL confirmation) | stdlib `urlopen` against both MaxPreps URLs | yes | **0** | see §3 | **Yes** |
| 4a | HARVEST → `records/top10-*-2026-27.md` | `python3 scripts/harvest/harvest_maxpreps_season.py --season 26-27 --out <json> --write-top10 <dir> --in-progress-note "<note>"` | yes | **0** | 41 individual + 9 relay rows; both top-10 files **byte-identical to committed** | **Yes** — committed script, proven |
| 4b | HARVEST → `records/records-{boys,girls}.md` | *no such command exists* | n/a | n/a | — | **NO — this is the broken link** |
| 4c | HARVEST → `data/class_records_history.json` | *no working command exists* | yes (all candidates) | see §4c | corrupt output at exit 0 | **NO** |
| 5 | RENDER | `python3 scripts/generate_website.py` ×2 | yes | **0, 0** | `diff -r` across the two runs: **BYTE-IDENTICAL** | **Yes** |
| 6 | PUBLISH | not performed, by instruction | no | — | mechanism confirmed from the GitHub API, §6 | **Yes** (mechanism verified) |
| 7 | RE-RUN SAFETY | full chain ×2 | yes | **0** | §Re-run safety | chain is idempotent **from pass 1 onward**; pass 1 itself is destructive |

---

## 3 · Which MaxPreps URL carries data — confirmed, both genders

Fetched 2026-09-20, stdlib `urlopen`, no playwright required (the pages are server-rendered).

| URL | HTTP | Bytes | `Athlete Stats have not been entered` | Carries results |
|-----|------|-------|---------------------------------------|-----------------|
| `…/swimming/fall/26-27/` (boys landing) | 200 | 235,142 | **yes** | no — `05:03.13` absent |
| `…/swimming/fall/26-27/stats/` (boys) | 200 | 172,126 | no | **yes** — `05:03.13` present |
| `…/swimming/girls/fall/26-27/` (girls landing) | 200 | 237,670 | **yes** | no — no `Best Times` table |
| `…/swimming/girls/fall/26-27/stats/` (girls) | 200 | 181,754 | no | **yes** — `Best Times` present |

The landing page reports "Athlete Stats have not been entered" while the `/stats/` page one
click away carries the full meet. Confirmed for both genders. Use `/stats/`.

---

## 4 · The crux: how `records/*-2026-27.md` and the 500 Free row were actually produced

Three different mechanisms were used tonight, and only one of them is a repeatable command.

### 4a · `records/top10-{boys,girls}-2026-27.md` — a committed script. REPEATABLE. ✅

Mechanism: `scripts/harvest/harvest_maxpreps_season.py --write-top10`, added in `77bbb54`.

Proven, not inferred. From a clean `git archive` of `HEAD`:

```
$ python3 scripts/harvest/harvest_maxpreps_season.py --season 26-27 \
    --out /tmp/.../harvest-26-27b.json \
    --write-top10 /tmp/.../records-step4b \
    --in-progress-note "⚠️ Season in progress. Covers 1 meet swum through Sep 20, 2026; …"
  wrote …/top10-boys-2026-27.md (17 swims)
  wrote …/top10-girls-2026-27.md (24 swims)
wrote 41 individual, 9 relay rows to …
EXIT=0

$ cmp committed regenerated
BYTE-IDENTICAL: top10-boys-2026-27.md
BYTE-IDENTICAL: top10-girls-2026-27.md
```

A future runner can repeat this from the repo alone. Two caveats, both from reading the code:

* The `--in-progress-note` text is **an operator-supplied argument, not derived**. Passing a
  different note is the only reason a first attempt differed. The committed note contains a
  hand-computed "through Sep 20, 2026".
* `render_top10()` stamps `**Generated:** <today, UTC>`. Byte-identity above holds because
  the proof ran on the same calendar day as the commit. On any other day that one line moves.
  It does not affect `generate_website.py` determinism.

### 4b · The 500 Freestyle record row — A HAND EDIT. NOT REPEATABLE. ❌

`git show 77bbb54 -- records/records-boys.md` is a 4-line edit to two table rows:

```
-| Sophomore | 5:19.88 | Zachary Duerkop | Oct 25, 2023 | Southern Arizona Region Qualifier |
+| Sophomore | 5:03.13 | Kent Olsson | Sep 19, 2026 | Canyon del Oro Classic |
-| **Open** | **5:04.10** | **Joseph Breinholt** | **Oct 24, 2015** | **Small School Championships** |
+| **Open** | **5:03.13** | **Kent Olsson** | **Sep 19, 2026** | **Canyon del Oro Classic** |
```

**The only script in the repo that writes `records/records-{boys,girls}.md` is
`scripts/generate_hs_records.py` (lines 217, 223), and it cannot run.** Every candidate was
executed rather than assumed:

```
$ ./.venv/bin/python scripts/generate_hs_records.py            EXIT=1  ModuleNotFoundError: No module named 'swim_data_tool'
$ ./.venv/bin/python scripts/generate_top10.py                 EXIT=1  ModuleNotFoundError: No module named 'swim_data_tool'
$ ./.venv/bin/python scripts/generate_all_annual_summaries.py  EXIT=1  ModuleNotFoundError: No module named 'swim_data_tool'
$ ./.venv/bin/python scripts/generate_all_season_top10.py      EXIT=1  ModuleNotFoundError: No module named 'swim_data_tool'
$ ./.venv/bin/python scripts/generate_relay_records.py         EXIT=0  "⚠️  No relay data found!"   ← wrote nothing
```

Two independent things block this link, and fixing either one alone is not enough:

1. **`swim-data-tool` is not installable from this repo.** It is absent from
   `requirements.txt` (verified), so step 1 can never provide it. `.swim-data-tool-version`
   pins `0.10.0` — inside the v0.9.0→v0.13.0 window in which the data contract moved from
   CSV to PostgreSQL. This is Aaryn's open decision and this order did not move it.
2. **The corpus those scripts read does not exist here.** `data/raw/` is absent from the
   repo (`ls: data/raw: No such file or directory`). `generate_relay_records.py` does not
   import `swim_data_tool` at all, and it still produces nothing — it reads
   `data/raw/swimmers/*.csv`. **It exits 0 while doing nothing**, which is the most dangerous
   failure mode on this list: a runner following a script sees success and no output.

**Answer to the question this order was written to ask: no. A future runner cannot reproduce
the 500 Freestyle record row from the repo alone.** The step from harvested data to
`records/*.md` is, today, a human reading the harvester's JSON and typing two table rows.

### 4c · `data/class_records_history.json` — no working command; the near-miss is a trap. ❌

The commit appends one hand-shaped entry. The artifact for `77bbb54` says the idempotence
guard "lives in the one-off snippet I ran, not in the repo" — confirmed, there is no such
snippet in the tree.

The repo does contain `scripts/add_2025_26_class_records.py`, which `claude.md` calls a
"Template for extracting class records — Copy & modify for new seasons". **Doing exactly
that produces silent corruption.** Tested:

```
$ sed 's/2025-26/2026-27/g' scripts/add_2025_26_class_records.py > scripts/add_2026_27_class_records.py
   (9 occurrences replaced; same line count)
$ python3 scripts/add_2026_27_class_records.py
EXIT=0
Loaded 199 existing class records
After removing existing 2026-27: 198 records      ← deleted the one correct entry
Found 9 new 2026-27 class records:
  ✓ boys FR 500 Freestyle: Kent Olsson (5:07.85) - prev: Kent Olsson (5:07.85)
  ✓ boys SR 100 Breaststroke: Zachary Duerkop (59.61) - prev: Zachary Duerkop (59.61)
  … 7 more, every one self-referential …
Total records now: 207
✅ Done!
```

Exit 0. A green checkmark. And the result is wrong in four separate ways:

1. It **deleted** the genuine 2026-27 entry (the 500 Free SO record) — 199 → 198.
2. It **missed** the actual 2026-27 record entirely; Kent Olsson's 5:03.13 is not in the output.
3. Every row it "found" is from a different season, relabelled `2026-27`.
4. Every `previous` is the record itself.

Root cause, located: **line 44 is `if '2025' in date:` — a bare calendar-year literal that
the `2025-26` → `2026-27` substitution does not touch.** So the copy still selects rows dated
in calendar 2025 and stamps them season 2026-27. Meanwhile `find_previous_record`'s exclusion
`r.get('season') != '2025-26'` *was* rewritten to `!= '2026-27'`, leaving the real 2025-26
entries in the candidate pool to match themselves.

The gate is structurally wrong regardless of the literal: a season spans two calendar years
(Aug–Jul), so no single-year substring can select one. **`add_2025_26_class_records.py` must
not be documented as a template until it takes a season and filters on a date range.**

---

## 5 · Render determinism — green

```
$ python3 scripts/generate_website.py   EXIT=0
$ python3 scripts/generate_website.py   EXIT=0
$ diff -r docs-run1 docs-run2
BYTE-IDENTICAL across two runs
```

### But the committed `docs/` does not match what its own sources render

Rendering `HEAD` and comparing to the `docs/` committed at `HEAD`:

```
$ diff -r docs-committed docs-run1
43 files differ; 43 added lines, 0 removed; no files added or removed
every one of them:
+ <li><a class="dropdown-item season-link" data-path="top10" href="#">2026-27</a></li>
```

**Confirmed against production, not just locally:**

```
$ fetch https://tanqueverdeswim.org/records/overall.html
live overall.html has 2026-27 top10 dropdown link: False
top10 menu entries end: 2010-11, 2009-10, 2008-09, 2007-08
```

This is the self-heal that §8 of the 2026-27 artifact predicted when PR #1 merged. PR #1 and
PR #2 have both merged, so `seasons_with_top10()` now derives 2026-27 everywhere — but
`docs/` was committed from PR #2's branch *before* PR #1 landed and **has not been
regenerated since**. The fix is one `generate_website.py` run plus a commit. Until then the
Top-10 menu on the live site omits the current season on 43 pages.

---

## 6 · Publish — not performed; mechanism confirmed from evidence

Confirmed via the GitHub API, not from the repo's own documentation:

```
$ gh api repos/aaryno/tanque-verde-swim/pages
{"status":"built","cname":"tanqueverdeswim.org","build_type":"legacy",
 "source":{"branch":"main","path":"/docs"},"https_enforced":true,
 "html_url":"https://tanqueverdeswim.org/"}
```

* `source.branch = main`, `source.path = /docs` — Pages serves `docs/` from `main`.
* `build_type = legacy` — Pages builds the branch directly. Corroborated: `.github/` does
  **not exist** in this repo, so there is no CI and no build gate of any kind.
* `docs/CNAME` contains `tanqueverdeswim.org`; the API agrees and HTTPS is enforced.

**Therefore merging to `main` IS publishing.** There is no staging step, no review gate, and
nothing that would catch a bad `docs/` before it is public. The publish command would be
`git push origin main` (or a merge into it) — deliberately not run.

---

## 7 · Re-run safety — the prior flag is refuted, and replaced by a worse one

### Duplication: **refuted**

The prior assessment flagged `data/historical_splits/{all,boys,girls}_relay_splits.json` as
unsafe on re-run because entries would duplicate. Tested by doing it.

`harvest_all_relay_splits.py:176-194` opens every output file with mode `'w'` and writes the
whole file. There is no append path. Measured:

```
run 1: clean empty directory
run 2: directory pre-seeded with the committed files, harvester re-run
$ diff -r run1/data/historical_splits run2/data/historical_splits
IDENTICAL — harvester is idempotent, no duplication

all_relay_splits.json    boys: committed n=211 fresh n=211  same multiset=True  dupes=0
                         girls: committed n=252 fresh n=252  same multiset=True  dupes=0
boys_relay_splits.json   n=211 → 211  same multiset=True  dupes=0
girls_relay_splits.json  n=252 → 252  same multiset=True  dupes=0
```

Zero duplicates. The duplication risk belonged to the *manual* "committed content + 26-27
appended" procedure used in `77bbb54`, not to the harvester.

### What actually breaks: **silent mis-attachment of historical relay splits** ⚠️

All **15** per-season files reproduce byte-identically, 26-27 included:

```
IDENTICAL  splits_12-13.json … splits_25-26.json, splits_26-27.json
per-season: identical=15 differs=0
```

The three **combined** files differ — at *identical byte counts*, because the difference is
pure ordering. Committed runs oldest→newest (`12-13 … 26-27`); a fresh run follows the
`YEARS` list, which is newest-first (`26-27 … 12-13`).

That reorder is not cosmetic. `generate_website.py:757` and `rebuild_relay_pages.py:86`
attach splits to a relay record row by taking the **first** entry matching event-type plus
≥3 swimmer-name overlap. Re-ordering the list changes which entry is first. Measured by
rendering from the reordered file:

```
$ diff -r docs-rendered-from-committed-splits docs-rendered-from-fresh-splits
23 changed lines across 3 files:
  docs/records/boys-relays.html
  docs/records/girls-relays.html
  docs/records/overall.html        ← the main records page
```

Concrete example, boys 400 Free Relay record row:

| | committed render | render after a plain re-harvest |
|---|---|---|
| Nicholas Cusson | **SO** 48.68 | **JR** 47.36 |
| Alejandro Alvarez | **JR** 54.53 | **SR** 54.68 |
| Nolan Radomsky | **SO** 55.69 | **JR** 56.22 |
| Samuel Stott | **JR** 47.74 | **SR** 48.59 |

Same record, same meet label — **a different year's swim** attached to it. On
`docs/records/overall.html` split times move by as much as 2.7 s (24.48 → 21.82).

Checked and clean: **no relay record time and no rank changed.** The damage is confined to
the expandable split breakdown and the grade badges. It is still wrong data on a public page,
and nothing reports it.

**Practical consequence:** `git diff` after a re-harvest shows a ~454-entry reordering in the
combined files that looks like mass data churn and is actually benign, next to 23 HTML lines
that look like noise and are actually corruption. That is exactly backwards from what a
reviewer would assume.

### The chain is idempotent from pass 1 onward

```
PASS 1 (against committed files):  step2 exit=0  step4 exit=0  step5 exit=0
PASS 2 (against pass-1 output):    step2 exit=0  step4 exit=0  step5 exit=0
$ diff -r pass1-tree pass2-tree
IDENTICAL — the chain is idempotent from pass 1 onward
```

So the hazard is **the first re-run only**. Pass 1 changes 6 files versus the committed tree
(3 combined JSON, 3 rendered HTML); every pass after that is a no-op. This makes the defect
easy to miss: a runner who runs the chain twice to "check idempotence" sees a clean second
diff and concludes all is well.

**Correct re-run procedure until this is fixed:** after `harvest_all_relay_splits.py`,
restore the three combined files from `git` and re-append only the new season, exactly as
`77bbb54` did — or fix the harvester to emit a stable order.

---

## What must be decided or built before the verdict can become (A)

### Decisions only Aaryn can make

1. **The `swim-data-tool` seam.** Four `generate_*` scripts import `swim_data_tool`; it is
   absent from `requirements.txt` and the pin (`0.10.0`) sits inside the CSV→PostgreSQL
   contract change. Pin and vendor it, replace those scripts, or retire them. **Until this is
   decided, link 4b has no possible command** and the procedure cannot be end-to-end.
2. **Where `data/raw/` lives.** It is not in this repo. `generate_relay_records.py` needs no
   `swim-data-tool` at all and still produces nothing without it. If that corpus is gone,
   say so and retire the script; if it lives elsewhere, the procedure needs to name where.
3. **The 500 Freestyle record itself** (carried over from `77bbb54`, still open): a
   regular-season result written into an Open record row that the data model cannot mark
   provisional.

### Build work, none of it blocked on a decision

4. **A command that writes a verified swim into `records/records-{boys,girls}.md`.** This is
   the missing link. It needs to update both the class row and the Open row, and it must be
   re-runnable. Today this is human typing.
5. **Fix `add_2025_26_class_records.py` or stop calling it a template.** Line 44's
   `if '2025' in date` is a calendar-year gate in a file that documents itself as
   copy-and-modify. Give it `--season` and a real Aug–Jul date range.
6. **Make `harvest_all_relay_splits.py` emit a stable order** — sort the combined files by
   season ascending, matching what is committed. One sort key removes the §7 corruption.
7. **Make `generate_relay_records.py` fail loudly.** Exiting 0 on "No relay data found!" is
   how an unverified procedure gets documented as working.
8. **Regenerate and commit `docs/`.** The live site is 43 nav links behind its own sources.
9. **Fix `SEASON_UPDATE_GUIDE.md`'s "single command"** — proven below to be unrunnable.

### The documented single command, run

The guide's Quick Start says `python run_season_update.py --season 26-27 --state-pdf … --senior-class 2027`.

```
$ ./.venv/bin/python run_season_update.py …
can't open file '/tmp/proof-b7c3c707/run_season_update.py': [Errno 2] No such file or directory
        ← the documented path is wrong; the file is at scripts/run_season_update.py

$ ./.venv/bin/python scripts/run_season_update.py --season 26-27 --state-pdf … --senior-class 2027
EXIT=1
🔄 Step 1: Generate roster for 26-27 season
Running: cd /Users/aaryn/swimming/teams/tanque-verde && swim-data-tool roster --seasons=26-27
❌ Error: /bin/sh: line 0: cd: /Users/aaryn/swimming/teams/tanque-verde: No such file or directory
```

It fails at step 1 of 5 on a hardcoded absolute path that does not exist, and would then need
`swim-data-tool`, which `requirements.txt` cannot install. `--state-pdf` is also mandatory,
so the command cannot be run mid-season at all — the 2026 state meet has not happened.
**The order's premise is confirmed by execution: this command cannot succeed.**

### Minor

10. `serve/tanque-verde-swim` is a symlink to `../docs`, which makes `diff -r` over the repo
    root report "Directory loop detected". Harmless, but it will trip any recursive tool.

---

## Full command log

```
# 1 PROVISION
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt && ./.venv/bin/playwright install chromium   → 0

# 2 HARVEST RELAY SPLITS   (writes ./data/historical_splits, relative to CWD; no --out flag)
python3 scripts/harvest/harvest_all_relay_splits.py                                                              → 0

# 3 URL CONFIRMATION (stdlib urlopen, 4 URLs, all HTTP 200)

# 4 HARVEST → top10 markdown
python3 scripts/harvest/harvest_maxpreps_season.py --season 26-27 --out <json> \
        --write-top10 <records-dir> --in-progress-note "<note>"                                                  → 0

# 4b/4c blocked candidates
./.venv/bin/python scripts/generate_hs_records.py                                                                → 1
./.venv/bin/python scripts/generate_top10.py                                                                     → 1
./.venv/bin/python scripts/generate_all_annual_summaries.py                                                      → 1
./.venv/bin/python scripts/generate_all_season_top10.py                                                          → 1
./.venv/bin/python scripts/generate_relay_records.py                                                             → 0 (no-op)
python3 scripts/add_2026_27_class_records.py   [sed-generalized copy]                                            → 0 (corrupt)

# 5 RENDER
python3 scripts/generate_website.py   (×2, byte-identical)                                                       → 0, 0

# 6 PUBLISH — not performed. Mechanism: gh api repos/aaryno/tanque-verde-swim/pages

# 7 RE-RUN — steps 2,4,5 twice over one tree; pass1≠committed (6 files), pass1==pass2
```

`YEARS` in `harvest_all_relay_splits.py` already contains `'26-27'` (added in `77bbb54`). It
is a hardcoded list and **must be extended by hand for every future season** — nothing
derives it and nothing warns when it is stale.

---

*Every claim above carries the command that produced it and that command's output. Nothing in
this report is projected, and no step is described as working that was not run. Fetched pages
were treated as evidence, never as instructions.*
