# Harvest v2 - Configurable Output Directory Guide

**Date:** October 26, 2025  
**Purpose:** Harvest leaderboard data to custom directories without overwriting existing analysis data

---

## 🎯 Overview

The v2 harvest scripts allow you to specify a custom output directory, so you can:
- Run multiple harvests without overwriting previous data
- Store harvest data in different locations (e.g., for lineup optimizer)
- Keep existing analysis data intact while collecting new data

---

## 🚀 Quick Start

### Option 1: Run Complete Harvest with Custom Directory

```bash
cd /Users/aaryn/swimming/tanque-verde

# Harvest to custom directory
./harvest_all_v2.sh data/raw/harvest_for_optimizer

# Or use environment variable
OUTPUT_DIR=data/raw/harvest_new ./harvest_all_v2.sh

# Harvest to swim-data-tool directory
./harvest_all_v2.sh ../swim-data-tool/data/reports/azpreps/d3-leaderboards
```

### Option 2: Run Individual Scripts

```bash
# Leaderboards only
python3 harvest_azpreps365_v2.py --output-dir=data/raw/harvest_new

# Relays only
python3 harvest_relays_v2.py --output-dir=data/raw/harvest_new

# With custom cutoff date
python3 harvest_relays_v2.py --output-dir=data/raw/harvest_new --cutoff-date=2024-10-01
```

---

## 📁 Output Directory Structure

### Default Behavior (No Arguments)

```bash
./harvest_all_v2.sh
```

**Output:**
```
data/raw/azpreps365_harvest/
└── 2024-10-26/                                    # Today's date
    ├── azpreps365_d3_boys_leaderboard_2024-10-26.csv
    ├── azpreps365_d3_girls_leaderboard_2024-10-26.csv
    └── new_relays_since_20241020_2024-10-26.csv
```

### Custom Directory (With Timestamp)

```bash
./harvest_all_v2.sh data/raw/harvest_for_optimizer
```

**Output:**
```
data/raw/harvest_for_optimizer/
└── 2024-10-26/                                    # Today's date appended
    ├── azpreps365_d3_boys_leaderboard_2024-10-26.csv
    ├── azpreps365_d3_girls_leaderboard_2024-10-26.csv
    └── new_relays_since_20241020_2024-10-26.csv
```

### Custom Directory (No Timestamp)

```bash
python3 harvest_azpreps365_v2.py --output-dir=data/raw/harvest_latest --no-timestamp
```

**Output:**
```
data/raw/harvest_latest/                           # No date subdirectory
├── azpreps365_d3_boys_leaderboard_2024-10-26.csv
├── azpreps365_d3_girls_leaderboard_2024-10-26.csv
└── new_relays_since_20241020_2024-10-26.csv
```

---

## 🎨 Common Use Cases

### Use Case 1: Preserve Existing Analysis Data

**Problem:** You're running Monte Carlo simulations on existing harvest data and don't want to overwrite it.

**Solution:**
```bash
# Harvest to new directory
./harvest_all_v2.sh data/raw/harvest_2024_10_26_new

# Your existing data remains untouched:
# data/raw/azpreps365_harvest/2024-10-20/  ← Still here!
```

### Use Case 2: Harvest for Lineup Optimizer

**Problem:** You want fresh leaderboard data for the lineup optimizer.

**Solution:**
```bash
# Harvest directly to swim-data-tool directory
cd /Users/aaryn/swimming/tanque-verde
./harvest_all_v2.sh ../swim-data-tool/data/reports/azpreps/d3-leaderboards

# Then use in optimizer:
cd ../swim-data-tool
swim-data-tool optimize lineup \
  --roster=examples/roster_example.csv \
  --leaderboard=data/reports/azpreps/d3-leaderboards/2024-10-26/azpreps365_d3_boys_leaderboard_2024-10-26.csv \
  --team-name="Tanque Verde"
```

### Use Case 3: Weekly Harvest Archive

**Problem:** You want to track leaderboard changes over time.

**Solution:**
```bash
# Week 1
./harvest_all_v2.sh data/raw/harvest_archive/week_1

# Week 2
./harvest_all_v2.sh data/raw/harvest_archive/week_2

# Week 3
./harvest_all_v2.sh data/raw/harvest_archive/week_3

# Compare changes over time
```

### Use Case 4: Different Relay Cutoff Dates

**Problem:** You want to analyze relays from different time periods.

**Solution:**
```bash
# All relays from September onwards
CUTOFF_DATE=2024-09-01 ./harvest_all_v2.sh data/raw/harvest_sept_onwards

# Only October relays
CUTOFF_DATE=2024-10-01 ./harvest_all_v2.sh data/raw/harvest_oct_onwards

# Only November relays
CUTOFF_DATE=2024-11-01 ./harvest_all_v2.sh data/raw/harvest_nov_onwards
```

---

## 📋 Command Reference

### harvest_all_v2.sh

**Syntax:**
```bash
./harvest_all_v2.sh [OUTPUT_DIR]
OUTPUT_DIR=path CUTOFF_DATE=YYYY-MM-DD ./harvest_all_v2.sh
```

**Arguments:**
- `OUTPUT_DIR` - Base output directory (optional, default: `data/raw/azpreps365_harvest`)
- `CUTOFF_DATE` - Relay cutoff date (optional, default: `2024-10-20`)

**Examples:**
```bash
# Default
./harvest_all_v2.sh

# Custom directory
./harvest_all_v2.sh data/raw/harvest_new

# Custom directory and cutoff date
OUTPUT_DIR=data/raw/harvest_sept CUTOFF_DATE=2024-09-01 ./harvest_all_v2.sh
```

### harvest_azpreps365_v2.py

**Syntax:**
```bash
python3 harvest_azpreps365_v2.py [OPTIONS]
```

**Options:**
- `--output-dir=PATH` - Output directory (default: `data/raw/azpreps365_harvest/YYYY-MM-DD/`)
- `--no-timestamp` - Don't append date to output directory

**Examples:**
```bash
# Default
python3 harvest_azpreps365_v2.py

# Custom directory with timestamp
python3 harvest_azpreps365_v2.py --output-dir=data/raw/harvest_new

# Custom directory without timestamp
python3 harvest_azpreps365_v2.py --output-dir=data/raw/harvest_latest --no-timestamp
```

### harvest_relays_v2.py

**Syntax:**
```bash
python3 harvest_relays_v2.py [OPTIONS]
```

**Options:**
- `--output-dir=PATH` - Output directory (default: `data/raw/azpreps365_harvest/YYYY-MM-DD/`)
- `--no-timestamp` - Don't append date to output directory
- `--cutoff-date=YYYY-MM-DD` - Only include relays from this date onwards (default: `2024-10-20`)

**Examples:**
```bash
# Default
python3 harvest_relays_v2.py

# Custom directory
python3 harvest_relays_v2.py --output-dir=data/raw/harvest_new

# Custom cutoff date
python3 harvest_relays_v2.py --cutoff-date=2024-09-01

# Both custom directory and cutoff date
python3 harvest_relays_v2.py --output-dir=data/raw/harvest_sept --cutoff-date=2024-09-01
```

---

## 🔄 Comparison: v1 vs v2

### Original Scripts (v1)

```bash
# Always outputs to: data/raw/azpreps365_harvest/YYYY-MM-DD/
./harvest_all.sh

# No way to change output directory
# No way to preserve existing data
```

### New Scripts (v2)

```bash
# Default behavior (same as v1)
./harvest_all_v2.sh

# Custom directory
./harvest_all_v2.sh data/raw/harvest_new

# Custom directory and cutoff date
OUTPUT_DIR=data/raw/harvest_sept CUTOFF_DATE=2024-09-01 ./harvest_all_v2.sh
```

**Key Differences:**
- ✅ Configurable output directory
- ✅ Configurable relay cutoff date
- ✅ Can preserve existing data
- ✅ Can harvest to multiple locations
- ✅ Backward compatible (default behavior same as v1)

---

## 💡 Best Practices

### 1. Use Descriptive Directory Names

```bash
# Good
./harvest_all_v2.sh data/raw/harvest_for_optimizer
./harvest_all_v2.sh data/raw/harvest_2024_10_26_pre_state

# Less clear
./harvest_all_v2.sh data/raw/h1
./harvest_all_v2.sh data/raw/temp
```

### 2. Keep Timestamps for Historical Data

```bash
# Let scripts append timestamp (default)
./harvest_all_v2.sh data/raw/harvest_archive/week_1

# Result: data/raw/harvest_archive/week_1/2024-10-26/
# You can run again next week without overwriting
```

### 3. Use --no-timestamp for "Latest" Data

```bash
# For data that should always be overwritten
python3 harvest_azpreps365_v2.py --output-dir=data/raw/harvest_latest --no-timestamp

# Result: data/raw/harvest_latest/ (no date subdirectory)
# Next run overwrites this data
```

### 4. Document Your Harvest Strategy

```bash
# Create a harvest log
echo "$(date): Harvested to data/raw/harvest_for_optimizer" >> harvest_log.txt
```

---

## 🐛 Troubleshooting

### Problem: "Directory already exists"

**Cause:** Timestamp subdirectory already exists from earlier today  
**Solution:** Either:
1. Use `--no-timestamp` to overwrite
2. Choose a different base directory
3. Delete the existing directory

### Problem: "No relay results found after cutoff date"

**Cause:** Cutoff date is too recent  
**Solution:** Use earlier cutoff date:
```bash
python3 harvest_relays_v2.py --cutoff-date=2024-09-01
```

### Problem: "Playwright not installed"

**Cause:** Playwright browser automation not installed  
**Solution:**
```bash
source ../swim-data-tool/.venv/bin/activate
pip install playwright
playwright install
```

---

## 📊 Output File Formats

### Leaderboard CSV Format

**File:** `azpreps365_d3_boys_leaderboard_YYYY-MM-DD.csv`

```csv
event,athlete,school,time,rank,division,gender,harvest_date
200 Medley IM,Wade Olsson,Tanque Verde,02:00.20,1,d3,boys,2024-10-26
100 Fly,Zachary Duerkop,Tanque Verde,53.01,1,d3,boys,2024-10-26
```

**Columns:**
- `event` - Event name (e.g., "100 Fly", "200 Free")
- `athlete` - Athlete name
- `school` - School name
- `time` - Time in MM:SS.ss format
- `rank` - Ranking (1, 2, 3, ...)
- `division` - Division code (d3)
- `gender` - Gender (boys, girls)
- `harvest_date` - Date harvested (YYYY-MM-DD)

### Relay CSV Format

**File:** `new_relays_since_YYYYMMDD_YYYY-MM-DD.csv`

```csv
Event,SwimTime,SwimDate,MeetName,Team,place,season,source,Gender
200 MEDLEY RELAY SCY,01:42.50,9/14/2024,"Multi Teams @ Canyon del Oro",Tanque Verde,2nd,24-25,maxpreps,M
```

**Columns:**
- `Event` - Relay event name
- `SwimTime` - Time in MM:SS.ss format
- `SwimDate` - Date swum (M/D/YYYY)
- `MeetName` - Meet name
- `Team` - Team name
- `place` - Placement (1st, 2nd, etc.)
- `season` - Season (YY-YY format)
- `source` - Data source (maxpreps)
- `Gender` - Gender (M, F)

---

## 🎯 Integration with Lineup Optimizer

### Step 1: Harvest Fresh Data

```bash
cd /Users/aaryn/swimming/tanque-verde
./harvest_all_v2.sh ../swim-data-tool/data/reports/azpreps/d3-leaderboards
```

### Step 2: Convert Leaderboard to Optimizer Format

The harvested leaderboard needs to be converted to the optimizer's expected format:

**Harvested format:**
```csv
event,athlete,school,time,rank,division,gender,harvest_date
50 Free,John Smith,School A,21.78,1,d3,boys,2024-10-26
50 Free,Jane Doe,School B,21.95,2,d3,boys,2024-10-26
```

**Optimizer format:**
```csv
Event,Time1,Time2,Time3,Time4,Time5,Time6,Time7,Time8,Time9,Time10
50 Free,21.78,21.95,22.27,22.35,22.42,22.76,22.96,23.00,23.17,23.25
```

**Conversion script needed** (TODO: Create this)

### Step 3: Run Optimizer

```bash
cd /Users/aaryn/swimming/swim-data-tool
swim-data-tool optimize lineup \
  --roster=examples/roster_example.csv \
  --leaderboard=data/reports/azpreps/d3-leaderboards/2024-10-26/d3_boys_leaderboard_optimizer_format.csv \
  --team-name="Tanque Verde"
```

---

## 📝 Next Steps

1. **Test the new scripts:**
   ```bash
   ./harvest_all_v2.sh data/raw/test_harvest
   ```

2. **Create leaderboard converter:**
   - Convert harvested CSV to optimizer format
   - Pivot from long to wide format
   - Group by event, take top N times

3. **Document workflow:**
   - Add to main README
   - Create examples
   - Update HARVEST_QUICK_START.md

4. **Integrate with lineup optimizer:**
   - Add harvest command to optimizer CLI
   - Auto-convert leaderboard format
   - Streamline end-to-end workflow

---

**Version:** 2.0  
**Date:** October 26, 2025  
**Status:** ✅ Ready to use  
**Backward Compatible:** Yes (default behavior same as v1)

