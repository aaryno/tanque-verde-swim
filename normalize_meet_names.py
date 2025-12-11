#!/usr/bin/env python3
"""
Normalize meet names in markdown files:
1. Standardize state meet names to "{YYYY} D-{2 or 3} AIA [Boys|Girls] State Championship"
2. Remove "(AZ)" from all meet names
3. Remove location info from state championships
"""

import re
from pathlib import Path

def normalize_meet_name(meet):
    """Normalize a meet name"""
    original = meet
    
    # Remove trailing (AZ) or other state abbreviations
    meet = re.sub(r'\s*\([A-Z]{2}\)\s*$', '', meet)
    
    # Remove trailing location for state meets like (Paradise Valley, AZ) or (Mesa, AZ)
    meet = re.sub(r'\s*\([^)]+,\s*AZ\)\s*$', '', meet)
    
    # Standardize various state meet formats
    state_patterns = [
        # 2024 D3 State Championship -> 2024 D-3 AIA State Championship
        (r'^(\d{4})\s+D-?(\d)\s+(?:AIA\s+)?State\s+Championshi[ps]*$', r'\1 D-\2 AIA State Championship'),
        
        # 2022 D-3 AIA Boys State Championships -> 2022 D-3 AIA Boys State Championship
        (r'^(\d{4})\s+D-?(\d)\s+AIA\s+(Boys|Girls)\s+State\s+Championshi[ps]*$', r'\1 D-\2 AIA \3 State Championship'),
        
        # 2025 D-3 AIA State Championships -> 2025 D-3 AIA State Championship
        (r'^(\d{4})\s+D-?(\d)\s+AIA\s+State\s+Championshi[ps]*$', r'\1 D-\2 AIA State Championship'),
        
        # AIA D-III Boys State Meet -> AIA D-3 Boys State Championship  
        (r'^AIA\s+D-?III\s+(Boys|Girls)\s+State\s+Meet$', r'AIA D-3 \1 State Championship'),
        
        # AIA State Meet - D3 -> AIA D-3 State Championship
        (r'^AIA\s+State\s+Meet\s*[-–]\s*D-?3$', r'AIA D-3 State Championship'),
        
        # 2019 AIA D-III State Meet -> 2019 D-3 AIA State Championship
        (r'^(\d{4})\s+AIA\s+D-?III\s+State\s+Meet$', r'\1 D-3 AIA State Championship'),
        
        # 2016 AIA Division III State Swimming & Diving Championships -> 2016 D-3 AIA State Championship
        (r'^(\d{4})\s+AIA\s+Division\s+III\s+State\s+Swimming\s*&?\s*Diving\s+Championshi[ps]*$', 
         r'\1 D-3 AIA State Championship'),
        
        # 2015 AIA Division II State Swimming & Diving Championships -> 2015 D-2 AIA State Championship
        (r'^(\d{4})\s+AIA\s+Division\s+II\s+State\s+Swimming\s*&?\s*Diving\s+Championshi[ps]*$', 
         r'\1 D-2 AIA State Championship'),
        
        # 2010 AIA Division I-II State Championships -> 2010 AIA D-2 State Championship
        (r'^(\d{4})\s+AIA\s+Division\s+I-II\s+State\s+Championshi[ps]*$', r'\1 D-2 AIA State Championship'),
        
        # 2009 AIA 1A-5A State Championships -> 2009 AIA State Championship
        (r'^(\d{4})\s+AIA\s+1A-5A\s+State\s+Championshi[ps]*$', r'\1 AIA State Championship'),
        
        # 2021 D-3 AIA State Championships -> 2021 D-3 AIA State Championship
        (r'^(\d{4})\s+D-?(\d)\s+AIA\s+State\s+Championshi[ps]*$', r'\1 D-\2 AIA State Championship'),
        
        # Division III - State Swim & Dive -> D-3 AIA State Championship
        (r'^Division\s+III\s*[-–]\s*State\s+Swim\s*&?\s*Dive$', r'D-3 AIA State Championship'),
    ]
    
    for pattern, replacement in state_patterns:
        new_meet = re.sub(pattern, replacement, meet, flags=re.IGNORECASE)
        if new_meet != meet:
            meet = new_meet
            break
    
    return meet

def is_meet_name(text):
    """Check if text looks like a meet name"""
    text = text.replace('**', '').strip()
    # Meet names typically contain keywords like:
    meet_keywords = ['Classic', 'Invitational', 'Invite', 'Championships', 'Championship', 
                     'State', 'Qualifier', 'Relays', 'Meet', 'AIA', 'Regional', 'Tournament']
    return any(kw.lower() in text.lower() for kw in meet_keywords)

def process_markdown_file(filepath):
    """Process a markdown file and normalize meet names"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Find table rows with meet names (last column typically)
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if '|' in line and not line.startswith('|--') and not line.startswith('| Rank') and not line.startswith('|:'):
            # Split by | and process last meaningful column
            parts = line.split('|')
            if len(parts) >= 6:  # Table with meet column
                # Last non-empty part is usually the meet
                for i in range(len(parts) - 1, 0, -1):
                    original_meet = parts[i].strip()
                    if original_meet and original_meet not in ['Meet', 'meet', '', '-']:
                        # Only process if it looks like a meet name
                        clean_meet = original_meet.replace('**', '')
                        if is_meet_name(clean_meet):
                            was_bold = original_meet.startswith('**') and original_meet.endswith('**')
                            
                            normalized = normalize_meet_name(clean_meet)
                            
                            if normalized != clean_meet:
                                if was_bold:
                                    parts[i] = f' **{normalized}** '
                                else:
                                    parts[i] = f' {normalized} '
                                changes.append((clean_meet, normalized))
                        break
            
            new_lines.append('|'.join(parts))
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    if new_content != original_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return changes
    
    return []

def main():
    print("Normalizing meet names in markdown files...")
    print("=" * 60)
    
    records_dir = Path('records')
    all_changes = []
    
    for md_file in sorted(records_dir.glob('*.md')):
        changes = process_markdown_file(md_file)
        if changes:
            print(f"\n{md_file.name}:")
            for old, new in changes[:5]:  # Show first 5
                print(f"  '{old}' -> '{new}'")
            if len(changes) > 5:
                print(f"  ... and {len(changes) - 5} more changes")
            all_changes.extend(changes)
    
    print(f"\n{'=' * 60}")
    print(f"Total changes: {len(all_changes)}")
    print("\nRun generate_website.py to regenerate HTML.")

if __name__ == '__main__':
    main()

