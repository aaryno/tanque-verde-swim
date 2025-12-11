#!/usr/bin/env python3
"""
Harvest relay splits from MaxPreps for all seasons.
URLs follow the pattern:
- Boys: https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/{year}/stats/
- Girls: https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/girls/fall/{year}/stats/

Year slugs: 24-25, 23-24, 22-23, 21-22, 20-21, 19-20, etc.
"""

import re
import json
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from pathlib import Path

# Years to harvest (most recent first)
YEARS = [
    '25-26',  # Current season
    '24-25',
    '23-24',
    '22-23',
    '21-22',
    '20-21',
    '19-20',
    '18-19',
    '17-18',
    '16-17',
    '15-16',
    '14-15',
    '13-14',
    '12-13',
]

def get_url(gender, year):
    """Get MaxPreps stats URL for a given gender and year"""
    if gender == 'boys':
        return f"https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/{year}/stats/"
    else:
        return f"https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/girls/fall/{year}/stats/"

def fetch_page(url):
    """Fetch a page with error handling"""
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except HTTPError as e:
        print(f"  HTTP Error {e.code}: {url}")
        return None
    except URLError as e:
        print(f"  URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def extract_splits_from_html(html, year, gender):
    """Extract relay split data from MaxPreps stats page HTML"""
    
    # Pattern to find ShowMedleySplitWindow or ShowFreeSplitWindow calls
    medley_pattern = r"ShowMedleySplitWindow\(\[([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],'([^']+)'\)"
    free_pattern = r"ShowFreeSplitWindow\(\[([^\]]+)\],\[([^\]]+)\],'([^']+)'\)"
    
    relays = []
    
    # Find medley relay splits
    medley_matches = re.findall(medley_pattern, html)
    for match in medley_matches:
        legs_str, names_str, times_str, team = match
        
        legs = [leg.strip().strip("'\"") for leg in legs_str.split(',')]
        names = [name.strip().strip("'\"") for name in names_str.split(',')]
        times = [time.strip().strip("'\"") for time in times_str.split(',')]
        
        relays.append({
            "type": "medley",
            "year": year,
            "gender": gender,
            "legs": legs,
            "swimmers": names,
            "splits": times,
            "team": team
        })
    
    # Find free relay splits
    free_matches = re.findall(free_pattern, html)
    for match in free_matches:
        names_str, times_str, team = match
        
        names = [name.strip().strip("'\"") for name in names_str.split(',')]
        times = [time.strip().strip("'\"") for time in times_str.split(',')]
        
        relays.append({
            "type": "free",
            "year": year,
            "gender": gender,
            "swimmers": names,
            "splits": times,
            "team": team
        })
    
    return relays

def harvest_all_seasons():
    """Harvest relay splits from all seasons"""
    
    all_relays = {
        'boys': [],
        'girls': []
    }
    
    for year in YEARS:
        print(f"\n{'='*50}")
        print(f"Harvesting {year} season...")
        print('='*50)
        
        for gender in ['boys', 'girls']:
            url = get_url(gender, year)
            print(f"\n{gender.upper()}: {url}")
            
            html = fetch_page(url)
            
            if html:
                relays = extract_splits_from_html(html, year, gender)
                
                if relays:
                    all_relays[gender].extend(relays)
                    print(f"  Found {len(relays)} relay splits")
                    
                    # Show summary of what we found
                    medley_count = sum(1 for r in relays if r['type'] == 'medley')
                    free_count = sum(1 for r in relays if r['type'] == 'free')
                    print(f"    - {medley_count} medley relays")
                    print(f"    - {free_count} free relays")
                else:
                    print(f"  No relay splits found")
            else:
                print(f"  Failed to fetch page")
            
            # Be nice to the server
            time.sleep(0.5)
    
    return all_relays

def save_results(all_relays):
    """Save harvested relays to JSON files"""
    
    output_dir = Path("data/historical_splits")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save combined
    with open(output_dir / "all_relay_splits.json", 'w') as f:
        json.dump(all_relays, f, indent=2)
    
    # Save by gender
    for gender in ['boys', 'girls']:
        with open(output_dir / f"{gender}_relay_splits.json", 'w') as f:
            json.dump(all_relays[gender], f, indent=2)
    
    # Save by year
    by_year = {}
    for gender in ['boys', 'girls']:
        for relay in all_relays[gender]:
            year = relay['year']
            if year not in by_year:
                by_year[year] = {'boys': [], 'girls': []}
            by_year[year][gender].append(relay)
    
    for year, data in by_year.items():
        with open(output_dir / f"splits_{year}.json", 'w') as f:
            json.dump(data, f, indent=2)
    
    print(f"\nSaved results to {output_dir}/")

def print_summary(all_relays):
    """Print a summary of harvested data"""
    
    print("\n" + "="*60)
    print("HARVEST SUMMARY")
    print("="*60)
    
    total_boys = len(all_relays['boys'])
    total_girls = len(all_relays['girls'])
    
    print(f"\nTotal relays harvested: {total_boys + total_girls}")
    print(f"  Boys: {total_boys}")
    print(f"  Girls: {total_girls}")
    
    # By year
    print("\nBy Year:")
    years_data = {}
    for gender in ['boys', 'girls']:
        for relay in all_relays[gender]:
            year = relay['year']
            if year not in years_data:
                years_data[year] = {'boys': 0, 'girls': 0}
            years_data[year][gender] += 1
    
    for year in sorted(years_data.keys(), reverse=True):
        data = years_data[year]
        print(f"  {year}: Boys={data['boys']}, Girls={data['girls']}")

def main():
    print("MaxPreps Relay Splits Harvester")
    print("================================")
    print(f"Harvesting {len(YEARS)} seasons: {', '.join(YEARS)}")
    
    all_relays = harvest_all_seasons()
    
    print_summary(all_relays)
    
    save_results(all_relays)
    
    print("\n✓ Harvest complete!")

if __name__ == "__main__":
    main()

