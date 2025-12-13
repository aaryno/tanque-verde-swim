#!/usr/bin/env python3
"""
Fix grades for all swimmers by inferring grade from swim dates.

Strategy:
1. Load each swimmer's CSV
2. Find their most recent swim and its grade
3. Group swims by season (Aug-Nov = fall season)
4. Assign grades working backward from most recent season
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


def determine_season(date_str):
    """Convert date string to season identifier (e.g., '2024-25' for fall 2024)."""
    try:
        date = pd.to_datetime(date_str)
        year = date.year
        month = date.month
        
        # High school swim season is typically Aug-Nov (fall)
        # If month is Aug-Dec, it's the start year of the season (e.g., 2024 in 2024-25)
        # If month is Jan-Jul, it's the end year (e.g., 2025 in 2024-25, so subtract 1)
        if month >= 8:  # Aug-Dec
            season_start = year
        else:  # Jan-Jul
            season_start = year - 1
        
        season_end = (season_start + 1) % 100  # Just the last 2 digits
        return f"{season_start}-{season_end:02d}"
    except:
        return None


def fix_swimmer_grades(csv_file):
    """Fix grades for a single swimmer based on swim dates."""
    df = pd.read_csv(csv_file)
    
    if df.empty or 'grade' not in df.columns or 'SwimDate' not in df.columns:
        return False
    
    # Find most recent swim with a grade
    df['date_parsed'] = pd.to_datetime(df['SwimDate'], errors='coerce')
    df_with_grade = df[df['grade'].notna()].copy()
    
    if df_with_grade.empty:
        return False
    
    # Get the most recent grade
    most_recent = df_with_grade.sort_values('date_parsed', ascending=False).iloc[0]
    most_recent_grade = int(most_recent['grade'])
    most_recent_date = most_recent['date_parsed']
    most_recent_season = determine_season(most_recent['SwimDate'])
    
    # Add season to all swims
    df['season'] = df['SwimDate'].apply(determine_season)
    
    # Get unique seasons, sorted from most recent to oldest
    seasons = sorted(df['season'].dropna().unique(), reverse=True)
    
    # Create mapping of season to grade
    season_to_grade = {}
    current_grade = most_recent_grade
    
    for season in seasons:
        # Check if this season has any swims with grades
        season_swims = df[df['season'] == season]
        existing_grades = season_swims['grade'].dropna()
        
        if len(existing_grades) > 0:
            # Use the most common grade for this season
            season_grade = int(existing_grades.mode()[0])
            season_to_grade[season] = season_grade
            current_grade = season_grade
        else:
            # Assign grade based on position relative to most recent season
            season_index = seasons.index(season)
            most_recent_index = seasons.index(most_recent_season)
            grade_diff = season_index - most_recent_index
            calculated_grade = most_recent_grade - grade_diff
            
            # Clamp to valid high school grades (9-12)
            if 9 <= calculated_grade <= 12:
                season_to_grade[season] = calculated_grade
    
    # Apply grades to all swims based on season
    for season, grade in season_to_grade.items():
        df.loc[df['season'] == season, 'grade'] = grade
    
    # Drop the temporary columns
    df = df.drop(columns=['date_parsed', 'season'])
    
    # Save back to file
    df.to_csv(csv_file, index=False)
    
    return True


def main():
    """Fix grades for all swimmers."""
    swimmers_dir = Path('data/raw/swimmers')
    
    if not swimmers_dir.exists():
        print(f"❌ Directory not found: {swimmers_dir}")
        return
    
    csv_files = list(swimmers_dir.glob('*.csv'))
    
    if not csv_files:
        print(f"❌ No CSV files found in {swimmers_dir}")
        return
    
    print(f"\n🔧 Fixing grades for {len(csv_files)} swimmers...\n")
    
    fixed_count = 0
    skipped_count = 0
    
    for csv_file in csv_files:
        swimmer_name = csv_file.stem
        try:
            if fix_swimmer_grades(csv_file):
                fixed_count += 1
                print(f"  ✓ {swimmer_name}")
            else:
                skipped_count += 1
                print(f"  ⊘ {swimmer_name} (no grade data)")
        except Exception as e:
            skipped_count += 1
            print(f"  ✗ {swimmer_name}: {e}")
    
    print(f"\n✓ Complete!")
    print(f"  Fixed: {fixed_count} swimmers")
    print(f"  Skipped: {skipped_count} swimmers")
    print()


if __name__ == '__main__':
    main()

