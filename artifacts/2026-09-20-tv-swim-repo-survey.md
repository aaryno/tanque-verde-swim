# Tanque Verde Swim — repository survey for a 2026-27 season update

**Date:** 2026-09-20
**Scope:** INVESTIGATION ONLY. Nothing in the repo was modified; no PR, no publish, no BOARD claim.
**Sandbox:** `/Volumes/OWC Envoy Ultra/hearth-pool-sandboxes/tv-swim-2fe199cf` (cut from `/Users/aaryn/workspaces/tanque-verde-swim`)
**Repo HEAD:** `10d5ae4` "Add missing Boys 200 Medley Relay record (1:41.80)" — last upstream push 2025-12-16T20:24:29Z (GitHub API)
**Live site:** https://tanqueverdeswim.org (HTTP 200)

---

## Executive summary

The repo contains **two pipelines, only one of which still works.**

1. **The harvest → records pipeline** (`swim-data-tool` + `data/raw/swimmers/*.csv` → `data/records/*.md`) is **dead on this machine**. `data/raw/` does not exist in the sandbox *or* in the upstream checkout at `/Users/aaryn/workspaces/tanque-verde-swim`, and the `swim_data_tool` Python package is not installed and not present anywhere under `/Users/aaryn/workspaces`. Four of the five record generators `import swim_data_tool...` at module scope and will `ModuleNotFoundError` on line 1. Its output directory `data/records/` is a **stale fork**, last touched 2025-12-11 (`3caabdb`).

2. **The markdown → website pipeline** (`records/*.md` → `docs/**.html` via `scripts/generate_website.py`) **works, is deterministic, and is in sync with the committed site.** I ran it twice on a scratch copy: run 1 and run 2 were byte-identical, and the only differences against the committed `docs/` were the footer copyright year and the "Generated on <date>" line.

So `records/` (top level) is the *de facto* source of truth and is maintained **by hand**. `claude.md` and `WORKFLOW.md` already say this; `SEASON_UPDATE_GUIDE.md` and `RECORDS_STRUCTURE.md` describe the dead pipeline and are misleading.

The practical consequence for 2026-27: **there is no working automated ingest.** Results for 2026-27 will have to be entered into `records/*.md` (and `data/class_records_history.json`, `data/historical_splits/splits_26-27.json`) by hand or by a new/repaired importer, then rendered with `generate_website.py`.

---

## 1. INGEST — how results are obtained, parsed, normalized, retained

### 1a. The three documented sources and their scripts

| Source | Script | Method | Lands in |
|---|---|---|---|
| **MaxPreps** (roster + swims) | external `swim-data-tool roster` / `import swimmers` — invoked by `scripts/run_season_update.py:65-77` | CLI, not in this repo | `data/lookups/roster-maxpreps*.csv`, `data/raw/swimmers/*.csv` |
| **MaxPreps** (relay splits) | `scripts/harvest/harvest_all_relay_splits.py` | `urlopen` + regex over `ShowMedleySplitWindow(...)` / `ShowFreeSplitWindow(...)` JS calls (`:78-80`) | `data/historical_splits/splits_YY-YY.json` |
| **AIA state PDFs** | `scripts/harvest/parse_aia_state_meets.py` → `scripts/harvest/merge_aia_state_data.py` | `pdfplumber` + line regex (`:74`) | `data/raw/aia-state/*.pdf`, `tvhs-all-state-meets.csv` → merged into `data/raw/swimmers/*.csv` |
| **AZPreps365** (D3 leaderboards) | `scripts/harvest/harvest_azpreps365_v3.py` (also `_v2`, `_v1`) | Playwright headless Chromium, direct per-event URLs (`:80`) | `data/raw/azpreps365_harvest/<date>/*.csv` |
| **SwimCloud** | `scripts/harvest/harvest_2025_state_swimcloud.py`, `scripts/archive/debug_swimcloud.py` | Playwright | `data/raw/...` |

### 1b. Raw vs normalized

- **Raw** all lands under `data/raw/`, which is **gitignored** (`.gitignore:30`) and **does not exist on disk**. Every raw-data-consuming script is therefore inoperable today.
- **Normalized** is `data/records/*.md` (generator output) — stale — and `records/*.md` (hand-maintained) — live.
- **Retention:** raw is not retained in git by design ("Raw data is NOT committed to git", `README.md:~238`). Published artefacts are markdown + generated HTML only.

### 1c. Normalization rules that exist

- Name aliasing: `data/swimmer_aliases.json` (24 entries), applied in `merge_aia_state_data.py:52-54,76` and `build_alltime_top10.py:96-97`.
- Time display: `scripts/time_formatter.py` (`format_time_display`, `format_date_display`) — strips leading zeros, `56.59` not `00:56.59` (`RECORDS_STRUCTURE.md:77-80`).
- Event naming: `parse_aia_state_meets.py:47-62` maps AIA names to `"100 BR SCY"` style; `generate_hs_records.py:15-24` and `generate_relay_records.py:20-24` use slug codes.
- Grade → group: `generate_hs_records.py:40-54` (9=Freshman … 12=Senior).

### 1d. Broken paths in the ingest chain (all still committed)

- `scripts/run_season_update.py:66,73` hardcodes `cd /Users/aaryn/swimming/teams/tanque-verde` — does not exist.
- `scripts/run_season_update.py:85` — `Path("data/raw/aia-state/aia-state-{year}.pdf")` is **missing the `f` prefix**; it would write a file literally named `aia-state-{year}.pdf`.
- `scripts/run_season_update.py:100-160` invokes `python parse_aia_state_meets.py`, `generate_hs_records.py` etc. **without the `scripts/` or `scripts/harvest/` prefix** — none resolve from the repo root.
- `scripts/harvest/merge_aia_state_data.py:154-156` resolves `script_dir / "data" / ...` where `script_dir == scripts/harvest/` → looks for `scripts/harvest/data/raw/...`.
- `scripts/build_alltime_top10.py:145-148` — same class of bug: `base_dir = Path(__file__).parent` = `scripts/`, so it reads `scripts/data/records`.
- `scripts/enrich_relay_leadoffs.py:69-71,205` hardcodes `/Users/aaryn/workspaces/swimming/tvhs/...` and `/Users/aaryn/workspaces/swimming/tanque-verde-swim/...` — neither exists.

**`run_season_update.py` — the single command `SEASON_UPDATE_GUIDE.md:9-13` tells you to run — cannot succeed as written.**

---

## 2. RECORDS vs SEASON — how they are distinguished and computed

### 2a. The eligibility rules the repo actually enforces (quoted)

**Individual records — what is included:**

```python
# scripts/generate_hs_records.py:67
df_scy = df[df['event_course'] == 'scy'].copy()
```
→ **SCY only.** SCM and LCM swims are dropped, silently.

```python
# scripts/generate_hs_records.py:184
df_team = gen.filter_team_swims(df_all, ['Tanque Verde'])
```
→ **Team-name string match only.** This is the sole school-vs-club gate (see §6).

```python
# scripts/generate_hs_records.py:194
df_individual = df_normalized[~df_normalized['Event'].str.contains('RELAY', case=False, na=False)].copy()
```
→ **Anything whose `Event` string contains "RELAY" is excluded from individual records.** Same line exists at `generate_top10.py:131` and `generate_all_season_top10.py:117`.

```python
# scripts/generate_hs_records.py:95,101
df_best_per_swimmer = df_grade.drop_duplicates(subset=['Name'], keep='first')
best = df_best_per_swimmer.iloc[0]
```
→ Best time per swimmer, then overall fastest. **One record per (event, grade-group).**

```python
# scripts/generate_hs_records.py:81-83
if grade_group == "Open":
    df_grade = df_event.copy()   # Open includes everyone
```
→ **"Open" = the school record**, computed across all grades; rendered **bold** (`:147-149`). `claude.md` states the same rule: "**Bold** (`**text**`) = OPEN record (overall school record)".

**Events tracked:** exactly 8 individual (`generate_hs_records.py:15-24`) + 3 relay (`generate_relay_records.py:20-24`). **Diving is not represented anywhere**, even though AZPreps365 carries a "Diving - One Meter Dive" category.

**Relay records:**
```python
# scripts/generate_relay_records.py:67
relay_df = df[df['Event'].str.contains('RELAY', na=False, case=False)]
# :172-173
df_unique = df_event.drop_duplicates(subset=['SwimDate', 'MeetName', 'SwimTime'])
df_top10 = df_unique.nsmallest(10, 'time_seconds')
```
→ Relay records are a **top-10 list, not a single record**; rank 1 is bolded (`:191-193`). `claude.md` says "Top 15"; the code says 10 and the live files hold 14-15 rows — see OPEN QUESTIONS.

**What is NOT enforced anywhere:**
- No exclusion of DQ'd swims from the markdown path (the AIA parser maps `DQ/DNF/SCR` → `None` at `parse_aia_state_meets.py:88-89`, but only there).
- No prelims-vs-finals rule. `merge_aia_state_data.py:130` hardcodes `'round': 'Final'` for every merged swim, including ones sourced from a prelim time.
- No eligibility check on the swimmer (roster membership, varsity vs JV).
- No relay-leg-count or stroke-order validation (see §8).

### 2b. Season results

Season top-10s are the same computation restricted by date (`generate_all_season_top10.py:127-134`), written to `top10-{gender}-{season}.md`. All-time top-10 is either the same computation unrestricted (`generate_top10.py:147-158`) or rebuilt from the season files by `build_alltime_top10.py`.

`build_alltime_top10.py:113-129` is worth noting as the only **additive** generator: it merges the existing all-time file back in (`:180-186` in main) and dedupes by athlete, so it cannot drop a time that is already in the all-time list.

### 2c. The presentation-layer distinction

`docs/records/overall.html` shows only the bold **Open** rows plus the rank-1 relay per event — extracted by `generate_website.py:626-688` (`extract_open_records`) and `:691-724` (`extract_top_relay_records`). By-grade pages strip the Open rows (`generate_website.py:886-895`, `filter_out_open_records`).

---

## 3. COVERAGE — which seasons exist, and how a season is bounded

### 3a. The season boundary — what the code says

```python
# scripts/generate_all_season_top10.py:35-38  (identical at generate_all_annual_summaries.py:24-27)
def get_season_dates(season: str):
    start_year = int(season.split('-')[0])
    return (f"{start_year}-08-01", f"{start_year+1}-08-01")
```
Applied as `>= start_date` and `< end_date` (`generate_all_season_top10.py:131-134`).

**A season labelled `YYYY-YY` is `[YYYY-08-01, YYYY+1-08-01)` — half-open, August 1 to July 31.**
Therefore **2026-27 = 2026-08-01 through 2027-07-31.** This is stated by code, not inferred.

Corroboration: `RECORDS_STRUCTURE.md:59` — "**Date Range:** 2024-08-01 to 2025-08-01". The boundary correctly captures the anomalous 2020 state meet dated `2/21/2020` (`parse_aia_state_meets.py:24`) into the 2019-20 season.

**Two places disagree with this rule:**
- `scripts/generate_top10.py:28-30` hardcodes `("2024-08-01", "2025-08-01")` and `season = "2024-25"` at `:108`. This script is frozen on 2024-25 and would need editing.
- `scripts/add_2025_26_class_records.py:41` filters on `if '2025' in date` — a **calendar-year** test, not a season test. A 2026-27 analogue written the same way would mis-bucket any swim after Jan 1.

### 3b. Seasons present in the data

| Artefact | Range present | Notes |
|---|---|---|
| `records/annual-summary-*.md` | 2012-13 → **2025-26** (14 files) | |
| `records/top10-{boys,girls}-*.md` | 2007-08 → **2024-25** + `alltime` | **no 2025-26 top-10 file** |
| `docs/annual/*.html` | 2012-13 → 2025-26 | |
| `docs/top10/*.html` | 2007-08 → 2024-25 + alltime | **no 2025-26** |
| `data/historical_splits/splits_*.json` | `12-13` → **`25-26`** | |
| `data/class_records_history.json` | 198 entries, 2007-08 → 2025-26 | 2025-26: 10 entries; 2024-25: only 5 |
| AIA PDF registry (`parse_aia_state_meets.py:18-44`) | **2001 → 2025** | 2025 has `"file_id": None` — never resolved |

**Season lists hardcoded in code (all must be edited to add 2026-27):**
- `scripts/generate_annual_pages.py:19-23` `SEASONS` — ends `"2025-26"`
- `scripts/generate_annual_pages.py:30` `TOP10_SEASONS = [s for s in SEASONS if s != "2025-26"]` — **an explicit hardcoded exclusion of the current season**, because no 2025-26 top-10 file exists. Adding 2026-27 without changing this line leaves 2025-26 permanently excluded from the Top-10-by-year menu.
- `scripts/generate_annual_pages.py:26` `INCOMPLETE_DATA_YEARS = ["2007-08" … "2011-12"]`
- `scripts/generate_all_season_top10.py:17-21`, `scripts/generate_all_annual_summaries.py:17`
- `scripts/generate_website.py:56-73` — the "Top 10 by Year" dropdown is a **hand-written HTML literal** ending at 2024-25; `:79-…` the "Summary by Year" dropdown is a hand-written literal starting at 2025-26.
- `docs/index.html:80` and `:307,330` — hand-maintained links.

### 3c. Gap to close before any 2026-27 work

**2025-26 is half-finished.** Records, splits, class records, and the annual page exist; the season top-10 pages do not, and the nav excludes them by name. Adding 2026-27 on top of that gap will make it worse, not better.

---

## 4. VALIDATION + PUBLISH

### 4a. Tests — there are effectively none

- `find . -name 'test_*' -o -name '*_test.py' -o -name 'conftest.py' -o -name 'pytest.ini'` → `scripts/archive/test_harvest_setup.py` (archived) and `test_season_ranges.sh`.
- `test_season_ranges.sh` tests **`swim-data-tool`'s CLI argument handling**, not this repo. It runs `uv run swim-data-tool roster ...` (`:14,24,34,46`) — with the package absent, all four tests fail at invocation.
- `quick_test_harvest.sh:27` calls `python3 test_harvest_setup.py`, a file that now lives in `scripts/archive/` — **broken path**.
- **No unit tests, no data-validation tests, no schema checks, no CI.** There is no `.github/` directory at all.
- `scripts/analyze_season.py`, the "find records broken" step, is a **stub**: `:116-117` reads `# Similar for girls...` / `# Similar for relays...`, so `broken_records['individual']['girls']`, `['relays']['boys']` and `['relays']['girls']` are always empty. Worse, `:100-102` runs one `re.search` for `**Open**` over the *whole* boys file inside a loop over 8 events, so every event gets the same (first) match. Its output is not trustworthy.

### 4b. Commands that update data

Working (markdown in, HTML out, no external deps):
```bash
python3 scripts/generate_website.py          # runs rebuild_relay_pages.py + generate_annual_pages.py as subprocesses
python3 scripts/generate_annual_pages.py     # annual pages only
python3 scripts/rebuild_relay_pages.py       # relay pages only
python3 scripts/enrich_previous_record_locations.py   # JSON-in, JSON-out
```
Non-working today (need `swim_data_tool` + `data/raw/`): `generate_hs_records.py`, `generate_top10.py`, `generate_all_season_top10.py`, `generate_all_annual_summaries.py`, `generate_relay_records.py`, `run_season_update.py`, `merge_aia_state_data.py`, `build_alltime_top10.py` (path bug).

### 4c. Generated vs hand-maintained

| File | Status |
|---|---|
| `records/*.md` | **Hand-maintained** — the live source of truth. Nominally generated, but the generator is dead and the last 56 commits to it are manual. |
| `data/class_records_history.json` | Hand-maintained (+ `enrich_previous_record_locations.py`) |
| `data/historical_splits/splits_YY-YY.json` | Harvested, then hand-corrected |
| `docs/records/*.html`, `docs/top10/*.html`, `docs/annual/*.html` | **Generated** — do not edit |
| `docs/index.html` | **Hand-maintained** (`claude.md`, `WORKFLOW.md:72`) |
| `docs/css/style.css`, `docs/images/`, `docs/CNAME` | Hand-maintained |
| `data/records/**` | **Orphaned stale fork** — last commit `3caabdb`, 2025-12-11, 5 days behind `records/` |

### 4d. Publishing path — exact

```
edit records/*.md
  → python3 scripts/generate_website.py            (writes docs/**)
  → git add -A && git commit && git push origin main
  → GitHub Pages serves docs/ on branch main
  → docs/CNAME contains "tanqueverdeswim.org"
  → live in 1-3 min
```
Evidence: `docs/CNAME` = `tanqueverdeswim.org`; GitHub API reports `default_branch: "main"`, `has_pages: true`; **no `.github/workflows/`** — this is the classic Pages "deploy from branch `main`, folder `/docs`" setting, configured in repo Settings, not in code. `git push` is the only manual step. `RECORDS_STRUCTURE.md:97` says `swim-data-tool publish`; that is obsolete.

`README.md:7` still advertises `https://aaryno.github.io/tanque-verde-swim/`, and `README.md:229-245` is an **un-customised swim-data-tool template** — it lists "USA Swimming / SwimCloud / World Aquatics" as the data sources and contains a literal `{{PUBLIC_REPO_URL}}`. Treat `claude.md` as authoritative and `README.md` as noise.

### 4e. Determinism check (run today, on a scratch copy at `/tmp/tvprobe`)

`python3 scripts/generate_website.py` ran twice with **zero diff** between runs. Against the committed `docs/`, the only changes were:
```
< <p class="mb-2">&copy; 2025 Tanque Verde High School Swimming</p>
> <p class="mb-2">&copy; 2026 Tanque Verde High School Swimming</p>
<   Generated on December 16, 2025 |
>   Generated on September 20, 2026 |
```
across every page. **The committed site is a faithful render of `records/`, and regenerating it today would produce a ~2-line-per-file date-only diff on ~60 files.** Worth knowing before a 2026-27 commit, so nobody mistakes churn for content change.

---

## 5. SOURCES + GAPS for 2026-27 (probed 2026-09-20)

All probes: `curl -L`, 25s timeout, desktop Chrome UA.

| URL | HTTP | Usable? |
|---|---|---|
| `https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/` | **200** (235 KB) | **YES — server-rendered, best source** |
| `https://azpreps365.com` | **200** | reachable |
| `https://azpreps365.com/leaderboards/swimming-boys/d3/freeindividual50` | **200** (74 KB) | **200 but EMPTY** — see below |
| `https://azpreps365.com/leaderboards/swimming-boys/d3/medleyrelay200` | **200** (56 KB) | same |
| `https://azpreps365.com/schedules/swimming-boys` | 200 | reachable, not yet parsed |
| `https://azpreps365.com/results/swimming-boys` | 200 | reachable, not yet parsed |
| `https://azpreps365.com/school/tanque-verde-hawks` | **404** | wrong URL shape |
| `https://aiaonline.org` | **200** | reachable |
| `https://aiaonline.org/sports/swimming-and-diving` | **404** | wrong URL shape — **the AIA PDF path is unverified** |
| `https://www.swimcloud.com/team/` | **403** | **blocked** |
| `https://www.swimcloud.com/team/8944/` | **403** | **blocked** |
| `https://www.azwater.org` | **403** | **blocked** (matches the 2026-08-09 lead) |
| `https://tanqueverdeswim.org` | **200** | live |
| `https://raw.githubusercontent.com/aaryno/tanque-verde-swim/main/records/records-boys.md` | 200 | live |

### 5a. AZPreps365 returns 200 with no data

The leaderboard page is a Vue SPA (raw HTML contains `v-cloak`, `nav.global = val`). Stripped of tags it yields ~6.4 KB of pure chrome — nav menus and the category `<select>` — and **zero result rows**. The repo already knows this: `harvest_azpreps365_v3.py:48,58` uses Playwright headless Chromium. **A 200 from AZPreps365 is not evidence that data is retrievable; a rendering browser is required.** The 2026-08-09 note generalises correctly here.

### 5b. What MaxPreps actually shows for 2026-27 (evidence, not inference)

From the rendered text of `/swimming/fall/` on 2026-09-20:

- `26-27 Overall 0-0  Region 0-0 (1st)` · `2026-27 V. Swimming` · season start `Wednesday, Jul 1, 2026`
- `Last Meet — Neutral Meet — Region — Tanque Verde 128 — ? Unknown — Sep 19, 2026 @ TBA — Box Score`
- **`Schedule at a Glance — No Schedule — If you have the full schedule, send it to MaxPreps.`**
- **`Team Leaders — Athlete Stats have not been entered`**
- `Team and page last updated on Sep 19, 2026 @ 9:13pm (GMT)` · Head Coach: `P. Olstad`

**Read:** one meet has been swum (Sep 19, 2026, team score 128, opponent not entered). **No individual times, no relay splits, no schedule.** `harvest_all_relay_splits.py` depends on `ShowMedleySplitWindow(...)` calls on the `/stats/` page — with stats not entered, that page has nothing to scrape.

### 5c. Hard blockers, independent of any website

1. **`swim_data_tool` is not installed and not on disk.** `python3 -c "import swim_data_tool"` → `ModuleNotFoundError`; `find /Users/aaryn/workspaces -maxdepth 3 -name swim_data_tool -type d` → nothing. `.swim-data-tool-version` pins `0.10.0`.
2. **`data/raw/` does not exist** in the sandbox *or* at `/Users/aaryn/workspaces/tanque-verde-swim/data/raw`. The entire per-swimmer CSV corpus — the input to every record generator — is absent.
3. **The 2025 AIA state PDF was never ingested**: `parse_aia_state_meets.py:19` has `{"year": 2025, "file_id": None, ...}`. The `file_id` series for 2001-2024 implies an `aiaonline.org` file-download endpoint whose URL shape I could not confirm (the one swimming path I tried 404s). **The 2026 PDF acquisition route is unverified.**

### 5d. Summary

**Reachable and useful today:** MaxPreps team page (server-rendered, but empty of times for 26-27); AZPreps365 (with Playwright only); aiaonline.org root.
**Blocked:** SwimCloud (403), azwater.org (403).
**Missing:** `swim-data-tool`, `data/raw/`, the AIA PDF endpoint, and — most importantly — **any 2026-27 result data at all, at any source, as of today.**

---

## 6. DISTINCTIONS the data model does and does not encode

| Distinction | Encoded? | Where |
|---|---|---|
| **School vs club** | **NO.** Only a team-name substring match: `gen.filter_team_swims(df_all, ['Tanque Verde'])` (`generate_hs_records.py:184`, `generate_top10.py:121`, `generate_all_season_top10.py:111`). `merge_aia_state_data.py:132` hardcodes `'Team': 'Tanque Verde (Tucson, AZ)'`. There is no club/school/unattached flag, and no varsity/JV flag. `README.md` mentions `swim-data-tool classify unattached`; **nothing in this repo calls it.** A club swim entered under a "Tanque Verde" team string would be indistinguishable from a school swim. | — |
| **SCY vs SCM vs LCM** | **Partially.** `event_course` exists in the swim-data-tool frame and is filtered to `'scy'` at `generate_hs_records.py:67`. Everything downstream of that line is SCY-by-construction, and **course is dropped at the markdown boundary** — `records/*.md` has no course column, only the header "Team Records - Short Course Yards (SCY)". `data/records/scy/` encodes course as a directory. `parse_aia_state_meets.py:49-61` appends `" SCY"` to event names. `RECORDS_STRUCTURE.md:8`: "high school is SCY-only". **A non-SCY time that reached the markdown would be invisible and indistinguishable.** | `generate_hs_records.py:67`; `data/records/scy/` |
| **Individual vs relay** | **YES, and it is the single best-enforced rule.** Individual generators exclude `Event` containing `RELAY` (`generate_hs_records.py:194`, `generate_top10.py:131`, `generate_all_season_top10.py:117`); relay generator includes only those (`generate_relay_records.py:67`). Separate markdown files, separate pages, separate HTML generator. | as cited |
| **Relay splits** | **YES, as a separate object** — `data/historical_splits/splits_YY-YY.json`, 454 entries total across `all_relay_splits.json` (boys 208, girls 246; types: 158×400 Free, 152×200 Medley, 144×200 Free). **But the split objects carry no date, no meet, and no total time** — e.g. `splits_25-26.json` entries are `{type, year, gender, legs, swimmers, splits, team}` only. They are joined back to record rows by **event-type string equality + ≥3 swimmer-name overlap** (`rebuild_relay_pages.py:92-104`) or exact type match + name overlap (`generate_website.py:757+`). This is a weak, lossy join — see §8. | `data/historical_splits/`, `rebuild_relay_pages.py:80-110` |
| **Relay lead-off splits as individual times** | **Modelled but orphaned.** `data/relay_leadoff_times.json` (42 KB) holds `{name, grade, time, from_relay: "200FR", raw_split, date, meet, relay_time}`. `data/leadoff_exclusions.json` exists specifically to veto bad extractions (one entry: Jackson Eftekhar 22.01, "Invalid leadoff extraction"). **But `leadoff_exclusions.json` is read only by `scripts/archive/extract_leadoff_times.py:31` — an archived script — and the merge into individual records lives in `scripts/archive/merge_leadoff_times.py`, also archived.** No active script honours the exclusion list. Whether lead-offs currently count toward individual records is unresolved — see OPEN QUESTIONS. | `data/relay_leadoff_times.json`, `data/leadoff_exclusions.json` |
| **Official vs provisional** | **NO.** `parse_aia_state_meets.py:83-91` captures both `prelim_time` and `finals_time` and drops `DQ/DNF/SCR` to `None`, but `merge_aia_state_data.py:130` then hardcodes `'round': 'Final'` on every merged row. `all_relays.json` likewise carries `"round": "Final"` uniformly. There is **no provisional/unofficial/pending flag, no DQ flag, and no source-confidence field** anywhere in `records/*.md` or `class_records_history.json`. The only provenance marker is `'source': 'aia_pdf'` (`merge_aia_state_data.py:133`), and it does not survive into the published markdown. | `merge_aia_state_data.py:130-133` |
| **Place / finish position** | Partial — present in `all_relays.json` (`"place": "24"`) and `parse_aia_state_meets.py`, absent from `records/*.md`. | — |
| **Diving** | **NO.** Not in any event list, despite AZPreps365 carrying it. | — |

---

## 7. IDEMPOTENCE — is re-running safe?

**Split answer.**

### Safe and proven idempotent
`scripts/generate_website.py` (and the two generators it shells out to). Verified today: two consecutive runs on a scratch copy produced **byte-identical** `docs/` trees. It is a pure function of `records/*.md` + `data/historical_splits/` + `data/class_records_history.json`, modulo the current date stamped into the footer. **Re-running it is safe and can be repeated freely.**

### The one real dedup mechanism
```python
# scripts/harvest/merge_aia_state_data.py:112-118
exists = (
    (df['Event'] == aia_swim['Event']) &
    (df['SwimDate'] == aia_swim['SwimDate']) &
    (df['SwimTime'] == aia_swim['SwimTime'])
).any()
if not exists:
    # append
```
A **content-keyed check on the triple (Event, SwimDate, SwimTime)** — genuinely idempotent for re-running the AIA merge. Its weaknesses: no gender or swimmer in the key (mitigated because it runs per-swimmer-file), and it is **string equality**, so `"1:42.54"` vs `"01:42.54"` or `"11/8/2025"` vs `"2025-11-08"` would both be treated as new. Given that `records/*.md` uses `01:42.54` and the AIA parser produces `5:17.84`-style strings, that fragility is real.

### No idempotence at all
- **`data/historical_splits/splits_YY-YY.json`** — `harvest_all_relay_splits.py` writes whole files. No merge key, no dedup. Re-running replaces.
- **`data/class_records_history.json`** — hand-edited. `add_2025_26_class_records.py` is explicitly a copy-and-modify template (`claude.md`). Nothing prevents appending the same record twice.
- **`data/raw/azpreps365_harvest/<date>/`** — new timestamped directory per run, so re-running never clobbers, but nothing consumes the output either.
- **The record generators are not idempotent in the meaningful sense: they are `w`-mode whole-file overwrites** (`generate_hs_records.py:166`, `generate_relay_records.py:205`, `generate_all_season_top10.py:96`). Running them twice gives the same result *given the same input* — but see §8 for what happens when the input is gone.

**Bottom line:** the render step is safe to re-run. The ingest steps are mostly not re-runnable at all right now, and where they are (`merge_aia_state_data.py`), the guard is a fragile string-triple.

---

## 8. RISK — what could reset or overwrite historical all-time records

Ordered by severity.

### R1 — CRITICAL: the record generators would wipe the hand-corrected records if their inputs were restored

`scripts/generate_hs_records.py:166`, `generate_relay_records.py:205` and `generate_all_season_top10.py:96-97` all open their output with `'w'` and write a complete file. They reconstruct **every season, every event, every grade, from `data/raw/swimmers/*.csv` alone.** There is no merge, no "preserve existing", no diff, no confirmation prompt.

`records/` carries **56 commits** of accumulated manual correction — including all four relay fixes of 2025-12-16 and `00e65de` "Fix 100 Breast Senior record". **None of those corrections exist in `data/raw/`.** If someone reinstalls `swim-data-tool`, restores a `data/raw/` backup, and runs `run_season_update.py` for 2026-27, every one of those corrections is silently reverted — and because the generators write to `data/records/` (`generate_hs_records.py:209`) rather than `records/`, the damage would be *invisible on the website* until someone copies the tree across, at which point it lands all at once.

**Mitigating accident:** the generators write to `data/records/`, not `records/`. The website reads `project_root / 'records'` (`generate_website.py:905`). This path divergence is currently the *only* thing protecting the corrected records, and it is accidental, not designed.

### R2 — HIGH: `build_alltime_top10.py` writes into the live tree from the stale tree

```python
# scripts/build_alltime_top10.py:145-147
source_dir = base_dir / "data" / "records"
dest_dir   = base_dir / "records"
```
It **reads `data/records/` (stale, 2025-12-11) and writes `records/` (live)**. The path bug (`base_dir` = `scripts/`) currently makes it a no-op. Fix the path without noticing the source/dest asymmetry and it overwrites `records/top10-*-alltime.md` from the stale fork. Its append-existing-alltime behaviour (`:180-186`) softens but does not eliminate this.

### R3 — HIGH: the relay mislabelling class of error is **only corrected after the fact, never prevented**

Four commits on 2025-12-16 (`1b6baf7`, `f2c5e97`, `5bb3316`, `10d5ae4`) removed three Free Relays that had been recorded as 200 Medley Relays, and added a genuine medley record that had been missing. All four were **manual, discovered by eyeballing times against MaxPreps**, as the messages say: *"WARNING: The remaining top entries from 2025 (1:52.45, 1:53.19) should also be verified — times seem suspiciously fast for medley relays."*

There are **two independent misclassification surfaces, and neither has a guard:**

**(a) `scripts/harvest/harvest_all_relay_splits.py:59-75`**
```python
stroke_keywords = ['back', 'breast', 'fly', 'free']
is_medley = any(kw in ' '.join(legs_lower) for kw in stroke_keywords[:3])
if is_medley and num_splits == 4:   return "200 Medley Relay"
elif num_splits == 8:               return "400 Free Relay"
elif num_splits == 4:               return "200 Free Relay"
```
Relay type is inferred **from the MaxPreps leg *labels***, because (per the script's own comment at `:82`) MaxPreps emits `ShowMedleySplitWindow(...)` for *all* relay types. When MaxPreps supplies generic labels, `is_medley` is False and any 4-split relay is classified "200 Free Relay". **This is not hypothetical: every entry in `data/historical_splits/splits_25-26.json` has `"legs": ["Split 1","Split 2","Split 3","Split 4"]`.** For those 29 entries the stroke evidence is simply absent and the classifier is guessing.

**(b) `scripts/generate_relay_records.py:46-55`**
```python
if "200" in event_lower and "medley" in event_lower:                    return "200-medley-relay"
if "200" in event_lower and ("free" in event_lower or "fr" in event_lower): return "200-free-relay"
```
Substring matching on an upstream `Event` string, with **`"fr"` as a bare substring** — it matches inside `freestyle`, `free`, and any other token containing `fr`. Order saves the medley case, but there is no validation that a row placed in the Medley bucket *has* medley splits.

**And the consumers do no better.** `rebuild_relay_pages.py:92-97` and `generate_website.py:757+` attach splits by **event-type string equality plus ≥3 swimmer-name overlap** — no stroke-order check, no leg-time plausibility check, no total-vs-sum-of-splits reconciliation (the split objects carry no total). A row mislabelled as Medley will happily render four freestyle splits under BK/BR/FL/FR headings, which is exactly what the site did until December.

**Nothing checks that a "200 Medley Relay" has a breaststroke leg slower than its freestyle leg.** That single sanity rule would have caught all three 2025 errors automatically.

### R4 — HIGH: a live, already-published data defect from the very fix that prompted this question

Commit `5bb3316` introduced a corruption that is **on tanqueverdeswim.org right now**. `records/relay-records-girls.md:10-13`:
```
| **1** | **01:53.50** | Isabelle Sansom, Sarynn Patterson, Kennady Pautler, Lindsey Schoel-Smith | Oct 26, 2018 | ...
| 2     | 01:53.58     | Isabelle Sansom, Kennady Pautler, Violet Dasse, Trinity Weatherwax | Nov 01, 2018 | ...
| 4     | 01:53.58     | Isabelle Sansom, Kennady Pautler, Violet Dasse, Trinity Weatherwax | Nov 01, 2018 | ...
| 5     | 01:54.06     | ...
```
The `01:53.58` row is **duplicated**, and the rank column **skips 3**. I confirmed both are rendered live at https://tanqueverdeswim.org/records/girls-relays.html (rows "2 … 1:53.58 Sansom, Pautler, Dasse, Weatherwax" and "4 …" both present). Remaining ranks run 5,6,7,…,14 with no 3 and no 15.

This is the signature of hand-editing markdown tables with no validator. **A trivial check — ranks are 1..N contiguous, and (time, date, participants) is unique within a table — would have caught it at commit time.** Nothing runs such a check.

### R5 — MEDIUM: `run_season_update.py` step ordering would compound damage

`run_season_update.py:112-128` runs `generate_hs_records.py` → `generate_relay_records.py` → `generate_all_season_top10.py` **unconditionally, with no dry-run, no backup, no diff review**, before `generate_website.py` at `:159`. The guide (`SEASON_UPDATE_GUIDE.md:9-13`) presents this as a one-command operation. If its path bugs were fixed without addressing R1, one command would rewrite the entire historical record set.

### R6 — MEDIUM: nothing pins historical records against change

There is no immutable/ratified record file, no "record set as of season N" snapshot, no checksum, no `previous`-value assertion outside `class_records_history.json` (which is itself hand-maintained). The only history is git. **Git is the sole safety net, and it is not enforced by any tooling.**

### R7 — LOW: the duplicated tree invites the wrong edit

`records/` vs `data/records/` differ in **every** shared file (meet names carry `(Tucson, AZ)`-style location suffixes in `data/records/`, stripped in `records/`). `claude.md` documents `records/`; `RECORDS_STRUCTURE.md:8` documents `data/records/`; `data/README.md` documents `data/records/scy/`, a third copy. An editor following the wrong doc edits a file nothing reads.

---

## OPEN QUESTIONS for Aaryn

These are genuinely ambiguous in the repo. I have not decided any of them.

1. **Do relay lead-off splits count as individual records?** `data/relay_leadoff_times.json` and `data/leadoff_exclusions.json` exist and are populated, but the only scripts that consume them (`scripts/archive/extract_leadoff_times.py`, `scripts/archive/merge_leadoff_times.py`) are archived. I cannot tell from the repo whether current `records/*.md` individual times include lead-offs. If they do, the exclusion list is unenforced; if they don't, two data files are dead weight. **This materially affects which 2026-27 swims are record-eligible.**

2. **Is `data/records/` alive or dead?** It is 5 days and 41 commits behind `records/`, with systematically different meet-name formatting. Delete it, or re-sync it, or leave it? Two scripts (`build_alltime_top10.py`, all the generators) still target it.

3. **Top 10 or Top 15 for relays?** `claude.md` says "Top 15 relay times per event". `generate_relay_records.py:173` says `nsmallest(10, ...)`. `rebuild_relay_pages.py:47` renders only `rank_num <= 10`. The live files carry 14-15 rows. Which is the rule?

4. **How is the 2026 AIA state PDF obtained?** `parse_aia_state_meets.py:18-44` carries `file_id` integers for 2001-2024 implying an `aiaonline.org` download endpoint, but 2025 is `None` (never ingested) and `aiaonline.org/sports/swimming-and-diving` 404s. **The acquisition URL is not recorded anywhere in the repo.**

5. **Is `swim-data-tool` coming back?** It is version-pinned (`.swim-data-tool-version` = `0.10.0`), referenced by 5 active scripts, and absent from this machine. Whether to repair the ingest pipeline or formally retire it changes the whole shape of a 2026-27 update. `claude.md` claims "No dependency on swim-data-tool" for website generation — true for `generate_website.py`, false for every record generator.

6. **What became of `data/raw/`?** Deliberately gitignored and evidently never backed up into this checkout. Does a copy exist elsewhere? Without it, the record markdown is the *only* surviving representation of TVHS swim history.

7. **Should 2025-26 season top-10 pages be produced before 2026-27 starts?** `generate_annual_pages.py:30` currently excludes 2025-26 by name. Adding 2026-27 without deciding this leaves a permanent hole.

8. **Does the club/school boundary matter for TVHS?** With only a team-name filter, a swimmer's club times could enter school records if a source labels them "Tanque Verde". Whether this has ever happened I cannot determine without `data/raw/`.

---

## Cross-check: the 2026-27 schedule lead (NOT FOUND)

I could not locate the family-calendar repo holding calendar theme `swim-tvhs`. Searched, read-only:
- `grep -rl 'swim-tvhs'` across all of `/Users/aaryn/workspaces` (json/yaml/yml/md/ics/ts/js/csv) → **no hits**
- Same grep across `/Users/aaryn/{ai-data,ai-context,scratch,incoming,sites,kitwork,ai-data-internal}`, plus `swim_tvhs` → **no hits**
- `find /Users/aaryn -maxdepth 4 -iname '*calendar*'` (excluding `Library/`) → **no hits**
- `/Users/aaryn/workspaces/personal` confirmed docs-only (`AGENTS.md`, `CLAUDE.md`, `README.md`, `artifacts/`, `decisions/`, `docs/`), as the lead anticipated.

Per instruction I time-boxed this and moved on. **The 10 meets, the Oct 17 HS Classic at U of A, and the Nov 6-7 AIA D-III State at PCDS remain unverified from this sandbox.**

Partial independent corroboration from MaxPreps (§5b): TVHS has swum **one** meet in 2026-27, on **Sep 19, 2026**, with the team score 128 recorded and the opponent unentered. MaxPreps itself reports **"No Schedule"** for 26-27, so it cannot confirm or refute the 10-meet list. A Sep 19 opener is consistent with an Oct 17 mid-season invitational and an early-November state meet — the 2025-26 pattern was Sep 20 / Sep 27 / Oct 18 / Oct 24 / Nov 8 (`records/annual-summary-2025-26.md:29-33`).

---

## RECOMMENDED FIRST UPDATE — the smallest safe 2026-27 change

**Described, not performed.** No file in the repo was modified by this investigation.

### Principle
Touch only the markdown→HTML pipeline, which is proven deterministic. Do not attempt to revive `swim-data-tool`, do not run any generator that writes `records/` or `data/records/`, and do not run `run_season_update.py`.

### Precondition: there is nothing to import yet
As of 2026-09-20 no source carries 2026-27 TVHS *times*. MaxPreps has one meet with a team score and no athlete stats; AZPreps365 needs Playwright and, being a season-to-date leaderboard, carries no per-meet dates or meet names at all; the AIA state meet has not happened. **The correct first update is scaffolding, not data.**

### Step 0 — fix the live defect first, on its own commit
Repair `records/relay-records-girls.md`: delete the duplicated `01:53.58` row and renumber ranks 1..N contiguously (R4). This is a pre-existing published error and should not be entangled with new-season work.

### Step 1 — create the 2026-27 scaffold (all hand-created, per `claude.md` §"Start a New Season")
```
records/annual-summary-2026-27.md            # structure copied from 2025-26, data cleared
records/top10-boys-2026-27.md                # header only
records/top10-girls-2026-27.md               # header only
data/historical_splits/splits_26-27.json     # {"boys": [], "girls": []}
```

### Step 2 — register the season in the hardcoded lists
- `scripts/generate_annual_pages.py:19-23` — append `"2026-27"` to `SEASONS`
- `scripts/generate_annual_pages.py:30` — **decide the 2025-26 question (OQ 7)**; if 2025-26 top-10s are being created, this line can become `TOP10_SEASONS = [s for s in SEASONS if s != "2026-27"]`, otherwise it needs both exclusions
- `scripts/generate_website.py:56-73` — add `2026-27` (and `2025-26`, if produced) to the hand-written "Top 10 by Year" dropdown literal
- `scripts/generate_website.py:~79` — add `2026-27` to the "Summary by Year" dropdown literal
- `docs/index.html:80` — add the `/annual/2026-27.html` link

### Step 3 — render and inspect
```bash
python3 scripts/generate_website.py
git diff --stat
```
**Expect a date-only diff on ~60 existing pages** (footer year 2025→2026, "Generated on" line) plus the genuinely new `docs/annual/2026-27.html` and any new top-10 pages. Anything else in the diff is a signal to stop and look.

### Step 4 — publish
```bash
git add -A
git commit -m "Scaffold 2026-27 season"
git push origin main
```
GitHub Pages serves `docs/` from `main`; `docs/CNAME` routes it to tanqueverdeswim.org; live in 1-3 minutes. **Coordinator action — not the worker's.**

### Then, per meet, for the rest of the season
Hand-enter results into `records/records-*.md`, `records/relay-records-*.md`, `records/top10-*-2026-27.md`, appending class records to `data/class_records_history.json` and splits to `data/historical_splits/splits_26-27.json`; run `enrich_previous_record_locations.py` and `generate_website.py`; commit. This is the workflow `WORKFLOW.md:19-42` already documents, and it is the only one that currently works.

### Explicitly NOT recommended for a first update
- `run_season_update.py` — broken paths, missing dependency, and R1/R5 risk
- any of `generate_hs_records.py`, `generate_relay_records.py`, `generate_all_season_top10.py`, `generate_all_annual_summaries.py`, `build_alltime_top10.py` — R1/R2
- reviving the AZPreps365 harvest — it produces division leaderboards with no dates or meet names, which is not the shape `records/*.md` needs
- touching `data/records/` until OQ 2 is answered

### Two cheap guards worth adding before 2026-27 data starts flowing (proposals only)
1. **A relay-plausibility check.** For any row in a `## 200 Medley Relay` table with attached splits, assert the leg pattern looks like a medley (breaststroke leg slowest, freestyle leg fastest, spread beyond ~1.5s). This alone would have caught all three December 2025 mislabellings automatically.
2. **A markdown table linter.** Assert ranks are contiguous `1..N` and `(time, date, participants)` is unique per table. This would have caught R4 at commit time.

Both are pure-stdlib, read-only, and would be the repo's first actual tests.

---

*Report produced under an investigation-only work order. No records were modified, no PR opened, no publish performed, no BOARD claim posted. The only file written was this report.*
