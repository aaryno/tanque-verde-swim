# Tanque Verde Swimming Website - AI Assistant Context

## Repository Overview

This is the **self-contained** repository for the Tanque Verde High School Swimming records website.

**Live Site:** https://tanqueverdeswim.org  
**GitHub:** https://github.com/aaryno/tanque-verde-swim

---

## Quick Start

### Regenerate Entire Website (Most Common)

```bash
cd ~/workspaces/swimming/tanque-verde-swim
python3 scripts/generate_website.py
git add -A && git commit -m "Regenerate website" && git push
```

That's it! The site auto-deploys via GitHub Pages in 1-3 minutes.

### First-Time Setup (New Computer)

```bash
cd ~/workspaces/swimming/tanque-verde-swim

# Create virtual environment (one-time)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (only needed for harvesting/analysis)
pip install -r requirements.txt

# For playwright-based scripts (SwimCloud scraping)
playwright install chromium
```

### Each Session

```bash
cd ~/workspaces/swimming/tanque-verde-swim
source .venv/bin/activate  # If using harvesting/analysis scripts
```

---

## Python Environment

### Requirements

- **Python 3.9+**
- **For website generation:** No external packages (stdlib only)
- **For harvesting/analysis:** See `requirements.txt`

### Key Packages

| Package | Purpose | Scripts That Use It |
|---------|---------|---------------------|
| pandas | Data processing | `generate_top10.py`, `analyze_*.py`, most harvest scripts |
| beautifulsoup4 | HTML parsing | `harvest_azpreps365.py`, `parse_azpreps365_html.py` |
| requests | HTTP requests | `harvest_azpreps365.py` |
| pdfplumber | PDF parsing | `parse_aia_state_meets.py` |
| playwright | Browser automation | `debug_swimcloud.py`, `harvest_division_complete.py` |

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
│   ├── annual/                # Annual summary pages (2012-13 through 2025-26)
│   └── archive/               # Backup of website (Dec 2025)
│
├── records/                   # SOURCE OF TRUTH - Markdown files
│   ├── records-boys.md        # Boys team records (edit this!)
│   ├── records-girls.md       # Girls team records (edit this!)
│   ├── relay-records-boys.md  # Boys relay records
│   ├── relay-records-girls.md # Girls relay records
│   ├── annual-summary-*.md    # Annual summary data
│   └── top10-*.md             # Top 10 lists by season
│
├── data/                      # JSON data files
│   ├── class_records_history.json    # All class records with previous holders
│   ├── all_relays.json               # Raw relay data (harvested)
│   ├── swimmer_aliases.json          # Name normalization
│   ├── historical_splits/            # Relay splits by season
│   │   ├── all_relay_splits.json     # Combined splits for all seasons
│   │   └── splits_YYYY-YY.json       # Per-season relay splits
│   └── lookups/                      # Rosters and swimmer data
│
├── scripts/                   # All Python scripts
│   ├── generate_website.py    # Main entry point
│   ├── *.py                   # Active scripts (23 total)
│   ├── harvest/               # Data harvesting scripts (17)
│   └── archive/               # Archived/superseded scripts (27)
│
├── artifacts/                 # Session notes, debugging logs
│
├── requirements.txt           # Python dependencies
├── claude.md                  # This file - AI assistant context
├── WORKFLOW.md                # Quick reference guide
└── SEASON_UPDATE_GUIDE.md     # End-of-season workflow
```

---

## Script Categories

All scripts are in the `scripts/` directory.

### 🟢 Core Generation (ALWAYS NEEDED)

These scripts generate the website. They only use Python stdlib.

| Script | Purpose | Called By |
|--------|---------|-----------|
| `scripts/generate_website.py` | **Main entry point** - runs all generators | Manual |
| `scripts/generate_annual_pages.py` | Creates annual summary HTML pages | generate_website.py |
| `scripts/rebuild_relay_pages.py` | Creates relay pages with expandable splits | generate_website.py |

### 🟡 Data Enrichment (AS NEEDED)

Run these after adding new data to enrich with additional info.

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/enrich_previous_record_locations.py` | Adds meet locations to previous records | After adding class records |
| `scripts/add_2025_26_class_records.py` | Template for extracting class records | Copy & modify for new seasons |

### 🟠 Harvesting Scripts

Located in `scripts/harvest/` - for importing data from external sources:
- `harvest_azpreps365_v3.py` - Latest AZPreps365 scraper
- `parse_aia_state_meets.py` - State championship PDF parsing
- `merge_aia_state_data.py` - Merge parsed state data

### ⚪ Archived Scripts

Located in `scripts/archive/` - one-time fixes and superseded versions (27 scripts).

### 🔵 Analysis Tools

Useful for generating insights and summaries.

| Script | Purpose | Usage |
|--------|---------|-------|
| `analyze_season.py` | Find records broken in a season | `python analyze_season.py --season 25-26` |
| `analyze_state_meet.py` | State meet highlights | `python analyze_state_meet.py --year 2025` |
| `analyze_seniors.py` | Senior class highlights | `python analyze_seniors.py --class-year 2026` |
| `build_alltime_top10.py` | Rebuild all-time top 10 lists | Manual |

### 🟠 Harvesting Scripts

For importing data from external sources. Require `requirements.txt` dependencies.

| Script | Purpose | Data Source |
|--------|---------|-------------|
| `harvest_azpreps365.py` | Scrape meet results | AZPreps365 |
| `harvest_azpreps365_v3.py` | Latest version with better parsing | AZPreps365 |
| `parse_aia_state_meets.py` | Parse state championship PDFs | AIA website |
| `merge_aia_state_data.py` | Merge parsed state data | Local files |
| `harvest_division_complete.py` | Comprehensive division harvest | Multiple sources |

### ⚪ One-Time/Archive (ALREADY RUN)

These were used for initial setup or one-time fixes. Keep for reference.

- `fix_*.py` - Data cleanup scripts (already run)
- `import_*.py` - Initial data imports (already run)
- `build_*.py` - Initial structure building (already run)
- `extract_*.py` - Data extraction utilities
- `merge_*.py` - Data merging utilities

---

## Data File Formats

### `records/records-boys.md` and `records-girls.md` (SOURCE OF TRUTH)

Format: Markdown with event sections and grade tables.

```markdown
### 50 Freestyle

| Grade | Time | Athlete | Date | Meet |
|-------|------|---------|------|------|
| Freshman | 23.45 | John Smith | 11/15/2024 | Mesa Relays |
| Sophomore | 22.89 | Mike Davis | 1/10/2023 | Div III Champs |
| Junior | 22.34 | Alex Johnson | 2/05/2022 | State |
| Senior | 21.98 | Chris Brown | 11/20/2021 | Regionals |
| **Open** | **21.34** | **Record Holder** | **1/20/2020** | **State** |
```

**Rules:**
- **Bold** (`**text**`) = OPEN record (overall school record)
- Grades: Freshman, Sophomore, Junior, Senior, Open
- One section per event (### Event Name)

### `records/relay-records-*.md`

Format: Top 15 relay times per event.

```markdown
## 200 Medley Relay

| Rank | Time | Participants | Date | Meet |
|------|------|--------------|------|------|
| **1** | **1:42.35** | **A. Smith, B. Jones, C. Davis, D. Wilson** | **11/15/2024** | **State** |
| 2 | 1:43.21 | E. Brown, F. Lee, G. Park, H. Chen | 10/20/2023 | Mesa Relays |
...
```

### `data/class_records_history.json`

Tracks class records with previous record holders for annual pages.

```json
[
  {
    "season": "2024-25",
    "gender": "boys",
    "event": "50 Freestyle",
    "grade": "FR",
    "time": "23.45",
    "swimmer": "John Smith",
    "date": "11/15/2024",
    "meet": "Mesa Relays",
    "previous": {
      "time": "24.12",
      "swimmer": "Previous Holder",
      "date": "12/01/2020",
      "meet": "Regionals"
    }
  }
]
```

### `data/historical_splits/splits_YYYY-YY.json`

Relay split times for a season.

```json
{
  "boys": [
    {
      "type": "200 Medley Relay",
      "time": "1:42.35",
      "swimmers": ["A. Smith - Sr.", "B. Jones - Jr.", "C. Davis - So.", "D. Wilson - Fr."],
      "splits": ["26.54", "29.87", "24.32", "21.62"],
      "meet": "State Championships",
      "date": "11/15/2024"
    }
  ],
  "girls": [...]
}
```

### `data/swimmer_aliases.json`

Name normalization for consistent display.

```json
{
  "Christopher Smith": "Chris Smith",
  "Michael Johnson Jr.": "Mike Johnson"
}
```

---

## Common Workflows

### 1. Regenerate Entire Website

```bash
cd ~/workspaces/swimming/tanque-verde-swim
python3 scripts/generate_website.py
git add -A && git commit -m "Regenerate website" && git push
```

### 2. Add a New Individual Record

1. **Edit source markdown:**
   ```bash
   # Edit records/records-boys.md or records/records-girls.md
   # Update the appropriate event table
   ```

2. **If it's a class record (FR/SO/JR/SR), add to history:**
   ```bash
   # Edit data/class_records_history.json
   # Add new entry with previous record info
   ```

3. **Regenerate and deploy:**
   ```bash
   python3 scripts/generate_website.py
   git add -A && git commit -m "New record: [event] [time] [athlete]"
   git push
   ```

### 3. Add Relay Splits

1. **Edit or create splits file:**
   ```bash
   # Edit data/historical_splits/splits_YYYY-YY.json
   # Or create new file for new season
   ```

2. **Regenerate relay pages:**
   ```bash
   python3 scripts/rebuild_relay_pages.py
   python3 scripts/generate_website.py
   ```

### 4. Start a New Season (e.g., 2026-27)

1. **Create annual summary markdown:**
   ```bash
   touch records/annual-summary-2026-27.md
   # Copy structure from previous year and clear data
   ```

2. **Create top 10 files:**
   ```bash
   touch records/top10-boys-2026-27.md
   touch records/top10-girls-2026-27.md
   ```

3. **Create splits file:**
   ```bash
   touch data/historical_splits/splits_26-27.json
   # Add: {"boys": [], "girls": []}
   ```

4. **Update `scripts/generate_annual_pages.py`:**
   ```python
   # Add "2026-27" to SEASONS list
   SEASONS = [..., "2025-26", "2026-27"]
   ```

5. **Regenerate:**
   ```bash
   python3 scripts/generate_website.py
   ```

### 5. End-of-Season Update (Comprehensive)

For a complete season update with harvesting and analysis, see `SEASON_UPDATE_GUIDE.md`.

Quick version:
```bash
# 1. Download state championship PDF from AIA website

# 2. Run automated update (if using swim-data-tool)
python scripts/run_season_update.py \
  --season 26-27 \
  --state-pdf ~/Downloads/d3-state-2026.pdf \
  --senior-class 2027

# 3. Or manually:
python scripts/harvest/parse_aia_state_meets.py   # Parse state PDF
python scripts/harvest/merge_aia_state_data.py   # Merge into data
python scripts/generate_website.py               # Regenerate site

# 4. Commit and push
git add -A && git commit -m "Season 2026-27 update" && git push
```

### 6. Update the Splash Page (index.html)

The splash page at `docs/index.html` is **manually maintained**. Edit it directly to:
- Add season highlights
- Update records broken section
- Add state meet results

---

## Website Styling

### Color Theme

Colors defined in `docs/css/style.css`:

```css
--tvhs-primary: #2C5F2D;     /* Forest Green */
--tvhs-secondary: #C0C0C0;   /* Silver */
.boys-nav: #2C5F2D;          /* Forest green */
.girls-nav: #808080;         /* Silver/Grey */
```

### Page Types

| Page | Location | Generated By |
|------|----------|--------------|
| Splash/Home | `docs/index.html` | Manual |
| Overall Records | `docs/records/overall.html` | generate_website.py |
| By-Grade Records | `docs/records/boys-bygrade.html` | generate_website.py |
| Relay Records | `docs/records/boys-relays.html` | rebuild_relay_pages.py |
| Top 10 (All-Time) | `docs/top10/boys-alltime.html` | generate_website.py |
| Top 10 (Season) | `docs/top10/boys-2024-25.html` | generate_website.py |
| Annual Summary | `docs/annual/2024-25.html` | generate_annual_pages.py |

---

## Relationship to swim-data-tool

**Historical Context:** This repo started using `swim-data-tool` for data harvesting, but has evolved to be largely independent.

### For Website Generation
- ✅ **No dependency on swim-data-tool**
- All generation scripts use local markdown/JSON files
- Just run `python3 generate_website.py`

### For Data Harvesting (Optional)
Some scripts reference swim-data-tool for MaxPreps data:
- `run_season_update.py` uses `swim-data-tool roster` and `import swimmers`
- Alternative: Use standalone harvest scripts directly (`harvest_azpreps365.py`, etc.)

### If You Want swim-data-tool Integration
```bash
# In a separate directory
cd ~/workspaces/swimming/swim-data-tool
source .venv/bin/activate
pip install -e .

# Then run from TV directory
cd ~/workspaces/swimming/tanque-verde-swim
swim-data-tool roster --seasons=25-26
```

---

## Data Sources

### Primary Sources
1. **AZPreps365** - Arizona high school sports results (https://azpreps365.com)
2. **MaxPreps** - National high school sports database (https://maxpreps.com)
3. **SwimCloud** - Swimming-specific results (https://swimcloud.com)
4. **AIA** - Arizona Interscholastic Association (state championship PDFs)

### Manual Entry
- Historical records before 2007
- Corrections and additions
- Records from meets not on primary sources

---

## Troubleshooting

### Pages are empty after generation
- Check regex patterns in generator scripts
- Verify markdown file format matches expected patterns
- Check for syntax errors in markdown tables

### Previous record locations are blank
```bash
python3 enrich_previous_record_locations.py
```
- Ensure the previous record exists in `data/class_records_history.json`

### Class records not appearing in annual pages
- Verify entries exist in `data/class_records_history.json`
- Check that `season` field matches the page (e.g., "2025-26")

### Website shows old data after push
- Wait 2-3 minutes for GitHub Pages rebuild
- Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
- Clear browser cache

### Python script errors
```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Key Files Reference

### Source of Truth
| File | Contains |
|------|----------|
| `records/records-boys.md` | Boys individual records |
| `records/records-girls.md` | Girls individual records |
| `records/relay-records-boys.md` | Boys relay records |
| `records/relay-records-girls.md` | Girls relay records |
| `data/class_records_history.json` | Historical class records with previous holders |

### Generated Output
| File | Generated By |
|------|--------------|
| `docs/records/overall.html` | generate_website.py |
| `docs/records/boys-bygrade.html` | generate_website.py |
| `docs/records/boys-relays.html` | rebuild_relay_pages.py |
| `docs/top10/*.html` | generate_website.py |
| `docs/annual/*.html` | generate_annual_pages.py |

### Configuration
| File | Purpose |
|------|---------|
| `docs/css/style.css` | All website styling |
| `docs/index.html` | Splash page (manual) |
| `requirements.txt` | Python dependencies |

---

## Season Reference

### Available Seasons
Data exists for: 2007-08 through 2025-26

### Incomplete Data Years
Only state meet results: 2007-08, 2008-09, 2009-10, 2010-11, 2011-12

### Current Season
2025-26 (update `SEASONS` list in scripts when adding new season)

---

## Deployment

The site auto-deploys via GitHub Pages when pushed to `main` branch.

```bash
git add -A
git commit -m "Description of changes"
git push origin main
```

**CDN Cache:** Changes may take 1-3 minutes to appear. Hard refresh to see updates immediately.

---

**Last Updated:** December 12, 2025
**Maintainer:** aaryno@gmail.com
