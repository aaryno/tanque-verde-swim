# Tanque Verde Swimming Website - AI Assistant Context

## Repository Overview

This is the **self-contained** repository for the Tanque Verde High School Swimming records website.

**Live Site:** https://tanqueverdeswim.org  
**GitHub:** https://github.com/aaryno/tanque-verde-swim

## Purpose

Track and publish swim team records and statistics:
- Team records (SCY) by grade and overall
- All-time and seasonal Top 10 lists
- Annual season summaries with records broken
- Relay records with split times

## Quick Start

```bash
cd ~/workspaces/swimming/tanque-verde-swim

# Regenerate entire website
python3 generate_website.py

# Commit and deploy
git add -A && git commit -m "Update records" && git push
```

## Directory Structure

```
tanque-verde-swim/
├── docs/                      # Generated HTML (GitHub Pages)
│   ├── index.html             # Splash page (manually maintained)
│   ├── css/style.css          # Main stylesheet
│   ├── images/                # Logos and images
│   ├── records/               # Overall, relays, by-grade pages
│   ├── top10/                 # All-time and seasonal top 10
│   └── annual/                # Annual summary pages
│
├── records/                   # Source markdown files
│   ├── records-boys.md        # Boys records (SOURCE OF TRUTH)
│   ├── records-girls.md       # Girls records (SOURCE OF TRUTH)
│   ├── annual-summary-*.md    # Annual data
│   └── top10-*.md             # Top 10 lists
│
├── data/                      # JSON data files
│   ├── class_records_history.json    # Class records with history
│   ├── historical_splits/            # Relay splits by season
│   └── all_relays.json               # Raw relay data
│
├── WORKFLOW.md                # Detailed maintenance guide
└── [Python scripts]           # Generation scripts
```

## Active Scripts

| Script | Purpose |
|--------|---------|
| `generate_website.py` | **Main entry point** - runs all generators |
| `generate_annual_pages.py` | Creates annual summary HTML pages |
| `rebuild_relay_pages.py` | Creates relay pages with splits |
| `enrich_previous_record_locations.py` | Adds meet info to previous records |

## Common Tasks

### Add a New Record
1. Edit `records/records-boys.md` or `records/records-girls.md`
2. Run `python3 generate_website.py`
3. Commit and push

### Add Class Records for New Season
1. Create script like `add_2025_26_class_records.py`
2. Run it to update `data/class_records_history.json`
3. Run `python3 enrich_previous_record_locations.py`
4. Run `python3 generate_website.py`

### Update Relay Splits
1. Add/edit `data/historical_splits/splits_YYYY-YY.json`
2. Run `python3 rebuild_relay_pages.py`

## Data Sources

- **AZPreps365** - Arizona high school results
- **MaxPreps** - National high school database
- **Manual Entry** - Historical records, corrections

## Deployment

Auto-deploys via GitHub Pages when pushed to `main` branch.

```bash
git add -A
git commit -m "Description"
git push origin main
```

## Key Files

| File | Description |
|------|-------------|
| `records/records-boys.md` | Boys team records - SOURCE OF TRUTH |
| `records/records-girls.md` | Girls team records - SOURCE OF TRUTH |
| `data/class_records_history.json` | Class records with previous holders |
| `docs/index.html` | Splash page (manually maintained) |
| `docs/css/style.css` | All website styling |

## Notes

- The `docs/` folder is deployed directly via GitHub Pages
- The splash page (`docs/index.html`) is manually maintained
- All other HTML pages are generated from markdown/JSON
- CDN may cache pages - hard refresh to see updates

---

**Last Updated:** December 12, 2025
