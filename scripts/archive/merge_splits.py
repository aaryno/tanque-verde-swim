#!/usr/bin/env python3
"""
Merge all individual season split files into all_relay_splits.json
"""

import json
from pathlib import Path

def main():
    splits_dir = Path('data/historical_splits')
    
    # Collect all splits from individual season files
    all_boys = []
    all_girls = []
    
    # Process each season file
    season_files = sorted(splits_dir.glob('splits_*.json'))
    
    print("Merging relay splits from individual season files...")
    for filepath in season_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            boys_count = len(data.get('boys', []))
            girls_count = len(data.get('girls', []))
            
            all_boys.extend(data.get('boys', []))
            all_girls.extend(data.get('girls', []))
            
            print(f"  {filepath.name}: {boys_count} boys, {girls_count} girls")
        except Exception as e:
            print(f"  Error loading {filepath.name}: {e}")
    
    # Create merged data
    merged = {
        'boys': all_boys,
        'girls': all_girls
    }
    
    # Write to all_relay_splits.json
    output_path = splits_dir / 'all_relay_splits.json'
    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=2)
    
    print(f"\n✅ Merged {len(all_boys)} boys splits, {len(all_girls)} girls splits")
    print(f"   Saved to: {output_path}")

if __name__ == '__main__':
    main()
