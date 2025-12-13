#!/usr/bin/env python3
"""
Process Top 10 files with proper name aliasing and deduplication.

1. Load swimmer aliases
2. Apply name normalization (informal -> formal names)
3. Deduplicate swimmers per event (keep fastest time)
4. Keep top 10 entries per event
5. Renumber rankings
"""

import json
import re
from pathlib import Path
from datetime import datetime


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


def process_top10_file(source_path: Path, dest_path: Path, aliases: dict) -> dict:
    """Process a single top10 file with aliasing and deduplication."""
    with open(source_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    stats = {'name_fixes': 0, 'duplicates_removed': 0, 'events_processed': 0}
    
    in_table = False
    table_rows = []
    header_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect event header (### Event Name)
        if line.startswith('### '):
            # Process previous table if any
            if table_rows:
                processed = process_table(table_rows, aliases, stats)
                new_lines.extend(header_lines)
                new_lines.extend(processed)
                stats['events_processed'] += 1
            
            # Start new event
            new_lines.append(line)
            table_rows = []
            header_lines = []
            in_table = False
            i += 1
            continue
        
        # Detect table header
        if '| Rank |' in line:
            in_table = True
            header_lines = [line]
            i += 1
            # Get separator line
            if i < len(lines) and lines[i].strip().startswith('|--'):
                header_lines.append(lines[i])
                i += 1
            continue
        
        # Detect table end
        if in_table and (line.strip() == '' or line.startswith('#') or line.startswith('---')):
            # Process table
            if table_rows:
                processed = process_table(table_rows, aliases, stats)
                new_lines.extend(header_lines)
                new_lines.extend(processed)
                stats['events_processed'] += 1
            table_rows = []
            header_lines = []
            in_table = False
            new_lines.append(line)
            i += 1
            continue
        
        # Collect table data rows
        if in_table and line.strip().startswith('|') and '|' in line[1:]:
            table_rows.append(line)
            i += 1
            continue
        
        # Non-table line
        new_lines.append(line)
        i += 1
    
    # Process final table if any
    if table_rows:
        processed = process_table(table_rows, aliases, stats)
        new_lines.extend(header_lines)
        new_lines.extend(processed)
        stats['events_processed'] += 1
    
    # Write output
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    return stats


def process_table(rows: list, aliases: dict, stats: dict) -> list:
    """Process table rows: apply aliases, deduplicate, keep top 10, renumber."""
    if not rows:
        return []
    
    # Parse rows
    parsed = []
    for row in rows:
        parts = [p.strip() for p in row.split('|')]
        if len(parts) >= 6:
            # parts: ['', rank, time, athlete, year, date, meet, '']
            rank = parts[1]
            time = parts[2]
            athlete = parts[3]
            year = parts[4]
            date = parts[5]
            meet = parts[6] if len(parts) > 6 else ""
            
            # Apply alias
            original_name = athlete
            if athlete in aliases:
                athlete = aliases[athlete]
                if athlete != original_name:
                    stats['name_fixes'] += 1
            
            parsed.append({
                'time': time,
                'time_seconds': parse_time_to_seconds(time),
                'athlete': athlete,
                'original_athlete': original_name,
                'year': year,
                'date': date,
                'date_parsed': parse_date(date),
                'meet': meet
            })
    
    # Sort by time (fastest first), then by date (earliest first for ties)
    parsed.sort(key=lambda x: (x['time_seconds'], x['date_parsed']))
    
    # Deduplicate by athlete (keep first = fastest)
    seen_athletes = set()
    deduped = []
    for entry in parsed:
        if entry['athlete'] not in seen_athletes:
            seen_athletes.add(entry['athlete'])
            deduped.append(entry)
        else:
            stats['duplicates_removed'] += 1
    
    # Keep top 10
    top10 = deduped[:10]
    
    # Renumber and format
    result = []
    for rank, entry in enumerate(top10, 1):
        result.append(
            f"| {rank} | {entry['time']} | {entry['athlete']} | {entry['year']} | {entry['date']} | {entry['meet']} |"
        )
    
    return result


def main():
    base_dir = Path(__file__).parent
    source_dir = base_dir / "data" / "records"
    dest_dir = base_dir / "records"
    aliases_path = base_dir / "data" / "swimmer_aliases.json"
    
    print("=" * 70)
    print("PROCESSING TOP 10 FILES WITH NAME ALIASES AND DEDUPLICATION")
    print("=" * 70)
    
    # Load aliases
    aliases = load_aliases(aliases_path)
    print(f"\n📋 Loaded {len(aliases)} swimmer aliases")
    
    # Find all top10 files
    top10_files = sorted(source_dir.glob("top10*.md"))
    print(f"📁 Found {len(top10_files)} top10 files to process\n")
    
    total_stats = {'name_fixes': 0, 'duplicates_removed': 0, 'events_processed': 0}
    
    for source_path in top10_files:
        dest_path = dest_dir / source_path.name
        stats = process_top10_file(source_path, dest_path, aliases)
        
        if stats['name_fixes'] > 0 or stats['duplicates_removed'] > 0:
            print(f"  {source_path.name}:")
            if stats['name_fixes'] > 0:
                print(f"    - {stats['name_fixes']} names normalized")
            if stats['duplicates_removed'] > 0:
                print(f"    - {stats['duplicates_removed']} duplicates removed")
        
        for key in total_stats:
            total_stats[key] += stats[key]
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Events processed:    {total_stats['events_processed']}")
    print(f"  Names normalized:    {total_stats['name_fixes']}")
    print(f"  Duplicates removed:  {total_stats['duplicates_removed']}")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

