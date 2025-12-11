#!/usr/bin/env python3
"""
Update relay records in index.html with splits harvested from MaxPreps.
This script:
1. Reads the harvested relay splits from JSON files
2. Matches them to specific relay records in the 2025 Records Broken section
3. Updates the HTML with splits where available
"""

import json
import re
from pathlib import Path

# Load harvested splits
def load_splits():
    boys_file = Path("data/relay_splits_2025-26_boys.json")
    girls_file = Path("data/relay_splits_2025-26_girls.json")
    
    boys_splits = []
    girls_splits = []
    
    if boys_file.exists():
        with open(boys_file, 'r') as f:
            boys_splits = json.load(f)
    
    if girls_file.exists():
        with open(girls_file, 'r') as f:
            girls_splits = json.load(f)
    
    return boys_splits, girls_splits

def clean_name(name):
    """Remove grade suffix from name like 'Kent Olsson - Fr.'"""
    if ' - ' in name:
        return name.split(' - ')[0].strip()
    return name.strip()

def get_last_name(name):
    """Get last name from full name"""
    cleaned = clean_name(name)
    return cleaned.split()[-1]

def match_relay_to_splits(record_swimmers, splits_data):
    """
    Try to match a relay record to splits data.
    record_swimmers: list of swimmer names from the record
    splits_data: list of splits dictionaries from harvested data
    """
    record_last_names = set([s.split()[-1] for s in record_swimmers])
    
    for splits in splits_data:
        splits_last_names = set([get_last_name(s) for s in splits.get('swimmers', [])])
        
        # Check if the last names match (same swimmers)
        if record_last_names == splits_last_names:
            return splits
    
    return None

# Define our target relays with swimmer info
TARGET_RELAYS = {
    # Boys 200 Medley Relay - NEW (1:41.80 Oct 24, 2025)
    'boys_200_medley_new': {
        'swimmers': ['Kent Olsson', 'Wade Olsson', 'Jackson Eftekhar', 'Zachary Duerkop'],
        'strokes': ['Backstroke', 'Breaststroke', 'Butterfly', 'Freestyle'],
        'type': 'medley',
        'time': '1:41.80'
    },
    # Boys 200 Medley Relay - OLD (1:45.73 Oct 25, 2024)  
    'boys_200_medley_old': {
        'swimmers': ['Wade Olsson', 'Zachary Duerkop', 'Jackson Eftekhar', 'Jackson Machamer'],
        'strokes': ['Backstroke', 'Breaststroke', 'Butterfly', 'Freestyle'],
        'type': 'medley',
        'time': '1:45.73'
    },
    # Boys 200 Free Relay - NEW (1:30.45 Nov 8, 2025)
    'boys_200_free_new': {
        'swimmers': ['Wade Olsson', 'Jackson Eftekhar', 'Grayson The', 'Zachary Duerkop'],
        'strokes': ['Freestyle', 'Freestyle', 'Freestyle', 'Freestyle'],
        'type': 'free',
        'time': '1:30.45'
    },
    # Boys 400 Free Relay - NEW (3:20.60 Oct 18, 2025)
    'boys_400_free_new': {
        'swimmers': ['Wade Olsson', 'Jackson Eftekhar', 'Grayson The', 'Zachary Duerkop'],
        'strokes': ['Freestyle', 'Freestyle', 'Freestyle', 'Freestyle'],
        'type': 'free',
        'time': '3:20.60'
    },
    # Girls 200 Medley Relay - NEW (2:00.57 Nov 8, 2025)
    'girls_200_medley_new': {
        'swimmers': ['Logan Sulger', 'Adrianna Witte', 'Hadley Cusson', 'Isla Cerepak'],
        'strokes': ['Backstroke', 'Breaststroke', 'Butterfly', 'Freestyle'],
        'type': 'medley',
        'time': '2:00.57'
    },
}

def find_best_matching_splits(boys_splits, girls_splits):
    """Find splits that match our target relays"""
    matches = {}
    
    for relay_key, relay_info in TARGET_RELAYS.items():
        gender = 'girls' if relay_key.startswith('girls') else 'boys'
        splits_data = girls_splits if gender == 'girls' else boys_splits
        
        # Filter by type
        relay_type = relay_info['type']
        type_splits = [s for s in splits_data if s.get('type') == relay_type]
        
        # Try to match
        match = match_relay_to_splits(relay_info['swimmers'], type_splits)
        
        if match:
            matches[relay_key] = match
            print(f"✓ Found splits for {relay_key}")
        else:
            print(f"✗ No splits found for {relay_key}")
    
    return matches

def format_splits_for_display(splits_data, strokes):
    """Format splits data for display in HTML"""
    swimmers = splits_data.get('swimmers', [])
    times = splits_data.get('splits', [])
    legs = splits_data.get('legs', strokes)  # Use strokes from our data if not in splits
    
    formatted = []
    for i, (swimmer, time) in enumerate(zip(swimmers, times)):
        name = clean_name(swimmer)
        stroke = legs[i] if i < len(legs) else strokes[i] if i < len(strokes) else 'Freestyle'
        
        # Clean up stroke names
        if stroke in ['Back', 'Split 1']:
            stroke = 'Backstroke'
        elif stroke in ['Breast', 'Split 2']:
            stroke = 'Breaststroke'
        elif stroke in ['Fly', 'Split 3']:
            stroke = 'Butterfly'
        elif stroke in ['Free', 'Split 4']:
            stroke = 'Freestyle'
        
        # Clean up time format (remove leading "00:")
        if time.startswith('00:'):
            time = time[3:]
        
        formatted.append({
            'name': name,
            'stroke': stroke,
            'split': time
        })
    
    return formatted

def main():
    boys_splits, girls_splits = load_splits()
    
    print(f"Loaded {len(boys_splits)} boys relay splits")
    print(f"Loaded {len(girls_splits)} girls relay splits")
    print()
    
    # Find matches
    matches = find_best_matching_splits(boys_splits, girls_splits)
    
    print(f"\nFound {len(matches)} matching splits")
    
    # Display the splits we found
    for relay_key, splits in matches.items():
        relay_info = TARGET_RELAYS[relay_key]
        formatted = format_splits_for_display(splits, relay_info['strokes'])
        
        print(f"\n{relay_key} ({relay_info['time']}):")
        for swimmer in formatted:
            print(f"  {swimmer['name']} ({swimmer['stroke']}): {swimmer['split']}")
    
    # Save formatted matches for use in rebuilding HTML
    output = {
        key: {
            'target': TARGET_RELAYS[key],
            'splits': format_splits_for_display(splits, TARGET_RELAYS[key]['strokes'])
        }
        for key, splits in matches.items()
    }
    
    output_file = Path("data/matched_relay_splits.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved matched splits to {output_file}")

if __name__ == "__main__":
    main()

