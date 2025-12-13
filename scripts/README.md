# Tanque Verde Swimming - Scripts

This directory contains all Python scripts for maintaining the website.

## Directory Structure

```
scripts/
├── README.md              # This file
├── *.py                   # Active operational scripts (23)
├── harvest/               # Data harvesting scripts (17)
└── archive/               # Archived/superseded scripts (27)
```

## Quick Start

### Regenerate Entire Website

```bash
cd ~/workspaces/swimming/tanque-verde-swim
python3 scripts/generate_website.py
```

This runs automatically:
1. `generate_website.py` - Main generator
2. `rebuild_relay_pages.py` - Relay pages with splits
3. `generate_annual_pages.py` - Annual summary pages

---

## Script Categories

### 🟢 Core Generation (3 scripts)

| Script | Purpose |
|--------|---------|
| `generate_website.py` | **Main entry point** - runs all generators |
| `generate_annual_pages.py` | Creates annual summary HTML pages |
| `rebuild_relay_pages.py` | Creates relay pages with expandable splits |

### 🟡 Data Enrichment (4 scripts)

| Script | Purpose |
|--------|---------|
| `enrich_previous_record_locations.py` | Add meet locations to previous records |
| `enrich_leadoff_times.py` | Add leadoff times to relay data |
| `enrich_relay_leadoffs.py` | Enrich relay records with leadoff splits |
| `add_2025_26_class_records.py` | Extract class records (template for new seasons) |

### 🔵 Analysis Tools (4 scripts)

| Script | Purpose |
|--------|---------|
| `analyze_season.py` | Find records broken in a season |
| `analyze_state_meet.py` | State championship highlights |
| `analyze_seniors.py` | Senior class career highlights |
| `analyze_class_of_2026.py` | Class of 2026 analysis |

### 🟣 Data Builders (8 scripts)

| Script | Purpose |
|--------|---------|
| `build_alltime_top10.py` | Rebuild all-time top 10 from source |
| `build_class_records_history.py` | Rebuild class_records_history.json |
| `generate_all_season_top10.py` | Generate all season top10 files |
| `generate_all_annual_summaries.py` | Generate all annual summary markdown |
| `generate_hs_records.py` | Generate high school format records |
| `generate_relay_records.py` | Generate relay-records-*.md files |
| `generate_top10.py` | Generate top 10 markdown |
| `process_top10_with_aliases.py` | Apply name aliases to top10 |

### 🟤 Utilities (4 scripts)

| Script | Purpose |
|--------|---------|
| `time_formatter.py` | Format swim times consistently |
| `extract_leaderboard_from_webpage.py` | Extract data from HTML tables |
| `update_senior_cards.py` | Update senior swimmer cards |
| `run_season_update.py` | Orchestrator for full season update |

---

## Subdirectories

### `harvest/` - Data Harvesting (17 scripts)

Scripts for importing data from external sources:
- `harvest_azpreps365*.py` - AZPreps365 scraping
- `parse_aia_state_meets.py` - State championship PDF parsing
- `import_*.py` - Data import scripts
- `merge_*.py` - Data merging utilities

### `archive/` - Archived Scripts (27 scripts)

Historical scripts that are no longer needed:
- `fix_*.py` - One-time data fixes (already applied)
- `debug_*.py` - Development/debugging scripts
- Superseded versions replaced by newer scripts

---

## Usage Examples

### Regenerate website
```bash
python3 scripts/generate_website.py
```

### Analyze a season
```bash
python3 scripts/analyze_season.py --season 25-26
```

### Enrich class records
```bash
python3 scripts/enrich_previous_record_locations.py
```

### Full season update
```bash
python3 scripts/run_season_update.py --season 26-27 --state-pdf ~/Downloads/state.pdf
```

---

**Last Updated:** December 12, 2025

