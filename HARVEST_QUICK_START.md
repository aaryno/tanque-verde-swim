# 🚀 AzPreps365 Harvest - Quick Start Guide

**Date:** October 26, 2024  
**Purpose:** Harvest D3 boys/girls leaderboards + new relay results (Oct 20+)

---

## ⚡ TL;DR - Run This Now

```bash
cd /Users/aaryn/swimming/tanque-verde
./harvest_all.sh
```

Done! All data will be in: `data/raw/azpreps365_harvest/2024-10-26/`

---

## 📋 What You'll Get

After running the harvest, you'll have:

### 1. D3 Boys Leaderboard
- All D3 boys swimming leaders
- Events: 50/100/200/500 Free, 100 Back/Breast/Fly, 200 IM, relays
- Includes: athlete name, school, time, rank

### 2. D3 Girls Leaderboard  
- All D3 girls swimming leaders
- Same events as boys
- Includes: athlete name, school, time, rank

### 3. New Relay Results (Oct 20+)
- 200 Medley Relay
- 200 Free Relay
- 400 Free Relay
- Only swims from October 20, 2024 onwards

All stored in timestamped directory: `data/raw/azpreps365_harvest/2024-10-26/`

---

## 🎯 Quick Commands

### Test the Setup
```bash
./quick_test_harvest.sh
```

### Full Harvest (Recommended)
```bash
./harvest_all.sh
```

### Individual Components
```bash
source ../swim-data-tool/.venv/bin/activate

# D3 leaderboards only
python3 harvest_azpreps365.py

# New relays only  
python3 harvest_relays.py

# Extract D3 boys from web search data
python3 extract_leaderboard_from_webpage.py
```

---

## 📊 Current D3 Boys Standings (Tanque Verde)

Based on azpreps365.com as of today:

### 🥇 #1 Rankings:
- **200 Medley IM** - Wade Olsson (2:00.20)
- **100 Fly** - Zachary Duerkop (53.01)
- **200 Medley Relay** - Team (1:41.80)
- **200 Free Relay** - Team (1:31.81)

### 🥈 #2 Rankings:
- **200 Medley IM** - Zachary Duerkop (2:00.80)
- **100 Breaststroke** - Zachary Duerkop (59.61)
- **200 Free** - Zachary Duerkop (1:48.07)
- **400 Free Relay** - Team (3:20.60)

### 🥉 #3 Rankings:
- **100 Breaststroke** - Wade Olsson (1:00.17)
- **50 Free** - Jackson Eftekhar (22.01)
- **100 Free** - Zachary Duerkop (47.92)

**Total:** 12 top-3 finishes across all events!

---

## 🔄 Weekly Harvest Workflow

Run this every week or after major meets:

```bash
# Week 1
cd /Users/aaryn/swimming/tanque-verde
./harvest_all.sh
# → Creates: data/raw/azpreps365_harvest/2024-10-26/

# Week 2  
./harvest_all.sh
# → Creates: data/raw/azpreps365_harvest/2024-11-02/

# Week 3
./harvest_all.sh
# → Creates: data/raw/azpreps365_harvest/2024-11-09/
```

Each harvest is timestamped - never overwrites previous data!

---

## 📁 Files Created

### Main Scripts:
- `harvest_all.sh` - Run everything (recommended)
- `harvest_azpreps365.py` - Scrape leaderboards
- `harvest_relays.py` - Collect new relay results
- `extract_leaderboard_from_webpage.py` - Manual extraction fallback
- `parse_azpreps365_html.py` - Debug HTML structure

### Test & Verification:
- `quick_test_harvest.sh` - Quick setup test
- `test_harvest_setup.py` - Full verification

### Documentation:
- `HARVEST_QUICK_START.md` - This file
- `HARVEST_SETUP_COMPLETE.md` - Detailed setup summary
- `README_HARVEST.md` - Complete technical documentation

---

## 🛠️ Troubleshooting

### Script won't run?
```bash
chmod +x harvest_all.sh quick_test_harvest.sh
```

### Missing pandas/libraries?
The script automatically activates the virtual environment. If issues persist:
```bash
source ../swim-data-tool/.venv/bin/activate
pip install pandas beautifulsoup4 requests playwright
```

### No data extracted?
1. Check raw HTML files in output directory
2. Use manual extraction: `python3 extract_leaderboard_from_webpage.py`
3. Manually copy data from https://azpreps365.com/leaderboards/swimming-boys/d3

---

## 💡 Integration with Simulations

The harvest system is **simulation-safe**:
- ✅ Uses separate directory (`azpreps365_harvest/`)
- ✅ Timestamped output (no overwrites)
- ✅ Non-destructive (preserves existing data)
- ✅ Can run alongside relay simulations

Your simulations can continue running while you harvest new data!

---

## 📈 Next Steps After Harvest

1. **Review the data:**
   ```bash
   cd data/raw/azpreps365_harvest/2024-10-26
   head *.csv
   ```

2. **Compare with previous harvest:**
   ```bash
   # If you have a previous harvest
   diff 2024-10-19/*.csv 2024-10-26/*.csv
   ```

3. **Integrate with records:**
   ```bash
   # TODO: Create merge script
   python3 merge_harvests.py
   ```

4. **Update leaderboards:**
   ```bash
   python3 generate_top10.py
   python3 generate_hs_records.py
   ```

---

## 🎯 Why This System?

1. **Reusable** - Run it weekly throughout the season
2. **Non-destructive** - Keeps history of all harvests
3. **Automated** - One command does everything
4. **Flexible** - Run pieces individually if needed
5. **Debug-friendly** - Saves raw HTML for troubleshooting
6. **Simulation-safe** - Won't interfere with ongoing work

---

## 📞 Need Help?

- **Technical details:** `README_HARVEST.md`
- **Setup summary:** `HARVEST_SETUP_COMPLETE.md`
- **swim-data-tool docs:** `../swim-data-tool/claude.md`

---

## ✅ Ready to Go!

Everything is set up. Just run:

```bash
./harvest_all.sh
```

The script will:
1. Activate the virtual environment
2. Scrape D3 boys and girls leaderboards
3. Collect new relay results (Oct 20+)
4. Save everything to `data/raw/azpreps365_harvest/2024-10-26/`
5. Display summary statistics

**Total runtime:** ~2-5 minutes (depending on page load times)

---

**Happy Harvesting! 🏊‍♂️🏊‍♀️**

