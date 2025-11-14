# Tanque Verde High School - Setup Guide

**Directory:** `~/swimming/tanque-verde`  
**Data Source:** MaxPreps  
**Purpose:** Test MaxPreps integration and season range features

---

## 🚀 Quick Setup

### 1. Initialize Directory

```bash
cd ~/swimming/tanque-verde

# Initialize with swim-data-tool
uv run swim-data-tool init "Tanque Verde High School"
```

**During initialization, you'll be prompted for:**
1. **Data Source:** Select `2. MaxPreps (high school)`
2. **Team name:** Tanque Verde High School
3. **Team abbreviation:** TVHS
4. **School slug:** tanque-verde-hawks (from MaxPreps URL)
5. **State:** az
6. **City:** tucson
7. **Default season:** 24-25

**Finding your school slug:**
- Go to https://www.maxpreps.com
- Search for your school
- Look at the URL: `maxpreps.com/az/tucson/tanque-verde-hawks/swimming/`
- The slug is: `tanque-verde-hawks`

**What gets configured:**
- `.env` file with MaxPreps configuration
- Directory structure for data storage
- README.md and claude.md documentation

No USA Swimming team code needed for MaxPreps teams! ✅

### 2. Test Roster Collection

```bash
# Test single season
uv run swim-data-tool roster --source=maxpreps

# Test season range (3 seasons)
uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25

# Test explicit season (future)
uv run swim-data-tool roster --source=maxpreps --seasons=25-26
```

---

## 📋 Testing Scripts

### Automated Test Suite
```bash
./test_season_ranges.sh
```

**Tests:**
- ✅ Single explicit season (25-26)
- ✅ Season range (22-23 to 24-25)
- ✅ Error handling (missing parameters)

### Manual Testing
See `SEASON_RANGE_TESTS.md` for detailed test cases.

---

## 📂 Expected Directory Structure

After setup, you'll have:

```
~/swimming/tanque-verde/
├── .env                      # MaxPreps configuration
├── SETUP.md                  # This file
├── SEASON_RANGE_TESTS.md     # Testing guide
├── test_season_ranges.sh     # Automated tests
└── data/
    ├── lookups/
    │   └── roster-maxpreps.csv  # Roster data
    ├── raw/
    │   └── swimmers/            # Individual swimmer data
    └── processed/
        └── classified/          # Processed swim times
```

---

## 🧪 Full Workflow

### 1. Collect Roster
```bash
uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25
```

### 2. Import Swimmer Data
```bash
uv run swim-data-tool import swimmers --source=maxpreps
```

### 3. Generate Records
```bash
# Coming soon: Grade-based records (Freshman/Sophomore/Junior/Senior)
uv run swim-data-tool generate records
```

---

## 🔍 Verify Setup

```bash
# Check .env configuration
cat .env

# List available data sources
uv run python3 << 'EOF'
from swim_data_tool.sources.factory import list_sources
print("Available sources:", list_sources())
EOF

# Test MaxPreps connection
uv run swim-data-tool roster --source=maxpreps --seasons=24-25
```

---

## 📊 MaxPreps URLs

**School Home:** https://www.maxpreps.com/az/tucson/tanque-verde-hawks/

**Roster (Boys 24-25):**  
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/24-25/roster/

**Individual Athlete Example:**  
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/athletes/wade-olsson/swimming/stats/?careerid=10aavdb9t0tee

---

## ✅ Success Indicators

After successful setup and roster collection, you should see:

✅ `.env` file created with MaxPreps configuration  
✅ `data/lookups/roster-maxpreps.csv` created  
✅ Roster contains athlete names, careerids, grades  
✅ Grade levels (Fr., So., Jr., Sr.) extracted correctly  
✅ No duplicate athletes (deduplicated by careerid)  

---

## 🚀 Next Steps

1. **Test Season Range Feature** - Run `./test_season_ranges.sh`
2. **Import Swimmer Data** - Scrape individual athlete stats
3. **Generate Records** - Create all-time and grade-based records
4. **Compare with USA Swimming** - Test backwards compatibility

See `SEASON_RANGE_TESTS.md` for detailed testing instructions.

