# Swimmer Name Consolidation - Tanque Verde

**Date:** October 9, 2025  
**Status:** ✅ Complete

## Summary

Consolidated duplicate swimmers who appeared with different name variations across data sources (MaxPreps vs AIA state meet PDFs).

## Tools Created

### 1. `detect_name_duplicates.py`
Scans swimmer CSV files to find potential duplicates based on:
- Similar last names
- Common nickname variations (Nick/Nicholas, Sam/Samuel, Zach/Zachary, etc.)
- Overlapping grades/dates

### 2. `consolidate_swimmers.py`
Interactive tool that:
- Prompts user to confirm duplicates
- Asks which name to display in records
- Merges CSV files
- Creates aliases mapping
- Removes duplicate files

### 3. `swimmer_aliases.json`
Permanent mapping file that tracks:
- All name variations for each swimmer
- Preferred display name
- Used automatically by merge scripts

## Consolidations Completed

| Original Names | Preferred Name | Swims Merged |
|----------------|----------------|--------------|
| Sam Stott, Samuel Stott | Sam Stott | 43 |
| Nick Cusson, Nicholas Cusson | Nick Cusson | 42 |
| Zach Duerkop, Zachary Duerkop | Zach Duerkop | 30 |
| Nick Spilotro (3 files), Nicholas Spilotro | Nick Spilotro | 33 |
| Nolan Radomsky (2 files) | Nolan Radomsky | 27 |
| Joseph Breinholt, Joe Breinholt | Joe Breinholt | 21 |
| JP Spilotro (2 files) | JP Spilotro | 3 |
| Tannor Soedor (2 files) | Tannor Soedor | 10 |
| Sam Merrill, Samuel Merrill | Sam Merrill | 13 |
| Natalie Armstrong (2 files) | Natalie Armstrong | 35 |

**Total:** 10 swimmers consolidated, 257 swims merged

## Files Updated

### Created:
- `/Users/aaryn/swimming/tanque-verde/detect_name_duplicates.py`
- `/Users/aaryn/swimming/tanque-verde/consolidate_swimmers.py`
- `/Users/aaryn/swimming/tanque-verde/data/swimmer_aliases.json`
- `/Users/aaryn/swimming/tanque-verde/data/README.md`

### Modified:
- `/Users/aaryn/swimming/tanque-verde/merge_aia_state_data.py` - Now applies aliases automatically
- Swimmer CSV files - Merged and updated with preferred names
- Records files - Regenerated with consolidated names

## Future Workflow

When importing new data:

1. **Auto-apply aliases:** `merge_aia_state_data.py` automatically uses aliases
2. **Detect new duplicates:** Run `detect_name_duplicates.py` after each import
3. **Consolidate if needed:** Run `consolidate_swimmers.py` for any new duplicates
4. **Regenerate records:** `generate_hs_records.py`
5. **Publish:** `swim-data-tool publish`

## Nickname Mappings Supported

The system recognizes these common nickname variations:

- Nicholas/Nick/Nicolas
- Samuel/Sam/Sammy
- Zachary/Zach/Zack
- William/Will/Bill/Billy
- Robert/Rob/Bob/Bobby
- Benjamin/Ben/Benji
- Michael/Mike/Mikey
- Christopher/Chris
- Joseph/Joe/Joey
- Jonathan/Jon/Jonny
- Daniel/Dan/Danny
- Matthew/Matt
- Alexander/Alex
- Elizabeth/Liz/Beth/Lizzy
- Katherine/Kate/Katie/Kathy
- Margaret/Maggie/Meg

Additional mappings can be easily added to `detect_name_duplicates.py`.

## Benefits

✅ **Consistent names** across all records  
✅ **Complete swim histories** - no data lost across sources  
✅ **Automatic handling** - future imports use aliases  
✅ **Extensible** - easy to add new swimmers or nicknames  
✅ **Auditable** - all mappings tracked in JSON file  

---

*Generated: October 9, 2025*
