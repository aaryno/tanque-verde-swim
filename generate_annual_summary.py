#!/usr/bin/env python3
"""
Generate Annual Summary for current season (2024-25).

Creates a comprehensive season overview with stats, highlights, and achievements.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from swim_data_tool.services.record_generator import RecordGenerator
from time_formatter import format_time_display, format_date_display


def get_current_season_dates():
    """Get date range for current season (2024-25)"""
    return ("2024-08-01", "2025-08-01")


def load_all_time_records(data_dir: Path) -> dict:
    """Load all-time records for comparison"""
    records = {'M': {}, 'F': {}}
    
    # This is a simplified version - ideally would parse the actual records files
    # For now, we'll return empty and skip records broken section if not available
    return records


def check_records_broken(df_season: pd.DataFrame, df_all_time: pd.DataFrame, season_start: str) -> list:
    """Check if any all-time records were broken this season"""
    records_broken = []
    
    # Get historical data (everything BEFORE current season)
    df_all_time['SwimDate'] = pd.to_datetime(df_all_time['SwimDate'], errors='coerce')
    df_historical = df_all_time[df_all_time['SwimDate'] < season_start].copy()
    
    # Get season bests
    season_bests = {}
    for gender in ['M', 'F']:
        df_gender = df_season[df_season['Gender'] == gender]
        for event_code in ['50-free', '100-free', '200-free', '500-free', '100-back', '100-breast', '100-fly', '200-im']:
            df_event = df_gender[df_gender['event_code'] == event_code]
            if not df_event.empty:
                best = df_event.nsmallest(1, 'time_seconds').iloc[0]
                season_bests[(gender, event_code)] = best
    
    # Compare with previous records (historical data before this season)
    for (gender, event_code), season_best in season_bests.items():
        df_gender_hist = df_historical[df_historical['Gender'] == gender]
        df_event_hist = df_gender_hist[df_gender_hist['event_code'] == event_code]
        
        if not df_event_hist.empty:
            # Find the PREVIOUS record (best time before this season)
            previous_best = df_event_hist.nsmallest(1, 'time_seconds').iloc[0]
            
            # Check if season time is faster than previous record
            if season_best['time_seconds'] < previous_best['time_seconds']:
                # This is a new record!
                records_broken.append({
                    'gender': gender,
                    'event': season_best['Event'],
                    'swimmer': season_best['Name'],
                    'grade': season_best['grade'],
                    'time': season_best['SwimTime'],
                    'date': season_best['SwimDate'],
                    'meet': season_best['MeetName'],
                    'old_time': previous_best['SwimTime'],
                    'old_holder': previous_best['Name']
                })
        else:
            # No previous record - this is the FIRST record for this event
            records_broken.append({
                'gender': gender,
                'event': season_best['Event'],
                'swimmer': season_best['Name'],
                'grade': season_best['grade'],
                'time': season_best['SwimTime'],
                'date': season_best['SwimDate'],
                'meet': season_best['MeetName'],
                'old_time': None,
                'old_holder': 'None (First Record)'
            })
    
    return records_broken


def generate_annual_summary(output_path: Path, df_season: pd.DataFrame, df_all_time: pd.DataFrame, season: str):
    """Generate annual summary markdown"""
    
    # Overall stats
    total_swims = len(df_season)
    swimmers = df_season['Name'].nunique()
    meets = df_season['MeetName'].nunique()
    
    # Gender breakdown
    boys_swims = len(df_season[df_season['Gender'] == 'M'])
    girls_swims = len(df_season[df_season['Gender'] == 'F'])
    
    # Grade breakdown
    grade_dist = df_season['grade'].value_counts().sort_index()
    
    # Check for records broken (pass season start date to exclude current season from comparison)
    records_broken = check_records_broken(df_season, df_all_time, get_current_season_dates()[0])
    
    lines = [
        f"# {season} Season Summary",
        "## Tanque Verde High School Swimming",
        "",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        "",
        "---",
        "",
        "## Season Overview",
        "",
        f"**Total Swims:** {total_swims:,}",
        f"**Swimmers:** {swimmers}",
        f"**Meets Attended:** {meets}",
        "",
        "### Participation by Gender",
        f"- **Boys:** {boys_swims} swims",
        f"- **Girls:** {girls_swims} swims",
        "",
        "### Participation by Grade",
    ]
    
    grade_labels = {9: "Freshman", 10: "Sophomore", 11: "Junior", 12: "Senior"}
    for grade, count in grade_dist.items():
        if not pd.isna(grade):
            label = grade_labels.get(int(grade), f"Grade {int(grade)}")
            lines.append(f"- **{label}:** {count} swims")
    
    lines.extend([
        "",
        "---",
        "",
        "## Meet Schedule",
        "",
    ])
    
    # List all meets with dates
    meets_df = df_season[['SwimDate', 'MeetName']].drop_duplicates().sort_values('SwimDate')
    lines.append("| Date | Meet |")
    lines.append("|------|------|")
    for _, row in meets_df.iterrows():
        date_str = format_date_display(row['SwimDate'])
        lines.append(f"| {date_str} | {row['MeetName']} |")
    
    # Records broken section
    if records_broken:
        lines.extend([
            "",
            "---",
            "",
            "## 🏆 Records Broken",
            "",
        ])
        
        for record in records_broken:
            gender_label = "Boys" if record['gender'] == 'M' else "Girls"
            grade_labels = {9: "FR", 10: "SO", 11: "JR", 12: "SR"}
            year = grade_labels.get(int(record['grade']), "") if not pd.isna(record['grade']) else ""
            
            # Format date and times
            date_str = format_date_display(record['date'])
            new_time = format_time_display(record['time'])
            
            lines.append(f"**{gender_label} {record['event']}**")
            lines.append(f"- **NEW:** {new_time} - {record['swimmer']} ({year})")
            
            if record['old_time']:
                old_time = format_time_display(record['old_time'])
                lines.append(f"- *Previous:* {old_time} - {record['old_holder']}")
            else:
                lines.append(f"- *Previous:* {record['old_holder']}")
            
            lines.append(f"- *Date:* {date_str} at {record['meet']}")
            lines.append("")
    
    lines.extend([
        "",
        "---",
        "",
        "## Season Best Times",
        "",
    ])
    
    # Event order
    event_order = ['50-free', '100-free', '200-free', '500-free', '100-back', '100-breast', '100-fly', '200-im']
    event_names = {
        '50-free': '50 Free',
        '100-free': '100 Free',
        '200-free': '200 Free',
        '500-free': '500 Free',
        '100-back': '100 Back',
        '100-breast': '100 Breast',
        '100-fly': '100 Fly',
        '200-im': '200 IM'
    }
    
    # Create table with both boys and girls
    lines.append("| Event | Boys Time | Boys Swimmer | Girls Time | Girls Swimmer |")
    lines.append("|-------|----------:|--------------|-----------:|---------------|")
    
    for event_code in event_order:
        event_name = event_names[event_code]
        
        # Boys
        df_boys = df_season[df_season['Gender'] == 'M']
        df_boys_event = df_boys[df_boys['event_code'] == event_code]
        if not df_boys_event.empty:
            fastest_boys = df_boys_event.nsmallest(1, 'time_seconds').iloc[0]
            boys_time = format_time_display(fastest_boys['SwimTime'])
            grade_labels = {9: "FR", 10: "SO", 11: "JR", 12: "SR"}
            boys_year = grade_labels.get(int(fastest_boys['grade']), "") if not pd.isna(fastest_boys['grade']) else ""
            boys_swimmer = f"{fastest_boys['Name']} ({boys_year})"
        else:
            boys_time = "—"
            boys_swimmer = "—"
        
        # Girls
        df_girls = df_season[df_season['Gender'] == 'F']
        df_girls_event = df_girls[df_girls['event_code'] == event_code]
        if not df_girls_event.empty:
            fastest_girls = df_girls_event.nsmallest(1, 'time_seconds').iloc[0]
            girls_time = format_time_display(fastest_girls['SwimTime'])
            girls_year = grade_labels.get(int(fastest_girls['grade']), "") if not pd.isna(fastest_girls['grade']) else ""
            girls_swimmer = f"{fastest_girls['Name']} ({girls_year})"
        else:
            girls_time = "—"
            girls_swimmer = "—"
        
        lines.append(f"| {event_name} | {boys_time} | {boys_swimmer} | {girls_time} | {girls_swimmer} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## Active Swimmers",
        "",
    ])
    
    # List swimmers who competed this season
    swimmers_list = df_season.groupby(['Name', 'Gender', 'grade']).size().reset_index(name='swims')
    swimmers_list = swimmers_list.sort_values(['Gender', 'grade', 'Name'])
    
    # Boys
    boys_list = swimmers_list[swimmers_list['Gender'] == 'M']
    if not boys_list.empty:
        lines.append("### Boys")
        lines.append("")
        for grade in [9, 10, 11, 12]:
            grade_swimmers = boys_list[boys_list['grade'] == grade]
            if not grade_swimmers.empty:
                grade_label = grade_labels.get(grade, f"Grade {grade}")
                lines.append(f"**{grade_label}:**")
                for _, swimmer in grade_swimmers.iterrows():
                    lines.append(f"- {swimmer['Name']} ({swimmer['swims']} swims)")
                lines.append("")
    
    # Girls
    girls_list = swimmers_list[swimmers_list['Gender'] == 'F']
    if not girls_list.empty:
        lines.append("### Girls")
        lines.append("")
        for grade in [9, 10, 11, 12]:
            grade_swimmers = girls_list[girls_list['grade'] == grade]
            if not grade_swimmers.empty:
                grade_label = grade_labels.get(grade, f"Grade {grade}")
                lines.append(f"**{grade_label}:**")
                for _, swimmer in grade_swimmers.iterrows():
                    lines.append(f"- {swimmer['Name']} ({swimmer['swims']} swims)")
                lines.append("")
    
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
    
    print(f"✓ Generated: {output_path}")


def main():
    season = "2024-25"
    start_date, end_date = get_current_season_dates()
    
    print(f"\n📊 Generating Annual Summary for {season}\n")
    
    # Load data
    print("📂 Loading swimmer data...")
    gen = RecordGenerator(Path('data'))
    df_all = gen.load_all_swimmer_data()
    
    # Filter for team
    df_team = gen.filter_team_swims(df_all, ['Tanque Verde'])
    
    # Parse events
    df_normalized = gen.parse_and_normalize_events(df_team)
    
    # Filter out relay events (they should not count as individual times)
    print("🔍 Filtering out relay events...")
    df_individual = df_normalized[~df_normalized['Event'].str.contains('RELAY', case=False, na=False)].copy()
    print(f"   Filtered out {len(df_normalized) - len(df_individual)} relay swims")
    
    # Filter for current season
    df_individual['SwimDate'] = pd.to_datetime(df_individual['SwimDate'], errors='coerce')
    df_season = df_individual[
        (df_individual['SwimDate'] >= start_date) &
        (df_individual['SwimDate'] < end_date)
    ].copy()
    
    if df_season.empty:
        print("⚠ No swims found for current season!")
        return
    
    print(f"✓ Found {len(df_season):,} individual swims in {season}\n")
    
    # Generate summary
    output_path = Path('data/records') / f'annual-summary-{season}.md'
    generate_annual_summary(output_path, df_season, df_individual, season)
    
    print("\n✓ Annual Summary Complete!\n")


if __name__ == '__main__':
    main()

