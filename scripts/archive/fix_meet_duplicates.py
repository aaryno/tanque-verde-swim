#!/usr/bin/env python3
"""
Fix duplicate meets in annual summary files.
Deduplicates meets by date, keeping the most complete name.
"""

import re
from pathlib import Path

def normalize_meet_name(meet_name: str) -> str:
    """Normalize meet name for comparison."""
    # Remove Boys/Girls qualifiers
    normalized = re.sub(r'\s+(Boys|Girls)\s+', ' ', meet_name)
    # Normalize case for location
    normalized = normalized.lower()
    return normalized

def choose_best_meet_name(names: list) -> str:
    """Choose the best (most complete) meet name from duplicates."""
    # Remove Boys/Girls from state championships
    cleaned = []
    for name in names:
        # Remove Boys/Girls from state meet names
        name = re.sub(r'\s+Boys\s+', ' ', name)
        name = re.sub(r'\s+Girls\s+', ' ', name)
        cleaned.append(name)
    
    # Prefer longer names (more complete location info)
    # Also prefer proper case (Sahuarita vs sahuarita)
    best = max(cleaned, key=lambda x: (len(x), x[0].isupper() if x else False))
    return best

def fix_meet_schedule(content: str) -> str:
    """Fix duplicate meets in the Meet Schedule section."""
    # Find the Meet Schedule table
    pattern = r'(\|\s*Date\s*\|\s*Meet\s*\|\n\|[-|\s]+\|\n)((?:\|[^|]+\|[^|]+\|\n)+)'
    
    def fix_table(match):
        header = match.group(1)
        rows = match.group(2)
        
        # Parse rows
        meets_by_date = {}
        for line in rows.strip().split('\n'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                date = parts[1]
                meet = parts[2]
                if date not in meets_by_date:
                    meets_by_date[date] = []
                meets_by_date[date].append(meet)
        
        # Deduplicate and rebuild (sort chronologically)
        from datetime import datetime
        def parse_date(d):
            try:
                return datetime.strptime(d.strip(), "%b %d, %Y")
            except:
                return datetime.max
        
        new_rows = []
        for date in sorted(meets_by_date.keys(), key=parse_date):
            names = meets_by_date[date]
            best_name = choose_best_meet_name(names)
            new_rows.append(f'| {date} | {best_name} |')
        
        return header + '\n'.join(new_rows) + '\n'
    
    return re.sub(pattern, fix_table, content)

def process_file(filepath: Path) -> tuple:
    """Process a single file, return (original_count, new_count)."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Count original meets
    original_meets = len(re.findall(r'^\|[^|]+\|[^|]+\|$', content, re.MULTILINE))
    
    # Fix duplicates
    new_content = fix_meet_schedule(content)
    
    # Count new meets
    new_meets = len(re.findall(r'^\|[^|]+\|[^|]+\|$', new_content, re.MULTILINE))
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return (original_meets, new_meets, True)
    return (original_meets, new_meets, False)

def main():
    records_dir = Path('records')
    
    print("=" * 70)
    print("DEDUPLICATING MEETS IN ANNUAL SUMMARIES")
    print("=" * 70)
    print()
    
    total_removed = 0
    files_updated = 0
    
    for md_file in sorted(records_dir.glob('annual-summary-*.md')):
        orig, new, changed = process_file(md_file)
        if changed:
            removed = orig - new
            total_removed += removed
            files_updated += 1
            print(f"  {md_file.name}: removed {removed} duplicate(s)")
    
    print()
    print("=" * 70)
    print(f"TOTAL: {total_removed} duplicates removed from {files_updated} files")
    print("=" * 70)

if __name__ == '__main__':
    main()

