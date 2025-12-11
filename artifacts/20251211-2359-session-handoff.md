# Session Handoff - Dec 11, 2025

## Completed This Session

### 1. Relay Splits Harvest & Display
- ✅ Created `harvest_all_relay_splits.py` - Pulls from MaxPreps using year slugs (e.g., `/fall/24-25/stats/`)
- ✅ Harvested 336 relay splits across 9 seasons (2017-18 through 2025-26)
- ✅ Applied splits to splash page "2025 Records Broken" section (all 8 relays: 4 NEW + 4 OLD)
- ✅ Applied splits to relay records pages (44 boys + 38 girls relays)

### 2. Senior Cards Cleanup
- ✅ Removed confusing inline badges from card titles
- ✅ Added clear "🏆 School Records" and "🥇 Class Records" sections
- ✅ Zachary Duerkop: 100 Breast + 100 Fly school records
- ✅ Logan Sulger: 100 Back school record
- ✅ Green gradient styling for records section

---

## Queued for Next Session

### Priority 1: Harvest Pre-2017 Relay Splits
- MaxPreps data goes back to at least 2012-13
- Update `harvest_all_relay_splits.py` to try earlier years
- May hit gaps where data doesn't exist

### Priority 2: Add Splits to Season Top 10 Pages
- Currently only splash page and relay records pages have splits
- Need to integrate splits into the season-by-season Top 10 relay tables

### Priority 3: Extract Relay Leadoff Times as Individual Times

**Concept:** In swimming, the first leg of a relay is a "leadoff" - they start from the blocks just like an individual event, so it counts as an official individual time.

**Mapping:**
| Relay Event | Leadoff Stroke | Individual Event |
|-------------|----------------|------------------|
| 200 Free Relay | Free | 50 Freestyle |
| 400 Free Relay | Free | 100 Freestyle |
| 200 Medley Relay | Back | 50 Backstroke* |

*Note: 50 Backstroke isn't a standard HS event, but the data could still be useful.

**Implementation Plan:**
1. Parse harvested splits data
2. Extract first leg (leadoff) swimmer + time for each relay
3. Cross-reference with existing individual times
4. Flag new times that could be added to Top 10 lists
5. Potentially create a "Relay Leadoffs" section or integrate into individual event rankings

**Data Already Available:**
- `data/historical_splits/all_relay_splits.json` contains all harvested splits
- Each entry has `swimmers[0]` as leadoff with their split time

**Example:**
```json
{
  "type": "free",
  "swimmers": ["Jackson Eftekhar - Jr.", "Grayson The - Sr.", ...],
  "splits": ["00:23.21", "00:23.25", ...]
}
```
→ Jackson Eftekhar has a 23.21 50 Free from this relay leadoff

---

## Files Modified This Session
- `docs/index.html` - Senior cards, relay splits on splash
- `docs/css/style.css` - Senior card styling, relay split styling
- `docs/records/boys-relays.html` - Added splits
- `docs/records/girls-relays.html` - Added splits
- `harvest_all_relay_splits.py` - New script for historical splits
- `apply_all_splits.py` - Script to inject splits into HTML
- `add_splits_to_relay_pages.py` - Script for relay pages

## Commits
1. "Harvest and add relay splits from all seasons (2017-2025)"
2. "Add relay splits to boys and girls relay records pages"
3. "Clean up senior cards: reorganize records section"

