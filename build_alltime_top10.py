#!/usr/bin/env python3
"""
Build comprehensive all-time Top 10 lists from all season data.

Collects all swims from every season file, applies aliases, deduplicates,
and outputs the true all-time top 10 for each event.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_aliases(aliases_path: Path) -> dict:
    """Load swimmer aliases from JSON file."""
    if aliases_path.exists():
        with open(aliases_path) as f:
            return json.load(f)
    return {}


def parse_time_to_seconds(time_str: str) -> float:
    """Convert swim time string to seconds for comparison."""
    time_str = time_str.strip()
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    try:
        return float(time_str)
    except ValueError:
        return float('inf')


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime for comparison."""
    date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, "%b %d, %Y")
    except ValueError:
        return datetime.max


def extract_events_from_file(filepath: Path, aliases: dict) -> dict:
    """Extract all events and their entries from a top10 file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    events = defaultdict(list)
    lines = content.split('\n')
    
    current_event = None
    in_table = False
    
    for line in lines:
        # Detect event header
        match = re.match(r'^##+ (.+)$', line)
        if match:
            event_name = match.group(1).strip()
            if event_name and not event_name.startswith('Tanque'):
                current_event = event_name
                in_table = False
            continue
        
        # Detect table start
        if '| Rank |' in line:
            in_table = True
            continue
        
        # Skip separator
        if line.strip().startswith('|--'):
            continue
        
        # Parse data row
        if in_table and current_event and line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 7:
                # parts: ['', rank, time, athlete, year, date, meet, ...]
                time_str = parts[2]
                athlete = parts[3]
                year = parts[4]
                date = parts[5]
                meet = parts[6]
                
                # Skip empty rows
                if not athlete or not time_str:
                    continue
                
                # Apply alias
                if athlete in aliases:
                    athlete = aliases[athlete]
                
                events[current_event].append({
                    'time': time_str,
                    'time_seconds': parse_time_to_seconds(time_str),
                    'athlete': athlete,
                    'year': year,
                    'date': date,
                    'date_parsed': parse_date(date),
                    'meet': meet,
                    'source': filepath.name
                })
        
        # Table end
        if in_table and (line.strip() == '' or line.startswith('---')):
            in_table = False
    
    return events


def build_alltime_top10(all_entries: list, limit: int = 10) -> list:
    """Build top 10 from all entries, deduplicating by athlete."""
    # Sort by time (fastest first), then by date (earliest first)
    sorted_entries = sorted(all_entries, key=lambda x: (x['time_seconds'], x['date_parsed']))
    
    # Deduplicate by athlete
    seen = set()
    result = []
    for entry in sorted_entries:
        if entry['athlete'] not in seen:
            seen.add(entry['athlete'])
            result.append(entry)
            if len(result) >= limit:
                break
    
    return result


def format_top10_table(entries: list) -> list:
    """Format entries as markdown table rows."""
    lines = [
        "| Rank | Time | Athlete | Year | Date | Meet |",
        "|-----:|-----:|---------|------|------|------|"
    ]
    for rank, entry in enumerate(entries, 1):
        lines.append(
            f"| {rank} | {entry['time']} | {entry['athlete']} | {entry['year']} | {entry['date']} | {entry['meet']} |"
        )
    return lines


def main():
    base_dir = Path(__file__).parent
    source_dir = base_dir / "data" / "records"
    dest_dir = base_dir / "records"
    aliases_path = base_dir / "data" / "swimmer_aliases.json"
    
    print("=" * 70)
    print("BUILDING COMPREHENSIVE ALL-TIME TOP 10 LISTS")
    print("=" * 70)
    
    # Load aliases
    aliases = load_aliases(aliases_path)
    print(f"\n📋 Loaded {len(aliases)} swimmer aliases")
    
    # Process boys and girls separately
    for gender in ['boys', 'girls']:
        print(f"\n{'='*70}")
        print(f"Processing {gender.upper()}")
        print('='*70)
        
        # Find all season files for this gender
        pattern = f"top10-{gender}-*.md"
        season_files = [f for f in sorted(source_dir.glob(pattern)) if 'alltime' not in f.name]
        print(f"📁 Found {len(season_files)} season files")
        
        # Collect all entries from all seasons
        all_events = defaultdict(list)
        for filepath in season_files:
            events = extract_events_from_file(filepath, aliases)
            for event, entries in events.items():
                all_events[event].extend(entries)
        
        print(f"📊 Found entries for {len(all_events)} events")
        
        # Also include existing alltime file
        alltime_file = source_dir / f"top10-{gender}-alltime.md"
        if alltime_file.exists():
            events = extract_events_from_file(alltime_file, aliases)
            for event, entries in events.items():
                all_events[event].extend(entries)
            print(f"📊 Merged existing all-time data")
        
        # Build top 10 for each event
        output_lines = [
            f"# All-Time Top 10 - {gender.title()}",
            "## Tanque Verde High School Swimming",
            "",
            f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "---",
            ""
        ]
        
        # Define event order
        event_order = [
            "50 Freestyle", "100 Freestyle", "200 Freestyle", "500 Freestyle",
            "100 Backstroke", "100 Breaststroke", "100 Butterfly", "200 Individual Medley"
        ]
        
        for event in event_order:
            if event in all_events:
                entries = all_events[event]
                top10 = build_alltime_top10(entries, limit=10)
                
                print(f"  {event}: {len(entries)} total entries → {len(top10)} unique swimmers")
                
                output_lines.append(f"### {event}")
                output_lines.append("")
                output_lines.extend(format_top10_table(top10))
                output_lines.append("")
        
        # Write output
        output_path = dest_dir / f"top10-{gender}-alltime.md"
        with open(output_path, 'w') as f:
            f.write('\n'.join(output_lines))
        print(f"\n✅ Wrote: {output_path}")
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

