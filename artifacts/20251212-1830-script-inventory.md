# Tanque Verde Swim - Complete Script Inventory

> Reference: @claude.md for project context

## Summary

**Total Scripts:** 67 Python files  
**Status:** ✅ REORGANIZED (December 12, 2025)

## Final Structure

```
scripts/                    # 23 active operational scripts
scripts/harvest/            # 17 harvesting scripts
scripts/archive/            # 27 archived/superseded scripts
```

| Location | Count | Contents |
|----------|-------|----------|
| `scripts/` | 23 | Core generation, enrichment, analysis, builders, utilities |
| `scripts/harvest/` | 17 | Data harvesting and import scripts |
| `scripts/archive/` | 27 | One-time fixes, superseded versions, debug scripts |

---

## 🟢 Core Generation (3 scripts) - REQUIRED

These scripts regenerate the website. Run `generate_website.py` which calls the others.

| Script | Purpose | Called By |
|--------|---------|-----------|
| `generate_website.py` | **Main entry point** - regenerates all HTML | Manual |
| `generate_annual_pages.py` | Creates annual summary HTML (14 pages) | generate_website.py |
| `rebuild_relay_pages.py` | Creates relay pages with expandable splits | generate_website.py |

---

## 🟡 Data Enrichment (4 scripts) - AS NEEDED

Run these after adding new data to enrich with additional info.

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `enrich_previous_record_locations.py` | Add meet locations to previous records in class_records_history.json | After adding class records |
| `enrich_leadoff_times.py` | Add leadoff times to relay data | After harvesting relay splits |
| `enrich_relay_leadoffs.py` | Enrich relay records with leadoff splits | After updating relay data |
| `add_2025_26_class_records.py` | Extract class records for 2025-26 season | **Template** - copy for new seasons |

---

## 🔵 Analysis Tools (4 scripts) - USEFUL

These analyze data and generate insights. Not required for website generation.

| Script | Purpose | Usage |
|--------|---------|-------|
| `analyze_season.py` | Find records broken in a season | `python analyze_season.py --season 25-26` |
| `analyze_state_meet.py` | State championship highlights | `python analyze_state_meet.py --year 2025` |
| `analyze_seniors.py` | Senior class career highlights | `python analyze_seniors.py --class-year 2026` |
| `analyze_class_of_2026.py` | Specific analysis for Class of 2026 | One-time for 2026 seniors |

---

## 🟠 Harvesting/Import (17 scripts) - FOR NEW DATA

These import data from external sources. Required when adding new seasons.

### AZPreps365 Harvesting
| Script | Purpose | Notes |
|--------|---------|-------|
| `harvest_azpreps365.py` | Original AZPreps scraper | Works but older |
| `harvest_azpreps365_v2.py` | Improved version with better parsing | Better error handling |
| `harvest_azpreps365_v3.py` | **Latest version** | **USE THIS ONE** |
| `parse_azpreps365_html.py` | Parse downloaded AZPreps HTML | Helper for harvesting |

### State Championship (AIA)
| Script | Purpose | Notes |
|--------|---------|-------|
| `parse_aia_state_meets.py` | Parse state championship PDFs | Requires pdfplumber |
| `merge_aia_state_data.py` | Merge parsed state data into records | After parsing PDFs |
| `import_state_2012_2014.py` | Import historical state data (2012-2014) | One-time import |
| `update_state_parser.py` | Update parser for new year | Called by run_season_update.py |

### Relay Data
| Script | Purpose | Notes |
|--------|---------|-------|
| `harvest_relays.py` | Original relay harvester | Works but older |
| `harvest_relays_v2.py` | **Latest relay harvester** | **USE THIS ONE** |
| `harvest_all_relay_splits.py` | Harvest splits from all seasons | Comprehensive |
| `harvest_relay_splits_2025.py` | 2025 season relay splits | Season-specific |
| `import_relays.py` | Import relay data into records | After harvesting |

### SwimCloud/Other
| Script | Purpose | Notes |
|--------|---------|-------|
| `harvest_2025_state_swimcloud.py` | SwimCloud state data | 2025 specific |
| `harvest_division_complete.py` | Comprehensive division data | Large harvest |
| `import_historical_state.py` | Import historical state data | One-time |
| `extract_historical_state.py` | Extract from old formats | One-time |

---

## 🟣 Data Builders (8 scripts) - MAY STILL NEED

These build/rebuild data structures. Some may be needed for major updates.

| Script | Purpose | When Needed |
|--------|---------|-------------|
| `build_alltime_top10.py` | Rebuild all-time top 10 from source data | If top10-*-alltime.md is wrong |
| `build_class_records_history.py` | Rebuild class_records_history.json | If history file is corrupted |
| `generate_all_season_top10.py` | Generate all season top10 files | After major data changes |
| `generate_all_annual_summaries.py` | Generate all annual summary markdown | After major data changes |
| `generate_hs_records.py` | Generate high school format records | Alternative format |
| `generate_relay_records.py` | Generate relay-records-*.md files | After relay data changes |
| `generate_top10.py` | Generate top 10 markdown | Single season |
| `process_top10_with_aliases.py` | Apply name aliases to top10 | After alias updates |

---

## ⚪ One-Time Fixes (11 scripts) - ALREADY RUN

These fixed data issues and have already been applied. Safe to archive.

| Script | Purpose | Status |
|--------|---------|--------|
| `fix_2020_years.py` | Fix swimmer years for 2020-21 season | ✅ Done |
| `fix_data_quality.py` | General data quality fixes | ✅ Done |
| `fix_empty_events.py` | Fill empty events in top10 | ✅ Done |
| `fix_grades_by_season.py` | Correct grade assignments | ✅ Done |
| `fix_meet_duplicates.py` | Remove duplicate meet entries | ✅ Done |
| `fix_missing_years.py` | Add missing year data | ✅ Done |
| `consolidate_swimmers.py` | Merge duplicate swimmer entries | ✅ Done |
| `detect_name_duplicates.py` | Find swimmer name variations | ✅ Done |
| `normalize_meet_names.py` | Standardize meet names | ✅ Done |
| `add_2025_state_relays.py` | Add 2025 state relay results | ✅ Done |
| `add_inline_badges.py` | Add badge HTML to pages | ✅ Done |

---

## 🔴 Superseded/Duplicates (13 scripts) - REPLACED

These have been replaced by newer versions or are no longer needed.

| Script | Replaced By | Notes |
|--------|-------------|-------|
| `generate_enhanced_annual.py` | `generate_annual_pages.py` | Old version |
| `generate_annual_summary.py` | `generate_annual_pages.py` | Old version |
| `generate_methods.py` | Various | Obsolete helpers |
| `format_annual_summary.py` | `generate_annual_pages.py` | Old formatter |
| `rebuild_class_records.py` | `build_class_records_history.py` | Duplicate |
| `rebuild_overall_records.py` | `generate_website.py` | Now integrated |
| `add_splits_to_relay_pages.py` | `rebuild_relay_pages.py` | Now integrated |
| `apply_all_splits.py` | `rebuild_relay_pages.py` | Now integrated |
| `extract_and_apply_splits.py` | `rebuild_relay_pages.py` | Now integrated |
| `update_relay_splits.py` | `rebuild_relay_pages.py` | Now integrated |
| `merge_splits.py` | `rebuild_relay_pages.py` | Now integrated |
| `extract_leadoff_times.py` | `enrich_leadoff_times.py` | Old version |
| `merge_leadoff_times.py` | `enrich_leadoff_times.py` | Old version |

---

## 🟤 Utilities (3 scripts) - SHARED HELPERS

Utility modules used by other scripts.

| Script | Purpose | Used By |
|--------|---------|---------|
| `time_formatter.py` | Format swim times consistently | Multiple scripts |
| `extract_leaderboard_from_webpage.py` | Extract data from HTML tables | Harvesting scripts |
| `update_senior_cards.py` | Update senior swimmer cards | Annual pages |

---

## ⚫ Debug/Test (4 scripts) - DEVELOPMENT ONLY

Development and debugging scripts. Not needed for production.

| Script | Purpose | Notes |
|--------|---------|-------|
| `debug_azpreps_page.py` | Debug AZPreps365 page structure | Development |
| `debug_swimcloud.py` | Debug SwimCloud page structure | Development |
| `test_harvest_setup.py` | Test harvesting configuration | Development |
| `run_season_update.py` | **Orchestrator** - runs full season update | Useful but needs swim-data-tool |

---

## Recommended Actions

### Keep in Root (Active)
- 🟢 Core Generation (3)
- 🟡 Data Enrichment (4)
- 🔵 Analysis Tools (4)
- 🟤 Utilities (3)
- `run_season_update.py` (orchestrator)

**Total: 15 scripts**

### Move to `archive/scripts/` (Historical)
- ⚪ One-Time Fixes (11)
- 🔴 Superseded/Duplicates (13)
- ⚫ Debug/Test (3, excluding run_season_update.py)

**Total: 27 scripts**

### Move to `harvest/` Subdirectory
- 🟠 Harvesting/Import (17)

**Total: 17 scripts**

### Keep but Mark as "May Need"
- 🟣 Data Builders (8)

**Total: 8 scripts**

---

## Summary Table

| Action | Count | Scripts |
|--------|-------|---------|
| **Keep Active** | 15 | Core + Enrichment + Analysis + Utilities + Orchestrator |
| **Move to harvest/** | 17 | All harvesting/import scripts |
| **Keep but Review** | 8 | Data builder scripts |
| **Archive** | 27 | Fixes + Superseded + Debug |
| **Total** | 67 | |

---

**Date:** December 12, 2025

