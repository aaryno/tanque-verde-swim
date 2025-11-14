# Season Update Guide
**Automated Workflow for Tanque Verde Swimming Records**

## Quick Start for Next Season (2026-27)

At the end of the season, run this single command:

```bash
python run_season_update.py \
  --season 26-27 \
  --state-pdf ~/Downloads/d3-state-2026.pdf \
  --senior-class 2027
```

That's it! The script will:
1. ✅ Harvest all MaxPreps data
2. ✅ Parse state championship PDF
3. ✅ Generate all records (individual, relay, top 10)
4. ✅ Analyze records broken
5. ✅ Generate state meet highlights
6. ✅ Generate senior class highlights
7. ✅ Create formatted annual summary
8. ✅ Regenerate entire website

Then commit and push:

```bash
git add -A
git commit -m "Season 2026-27 update"
git push origin main
```

The website will update automatically in 1-3 minutes!

---

## Manual Step-by-Step (if needed)

### 1. Prepare Data

**Get the MaxPreps Roster:**
```bash
swim-data-tool roster --seasons=26-27
```

**Import Swimmer Data:**
```bash
swim-data-tool import swimmers --source=maxpreps
```

**Get State Championship PDF:**
- Download from AIA website
- Save as `~/Downloads/d3-state-2026.pdf`

### 2. Process State Championship

**Copy PDF:**
```bash
cp ~/Downloads/d3-state-2026.pdf data/raw/aia-state/aia-state-2026.pdf
```

**Update Parser:**
Edit `parse_aia_state_meets.py` and add to the `AIA_STATE_MEETS` list:
```python
{"year": 2026, "file_id": None, "date": "11/X/2026"},
```

**Parse and Merge:**
```bash
python parse_aia_state_meets.py
python merge_aia_state_data.py
```

### 3. Generate Records

```bash
# Individual records
python generate_hs_records.py

# Relay records
python generate_relay_records.py

# All top 10 lists
python generate_all_season_top10.py

# Annual summary
python generate_annual_summary.py
```

### 4. Analyze Highlights

**Find Records Broken:**
```bash
python analyze_season.py --season 26-27 --year 2026
```

**State Meet Highlights:**
```bash
python analyze_state_meet.py --year 2026
```

**Senior Class Highlights:**
```bash
python analyze_seniors.py --class-year 2027
```

### 5. Update Website

**Regenerate All Pages:**
```bash
python generate_website.py
```

**Update Landing Page:**
Manually edit `docs/index.html` to add:
- Records broken this season
- State meet highlights
- Senior class highlights

Or better yet, use the formatted annual summary content!

### 6. Deploy

```bash
git add -A
git commit -m "Season 2026-27 update - records, highlights, and website"
git push origin main
```

---

## File Structure

```
tanque-verde/
├── run_season_update.py          # Main orchestrator script
├── analyze_season.py              # Find records broken
├── analyze_state_meet.py          # State meet highlights
├── analyze_seniors.py             # Senior class highlights
├── generate_annual_summary.py     # Create formatted summary
├── generate_website.py            # Build HTML site
│
├── data/
│   ├── lookups/
│   │   └── roster-maxpreps-2026.csv
│   ├── raw/
│   │   ├── swimmers/              # Individual swimmer CSVs
│   │   └── aia-state/             # State championship PDFs
│   └── records/
│       ├── records-boys.md
│       ├── records-girls.md
│       ├── relay-records-boys.md
│       ├── relay-records-girls.md
│       ├── top10-*.md
│       └── annual-summary-26-27.md
│
├── docs/                          # GitHub Pages website
│   ├── index.html                 # Landing page
│   ├── css/style.css
│   ├── records/                   # Individual & relay records
│   ├── top10/                     # Top 10 lists
│   └── annual/                    # Annual summaries
│
└── artifacts/                     # Analysis outputs
    ├── records-broken-26-27.md
    ├── state-meet-highlights-2026.md
    └── senior-class-2027.md
```

---

## Customization

### Annual Summary Format

The annual summary should match the landing page format with:

1. **Season Overview**
   - Record count
   - State meet placement
   - Team highlights

2. **Records Broken** 
   - Overall school records (individual + relay)
   - Grade records
   - Format: NEW/OLD with dates, improvement

3. **State Championship Highlights**
   - Top finishers (1st-8th place)
   - Biggest time improvements
   - All qualifiers

4. **Senior Class Highlights** (if applicable)
   - Career bests by event
   - State meet history
   - Career progression

### Website Theme

Colors are defined in `docs/css/style.css`:
- `--tvhs-primary`: Forest Green (#2C5F2D)
- `--tvhs-secondary`: Silver (#C0C0C0)
- `.boys-nav`: Forest green (#2C5F2D)
- `.girls-nav`: Silver/Grey (#808080)

---

## Troubleshooting

**"No swimmers found for this team"**
- Check season format: Use "26-27" not "2026-27"
- Verify MaxPreps roster exists

**"Module not found" errors**
- Ensure you're in the correct directory
- Check Python environment has required packages

**Records don't update**
- Verify state data was merged: `ls data/raw/swimmers/*.csv | wc -l`
- Check for relay data filtering in generate scripts

**Website shows old data**
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- Wait 2-3 minutes for GitHub Pages rebuild
- Clear browser cache

---

## For Next Year (Quick Checklist)

- [ ] Download state championship PDF
- [ ] Run `run_season_update.py` with correct parameters
- [ ] Review generated content
- [ ] Commit and push to GitHub
- [ ] Wait for GitHub Pages to rebuild
- [ ] Verify website shows new data

---

## Maintenance

**Update Python Dependencies:**
```bash
pip install --upgrade swim-data-tool pdfplumber pandas
```

**Update MaxPreps URLs:**
If MaxPreps changes their URL structure, update the configuration in:
- `.env` file (MAXPREPS_TEAM_ID)
- `swim-data-tool` configuration

**Add New Swimmers:**
The roster command will automatically find new swimmers. If you need to manually add:
1. Add to `data/lookups/roster-maxpreps.csv`
2. Run import again

---

## Contact

Questions? Check `claude.md` for project documentation or refer to commit history for examples.

Last Updated: November 14, 2025

