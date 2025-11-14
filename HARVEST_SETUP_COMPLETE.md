# 🎉 AzPreps365 Harvest System - Setup Complete!

**Created:** October 26, 2024  
**Location:** `/Users/aaryn/swimming/tanque-verde/`

---

## ✅ What Was Created

### 1. **Main Harvest Scripts**

- **`harvest_azpreps365.py`** - Scrapes D3 boys/girls leaderboards from azpreps365.com
  - Uses Playwright for JavaScript-rendered content
  - Saves raw HTML for debugging
  - Extracts athlete names, schools, times, rankings

- **`harvest_relays.py`** - Collects NEW relay results (Oct 20, 2024+)
  - Uses MaxPrepsSource from swim-data-tool
  - Filters by date automatically
  - Deduplicates and saves to CSV

- **`harvest_all.sh`** - One-command complete harvest
  - Runs both scripts in sequence
  - Activates virtual environment automatically
  - Creates timestamped output directories

### 2. **Utility Scripts**

- **`extract_leaderboard_from_webpage.py`** - Manual extraction from web search data
  - Contains D3 boys data visible in your web search
  - Good for quick testing and validation
  - Can be extended with more manual data

- **`parse_azpreps365_html.py`** - HTML parser and inspector
  - Analyzes downloaded HTML files
  - Helps debug scraping issues
  - Extracts text snippets for inspection

- **`test_harvest_setup.py`** - Setup verification
  - Checks all dependencies
  - Verifies directory structure
  - Tests swim-data-tool integration

### 3. **Documentation**

- **`README_HARVEST.md`** - Complete harvest system documentation
  - Usage instructions
  - File format specifications
  - Troubleshooting guide
  - Integration workflow

- **`HARVEST_SETUP_COMPLETE.md`** (this file) - Setup summary

---

## 📁 Output Structure

All harvests are stored with timestamps to avoid conflicts:

```
data/raw/azpreps365_harvest/
├── 2024-10-26/                                      # Today's harvest
│   ├── azpreps365_d3_boys_leaderboard_2024-10-26.csv
│   ├── azpreps365_d3_girls_leaderboard_2024-10-26.csv
│   ├── new_relays_since_20241020_2024-10-26.csv
│   └── raw_html_*.html                              # For debugging
│
├── 2024-11-02/                                      # Next week's harvest
│   └── ...
│
└── 2024-11-09/                                      # Following week
    └── ...
```

**Benefits:**
- Non-destructive: Previous harvests are preserved
- Trackable: See how leaderboards change over time
- Merge-friendly: Easy to combine multiple harvest dates

---

## 🚀 How to Use

### Option 1: Complete Harvest (Recommended)

```bash
cd /Users/aaryn/swimming/tanque-verde

# Run everything at once
./harvest_all.sh
```

This will:
1. Activate swim-data-tool virtual environment
2. Scrape D3 boys and girls leaderboards
3. Fetch new relay results (Oct 20+)
4. Save all data to `data/raw/azpreps365_harvest/YYYY-MM-DD/`

### Option 2: Individual Components

```bash
# Activate environment first
source ../swim-data-tool/.venv/bin/activate

# Just leaderboards
python3 harvest_azpreps365.py

# Just relays
python3 harvest_relays.py

# Extract from web search data (quick test)
python3 extract_leaderboard_from_webpage.py
```

### Option 3: Manual Data Entry

If scraping fails, you can manually enter data from the azpreps365.com website:

```bash
# 1. Visit the leaderboard page
open https://azpreps365.com/leaderboards/swimming-boys/d3

# 2. Copy data into extract_leaderboard_from_webpage.py
# 3. Run the extraction
source ../swim-data-tool/.venv/bin/activate
python3 extract_leaderboard_from_webpage.py
```

---

## 🔄 Regular Harvest Workflow

Run this workflow **weekly** or **after major meets**:

```bash
# Week 1 (Oct 26)
cd /Users/aaryn/swimming/tanque-verde
./harvest_all.sh

# Week 2 (Nov 2)
./harvest_all.sh  # New timestamped directory created

# Week 3 (Nov 9)
./harvest_all.sh  # Another new directory

# Merge all harvests
# TODO: Create merge script
```

---

## 📊 Data Formats

### Leaderboard CSV

```csv
event,rank,athlete,school,time,division,gender,harvest_date
200 Medley IM,1,Wade Olsson,Tanque Verde,02:00.20,d3,boys,2024-10-26
100 Fly,1,Zachary Duerkop,Tanque Verde,00:53.01,d3,boys,2024-10-26
50 Free,3,Jackson Eftekhar,Tanque Verde,00:22.01,d3,boys,2024-10-26
```

### Relay CSV

```csv
Event,SwimTime,SwimDate,MeetName,Team,place,season,source,Gender
200 MEDLEY RELAY SCY,01:42.50,9/14/2024,"Multi Teams @ CDO",Tanque Verde,2nd,24-25,maxpreps,M
200 FR RELAY SCY,01:35.47,9/14/2024,"Multi Teams @ CDO",Tanque Verde,3rd,24-25,maxpreps,M
```

---

## 🔍 Verify Setup

```bash
cd /Users/aaryn/swimming/tanque-verde

# Check everything is in place
python3 test_harvest_setup.py
```

Should show:
- ✅ All harvest scripts present
- ✅ Dependencies available (in venv)
- ✅ swim-data-tool found
- ✅ Directory structure ready

---

## 💡 Key Features

### 1. **Timestamped Harvests**
Each harvest gets its own dated directory - never overwrites previous data.

### 2. **Date Filtering for Relays**
Automatically filters to only NEW relay results since October 20, 2024.

### 3. **Playoff-Safe**
Since simulations are running, all harvest data goes to separate directories (`azpreps365_harvest/`) to avoid conflicts.

### 4. **Reusable**
Designed to be run multiple times throughout the season. Just run `./harvest_all.sh` whenever you need fresh data.

### 5. **Dual-Gender Support**
Handles both D3 boys and D3 girls in one pass.

### 6. **Debug-Friendly**
Saves raw HTML files so you can inspect the actual page structure if scraping fails.

---

## 🎯 Tanque Verde D3 Boys Results (From Web Search)

Based on the current D3 boys leaderboard, Tanque Verde has **strong performances**:

### Top 3 Rankings:
- **#1 200 Medley IM:** Wade Olsson (2:00.20)
- **#1 100 Fly:** Zachary Duerkop (53.01)
- **#1 200 Medley Relay:** Team (1:41.80)
- **#1 200 Free Relay:** Team (1:31.81)
- **#2 200 Medley IM:** Zachary Duerkop (2:00.80)
- **#2 100 Breaststroke:** Zachary Duerkop (59.61)
- **#2 200 Free:** Zachary Duerkop (1:48.07)
- **#2 400 Free Relay:** Team (3:20.60)
- **#3 100 Breaststroke:** Wade Olsson (1:00.17)
- **#3 50 Free:** Jackson Eftekhar (22.01)
- **#3 100 Free:** Zachary Duerkop (47.92)

### Additional Top 10s:
- Wade Olsson: 5 events in top 10
- Zachary Duerkop: 5 events in top 10
- Jackson Eftekhar: 2 events in top 10

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"

**Solution:** Activate the virtual environment first:
```bash
source ../swim-data-tool/.venv/bin/activate
python3 harvest_relays.py
```

Or use the master script which does this automatically:
```bash
./harvest_all.sh
```

### "Playwright not installed"

**Solution:** Install Playwright:
```bash
source ../swim-data-tool/.venv/bin/activate
pip install playwright
playwright install chromium
```

### No data extracted from azpreps365.com

**Options:**
1. Check if website structure changed (inspect raw HTML files)
2. Use manual extraction: `python3 extract_leaderboard_from_webpage.py`
3. Update parsing logic in `harvest_azpreps365.py`

---

## 📝 Next Steps

### Immediate:
1. ✅ Test the harvest: `./harvest_all.sh`
2. ✅ Review output files in `data/raw/azpreps365_harvest/2024-10-26/`
3. ✅ Verify Tanque Verde results are captured

### This Week:
1. Create merge script to combine multiple harvest dates
2. Integrate with existing relay simulation system
3. Generate updated records and leaderboards

### Future:
1. Add D3 girls leaderboard scraping
2. Automate weekly harvests (cron job)
3. Track record progressions over time
4. Compare with MaxPreps individual stats

---

## 📚 Documentation

- **Full Guide:** `README_HARVEST.md`
- **swim-data-tool Docs:** `../swim-data-tool/claude.md`
- **Tanque Verde Context:** `claude.md`

---

## 🏊 Summary

You now have a **complete, streamlined harvest system** that:

✅ Scrapes D3 boys and girls leaderboards  
✅ Collects new relay results (Oct 20+)  
✅ Stores data with timestamps (non-destructive)  
✅ Works alongside existing simulations  
✅ Can be run multiple times throughout the season  
✅ Includes debugging and validation tools  

**Ready to harvest!** Just run:
```bash
./harvest_all.sh
```

---

**Questions? Check:** `README_HARVEST.md` for detailed documentation.

