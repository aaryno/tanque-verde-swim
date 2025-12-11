#!/usr/bin/env python3
"""
Fix missing swimmer years in 2020-21 season based on 2019-20 and 2021-22 data.
"""

import re
from pathlib import Path

# Years determined from cross-referencing 2019-20 and 2021-22 seasons
# Format: swimmer_name -> year_in_2020_21
YEAR_MAP = {
    # BOYS - from 2019-20 data (add 1 year)
    "Nicholas Spilotro": "JR",   # SO in 2019-20
    "Joseph Jacobs": "SR",       # JR in 2019-20
    "Julian Pacheco": "SR",      # JR in 2019-20
    
    # BOYS - from 2021-22 data (subtract 1 year)
    "Nolan Radomsky": "FR",      # SO in 2021-22
    "Tannor Soedor": "SO",       # JR in 2021-22
    "JP Spilotro": "FR",         # SO in 2021-22
    
    # GIRLS - from 2019-20 data (add 1 year)
    "Jillian Lightcap": "SO",    # FR in 2019-20
    "Kennady Pautler": "SR",     # JR in 2019-20
    "Sydney Hagerman": "SO",     # FR in 2019-20
    "Delaney Dikeman": "JR",     # SO in 2019-20
    "Felicity Holbrook": "SO",   # FR in 2019-20
    "Lainie Radomsky": "JR",     # SO in 2019-20
    "Violet Dasse": "SR",        # JR in 2019-20
    
    # GIRLS - from 2021-22 data (subtract 1 year)
    "Shaye Sulger": "JR",        # SR in 2021-22 (also spelled Sulgar)
    "Shaye Sulgar": "JR",        # SR in 2021-22 (alternate spelling)
    
    # From Coach Porter Olstad + data verification
    "Beck Caballero": "FR",      # Per coach, also appears in 2021-22
    "Zach Head": "FR",           # Per coach, only appears in 2020-21
    "Finbar Whitfield": "SO",    # Per coach
    "Rosalyn Jacobs": "FR",      # Per coach
    "Emma Kalway": "JR",         # FR(2018-19), SO(2019-20), SR(2021-22) = JR in 2020-21
    "Kylie England": "JR",       # FR(2018-19), SO(2019-20) = JR in 2020-21
    "Samantha Oligmuller": "SO", # Per coach - swam SO year only
}

# Swimmers still unknown after cross-reference
UNKNOWN_SWIMMERS = []

def fix_years_in_file(filepath: Path) -> list:
    """Fix missing years in a file, return list of updates made."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    updates = []
    unknown = []
    
    for line in content.split('\n'):
        # Check for missing year pattern: | Name |  | Date
        match = re.search(r'\| ([A-Za-z]+ [A-Za-z\-]+) \|  \|', line)
        if match:
            swimmer = match.group(1)
            if swimmer in YEAR_MAP:
                # Update the year
                old_pattern = f'| {swimmer} |  |'
                new_pattern = f'| {swimmer} | {YEAR_MAP[swimmer]} |'
                content = content.replace(old_pattern, new_pattern)
                updates.append(f"{swimmer} -> {YEAR_MAP[swimmer]}")
            else:
                if swimmer not in unknown:
                    unknown.append(swimmer)
    
    if updates:
        with open(filepath, 'w') as f:
            f.write(content)
    
    return updates, unknown

def main():
    records_dir = Path('records')
    
    print("=" * 70)
    print("FIXING MISSING YEARS IN 2020-21 SEASON")
    print("=" * 70)
    print()
    
    all_unknown = set()
    
    for md_file in records_dir.glob('top10-*-2020-21.md'):
        print(f"Processing {md_file.name}:")
        updates, unknown = fix_years_in_file(md_file)
        
        for u in updates:
            print(f"  ✓ {u}")
        
        for u in unknown:
            all_unknown.add(u)
    
    print()
    print("=" * 70)
    print("YEAR ASSIGNMENTS (based on 2019-20 and 2021-22 data)")
    print("=" * 70)
    for swimmer, year in sorted(YEAR_MAP.items()):
        print(f"  {swimmer}: {year}")
    
    if all_unknown:
        print()
        print("=" * 70)
        print("⚠️  UNKNOWN SWIMMERS (need manual verification)")
        print("=" * 70)
        for swimmer in sorted(all_unknown):
            print(f"  - {swimmer}")
    else:
        print()
        print("✅ All swimmers have years assigned!")

if __name__ == '__main__':
    main()

