#!/usr/bin/env python3
"""
Harvest Relay Results from AzPreps365 and MaxPreps (v2 - Configurable Output)

Collects relay results from October 20, 2024 onwards for Tanque Verde.
Enhanced version with configurable output directory to avoid overwriting existing data.

Usage:
    python3 harvest_relays_v2.py
    python3 harvest_relays_v2.py --output-dir=data/raw/harvest_2024_11_01
    python3 harvest_relays_v2.py --output-dir=../swim-data-tool/data/reports/azpreps/d3-leaderboards
    python3 harvest_relays_v2.py --cutoff-date=2024-10-01
"""

import sys
import argparse
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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Harvest relay results with configurable output directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default directory and cutoff date (Oct 20, 2024)
  python3 harvest_relays_v2.py
  
  # Specify custom output directory
  python3 harvest_relays_v2.py --output-dir=data/raw/harvest_2024_11_01
  
  # Specify different cutoff date
  python3 harvest_relays_v2.py --cutoff-date=2024-10-01
  
  # Both custom directory and cutoff date
  python3 harvest_relays_v2.py --output-dir=../swim-data-tool/data/reports/azpreps/d3-leaderboards --cutoff-date=2024-09-01
        """
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for harvest data (default: data/raw/azpreps365_harvest/YYYY-MM-DD/)'
    )
    parser.add_argument(
        '--no-timestamp',
        action='store_true',
        help='Do not append timestamp to output directory'
    )
    parser.add_argument(
        '--cutoff-date',
        type=str,
        default='2024-10-20',
        help='Only include relays from this date onwards (format: YYYY-MM-DD, default: 2024-10-20)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" Relay Results Harvest (v2 - Configurable)")
    print("="*70)
    
    # Load environment
    load_dotenv()
    
    # Determine output directory
    harvest_date = datetime.now().strftime("%Y-%m-%d")
    
    if args.output_dir:
        # Use specified directory
        if args.no_timestamp:
            harvest_dir = Path(args.output_dir)
        else:
            harvest_dir = Path(args.output_dir) / harvest_date
    else:
        # Use default directory with timestamp
        harvest_dir = Path("data/raw/azpreps365_harvest") / harvest_date
    
    harvest_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Output directory: {harvest_dir.absolute()}")
    
    # Parse cutoff date
    try:
        cutoff_date = datetime.strptime(args.cutoff_date, '%Y-%m-%d').date()
    except ValueError:
        print(f"❌ Invalid cutoff date format: {args.cutoff_date}")
        print("   Expected format: YYYY-MM-DD (e.g., 2024-10-20)")
        sys.exit(1)
    
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
    print(f"\n📊 Results saved to: {harvest_dir.absolute()}")
    print()


if __name__ == "__main__":
    main()

