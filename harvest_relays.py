#!/usr/bin/env python3
"""
Harvest Relay Results from AzPreps365 and MaxPreps

Collects relay results from October 20, 2024 onwards for Tanque Verde.
"""

import sys
from pathlib import Path
from datetime import datetime, date
import pandas as pd
from dotenv import load_dotenv

# Add swim-data-tool to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'swim-data-tool' / 'src'))

from swim_data_tool.sources.maxpreps import MaxPrepsSource


def filter_relays_by_date(df: pd.DataFrame, cutoff_date: date) -> pd.DataFrame:
    """
    Filter relay results to only include those from cutoff_date onwards.
    
    Args:
        df: DataFrame with relay results
        cutoff_date: Only include results on or after this date
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    # Convert SwimDate to datetime
    df['SwimDate_dt'] = pd.to_datetime(df['SwimDate'], format='%m/%d/%Y', errors='coerce')
    
    # Filter by date
    df_filtered = df[df['SwimDate_dt'] >= pd.Timestamp(cutoff_date)]
    
    # Drop the temporary datetime column
    df_filtered = df_filtered.drop('SwimDate_dt', axis=1)
    
    return df_filtered


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print(" Relay Results Harvest (October 20+)")
    print("="*70)
    
    # Load environment
    load_dotenv()
    
    # Create harvest directory
    harvest_date = datetime.now().strftime("%Y-%m-%d")
    harvest_dir = Path("data/raw/azpreps365_harvest") / harvest_date
    harvest_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Output directory: {harvest_dir}")
    
    # Set cutoff date
    cutoff_date = date(2024, 10, 20)
    print(f"📅 Collecting relays from {cutoff_date} onwards")
    
    # Initialize MaxPreps source
    print("\n🏊 Fetching relay results from MaxPreps...")
    source = MaxPrepsSource()
    
    try:
        # Fetch all relay data
        df_all_relays = source.get_team_relays()
        
        if df_all_relays.empty:
            print("⚠️  No relay results found!")
            return
        
        print(f"✓ Found {len(df_all_relays)} total relay results")
        
        # Filter by date
        df_new_relays = filter_relays_by_date(df_all_relays, cutoff_date)
        
        if df_new_relays.empty:
            print(f"⚠️  No relay results found after {cutoff_date}")
            return
        
        print(f"✓ Found {len(df_new_relays)} NEW relay results (since {cutoff_date})")
        
        # Display summary
        print("\n📊 Summary by gender and event:")
        summary = df_new_relays.groupby(['Gender', 'Event']).size().reset_index(name='count')
        for _, row in summary.iterrows():
            gender_label = "Boys" if row['Gender'] == 'M' else "Girls"
            print(f"   {gender_label} {row['Event']}: {row['count']} results")
        
        # Save to CSV
        output_filename = f"new_relays_since_{cutoff_date.strftime('%Y%m%d')}_{harvest_date}.csv"
        output_path = harvest_dir / output_filename
        
        df_new_relays.to_csv(output_path, index=False)
        print(f"\n✅ Saved relay data to: {output_path}")
        
        # Also save a summary of unique meets
        unique_meets = df_new_relays[['SwimDate', 'MeetName']].drop_duplicates()
        print(f"\n📅 Meets included ({len(unique_meets)} meets):")
        for _, row in unique_meets.sort_values('SwimDate').iterrows():
            print(f"   {row['SwimDate']}: {row['MeetName']}")
        
    except Exception as e:
        print(f"❌ Error fetching relay data: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print(" Relay Harvest Complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()

