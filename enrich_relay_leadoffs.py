#!/usr/bin/env python3
"""
Enrich relay_leadoff_times.json with actual meet names and dates
by matching split totals to harvested relay data.
"""

import json
from pathlib import Path
from datetime import datetime


def parse_time_to_seconds(time_str):
    """Convert time string to total seconds"""
    time_str = str(time_str).strip()
    if ':' in time_str:
        # Format: MM:SS.ss or HH:MM:SS.ss
        parts = time_str.split(':')
        if len(parts) == 2:
            mins, secs = parts
            return float(mins) * 60 + float(secs)
        elif len(parts) == 3:
            hours, mins, secs = parts
            return float(hours) * 3600 + float(mins) * 60 + float(secs)
    return float(time_str)


def format_date(date_str):
    """Convert date from various formats to 'Mon DD, YYYY' format"""
    if not date_str or date_str == '—':
        return None
    
    # Try various formats
    formats = [
        '%m/%d/%Y',   # 10/29/2016
        '%Y-%m-%d',   # 2016-10-29
        '%b %d, %Y',  # Oct 29, 2016
        '%B %d, %Y',  # October 29, 2016
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%b %d, %Y')
        except ValueError:
            continue
    return None


def clean_meet_name(meet):
    """Clean up meet name for consistency"""
    if not meet:
        return meet
    # Remove "Multi Teams @" prefix
    if meet.startswith('Multi Teams @ '):
        meet = meet[14:]
    # Remove location suffix in parentheses if it's just the city
    if '(Tucson, AZ)' in meet:
        meet = meet.replace(' (Tucson, AZ)', '')
    if '(Mesa, AZ)' in meet:
        meet = meet.replace(' (Mesa, AZ)', '')
    if '(AZ)' in meet:
        meet = meet.replace(' (AZ)', '')
    return meet.strip()


def load_harvested_relays():
    """Load all harvested relay data with meet information"""
    all_relays = []
    
    # Load from tvhs harvested_relays
    paths = [
        Path('/Users/aaryn/workspaces/swimming/tvhs/harvested_relays/all_relays.json'),
        Path('/Users/aaryn/workspaces/swimming/tvhs/harvested_relays/all_relays_v2.json'),
    ]
    
    for p in paths:
        if p.exists():
            try:
                with open(p) as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for gender, relays in data.items():
                            if isinstance(relays, list):
                                for relay in relays:
                                    relay['_source'] = p.name
                                    all_relays.append(relay)
                    elif isinstance(data, list):
                        all_relays.extend(data)
            except Exception as e:
                print(f"  Warning: Could not load {p}: {e}")
    
    return all_relays


def load_historical_splits():
    """Load all historical splits with calculated totals"""
    splits_data = []
    splits_dir = Path('/Users/aaryn/workspaces/swimming/tanque-verde-swim/data/historical_splits')
    
    for filepath in splits_dir.glob('splits_*.json'):
        try:
            with open(filepath) as f:
                data = json.load(f)
                for gender in ['boys', 'girls']:
                    if gender in data:
                        for relay in data[gender]:
                            # Calculate total time from splits
                            total_secs = 0
                            for split in relay.get('splits', []):
                                try:
                                    total_secs += parse_time_to_seconds(split)
                                except:
                                    pass
                            relay['_total_seconds'] = total_secs
                            relay['_source'] = filepath.name
                            relay['_gender'] = gender
                            splits_data.append(relay)
        except Exception as e:
            print(f"  Warning: Could not load {filepath}: {e}")
    
    return splits_data


def find_matching_relay(leadoff_entry, harvested_relays, historical_splits):
    """Try to find matching relay with meet info"""
    swimmer = leadoff_entry.get('name', '')
    split_time = leadoff_entry.get('time', 0)
    year = leadoff_entry.get('year', '')
    from_relay = leadoff_entry.get('from_relay', '')
    
    # Map relay type
    relay_type_map = {
        '200FR': '200 Free Relay',
        '400FR': '400 Free Relay',
        '200MR': '200 Medley Relay',
    }
    expected_relay_type = relay_type_map.get(from_relay, from_relay)
    
    # First, find in historical splits
    for split_data in historical_splits:
        if split_data.get('year') != year:
            continue
        
        splits = split_data.get('splits', [])
        swimmers = split_data.get('swimmers', [])
        
        if not splits or not swimmers:
            continue
        
                # Check if first split matches (leadoff)
        try:
            first_split = parse_time_to_seconds(splits[0])
            if abs(first_split - split_time) < 0.01:
                # Check if swimmer name matches first swimmer (use last name matching)
                first_swimmer = swimmers[0].split(' - ')[0] if ' - ' in swimmers[0] else swimmers[0]
                swimmer_last = swimmer.split()[-1].lower() if swimmer else ''
                first_swimmer_last = first_swimmer.split()[-1].lower() if first_swimmer else ''
                names_match = (swimmer.lower() in first_swimmer.lower() or 
                               first_swimmer.lower() in swimmer.lower() or
                               swimmer_last == first_swimmer_last)
                if names_match:
                    # Found a match in historical splits, now find the meet
                    total_time = split_data.get('_total_seconds', 0)
                    
                    # Search harvested relays for matching total time
                    season = year if '-' in year else f"20{year}" if len(year) == 2 else year
                    for relay in harvested_relays:
                        relay_season = relay.get('season', '')
                        if relay_season != year and not relay_season.endswith(year):
                            continue
                        
                        try:
                            relay_time = parse_time_to_seconds(relay.get('time', '0'))
                            if abs(relay_time - total_time) < 0.5:  # Within 0.5 sec
                                # Check swimmers match (use last name matching)
                                relay_swimmers = relay.get('swimmers', [])
                                if relay_swimmers:
                                    first_relay_swimmer = relay_swimmers[0].split(' - ')[0] if ' - ' in relay_swimmers[0] else relay_swimmers[0]
                                    first_relay_last = first_relay_swimmer.split()[-1].lower() if first_relay_swimmer else ''
                                    relay_names_match = (swimmer.lower() in first_relay_swimmer.lower() or 
                                                         first_relay_swimmer.lower() in swimmer.lower() or
                                                         swimmer_last == first_relay_last)
                                    if relay_names_match:
                                        return {
                                            'date': format_date(relay.get('date', '')),
                                            'meet': clean_meet_name(relay.get('meet', '')),
                                            'relay_time': relay.get('time', ''),
                                            'match_type': 'exact_split_match'
                                        }
                        except:
                            pass
        except:
            pass
    
    return None


def main():
    print("=" * 60)
    print("Enriching Relay Leadoff Times with Meet Information")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading data sources...")
    leadoff_path = Path('/Users/aaryn/workspaces/swimming/tanque-verde-swim/data/relay_leadoff_times.json')
    with open(leadoff_path) as f:
        leadoff_data = json.load(f)
    
    harvested = load_harvested_relays()
    print(f"   Loaded {len(harvested)} harvested relay records")
    
    splits = load_historical_splits()
    print(f"   Loaded {len(splits)} historical split records")
    
    # Process each gender
    updates = 0
    checked = 0
    
    for gender in ['boys', 'girls']:
        if gender not in leadoff_data:
            continue
        
        for event, entries in leadoff_data[gender].items():
            for entry in entries:
                current_meet = entry.get('meet', '')
                current_date = entry.get('date', '')
                
                # Check if this entry needs enrichment
                if 'Leadoff' in current_meet or current_date == entry.get('year', ''):
                    checked += 1
                    match = find_matching_relay(entry, harvested, splits)
                    
                    if match and match['date'] and match['meet']:
                        print(f"\n✅ Found match for {entry['name']} ({entry.get('year', '')})")
                        print(f"   Old: {current_date} / {current_meet}")
                        print(f"   New: {match['date']} / {match['meet']}")
                        
                        entry['date'] = match['date']
                        entry['meet'] = match['meet']
                        if match.get('relay_time'):
                            entry['relay_time'] = match['relay_time']
                        updates += 1
    
    print(f"\n" + "=" * 60)
    print(f"Checked {checked} entries needing enrichment")
    print(f"Updated {updates} entries with meet information")
    
    if updates > 0:
        # Save updated data
        with open(leadoff_path, 'w') as f:
            json.dump(leadoff_data, f, indent=2)
        print(f"✅ Saved to {leadoff_path}")
    else:
        print("ℹ️  No updates made - meet matching data may be incomplete")
        print("\nEntries that still need enrichment:")
        for gender in ['boys', 'girls']:
            if gender not in leadoff_data:
                continue
            for event, entries in leadoff_data[gender].items():
                for entry in entries:
                    if 'Leadoff' in entry.get('meet', ''):
                        print(f"   - {entry['name']} ({entry.get('year', '')}) {entry.get('time_str', '')} - {event}")


if __name__ == '__main__':
    main()
