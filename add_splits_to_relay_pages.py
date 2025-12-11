#!/usr/bin/env python3
"""
Add relay splits to the boys and girls relay records pages.
This script modifies the generated HTML to include splits in the expanded details
for each relay where we have splits data.
"""

import json
import re
from pathlib import Path

def clean_name(name):
    """Remove grade suffix from name"""
    if ' - ' in name:
        return name.split(' - ')[0].strip()
    return name.strip()

def get_last_name(name):
    """Get last name from full name"""
    cleaned = clean_name(name)
    parts = cleaned.split()
    return parts[-1] if parts else cleaned

def calc_total(splits):
    """Calculate total time from splits"""
    total = 0
    for s in splits:
        if not s or s.strip() == '':
            continue
        if s.startswith('00:'):
            s = s[3:]
        try:
            total += float(s)
        except:
            pass
    return total

def load_all_splits():
    """Load all harvested splits from historical data"""
    splits_dir = Path("data/historical_splits")
    all_splits = {'boys': [], 'girls': []}
    
    for year_file in splits_dir.glob("splits_*.json"):
        with open(year_file, 'r') as f:
            year_data = json.load(f)
            for gender in ['boys', 'girls']:
                if gender in year_data:
                    all_splits[gender].extend(year_data[gender])
    
    return all_splits

def format_split_time(split):
    """Format a split time - remove leading 00:"""
    if split.startswith('00:'):
        return split[3:]
    return split

def match_relay_to_splits(relay_swimmers, relay_time, all_splits, relay_type='medley'):
    """Try to find splits that match a relay based on swimmers and time"""
    
    relay_last_names = set([get_last_name(s) for s in relay_swimmers])
    
    # Convert relay time to seconds for comparison
    relay_seconds = None
    time_str = relay_time.strip()
    if ':' in time_str:
        parts = time_str.split(':')
        try:
            relay_seconds = int(parts[0]) * 60 + float(parts[1])
        except:
            pass
    
    for splits_entry in all_splits:
        # Get last names from splits
        splits_swimmers = splits_entry.get('swimmers', [])
        if len(splits_swimmers) < 4:
            continue
            
        # For 4-swimmer entries (200 relays)
        if len(splits_entry.get('splits', [])) == 4:
            splits_last_names = set([get_last_name(clean_name(s)) for s in splits_swimmers[:4]])
            
            # Check if last names match
            if relay_last_names == splits_last_names:
                # Verify time matches approximately
                total = calc_total(splits_entry['splits'])
                if relay_seconds and abs(total - relay_seconds) < 2:
                    return {
                        'swimmers': [
                            {
                                'name': clean_name(splits_swimmers[i]),
                                'stroke': splits_entry.get('legs', ['', '', '', ''])[i] if splits_entry.get('legs') else '',
                                'split': format_split_time(splits_entry['splits'][i])
                            }
                            for i in range(4)
                        ]
                    }
        
        # For 8-swimmer entries (400 Free relays)
        elif len(splits_entry.get('splits', [])) == 8:
            # Get unique swimmers (each appears twice)
            unique_swimmers = []
            for i in range(0, 8, 2):
                unique_swimmers.append(clean_name(splits_swimmers[i]))
            
            splits_last_names = set([get_last_name(s) for s in unique_swimmers])
            
            if relay_last_names == splits_last_names:
                # Combine 50y splits into 100y splits
                combined_splits = []
                for i in range(0, 8, 2):
                    s1 = format_split_time(splits_entry['splits'][i])
                    s2 = format_split_time(splits_entry['splits'][i+1])
                    try:
                        total_100 = float(s1) + float(s2)
                        combined_splits.append(f"{total_100:.2f}")
                    except:
                        combined_splits.append('')
                
                total = sum(float(s) for s in combined_splits if s)
                if relay_seconds and abs(total - relay_seconds) < 2:
                    return {
                        'swimmers': [
                            {
                                'name': unique_swimmers[i],
                                'stroke': 'Freestyle',
                                'split': combined_splits[i]
                            }
                            for i in range(4)
                        ]
                    }
    
    return None

def add_splits_to_html(html_content, all_splits, gender):
    """Add splits to the relay records HTML"""
    
    # Process each relay table
    # Look for patterns like:
    # <td>01:42.54</td>
    # <td>Kent Olsson, Wade Olsson, Jackson Eftekhar, Grayson The</td>
    
    # Find all table rows with relay data
    row_pattern = r'<tr>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>([\d:\.]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*</tr>'
    
    def replace_row(match):
        rank = match.group(1)
        time = match.group(2)
        participants = match.group(3)
        date = match.group(4)
        meet = match.group(5)
        
        # Parse participants
        swimmers = [s.strip() for s in participants.split(',')]
        
        # Try to find splits
        splits_data = match_relay_to_splits(swimmers, time, all_splits[gender])
        
        if splits_data:
            # Generate splits HTML
            splits_html = '<div class="relay-splits">'
            for swimmer in splits_data['swimmers']:
                stroke = swimmer.get('stroke', '')
                if stroke in ['Back', 'Split 1']:
                    stroke = 'Back'
                elif stroke in ['Breast', 'Split 2']:
                    stroke = 'Breast'
                elif stroke in ['Fly', 'Split 3']:
                    stroke = 'Fly'
                elif stroke in ['Free', 'Split 4']:
                    stroke = 'Free'
                elif stroke == 'Freestyle':
                    stroke = 'Free'
                
                splits_html += f'<span class="split-entry"><span class="split-name">{swimmer["name"]}</span>'
                if stroke:
                    splits_html += f'<span class="split-stroke">{stroke}</span>'
                splits_html += f'<span class="split-time">{swimmer["split"]}</span></span>'
            splits_html += '</div>'
            
            # Create enhanced participants cell with splits
            enhanced_participants = f'{participants}{splits_html}'
            
            return f'''<tr>
<td>{rank}</td>
<td>{time}</td>
<td class="has-splits">{enhanced_participants}</td>
<td>{date}</td>
<td>{meet}</td>
</tr>'''
        
        # No splits found, return original
        return match.group(0)
    
    # Also handle record-holder class rows
    row_pattern_record = r'<tr>\s*<td class="record-holder">(\d+)</td>\s*<td class="record-holder">([\d:\.]+)</td>\s*<td class="record-holder">([^<]+)</td>\s*<td class="record-holder">([^<]+)</td>\s*<td class="record-holder">([^<]+)</td>\s*</tr>'
    
    def replace_record_row(match):
        rank = match.group(1)
        time = match.group(2)
        participants = match.group(3)
        date = match.group(4)
        meet = match.group(5)
        
        swimmers = [s.strip() for s in participants.split(',')]
        splits_data = match_relay_to_splits(swimmers, time, all_splits[gender])
        
        if splits_data:
            splits_html = '<div class="relay-splits">'
            for swimmer in splits_data['swimmers']:
                stroke = swimmer.get('stroke', '')
                if stroke in ['Back', 'Split 1']:
                    stroke = 'Back'
                elif stroke in ['Breast', 'Split 2']:
                    stroke = 'Breast'
                elif stroke in ['Fly', 'Split 3']:
                    stroke = 'Fly'
                elif stroke in ['Free', 'Split 4']:
                    stroke = 'Free'
                elif stroke == 'Freestyle':
                    stroke = 'Free'
                
                splits_html += f'<span class="split-entry"><span class="split-name">{swimmer["name"]}</span>'
                if stroke:
                    splits_html += f'<span class="split-stroke">{stroke}</span>'
                splits_html += f'<span class="split-time">{swimmer["split"]}</span></span>'
            splits_html += '</div>'
            
            enhanced_participants = f'{participants}{splits_html}'
            
            return f'''<tr>
<td class="record-holder">{rank}</td>
<td class="record-holder">{time}</td>
<td class="record-holder has-splits">{enhanced_participants}</td>
<td class="record-holder">{date}</td>
<td class="record-holder">{meet}</td>
</tr>'''
        
        return match.group(0)
    
    # Apply replacements
    html_content = re.sub(row_pattern_record, replace_record_row, html_content, flags=re.DOTALL)
    html_content = re.sub(row_pattern, replace_row, html_content, flags=re.DOTALL)
    
    return html_content

def add_splits_css(html_content):
    """Add CSS for splits display if not already present"""
    
    css = '''
    /* Relay Splits Styling */
    .relay-splits {
        display: none;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }
    .has-splits .relay-details.show + .relay-splits,
    .has-splits:hover .relay-splits {
        display: block;
    }
    .split-entry {
        display: flex;
        justify-content: space-between;
        padding: 0.2rem 0;
        border-bottom: 1px solid #eee;
    }
    .split-entry:last-child {
        border-bottom: none;
    }
    .split-name {
        flex: 2;
    }
    .split-stroke {
        flex: 1;
        text-align: center;
        font-style: italic;
        color: #666;
    }
    .split-time {
        flex: 1;
        text-align: right;
        font-family: monospace;
        color: var(--tvhs-primary);
    }
    '''
    
    # Add CSS before </head>
    if 'relay-splits' not in html_content:
        html_content = html_content.replace('</head>', f'<style>{css}</style>\n</head>')
    
    return html_content

def update_js_for_splits(html_content):
    """Update the JavaScript to show splits in expanded details"""
    
    # Add splits display to the expanded details
    new_js = '''
                    // Add splits if present
                    const splitsDiv = cells[2].querySelector('.relay-splits');
                    if (splitsDiv) {
                        details.appendChild(splitsDiv.cloneNode(true));
                        splitsDiv.style.display = 'none'; // Hide original
                    }
'''
    
    # Insert after the meet details are added
    insert_after = "details.appendChild(meetDiv);"
    if new_js.strip() not in html_content:
        html_content = html_content.replace(insert_after, insert_after + '\n' + new_js)
    
    return html_content

def main():
    print("Loading harvested splits...")
    all_splits = load_all_splits()
    print(f"  Loaded {len(all_splits['boys'])} boys relay entries")
    print(f"  Loaded {len(all_splits['girls'])} girls relay entries")
    
    for gender in ['boys', 'girls']:
        html_file = Path(f"docs/records/{gender}-relays.html")
        
        if not html_file.exists():
            print(f"\n✗ {html_file} not found")
            continue
        
        print(f"\nProcessing {html_file}...")
        
        with open(html_file, 'r') as f:
            content = f.read()
        
        # Add splits to HTML
        content = add_splits_to_html(content, all_splits, gender)
        
        # Add CSS for splits
        content = add_splits_css(content)
        
        # Update JS to show splits
        content = update_js_for_splits(content)
        
        with open(html_file, 'w') as f:
            f.write(content)
        
        print(f"  ✓ Updated {html_file}")
    
    print("\n✓ All relay pages updated with splits!")

if __name__ == "__main__":
    main()

