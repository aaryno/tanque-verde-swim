#!/usr/bin/env python3
"""
Merge relay leadoff times into existing individual records.

Times from relay leadoffs are marked with "(r)" to distinguish them.
Only 50 Free (from 200FR) and 100 Free (from 400FR) are extracted.

This script:
1. Reads existing Top 10 markdown files
2. Merges leadoff times into the appropriate events
3. Re-ranks and keeps top 10 unique swimmers
4. Marks relay-derived times with "(r)"
5. Writes updated markdown files
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def parse_time_to_seconds(time_str):
    """Convert time string to seconds"""
    time_str = str(time_str).strip()
    if time_str.startswith('00:'):
        time_str = time_str[3:]
    
    if ':' in time_str:
        parts = time_str.split(':')
        try:
            return int(parts[0]) * 60 + float(parts[1])
        except:
            return None
    else:
        try:
            return float(time_str)
        except:
            return None

def format_time(seconds):
    """Format seconds as time string"""
    if seconds >= 60:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}:{secs:05.2f}"
    else:
        return f"{seconds:.2f}"

def parse_markdown_table(content, event_name):
    """Parse a markdown table for a specific event and return records"""
    # Find the section for this event
    pattern = rf'##+ {re.escape(event_name)}\s*\n\n?\|[^\n]+\n\|[-:\s|]+\n((?:\|[^\n]+\n)+)'
    match = re.search(pattern, content, re.IGNORECASE)
    
    if not match:
        return []
    
    records = []
    table_rows = match.group(1).strip().split('\n')
    
    for row in table_rows:
        cells = [c.strip() for c in row.split('|')[1:-1]]  # Skip empty first/last
        if len(cells) >= 5:
            # Remove bold markers
            rank = cells[0].replace('**', '').strip()
            time_str = cells[1].replace('**', '').strip()
            name = cells[2].replace('**', '').strip()
            year = cells[3].replace('**', '').strip()
            date = cells[4].replace('**', '').strip()
            meet = cells[5].replace('**', '').strip() if len(cells) > 5 else ''
            
            # Check if this is a relay time (marked with r)
            is_relay = '(r)' in time_str
            time_clean = time_str.replace('(r)', '').strip()
            
            records.append({
                'time': parse_time_to_seconds(time_clean),
                'time_str': time_clean,
                'name': name,
                'year': year,
                'date': date,
                'meet': meet,
                'is_relay': is_relay
            })
    
    return records

def load_leadoff_times():
    """Load extracted leadoff times"""
    with open('data/relay_leadoff_times.json', 'r') as f:
        return json.load(f)

def merge_records(existing, leadoffs, event_type):
    """Merge existing records with leadoff times, keeping best per swimmer"""
    
    # Convert leadoffs to record format
    for leadoff in leadoffs:
        grade = leadoff.get('grade', '')
        
        # Use enriched date/meet if available, fallback to season
        date = leadoff.get('date', '')
        meet = leadoff.get('meet', '')
        
        # If date looks like a season (e.g., "2022-23"), keep as is
        # Otherwise it's an actual date
        
        existing.append({
            'time': leadoff['time'],
            'time_str': leadoff['time_str'],
            'name': leadoff['name'],
            'year': grade,
            'date': date,
            'meet': meet,
            'is_relay': True
        })
    
    # Group by swimmer, keep fastest time per swimmer
    best_times = {}
    for record in existing:
        name = record['name']
        if record['time'] is None:
            continue
        if name not in best_times or record['time'] < best_times[name]['time']:
            best_times[name] = record
    
    # Sort by time and return
    return sorted(best_times.values(), key=lambda x: x['time'])

def format_record_row(record, rank, is_record_holder=False):
    """Format a record as a markdown table row"""
    time_str = record['time_str']
    if record.get('is_relay'):
        time_str = f"{time_str} (r)"
    
    if is_record_holder:
        return f"| **{rank}** | **{time_str}** | **{record['name']}** | **{record['year']}** | **{record['date']}** | **{record['meet']}** |"
    else:
        return f"| {rank} | {time_str} | {record['name']} | {record['year']} | {record['date']} | {record['meet']} |"

def update_markdown_file(filepath, event_updates):
    """Update a markdown file with merged leadoff times"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for event_name, new_records in event_updates.items():
        # Find and replace the table for this event
        pattern = rf'(##+ {re.escape(event_name)}\s*\n\n?\|[^\n]+\n\|[-:\s|]+\n)((?:\|[^\n]+\n)+)'
        
        def replace_table(match):
            header = match.group(1)
            
            # Generate new table rows
            rows = []
            for i, record in enumerate(new_records[:10], 1):  # Top 10 only
                rows.append(format_record_row(record, i, i == 1))
            
            return header + '\n'.join(rows) + '\n'
        
        content = re.sub(pattern, replace_table, content, flags=re.IGNORECASE)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    print("Loading leadoff times...")
    leadoffs = load_leadoff_times()
    
    print(f"  Boys 50 Free: {len(leadoffs['boys']['50_free'])} swimmers")
    print(f"  Boys 100 Free: {len(leadoffs['boys']['100_free'])} swimmers")
    print(f"  Girls 50 Free: {len(leadoffs['girls']['50_free'])} swimmers")
    print(f"  Girls 100 Free: {len(leadoffs['girls']['100_free'])} swimmers")
    
    # Process all-time top 10 files ONLY (seasonal files need season-specific filtering)
    files_to_process = [
        ('records/top10-boys-alltime.md', 'boys'),
        ('records/top10-girls-alltime.md', 'girls'),
    ]
    
    # NOTE: Seasonal files are not processed here because leadoff times
    # would need to be filtered by season, which requires additional logic.
    # For now, only all-time records include relay leadoff times.
    
    updated_files = []
    
    for filepath, gender in files_to_process:
        if not Path(filepath).exists():
            continue
        
        print(f"\nProcessing {filepath}...")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        event_updates = {}
        
        # Process 50 Freestyle
        existing_50 = parse_markdown_table(content, '50 Freestyle')
        if existing_50:
            merged_50 = merge_records(existing_50, leadoffs[gender]['50_free'], '50_free')
            event_updates['50 Freestyle'] = merged_50
            print(f"  50 Free: {len(existing_50)} existing + {len(leadoffs[gender]['50_free'])} leadoffs = {len(merged_50)} unique")
        
        # Process 100 Freestyle
        existing_100 = parse_markdown_table(content, '100 Freestyle')
        if existing_100:
            merged_100 = merge_records(existing_100, leadoffs[gender]['100_free'], '100_free')
            event_updates['100 Freestyle'] = merged_100
            print(f"  100 Free: {len(existing_100)} existing + {len(leadoffs[gender]['100_free'])} leadoffs = {len(merged_100)} unique")
        
        if event_updates:
            if update_markdown_file(filepath, event_updates):
                updated_files.append(filepath)
                print(f"  ✓ Updated")
            else:
                print(f"  (no changes needed)")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: Updated {len(updated_files)} files with leadoff times")
    print("="*60)
    for f in updated_files:
        print(f"  ✓ {f}")
    
    print("\nNote: Times marked with '(r)' are from relay leadoffs.")
    print("Run generate_website.py to regenerate HTML with updated records.")

if __name__ == "__main__":
    main()

