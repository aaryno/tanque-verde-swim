#!/usr/bin/env python3
"""
Import relay results from MaxPreps.

Relays are team events (4 swimmers) that appear on team meet results pages,
not on individual athlete pages.
"""

import sys
from pathlib import Path

# Add swim-data-tool to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'swim-data-tool' / 'src'))

from swim_data_tool.sources.maxpreps import MaxPrepsSource
from dotenv import load_dotenv
import pandas as pd

def main():
    # Load environment
    load_dotenv()
    
    print("\n🏊 Importing Relay Results from MaxPreps\n")
    
    # Initialize MaxPreps source
    source = MaxPrepsSource()
    
    # Fetch relay data
    print("📥 Fetching relay results...")
    df_relays = source.get_team_relays()
    
    if df_relays.empty:
        print("⚠️  No relay results found!")
        return
    
    print(f"✓ Found {len(df_relays)} relay results\n")
    
    # Display summary
    print("Summary by gender and event:")
    summary = df_relays.groupby(['Gender', 'Event']).size().reset_index(name='count')
    for _, row in summary.iterrows():
        gender_label = "Boys" if row['Gender'] == 'M' else "Girls"
        print(f"  {gender_label} {row['Event']}: {row['count']} results")
    
    # Save to CSV
    output_dir = Path('data/raw')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'team-relays.csv'
    
    df_relays.to_csv(output_path, index=False)
    print(f"\n✓ Saved relay data to: {output_path}")
    print(f"✓ Total relay results: {len(df_relays)}\n")

if __name__ == '__main__':
    main()

