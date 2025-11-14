# Season Range Testing Guide

**Date:** October 8, 2025  
**Feature:** Season range support for MaxPreps

---

## 🎯 What's New

1. **Season Range Syntax:** Use `--start-season=XX-XX --end-season=YY-YY` instead of listing all seasons individually
2. **Explicit Season Testing:** Verify that future seasons like `25-26` work correctly

---

## 🧪 Quick Tests

### Test 1: Single Explicit Season (25-26)
```bash
cd ~/swimming/tanque-verde
uv run swim-data-tool roster --source=maxpreps --seasons=25-26
```

**Expected:**
- Scrapes only 2025-26 season
- Works correctly with future season

---

### Test 2: Season Range (Small - 3 seasons)
```bash
cd ~/swimming/tanque-verde
uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25
```

**Expected:**
- Shows: `Seasons: 22-23 to 24-25 (3 seasons)`
- Scrapes: 22-23, 23-24, 24-25
- Deduplicates swimmers by `careerid` (keeps most recent grade)

---

### Test 3: Season Range (Large - 13 seasons)
```bash
cd ~/swimming/tanque-verde
uv run swim-data-tool roster --source=maxpreps --start-season=12-13 --end-season=24-25
```

**Expected:**
- Shows: `Seasons: 12-13 to 24-25 (13 seasons)`
- Scrapes all 13 seasons
- Takes longer (~2-3 minutes)
- Many historical swimmers

---

### Test 4: Error Handling
```bash
cd ~/swimming/tanque-verde

# Only start-season (should error)
uv run swim-data-tool roster --source=maxpreps --start-season=22-23

# Only end-season (should error)
uv run swim-data-tool roster --source=maxpreps --end-season=24-25
```

**Expected:**
- Error: `Both --start-season and --end-season must be provided together`

---

## 🤖 Automated Test Script

Run all tests automatically:
```bash
cd ~/swimming/tanque-verde
./test_season_ranges.sh
```

This will:
- ✅ Test single explicit season
- ✅ Test season range (22-23 to 24-25)
- ✅ Test error handling (missing start-season)
- ✅ Test error handling (missing end-season)

---

## 📊 Verify Results

```bash
# Check the roster CSV
cat data/lookups/roster-maxpreps.csv | head -20

# Count unique swimmers
wc -l data/lookups/roster-maxpreps.csv

# Check grades distribution
cut -d',' -f4 data/lookups/roster-maxpreps.csv | sort | uniq -c
```

---

## ✅ Success Criteria

- [ ] Single season (25-26) works
- [ ] Season range expands correctly (e.g., 22-23 to 24-25 = 3 seasons)
- [ ] Deduplication keeps most recent grade
- [ ] Error shown when only one range parameter provided
- [ ] CSV saved to `data/lookups/roster-maxpreps.csv`
- [ ] All seasons in range are scraped

---

## 🚀 Next Steps

After verifying season ranges work:
1. Test `import swimmers` with MaxPreps data
2. Generate records with grade-based filtering
3. Compare with USA Swimming backwards compatibility

See `TESTING.md` for full test suite.

