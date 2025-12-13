#!/usr/bin/env python3
"""
Generate season-specific top 10 lists for all historical seasons.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))
from time_formatter import format_time_display, format_date_display
from swim_data_tool.services.record_generator import RecordGenerator


# Seasons to generate
SEASONS = [
    "2025-26", "2024-25", "2023-24", "2022-23", "2021-22", "2020-21",
    "2019-20", "2018-19", "2017-18", "2016-17", "2015-16",
    "2014-15", "2013-14", "2012-13"
]

HS_EVENTS = {
    "50-free": "50 Freestyle",
    "100-free": "100 Freestyle",
    "200-free": "200 Freestyle",
    "500-free": "500 Freestyle",
    "100-back": "100 Backstroke",
    "100-breast": "100 Breaststroke",
    "100-fly": "100 Butterfly",
    "200-im": "200 Individual Medley",
}


def get_season_dates(season: str):
    """Get date range for a season"""
    start_year = int(season.split('-')[0])
    return (f"{start_year}-08-01", f"{start_year+1}-08-01")


def generate_top10(output_path: Path, df: pd.DataFrame, gender: str, season: str):
    """Generate top 10 list for a season"""
    gender_label = "Boys" if gender == "M" else "Girls"
    
    df_gender = df[df['Gender'] == gender].copy()
    
    if df_gender.empty:
        print(f"    ⚠️  No {gender_label.lower()} data for {season}")
        return
    
    lines = [
        f"# {gender_label} Top 10 - {season} Season",
        "## Tanque Verde High School Swimming",
        "",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y')}",
        "",
        "---",
        "",
    ]
    
    grade_labels = {9: "FR", 10: "SO", 11: "JR", 12: "SR"}
    
    for event_code, event_name in HS_EVENTS.items():
        df_event = df_gender[df_gender['event_code'] == event_code].copy()
        
        if df_event.empty:
            continue
        
        # Get best time per swimmer
        df_best = df_event.loc[df_event.groupby('Name')['time_seconds'].idxmin()]
        df_top10 = df_best.nsmallest(10, 'time_seconds')
        
        if df_top10.empty:
            continue
        
        lines.extend([
            f"## {event_name}",
            "",
            "| Rank | Time | Athlete | Year | Date | Meet |",
            "|-----:|-----:|---------|------|------|------|",
        ])
        
        for rank, (_, row) in enumerate(df_top10.iterrows(), 1):
            time = format_time_display(row['SwimTime'])
            date_str = format_date_display(row['SwimDate'])
            year = grade_labels.get(int(row['grade']), "") if not pd.isna(row['grade']) else ""
            
            lines.append(
                f"| {rank} | {time} | {row['Name']} | {year} | {date_str} | {row['MeetName']} |"
            )
        
        lines.extend(["", "---", ""])
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"    ✓ Generated: {output_path.name}")


def main():
    print("\n🏊 Generating All Season Top 10 Lists\n")
    
    # Load data
    print("📂 Loading swimmer data...")
    gen = RecordGenerator(Path('data'))
    df_all = gen.load_all_swimmer_data()
    
    # Filter for team
    df_team = gen.filter_team_swims(df_all, ['Tanque Verde'])
    
    # Parse events
    df_normalized = gen.parse_and_normalize_events(df_team)
    
    # Filter out relay events (they have their own records)
    df_individual = df_normalized[~df_normalized['Event'].str.contains('RELAY', case=False, na=False)].copy()
    relay_count = len(df_normalized) - len(df_individual)
    df_normalized = df_individual
    
    print(f"✓ Loaded {len(df_normalized):,} individual swims ({relay_count:,} relay swims filtered out)\n")
    
    output_dir = Path('data/records')
    
    for season in SEASONS:
        print(f"📊 Generating top 10 for {season}...")
        start_date, end_date = get_season_dates(season)
        
        # Filter for this season
        df_normalized['SwimDate'] = pd.to_datetime(df_normalized['SwimDate'], errors='coerce')
        df_season = df_normalized[
            (df_normalized['SwimDate'] >= start_date) &
            (df_normalized['SwimDate'] < end_date)
        ].copy()
        
        if df_season.empty:
            print(f"  ⚠️  No swims found for {season}, skipping...\n")
            continue
        
        # Generate boys and girls
        generate_top10(output_dir / f'top10-boys-{season}.md', df_season, 'M', season)
        generate_top10(output_dir / f'top10-girls-{season}.md', df_season, 'F', season)
        print("")
    
    print("✓ All Season Top 10 Lists Complete!\n")


if __name__ == '__main__':
    main()

