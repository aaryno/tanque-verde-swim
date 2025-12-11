#!/usr/bin/env python3
"""
Fix missing swimmer years in records based on historical data research.
Logs all updates for review.
"""

import re
from pathlib import Path

# Swimmer years determined from historical records:
# - Samuel Stott: FR in 2019-20, SO in 2020-21, JR in 2021-22
# - John Deninghoff: Based on Nov 2018 state meet, likely SR (graduating)
# - Lindsey Schoel-Smith: FR in 2015-16, SO in 2016-17, JR in 2017-18, SR in 2018-19
# - Dominic Colombo: FR in 2017-18, SO in 2018-19, JR in 2019-20, SR in 2020-21
# - Sage Weatherwax: FR in 2018-19, SO in 2019-20, JR in 2020-21, SR in 2021-22
# - Chloe Weatherwax: Unknown - appears in 2020-21
# - Alexa Barrera: Unknown - appears in 2023-24

YEAR_FIXES = [
    # (pattern, replacement, swimmer name for log)
    # Samuel Stott - 2020-21 season = SO (was FR in 2019-20)
    (r'\| Samuel Stott \| +\| (Nov 0[45], 2020|Oct 30, 2020)', r'| Samuel Stott | SO | \1', 'Samuel Stott'),
    (r'\| Samuel Stott \| +\| (Nov 05, 2021)', r'| Samuel Stott | JR | \1', 'Samuel Stott'),
    
    # John Deninghoff - 2018-19 season - assumed SR based on being record holder
    (r'\| John Deninghoff \| +\| Nov 01, 2018', r'| John Deninghoff | SR | Nov 01, 2018', 'John Deninghoff'),
    
    # Lindsey Schoel-Smith - SR in 2018-19 (FR in 2015-16)
    (r'\| Lindsey Schoel-Smith \| +\| Nov 01, 2018', r'| Lindsey Schoel-Smith | SR | Nov 01, 2018', 'Lindsey Schoel-Smith'),
    
    # Dominic Colombo - SR in 2020-21 (FR in 2017-18)
    (r'\| Dominic Colombo \| +\| Oct 30, 2020', r'| Dominic Colombo | SR | Oct 30, 2020', 'Dominic Colombo'),
    
    # Sage Weatherwax - JR in 2020-21 (FR in 2018-19)
    (r'\| Sage Weatherwax \| +\| Oct 30, 2020', r'| Sage Weatherwax | JR | Oct 30, 2020', 'Sage Weatherwax'),
]

def fix_missing_years():
    records_dir = Path('records')
    updates_log = []
    
    for md_file in records_dir.glob('top10-*.md'):
        with open(md_file, 'r') as f:
            content = f.read()
        
        original = content
        for pattern, replacement, swimmer in YEAR_FIXES:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                updates_log.append(f"  {md_file.name}: Updated {swimmer}")
                content = new_content
        
        if content != original:
            with open(md_file, 'w') as f:
                f.write(content)
    
    return updates_log

if __name__ == '__main__':
    print("=" * 70)
    print("FIXING MISSING SWIMMER YEARS")
    print("=" * 70)
    print()
    
    updates = fix_missing_years()
    
    if updates:
        print("Updates made:")
        for update in updates:
            print(update)
    else:
        print("No updates needed.")
    
    print()
    print("=" * 70)
    print("Year assignments based on:")
    print("  - Samuel Stott: FR(2019-20), SO(2020-21), JR(2021-22)")
    print("  - John Deninghoff: SR(2018-19) [assumed]")
    print("  - Lindsey Schoel-Smith: FR(2015-16), SO(2016-17), JR(2017-18), SR(2018-19)")
    print("  - Dominic Colombo: FR(2017-18), SO(2018-19), JR(2019-20), SR(2020-21)")
    print("  - Sage Weatherwax: FR(2018-19), SO(2019-20), JR(2020-21)")
    print("=" * 70)
    print()
    print("⚠️  UNKNOWN YEARS (need manual verification):")
    print("  - Chloe Weatherwax (2020-21)")
    print("  - Alexa Barrera (2023-24)")
    print()

