# Tanque Verde Swimming Website - Maintenance Workflow

**Last Updated:** December 12, 2025

This document describes the complete workflow for maintaining and updating https://tanqueverdeswim.org

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Data Sources](#data-sources)
4. [Core Data Files](#core-data-files)
5. [Active Scripts](#active-scripts)
6. [Generation Workflow](#generation-workflow)
7. [Common Tasks](#common-tasks)
8. [Deployment](#deployment)

---

## Overview

The website is a static site generated from markdown source files and JSON data files. The generated HTML is stored in `docs/` and deployed via GitHub Pages.

**Repository:** https://github.com/aaryno/tanque-verde-swim
**Live Site:** https://tanqueverdeswim.org

---

## Directory Structure

```
tanque-verde-swim/
├── docs/                      # Generated HTML (deployed via GitHub Pages)
│   ├── index.html             # Splash page (manually maintained)
│   ├── css/style.css          # Main stylesheet
│   ├── images/                # Logos and images
│   ├── records/               # Overall records, relays, by-grade pages
│   ├── top10/                 # All-time and seasonal top 10 pages
│   └── annual/                # Annual summary pages (2012-13 through 2025-26)
│
├── records/                   # Source markdown files
│   ├── records-boys.md        # Boys team records (SOURCE OF TRUTH)
│   ├── records-girls.md       # Girls team records (SOURCE OF TRUTH)
│   ├── annual-summary-*.md    # Annual summary data
│   └── top10-*.md             # Top 10 lists by season
│
├── data/                      # JSON data files
│   ├── class_records_history.json    # All class records with previous holders
│   ├── all_relays.json               # Raw relay data (harvested)
│   ├── relay_leadoff_times.json      # Leadoff splits for top 10
│   ├── historical_splits/            # Relay splits by season
│   └── records/                      # Processed records data
│
├── artifacts/                 # Session notes and debugging logs
│
└── [scripts]                  # Python generation scripts (see below)
```

---

## Data Sources

### Primary Data Sources
1. **AZPreps365** - Arizona high school sports results
2. **MaxPreps** - National high school sports database
3. **SwimCloud** - Swimming-specific results database
4. **Manual Entry** - Historical records, corrections

### Data Entry Points
- **Team Records:** Edit `records/records-boys.md` and `records/records-girls.md`
- **Class Records:** Add to `data/class_records_history.json`
- **Relay Splits:** Add to `data/historical_splits/splits_YYYY-YY.json`

---

## Core Data Files

### `records/records-boys.md` and `records/records-girls.md`
**Purpose:** Source of truth for all team records
**Format:** Markdown tables with Grade, Time, Athlete, Date, Meet columns
**Updated:** Manually when new records are set

### `data/class_records_history.json`
**Purpose:** Historical class records (FR/SO/JR/SR) with previous record info
**Format:** JSON array of record objects with `previous` nested object
**Updated:** Run `add_YYYY_YY_class_records.py` or add manually

### `data/historical_splits/*.json`
**Purpose:** Relay split times by season
**Format:** JSON with relay events and swimmer splits
**Updated:** Add new `splits_YYYY-YY.json` files

### `records/annual-summary-*.md`
**Purpose:** Annual summary data (records broken, season stats)
**Format:** Markdown with structured sections
**Updated:** End of each season

---

## Active Scripts

### Primary Generation Scripts (REQUIRED)

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `generate_website.py` | Main entry point - generates all pages | After any data changes |
| `generate_annual_pages.py` | Creates annual summary HTML pages | Called by generate_website.py |
| `rebuild_relay_pages.py` | Creates relay records pages with splits | Called by generate_website.py |

### Data Enrichment Scripts (AS NEEDED)

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `enrich_previous_record_locations.py` | Adds meet locations to previous records | After adding new class records |
| `add_2025_26_class_records.py` | Extract class records from markdown | Template for new seasons |

### One-Time/Utility Scripts (ARCHIVE CANDIDATES)

These scripts were used for initial data import or one-time fixes:
- `harvest_*.py` - Data harvesting from external sources
- `import_*.py` - Data import scripts
- `fix_*.py` - Data cleanup scripts
- `build_*.py` - Initial data structure building

---

## Generation Workflow

### Full Site Regeneration

```bash
cd /Users/aaryn/workspaces/swimming/tanque-verde-swim
python3 generate_website.py
```

This will:
1. Generate `docs/records/overall.html` (Overall Team Records)
2. Generate by-grade pages (`boys-bygrade.html`, `girls-bygrade.html`)
3. Call `rebuild_relay_pages.py` for relay pages
4. Convert all `top10-*.md` files to card-format HTML
5. Call `generate_annual_pages.py` for annual summaries

### After Adding Class Records

```bash
python3 enrich_previous_record_locations.py  # Add meet locations
python3 generate_annual_pages.py             # Regenerate annual pages
```

---

## Common Tasks

### Task 1: Add a New Record

1. **Edit source markdown:**
   ```
   records/records-boys.md  (or records-girls.md)
   ```
   Update the appropriate event table with new time/athlete/date/meet

2. **If it's a class record, add to history:**
   ```bash
   # Edit data/class_records_history.json
   # Or create a script like add_2025_26_class_records.py
   ```

3. **Regenerate:**
   ```bash
   python3 generate_website.py
   ```

4. **Commit and push:**
   ```bash
   git add -A && git commit -m "Add new record: [event] [time] [athlete]"
   git push
   ```

### Task 2: Start a New Season

1. **Create annual summary markdown:**
   ```
   records/annual-summary-YYYY-YY.md
   ```

2. **Create top 10 files:**
   ```
   records/top10-boys-YYYY-YY.md
   records/top10-girls-YYYY-YY.md
   ```

3. **Add relay splits (if available):**
   ```
   data/historical_splits/splits_YYYY-YY.json
   ```

4. **Regenerate and push**

### Task 3: Update Relay Splits

1. **Add/edit split file:**
   ```
   data/historical_splits/splits_YYYY-YY.json
   ```

2. **Regenerate relay pages:**
   ```bash
   python3 rebuild_relay_pages.py
   ```

### Task 4: Update the Splash Page (index.html)

The splash page at `docs/index.html` is **manually maintained**. Edit it directly.

---

## Deployment

The site auto-deploys via GitHub Pages when changes are pushed to the `main` branch.

```bash
git add -A
git commit -m "Description of changes"
git push origin main
```

**CDN Cache:** Changes may take a few minutes to appear. Hard refresh (Cmd+Shift+R) to see updates immediately.

---

## Troubleshooting

### Pages are empty after generation
- Check regex patterns in generator scripts
- Verify markdown file format matches expected patterns

### Previous record locations are blank
- Run `python3 enrich_previous_record_locations.py`
- Ensure the previous record exists in `class_records_history.json`

### Class records not appearing in annual pages
- Verify entries exist in `data/class_records_history.json`
- Check that `season` field matches the page (e.g., "2025-26")

---

## Appendix: Script Inventory

### Scripts to KEEP (Active Use)
- `generate_website.py`
- `generate_annual_pages.py`
- `rebuild_relay_pages.py`
- `enrich_previous_record_locations.py`

### Scripts to ARCHIVE (One-Time Use / Templates)
- `add_2025_26_class_records.py` (template for future seasons)
- `harvest_*.py` (data harvesting - run externally)
- `import_*.py` (initial data imports)
- `fix_*.py` (one-time fixes)
- `build_*.py` (initial structure building)
- `extract_*.py` (data extraction utilities)
- `merge_*.py` (data merging utilities)

### Scripts to REVIEW (May be obsolete)
- Any script not mentioned in this document
- Scripts with similar names (duplicates)

---

## Contact

**Maintainer:** aaryno@gmail.com
