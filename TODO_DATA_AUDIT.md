# Data Audit & Formatting TODO

## 1. Formatting Issues (Top 10 pages)

### Current Problem
- Events with no swimmers show empty tables with just headers
- Example: https://aaryno.github.io/tanque-verde-swim/top10/boys-2007-08.html

### Solution
- [ ] Modify `generate_website.py` to detect empty event tables
- [ ] Omit empty events from main display
- [ ] Add section at bottom: "Events with no recorded times: 50 Free, 100 Free, ..."
- [ ] For years without invitationals, add note: "Note: Only state championship results available for this season"

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
| 2012-13 | ❌ No | Need to check if TVHS swam at state |
| 2013-14 | ❌ No | Need to check if TVHS swam at state |
| 2014-15 | ✓ Yes | Has "2014 AIA Division II State Meet" |
| 2015-16 | ? | Need to verify |

### AZPreps365 Archive Links
- 2012: https://azpreps365.com/archives/swimming-boys (check dropdown for 2012)
- 2013: Same site
- 2014: Same site

### Action Items
- [ ] Check AZPreps365 archives for 2012-2014 state results
- [ ] Verify if TVHS had swimmers at each state meet
- [ ] Import missing state data
- [ ] Always include state meet in annual summary (even if no TVHS swimmers)

---

## 3. Annual Summary Formatting

### Requirements
- [ ] State meet should always be listed (with note if no TVHS swimmers)
- [ ] Events with no times should be listed separately
- [ ] Add note about invitational data availability

---

## Progress Log

- 2025-12-11: Created this audit plan

