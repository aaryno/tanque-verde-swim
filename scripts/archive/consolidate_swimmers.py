#!/usr/bin/env python3
"""
Interactive script to consolidate duplicate swimmers.

Prompts user to confirm duplicates and choose preferred name,
then merges CSV files and creates aliases mapping.
"""

import pandas as pd
from pathlib import Path
import json
import shutil
from detect_name_duplicates import find_potential_duplicates


def load_aliases(aliases_file: Path) -> dict:
    """Load existing aliases mapping"""
    if aliases_file.exists():
        with open(aliases_file, 'r') as f:
            return json.load(f)
    return {}


def save_aliases(aliases_file: Path, aliases: dict):
    """Save aliases mapping"""
    with open(aliases_file, 'w') as f:
        json.dump(aliases, f, indent=2)


def merge_swimmer_files(file1: Path, file2: Path, preferred_name: str, keep_file: Path) -> Path:
    """
    Merge two swimmer CSV files, using preferred name for all records.
    Returns path to the merged file.
    """
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Update names to preferred name
    df1['Name'] = preferred_name
    df2['Name'] = preferred_name
    
    # Combine
    df_merged = pd.concat([df1, df2], ignore_index=True)
    
    # Remove exact duplicates (same event, date, time)
    df_merged = df_merged.drop_duplicates(
        subset=['Event', 'SwimDate', 'SwimTime'], 
        keep='first'
    )
    
    # Sort by date
    df_merged = df_merged.sort_values('SwimDate')
    
    # Save to the kept file
    df_merged.to_csv(keep_file, index=False)
    
    return keep_file


def main():
    script_dir = Path(__file__).parent
    swimmers_dir = script_dir / "data" / "raw" / "swimmers"
    aliases_file = script_dir / "data" / "swimmer_aliases.json"
    
    print("\n🔄 Interactive Swimmer Consolidation\n")
    print("=" * 80)
    
    # Load existing aliases
    aliases = load_aliases(aliases_file)
    print(f"\n📂 Loaded {len(aliases)} existing aliases")
    
    # Find duplicates
    print("\n🔍 Scanning for duplicates...")
    duplicates = find_potential_duplicates(swimmers_dir)
    
    if not duplicates:
        print("\n✓ No duplicates found!")
        return
    
    print(f"📊 Found {len(duplicates)} potential duplicate(s)\n")
    
    merged_count = 0
    skipped_count = 0
    
    for i, dup in enumerate(duplicates, 1):
        s1 = dup['swimmer1']
        s2 = dup['swimmer2']
        
        print("\n" + "=" * 80)
        print(f"\n{i}/{len(duplicates)}. Potential Match ({dup['confidence']} confidence)\n")
        print(f"   [1] {s1['full_name']}")
        print(f"       File: {s1['file']}")
        print(f"       Gender: {s1['gender']}, Grades: {s1['grades']}, Swims: {s1['swim_count']}")
        print(f"\n   [2] {s2['full_name']}")
        print(f"       File: {s2['file']}")
        print(f"       Gender: {s2['gender']}, Grades: {s2['grades']}, Swims: {s2['swim_count']}")
        
        # Ask if same person
        print("\n❓ Are these the same person? (y/n/q to quit): ", end='')
        response = input().strip().lower()
        
        if response == 'q':
            print("\n⚠ Quitting early...")
            break
        
        if response != 'y':
            print("   ⊘ Skipped")
            skipped_count += 1
            continue
        
        # Ask which name to use
        print(f"\n❓ Which name should be displayed in records?")
        print(f"   [1] {s1['full_name']}")
        print(f"   [2] {s2['full_name']}")
        print(f"   [3] Custom name")
        print("\nChoice (1/2/3): ", end='')
        choice = input().strip()
        
        if choice == '1':
            preferred_name = s1['full_name']
            keep_file = swimmers_dir / s1['file']
            remove_file = swimmers_dir / s2['file']
        elif choice == '2':
            preferred_name = s2['full_name']
            keep_file = swimmers_dir / s2['file']
            remove_file = swimmers_dir / s1['file']
        elif choice == '3':
            print("Enter custom name: ", end='')
            preferred_name = input().strip()
            # Keep the file with more data
            if s1['swim_count'] >= s2['swim_count']:
                keep_file = swimmers_dir / s1['file']
                remove_file = swimmers_dir / s2['file']
            else:
                keep_file = swimmers_dir / s2['file']
                remove_file = swimmers_dir / s1['file']
        else:
            print("   ⚠ Invalid choice, skipping")
            skipped_count += 1
            continue
        
        # Merge files
        print(f"\n   🔄 Merging into {keep_file.name}...")
        try:
            merge_swimmer_files(
                swimmers_dir / s1['file'],
                swimmers_dir / s2['file'],
                preferred_name,
                keep_file
            )
            
            # Remove the other file
            if remove_file.exists() and remove_file != keep_file:
                remove_file.unlink()
                print(f"   🗑️  Removed {remove_file.name}")
            
            # Update aliases
            # Map all variations to preferred name
            aliases[s1['full_name']] = preferred_name
            aliases[s2['full_name']] = preferred_name
            
            print(f"   ✓ Merged as '{preferred_name}'")
            merged_count += 1
            
        except Exception as e:
            print(f"   ✗ Error merging: {e}")
            continue
    
    # Save aliases
    if merged_count > 0:
        save_aliases(aliases_file, aliases)
        print(f"\n💾 Saved aliases to {aliases_file}")
    
    print("\n" + "=" * 80)
    print(f"\n📊 Summary:")
    print(f"   ✓ Merged: {merged_count}")
    print(f"   ⊘ Skipped: {skipped_count}")
    
    if merged_count > 0:
        print(f"\n✓ Consolidation complete!")
        print(f"\nNext steps:")
        print(f"  1. Run generate_hs_records.py to update records")
        print(f"  2. Run swim-data-tool publish to publish")


if __name__ == "__main__":
    main()

