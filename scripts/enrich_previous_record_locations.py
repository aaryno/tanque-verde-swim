#!/usr/bin/env python3
"""
Enrich previous record entries with meet locations.
This script looks up the meet location for previous records by finding
the matching entry in the class_records_history.json file.
"""

import json
from pathlib import Path


def enrich_class_records_history():
    """Add meet locations to previous record entries in class_records_history.json"""
    
    history_file = Path('data/class_records_history.json')
    if not history_file.exists():
        print(f"Error: {history_file} not found")
        return
    
    with open(history_file, 'r') as f:
        records = json.load(f)
    
    # Build a lookup index: (gender, event, grade, time, name) -> record
    record_index = {}
    for record in records:
        key = (
            record.get('gender', ''),
            record.get('event', ''),
            record.get('grade', ''),
            record.get('time', ''),
            record.get('name', '')
        )
        record_index[key] = record
    
    # Also build a looser index by just time and name for cross-grade lookups
    time_name_index = {}
    for record in records:
        key = (
            record.get('gender', ''),
            record.get('event', ''),
            record.get('time', ''),
            record.get('name', '')
        )
        if key not in time_name_index:
            time_name_index[key] = record
    
    # Enrich previous records
    updated_count = 0
    for record in records:
        prev = record.get('previous')
        if prev and isinstance(prev, dict) and 'meet' not in prev:
            prev_time = prev.get('time', '')
            prev_name = prev.get('name', '')
            prev_season = prev.get('season', '')
            gender = record.get('gender', '')
            event = record.get('event', '')
            grade = record.get('grade', '')
            
            # Try to find the previous record entry
            # First, try exact match with same grade
            key = (gender, event, grade, prev_time, prev_name)
            prev_record = record_index.get(key)
            
            # If not found, try looser match
            if not prev_record:
                key = (gender, event, prev_time, prev_name)
                prev_record = time_name_index.get(key)
            
            # Verify the season matches if we found a record
            if prev_record and prev_record.get('season') == prev_season:
                prev_meet = prev_record.get('meet', '')
                if prev_meet:
                    prev['meet'] = prev_meet
                    updated_count += 1
                    print(f"  ✓ Added meet for {gender} {grade} {event}: {prev_name} at {prev_meet}")
    
    # Write back
    with open(history_file, 'w') as f:
        json.dump(records, f, indent=2)
    
    print(f"\nUpdated {updated_count} previous record entries with meet locations")


def main():
    print("=" * 60)
    print("Enriching Previous Record Locations")
    print("=" * 60)
    
    print("\n📋 Processing class_records_history.json...")
    enrich_class_records_history()
    
    print("\n✅ Done!")


if __name__ == '__main__':
    main()
