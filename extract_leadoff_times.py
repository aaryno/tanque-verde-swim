#!/usr/bin/env python3
"""
Extract relay leadoff times as individual event times.

Mapping:
- 200 Free Relay leadoff (Split 1) → 50 Freestyle
- 400 Free Relay leadoff (Split 1 + Split 2) → 100 Freestyle

The leadoff swimmer starts from the blocks (like an individual event),
so their time counts as an official individual time.

Times are marked with "(r)" to indicate they came from relay leadoffs.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def clean_name(name):
    """Remove grade suffix from name"""
    if ' - ' in name:
        return name.split(' - ')[0].strip()
    return name.strip()

def get_grade(name):
    """Extract grade from name like 'Wade Olsson - Jr.'"""
    if ' - ' in name:
        grade_part = name.split(' - ')[1].strip().rstrip('.')
        grade_map = {
            'Fr': 'FR', 'So': 'SO', 'Jr': 'JR', 'Sr': 'SR',
            'Freshman': 'FR', 'Sophomore': 'SO', 'Junior': 'JR', 'Senior': 'SR'
        }
        return grade_map.get(grade_part, grade_part.upper())
    return ''

def parse_time_to_seconds(time_str):
    """Convert time string to seconds"""
    time_str = time_str.strip()
    if time_str.startswith('00:'):
        time_str = time_str[3:]
    
    if ':' in time_str:
        parts = time_str.split(':')
        try:
            return int(parts[0]) * 60 + float(parts[1])
        except:
            return None
    else:
        try:
            return float(time_str)
        except:
            return None

def format_time(seconds):
    """Format seconds as time string"""
    if seconds >= 60:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}:{secs:05.2f}"
    else:
        return f"{seconds:.2f}"

def classify_relay(relay):
    """Classify relay type based on splits structure"""
    legs = relay.get('legs', [])
    splits = relay.get('splits', [])
    
    # 200 Medley Relay: 4 splits with stroke names
    if len(splits) == 4 and 'Back' in legs:
        return '200_medley'
    
    # 400 Free Relay: 8 splits (two per swimmer)
    if len(splits) == 8:
        return '400_free'
    
    # 200 Free Relay: 4 splits with Split 1-4
    if len(splits) == 4 and 'Split 1' in legs:
        # Check if times are in 50y range (< 35s typically)
        first_split = parse_time_to_seconds(splits[0])
        if first_split and first_split < 35:
            return '200_free'
    
    return 'unknown'

def extract_leadoff_times(all_splits):
    """Extract leadoff times from all relay splits"""
    
    leadoffs = {
        'boys': {'50_free': [], '100_free': []},
        'girls': {'50_free': [], '100_free': []}
    }
    
    for gender in ['boys', 'girls']:
        for relay in all_splits.get(gender, []):
            relay_type = classify_relay(relay)
            swimmers = relay.get('swimmers', [])
            splits = relay.get('splits', [])
            year = relay.get('year', '')
            
            if not swimmers or not splits:
                continue
            
            if relay_type == '200_free':
                # 200 Free Relay: first swimmer's split = 50 Free
                leadoff_name = clean_name(swimmers[0])
                leadoff_grade = get_grade(swimmers[0])
                leadoff_time = parse_time_to_seconds(splits[0])
                
                # Sanity check: 50 Free should be between 20-40 seconds
                if leadoff_time and 20.0 <= leadoff_time <= 40.0:
                    leadoffs[gender]['50_free'].append({
                        'name': leadoff_name,
                        'grade': leadoff_grade,
                        'time': leadoff_time,
                        'time_str': format_time(leadoff_time),
                        'year': year,
                        'from_relay': '200FR',
                        'raw_split': splits[0]
                    })
            
            elif relay_type == '400_free':
                # 400 Free Relay: first swimmer's two splits = 100 Free
                # Swimmers list has duplicates: [A, A, B, B, C, C, D, D]
                leadoff_name = clean_name(swimmers[0])
                leadoff_grade = get_grade(swimmers[0])
                
                split1 = parse_time_to_seconds(splits[0])
                split2 = parse_time_to_seconds(splits[1])
                
                if split1 and split2:
                    leadoff_time = split1 + split2
                    # Sanity check: 100 Free should be between 45-90 seconds
                    if not (45.0 <= leadoff_time <= 90.0):
                        continue
                    leadoffs[gender]['100_free'].append({
                        'name': leadoff_name,
                        'grade': leadoff_grade,
                        'time': leadoff_time,
                        'time_str': format_time(leadoff_time),
                        'year': year,
                        'from_relay': '400FR',
                        'raw_splits': [splits[0], splits[1]]
                    })
    
    return leadoffs

def deduplicate_and_rank(times_list):
    """Deduplicate by swimmer (keep fastest) and sort by time"""
    # Group by swimmer name
    best_times = {}
    for entry in times_list:
        name = entry['name']
        if name not in best_times or entry['time'] < best_times[name]['time']:
            best_times[name] = entry
    
    # Sort by time
    sorted_times = sorted(best_times.values(), key=lambda x: x['time'])
    return sorted_times

def main():
    print("Loading all relay splits...")
    
    # Load from individual year files
    splits_dir = Path("data/historical_splits")
    all_splits = {'boys': [], 'girls': []}
    
    for year_file in splits_dir.glob("splits_*.json"):
        with open(year_file, 'r') as f:
            year_data = json.load(f)
            for gender in ['boys', 'girls']:
                if gender in year_data:
                    all_splits[gender].extend(year_data[gender])
    
    print(f"  Loaded {len(all_splits['boys'])} boys relays")
    print(f"  Loaded {len(all_splits['girls'])} girls relays")
    
    # Classify relays
    print("\nClassifying relays...")
    counts = defaultdict(int)
    for gender in ['boys', 'girls']:
        for relay in all_splits[gender]:
            relay_type = classify_relay(relay)
            counts[f"{gender}_{relay_type}"] += 1
    
    for key, count in sorted(counts.items()):
        print(f"  {key}: {count}")
    
    # Extract leadoff times
    print("\nExtracting leadoff times...")
    leadoffs = extract_leadoff_times(all_splits)
    
    for gender in ['boys', 'girls']:
        print(f"\n{gender.upper()}:")
        for event in ['50_free', '100_free']:
            times = leadoffs[gender][event]
            print(f"  {event}: {len(times)} raw entries")
            
            # Deduplicate
            unique_times = deduplicate_and_rank(times)
            print(f"  {event}: {len(unique_times)} unique swimmers")
            
            # Show top 10
            print(f"  Top 10 {event.replace('_', ' ').title()} from leadoffs:")
            for i, entry in enumerate(unique_times[:10], 1):
                print(f"    {i}. {entry['time_str']} {entry['name']} ({entry['grade']}) - {entry['from_relay']} [{entry['year']}]")
    
    # Save extracted times
    output_file = Path("data/relay_leadoff_times.json")
    
    output_data = {
        'boys': {
            '50_free': deduplicate_and_rank(leadoffs['boys']['50_free']),
            '100_free': deduplicate_and_rank(leadoffs['boys']['100_free'])
        },
        'girls': {
            '50_free': deduplicate_and_rank(leadoffs['girls']['50_free']),
            '100_free': deduplicate_and_rank(leadoffs['girls']['100_free'])
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Saved leadoff times to {output_file}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY: Unique leadoff times extracted")
    print("="*60)
    for gender in ['boys', 'girls']:
        print(f"\n{gender.upper()}:")
        for event in ['50_free', '100_free']:
            count = len(output_data[gender][event])
            print(f"  {event.replace('_', ' ').title()}: {count} swimmers")

if __name__ == "__main__":
    main()

