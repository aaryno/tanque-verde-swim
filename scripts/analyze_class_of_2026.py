#!/usr/bin/env python3
"""
Analyze Class of 2026 seniors' complete swimming history
- Find all events they swam across all years
- Get first and last times in each event
- Calculate time drops
- Identify all records they hold
"""

import re
import json
from pathlib import Path
from datetime import datetime

# Class of 2026 Seniors
SENIORS_2026 = [
    "Zachary Duerkop",
    "Logan Sulger",
    "Madeline Barnard",
    "Grayson The",
    "Adrianna Witte",
    "Carter Caballero",
    "Brooklyn Johnson"
]

def parse_time(time_str):
    """Convert time string to seconds for comparison"""
    if not time_str:
        return None
    
    # Remove any whitespace
    time_str = time_str.strip()
    
    # Handle formats: 1:23.45 or 23.45
    if ':' in time_str:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        return float(time_str)

def parse_date(date_str):
    """Parse date string to datetime for sorting"""
    # Formats: "Nov 08, 2025" or "Nov 8, 2025"
    try:
        return datetime.strptime(date_str, "%b %d, %Y")
    except:
        try:
            return datetime.strptime(date_str, "%b %d, %Y")
        except:
            return None

def analyze_swimmer_history(swimmer_name, gender):
    """Analyze complete swimming history for a swimmer"""
    
    records_dir = Path("records")
    
    # Dictionary to store all swims by event
    swims_by_event = {}
    
    # Search through all Top 10 files for this swimmer
    pattern = rf"\|\s*\d+\s*\|\s*([\d:\.]+)\s*\|\s*{re.escape(swimmer_name)}\s*\|([^|]*)\|([^|]*)\|([^|]*)\|"
    
    for md_file in records_dir.glob(f"top10-{gender}-*.md"):
        season = md_file.stem.replace(f"top10-{gender}-", "")
        
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Find current event section
        current_event = None
        for line in content.split('\n'):
            # Check if this is an event header
            if line.startswith('##') and not line.startswith('###'):
                current_event = line.replace('##', '').strip()
            
            # Check if this line has the swimmer
            if swimmer_name in line and '|' in line:
                match = re.search(pattern, line)
                if match and current_event:
                    time_str = match.group(1).strip()
                    year = match.group(2).strip()
                    date_str = match.group(3).strip()
                    meet = match.group(4).strip()
                    
                    if current_event not in swims_by_event:
                        swims_by_event[current_event] = []
                    
                    swims_by_event[current_event].append({
                        'time': time_str,
                        'time_seconds': parse_time(time_str),
                        'year': year,
                        'date': date_str,
                        'date_parsed': parse_date(date_str),
                        'meet': meet,
                        'season': season
                    })
    
    # For each event, sort by date and calculate improvement
    results = {}
    for event, swims in swims_by_event.items():
        # Sort by date
        swims_sorted = sorted(swims, key=lambda x: x['date_parsed'] if x['date_parsed'] else datetime.min)
        
        if len(swims_sorted) >= 2:
            first_swim = swims_sorted[0]
            last_swim = swims_sorted[-1]
            
            # Calculate time drop
            if first_swim['time_seconds'] and last_swim['time_seconds']:
                time_drop = first_swim['time_seconds'] - last_swim['time_seconds']
                
                results[event] = {
                    'first_swim': first_swim,
                    'last_swim': last_swim,
                    'total_swims': len(swims_sorted),
                    'time_drop': time_drop,
                    'improvement_text': f"{time_drop:.2f}s" if time_drop > 0 else f"{abs(time_drop):.2f}s slower"
                }
        elif len(swims_sorted) == 1:
            results[event] = {
                'first_swim': swims_sorted[0],
                'last_swim': swims_sorted[0],
                'total_swims': 1,
                'time_drop': 0,
                'improvement_text': "Only 1 recorded swim"
            }
    
    return results

def get_swimmer_records(swimmer_name, gender):
    """Find all records held by this swimmer"""
    records = []
    
    records_file = Path(f"records/records-{gender}.md")
    if not records_file.exists():
        return records
    
    with open(records_file, 'r') as f:
        content = f.read()
    
    # Find lines with this swimmer that are bolded (indicating a record)
    pattern = rf"\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*{re.escape(swimmer_name)}\*\*"
    
    current_event = None
    for line in content.split('\n'):
        if line.startswith('##') and not line.startswith('###'):
            current_event = line.replace('##', '').strip()
        
        if match := re.search(pattern, line):
            grade = match.group(1).strip()
            time = match.group(2).strip()
            records.append({
                'event': current_event,
                'grade': grade,
                'time': time
            })
    
    return records

def main():
    results = {}
    
    for swimmer in SENIORS_2026:
        print(f"\n{'='*60}")
        print(f"Analyzing: {swimmer}")
        print('='*60)
        
        # Determine gender from historical data
        gender = "boys"
        if swimmer in ["Logan Sulger", "Madeline Barnard", "Adrianna Witte", "Brooklyn Johnson"]:
            gender = "girls"
        
        # Get swimming history
        history = analyze_swimmer_history(swimmer, gender)
        
        # Get records
        records = get_swimmer_records(swimmer, gender)
        
        results[swimmer] = {
            'gender': gender,
            'history': history,
            'records': records
        }
        
        # Print summary
        print(f"\n{swimmer} ({gender.upper()}):")
        print(f"  Records held: {len(records)}")
        for record in records:
            print(f"    - {record['event']} ({record['grade']}): {record['time']}")
        
        print(f"\n  Events swam: {len(history)}")
        for event, data in sorted(history.items()):
            first = data['first_swim']
            last = data['last_swim']
            print(f"    - {event}:")
            print(f"      First: {first['time']} on {first['date']} ({first['season']})")
            print(f"      Last: {last['time']} on {last['date']} ({last['season']})")
            if data['total_swims'] > 1:
                print(f"      Improvement: {data['improvement_text']} over {data['total_swims']} swims")
    
    # Save to JSON
    output_file = Path("data/class_of_2026_analysis.json")
    output_file.parent.mkdir(exist_ok=True)
    
    # Make dates JSON serializable
    for swimmer, data in results.items():
        for event, event_data in data['history'].items():
            if event_data['first_swim']['date_parsed'] and not isinstance(event_data['first_swim']['date_parsed'], str):
                event_data['first_swim']['date_parsed'] = event_data['first_swim']['date_parsed'].isoformat()
            if event_data['last_swim']['date_parsed'] and not isinstance(event_data['last_swim']['date_parsed'], str):
                event_data['last_swim']['date_parsed'] = event_data['last_swim']['date_parsed'].isoformat()
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Saved analysis to {output_file}")
    print('='*60)

if __name__ == "__main__":
    main()

