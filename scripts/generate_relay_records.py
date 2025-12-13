#!/usr/bin/env python3
"""
Generate relay records for Tanque Verde High School.

Relays are team events with 4 swimmers. We track the best times for each relay
event by grade level and all-time.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add time_formatter to path
sys.path.insert(0, str(Path(__file__).parent))
from time_formatter import format_time_display, format_date_display


# High school relay events
HS_RELAY_EVENTS = {
    "200-medley-relay": "200 Medley Relay",
    "200-free-relay": "200 Free Relay",
    "400-free-relay": "400 Free Relay",
}

# Grade groups
HS_GRADE_GROUPS = ["Freshman", "Sophomore", "Junior", "Senior", "Open"]


def determine_grade_group(grade: float | None) -> str:
    """Determine grade group from numeric grade"""
    if pd.isna(grade):
        return "Open"
    grade = int(grade)
    if grade == 9:
        return "Freshman"
    if grade == 10:
        return "Sophomore"
    if grade == 11:
        return "Junior"
    if grade == 12:
        return "Senior"
    return "Open"


def normalize_event_code(event: str) -> str:
    """Convert event name to event code"""
    event_lower = event.lower()
    if "200" in event_lower and "medley" in event_lower:
        return "200-medley-relay"
    if "200" in event_lower and ("free" in event_lower or "fr" in event_lower):
        return "200-free-relay"
    if "400" in event_lower and ("free" in event_lower or "fr" in event_lower):
        return "400-free-relay"
    return None


def load_relay_data() -> pd.DataFrame:
    """Load all relay data from swimmer CSVs"""
    data_dir = Path('data/raw/swimmers')
    all_relays = []
    
    for csv_file in data_dir.glob('*.csv'):
        try:
            df = pd.read_csv(csv_file)
            # Filter for relay events
            relay_df = df[df['Event'].str.contains('RELAY', na=False, case=False)]
            if not relay_df.empty:
                all_relays.append(relay_df)
        except Exception as e:
            print(f"Warning: Could not read {csv_file}: {e}")
            continue
    
    if not all_relays:
        return pd.DataFrame()
    
    combined = pd.concat(all_relays, ignore_index=True)
    
    # Parse times to seconds for comparison
    combined['time_seconds'] = combined['SwimTime'].apply(parse_time_to_seconds)
    combined['SwimDate'] = pd.to_datetime(combined['SwimDate'], errors='coerce')
    combined['event_code'] = combined['Event'].apply(normalize_event_code)
    combined['grade_group'] = combined['grade'].apply(determine_grade_group)
    
    return combined


def parse_time_to_seconds(time_str: str) -> float:
    """Convert time string to seconds"""
    if not time_str or pd.isna(time_str):
        return float('inf')
    
    try:
        time_str = str(time_str).strip()
        if ':' in time_str:
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    except (ValueError, IndexError):
        return float('inf')


def get_relay_participants(df: pd.DataFrame, event_code: str, gender: str, 
                           swim_date: str, meet_name: str, time: str) -> list:
    """Get list of swimmers who participated in a specific relay"""
    # Find all swimmers with this exact relay result
    mask = (
        (df['event_code'] == event_code) &
        (df['Gender'] == gender) &
        (df['SwimDate'] == swim_date) &
        (df['MeetName'] == meet_name) &
        (df['SwimTime'] == time)
    )
    participants = df[mask][['Name', 'grade']].drop_duplicates()
    
    # Format as list of "Name (Grade)"
    result = []
    grade_labels = {9: "FR", 10: "SO", 11: "JR", 12: "SR"}
    for _, row in participants.iterrows():
        if pd.notna(row['grade']):
            grade_label = grade_labels.get(int(row['grade']), "")
            result.append(f"{row['Name']} ({grade_label})")
        else:
            result.append(row['Name'])
    
    return result


def generate_relay_records_markdown(df: pd.DataFrame, gender: str, output_path: Path):
    """Generate relay records markdown file"""
    gender_label = "Boys" if gender == "M" else "Girls"
    
    lines = [
        f"# {gender_label} Relay Records",
        f"## Tanque Verde High School Swimming",
        "",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y')}",
        "",
        "---",
        "",
    ]
    
    # Filter for this gender
    df_gender = df[df['Gender'] == gender].copy()
    
    if df_gender.empty:
        lines.extend([
            f"No relay data available for {gender_label.lower()}.",
            ""
        ])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        return
    
    # For each relay event
    for event_code, event_name in HS_RELAY_EVENTS.items():
        df_event = df_gender[df_gender['event_code'] == event_code].copy()
        
        if df_event.empty:
            continue
        
        lines.extend([
            f"## {event_name}",
            "",
        ])
        
        # Get top 10 unique relay times (deduplicate by date, meet, and time)
        df_unique = df_event.drop_duplicates(subset=['SwimDate', 'MeetName', 'SwimTime'])
        df_top10 = df_unique.nsmallest(10, 'time_seconds')
        
        lines.append("| Rank | Time | Participants | Date | Meet |")
        lines.append("|-----:|-----:|--------------|------|------|")
        
        for rank, (_, relay) in enumerate(df_top10.iterrows(), 1):
            # Get all participants for this specific relay
            participants = get_relay_participants(
                df_event, event_code, gender,
                relay['SwimDate'], relay['MeetName'], relay['SwimTime']
            )
            participants_str = ", ".join(participants) if participants else "—"
            
            # Format output
            time = format_time_display(relay['SwimTime'])
            date_str = format_date_display(relay['SwimDate'])
            
            # Bold the #1 time
            if rank == 1:
                lines.append(
                    f"| **{rank}** | **{time}** | **{participants_str}** | **{date_str}** | **{relay['MeetName']}** |"
                )
            else:
                lines.append(
                    f"| {rank} | {time} | {participants_str} | {date_str} | {relay['MeetName']} |"
                )
        
        lines.extend(["", "---", ""])
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")


def main():
    print("\n🏊 Generating Relay Records\n")
    
    # Load relay data
    print("📂 Loading relay data...")
    df = load_relay_data()
    
    if df.empty:
        print("⚠️  No relay data found!")
        return
    
    print(f"✓ Loaded {len(df):,} relay results from {df['Name'].nunique()} swimmers\n")
    
    # Generate records for boys and girls
    output_dir = Path('data/records')
    
    generate_relay_records_markdown(df, 'M', output_dir / 'relay-records-boys.md')
    generate_relay_records_markdown(df, 'F', output_dir / 'relay-records-girls.md')
    
    print("\n✓ Relay Records Complete!\n")


if __name__ == '__main__':
    main()

