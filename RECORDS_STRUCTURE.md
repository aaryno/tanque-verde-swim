# Tanque Verde Records Structure

**Last Updated:** October 9, 2025  
**Status:** ✅ Published

## File Organization

All records are in the top-level `data/records/` directory (high school is SCY-only):

```
data/records/
├── records-boys.md              # All-time records by grade
├── records-girls.md             # All-time records by grade
├── top10-boys-alltime.md        # All-time top 10 lists
├── top10-girls-alltime.md       # All-time top 10 lists
├── top10-boys-2024-25.md        # Current season top 10
├── top10-girls-2024-25.md       # Current season top 10
└── annual-summary-2024-25.md    # Season summary
```

## Records Files

### All-Time Records (records-*.md)
- **Format:** Best time per grade level (Freshman, Sophomore, Junior, Senior, Open)
- **Events:** 8 events (50/100/200/500 Free, 100 Back/Breast/Fly, 200 IM)
- **Open:** Best time across all grades (**bold** formatting)
- **Time Format:** Clean (56.59 not 00:56.59)

**Example:**
```markdown
### 100 Backstroke

| Grade | Time | Athlete | Date | Meet |
|-------|-----:|---------|------|------|
| Freshman | 1:00.60 | Kent Olsson | 9/27/2025 | Arena HS Classic |
| Sophomore | 56.59 | Nick Cusson | 10/23/2021 | Pecan Classic |
| **Open** | **52.68** | **Nick Cusson** | **11/4/2023** | **2023 D-3 AIA State** |
```

### All-Time Top 10 (top10-*-alltime.md)
- **Format:** Ranked 1-10 with best time per swimmer
- **Year Column:** FR, SO, JR, SR labels (not grades)
- **Coverage:** All historical data (2001-2025)
- **Sorted:** By time (fastest first)

**Example:**
```markdown
### 50 Freestyle

| Rank | Time | Athlete | Year | Date | Meet |
|-----:|-----:|---------|------|------|------|
| 1 | 21.99 | Nick Cusson | SO | 10/23/2021 | 2021 D-3 AIA State |
| 2 | 22.13 | Sam Stott | SR | 11/5/2022 | 2022 D-3 AIA Boys State |
```

### Current Season Top 10 (top10-*-2024-25.md)
- **Format:** Same as all-time, but filtered to current season
- **Date Range:** 2024-08-01 to 2025-08-01
- **Purpose:** Track season progress
- **Updates:** After each meet

### Annual Summary (annual-summary-2024-25.md)
- **Season Overview:** Total swims, swimmers, meets
- **Participation:** By gender and grade
- **Meet Schedule:** All meets with dates
- **Season Bests:** Fastest time per event
- **Active Roster:** All swimmers with swim counts

## Key Features

### 1. Year Labels (Not Grades)
- ✅ **FR** (Freshman/9th grade)
- ✅ **SO** (Sophomore/10th grade)
- ✅ **JR** (Junior/11th grade)
- ✅ **SR** (Senior/12th grade)

### 2. Time Formatting
- ✅ No leading zeros: `56.59` not `00:56.59`
- ✅ Minimal padding: `1:00.60` not `01:00.60`
- ✅ Right-aligned in tables

### 3. Data Quality
- ✅ Name consolidation via aliases
- ✅ Season-specific grade assignment
- ✅ AIA state meet integration (24 years)
- ✅ Duplicate swim removal

## Generation Scripts

```bash
# Generate all records
python3 generate_hs_records.py       # All-time records by grade
python3 generate_top10.py            # Both all-time and season top 10
python3 generate_annual_summary.py   # Season summary

# Publish to GitHub
swim-data-tool publish
```

## Update Workflow

### After Each Meet
```bash
cd /Users/aaryn/swimming/tanque-verde
swim-data-tool import swimmers --file=data/lookups/roster-maxpreps.csv
python3 generate_hs_records.py
python3 generate_top10.py
python3 generate_annual_summary.py
swim-data-tool publish
```

### At End of Season
1. Download new AIA state championship PDF
2. Update year in `parse_aia_state_meets.py`
3. Run full workflow including AIA processing
4. Check for new duplicate swimmers
5. Generate and publish all records

## Published URL

**Live Records:** https://github.com/aaryno/tanque-verde-swim

---

*Generated: October 9, 2025*
