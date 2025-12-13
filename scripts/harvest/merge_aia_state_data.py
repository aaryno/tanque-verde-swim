#!/usr/bin/env python3
"""
Merge AIA State Championship data into existing swimmer CSV files

Matches AIA state meet swims with existing swimmer files and adds any
missing swims to create a complete historical record.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import re
import json


def normalize_name(name: str) -> str:
    """Normalize name for matching (lowercase, no spaces, no punctuation)"""
    return re.sub(r'[^a-z]', '', name.lower())


def find_swimmer_file(name: str, swimmers_dir: Path) -> Path | None:
    """Find the CSV file for a swimmer by name matching"""
    normalized_search = normalize_name(name)
    
    for csv_file in swimmers_dir.glob("*.csv"):
        # Check filename
        filename_normalized = normalize_name(csv_file.stem)
        if normalized_search in filename_normalized:
            return csv_file
        
        # Check Name column in file
        try:
            df = pd.read_csv(csv_file, nrows=1)
            if 'Name' in df.columns:
                file_name_normalized = normalize_name(df['Name'].iloc[0])
                if file_name_normalized == normalized_search:
                    return csv_file
        except:
            continue
    
    return None


def load_aliases(aliases_file: Path) -> dict:
    """Load swimmer name aliases"""
    if aliases_file.exists():
        with open(aliases_file, 'r') as f:
            return json.load(f)
    return {}


def apply_alias(name: str, aliases: dict) -> str:
    """Apply alias mapping to get preferred name"""
    return aliases.get(name, name)


def merge_aia_swims(aia_csv: Path, swimmers_dir: Path, aliases_file: Path) -> Dict:
    """
    Merge AIA state meet swims into swimmer CSV files
    
    Returns:
        Dict with statistics about the merge
    """
    print("🔄 Merging AIA State Meet Data\n")
    
    # Load aliases
    aliases = load_aliases(aliases_file)
    if aliases:
        print(f"📋 Loaded {len(aliases)} name aliases")
    
    # Load AIA state meet data
    aia_df = pd.read_csv(aia_csv)
    print(f"📂 Loaded {len(aia_df)} AIA state meet swims")
    
    # Apply aliases to normalize names
    aia_df['Name'] = aia_df['Name'].apply(lambda x: apply_alias(x, aliases))
    
    stats = {
        'swimmers_found': 0,
        'swimmers_not_found': 0,
        'swims_added': 0,
        'swims_already_exist': 0,
        'swimmers_processed': [],
        'swimmers_missing': [],
    }
    
    # Group by swimmer
    for swimmer_name, swimmer_swims in aia_df.groupby('Name'):
        print(f"\n👤 {swimmer_name}")
        
        # Find swimmer's CSV file
        swimmer_file = find_swimmer_file(swimmer_name, swimmers_dir)
        
        if not swimmer_file:
            print(f"  ⚠ No CSV file found - skipping")
            stats['swimmers_not_found'] += 1
            stats['swimmers_missing'].append(swimmer_name)
            continue
        
        print(f"  ✓ Found file: {swimmer_file.name}")
        stats['swimmers_found'] += 1
        stats['swimmers_processed'].append(swimmer_name)
        
        # Load swimmer's existing data
        df = pd.read_csv(swimmer_file)
        original_count = len(df)
        
        # Process each AIA swim
        swims_added = 0
        for _, aia_swim in swimmer_swims.iterrows():
            # Check if swim already exists (match on event, date, and time)
            exists = (
                (df['Event'] == aia_swim['Event']) &
                (df['SwimDate'] == aia_swim['SwimDate']) &
                (df['SwimTime'] == aia_swim['SwimTime'])
            ).any()
            
            if not exists:
                # Add new swim
                new_row = {
                    'swimmer_id': df['swimmer_id'].iloc[0] if 'swimmer_id' in df.columns else '',
                    'Name': swimmer_name,
                    'Gender': aia_swim['Gender'],
                    'Age': None,
                    'grade': aia_swim['grade'],
                    'Event': aia_swim['Event'],
                    'SwimTime': aia_swim['SwimTime'],
                    'SwimDate': aia_swim['SwimDate'],
                    'MeetName': aia_swim['MeetName'],
                    'round': 'Final',
                    'splits': aia_swim['splits'] if pd.notna(aia_swim['splits']) else '',
                    'Team': 'Tanque Verde (Tucson, AZ)',
                    'source': 'aia_pdf',
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                swims_added += 1
                stats['swims_added'] += 1
                print(f"  ✓ Added: {aia_swim['Event']} - {aia_swim['SwimTime']} ({aia_swim['year']})")
            else:
                stats['swims_already_exist'] += 1
        
        if swims_added > 0:
            # Save updated file
            df.to_csv(swimmer_file, index=False)
            print(f"  💾 Saved {swims_added} new swims (total: {original_count} → {len(df)})")
        else:
            print(f"  ⊘ All swims already exist")
    
    return stats


def main():
    script_dir = Path(__file__).parent
    aia_csv = script_dir / "data" / "raw" / "aia-state" / "tvhs-all-state-meets.csv"
    swimmers_dir = script_dir / "data" / "raw" / "swimmers"
    aliases_file = script_dir / "data" / "swimmer_aliases.json"
    
    if not aia_csv.exists():
        print(f"❌ AIA data not found: {aia_csv}")
        print("Run parse_aia_state_meets.py first!")
        return
    
    if not swimmers_dir.exists():
        print(f"❌ Swimmers directory not found: {swimmers_dir}")
        return
    
    print("=" * 80)
    stats = merge_aia_swims(aia_csv, swimmers_dir, aliases_file)
    print("\n" + "=" * 80)
    
    print(f"\n📊 Summary:")
    print(f"  ✓ Swimmers matched: {stats['swimmers_found']}")
    print(f"  ⚠ Swimmers not found: {stats['swimmers_not_found']}")
    print(f"  ✓ Swims added: {stats['swims_added']}")
    print(f"  ⊘ Swims already exist: {stats['swims_already_exist']}")
    
    if stats['swimmers_missing']:
        print(f"\n⚠ Swimmers without CSV files:")
        for name in stats['swimmers_missing']:
            print(f"  - {name}")
    
    print("\n✓ Merge complete!")


if __name__ == "__main__":
    main()

