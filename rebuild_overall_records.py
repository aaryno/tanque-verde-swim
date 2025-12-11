#!/usr/bin/env python3
"""
Rebuild all 2025 Overall School Records to match the Boys 200 Medley Relay style:
- Expandable/collapsible format
- Shows rank, time, date on line 1
- Shows last names on line 2 (clickable)
- When expanded: full names with year badges, splits (for relays), meet location
- Shows OLD record in same format
- Pale green background
"""

from pathlib import Path

# Define all 2025 Overall School Records with complete data
OVERALL_RECORDS = [
    {
        'title': 'Boys 200 Medley Relay',
        'type': 'relay',
        'new': {
            'time': '1:41.80',
            'date': 'Oct 24, 2025',
            'place': '🥇',
            'swimmers': [
                {'name': 'Kent Olsson', 'grade': 'FR', 'stroke': 'Backstroke', 'split': '28.12'},
                {'name': 'Wade Olsson', 'grade': 'JR', 'stroke': 'Breaststroke', 'split': '27.30'},
                {'name': 'Jackson Eftekhar', 'grade': 'JR', 'stroke': 'Butterfly', 'split': '24.56'},
                {'name': 'Zachary Duerkop', 'grade': 'SR', 'stroke': 'Freestyle', 'split': '21.82'},
            ],
            'meet': 'Southern AZ Qualifier (Tucson, AZ)'
        },
        'old': {
            'time': '1:45.73',
            'date': 'Oct 25, 2024',
            'place': '🥈',
            'swimmers': [
                {'name': 'Jackson Machamer', 'grade': 'JR'},
                {'name': 'Wade Olsson', 'grade': 'SO'},
                {'name': 'Zachary Duerkop', 'grade': 'JR'},
                {'name': 'Jackson Eftekhar', 'grade': 'SO'},
            ],
            'meet': 'Southern AZ Qualifier (Oro Valley, AZ)'
        },
        'improvement': '3.93'
    },
    {
        'title': 'Boys 200 Free Relay',
        'type': 'relay',
        'new': {
            'time': '1:30.45',
            'date': 'Nov 8, 2025',
            'place': '🥇',
            'swimmers': [
                {'name': 'Wade Olsson', 'grade': 'JR', 'stroke': 'Freestyle', 'split': None},
                {'name': 'Jackson Eftekhar', 'grade': 'JR', 'stroke': 'Freestyle', 'split': None},
                {'name': 'Grayson The', 'grade': 'SR', 'stroke': 'Freestyle', 'split': None},
                {'name': 'Zachary Duerkop', 'grade': 'SR', 'stroke': 'Freestyle', 'split': None},
            ],
            'meet': 'AIA D3 State Championship (Paradise Valley, AZ)'
        },
        'old': {
            'time': '1:32.46',
            'date': 'Nov 7, 2019',
            'place': None,
            'swimmers': [
                {'name': 'Logan Radomsky', 'grade': None},
                {'name': 'Nicholas Spilotro', 'grade': None},
                {'name': 'Trevor Clausen', 'grade': None},
                {'name': 'Sam Stott', 'grade': None},
            ],
            'meet': 'AIA D-III State Meet (Paradise Valley, AZ)'
        },
        'improvement': '2.01'
    },
    {
        'title': 'Boys 400 Free Relay',
        'type': 'relay',
        'new': {
            'time': '3:20.60',
            'date': 'Oct 18, 2025',
            'place': None,
            'swimmers': [
                {'name': 'Wade Olsson', 'grade': 'JR', 'stroke': 'Freestyle', 'split': None},
                {'name': 'Jackson Eftekhar', 'grade': 'JR', 'stroke': 'Freestyle', 'split': None},
                {'name': 'Grayson The', 'grade': 'SR', 'stroke': 'Freestyle', 'split': None},
                {'name': 'Zachary Duerkop', 'grade': 'SR', 'stroke': 'Freestyle', 'split': None},
            ],
            'meet': 'Pecan Classic (Sahuarita, AZ)'
        },
        'old': {
            'time': '3:26.64',
            'date': 'Nov 5, 2021',
            'place': None,
            'swimmers': [
                {'name': 'Alejandro Alvarez', 'grade': None},
                {'name': 'Nolan Radomsky', 'grade': None},
                {'name': 'Nick Cusson', 'grade': None},
                {'name': 'Sam Stott', 'grade': None},
            ],
            'meet': 'AIA D-III Boys State (Paradise Valley, AZ)'
        },
        'improvement': '6.04'
    },
    {
        'title': 'Girls 200 Medley Relay',
        'type': 'relay',
        'new': {
            'time': '2:00.57',
            'date': 'Nov 8, 2025',
            'place': None,
            'swimmers': [
                {'name': 'Logan Sulger', 'grade': 'SR', 'stroke': 'Backstroke', 'split': None},
                {'name': 'Adrianna Witte', 'grade': 'SR', 'stroke': 'Breaststroke', 'split': None},
                {'name': 'Hadley Cusson', 'grade': 'JR', 'stroke': 'Butterfly', 'split': None},
                {'name': 'Isla Cerepak', 'grade': 'FR', 'stroke': 'Freestyle', 'split': None},
            ],
            'meet': 'AIA D3 State Championship (Paradise Valley, AZ)'
        },
        'old': {
            'time': '2:00.67',
            'date': 'Nov 1, 2019',
            'place': None,
            'swimmers': [
                {'name': 'Isabelle Sansom', 'grade': None},
                {'name': 'Maggie Colombo', 'grade': None},
                {'name': 'Paisley White', 'grade': None},
                {'name': 'Sarynn Patterson', 'grade': None},
            ],
            'meet': 'Canyon Del Oro Invite (Tucson, AZ)'
        },
        'improvement': '0.10'
    },
    {
        'title': 'Boys 100 Butterfly',
        'type': 'individual',
        'new': {
            'time': '52.48',
            'date': 'Nov 8, 2025',
            'place': None,
            'name': 'Zachary Duerkop',
            'grade': 'SR',
            'meet': 'AIA D3 State Championship (Paradise Valley, AZ)'
        },
        'old': {
            'time': '53.45',
            'date': 'Oct 21, 2023',
            'place': None,
            'name': 'Nick Cusson',
            'grade': 'SR',
            'meet': 'Pecan Classic (Sahuarita, AZ)'
        },
        'improvement': '0.97'
    },
    {
        'title': 'Boys 200 IM',
        'type': 'individual',
        'new': {
            'time': '1:57.78',
            'date': 'Nov 8, 2025',
            'place': None,
            'name': 'Wade Olsson',
            'grade': 'JR',
            'meet': 'AIA D3 State Championship (Paradise Valley, AZ)'
        },
        'old': {
            'time': '2:02.29',
            'date': 'Sep 16, 2023',
            'place': None,
            'name': 'Nick Cusson',
            'grade': 'SR',
            'meet': 'CDO Classic (Tucson, AZ)'
        },
        'improvement': '4.51'
    },
    {
        'title': 'Girls 100 Backstroke',
        'type': 'individual',
        'new': {
            'time': '1:02.29',
            'date': 'Nov 8, 2025',
            'place': None,
            'name': 'Logan Sulger',
            'grade': 'SR',
            'meet': 'AIA D3 State Championship (Paradise Valley, AZ)'
        },
        'old': {
            'time': '1:02.65',
            'date': 'Oct 27, 2017',
            'place': None,
            'name': 'Calla Isenberg',
            'grade': 'SR',
            'meet': 'Southern AZ Regional Qualifier (Oro Valley, AZ)'
        },
        'improvement': '0.36'
    },
]

def get_last_names(swimmers):
    """Get comma-separated last names"""
    return ', '.join([s['name'].split()[-1] for s in swimmers])

def generate_relay_html(record):
    """Generate HTML for a relay record"""
    new = record['new']
    old = record['old']
    
    html = f'''            <div class="col-md-6">
                <div class="card relay-record-broken">
                    <div class="card-body">
                        <h5 class="card-title">{record['title']}{" " + new['place'] if new.get('place') else ""}</h5>
                        
                        <!-- NEW Record -->
                        <div class="relay-record-entry mb-3">
                            <div class="record-label">NEW RECORD</div>
                            <div class="relay-compact-wrapper">
                                <div class="relay-line-1">
                                    {f'<span class="rank-badge">{new["place"]}</span>' if new.get('place') else ''}
                                    <span class="time-value">{new['time']}</span>
                                    <span class="date-value">{new['date']}</span>
                                </div>
                                <div class="relay-line-2" onclick="this.parentElement.classList.toggle('expanded')">
                                    <span class="relay-names-short">{get_last_names(new['swimmers'])} ▼</span>
                                </div>
                                <div class="relay-expanded-content">
                                    <div class="relay-swimmers">'''
    
    # Add swimmers with splits if available
    for swimmer in new['swimmers']:
        grade_badge = f' <span class="grade-badge grade-{swimmer["grade"].lower()}">{swimmer["grade"]}</span>' if swimmer.get('grade') else ''
        if swimmer.get('split'):
            html += f'''
                                        <div class="swimmer-entry">
                                            <span class="swimmer-name">{swimmer['name']}{grade_badge}</span>
                                            <span class="swimmer-stroke">{swimmer.get('stroke', '')}</span>
                                            <span class="swimmer-time">{swimmer['split']}</span>
                                        </div>'''
        else:
            html += f'''
                                        <div>{swimmer['name']}{grade_badge}</div>'''
    
    html += f'''
                                    </div>
                                    <div class="relay-meet">📍 {new['meet']}</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- OLD Record -->
                        <div class="relay-record-entry">
                            <div class="record-label-old">PREVIOUS RECORD</div>
                            <div class="relay-compact-wrapper">
                                <div class="relay-line-1">
                                    {f'<span class="rank-badge">{old["place"]}</span>' if old.get('place') else ''}
                                    <span class="time-value">{old['time']}</span>
                                    <span class="date-value">{old['date']}</span>
                                </div>
                                <div class="relay-line-2" onclick="this.parentElement.classList.toggle('expanded')">
                                    <span class="relay-names-short">{get_last_names(old['swimmers'])} ▼</span>
                                </div>
                                <div class="relay-expanded-content">
                                    <div class="relay-swimmers">'''
    
    for swimmer in old['swimmers']:
        grade_badge = f' <span class="grade-badge grade-{swimmer["grade"].lower()}">{swimmer["grade"]}</span>' if swimmer.get('grade') else ''
        html += f'''
                                        <div>{swimmer['name']}{grade_badge}</div>'''
    
    html += f'''
                                    </div>
                                    <div class="relay-meet">📍 {old['meet']}</div>
                                </div>
                            </div>
                        </div>
                        
                        <p class="mb-0 text-success mt-3"><strong>Improvement: {record['improvement']} seconds</strong></p>
                    </div>
                </div>
            </div>'''
    
    return html

def generate_individual_html(record):
    """Generate HTML for an individual record"""
    new = record['new']
    old = record['old']
    
    new_grade = f' <span class="grade-badge grade-{new["grade"].lower()}">{new["grade"]}</span>' if new.get('grade') else ''
    old_grade = f' <span class="grade-badge grade-{old["grade"].lower()}">{old["grade"]}</span>' if old.get('grade') else ''
    
    html = f'''            <div class="col-md-6">
                <div class="card relay-record-broken">
                    <div class="card-body">
                        <h5 class="card-title">{record['title']}</h5>
                        
                        <!-- NEW Record -->
                        <div class="relay-record-entry mb-3">
                            <div class="record-label">NEW RECORD</div>
                            <div class="relay-compact-wrapper">
                                <div class="relay-line-1">
                                    <span class="time-value">{new['time']}</span>
                                    <span class="date-value">{new['date']}</span>
                                </div>
                                <div class="relay-line-2" onclick="this.parentElement.classList.toggle('expanded')">
                                    <span class="relay-names-short">{new['name'].split()[-1]} ▼</span>
                                </div>
                                <div class="relay-expanded-content">
                                    <div class="relay-swimmers">
                                        <div>{new['name']}{new_grade}</div>
                                    </div>
                                    <div class="relay-meet">📍 {new['meet']}</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- OLD Record -->
                        <div class="relay-record-entry">
                            <div class="record-label-old">PREVIOUS RECORD</div>
                            <div class="relay-compact-wrapper">
                                <div class="relay-line-1">
                                    <span class="time-value">{old['time']}</span>
                                    <span class="date-value">{old['date']}</span>
                                </div>
                                <div class="relay-line-2" onclick="this.parentElement.classList.toggle('expanded')">
                                    <span class="relay-names-short">{old['name'].split()[-1]} ▼</span>
                                </div>
                                <div class="relay-expanded-content">
                                    <div class="relay-swimmers">
                                        <div>{old['name']}{old_grade}</div>
                                    </div>
                                    <div class="relay-meet">📍 {old['meet']}</div>
                                </div>
                            </div>
                        </div>
                        
                        <p class="mb-0 text-success mt-3"><strong>Improvement: {record['improvement']} seconds</strong></p>
                    </div>
                </div>
            </div>'''
    
    return html

def main():
    # Read index.html
    with open('docs/index.html', 'r') as f:
        content = f.read()
    
    # Find the Overall Records section
    start_marker = '<!-- Overall Records -->'
    end_marker = '</div>\n        </div>\n    </div>\n    \n    <!-- Class Records Broken -->'
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker, start_pos)
    
    if start_pos == -1 or end_pos == -1:
        print("Could not find Overall Records section!")
        return
    
    # Generate new HTML
    new_html_parts = [
        '<!-- Overall Records -->',
        '            <h3 class="mt-4 mb-3">🏆 Overall School Records</h3>',
        '        <div class="row g-4">'
    ]
    
    for record in OVERALL_RECORDS:
        if record['type'] == 'relay':
            new_html_parts.append(generate_relay_html(record))
        else:
            new_html_parts.append(generate_individual_html(record))
    
    new_html_parts.append('        </div>')
    
    new_html = '\n'.join(new_html_parts)
    
    # Replace
    new_content = content[:start_pos] + new_html + '\n' + content[end_pos:]
    
    # Write back
    with open('docs/index.html', 'w') as f:
        f.write(new_content)
    
    print("✓ Rebuilt all Overall School Records with consistent style")
    print("  - All records now use expandable/collapsible format")
    print("  - Shows NEW and PREVIOUS records with full details")
    print(f"  - Updated {len(OVERALL_RECORDS)} records ({sum(1 for r in OVERALL_RECORDS if r['type'] == 'relay')} relays, {sum(1 for r in OVERALL_RECORDS if r['type'] == 'individual')} individual)")

if __name__ == "__main__":
    main()

