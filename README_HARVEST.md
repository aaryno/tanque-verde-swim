# AzPreps365 Harvest System

Streamlined data collection pipeline for AIA Division III swimming leaderboards and relay results.

## Overview

This system harvests:
1. **D3 Leaderboards** - Top performers in boys and girls Division III swimming
2. **New Relay Results** - Recent relay times from October 20, 2024 onwards

All harvests are timestamped and stored separately to avoid conflicts with ongoing simulations or analyses.

## Quick Start

### Run Complete Harvest

```bash
# Run everything at once
./harvest_all.sh
```

This will:
1. Scrape D3 boys and girls leaderboards from azpreps365.com
2. Fetch new relay results from MaxPreps (Oct 20+)
3. Save all data to `data/raw/azpreps365_harvest/YYYY-MM-DD/`

### Run Individual Components

```bash
# Just leaderboards
python3 harvest_azpreps365.py

# Just new relays
python3 harvest_relays.py

# Parse downloaded HTML files
python3 parse_azpreps365_html.py
```

## Output Structure

```
data/raw/azpreps365_harvest/
└── 2024-10-26/                                    # Harvest date
    ├── azpreps365_d3_boys_leaderboard_2024-10-26.csv
    ├── azpreps365_d3_girls_leaderboard_2024-10-26.csv
    ├── new_relays_since_20241020_2024-10-26.csv
    └── raw_html_boys_d3_*.html                    # Raw HTML for debugging
```

## File Formats

### Leaderboard CSV Format

```csv
event,athlete,school,time,rank,division,gender,harvest_date
200 Medley IM,Wade Olsson,Tanque Verde,02:00.20,1,d3,boys,2024-10-26
```

### Relay CSV Format

```csv
Event,SwimTime,SwimDate,MeetName,Team,place,season,source,Gender
200 MEDLEY RELAY SCY,01:42.50,9/14/2024,"Multi Teams @ Canyon del Oro",Tanque Verde,2nd,24-25,maxpreps,M
```

## Technical Details

### Leaderboard Scraping

The azpreps365.com leaderboard page uses:
- Dynamic JavaScript loading (requires Playwright)
- Dropdown menu for event selection
- "Load Leaderboard" button to trigger display
- MaxPreps data backend for athlete stats

Events covered:
- Individual: 50/100/200/500 Free, 100 Back/Breast/Fly, 200 IM
- Relays: 200 Medley, 200/400 Free Relay
- Diving: 1-meter dive

### Relay Collection

Relays are collected from MaxPreps using:
- The `MaxPrepsSource` plugin from swim-data-tool
- Date filtering to get only new results
- Deduplication by event, date, and time

## Reusability

This system is designed to be run multiple times throughout the season:

1. **Regular Intervals** - Run weekly or after major meets
2. **Timestamped Storage** - Each harvest gets its own dated directory
3. **Non-destructive** - Never overwrites previous harvests
4. **Merge-friendly** - CSVs can be easily combined and deduplicated

### Example: Weekly Harvest Workflow

```bash
# Week 1
./harvest_all.sh  # → data/raw/azpreps365_harvest/2024-10-26/

# Week 2
./harvest_all.sh  # → data/raw/azpreps365_harvest/2024-11-02/

# Combine all harvests
python3 merge_harvests.py  # TODO: Create this script
```

## Troubleshooting

### Playwright Not Installed

If you see "Playwright not installed":

```bash
pip install playwright
playwright install chromium
```

### No Data Found

If leaderboards return empty:
1. Check if azpreps365.com structure changed
2. Inspect raw HTML files in harvest directory
3. Run `parse_azpreps365_html.py` to see what data is present
4. Update parsing logic in `harvest_azpreps365.py`

### Date Filter Issues

If relay date filtering fails:
- Check date format in CSV (should be MM/DD/YYYY)
- Verify cutoff date is correct in `harvest_relays.py`
- Manually inspect `data/raw/team-relays.csv` for date format

## Integration with Records

After harvesting, integrate with existing records:

```bash
# 1. Review harvest data
cd data/raw/azpreps365_harvest/2024-10-26
head *.csv

# 2. Merge with existing data (manual or scripted)
# TODO: Create merge script

# 3. Regenerate records
cd ~/swimming/tanque-verde
python3 generate_hs_records.py

# 4. Update top 10 lists
python3 generate_top10.py
```

## Future Enhancements

- [ ] Automatic merge of multiple harvests
- [ ] Deduplication across harvest dates
- [ ] Change detection (new records broken)
- [ ] Email notifications of new season bests
- [ ] Integration with relay simulation system
- [ ] Historical trend analysis

## Notes

- The system respects server load (polite delays between requests)
- Raw HTML is saved for debugging and parser updates
- All dates are in local timezone (Arizona)
- Relay results include all Tanque Verde relay teams (A, B, C, etc.)

---

**Last Updated:** 2024-10-26  
**Compatible with:** swim-data-tool v0.12.2+

