# 📑 Harvest System - Complete File Index

**Created:** October 26, 2024  
**Location:** `/Users/aaryn/swimming/tanque-verde/`

---

## 🎯 Start Here

**Quick Start:** Open `HARVEST_QUICK_START.md`  
**Full Documentation:** Open `README_HARVEST.md`  
**Setup Summary:** Open `HARVEST_SETUP_COMPLETE.md`

---

## 📁 All Harvest Files

### 🚀 Executable Scripts

| File | Purpose | Usage |
|------|---------|-------|
| `harvest_all.sh` | **Run everything** | `./harvest_all.sh` |
| `quick_test_harvest.sh` | Test setup | `./quick_test_harvest.sh` |

### 🐍 Python Scripts

| File | Purpose | When to Use |
|------|---------|-------------|
| `harvest_azpreps365.py` | Scrape D3 leaderboards | Individual component or debugging |
| `harvest_relays.py` | Collect new relay results (Oct 20+) | Individual component or debugging |
| `extract_leaderboard_from_webpage.py` | Manual extraction from web data | Fallback if scraping fails |
| `parse_azpreps365_html.py` | Parse saved HTML files | Debug scraping issues |
| `test_harvest_setup.py` | Verify system setup | Check dependencies |

### 📖 Documentation

| File | Content | Audience |
|------|---------|----------|
| `HARVEST_QUICK_START.md` | Quick start guide | **Everyone - READ THIS FIRST** |
| `HARVEST_SETUP_COMPLETE.md` | Detailed setup summary | Reference when needed |
| `README_HARVEST.md` | Complete technical docs | Deep dive into system |
| `HARVEST_FILES_INDEX.md` | This file | Quick file reference |

---

## 🗂️ Output Structure

After running `./harvest_all.sh`, you'll get:

```
data/raw/azpreps365_harvest/
└── 2024-10-26/                                    # Today's harvest
    ├── azpreps365_d3_boys_leaderboard_2024-10-26.csv
    ├── azpreps365_d3_girls_leaderboard_2024-10-26.csv
    ├── new_relays_since_20241020_2024-10-26.csv
    └── raw_html_boys_d3_*.html                    # Debug files
```

---

## 🎮 Usage Patterns

### Pattern 1: Complete Harvest (Most Common)
```bash
./harvest_all.sh
```
**Result:** Everything done in one command

### Pattern 2: Quick Test
```bash
./quick_test_harvest.sh
```
**Result:** Verify system is ready

### Pattern 3: Individual Components
```bash
source ../swim-data-tool/.venv/bin/activate
python3 harvest_azpreps365.py    # Just leaderboards
python3 harvest_relays.py        # Just relays
```
**Result:** Run specific parts

### Pattern 4: Manual Fallback
```bash
source ../swim-data-tool/.venv/bin/activate
python3 extract_leaderboard_from_webpage.py
```
**Result:** Use pre-extracted web search data

### Pattern 5: Debug Scraping
```bash
source ../swim-data-tool/.venv/bin/activate
python3 harvest_azpreps365.py    # Downloads raw HTML
python3 parse_azpreps365_html.py # Analyzes HTML structure
```
**Result:** Troubleshoot parsing issues

---

## 🔄 Weekly Workflow

```bash
# Week 1
./harvest_all.sh

# Week 2
./harvest_all.sh

# Week 3
./harvest_all.sh

# Each run creates: data/raw/azpreps365_harvest/YYYY-MM-DD/
```

---

## 📊 Data Files Generated

### Leaderboard CSV Format
```csv
event,rank,athlete,school,time,division,gender,harvest_date
200 Medley IM,1,Wade Olsson,Tanque Verde,02:00.20,d3,boys,2024-10-26
```

**Fields:**
- `event` - Event name (e.g., "200 Medley IM", "100 Fly")
- `rank` - Position in division (1, 2, 3, ...)
- `athlete` - Athlete name or "Team" for relays
- `school` - School name
- `time` - Swim time (MM:SS.SS format)
- `division` - Division code (d3)
- `gender` - boys or girls
- `harvest_date` - Date data was collected

### Relay CSV Format
```csv
Event,SwimTime,SwimDate,MeetName,Team,place,season,source,Gender
200 MEDLEY RELAY SCY,01:42.50,9/14/2024,"Multi Teams @ CDO",Tanque Verde,2nd,24-25,maxpreps,M
```

**Fields:**
- `Event` - Relay event name
- `SwimTime` - Time (MM:SS.SS)
- `SwimDate` - Date swam (M/D/YYYY)
- `MeetName` - Meet name and location
- `Team` - School name
- `place` - Placement (1st, 2nd, 3rd, etc.)
- `season` - Season (24-25)
- `source` - Data source (maxpreps)
- `Gender` - M or F

---

## 🔧 Troubleshooting Quick Reference

### Scripts won't execute
```bash
chmod +x harvest_all.sh quick_test_harvest.sh
```

### Import errors
```bash
source ../swim-data-tool/.venv/bin/activate
```

### No data extracted
1. Check `data/raw/azpreps365_harvest/YYYY-MM-DD/` for raw HTML
2. Run `python3 parse_azpreps365_html.py` to inspect
3. Use manual extraction as fallback

### Playwright issues
```bash
source ../swim-data-tool/.venv/bin/activate
pip install playwright
playwright install chromium
```

---

## 📈 Integration Points

### With Existing Systems:
- **Relay Simulations:** Uses separate directory (safe to run concurrently)
- **MaxPreps Data:** Leverages existing `MaxPrepsSource` plugin
- **swim-data-tool:** Uses virtual environment and libraries

### Future Integration:
- Merge multiple harvest dates
- Compare with individual athlete data
- Track record progressions
- Generate change reports

---

## ✅ System Benefits

1. **Timestamped** - Each harvest preserved with date
2. **Non-destructive** - Never overwrites previous data
3. **Reusable** - Run weekly or after meets
4. **Modular** - Use individual components
5. **Debuggable** - Saves raw HTML for inspection
6. **Documented** - Complete docs for all use cases
7. **Tested** - Verification scripts included

---

## 📞 Quick Links

- **Quick Start:** `HARVEST_QUICK_START.md`
- **Setup Details:** `HARVEST_SETUP_COMPLETE.md`
- **Technical Docs:** `README_HARVEST.md`
- **swim-data-tool:** `../swim-data-tool/claude.md`
- **Tanque Verde:** `claude.md`

---

## 🎯 Summary

**10 files created** to give you a complete, production-ready harvest system:

✅ 2 executable scripts (harvest_all.sh, quick_test_harvest.sh)  
✅ 5 Python scripts (scraping, extraction, parsing, testing)  
✅ 4 documentation files (quick start, setup, technical, index)

**One command to run:** `./harvest_all.sh`

**Output location:** `data/raw/azpreps365_harvest/YYYY-MM-DD/`

---

**Happy Harvesting! 🏊‍♂️🏊‍♀️**

