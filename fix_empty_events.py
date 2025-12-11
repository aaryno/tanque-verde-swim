#!/usr/bin/env python3
"""
Fix empty events in Top 10 markdown files.
- Removes events with no swimmers from the main content
- Adds a section at the bottom listing events with no recorded times
- Adds note about data availability for historical years
"""

import re
from pathlib import Path

# Years that only have state championship data (no invitationals)
STATE_ONLY_YEARS = ['2007-08', '2008-09', '2009-10', '2010-11', '2011-12']

def process_top10_file(filepath: Path) -> tuple:
    """Process a single top10 file, return (events_with_data, events_without_data)."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract season from filename
    season_match = re.search(r'(\d{4}-\d{2})', filepath.name)
    season = season_match.group(1) if season_match else ""
    
    lines = content.split('\n')
    new_lines = []
    current_event = None
    event_lines = []
    events_with_data = []
    events_without_data = []
    in_header = True
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect event headings
        if line.startswith('## ') and not line.startswith('## Tanque Verde'):
            # Save previous event if any
            if current_event:
                # Check if event has data (more than just header row)
                has_data = False
                for el in event_lines:
                    if el.strip().startswith('|') and '|-----' not in el and '| Rank |' not in el:
                        has_data = True
                        break
                
                if has_data:
                    events_with_data.append(current_event)
                    new_lines.extend(event_lines)
                else:
                    events_without_data.append(current_event)
            
            current_event = line.replace('## ', '').strip()
            event_lines = [line]
            in_header = False
        elif in_header:
            new_lines.append(line)
        elif current_event:
            event_lines.append(line)
        
        i += 1
    
    # Handle last event
    if current_event:
        has_data = False
        for el in event_lines:
            if el.strip().startswith('|') and '|-----' not in el and '| Rank |' not in el:
                has_data = True
                break
        
        if has_data:
            events_with_data.append(current_event)
            new_lines.extend(event_lines)
        else:
            events_without_data.append(current_event)
    
    # Add section for events without data
    if events_without_data:
        new_lines.append('')
        new_lines.append('---')
        new_lines.append('')
        new_lines.append('## Events With No Recorded Times')
        new_lines.append('')
        new_lines.append('The following events have no recorded times for this season:')
        new_lines.append('')
        for event in events_without_data:
            new_lines.append(f'- {event}')
        new_lines.append('')
    
    # Add note for state-only years
    if season in STATE_ONLY_YEARS:
        # Check if note already exists
        if 'Note:' not in content or 'Only state championship' not in content:
            # Find the source line and add note after it
            for i, line in enumerate(new_lines):
                if line.startswith('**Source:**'):
                    new_lines[i] = '**Source:** AIA State Championships Only'
                    if i + 1 < len(new_lines) and not new_lines[i+1].startswith('**Note:**'):
                        new_lines.insert(i + 1, '**Note:** Invitational meet data not available for this season.')
                    break
    
    # Write back
    with open(filepath, 'w') as f:
        f.write('\n'.join(new_lines))
    
    return events_with_data, events_without_data

def main():
    records_dir = Path('records')
    
    print("=" * 70)
    print("FIXING EMPTY EVENTS IN TOP 10 FILES")
    print("=" * 70)
    print()
    
    total_empty = 0
    
    for md_file in sorted(records_dir.glob('top10-*-20*.md')):
        if 'alltime' in md_file.name:
            continue
            
        with_data, without_data = process_top10_file(md_file)
        
        if without_data:
            print(f"  {md_file.name}:")
            print(f"    Events with data: {len(with_data)}")
            print(f"    Events without data: {len(without_data)} - {', '.join(without_data)}")
            total_empty += len(without_data)
    
    print()
    print("=" * 70)
    print(f"TOTAL: {total_empty} empty events moved to bottom sections")
    print("=" * 70)

if __name__ == '__main__':
    main()

