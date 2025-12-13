#!/usr/bin/env python3
"""
Generate Top 10 lists for current season (2024-25).

Creates leaderboards for each event showing the 10 fastest times.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from swim_data_tool.services.record_generator import RecordGenerator
from time_formatter import format_time_display, format_date_display


# High school events (8 events)
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


def get_current_season_dates():
    """Get date range for current season (2024-25)"""
    return ("2024-08-01", "2025-08-01")


def generate_top10_for_event(df: pd.DataFrame, event_code: str, event_name: str) -> list:
    """Generate top 10 list for a single event"""
    # Filter for this event
    df_event = df[df['event_code'] == event_code].copy()
    
    if df_event.empty:
        return []
    
    # Sort by time
    df_event = df_event.sort_values('time_seconds')
    
    # Get best time per swimmer
    df_best = df_event.drop_duplicates(subset=['Name'], keep='first')
    
    # Get top 10
    df_top10 = df_best.head(10)
    
    # Map grades to year labels
    grade_labels = {9: "FR", 10: "SO", 11: "JR", 12: "SR"}
    
    lines = [f"### {event_name}", ""]
    lines.append("| Rank | Time | Athlete | Year | Date | Meet |")
    lines.append("|-----:|-----:|---------|------|------|------|")
    
    for rank, (_, row) in enumerate(df_top10.iterrows(), 1):
        if not pd.isna(row['grade']):
            grade_num = int(row['grade'])
            year = grade_labels.get(grade_num, f"G{grade_num}")
        else:
            year = "—"
        time = format_time_display(row['SwimTime'])
        date_str = format_date_display(row['SwimDate'])
        lines.append(
            f"| {rank} | {time} | {row['Name']} | {year} | {date_str} | {row['MeetName']} |"
        )
    
    lines.append("")
    return lines


def generate_top10_markdown(df: pd.DataFrame, gender: str, output_path: Path, title: str):
    """Generate top 10 markdown file"""
    gender_label = "Boys" if gender == "M" else "Girls"
    
    lines = [
        f"# {title} - {gender_label}",
        "## Tanque Verde High School Swimming",
        "",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        "",
        "---",
        "",
    ]
    
    # Generate top 10 for each event
    for event_code, event_name in HS_EVENTS.items():
        event_lines = generate_top10_for_event(df, event_code, event_name)
        lines.extend(event_lines)
    
    lines.extend([
        "---",
        "",
        f"*Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*",
        "",
    ])
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"  ✓ Generated: {output_path}")


def main():
    season = "2024-25"
    start_date, end_date = get_current_season_dates()
    
    print(f"\n🏊 Generating Top 10 Lists\n")
    
    # Load data
    print("📂 Loading swimmer data...")
    gen = RecordGenerator(Path('data'))
    df_all = gen.load_all_swimmer_data()
    print(f"✓ Loaded {len(df_all):,} swims\n")
    
    # Filter for team
    print("🔍 Filtering team swims...")
    df_team = gen.filter_team_swims(df_all, ['Tanque Verde'])
    print(f"✓ Found {len(df_team):,} team swims\n")
    
    # Parse events
    print("⚙️  Parsing events...")
    df_normalized = gen.parse_and_normalize_events(df_team)
    print(f"✓ Parsed events\n")
    
    # Filter out relay events (they have their own records)
    print("🔍 Filtering out relay events...")
    df_individual = df_normalized[~df_normalized['Event'].str.contains('RELAY', case=False, na=False)].copy()
    relay_count = len(df_normalized) - len(df_individual)
    print(f"✓ Filtered out {relay_count:,} relay swims (relays have separate records)\n")
    df_normalized = df_individual
    
    # Check gender split
    has_gender = 'Gender' in df_normalized.columns and df_normalized['Gender'].notna().any()
    
    if has_gender:
        gender_counts = df_normalized['Gender'].value_counts()
        print(f"👥 Gender split: {gender_counts.get('M', 0)} male swims, {gender_counts.get('F', 0)} female swims\n")
    
    # Generate top 10 lists
    output_dir = Path('data/records')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate ALL-TIME top 10
    print("📊 Generating all-time top 10 lists...")
    if has_gender:
        # Boys
        df_boys = df_normalized[df_normalized['Gender'] == 'M']
        if not df_boys.empty:
            generate_top10_markdown(df_boys, 'M', output_dir / 'top10-boys-alltime.md', 'All-Time Top 10')
        
        # Girls
        df_girls = df_normalized[df_normalized['Gender'] == 'F']
        if not df_girls.empty:
            generate_top10_markdown(df_girls, 'F', output_dir / 'top10-girls-alltime.md', 'All-Time Top 10')
    
    # Generate CURRENT SEASON top 10
    print(f"\n📅 Filtering for {season} season ({start_date} to {end_date})...")
    df_normalized['SwimDate'] = pd.to_datetime(df_normalized['SwimDate'], errors='coerce')
    df_season = df_normalized[
        (df_normalized['SwimDate'] >= start_date) &
        (df_normalized['SwimDate'] < end_date)
    ].copy()
    print(f"✓ Found {len(df_season):,} swims in {season}\n")
    
    if not df_season.empty:
        print(f"📊 Generating {season} top 10 lists...")
        if has_gender:
            # Boys
            df_boys_season = df_season[df_season['Gender'] == 'M']
            if not df_boys_season.empty:
                generate_top10_markdown(df_boys_season, 'M', output_dir / f'top10-boys-{season}.md', f'{season} Top 10')
            
            # Girls
            df_girls_season = df_season[df_season['Gender'] == 'F']
            if not df_girls_season.empty:
                generate_top10_markdown(df_girls_season, 'F', output_dir / f'top10-girls-{season}.md', f'{season} Top 10')
    
    print("\n✓ Top 10 Lists Complete!\n")


if __name__ == '__main__':
    main()

