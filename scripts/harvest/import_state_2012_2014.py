#!/usr/bin/env python3
"""
Import state championship data for 2012-2014 from downloaded PDFs.
These were previously missing from the annual summaries.
"""

import re
from pathlib import Path
from datetime import datetime

# TVHS results extracted from PDFs
RESULTS_2012 = {
    'season': '2012-13',
    'meet_date': 'Nov 03, 2012',
    'meet_name': '2012 AIA Division II State Championships',
    'girls': [
        {'event': '200 Freestyle', 'rank': 20, 'name': 'Marisol Rivera', 'year': 'JR', 'time': '2:28.21'},
        {'event': '100 Breaststroke', 'rank': 17, 'name': 'Marisol Rivera', 'year': 'JR', 'time': '1:06.04'},
        {'event': '100 Freestyle', 'rank': 26, 'name': 'Megan Marner', 'year': 'JR', 'time': '1:01.23'},
    ],
    'boys': []
}

RESULTS_2013 = {
    'season': '2013-14',
    'meet_date': 'Nov 02, 2013',
    'meet_name': '2013 AIA Division II State Championships',
    'girls': [
        {'event': '200 Freestyle', 'rank': 11, 'name': 'Marisol Rivera', 'year': 'SR', 'time': '2:03.27'},
        {'event': '500 Freestyle', 'rank': 9, 'name': 'Marisol Rivera', 'year': 'SR', 'time': '5:34.97'},
        {'event': '400 Free Relay', 'rank': 19, 'name': 'Relay Team', 'year': '', 'time': '4:04.26'},
    ],
    'boys': []
}

RESULTS_2014 = {
    'season': '2014-15',
    'meet_date': 'Nov 08, 2014',
    'meet_name': '2014 AIA Division II State Championships',
    'girls': [
        {'event': '200 Freestyle', 'rank': 25, 'name': 'Bridget Spooner', 'year': 'SO', 'time': '2:11.68'},
        {'event': '500 Freestyle', 'rank': 28, 'name': 'Bridget Spooner', 'year': 'SO', 'time': '5:56.61'},
        {'event': '100 Breaststroke', 'rank': 18, 'name': 'Madisyn Clausen', 'year': 'SR', 'time': '1:16.21'},
        {'event': '400 Free Relay', 'rank': 21, 'name': 'Relay Team', 'year': '', 'time': '4:11.63'},
    ],
    'boys': [
        {'event': '500 Freestyle', 'rank': 26, 'name': 'Austin Morris', 'year': 'JR', 'time': '5:29.68'},
        {'event': '100 Freestyle', 'rank': 19, 'name': 'Austin Morris', 'year': 'JR', 'time': '1:00.88'},
        {'event': '100 Freestyle', 'rank': 29, 'name': 'Samuel Merrill', 'year': 'FR', 'time': '1:02.84'},
    ]
}

def update_top10_file(filepath: Path, results: list, meet_date: str, meet_name: str):
    """Add state results to a top10 file."""
    if not results:
        return 0
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    added = 0
    for result in results:
        event = result['event']
        
        # Skip relays for now - they go in relay files
        if 'Relay' in event:
            continue
            
        # Find the event section
        event_pattern = rf'## {re.escape(event)}\n'
        event_match = re.search(event_pattern, content)
        
        if not event_match:
            print(f"  Warning: Event '{event}' not found in {filepath.name}")
            continue
        
        # Check if this result is already in the file
        name_in_file = re.search(rf'{re.escape(result["name"])}.*{re.escape(result["time"])}', content)
        if name_in_file:
            print(f"  Skipping duplicate: {result['name']} - {result['time']}")
            continue
        
        # Find where to insert (after the header row)
        # Look for the separator line after the event header
        insert_pos = content.find('|-----', event_match.end())
        if insert_pos == -1:
            continue
        
        # Find the end of the separator line
        insert_pos = content.find('\n', insert_pos) + 1
        
        # Find the next event section or end
        next_event = re.search(r'\n---\n\n## ', content[insert_pos:])
        
        # Count existing entries to determine rank
        if next_event:
            section_content = content[insert_pos:insert_pos + next_event.start()]
        else:
            section_content = content[insert_pos:]
        
        existing_rows = [l for l in section_content.split('\n') if l.strip().startswith('|') and 'Rank' not in l]
        new_rank = len(existing_rows) + 1
        
        # Create new row
        new_row = f"| {new_rank} | {result['time']} | {result['name']} | {result['year']} | {meet_date} | {meet_name} |\n"
        
        # Insert at the end of the section (before ---)
        section_end = insert_pos
        for line in section_content.split('\n'):
            if line.strip() == '---' or line.strip() == '':
                break
            section_end += len(line) + 1
        
        content = content[:section_end] + new_row + content[section_end:]
        added += 1
        print(f"  Added: {result['name']} - {result['event']} - {result['time']}")
    
    if added > 0:
        with open(filepath, 'w') as f:
            f.write(content)
    
    return added

def update_annual_summary(filepath: Path, meet_date: str, meet_name: str):
    """Add state meet to annual summary if missing."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if meet already exists
    if meet_name in content or 'State Championship' in content:
        print(f"  State meet already in {filepath.name}")
        return False
    
    # Find the meet schedule section
    if '## Meet Schedule' not in content:
        print(f"  No Meet Schedule section in {filepath.name}")
        return False
    
    # Find the end of the meet table
    schedule_pos = content.find('## Meet Schedule')
    table_end = content.find('\n---\n', schedule_pos)
    
    if table_end == -1:
        table_end = content.find('\n\n', schedule_pos + 100)
    
    # Insert state meet
    new_row = f"| {meet_date} | {meet_name} |\n"
    content = content[:table_end] + new_row + content[table_end:]
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"  Added state meet to {filepath.name}")
    return True

def main():
    records_dir = Path('records')
    
    print("=" * 70)
    print("IMPORTING 2012-2014 STATE CHAMPIONSHIP DATA")
    print("=" * 70)
    
    all_results = [RESULTS_2012, RESULTS_2013, RESULTS_2014]
    
    for results in all_results:
        season = results['season']
        meet_date = results['meet_date']
        meet_name = results['meet_name']
        
        print(f"\n=== {season} Season ===")
        print(f"Meet: {meet_name}")
        
        # Update boys top10
        boys_file = records_dir / f"top10-boys-{season}.md"
        if boys_file.exists() and results['boys']:
            print(f"\nUpdating {boys_file.name}:")
            update_top10_file(boys_file, results['boys'], meet_date, meet_name)
        elif not results['boys']:
            print(f"\n  No boys results for {season}")
        
        # Update girls top10
        girls_file = records_dir / f"top10-girls-{season}.md"
        if girls_file.exists() and results['girls']:
            print(f"\nUpdating {girls_file.name}:")
            update_top10_file(girls_file, results['girls'], meet_date, meet_name)
        elif not results['girls']:
            print(f"\n  No girls results for {season}")
        
        # Update annual summary
        summary_file = records_dir / f"annual-summary-{season}.md"
        if summary_file.exists():
            print(f"\nUpdating {summary_file.name}:")
            update_annual_summary(summary_file, meet_date, meet_name)
    
    print("\n" + "=" * 70)
    print("IMPORT COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()

