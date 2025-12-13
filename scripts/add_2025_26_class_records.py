#!/usr/bin/env python3
"""
Add 2025-26 class records to class_records_history.json
"""

import json
import re
from pathlib import Path


def parse_records_file(filepath, gender):
    """Parse a records markdown file and extract all 2025-26 class records"""
    records = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all event sections
    event_pattern = r'### (.+?)\n\n\|.*?\|\n\|[-:\|\s]+\|\n((?:\|[^\n]+\n?)+)'
    
    for match in re.finditer(event_pattern, content, re.MULTILINE):
        event_name = match.group(1).strip()
        table_rows = match.group(2).strip()
        
        for row in table_rows.split('\n'):
            if not row.strip() or row.startswith('|--') or '**Open**' in row:
                continue
            
            # Parse: | Grade | Time | Athlete | Date | Meet |
            parts = [p.strip() for p in row.split('|')[1:-1]]
            if len(parts) < 5:
                continue
            
            grade = parts[0].strip()
            time = parts[1].strip()
            athlete = parts[2].strip()
            date = parts[3].strip()
            meet = parts[4].strip()
            
            # Only include 2025 records
            if '2025' in date:
                # Map grade to abbreviation
                grade_map = {
                    'Freshman': 'FR',
                    'Sophomore': 'SO',
                    'Junior': 'JR',
                    'Senior': 'SR'
                }
                grade_abbr = grade_map.get(grade, grade)
                
                records.append({
                    'season': '2025-26',
                    'gender': gender,
                    'event': event_name,
                    'grade': grade_abbr,
                    'time': time,
                    'name': athlete,
                    'date': date,
                    'meet': meet,
                    'previous': None  # Will be populated by looking up previous holder
                })
    
    return records


def find_previous_record(class_records, gender, event, grade, new_time, new_name):
    """Find the previous record holder for a given event/grade"""
    # Look for records with the same gender, event, grade but earlier season
    candidates = [
        r for r in class_records
        if r.get('gender') == gender
        and r.get('event') == event
        and r.get('grade') == grade
        and r.get('season') != '2025-26'
    ]
    
    if not candidates:
        return None
    
    # Sort by season descending to get the most recent
    candidates.sort(key=lambda x: x.get('season', ''), reverse=True)
    
    # Return the most recent previous record
    prev = candidates[0]
    return {
        'time': prev.get('time'),
        'name': prev.get('name'),
        'date': prev.get('date'),
        'season': prev.get('season'),
        'meet': prev.get('meet')
    }


def main():
    print("=" * 60)
    print("Adding 2025-26 Class Records")
    print("=" * 60)
    
    records_dir = Path('records')
    history_file = Path('data/class_records_history.json')
    
    # Load existing class records
    with open(history_file, 'r') as f:
        class_records = json.load(f)
    
    print(f"\nLoaded {len(class_records)} existing class records")
    
    # Remove any existing 2025-26 records
    class_records = [r for r in class_records if r.get('season') != '2025-26']
    print(f"After removing existing 2025-26: {len(class_records)} records")
    
    # Parse boys and girls records
    boys_records = parse_records_file(records_dir / 'records-boys.md', 'boys')
    girls_records = parse_records_file(records_dir / 'records-girls.md', 'girls')
    
    new_records = boys_records + girls_records
    print(f"\nFound {len(new_records)} new 2025-26 class records:")
    
    # Find previous record holders
    for record in new_records:
        prev = find_previous_record(
            class_records,
            record['gender'],
            record['event'],
            record['grade'],
            record['time'],
            record['name']
        )
        record['previous'] = prev
        
        grade = record['grade']
        event = record['event']
        gender = record['gender']
        name = record['name']
        time = record['time']
        
        if prev:
            print(f"  ✓ {gender} {grade} {event}: {name} ({time}) - prev: {prev['name']} ({prev['time']})")
        else:
            print(f"  ✓ {gender} {grade} {event}: {name} ({time}) - FIRST RECORD")
    
    # Add new records
    class_records.extend(new_records)
    
    # Sort by season, gender, event, grade
    class_records.sort(key=lambda x: (
        x.get('season', ''),
        x.get('gender', ''),
        x.get('event', ''),
        ['FR', 'SO', 'JR', 'SR'].index(x.get('grade', 'FR')) if x.get('grade') in ['FR', 'SO', 'JR', 'SR'] else 99
    ))
    
    # Write back
    with open(history_file, 'w') as f:
        json.dump(class_records, f, indent=2)
    
    print(f"\nTotal records now: {len(class_records)}")
    print("✅ Done!")


if __name__ == '__main__':
    main()
