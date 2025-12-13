#!/usr/bin/env python3
"""
Extract relay splits from harvested data and apply them to the HTML.
Based on analysis of the data, we can match:
- Boys 200 Medley NEW (1:41.80): Entry with Back/Breast/Fly/Free + Kent, Wade, Jackson E, Zachary
- Boys 200 Free (1:30.45): Entry 1 with 4 splits totaling 1:30.45
- Boys 400 Free (3:20.60): Entry 11 with 8 splits totaling 3:20.60
"""

import json
import re
from pathlib import Path

def clean_name(name):
    """Remove grade suffix from name"""
    if ' - ' in name:
        return name.split(' - ')[0].strip()
    return name.strip()

def get_grade(name):
    """Extract grade from name like 'Kent Olsson - Fr.'"""
    if ' - ' in name:
        grade_map = {'Fr.': 'FR', 'So.': 'SO', 'Jr.': 'JR', 'Sr.': 'SR'}
        grade_str = name.split(' - ')[1].strip()
        return grade_map.get(grade_str, '')
    return ''

def format_split(split_str):
    """Format split time - remove leading 00:"""
    if split_str.startswith('00:'):
        return split_str[3:]
    return split_str

def load_and_process_splits():
    """Load harvested splits and extract the ones we need"""
    
    with open('data/relay_splits_2025-26_boys.json', 'r') as f:
        boys_splits = json.load(f)
    
    results = {}
    
    # Find Boys 200 Medley NEW - entry with proper stroke labels and Kent, Wade, Jackson E, Zachary
    for entry in boys_splits:
        if entry.get('legs') == ['Back', 'Breast', 'Fly', 'Free']:
            swimmers = [clean_name(s) for s in entry['swimmers']]
            if 'Kent Olsson' in swimmers and 'Wade Olsson' in swimmers:
                results['boys_200_medley_new'] = {
                    'swimmers': [
                        {'name': clean_name(entry['swimmers'][0]), 'grade': get_grade(entry['swimmers'][0]), 'stroke': 'Backstroke', 'split': format_split(entry['splits'][0])},
                        {'name': clean_name(entry['swimmers'][1]), 'grade': get_grade(entry['swimmers'][1]), 'stroke': 'Breaststroke', 'split': format_split(entry['splits'][1])},
                        {'name': clean_name(entry['swimmers'][2]), 'grade': get_grade(entry['swimmers'][2]), 'stroke': 'Butterfly', 'split': format_split(entry['splits'][2])},
                        {'name': clean_name(entry['swimmers'][3]), 'grade': get_grade(entry['swimmers'][3]), 'stroke': 'Freestyle', 'split': format_split(entry['splits'][3])},
                    ]
                }
                print("✓ Found Boys 200 Medley NEW splits")
                break
    
    # Find Boys 200 Free (1:30.45) - 4 splits totaling ~90.45 seconds
    for entry in boys_splits:
        if len(entry.get('splits', [])) == 4 and entry.get('legs', [None])[0] in ['Split 1', None]:
            # Check if this is a free relay (not medley)
            if entry.get('legs') != ['Back', 'Breast', 'Fly', 'Free']:
                swimmers = [clean_name(s) for s in entry['swimmers']]
                # Calculate total time
                total = sum(float(format_split(s)) for s in entry['splits'])
                if 90.0 <= total <= 91.0:  # About 1:30.45
                    results['boys_200_free_new'] = {
                        'swimmers': [
                            {'name': clean_name(entry['swimmers'][i]), 'grade': get_grade(entry['swimmers'][i]), 'stroke': 'Freestyle', 'split': format_split(entry['splits'][i])}
                            for i in range(4)
                        ]
                    }
                    print(f"✓ Found Boys 200 Free splits (total: {total:.2f}s = 1:{total:.2f})")
                    break
    
    # Find Boys 400 Free (3:20.60) - 8 splits totaling ~200.60 seconds
    for entry in boys_splits:
        if len(entry.get('splits', [])) == 8:
            swimmers_raw = entry['swimmers']
            splits_raw = entry['splits']
            
            # Group into 4 swimmers with 2 splits each (100y = 50y + 50y)
            swimmer_splits = []
            for i in range(0, 8, 2):
                name = clean_name(swimmers_raw[i])
                grade = get_grade(swimmers_raw[i])
                split1 = float(format_split(splits_raw[i]))
                split2 = float(format_split(splits_raw[i+1]))
                total_100 = split1 + split2
                swimmer_splits.append({
                    'name': name,
                    'grade': grade,
                    'stroke': 'Freestyle',
                    'split': f"{total_100:.2f}"
                })
            
            # Calculate total relay time
            total_time = sum(float(s['split']) for s in swimmer_splits)
            if 200.0 <= total_time <= 201.0:  # About 3:20.60
                results['boys_400_free_new'] = {'swimmers': swimmer_splits}
                print(f"✓ Found Boys 400 Free splits (total: {total_time:.2f}s = 3:{total_time-180:.2f})")
                break
    
    return results

def generate_swimmer_entries_html(swimmers, include_stroke=True, include_time=True):
    """Generate HTML for swimmer entries with splits"""
    html_parts = []
    
    for swimmer in swimmers:
        grade_badge = f' <span class="grade-badge grade-{swimmer["grade"].lower()}">{swimmer["grade"]}</span>' if swimmer.get('grade') else ''
        
        if include_stroke and include_time and swimmer.get('split'):
            html_parts.append(f'''                                        <div class="swimmer-entry">
                                            <span class="swimmer-name">{swimmer['name']}{grade_badge}</span>
                                            <span class="swimmer-stroke">{swimmer.get('stroke', 'Freestyle')}</span>
                                            <span class="swimmer-time">{swimmer['split']}</span>
                                        </div>''')
        else:
            html_parts.append(f'''                                        <div>{swimmer['name']}{grade_badge}</div>''')
    
    return '\n'.join(html_parts)

def update_html_with_splits(splits_data):
    """Update the index.html with the extracted splits"""
    
    with open('docs/index.html', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    # Update Boys 200 Free Relay
    if 'boys_200_free_new' in splits_data:
        swimmers = splits_data['boys_200_free_new']['swimmers']
        
        # Find the section to replace
        # Pattern: From "relay-swimmers" div until closing </div> for Boys 200 Free Relay NEW
        pattern = r'(<h5 class="card-title">Boys 200 Free Relay.*?<!-- NEW Record -->.*?<div class="relay-swimmers">)\s*<div>Wade Olsson.*?</div>\s*<div>Jackson Eftekhar.*?</div>\s*<div>Grayson The.*?</div>\s*<div>Zachary Duerkop.*?</div>(\s*</div>)'
        
        new_swimmers_html = generate_swimmer_entries_html(swimmers)
        replacement = r'\1\n' + new_swimmers_html + r'\2'
        
        new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
        if count > 0:
            content = new_content
            updates_made += 1
            print("✓ Updated Boys 200 Free Relay with splits")
    
    # Update Boys 400 Free Relay
    if 'boys_400_free_new' in splits_data:
        swimmers = splits_data['boys_400_free_new']['swimmers']
        
        pattern = r'(<h5 class="card-title">Boys 400 Free Relay.*?<!-- NEW Record -->.*?<div class="relay-swimmers">)\s*<div>Wade Olsson.*?</div>\s*<div>Jackson Eftekhar.*?</div>\s*<div>Grayson The.*?</div>\s*<div>Zachary Duerkop.*?</div>(\s*</div>)'
        
        new_swimmers_html = generate_swimmer_entries_html(swimmers)
        replacement = r'\1\n' + new_swimmers_html + r'\2'
        
        new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
        if count > 0:
            content = new_content
            updates_made += 1
            print("✓ Updated Boys 400 Free Relay with splits")
    
    # Write back
    with open('docs/index.html', 'w') as f:
        f.write(content)
    
    print(f"\nMade {updates_made} updates to index.html")

def main():
    print("Extracting relay splits from harvested data...\n")
    
    splits = load_and_process_splits()
    
    print(f"\nExtracted {len(splits)} relay split sets")
    
    for relay_key, data in splits.items():
        print(f"\n{relay_key}:")
        for swimmer in data['swimmers']:
            print(f"  {swimmer['name']} ({swimmer.get('stroke', 'Free')}): {swimmer.get('split', 'N/A')}")
    
    # Save extracted splits
    with open('data/extracted_relay_splits.json', 'w') as f:
        json.dump(splits, f, indent=2)
    
    print("\nSaved extracted splits to data/extracted_relay_splits.json")
    
    # Update HTML
    print("\n" + "="*50)
    print("Updating HTML with splits...")
    update_html_with_splits(splits)

if __name__ == "__main__":
    main()

