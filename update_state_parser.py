#!/usr/bin/env python3
"""
Update AIA State Parser
=======================
Adds a new year to the AIA_STATE_MEETS list in parse_aia_state_meets.py

Usage:
    python update_state_parser.py --year 2026 --date "11/X/2026"
"""

import argparse
import re
from pathlib import Path

def update_parser(year, date):
    """Add new year to AIA_STATE_MEETS list"""
    parser_file = Path('parse_aia_state_meets.py')
    
    if not parser_file.exists():
        print(f"❌ Error: {parser_file} not found")
        return False
    
    content = parser_file.read_text()
    
    # Check if year already exists
    if f'"year": {year}' in content:
        print(f"✅ Year {year} already in parser")
        return True
    
    # Find the AIA_STATE_MEETS list
    pattern = r'(AIA_STATE_MEETS = \[\s*)'
    match = re.search(pattern, content)
    
    if not match:
        print("❌ Error: Could not find AIA_STATE_MEETS list")
        return False
    
    # Insert new entry at the beginning of the list
    new_entry = f'    {{"year": {year}, "file_id": None, "date": "{date}"}},\n'
    
    # Find position after the opening bracket
    insert_pos = match.end()
    new_content = content[:insert_pos] + new_entry + content[insert_pos:]
    
    # Write back
    parser_file.write_text(new_content)
    
    print(f"✅ Added year {year} to AIA state parser")
    print(f"   Entry: {new_entry.strip()}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Update AIA state parser with new year')
    parser.add_argument('--year', required=True, type=int, help='Year to add (e.g., 2026)')
    parser.add_argument('--date', help='Date of state meet (e.g., "11/X/2026")')
    
    args = parser.parse_args()
    
    # If date not provided, use a placeholder
    date = args.date or f"11/X/{args.year}"
    
    if update_parser(args.year, date):
        print("\n✅ Parser updated successfully!")
        print("   Next: Run python parse_aia_state_meets.py")
    else:
        print("\n❌ Failed to update parser")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

