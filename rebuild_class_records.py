#!/usr/bin/env python3
"""
Rebuild the Class Records Broken section with:
1. Old record information (who held it, when, what time)
2. Time drop badges
3. Organized by grade level (Freshman, Sophomore, Junior, Senior)
4. Omit grades with no records broken
"""

import re
from pathlib import Path
from collections import defaultdict

def parse_time(time_str):
    """Convert time string to seconds"""
    if ':' in time_str:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + float(parts[1])
    return float(time_str)

def format_time_drop(drop_seconds):
    """Format time drop for display"""
    if drop_seconds < 0:
        return f"+{abs(drop_seconds):.2f}s"
    return f"-{drop_seconds:.2f}s"

def get_pb_badge_class(drop_seconds, event):
    """Get PB badge class based on time drop per 50y"""
    if drop_seconds <= 0:
        return "pb-verylightgray"  # Slower time
    
    # Calculate per 50y
    if "50" in event and "500" not in event:
        per_50y = drop_seconds / 1
    elif "100" in event:
        per_50y = drop_seconds / 2
    elif "200" in event:
        per_50y = drop_seconds / 4
    elif "500" in event:
        per_50y = drop_seconds / 10
    else:
        per_50y = drop_seconds / 2
    
    if per_50y >= 5.0:
        return "pb-black"
    elif per_50y >= 4.0:
        return "pb-darkgray"
    elif per_50y >= 3.0:
        return "pb-gray"
    elif per_50y >= 2.0:
        return "pb-mediumgray"
    elif per_50y >= 1.0:
        return "pb-lightgray"
    elif per_50y >= 0.5:
        return "pb-verylightgray"
    else:
        return "pb-verylightgray"

# Define 2025 class records broken with OLD record information
RECORDS_2025 = [
    # Boys
    {
        'gender': 'boys',
        'grade': 'Freshman',
        'event': '500 Freestyle',
        'time': '5:07.85',
        'athlete': 'Kent Olsson',
        'date': 'Nov 8, 2025',
        'meet': 'State Championship',
        'also_overall': False,
        'old_record': None  # First-ever freshman record
    },
    {
        'gender': 'boys',
        'grade': 'Freshman',
        'event': '100 Backstroke',
        'time': '59.71',
        'athlete': 'Kent Olsson',
        'date': 'Oct 24, 2025',
        'meet': 'Southern AZ Qualifier',
        'also_overall': False,
        'old_record': None  # First-ever freshman record
    },
    {
        'gender': 'boys',
        'grade': 'Junior',
        'event': '100 Butterfly',
        'time': '54.41',
        'athlete': 'Jackson Eftekhar',
        'date': 'Nov 8, 2025',
        'meet': 'State Championship',
        'also_overall': False,
        'old_record': None  # First-ever junior record
    },
    {
        'gender': 'boys',
        'grade': 'Junior',
        'event': '200 Individual Medley',
        'time': '1:57.78',
        'athlete': 'Wade Olsson',
        'date': 'Nov 8, 2025',
        'meet': 'State Championship',
        'also_overall': True,
        'old_record': None  # First-ever junior record
    },
    {
        'gender': 'boys',
        'grade': 'Senior',
        'event': '100 Butterfly',
        'time': '52.48',
        'athlete': 'Zachary Duerkop',
        'date': 'Nov 8, 2025',
        'meet': 'State Championship',
        'also_overall': True,
        'old_record': {
            'time': '54.04',
            'athlete': 'Nicholas Cusson',
            'date': 'Nov 04, 2023',
            'meet': '2023 D-3 AIA State Championships (AZ)'
        }
    },
    {
        'gender': 'boys',
        'grade': 'Senior',
        'event': '100 Breaststroke',
        'time': '59.61',
        'athlete': 'Zachary Duerkop',
        'date': 'Sep 20, 2025',
        'meet': 'CDO Classic',
        'also_overall': False,
        'old_record': {
            'time': '1:02.87',
            'athlete': 'Samuel Merrill',
            'date': 'Oct 21, 2023',
            'meet': 'Pecan Classic (Sahuarita Aquatic Center, AZ)'
        }
    },
    # Girls
    {
        'gender': 'girls',
        'grade': 'Freshman',
        'event': '100 Freestyle',
        'time': '58.02',
        'athlete': 'Isla Cerepak',
        'date': 'Nov 8, 2025',
        'meet': 'State Championship',
        'also_overall': False,
        'old_record': None  # First-ever freshman record
    },
    {
        'gender': 'girls',
        'grade': 'Senior',
        'event': '100 Backstroke',
        'time': '1:02.29',
        'athlete': 'Logan Sulger',
        'date': 'Nov 8, 2025',
        'meet': 'State Championship',
        'also_overall': True,
        'old_record': {
            'time': '1:07.56',
            'athlete': 'Carly Wilson',
            'date': 'Oct 28, 2011',
            'meet': 'AIA State Championships (AZ)'
        }
    },
    {
        'gender': 'girls',
        'grade': 'Senior',
        'event': '100 Breaststroke',
        'time': '1:13.71',
        'athlete': 'Adrianna Witte',
        'date': 'Sep 20, 2025',
        'meet': 'CDO Classic',
        'also_overall': False,
        'old_record': {
            'time': '1:15.19',
            'athlete': 'Chloe Weatherwax',
            'date': 'Oct 21, 2023',
            'meet': 'Pecan Classic (Sahuarita Aquatic Center, AZ)'
        }
    },
]

def get_old_record(gender, grade, event):
    """Get old record from records file"""
    records_file = Path(f"records/records-{gender}.md")
    
    with open(records_file, 'r') as f:
        content = f.read()
    
    # Find the event section - need to match exactly
    event_header = f"### {event}"
    event_start = content.find(event_header)
    if event_start == -1:
        print(f"Could not find event: {event}")
        return None
    
    # Find the next event header or end of file
    next_event = content.find("\n###", event_start + len(event_header))
    if next_event == -1:
        event_section = content[event_start:]
    else:
        event_section = content[event_start:next_event]
    
    # Find the table for this event
    # Look for the specific grade line
    lines = event_section.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('| ' + grade + ' |') or line.startswith('|' + grade + '|'):
            # Parse this line
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                return {
                    'time': parts[2],
                    'athlete': parts[3],
                    'date': parts[4],
                    'meet': parts[5]
                }
    
    print(f"Could not find grade {grade} in event {event}")
    return None

def generate_class_records_html():
    """Generate HTML for class records section organized by grade"""
    
    # Organize records by grade
    by_grade = defaultdict(list)
    for record in RECORDS_2025:
        by_grade[record['grade']].append(record)
    
    # Grade order
    grade_order = ['Freshman', 'Sophomore', 'Junior', 'Senior']
    
    html_parts = []
    
    for grade in grade_order:
        if grade not in by_grade:
            continue  # Skip grades with no records
        
        records = by_grade[grade]
        
        # Add grade section header
        html_parts.append(f'''
        <h3 class="mt-5 mb-3">{grade} Records</h3>
        <div class="row g-4">''')
        
        for record in records:
            # Get old record from data
            old_record = record.get('old_record')
            
            # Calculate time drop
            time_drop = 0
            time_drop_badge = ""
            is_first_record = (old_record is None)
            
            if old_record:
                new_time_sec = parse_time(record['time'])
                old_time_sec = parse_time(old_record['time'])
                time_drop = old_time_sec - new_time_sec
                
                pb_class = get_pb_badge_class(time_drop, record['event'])
                time_drop_badge = f'<span class="badge badge-pb {pb_class} ms-2">{format_time_drop(time_drop)}</span>'
            
            # Determine color
            if record['gender'] == 'boys':
                color = "#2C5F2D"
            else:
                color = "#808080"
            
            # Overall record indicator
            overall_star = " ⭐" if record['also_overall'] else ""
            
            # Build card
            card_html = f'''
            <div class="col-md-6">
                <div class="card" style="border-left: 4px solid {color}; background-color: #fafff5;">
                    <div class="card-body">
                        <h6 class="mb-2" style="color: {color};"><strong>{record['gender'].upper()} - {record['grade']} {record['event']}{overall_star}</strong></h6>
                        <p class="mb-1">
                            <span class="time">{record['time']}</span> - <strong>{record['athlete']}</strong>
                            {time_drop_badge}
                        </p>
                        <small class="text-muted">{record['date']} at {record['meet']}</small>'''
            
            # Add old record info if available and not the first record
            if old_record and not is_first_record:
                card_html += f'''
                        <hr class="my-2">
                        <small class="text-muted">
                            <strong>Previous:</strong> {old_record['time']} - {old_record['athlete']}<br>
                            <span style="font-size: 0.85em;">{old_record['date'][:3]} {old_record['date'].split()[-1]} at {old_record['meet'].split("(")[0].strip()}</span>
                        </small>'''
            elif is_first_record:
                card_html += f'''
                        <hr class="my-2">
                        <small class="text-muted">
                            <strong>First-Ever {record['grade']} Record!</strong>
                        </small>'''
            
            if record['also_overall']:
                card_html += '''
                        <div class="mt-2">
                            <span class="badge badge-sr">Overall School Record</span>
                        </div>'''
            
            card_html += '''
                    </div>
                </div>
            </div>'''
            
            html_parts.append(card_html)
        
        html_parts.append('''
        </div>''')
    
    return '\n'.join(html_parts)

def main():
    # Generate new HTML
    new_html = generate_class_records_html()
    
    # Read current index.html
    with open('docs/index.html', 'r') as f:
        content = f.read()
    
    # Find and replace the class records section content
    # Find start: after <div class="section-content" id="class-records-content">
    # Find end: before </div>\n    </div>\n    \n    <!-- Footer -->
    
    start_marker = '<div class="section-content" id="class-records-content">'
    end_marker = '</div>\n    </div>\n    \n    <!-- Footer -->'
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker, start_pos)
    
    if start_pos == -1 or end_pos == -1:
        print("Could not find class records section!")
        return
    
    # Build new content
    new_content = (
        content[:start_pos + len(start_marker)] +
        '\n' + new_html + '\n        ' +
        content[end_pos:]
    )
    
    # Write back
    with open('docs/index.html', 'w') as f:
        f.write(new_content)
    
    # Also update Jump To dropdown (only if not already present)
    if '#class-records-broken' not in new_content:
        jump_to_pattern = r'(<li><a class="dropdown-item jump-to-link" href="#records-broken">📈 2025 Records Broken</a></li>)'
        jump_to_replacement = r'\1\n                            <li><a class="dropdown-item jump-to-link" href="#class-records-broken">🎯 2025 Class Records</a></li>'
        
        new_content = re.sub(jump_to_pattern, jump_to_replacement, new_content)
    
    with open('docs/index.html', 'w') as f:
        f.write(new_content)
    
    print("✓ Updated Class Records section with old records and time drops")
    print("✓ Added Jump To link for Class Records")

if __name__ == "__main__":
    main()

