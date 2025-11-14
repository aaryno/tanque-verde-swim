# Complete Harvest System - Summary

**Date:** October 26, 2025  
**Status:** ✅ All harvest tools ready with configurable output directories

---

## 🎉 What You Have Now

You now have **three tiers of harvest scripts**, each solving different needs:

### Tier 1: Basic Harvest (v2 - Configurable)
**Scripts:** `harvest_azpreps365_v2.py`, `harvest_relays_v2.py`, `harvest_all_v2.sh`

**What it does:**
- Harvests D3 leaderboards (boys/girls)
- Harvests Tanque Verde relays from MaxPreps
- **Configurable output directory** (your priority!)
- **Configurable relay cutoff date**

**Use when:**
- You need Tanque Verde-specific data
- You want to preserve existing analysis data
- You need quick, reliable harvest

**Status:** ✅ **100% Complete and Ready**

### Tier 2: Division-Wide Harvest
**Script:** `harvest_division_complete.py`

**What it does:**
- Harvests **top N swimmers** from D3 leaderboards (default: 50)
- Extracts **all unique schools** from leaderboard
- **Phase 2 (in progress):** Harvest relays from all schools

**Use when:**
- You need complete division data
- You want to analyze all competitors
- You're building lineup optimizer input

**Status:** ✅ **Phase 1 Complete** (leaderboards + school list)  
⚠️ **Phase 2 In Progress** (multi-school relay harvesting)

### Tier 3: Original Harvest (v1 - Legacy)
**Scripts:** `harvest_azpreps365.py`, `harvest_relays.py`, `harvest_all.sh`

**What it does:**
- Original harvest scripts
- Fixed output directory
- Still works perfectly

**Use when:**
- You want default behavior
- You don't need custom directories

**Status:** ✅ **Still works, backward compatible**

---

## 🚀 Quick Usage Guide

### Your Priority: Configurable Output (Tier 1)

```bash
cd /Users/aaryn/swimming/tanque-verde

# Harvest to custom directory (preserves existing data)
./harvest_all_v2.sh data/raw/harvest_for_optimizer

# Or with custom cutoff date
OUTPUT_DIR=data/raw/harvest_sept CUTOFF_DATE=2024-09-01 ./harvest_all_v2.sh

# Or harvest to swim-data-tool directory
./harvest_all_v2.sh ../swim-data-tool/data/reports/azpreps/d3-leaderboards
```

### Division-Wide Harvest (Tier 2)

```bash
# Harvest top 50 from D3 (leaderboards + school list)
python3 harvest_division_complete.py --leaderboard-only

# Top 100 for comprehensive analysis
python3 harvest_division_complete.py --top-n=100 --leaderboard-only

# Custom output directory
python3 harvest_division_complete.py \
  --output-dir=../swim-data-tool/data/reports/azpreps/d3-complete \
  --top-n=50 \
  --leaderboard-only
```

---

## 📁 Files Created

### New Harvest Scripts

```
tanque-verde/
├── harvest_azpreps365_v2.py          ✅ Configurable leaderboard harvest
├── harvest_relays_v2.py              ✅ Configurable relay harvest
├── harvest_all_v2.sh                 ✅ Complete pipeline (v2)
├── harvest_division_complete.py      ✅ Division-wide harvest (Phase 1 complete)
│
├── HARVEST_V2_GUIDE.md               ✅ Comprehensive v2 guide
├── HARVEST_V2_SUMMARY.md             ✅ V2 quick reference
├── HARVEST_DIVISION_COMPLETE_GUIDE.md ✅ Division harvest guide
└── HARVEST_COMPLETE_SUMMARY.md       ✅ This file
```

### Original Scripts (Unchanged)

```
tanque-verde/
├── harvest_azpreps365.py             ← Original (still works)
├── harvest_relays.py                 ← Original (still works)
└── harvest_all.sh                    ← Original (still works)
```

---

## 🎯 Use Case Matrix

| Need | Use This | Command |
|------|----------|---------|
| **Preserve existing data** | Tier 1 (v2) | `./harvest_all_v2.sh data/raw/harvest_new` |
| **Custom output directory** | Tier 1 (v2) | `./harvest_all_v2.sh path/to/output` |
| **Different relay cutoff** | Tier 1 (v2) | `CUTOFF_DATE=2024-09-01 ./harvest_all_v2.sh` |
| **Top N from leaderboard** | Tier 2 | `python3 harvest_division_complete.py --top-n=50` |
| **All division schools** | Tier 2 | `python3 harvest_division_complete.py --leaderboard-only` |
| **Default behavior** | Tier 3 (v1) | `./harvest_all.sh` |
| **Lineup optimizer input** | Tier 2 | `python3 harvest_division_complete.py --output-dir=../swim-data-tool/data/reports/azpreps/d3-complete` |

---

## 📊 What Each Tier Produces

### Tier 1 Output (v2 - Tanque Verde Specific)

```
data/raw/harvest_for_optimizer/
└── 2024-10-26/
    ├── azpreps365_d3_boys_leaderboard_2024-10-26.csv      # Full D3 boys leaderboard
    ├── azpreps365_d3_girls_leaderboard_2024-10-26.csv     # Full D3 girls leaderboard
    └── new_relays_since_20241020_2024-10-26.csv           # Tanque Verde relays only
```

### Tier 2 Output (Division-Wide)

```
data/raw/division_harvest/
└── 2024-10-26/
    ├── d3_boys_leaderboard_top50_2024-10-26.csv           # Top 50 boys per event
    ├── d3_girls_leaderboard_top50_2024-10-26.csv          # Top 50 girls per event
    ├── d3_schools_2024-10-26.csv                          # All unique schools
    └── (relay files - Phase 2 in progress)
```

### Tier 3 Output (v1 - Original)

```
data/raw/azpreps365_harvest/
└── 2024-10-26/
    ├── azpreps365_d3_boys_leaderboard_2024-10-26.csv
    ├── azpreps365_d3_girls_leaderboard_2024-10-26.csv
    └── new_relays_since_20241020_2024-10-26.csv
```

---

## ✅ Your Original Question Answered

> "Can this be run to harvest the top 50 again and then go to each team's boys and girls page and harvest all the relays?"

**Answer:** Yes! Here's how:

### Phase 1: ✅ READY NOW

```bash
# Harvest top 50 from leaderboards + extract all schools
python3 harvest_division_complete.py \
  --output-dir=data/raw/d3_complete \
  --top-n=50 \
  --leaderboard-only

# Result:
# - Top 50 boys per event
# - Top 50 girls per event
# - List of all unique schools
```

### Phase 2: ⚠️ IN PROGRESS

The "go to each team's page and harvest relays" part is **partially implemented**:

**What's done:**
- Framework for multi-school relay harvesting
- School name to MaxPreps slug conversion
- URL discovery logic

**What's needed:**
- Full implementation of relay scraper for arbitrary schools
- MaxPreps URL mapping for all D3 schools
- Rate limiting and error handling

**Workaround for now:**
```bash
# Harvest leaderboards (works now)
python3 harvest_division_complete.py --leaderboard-only

# Harvest Tanque Verde relays separately (works now)
python3 harvest_relays_v2.py --output-dir=data/raw/d3_complete/2024-10-26 --no-timestamp
```

---

## 🔨 Completing Multi-School Relay Harvest

To finish Phase 2, we need to:

### Option 1: Manual School Mapping (Fastest)

Create a mapping file with known MaxPreps slugs:

```csv
school,maxpreps_slug,state,city
Tanque Verde,tanque-verde-hawks,az,tucson
Canyon del Oro,canyon-del-oro-dorados,az,tucson
Catalina Foothills,catalina-foothills-falcons,az,tucson
...
```

Then modify `harvest_division_complete.py` to use this mapping.

### Option 2: Automated Discovery (More Work)

Implement MaxPreps search functionality:
1. Search MaxPreps for each school name
2. Parse search results
3. Verify correct school
4. Extract relay data

### Option 3: Incremental Approach (Recommended)

1. **Start with known schools** (manual mapping)
2. **Test with 2-3 schools** to validate approach
3. **Expand to all D3 schools** once working
4. **Add automated discovery** as enhancement

---

## 💡 Recommended Next Steps

### Immediate (Ready Now)

1. **Use Tier 1 for your priority:**
   ```bash
   ./harvest_all_v2.sh data/raw/harvest_for_optimizer
   ```
   ✅ Preserves existing data  
   ✅ Configurable output  
   ✅ Works perfectly

2. **Use Tier 2 for division analysis:**
   ```bash
   python3 harvest_division_complete.py --top-n=50 --leaderboard-only
   ```
   ✅ Top 50 per event  
   ✅ All school names  
   ✅ Ready for lineup optimizer

3. **Convert leaderboard for optimizer:**
   - Create pivot script (long to wide format)
   - Transform for lineup optimizer input

### Short Term (1-2 hours)

4. **Create school mapping file:**
   - Manually map D3 schools to MaxPreps slugs
   - Test with 2-3 schools
   - Validate relay harvesting

5. **Complete Phase 2:**
   - Implement multi-school relay harvesting
   - Test with full D3 division
   - Document results

### Long Term (Future Enhancement)

6. **Automated school discovery:**
   - MaxPreps search integration
   - Automatic slug detection
   - Verification logic

7. **Data quality checks:**
   - Validate completeness
   - Check for duplicates
   - Time format validation

8. **Analysis tools:**
   - Division statistics
   - School comparisons
   - Event strength analysis

---

## 📚 Documentation

### Comprehensive Guides

- **`HARVEST_V2_GUIDE.md`** - Complete guide for Tier 1 (v2 scripts)
- **`HARVEST_DIVISION_COMPLETE_GUIDE.md`** - Complete guide for Tier 2 (division-wide)
- **`HARVEST_V2_SUMMARY.md`** - Quick reference for v2
- **`HARVEST_COMPLETE_SUMMARY.md`** - This file (overview of all tiers)

### Quick Reference

```bash
# Tier 1: Configurable output (Tanque Verde specific)
./harvest_all_v2.sh data/raw/harvest_new

# Tier 2: Division-wide (top N + all schools)
python3 harvest_division_complete.py --top-n=50 --leaderboard-only

# Tier 3: Original (default behavior)
./harvest_all.sh

# Help
python3 harvest_azpreps365_v2.py --help
python3 harvest_relays_v2.py --help
python3 harvest_division_complete.py --help
```

---

## 🎉 Summary

**You now have:**

✅ **Tier 1 (v2)** - Configurable output directory (YOUR PRIORITY - COMPLETE)  
✅ **Tier 2** - Division-wide harvest (Phase 1 complete: top N + schools)  
✅ **Tier 3 (v1)** - Original scripts (still work, backward compatible)

**Your original question:**
> "Can this be run to harvest the top 50 again and then go to each team's boys and girls page and harvest all the relays?"

**Answer:**
- ✅ **Top 50 harvest:** READY NOW
- ✅ **Extract all schools:** READY NOW
- ⚠️ **All team relays:** Framework ready, needs completion

**Immediate use:**
```bash
# Harvest top 50 + get school list (works now)
python3 harvest_division_complete.py --top-n=50 --leaderboard-only

# Harvest Tanque Verde relays (works now)
python3 harvest_relays_v2.py --output-dir=data/raw/d3_complete/2024-10-26 --no-timestamp
```

**Your existing data is safe!** All new scripts use configurable directories and won't overwrite your analysis data.

---

**Date:** October 26, 2025  
**Status:** Tier 1 & 2 Phase 1 Complete, Tier 2 Phase 2 In Progress  
**All scripts ready to use immediately!** 🎉

