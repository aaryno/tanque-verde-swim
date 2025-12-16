# Annual Page Generation Guide - Complete Workflow

> Reference: @claude.md for project context

## Purpose

This document describes the **complete workflow** for generating annual summary pages for a swim season. Use this guide at the end of each season (typically November after State Championships).

---

## Quick Reference

### Season Dates
- High school swim season runs **August - November**
- State Championships typically first weekend of November
- Season naming: `2025-26` means Aug 2025 - Aug 2026

### Required Files for Annual Page

| File | Purpose | How to Create |
|------|---------|---------------|
| `records/annual-summary-YYYY-YY.md` | Season overview, records, best times | Manual + Harvest |
| `records/top10-boys-YYYY-YY.md` | Boys top 10 per event with meets | Harvest + Generate |
| `records/top10-girls-YYYY-YY.md` | Girls top 10 per event with meets | Harvest + Generate |
| `data/class_records_history.json` | Class records with previous holders | Script |
| `data/historical_splits/splits_YY-YY.json` | Relay splits | Manual/Harvest |

---

## Current State (December 2025)

### ✅ What Works
- Class records extraction (`scripts/add_2025_26_class_records.py`)
- Annual page generation (`scripts/generate_annual_pages.py`)
- Website generation (`scripts/generate_website.py`)
- 2025-26 page exists with class records

### ❌ Known Issue: "Meet info not available"
The 2025-26 Season Best section shows "📍 Meet info not available" because:
- `records/top10-boys-2025-26.md` does NOT exist
- `records/top10-girls-2025-26.md` does NOT exist
- `generate_annual_pages.py` pulls meet names from top10 files (lines 175-176)

---

## Complete Workflow for New Season

### Phase 1: During the Season (Aug - Nov)

No action needed. Just track meets as they happen.

### Phase 2: After State Championships (Nov)

#### Step 1: Download State Championship PDF
```bash
# Download from AIA website
# Save as: ~/Downloads/d3-state-YYYY.pdf
# Example: ~/Downloads/d3-state-2026.pdf for 2026-27 season
```

#### Step 2: Harvest Meet Data

**Option A: Using swim-data-tool (Recommended if available)**
```bash
# From swim-data-tool directory with venv activated
cd ~/workspaces/swimming/swim-data-tool
source .venv/bin/activate

# Harvest roster
swim-data-tool roster --seasons=26-27

# Import swimmer data
swim-data-tool import swimmers --source=maxpreps
```

**Option B: Using standalone harvest scripts**
```bash
cd ~/workspaces/swimming/tanque-verde-swim

# Harvest from AZPreps365
python3 scripts/harvest/harvest_azpreps365_v3.py --season 26-27

# Parse state championship PDF
cp ~/Downloads/d3-state-2026.pdf data/raw/aia-state/
python3 scripts/harvest/parse_aia_state_meets.py
python3 scripts/harvest/merge_aia_state_data.py
```

#### Step 3: Generate Top 10 Files

**If swim-data-tool is available:**
```bash
python3 scripts/generate_all_season_top10.py
# This creates records/top10-boys-2026-27.md and records/top10-girls-2026-27.md
```

**If NOT available (manual workaround):**
Create minimal top10 files manually:
```bash
# Create records/top10-boys-2026-27.md with format:
# ## 50 Freestyle
# | Rank | Time | Athlete | Year | Date | Meet |
# | 1 | 23.45 | Name | SR | Nov 08, 2026 | State Championship |
# ... (at minimum, just #1 for each event with meet name)
```

#### Step 4: Create Annual Summary Markdown

Create `records/annual-summary-2026-27.md`:
```markdown
# 2026-27 Season Summary
## Tanque Verde High School Swimming

**Generated:** November 2026

---

## Season Overview

**Total Swims:** [count from harvested data]
**Swimmers:** [count]
**Meets Attended:** [count]

### Participation by Gender
- **Boys:** X swims
- **Girls:** X swims

### Participation by Grade
- **Freshman:** X swims
- **Sophomore:** X swims
- **Junior:** X swims
- **Senior:** X swims

---

## Meet Schedule

| Date | Meet |
|------|------|
| Sep XX, 2026 | Canyon del Oro Classic (Tucson, AZ) |
| Sep XX, 2026 | TYR HS Classic (Tucson, AZ) |
| Oct XX, 2026 | Pecan Classic (Sahuarita, AZ) |
| Oct XX, 2026 | Southern Arizona Qualifier (Tucson, AZ) |
| Nov XX, 2026 | 2026 D-3 AIA State Championship (Phoenix, AZ) |

---

## 🏆 Records Broken

**[Event] SCY**
- **NEW:** [time] - [Name] ([Grade])
- *Previous:* [time] - [Name]
- *Date:* [Date] at [Meet]

---

## Season Best Times

| Event | Boys Time | Boys Swimmer | Girls Time | Girls Swimmer |
|-------|----------:|--------------|-----------:|---------------|
| 50 Free | XX.XX | Name (GR) | XX.XX | Name (GR) |
| 100 Free | XX.XX | Name (GR) | XX.XX | Name (GR) |
| 200 Free | X:XX.XX | Name (GR) | X:XX.XX | Name (GR) |
| 500 Free | X:XX.XX | Name (GR) | X:XX.XX | Name (GR) |
| 100 Back | X:XX.XX | Name (GR) | X:XX.XX | Name (GR) |
| 100 Breast | X:XX.XX | Name (GR) | X:XX.XX | Name (GR) |
| 100 Fly | XX.XX | Name (GR) | XX.XX | Name (GR) |
| 200 IM | X:XX.XX | Name (GR) | X:XX.XX | Name (GR) |

---

*Generated: November 2026*
```

#### Step 5: Update Records Markdown (if new records)

Edit `records/records-boys.md` and/or `records/records-girls.md`:
- Add any new school records
- Update class records (FR/SO/JR/SR) with 2026 dates

#### Step 6: Extract Class Records

```bash
# Copy and modify the template script
cp scripts/add_2025_26_class_records.py scripts/add_2026_27_class_records.py

# Edit to change:
# - "2025-26" → "2026-27" 
# - "2025" → "2026" (in date filter)

python3 scripts/add_2026_27_class_records.py
```

#### Step 7: Enrich Previous Record Locations

```bash
python3 scripts/enrich_previous_record_locations.py
```

#### Step 8: Update Season Lists in Scripts

Edit `scripts/generate_annual_pages.py`:
```python
# Add "2026-27" to SEASONS list (around line 19)
SEASONS = [
    "2007-08", ..., "2025-26", "2026-27"  # Add new season
]
```

Edit `scripts/generate_website.py`:
- Update navigation dropdowns if needed (hardcoded season lists)

#### Step 9: Generate Website

```bash
python3 scripts/generate_website.py
```

#### Step 10: Add Relay Splits (Optional)

Create `data/historical_splits/splits_26-27.json`:
```json
{
  "boys": [
    {
      "type": "200 Medley Relay",
      "time": "1:42.35",
      "swimmers": ["Name1 - Sr.", "Name2 - Jr.", "Name3 - So.", "Name4 - Fr."],
      "splits": ["26.54", "29.87", "24.32", "21.62"],
      "meet": "State Championships",
      "date": "11/XX/2026"
    }
  ],
  "girls": []
}
```

Then regenerate relay pages:
```bash
python3 scripts/rebuild_relay_pages.py
```

#### Step 11: Commit and Deploy

```bash
git add -A
git commit -m "Add 2026-27 season: records, top10, annual summary"
git push origin main
```

---

## File Format Reference

### Top 10 File Format (`records/top10-{gender}-YYYY-YY.md`)

```markdown
# Boys Top 10 - 2026-27 Season
## Tanque Verde High School Swimming

**Generated:** November 2026

---

## 50 Freestyle

| Rank | Time | Athlete | Year | Date | Meet |
|-----:|-----:|---------|------|------|------|
| 1 | 23.45 | John Smith | SR | Nov 08, 2026 | 2026 D-3 State Championship |
| 2 | 24.12 | Mike Jones | JR | Oct 25, 2026 | Southern Arizona Qualifier |
...

---

## 100 Freestyle

| Rank | Time | Athlete | Year | Date | Meet |
...
```

**Critical:** The `| 1 |` row must have the Meet name in column 6 for the annual page to work.

### Class Records JSON Format (`data/class_records_history.json`)

```json
[
  {
    "season": "2026-27",
    "gender": "boys",
    "event": "100 Freestyle",
    "grade": "SR",
    "time": "48.50",
    "name": "John Smith",
    "date": "Nov 08, 2026",
    "meet": "2026 D-3 State Championship",
    "previous": {
      "time": "49.23",
      "name": "Previous Holder",
      "date": "Nov 10, 2024",
      "season": "2024-25",
      "meet": "State Championship"
    }
  }
]
```

---

## Script Dependencies

### Scripts That DON'T Need swim-data-tool

| Script | Purpose |
|--------|---------|
| `scripts/generate_website.py` | Generate all HTML pages |
| `scripts/generate_annual_pages.py` | Generate annual summary HTML |
| `scripts/rebuild_relay_pages.py` | Generate relay pages |
| `scripts/enrich_previous_record_locations.py` | Add meet info to previous records |
| `scripts/add_YYYY_YY_class_records.py` | Extract class records from markdown |

### Scripts That NEED swim-data-tool

| Script | Purpose | Workaround |
|--------|---------|------------|
| `scripts/generate_top10.py` | Generate single season top10 | Create manually |
| `scripts/generate_all_season_top10.py` | Generate all season top10s | Create manually |
| `scripts/harvest/*.py` | Harvest from MaxPreps/AZPreps | Manual data entry |

---

## Troubleshooting

### "Meet info not available" in Season Best

**Cause:** `records/top10-{gender}-YYYY-YY.md` doesn't exist

**Fix:** Create the top10 file with at least the #1 entry for each event with meet name

### Class Records Not Showing

**Cause:** Records not in `data/class_records_history.json`

**Fix:** Run `python3 scripts/add_YYYY_YY_class_records.py`

### Previous Record Location Missing

**Cause:** Previous record not in class_records_history.json

**Fix:** Run `python3 scripts/enrich_previous_record_locations.py`

### New Season Not in Dropdown

**Cause:** Season not in SEASONS list in scripts

**Fix:** Add season to:
- `scripts/generate_annual_pages.py` line ~19
- `scripts/generate_website.py` navigation (if hardcoded)

---

## Recommended Future Improvements

### 1. Remove swim-data-tool Dependency
Modify `scripts/generate_all_season_top10.py` to:
- Read from harvested CSV files directly
- Or parse from MaxPreps HTML exports
- Remove import of `swim_data_tool`

### 2. Extract Meet Info from Annual Summary
Modify `scripts/generate_annual_pages.py` to:
- Read meet names from `annual-summary-YYYY-YY.md` Season Best table
- Fall back to top10 only if not in summary

### 3. Create Season Setup Script
Create `scripts/setup_new_season.py` that:
- Creates all necessary files from templates
- Updates SEASONS lists automatically
- Prompts for state championship date

---

## Data Sources Reference

| Source | URL | Data Available |
|--------|-----|----------------|
| AZPreps365 | https://azpreps365.com | AZ high school meets, results |
| MaxPreps | https://maxpreps.com/az/tucson/tanque-verde-hawks | Rosters, individual stats |
| AIA | https://aiaonline.org | State championship PDFs |
| SwimCloud | https://swimcloud.com | Individual swimmer times |

---

## Checklist for New Season

```markdown
## 20XX-XX Season Setup Checklist

### Pre-Season (August)
- [ ] Verify roster is available on MaxPreps

### After State (November)
- [ ] Download state championship PDF
- [ ] Harvest meet data (MaxPreps/AZPreps)
- [ ] Create `records/top10-boys-20XX-XX.md`
- [ ] Create `records/top10-girls-20XX-XX.md`
- [ ] Create `records/annual-summary-20XX-XX.md`
- [ ] Update `records/records-boys.md` with new records
- [ ] Update `records/records-girls.md` with new records
- [ ] Run `add_20XX_XX_class_records.py`
- [ ] Run `enrich_previous_record_locations.py`
- [ ] Add season to SEASONS list in scripts
- [ ] Create `data/historical_splits/splits_XX-XX.json`
- [ ] Run `generate_website.py`
- [ ] Verify annual page shows correct meet info
- [ ] Commit and push

### Verification
- [ ] Check https://tanqueverdeswim.org/annual/20XX-XX.html
- [ ] Verify no "Meet info not available"
- [ ] Verify class records show with previous holders
- [ ] Verify relay splits (if added)
```

---

---

## Historical Records Reference

### Carly Wilson (2009-2011) - Record Holder

Carly Wilson holds multiple OPEN records from the 2009-10 and 2010-11 seasons:

| Event | Time | Date | Meet | Notes |
|-------|------|------|------|-------|
| 50 Free | **23.84** | Nov 06, 2010 | 2010 D-2 AIA State Championship | OPEN RECORD |
| 100 Free | **52.12** | Nov 06, 2010 | 2010 D-2 AIA State Championship | OPEN RECORD |
| 200 Free | **2:02.06** | Oct 18, 2011 | Pecan Classic | OPEN RECORD |
| 500 Free | **5:27.18** | Oct 21, 2010 | Pecan Classic | OPEN RECORD |
| 100 Fly | **1:00.33** | Sep 23, 2010 | CDO Classic | OPEN RECORD |
| 200 IM | **2:14.87** | Sep 23, 2010 | CDO Classic | OPEN RECORD |

**Important:** These records pre-date most digital tracking. When adding historical data, verify against the original source document.

### Boys 50 Free - Verified

Nick Cusson's 50 Free times (verified Dec 2025):
- **Individual Record:** 21.99 (Oct 23, 2021 - 2021 D-3 AIA State Championship)
- **Fastest Relay Split:** 21.64r (Nov 05, 2022 - 2022 D-3 AIA Boys State Championship)
- MaxPreps shows 21.76 relay leadoff (Sep 16, 2023 - CDO Classic)

**Note:** A "21.5" in some historical documents was a typo. No sub-21.64 time exists.

---

**Last Updated:** December 14, 2025  
**Season Covered:** 2025-26 (complete), 2026-27 (template ready)
**Records Fixed:** Carly Wilson historical records added Dec 2025


