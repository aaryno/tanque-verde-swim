#!/usr/bin/env python3
"""
Enrich relay leadoff times with actual date and meet information
by cross-referencing with relay records files.
"""

import json
import re
from pathlib import Path

def load_aliases():
    with open('data/swimmer_aliases.json', 'r') as f:
        return json.load(f)

def normalize_name(name, aliases):
    return aliases.get(name, name)

def parse_relay_records(filepath, aliases):
    """Parse relay records markdown file to get actual dates/meets"""
    relays = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find 200 Free Relay section
    fr200_match = re.search(r'## 200 Free Relay\s*\n\n?\|[^\n]+\n\|[-:\s|]+\n((?:\|[^\n]+\n)+)', content)
    if fr200_match:
        for row in fr200_match.group(1).strip().split('\n'):
            cells = [c.strip().replace('**', '') for c in row.split('|')[1:-1]]
            if len(cells) >= 5:
                time_str = cells[1].strip()
                participants = cells[2].strip()
                date = cells[3].strip()
                meet = cells[4].strip()
                
                # Get first swimmer (leadoff)
                swimmers = [s.strip() for s in participants.split(',')]
                if swimmers:
                    leadoff = normalize_name(swimmers[0], aliases)
                    relays.append({
                        'type': '200FR',
                        'event': '50_free',
                        'leadoff': leadoff,
                        'relay_time': time_str,
                        'date': date,
                        'meet': meet
                    })
    
    # Find 400 Free Relay section
    fr400_match = re.search(r'## 400 Free Relay\s*\n\n?\|[^\n]+\n\|[-:\s|]+\n((?:\|[^\n]+\n)+)', content)
    if fr400_match:
        for row in fr400_match.group(1).strip().split('\n'):
            cells = [c.strip().replace('**', '') for c in row.split('|')[1:-1]]
            if len(cells) >= 5:
                time_str = cells[1].strip()
                participants = cells[2].strip()
                date = cells[3].strip()
                meet = cells[4].strip()
                
                swimmers = [s.strip() for s in participants.split(',')]
                if swimmers:
                    leadoff = normalize_name(swimmers[0], aliases)
                    relays.append({
                        'type': '400FR',
                        'event': '100_free',
                        'leadoff': leadoff,
                        'relay_time': time_str,
                        'date': date,
                        'meet': meet
                    })
    
    return relays

def match_leadoff_to_relay(leadoff, relays, event_type):
    """Find the best matching relay for a leadoff time"""
    
    # Filter relays by event type
    matching_relays = [r for r in relays if r['event'] == event_type and r['leadoff'] == leadoff['name']]
    
    if not matching_relays:
        return None
    
    # Return the first match (could improve to match by time if needed)
    return matching_relays[0]

def main():
    aliases = load_aliases()
    
    # Load leadoff times
    with open('data/relay_leadoff_times.json', 'r') as f:
        leadoffs = json.load(f)
    
    # Parse relay records
    boys_relays = parse_relay_records('records/relay-records-boys.md', aliases)
    girls_relays = parse_relay_records('records/relay-records-girls.md', aliases)
    
    print(f"Loaded {len(boys_relays)} boys relay records")
    print(f"Loaded {len(girls_relays)} girls relay records")
    
    # Enrich leadoff times with actual date/meet
    enriched = {'boys': {'50_free': [], '100_free': []}, 
                'girls': {'50_free': [], '100_free': []}}
    
    for gender in ['boys', 'girls']:
        relays = boys_relays if gender == 'boys' else girls_relays
        
        for event in ['50_free', '100_free']:
            for leadoff in leadoffs[gender][event]:
                match = match_leadoff_to_relay(leadoff, relays, event)
                
                if match:
                    leadoff['date'] = match['date']
                    leadoff['meet'] = match['meet']
                    leadoff['relay_time'] = match['relay_time']
                else:
                    # Keep original format if no match found
                    year = leadoff.get('year', '')
                    if year and len(year) == 5:
                        leadoff['date'] = f"20{year[:2]}-{year[3:]}"
                    leadoff['meet'] = f"{leadoff['from_relay']} Relay Leadoff"
                
                enriched[gender][event].append(leadoff)
    
    # Save enriched data
    with open('data/relay_leadoff_times.json', 'w') as f:
        json.dump(enriched, f, indent=2)
    
    # Show results
    print("\nEnriched leadoff times:")
    for gender in ['boys', 'girls']:
        print(f"\n{gender.upper()}:")
        for event in ['50_free', '100_free']:
            print(f"  {event}:")
            for entry in enriched[gender][event][:5]:
                print(f"    {entry['time_str']} {entry['name']} - {entry['date']} @ {entry['meet'][:40]}...")
    
    print("\n✓ Saved enriched leadoff times to data/relay_leadoff_times.json")

if __name__ == "__main__":
    main()

