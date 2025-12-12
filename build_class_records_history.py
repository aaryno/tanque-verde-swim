#!/usr/bin/env python3
"""
Build class records history from oldest year to newest.
This creates a JSON file tracking all class records over time.
"""

import json
import re
from pathlib import Path
from datetime import datetime

def parse_time_to_seconds(time_str):
    """Convert time string to seconds for comparison"""
    time_str = time_str.strip().replace('**', '')
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                mins, secs = parts
                return float(mins) * 60 + float(secs)
        return float(time_str)
    except:
        return float('inf')

def parse_top10_file(filepath):
    """Parse a Top 10 markdown file and extract times with grades"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    entries = []
    current_event = None
    
    for line in content.split('\n'):
        # Match event headings
        event_match = re.match(r'^###?\s+(.+)$', line)
        if event_match:
            current_event = event_match.group(1).strip()
            continue
        
        # Match table rows
        if current_event and line.startswith('|') and not line.startswith('| Rank') and not line.startswith('|--') and not line.startswith('|:'):
            parts = [p.strip().replace('**', '') for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                try:
                    rank = int(parts[0]) if parts[0].isdigit() else None
                    time = parts[1].replace('(r)', '').strip()
                    name = parts[2]
                    year = parts[3].upper()  # FR, SO, JR, SR
                    date = parts[4]
                    meet = parts[5] if len(parts) > 5 else ''
                    
                    if year in ['FR', 'SO', 'JR', 'SR']:
                        entries.append({
                            'event': current_event,
                            'time': time,
                            'time_seconds': parse_time_to_seconds(time),
                            'name': name,
                            'year': year,
                            'date': date,
                            'meet': meet,
                            'rank': rank
                        })
                except:
                    pass
    
    return entries

def get_season_range():
    """Get list of seasons from oldest to newest"""
    seasons = []
    records_dir = Path('records')
    
    for f in records_dir.glob('top10-boys-20*.md'):
        match = re.search(r'(\d{4}-\d{2})\.md$', f.name)
        if match and 'alltime' not in f.name:
            seasons.append(match.group(1))
    
    return sorted(set(seasons))

def main():
    print("Building class records history...")
    print("=" * 60)
    
    # Initialize class records tracker
    # Structure: {gender: {event: {grade: {time, name, date, meet, season}}}}
    class_records = {
        'boys': {},
        'girls': {}
    }
    
    # History of when records were set
    # Structure: [{season, gender, event, grade, time, name, date, meet, previous_time, previous_holder}]
    records_history = []
    
    seasons = get_season_range()
    print(f"Processing {len(seasons)} seasons: {seasons[0]} to {seasons[-1]}")
    
    records_dir = Path('records')
    
    for season in seasons:
        print(f"\n📅 Processing {season}...")
        
        for gender in ['boys', 'girls']:
            filepath = records_dir / f'top10-{gender}-{season}.md'
            if not filepath.exists():
                continue
            
            entries = parse_top10_file(filepath)
            
            for entry in entries:
                event = entry['event']
                grade = entry['year']
                time_secs = entry['time_seconds']
                
                if event not in class_records[gender]:
                    class_records[gender][event] = {}
                
                current_record = class_records[gender][event].get(grade)
                
                # Check if this is a new record
                if current_record is None or time_secs < current_record['time_seconds']:
                    previous = None
                    if current_record:
                        previous = {
                            'time': current_record['time'],
                            'name': current_record['name'],
                            'date': current_record['date'],
                            'season': current_record['season']
                        }
                    
                    # Update the record
                    class_records[gender][event][grade] = {
                        'time': entry['time'],
                        'time_seconds': time_secs,
                        'name': entry['name'],
                        'date': entry['date'],
                        'meet': entry['meet'],
                        'season': season
                    }
                    
                    # Log the record
                    records_history.append({
                        'season': season,
                        'gender': gender,
                        'event': event,
                        'grade': grade,
                        'time': entry['time'],
                        'name': entry['name'],
                        'date': entry['date'],
                        'meet': entry['meet'],
                        'previous': previous
                    })
                    
                    if previous:
                        print(f"  {gender.title()} {grade} {event}: {entry['time']} {entry['name']} (was {previous['time']} by {previous['name']})")
                    else:
                        print(f"  {gender.title()} {grade} {event}: {entry['time']} {entry['name']} (FIRST RECORD)")
    
    # Save outputs
    output_dir = Path('data')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'class_records_current.json', 'w') as f:
        json.dump(class_records, f, indent=2)
    
    with open(output_dir / 'class_records_history.json', 'w') as f:
        json.dump(records_history, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Built class records history")
    print(f"  Current records: data/class_records_current.json")
    print(f"  History log: data/class_records_history.json")
    print(f"  Total records set: {len(records_history)}")

if __name__ == '__main__':
    main()

