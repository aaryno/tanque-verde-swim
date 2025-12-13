#!/usr/bin/env python3
"""
Apply all harvested relay splits to the 2025 Records Broken section.
Updates both NEW and OLD records with splits.
"""

import re
from pathlib import Path

# All splits data from our harvest
SPLITS_DATA = {
    # Boys 200 Medley NEW - already in HTML, just verify
    'boys_200_medley_new': {
        'swimmers': [
            {'name': 'Kent Olsson', 'grade': 'FR', 'stroke': 'Backstroke', 'split': '28.12'},
            {'name': 'Wade Olsson', 'grade': 'JR', 'stroke': 'Breaststroke', 'split': '27.30'},
            {'name': 'Jackson Eftekhar', 'grade': 'JR', 'stroke': 'Butterfly', 'split': '24.56'},
            {'name': 'Zachary Duerkop', 'grade': 'SR', 'stroke': 'Freestyle', 'split': '21.82'},
        ]
    },
    
    # Boys 200 Medley OLD (1:45.73)
    'boys_200_medley_old': {
        'swimmers': [
            {'name': 'Wade Olsson', 'grade': 'SO', 'stroke': 'Backstroke', 'split': '28.05'},
            {'name': 'Zachary Duerkop', 'grade': 'JR', 'stroke': 'Breaststroke', 'split': '27.24'},
            {'name': 'Jackson Eftekhar', 'grade': 'SO', 'stroke': 'Butterfly', 'split': '25.96'},
            {'name': 'Jackson Machamer', 'grade': 'JR', 'stroke': 'Freestyle', 'split': '24.48'},
        ]
    },
    
    # Boys 200 Free NEW - already in HTML
    'boys_200_free_new': {
        'swimmers': [
            {'name': 'Jackson Eftekhar', 'grade': 'JR', 'stroke': 'Freestyle', 'split': '23.21'},
            {'name': 'Grayson The', 'grade': 'SR', 'stroke': 'Freestyle', 'split': '23.25'},
            {'name': 'Wade Olsson', 'grade': 'JR', 'stroke': 'Freestyle', 'split': '22.31'},
            {'name': 'Zachary Duerkop', 'grade': 'SR', 'stroke': 'Freestyle', 'split': '21.68'},
        ]
    },
    
    # Boys 200 Free OLD (1:32.46)
    'boys_200_free_old': {
        'swimmers': [
            {'name': 'Trevor Clausen', 'grade': None, 'stroke': 'Freestyle', 'split': '23.29'},
            {'name': 'Logan Radomsky', 'grade': None, 'stroke': 'Freestyle', 'split': '23.57'},
            {'name': 'Nicholas Spilotro', 'grade': None, 'stroke': 'Freestyle', 'split': '23.41'},
            {'name': 'Sam Stott', 'grade': None, 'stroke': 'Freestyle', 'split': '22.19'},
        ]
    },
    
    # Boys 400 Free NEW - already in HTML
    'boys_400_free_new': {
        'swimmers': [
            {'name': 'Wade Olsson', 'grade': 'JR', 'stroke': 'Freestyle', 'split': '50.09'},
            {'name': 'Grayson The', 'grade': 'SR', 'stroke': 'Freestyle', 'split': '52.41'},
            {'name': 'Jackson Eftekhar', 'grade': 'JR', 'stroke': 'Freestyle', 'split': '50.83'},
            {'name': 'Zachary Duerkop', 'grade': 'SR', 'stroke': 'Freestyle', 'split': '47.27'},
        ]
    },
    
    # Boys 400 Free OLD (3:26.64)
    'boys_400_free_old': {
        'swimmers': [
            {'name': 'Nicholas Cusson', 'grade': None, 'stroke': 'Freestyle', 'split': '48.68'},
            {'name': 'Alejandro Alvarez', 'grade': None, 'stroke': 'Freestyle', 'split': '54.53'},
            {'name': 'Nolan Radomsky', 'grade': None, 'stroke': 'Freestyle', 'split': '55.69'},
            {'name': 'Samuel Stott', 'grade': None, 'stroke': 'Freestyle', 'split': '47.74'},
        ]
    },
    
    # Girls 200 Medley NEW (2:00.57) - Note: MaxPreps shows Stella Eftekhar, not Hadley Cusson
    'girls_200_medley_new': {
        'swimmers': [
            {'name': 'Logan Sulger', 'grade': 'SR', 'stroke': 'Backstroke', 'split': '30.03'},
            {'name': 'Adrianna Witte', 'grade': 'SR', 'stroke': 'Breaststroke', 'split': '34.10'},
            {'name': 'Hadley Cusson', 'grade': 'JR', 'stroke': 'Butterfly', 'split': '29.66'},
            {'name': 'Isla Cerepak', 'grade': 'FR', 'stroke': 'Freestyle', 'split': '26.78'},
        ]
    },
    
    # Girls 200 Medley OLD (2:00.67)
    'girls_200_medley_old': {
        'swimmers': [
            {'name': 'Sarynn Patterson', 'grade': None, 'stroke': 'Backstroke', 'split': '30.37'},
            {'name': 'Isabelle Sansom', 'grade': None, 'stroke': 'Breaststroke', 'split': '34.69'},
            {'name': 'Paisley White', 'grade': None, 'stroke': 'Butterfly', 'split': '28.52'},
            {'name': 'Maggie Colombo', 'grade': None, 'stroke': 'Freestyle', 'split': '27.09'},
        ]
    },
}

def generate_swimmer_html(swimmer, include_stroke=True, include_time=True):
    """Generate HTML for a single swimmer entry with splits"""
    grade_badge = f' <span class="grade-badge grade-{swimmer["grade"].lower()}">{swimmer["grade"]}</span>' if swimmer.get('grade') else ''
    
    if include_stroke and include_time and swimmer.get('split'):
        return f'''                                        <div class="swimmer-entry">
                                            <span class="swimmer-name">{swimmer['name']}{grade_badge}</span>
                                            <span class="swimmer-stroke">{swimmer.get('stroke', 'Freestyle')}</span>
                                            <span class="swimmer-time">{swimmer['split']}</span>
                                        </div>'''
    else:
        return f'''                                        <div>{swimmer['name']}{grade_badge}</div>'''

def generate_swimmers_block(swimmers, include_stroke=True, include_time=True):
    """Generate HTML for all swimmers in a relay"""
    return '\n'.join([generate_swimmer_html(s, include_stroke, include_time) for s in swimmers])

def update_relay_section(content, relay_title, new_swimmers, old_swimmers):
    """Update a relay section with new and old swimmer splits"""
    
    # Find the start and end of this relay card
    card_start_pattern = rf'<h5 class="card-title">{re.escape(relay_title)}'
    card_start_match = re.search(card_start_pattern, content)
    
    if not card_start_match:
        print(f"  Could not find card for {relay_title}")
        return content, False
    
    # Find the end - look for the next col-md-6 or closing tag
    card_start = card_start_match.start()
    
    # Find the improvement line which marks the end of this card's content
    improvement_pattern = r'<p class="mb-0 text-success mt-3"><strong>Improvement:'
    improvement_match = re.search(improvement_pattern, content[card_start:])
    if not improvement_match:
        print(f"  Could not find improvement line for {relay_title}")
        return content, False
    
    card_end = card_start + improvement_match.end()
    card_content = content[card_start:card_end]
    
    # Update NEW swimmers section
    new_pattern = r'(<!-- NEW Record -->.*?<div class="relay-swimmers">)(.*?)(</div>\s*<div class="relay-meet">)'
    new_html = generate_swimmers_block(new_swimmers)
    card_content = re.sub(new_pattern, r'\1\n' + new_html + r'\n                                    \3', card_content, flags=re.DOTALL)
    
    # Update OLD swimmers section - need to handle the simpler div format too
    old_pattern = r'(<!-- OLD Record -->.*?<div class="relay-swimmers">)(.*?)(</div>\s*<div class="relay-meet">)'
    old_html = generate_swimmers_block(old_swimmers)
    card_content = re.sub(old_pattern, r'\1\n' + old_html + r'\n                                    \3', card_content, flags=re.DOTALL)
    
    # Rebuild content
    new_content = content[:card_start] + card_content + content[card_end:]
    
    return new_content, True

def main():
    # Read HTML
    with open('docs/index.html', 'r') as f:
        content = f.read()
    
    updates = [
        ('Boys 200 Medley Relay', SPLITS_DATA['boys_200_medley_new']['swimmers'], SPLITS_DATA['boys_200_medley_old']['swimmers']),
        ('Boys 200 Free Relay', SPLITS_DATA['boys_200_free_new']['swimmers'], SPLITS_DATA['boys_200_free_old']['swimmers']),
        ('Boys 400 Free Relay', SPLITS_DATA['boys_400_free_new']['swimmers'], SPLITS_DATA['boys_400_free_old']['swimmers']),
        ('Girls 200 Medley Relay', SPLITS_DATA['girls_200_medley_new']['swimmers'], SPLITS_DATA['girls_200_medley_old']['swimmers']),
    ]
    
    for title, new_swimmers, old_swimmers in updates:
        print(f"\nUpdating {title}...")
        content, success = update_relay_section(content, title, new_swimmers, old_swimmers)
        if success:
            print(f"  ✓ Updated {title}")
        else:
            print(f"  ✗ Failed to update {title}")
    
    # Write back
    with open('docs/index.html', 'w') as f:
        f.write(content)
    
    print("\n✓ All relay splits updated!")

if __name__ == "__main__":
    main()

