# Complete Division Harvest Guide

**Date:** October 26, 2025  
**Purpose:** Harvest top N swimmers from leaderboards + extract all schools for relay harvesting

---

## 🎯 What This Does

The `harvest_division_complete.py` script provides a complete division data harvest:

### Phase 1: Leaderboard Harvest ✅ READY
1. **Harvest top N swimmers** from D3 boys/girls leaderboards (default: 50)
2. **Extract all unique schools** from the leaderboard data
3. **Save school list** for further processing

### Phase 2: Relay Harvest ⚠️ IN PROGRESS
4. **Visit each school's MaxPreps page** and harvest relay results
5. **Filter relays by date** (configurable cutoff)
6. **Combine all relay data** into comprehensive dataset

---

## 🚀 Quick Start

### Basic Usage (Top 50)

```bash
cd /Users/aaryn/swimming/tanque-verde

# Harvest top 50 from D3 leaderboards
python3 harvest_division_complete.py

# Output: data/raw/division_harvest/2024-10-26/
#   - d3_boys_leaderboard_top50_2024-10-26.csv
#   - d3_girls_leaderboard_top50_2024-10-26.csv
#   - d3_schools_2024-10-26.csv
```

### Custom Top N

```bash
# Top 100 swimmers per event
python3 harvest_division_complete.py --top-n=100

# Top 25 swimmers per event
python3 harvest_division_complete.py --top-n=25
```

### Custom Output Directory

```bash
# Harvest to specific directory
python3 harvest_division_complete.py --output-dir=data/raw/d3_top100 --top-n=100

# For lineup optimizer
python3 harvest_division_complete.py --output-dir=../swim-data-tool/data/reports/azpreps/d3-complete
```

---

## 📊 What You Get

### 1. Boys Leaderboard CSV

**File:** `d3_boys_leaderboard_top50_2024-10-26.csv`

```csv
event,athlete,school,time,rank,division,gender,harvest_date
50 Free,John Smith,School A,21.78,1,d3,boys,2024-10-26
50 Free,Mike Johnson,School B,21.95,2,d3,boys,2024-10-26
100 Free,John Smith,School A,47.15,1,d3,boys,2024-10-26
...
```

**Events included:**
- Individual: 50/100/200/500 Free, 100 Back/Breast/Fly, 200 IM
- Relays: 200 Medley Relay, 200 Free Relay, 400 Free Relay

### 2. Girls Leaderboard CSV

**File:** `d3_girls_leaderboard_top50_2024-10-26.csv`

Same format as boys, with `gender=girls`

### 3. Schools List CSV

**File:** `d3_schools_2024-10-26.csv`

```csv
school
Canyon del Oro
Catalina Foothills
Cienega
Flowing Wells
Ironwood Ridge
Marana
Sahuaro
Salpointe Catholic
Tanque Verde
...
```

**This list is used for:**
- Phase 2 relay harvesting
- Division analysis
- Competitive intelligence
- Lineup optimization

---

## 🔧 Command-Line Options

### Full Syntax

```bash
python3 harvest_division_complete.py [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir=PATH` | Output directory | `data/raw/division_harvest/YYYY-MM-DD/` |
| `--division=d1\|d2\|d3\|d4` | Division to harvest | `d3` |
| `--top-n=N` | Number of top swimmers per event | `50` |
| `--cutoff-date=YYYY-MM-DD` | Relay cutoff date | `2024-10-20` |
| `--no-timestamp` | Don't append date to output dir | (adds timestamp) |
| `--leaderboard-only` | Skip relay harvesting | (harvests both) |

### Examples

```bash
# Default (top 50 from D3)
python3 harvest_division_complete.py

# Top 100 from D3
python3 harvest_division_complete.py --top-n=100

# Different division
python3 harvest_division_complete.py --division=d2 --top-n=50

# Custom output directory
python3 harvest_division_complete.py --output-dir=data/raw/d3_complete

# Only leaderboards (skip relays)
python3 harvest_division_complete.py --leaderboard-only

# Different relay cutoff date
python3 harvest_division_complete.py --cutoff-date=2024-09-01

# Everything custom
python3 harvest_division_complete.py \
  --division=d3 \
  --top-n=100 \
  --output-dir=data/raw/d3_top100 \
  --cutoff-date=2024-09-01
```

---

## 📁 Output Structure

### Default Output

```
data/raw/division_harvest/
└── 2024-10-26/
    ├── d3_boys_leaderboard_top50_2024-10-26.csv
    ├── d3_girls_leaderboard_top50_2024-10-26.csv
    ├── d3_schools_2024-10-26.csv
    └── (relay files - pending Phase 2 implementation)
```

### Custom Output

```bash
python3 harvest_division_complete.py --output-dir=data/raw/d3_top100 --top-n=100
```

```
data/raw/d3_top100/
└── 2024-10-26/
    ├── d3_boys_leaderboard_top100_2024-10-26.csv
    ├── d3_girls_leaderboard_top100_2024-10-26.csv
    └── d3_schools_2024-10-26.csv
```

---

## 🎯 Use Cases

### Use Case 1: Lineup Optimizer Input

**Goal:** Get complete division data for lineup optimization

```bash
# Harvest top 50 (enough for competitive analysis)
python3 harvest_division_complete.py \
  --output-dir=../swim-data-tool/data/reports/azpreps/d3-complete \
  --top-n=50

# Then use in lineup optimizer
cd ../swim-data-tool
swim-data-tool optimize lineup \
  --roster=examples/roster_example.csv \
  --leaderboard=data/reports/azpreps/d3-complete/2024-10-26/d3_boys_leaderboard_top50_2024-10-26.csv \
  --team-name="Tanque Verde"
```

### Use Case 2: Division Analysis

**Goal:** Analyze entire division's performance

```bash
# Harvest top 100 for comprehensive analysis
python3 harvest_division_complete.py \
  --output-dir=data/raw/d3_analysis \
  --top-n=100

# Analyze:
# - Which schools dominate which events?
# - What are the cutoff times for top 8/16?
# - How does our team compare?
```

### Use Case 3: Competitive Intelligence

**Goal:** Track all schools in division

```bash
# Harvest leaderboards
python3 harvest_division_complete.py --leaderboard-only

# Get school list
cat data/raw/division_harvest/2024-10-26/d3_schools_2024-10-26.csv

# Use for:
# - Scouting reports
# - Meet preparation
# - Strategy planning
```

### Use Case 4: Historical Tracking

**Goal:** Track division performance over time

```bash
# Week 1
python3 harvest_division_complete.py --output-dir=data/raw/d3_tracking/week_1

# Week 2
python3 harvest_division_complete.py --output-dir=data/raw/d3_tracking/week_2

# Week 3
python3 harvest_division_complete.py --output-dir=data/raw/d3_tracking/week_3

# Compare changes over time
```

---

## ⚠️ Current Status

### ✅ Phase 1: COMPLETE

- [x] Harvest top N from leaderboards
- [x] Extract unique schools
- [x] Save leaderboard data
- [x] Save school list
- [x] Command-line options
- [x] Help documentation

### ⚠️ Phase 2: IN PROGRESS

The relay harvesting portion is **partially implemented**:

**What's done:**
- School name to MaxPreps slug conversion
- MaxPreps URL discovery logic
- Framework for relay scraping

**What's needed:**
- Full implementation of `harvest_school_relays()`
- Adapt existing MaxPreps relay scraping code
- Handle multiple schools (not just Tanque Verde)
- Rate limiting and error handling
- Progress tracking

**Why it's not complete:**
The existing `MaxPrepsSource.get_team_relays()` is hardcoded for a single team from `.env`. To harvest all division schools, we need to:

1. **Generalize the relay scraper** to work with any school slug
2. **Find MaxPreps URLs** for each school (requires search/guessing)
3. **Handle missing data** gracefully (not all schools have MaxPreps pages)
4. **Implement rate limiting** to avoid overwhelming MaxPreps servers

---

## 🔨 Completing Phase 2

### Option 1: Manual School Mapping

Create a mapping file with known MaxPreps slugs:

**`d3_school_slugs.csv`:**
```csv
school,maxpreps_slug,state,city
Tanque Verde,tanque-verde-hawks,az,tucson
Canyon del Oro,canyon-del-oro-dorados,az,tucson
Catalina Foothills,catalina-foothills-falcons,az,tucson
...
```

Then use this mapping to harvest relays.

### Option 2: Automated Discovery

Implement MaxPreps search to automatically find school URLs:
1. Search MaxPreps for school name
2. Parse search results
3. Verify correct school
4. Extract slug from URL

### Option 3: Use Existing Tanque Verde Script

For now, use the existing `harvest_relays_v2.py` which works for Tanque Verde:

```bash
# Harvest leaderboards for all schools
python3 harvest_division_complete.py --leaderboard-only

# Harvest Tanque Verde relays separately
python3 harvest_relays_v2.py --output-dir=data/raw/division_harvest/2024-10-26
```

---

## 💡 Recommended Workflow

### For Immediate Use

```bash
# Step 1: Harvest leaderboards (works now)
python3 harvest_division_complete.py \
  --output-dir=data/raw/d3_complete \
  --top-n=50 \
  --leaderboard-only

# Step 2: Harvest Tanque Verde relays separately
python3 harvest_relays_v2.py \
  --output-dir=data/raw/d3_complete/2024-10-26 \
  --no-timestamp

# Step 3: Use in lineup optimizer
cd ../swim-data-tool
swim-data-tool optimize lineup \
  --roster=examples/roster_example.csv \
  --leaderboard=../tanque-verde/data/raw/d3_complete/2024-10-26/d3_boys_leaderboard_top50_2024-10-26.csv \
  --team-name="Tanque Verde"
```

### For Future (When Phase 2 Complete)

```bash
# One command does everything
python3 harvest_division_complete.py \
  --output-dir=data/raw/d3_complete \
  --top-n=50

# Result: Leaderboards + all school relays in one harvest
```

---

## 📊 Data Quality

### Leaderboard Data Quality: ✅ Excellent

- **Source:** AzPreps365 official leaderboards
- **Accuracy:** High (official state data)
- **Completeness:** Top N per event (configurable)
- **Freshness:** Real-time (scraped from live site)

### School List Quality: ✅ Excellent

- **Extracted from:** Leaderboard data
- **Accuracy:** High (only schools with results)
- **Completeness:** All schools with top N results
- **Use:** Ready for relay harvesting

### Relay Data Quality: ⚠️ Pending

- **Status:** Implementation in progress
- **Challenge:** Finding MaxPreps URLs for all schools
- **Workaround:** Use existing Tanque Verde relay harvest

---

## 🐛 Troubleshooting

### Problem: "Playwright not installed"

**Solution:**
```bash
source ../swim-data-tool/.venv/bin/activate
pip install playwright
playwright install chromium
```

### Problem: "No data scraped"

**Causes:**
- AzPreps365 site structure changed
- JavaScript not loading properly
- Network issues

**Solution:**
- Check internet connection
- Try again (may be temporary)
- Check AzPreps365 site manually

### Problem: "School list is empty"

**Cause:** Leaderboard harvest failed

**Solution:**
- Check that leaderboard CSVs were created
- Verify they contain data
- Re-run harvest

---

## 📚 Next Steps

### Immediate (Ready Now)

1. **Harvest leaderboards:**
   ```bash
   python3 harvest_division_complete.py --leaderboard-only
   ```

2. **Use school list for analysis:**
   ```bash
   cat data/raw/division_harvest/2024-10-26/d3_schools_2024-10-26.csv
   ```

3. **Convert for lineup optimizer:**
   - Create converter script (pivot leaderboard to optimizer format)
   - See `HARVEST_V2_GUIDE.md` for details

### Future Enhancements

1. **Complete Phase 2 relay harvesting**
   - Implement school URL discovery
   - Generalize relay scraper
   - Add progress tracking

2. **Create school mapping database**
   - Manual mapping of D3 schools to MaxPreps slugs
   - Automated discovery and verification
   - Maintain as reference data

3. **Add data quality checks**
   - Verify leaderboard completeness
   - Check for duplicate schools
   - Validate time formats

4. **Create analysis tools**
   - Division statistics
   - School comparisons
   - Event strength analysis

---

## 🎉 Summary

**What works now:**
- ✅ Harvest top N from D3 leaderboards (boys/girls)
- ✅ Extract all unique schools
- ✅ Save comprehensive leaderboard data
- ✅ Configurable output directory
- ✅ Configurable top N

**What's in progress:**
- ⚠️ Automated relay harvesting for all schools
- ⚠️ MaxPreps URL discovery
- ⚠️ Multi-school relay scraping

**Workaround for now:**
- Use `harvest_division_complete.py --leaderboard-only` for leaderboards
- Use `harvest_relays_v2.py` for Tanque Verde relays specifically

**Ready to use immediately for:**
- Lineup optimization input
- Division analysis
- Competitive intelligence
- School identification

---

**Date:** October 26, 2025  
**Status:** Phase 1 Complete, Phase 2 In Progress  
**Version:** 1.0

