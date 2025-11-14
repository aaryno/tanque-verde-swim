# Tanque Verde High School Swimming Data

## Directory Structure

```
data/
├── lookups/
│   └── roster-maxpreps.csv          # MaxPreps roster data
├── raw/
│   ├── swimmers/                     # Individual swimmer CSV files
│   └── aia-state/                    # AIA state championship data
│       ├── aia-state-2001.pdf → 2024.pdf
│       ├── tvhs-all-state-meets.csv
│       └── tvhs-state-YYYY.csv
├── records/
│   └── scy/
│       ├── records-boys.md
│       └── records-girls.md
└── swimmer_aliases.json              # Name alias mappings

```

## Swimmer Aliases

The `swimmer_aliases.json` file tracks swimmers who appear with different name variations across data sources (MaxPreps vs AIA PDFs):

**Purpose:**
- Consolidate duplicate swimmer records
- Map all name variations to a preferred display name
- Ensure consistent naming across records

**Format:**
```json
{
  "Nicholas Cusson": "Nick Cusson",
  "Samuel Stott": "Sam Stott",
  "Zachary Duerkop": "Zach Duerkop"
}
```

**Usage:**
- `detect_name_duplicates.py` - Scans for potential duplicates
- `consolidate_swimmers.py` - Interactive tool to merge duplicates and create aliases
- `merge_aia_state_data.py` - Automatically applies aliases when merging AIA data

## Workflow

### Initial Setup
1. Import MaxPreps data: `swim-data-tool import swimmers --file=data/lookups/roster-maxpreps.csv`
2. Parse AIA state meets: `python3 parse_aia_state_meets.py`
3. Detect duplicates: `python3 detect_name_duplicates.py`
4. Consolidate duplicates: `python3 consolidate_swimmers.py`
5. Merge AIA data: `python3 merge_aia_state_data.py`
6. Generate records: `python3 generate_hs_records.py`
7. Publish: `swim-data-tool publish`

### Regular Updates
1. Re-import MaxPreps: `swim-data-tool import swimmers --file=data/lookups/roster-maxpreps.csv`
2. Re-parse AIA (if new year available): `python3 parse_aia_state_meets.py`
3. Merge new data: `python3 merge_aia_state_data.py` (automatically applies aliases)
4. Check for new duplicates: `python3 detect_name_duplicates.py`
5. Regenerate records: `python3 generate_hs_records.py`
6. Publish: `swim-data-tool publish`

