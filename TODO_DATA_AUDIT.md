# Data Audit & Formatting TODO

## 1. Formatting Issues (Top 10 pages) ✅ COMPLETED

### Problem (Fixed)
- Events with no swimmers showed empty tables with just headers

### Solution Implemented
- [x] Created `fix_empty_events.py` to detect empty event tables
- [x] Empty events omitted from main display
- [x] Added "Events with no recorded times" section at bottom
- [x] Added note: "Invitational meet data not available for this season" for 2007-2011

---

## 2. State Meet Audit (2012-2015)

### Current Status

| Season | State Meet in Data? | Notes |
|--------|---------------------|-------|
| 2007-08 | ✓ Yes | Imported from AZPreps365 PDF |
| 2008-09 | ✓ Yes | Imported from AZPreps365 PDF |
| 2009-10 | ✓ Yes | Imported from AZPreps365 PDF |
| 2010-11 | ✓ Yes | Imported from AZPreps365 PDF |
| 2011-12 | ✓ Yes | Imported from AZPreps365 PDF |
| 2012-13 | ❌ No | Need to manually check AZPreps365 archive |
| 2013-14 | ❌ No | Need to manually check AZPreps365 archive |
| 2014-15 | ✓ Yes | Has "2014 AIA Division II State Meet" |
| 2015-16 | ✓ Fixed | Removed duplicate D-3 meet, kept D-II |

### AZPreps365 Archive Links
- Archive page: https://azpreps365.com/archives/swimming-boys
- Need to manually check dropdown for 2012, 2013, 2014 PDFs

### Remaining Action Items
- [ ] Manually check AZPreps365 archives for 2012-2014 state results
- [ ] Verify if TVHS had swimmers at each state meet
- [ ] Import missing state data if available
- [ ] Always include state meet in annual summary (even if no TVHS swimmers)

---

## 3. Annual Summary Formatting ✅ COMPLETED

### Requirements Implemented
- [x] Events with no times listed separately at bottom
- [x] Note about invitational data availability added

### Remaining
- [ ] State meet should always be listed (with note if no TVHS swimmers)

---

## Progress Log

- 2025-12-11: Created this audit plan
- 2025-12-11: Fixed empty event formatting (46 events across 10 files)
- 2025-12-11: Added data availability notes for 2007-2011
- 2025-12-11: Fixed 2015-16 duplicate state meet (removed D-3, kept D-II)
- 2025-12-11: Could not automatically find 2012-2014 PDF links - need manual verification

