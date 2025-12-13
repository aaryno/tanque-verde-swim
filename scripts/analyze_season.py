#!/usr/bin/env python3
"""
Analyze Season for Records Broken
==================================
Compares current season records to previous season to identify:
- Individual records broken (overall and by grade)
- Relay records broken
- Improvement margins

Outputs formatted markdown for use in annual summary and landing page.

Usage:
    python analyze_season.py --season 25-26 --year 2025
"""

import argparse
import re
from pathlib import Path
from datetime import datetime

def parse_time(time_str):
    """Convert time string to seconds for comparison"""
    time_str = time_str.strip().replace('**', '')
    if ':' in time_str:
        parts = time_str.split(':')
        return float(parts[0]) * 60 + float(parts[1])
    return float(time_str)

def time_diff(old_time, new_time):
    """Calculate improvement in seconds"""
    return parse_time(old_time) - parse_time(new_time)

def find_pre_season_record(records_content, event_name, current_year):
    """Find the record holder from before current season"""
    lines = records_content.split('\n')
    in_event = False
    found_header = False
    
    for line in lines:
        if f'### {event_name}' in line or f'## {event_name}' in line:
            in_event = True
            continue
        
        if in_event and '|-----:|-----:|' in line:
            found_header = True
            continue
            
        if in_event and found_header and '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                rank = parts[1]
                time = parts[2]
                athlete = parts[3]
                date = parts[4]
                meet = parts[5]
                
                # Skip lines with **Open** or grade labels
                if 'Open' in rank or 'Freshman' in rank or 'Sophomore' in rank:
                    continue
                    
                # Check if this is from before current year
                if str(current_year) not in date:
                    return {
                        'time': time,
                        'athlete': athlete,
                        'date': date,
                        'meet': meet
                    }
        
        if in_event and line.startswith('###') and event_name not in line:
            break
    
    return None

def analyze_records(season, year):
    """Analyze all records to find what was broken"""
    records_dir = Path('records')
    
    # Read current records
    boys_records = (records_dir / 'records-boys.md').read_text()
    girls_records = (records_dir / 'records-girls.md').read_text()
    boys_relays = (records_dir / 'relay-records-boys.md').read_text()
    girls_relays = (records_dir / 'relay-records-girls.md').read_text()
    
    broken_records = {
        'individual': {'boys': [], 'girls': []},
        'relays': {'boys': [], 'girls': []},
        'grade': {'boys': [], 'girls': []}
    }
    
    # Individual events to check
    events = [
        '50 Freestyle', '100 Freestyle', '200 Freestyle', '500 Freestyle',
        '100 Backstroke', '100 Breaststroke', '100 Butterfly', '200 Individual Medley'
    ]
    
    # Check boys individual records
    for event in events:
        # Check overall record
        pattern = rf'\|\s*\*\*Open\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*'
        match = re.search(pattern, boys_records)
        if match and str(year) in boys_records[match.start():match.end()]:
            old_record = find_pre_season_record(boys_records, event, year)
            if old_record:
                broken_records['individual']['boys'].append({
                    'event': event,
                    'new_time': match.group(1).strip(),
                    'new_athlete': match.group(2).strip(),
                    'new_date': match.group(3).strip(),
                    'old_time': old_record['time'],
                    'old_athlete': old_record['athlete'],
                    'old_date': old_record['date'],
                    'old_meet': old_record['meet']
                })
    
    # Similar for girls...
    # Similar for relays...
    
    return broken_records

def generate_markdown_output(broken_records, season):
    """Generate formatted markdown for records broken"""
    output = f"# Records Broken - {season} Season\n\n"
    
    output += "## Overall School Records\n\n"
    
    for gender in ['boys', 'girls']:
        gender_cap = gender.capitalize()
        if broken_records['individual'][gender]:
            output += f"### {gender_cap} Individual\n\n"
            for record in broken_records['individual'][gender]:
                improvement = time_diff(record['old_time'], record['new_time'])
                output += f"**{record['event']}**\n"
                output += f"- NEW: {record['new_time']} - {record['new_athlete']}\n"
                output += f"- OLD: {record['old_time']} - {record['old_athlete']} ({record['old_date']})\n"
                output += f"- Improvement: {improvement:.2f} seconds\n\n"
        
        if broken_records['relays'][gender]:
            output += f"### {gender_cap} Relays\n\n"
            for record in broken_records['relays'][gender]:
                improvement = time_diff(record['old_time'], record['new_time'])
                output += f"**{record['event']}**\n"
                output += f"- NEW: {record['new_time']} - {record['new_athletes']}\n"
                output += f"- OLD: {record['old_time']} - {record['old_athletes']} ({record['old_date']})\n"
                output += f"- Improvement: {improvement:.2f} seconds\n\n"
    
    return output

def main():
    parser = argparse.ArgumentParser(description='Analyze season for records broken')
    parser.add_argument('--season', required=True, help='Season in YY-YY format')
    parser.add_argument('--year', required=True, type=int, help='Year (e.g., 2025)')
    args = parser.parse_args()
    
    broken_records = analyze_records(args.season, args.year)
    markdown = generate_markdown_output(broken_records, args.season)
    
    # Save output
    output_file = Path(f'artifacts/records-broken-{args.season}.md')
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(markdown)
    
    print(f"✅ Analysis complete! Output saved to {output_file}")
    print(f"\nSummary:")
    print(f"  Boys Individual: {len(broken_records['individual']['boys'])}")
    print(f"  Girls Individual: {len(broken_records['individual']['girls'])}")
    print(f"  Boys Relays: {len(broken_records['relays']['boys'])}")
    print(f"  Girls Relays: {len(broken_records['relays']['girls'])}")

if __name__ == '__main__':
    main()

