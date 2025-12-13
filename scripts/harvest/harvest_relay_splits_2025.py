#!/usr/bin/env python3
"""
Harvest relay splits from MaxPreps stats page for 2025-26 season
The splits are embedded in JavaScript onclick handlers: ShowMedleySplitWindow()
"""

import re
import json
from urllib.request import urlopen
from pathlib import Path

def extract_relay_splits_from_stats_page(gender="boys"):
    """
    Extract relay split data from MaxPreps stats page
    """
    
    if gender == "boys":
        url = "https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/stats/"
    else:
        url = "https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/girls-stats/"
    
    print(f"Fetching {gender} {url}")
    with urlopen(url) as response:
        html = response.read().decode('utf-8')
    
    # Pattern to find ShowMedleySplitWindow or ShowFreeSplitWindow calls
    # ShowMedleySplitWindow(['Back','Breast','Fly','Free'],['Name1','Name2','Name3','Name4'],['25.3','28.1','24.8','23.6'],'Team Name')
    medley_pattern = r"ShowMedleySplitWindow\(\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],'([^']+)'\)"
    free_pattern = r"ShowFreeSplitWindow\(\[([^\]]+)\],\[([^\]]+)\],'([^']+)'\)"
    
    relays = []
    
    # Find all relay tables (200 Medley Relay, 200 Free Relay, 400 Free Relay)
    # Look for table rows with "Relay Team" and extract split data
    
    # Search for onclick handlers with split data
    medley_matches = re.findall(medley_pattern, html)
    free_matches = re.findall(free_pattern, html)
    
    print(f"\nFound {len(medley_matches)} medley relay splits")
    print(f"Found {len(free_matches)} free relay splits")
    
    # Parse medley relay splits
    for match in medley_matches:
        legs_str, names_str, times_str, team = match
        
        # Parse arrays
        legs = [leg.strip().strip("'\"") for leg in legs_str.split(',')]
        names = [name.strip().strip("'\"") for name in names_str.split(',')]
        times = [time.strip().strip("'\"") for time in times_str.split(',')]
        
        relay_data = {
            "type": "medley",
            "legs": legs,
            "swimmers": names,
            "splits": times,
            "team": team
        }
        relays.append(relay_data)
        
        print(f"\nMedley Relay:")
        for i, (leg, name, time) in enumerate(zip(legs, names, times), 1):
            print(f"  {i}. {name} ({leg}): {time}")
    
    # Parse free relay splits
    for match in free_matches:
        names_str, times_str, team = match
        
        names = [name.strip().strip("'\"") for name in names_str.split(',')]
        times = [time.strip().strip("'\"") for time in times_str.split(',')]
        
        relay_data = {
            "type": "free",
            "swimmers": names,
            "splits": times,
            "team": team
        }
        relays.append(relay_data)
        
        print(f"\nFree Relay:")
        for i, (name, time) in enumerate(zip(names, times), 1):
            print(f"  {i}. {name}: {time}")
    
    # Save to file
    output_file = Path(f"data/relay_splits_2025-26_{gender}.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(relays, f, indent=2)
    
    print(f"\nSaved {len(relays)} relay splits to {output_file}")
    return relays

if __name__ == "__main__":
    boys_relays = extract_relay_splits_from_stats_page("boys")
    girls_relays = extract_relay_splits_from_stats_page("girls")
    
    # Combine and save all
    all_relays = {
        "boys": boys_relays,
        "girls": girls_relays
    }
    
    output_file = Path("data/relay_splits_2025-26_all.json")
    with open(output_file, 'w') as f:
        json.dump(all_relays, f, indent=2)
    
    print(f"\nSaved combined splits to {output_file}")

