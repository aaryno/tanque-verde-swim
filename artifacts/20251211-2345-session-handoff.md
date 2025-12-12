# Session Handoff - December 11, 2025 @ 11:45 PM

## Project Overview

**Tanque Verde High School Swimming Records Website**
- Live site: https://tanqueverdeswim.org
- GitHub: https://github.com/aaryno/tanque-verde-swim
- Workspace: `/Users/aaryn/workspaces/swimming/tanque-verde-swim`

A static website displaying swim records, Top 10 lists, relay records, and annual summaries for Tanque Verde High School.

## Current Session Summary

This session focused on:
1. ✅ Adding class badges (FR/SO/JR/SR) to relay swimmers in relay records and annual pages
2. ✅ Updating overall records to use badge styling instead of plain text
3. ✅ Adding landscape mode CSS adjustments
4. 🔴 **UNRESOLVED:** Fixing left-alignment of swimmer names in expanded relay details

## Immediate Issue - LEFT ALIGNMENT BUG

### Problem
When you expand a relay row on https://tanqueverdeswim.org/records/boys-relays.html, the swimmer names appear **center-justified** instead of left-justified.

### Desired Layout
```
Backstroke Logan Radomsky SR                    30.98
Breaststroke Titan Flint                        34.18
Butterfly Lukas Baker                           29.66
Freestyle John Deninghoff                       26.78
```

### Current (Broken) Layout
The stroke, swimmer name, and time are all centered in the expanded row instead of:
- Stroke + Name packed to the LEFT
- Time aligned to the RIGHT

### Root Cause (Suspected)
The main `docs/css/style.css` has mobile grid transforms for `.table tbody tr` (around line 1145) that override the inline flexbox styles from `rebuild_relay_pages.py`.

### Files to Investigate
1. **`docs/css/style.css`** - Lines 1145-1300 (mobile table transforms)
2. **`rebuild_relay_pages.py`** - Lines 350-520 (inline CSS generation)
3. **`docs/records/boys-relays.html`** - Generated output to inspect

### CSS Classes Involved
- `.relay-details-row` - The hidden/shown row containing expanded content
- `.relay-expanded-rows` - Container for swimmer rows
- `.relay-split-row` - Individual swimmer row (flexbox)
- `.split-stroke` - Stroke name (contains `.stroke-abbrev` and `.stroke-full`)
- `.split-swimmer` - Swimmer name + class badge
- `.split-time` - Split time

### Detailed CSS Documentation
See: `artifacts/20251211-relay-css-handoff.md`

---

## Completed Tasks This Session

### 1. Class Badges on Relay Pages ✅
- Added FR/SO/JR/SR badges next to swimmer names in expanded relay details
- Extracts class from MaxPreps splits data
- Files: `rebuild_relay_pages.py`, `generate_enhanced_annual.py`

### 2. Class Badges in Overall Records ✅
- Updated `generate_website.py` to detect abbreviated grades (FR/SO/JR/SR) and apply badge styling
- All Top 10 pages now show colored badges instead of plain text

### 3. Responsive Stroke Names ✅
- Desktop shows full names: Backstroke, Breaststroke, Butterfly, Freestyle
- Mobile shows abbreviations: BK, BR, FL, FR
- Both versions in HTML, CSS shows/hides based on screen width

### 4. Landscape Mode CSS ✅
- Added `@media (orientation: landscape)` rules
- Compact headers, tables revert to traditional layout
- File: `docs/css/style.css` (end of file)

---

## Pending TODOs (Not Started)

These were mentioned but not implemented:

1. **Prevent `generate_website.py` from overwriting relay pages**
   - Currently, running `generate_website.py` overwrites the expandable relay pages with plain markdown conversion
   - Need to either skip relay generation or call `rebuild_relay_pages.py` automatically

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `generate_website.py` | Main site generator - converts markdown to HTML |
| `rebuild_relay_pages.py` | Generates relay pages with expandable cards and splits |
| `generate_enhanced_annual.py` | Generates annual summary pages |
| `harvest_all_relay_splits.py` | Scrapes relay splits from MaxPreps |

## Important: Relay Page Generation

**Always run `rebuild_relay_pages.py` after `generate_website.py`** to ensure relay pages have the expandable card format with splits.

```bash
cd /Users/aaryn/workspaces/swimming/tanque-verde-swim
python3 generate_website.py
python3 rebuild_relay_pages.py
git add -A && git commit -m "Regenerate site" && git push origin main
```

---

## Data Files

| File | Purpose |
|------|---------|
| `data/historical_splits/all_relay_splits.json` | Harvested relay splits (208 boys, 246 girls) |
| `data/swimmer_aliases.json` | Name normalization mappings |
| `data/class_records_current.json` | Current class records by grade |
| `data/class_of_2026_analysis.json` | Senior swimmer analysis |

---

## User Preferences (from memories)

1. **No screenshots** - They consume too many tokens. Ask user to share if needed.
2. **Artifacts go to `artifacts/`** - Format: `YYYYMMDD-HHMM-description.md`
3. **Weekly Grooming** on Sunday/Monday
4. **Nightly Commit** when ending sessions

---

## Next Steps for Incoming Agent

1. **Fix the left-alignment bug** in relay expanded content
   - Use browser DevTools to trace where `text-align: center` is coming from
   - Check computed styles on `.split-swimmer` and ancestors
   - May need to add more specific CSS selectors or use `!important`

2. **Test both mobile and desktop** after any CSS changes

3. **Run `rebuild_relay_pages.py`** after making changes to ensure relay pages are regenerated

4. **Push changes** to see them on the live site (GitHub Pages deploys automatically)

