#!/usr/bin/env python3
"""Generate high school swimming records organized by grade."""

import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from swim_data_tool.services.record_generator import RecordGenerator
from swim_data_tool.models.events import convert_time_to_seconds, format_event_name
from time_formatter import format_time_display, format_date_display

# High school grade groups
GRADE_GROUPS = ["Freshman", "Sophomore", "Junior", "Senior", "Open"]

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


@dataclass
class HSRecordEntry:
    """A high school record entry."""
    event_code: str
    grade_group: str
    swimmer_name: str
    time: str
    grade: str
    date: str
    meet: str
    time_seconds: float = 0.0


def determine_grade_group(grade):
    """Convert numeric grade to grade group label."""
    if pd.isna(grade):
        return None
    grade = int(grade)
    if grade == 9:
        return "Freshman"
    elif grade == 10:
        return "Sophomore"
    elif grade == 11:
        return "Junior"
    elif grade == 12:
        return "Senior"
    else:
        return None


def get_best_times_by_grade(df: pd.DataFrame) -> dict[str, dict[str, HSRecordEntry]]:
    """Get best times for each event/grade group combination."""
    records: dict[str, dict[str, HSRecordEntry]] = {}
    
    # Make a copy and add grade groups
    df = df.copy()
    df['grade_group'] = df['grade'].apply(determine_grade_group)
    
    # event_code and time_seconds are already added by parse_and_normalize_events
    # Just filter for SCY events (event_course == 'scy')
    df_scy = df[df['event_course'] == 'scy'].copy()
    
    # Process each event
    for event_code, event_name in HS_EVENTS.items():
        records[event_code] = {}
        
        # Filter for this event
        df_event = df_scy[df_scy['event_code'] == event_code]
        
        if df_event.empty:
            continue
        
        # Process each grade group
        for grade_group in GRADE_GROUPS:
            if grade_group == "Open":
                # Open includes everyone
                df_grade = df_event.copy()
            else:
                # Specific grade group
                df_grade = df_event[df_event['grade_group'] == grade_group]
            
            if df_grade.empty:
                continue
            
            # Sort by time and get best
            df_grade = df_grade.sort_values('time_seconds')
            
            # Get best time per swimmer, then overall best
            df_best_per_swimmer = df_grade.drop_duplicates(subset=['Name'], keep='first')
            
            if df_best_per_swimmer.empty:
                continue
            
            # Get overall best
            best = df_best_per_swimmer.iloc[0]
            
            # Create record entry with formatted time
            record = HSRecordEntry(
                event_code=event_code,
                grade_group=grade_group,
                swimmer_name=best.get('Name', ''),
                time=format_time_display(best.get('SwimTime', '')),
                grade=str(int(best.get('grade', 0))) if not pd.isna(best.get('grade')) else '',
                date=best.get('SwimDate', ''),
                meet=best.get('MeetName', ''),
                time_seconds=best.get('time_seconds', 0.0),
            )
            
            records[event_code][grade_group] = record
    
    return records


def generate_hs_markdown(records: dict, gender: str, team_name: str, output_path: Path):
    """Generate markdown file for high school records."""
    gender_label = "Boys" if gender == "M" else "Girls"
    
    lines = [
        f"# {team_name} - {gender_label}",
        "## Team Records - Short Course Yards (SCY)",
        "",
        f"**Generated:** {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}",
        "",
        "---",
        "",
    ]
    
    # Generate tables for each event
    for event_code, event_name in HS_EVENTS.items():
        lines.append(f"### {event_name}")
        lines.append("")
        lines.append("| Grade | Time | Athlete | Date | Meet |")
        lines.append("|-------|-----:|---------|------|------|")  # Right-align time column
        
        for grade_group in GRADE_GROUPS:
            if event_code in records and grade_group in records[event_code]:
                record = records[event_code][grade_group]
                date_str = format_date_display(record.date)
                # Make Open category rows bold
                if grade_group == "Open":
                    lines.append(
                        f"| **{grade_group}** | **{record.time}** | **{record.swimmer_name}** | **{date_str}** | **{record.meet}** |"
                    )
                else:
                    lines.append(
                        f"| {grade_group} | {record.time} | {record.swimmer_name} | {date_str} | {record.meet} |"
                    )
            else:
                lines.append(f"| {grade_group} | — | — | — | — |")
        
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}*")
    lines.append("")
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"  ✓ Generated: {output_path}")


def main():
    """Main entry point."""
    print("\n🏊 Generating High School Records\n")
    
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
    
    # Filter out relay events (they should not count as individual records)
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
    
    # Generate records
    print("📊 Generating high school records...")
    
    output_dir = Path('data/records')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if has_gender:
        # Boys
        df_boys = df_normalized[df_normalized['Gender'] == 'M']
        if not df_boys.empty:
            records_boys = get_best_times_by_grade(df_boys)
            generate_hs_markdown(records_boys, 'M', 'Tanque Verde (Tucson, AZ)', output_dir / 'records-boys.md')
        
        # Girls
        df_girls = df_normalized[df_normalized['Gender'] == 'F']
        if not df_girls.empty:
            records_girls = get_best_times_by_grade(df_girls)
            generate_hs_markdown(records_girls, 'F', 'Tanque Verde (Tucson, AZ)', output_dir / 'records-girls.md')
    else:
        # Combined
        records = get_best_times_by_grade(df_normalized)
        generate_hs_markdown(records, 'M', 'Tanque Verde (Tucson, AZ)', output_dir / 'records.md')
    
    print("\n✓ High School Records Complete!\n")


if __name__ == '__main__':
    main()

