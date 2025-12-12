#!/usr/bin/env python3
"""
Rebuild relay records pages with expandable card pattern.
- Top 10 only (not 15)
- First row: Rank | Time | Last names + Date (clickable)
- Expanded: 4 swimmer lines with splits, then meet line
"""

import json
import re
from pathlib import Path

def load_splits():
    """Load all relay splits from harvested data"""
    try:
        with open('data/historical_splits/all_relay_splits.json', 'r') as f:
            return json.load(f)
    except:
        return {'boys': [], 'girls': []}

def parse_relay_markdown(filepath):
    """Parse relay records from markdown file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    events = {}
    current_event = None
    
    for line in content.split('\n'):
        # Event header
        if line.startswith('## ') and 'Relay' in line:
            current_event = line[3:].strip()
            events[current_event] = []
        # Table row with data
        elif current_event and line.startswith('|') and not line.startswith('| Rank') and not line.startswith('|--'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                rank = parts[1].replace('**', '').strip()
                time = parts[2].replace('**', '').strip()
                participants = parts[3].replace('**', '').strip()
                date = parts[4].replace('**', '').strip()
                meet = parts[5].replace('**', '').strip()
                
                try:
                    rank_num = int(rank)
                    if rank_num <= 10:  # Only Top 10
                        events[current_event].append({
                            'rank': rank_num,
                            'time': time,
                            'participants': participants,
                            'date': date,
                            'meet': meet
                        })
                except ValueError:
                    pass
    
    return events

def get_last_name(full_name):
    """Extract last name from full name"""
    parts = full_name.strip().split()
    return parts[-1] if parts else full_name

def find_splits_for_relay(splits_data, gender, event_type, swimmers, total_time):
    """Find matching splits for a relay based on swimmers and time"""
    # Normalize swimmer names for matching
    relay_swimmers = [s.strip() for s in swimmers.split(',')]
    relay_set = set(s.lower().strip() for s in relay_swimmers)
    
    # Parse total time to seconds for comparison
    try:
        time_parts = total_time.replace(':', '.').split('.')
        if len(time_parts) == 3:
            total_secs = int(time_parts[0]) * 60 + float(f"{time_parts[1]}.{time_parts[2]}")
        else:
            total_secs = float(total_time)
    except:
        total_secs = 0
    
    best_match = None
    best_score = 0
    
    for split_entry in splits_data.get(gender, []):
        # Check event type - now using full event names
        entry_type = split_entry.get('type', '')
        num_splits = len(split_entry.get('splits', []))
        
        # Match based on event type (full names now)
        if event_type == '200 Medley Relay' and entry_type != '200 Medley Relay':
            continue
        if event_type == '200 Free Relay' and entry_type != '200 Free Relay':
            continue
        if event_type == '400 Free Relay' and entry_type != '400 Free Relay':
            continue
        
        # Match swimmers
        entry_swimmers = set()
        for s in split_entry.get('swimmers', []):
            # Remove grade suffix like " - Jr."
            name = re.sub(r'\s*-\s*(Fr|So|Jr|Sr)\.$', '', s, flags=re.IGNORECASE)
            entry_swimmers.add(name.lower().strip())
        
        # Check overlap
        matching = len(relay_set & entry_swimmers)
        if matching >= 3:  # At least 3 swimmers match
            if matching > best_score:
                best_score = matching
                best_match = split_entry
    
    return best_match

def format_split_time(split_str):
    """Format split time for display"""
    if not split_str:
        return ''
    # Remove leading zeros from minutes
    return re.sub(r'^00:', '', split_str)

def get_stroke_for_position(event_type, position):
    """Get stroke name for relay position"""
    if 'Medley' in event_type:
        strokes = ['Backstroke', 'Breaststroke', 'Butterfly', 'Freestyle']
        return strokes[position] if position < 4 else ''
    else:
        return 'Freestyle'

def strip_leading_zero(time_str):
    """Remove leading zero from time (01:42.54 -> 1:42.54)"""
    if time_str.startswith('0'):
        return time_str[1:]
    return time_str

def generate_relay_row_html(relay, gender, splits_data, event_type, row_num):
    """Generate HTML for a single relay table row"""
    rank = relay['rank']
    time = strip_leading_zero(relay['time'])
    participants = relay['participants']
    date = relay['date']
    meet = relay['meet']
    
    swimmers = [s.strip() for s in participants.split(',')]
    last_names = ', '.join(get_last_name(s) for s in swimmers)
    
    # Find splits
    splits_match = find_splits_for_relay(splits_data, gender, event_type, participants, time)
    
    # Build expanded content
    expanded_html = '<div class="relay-expanded-rows">'
    for i, swimmer in enumerate(swimmers):
        stroke = get_stroke_for_position(event_type, i)
        split_time = ''
        
        if splits_match:
            splits = splits_match.get('splits', [])
            if event_type == '400 Free Relay' and len(splits) == 8:
                idx = i * 2
                if idx + 1 < len(splits):
                    try:
                        t1 = float(splits[idx].replace('00:', ''))
                        t2 = float(splits[idx + 1].replace('00:', ''))
                        split_time = f"{t1 + t2:.2f}"
                    except:
                        pass
            elif i < len(splits):
                split_time = format_split_time(splits[i])
        
        expanded_html += f'<div class="relay-split-row">'
        expanded_html += f'<span class="split-swimmer">{swimmer}</span>'
        expanded_html += f'<span class="split-stroke">{stroke}</span>'
        expanded_html += f'<span class="split-time">{split_time}</span>'
        expanded_html += '</div>'
    
    expanded_html += f'<div class="relay-meet-row">{meet}</div>'
    expanded_html += '</div>'
    
    row_class = '' if row_num % 2 == 0 else 'table-row-alt'
    
    html = f'''<tr class="relay-row {row_class}" onclick="this.classList.toggle('expanded'); this.nextElementSibling.classList.toggle('show')">
            <td class="rank-cell">{rank}</td>
            <td class="time-cell"><strong>{time}</strong></td>
            <td class="relay-names-cell">{last_names} <span class="relay-arrow">▼</span></td>
            <td class="date-cell">{date}</td>
        </tr>
        <tr class="relay-details-row">
            <td colspan="4">{expanded_html}</td>
        </tr>'''
    
    return html

def generate_relay_section_html(event_name, relays, gender, splits_data):
    """Generate HTML table for an event section"""
    event_id = event_name.lower().replace(' ', '-')
    
    html = f'<h2 id="{event_id}" class="event-heading">{event_name}</h2>\n'
    html += '<div class="table-responsive">\n'
    html += '<table class="table table-hover table-relay">\n'
    html += '<thead><tr><th>Rank</th><th>Time</th><th>Relay</th><th>Date</th></tr></thead>\n'
    html += '<tbody>\n'
    
    for i, relay in enumerate(relays[:10]):  # Top 10
        html += generate_relay_row_html(relay, gender, splits_data, event_name, i)
    
    html += '</tbody></table>\n'
    html += '</div>\n'
    
    return html

def generate_full_page_html(gender, events, splits_data):
    """Generate the full HTML page"""
    gender_title = gender.title()
    other_gender = 'girls' if gender == 'boys' else 'boys'
    
    # Generate sections
    sections_html = ''
    for event_name in ['200 Medley Relay', '200 Free Relay', '400 Free Relay']:
        if event_name in events and events[event_name]:
            sections_html += generate_relay_section_html(event_name, events[event_name], gender, splits_data)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{gender_title} Relay Records | Tanque Verde Swimming</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/css/style.css">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/images/favicon.png">
    <link rel="apple-touch-icon" href="/images/hawk-logo.png">
    
    <style>
        /* Relay Table Styles - matching Top 10 pages */
        .table-relay {{
            margin-bottom: 2rem;
        }}
        
        .table-relay thead th {{
            background: var(--tvhs-primary, #0a3622);
            color: white;
            font-weight: 500;
        }}
        
        .relay-row {{
            cursor: pointer;
        }}
        
        .relay-row:hover {{
            background-color: #e8f5e9 !important;
        }}
        
        .table-row-alt {{
            background-color: #f8f9fa;
        }}
        
        .rank-cell {{
            width: 50px;
            font-weight: bold;
            text-align: center;
        }}
        
        .time-cell {{
            font-family: 'Courier New', monospace;
            white-space: nowrap;
        }}
        
        .relay-names-cell {{
            position: relative;
        }}
        
        .relay-arrow {{
            font-size: 0.7rem;
            display: inline-block;
            transition: transform 0.2s ease;
            color: #999;
            margin-left: 0.5rem;
        }}
        
        .relay-row.expanded .relay-arrow {{
            transform: rotate(180deg);
        }}
        
        .relay-details-row {{
            display: none !important;
        }}
        
        .relay-details-row.show {{
            display: table-row !important;
        }}
        
        .relay-details-row td {{
            background: #f8f9fa !important;
            padding: 0.75rem 1rem !important;
            border-radius: 0 !important;
            width: auto !important;
            height: auto !important;
        }}
        
        .relay-expanded-rows {{
            padding: 0.5rem 0;
        }}
        
        .relay-split-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.25rem 0;
            border-bottom: 1px solid #eee;
        }}
        
        .relay-split-row:last-of-type {{
            border-bottom: none;
        }}
        
        .split-swimmer {{
            font-weight: 500;
            flex: 1;
        }}
        
        .split-stroke {{
            font-style: italic;
            color: #666;
            margin: 0 1rem;
            display: inline !important;
        }}
        
        .split-time {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: var(--tvhs-primary, #0a3622);
            min-width: 3rem;
            text-align: right;
            display: inline !important;
        }}
        
        .relay-meet-row {{
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid #ddd;
            font-size: 0.85rem;
            color: #666;
        }}
        
        .date-cell {{
            white-space: nowrap;
            color: #666;
        }}
        
        /* Mobile styles - override main style.css table transformations */
        @media (max-width: 768px) {{
            /* Prevent table from being converted to block display */
            .table-relay,
            .table-relay thead,
            .table-relay tbody,
            .table-relay th,
            .table-relay td {{
                display: revert !important;
            }}
            
            /* Relay rows need explicit table-row display */
            .table-relay .relay-row {{
                display: table-row !important;
            }}
            
            /* Details rows stay hidden until toggled */
            .table-relay .relay-details-row {{
                display: none !important;
            }}
            
            .table-relay .relay-details-row.show {{
                display: table-row !important;
            }}
            
            .table-relay {{
                width: 100%;
                font-size: 0.85rem;
            }}
            
            .table-relay th,
            .table-relay td {{
                padding: 0.5rem 0.3rem;
            }}
            
            .rank-cell {{
                width: 35px;
            }}
            
            .time-cell {{
                width: 70px;
            }}
            
            .relay-names-cell {{
                font-size: 0.8rem;
            }}
            
            .date-cell {{
                font-size: 0.75rem;
                width: 80px;
            }}
            
            /* Expanded rows */
            .relay-details-row td {{
                padding: 0.5rem !important;
            }}
            
            .relay-split-row {{
                flex-wrap: wrap;
                padding: 0.4rem 0;
            }}
            
            .split-swimmer {{
                flex: 0 0 100%;
                margin-bottom: 0.2rem;
            }}
            
            .split-stroke {{
                margin: 0;
                font-size: 0.8rem;
            }}
            
            .split-time {{
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    
    <!-- Main Navigation -->
    <nav class="navbar navbar-dark" id="main-nav">
        <div class="container-fluid">
            <a class="navbar-brand" href="/index.html">
                <img src="/images/hawk-logo.png" alt="Tanque Verde Hawks" class="navbar-logo">
                <span class="navbar-brand-text">TVHS</span>
            </a>
            <!-- Gender Toggle -->
            <div class="gender-toggle" id="gender-toggle">
                <button class="btn btn-gender {'active' if gender == 'boys' else ''}" data-gender="boys">Boys</button>
                <button class="btn btn-gender {'active' if gender == 'girls' else ''}" data-gender="girls">Girls</button>
            </div>
        </div>
    </nav>
    
    <!-- Quick Nav Bar -->
    <nav class="navbar navbar-dark quick-nav" id="quick-nav">
        <div class="container-fluid justify-content-center">
            <ul class="nav">
                <li class="nav-item">
                    <a class="nav-link" href="/records/overall.html" title="Overall Records">🏆</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/records/{gender}-bygrade.html" title="Records by Grade">📊</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/top10/{gender}-alltime.html" title="All-Time Top 10">🔟</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link active" href="/records/{gender}-relays.html" title="Relay Records">🤝</a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" title="Season Top 10">📅</a>
                    <ul class="dropdown-menu dropdown-menu-scroll">
                        <li><a class="dropdown-item" href="/top10/{gender}-2024-25.html">2024-25</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2023-24.html">2023-24</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2022-23.html">2022-23</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2021-22.html">2021-22</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2020-21.html">2020-21</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2019-20.html">2019-20</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2018-19.html">2018-19</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2017-18.html">2017-18</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2016-17.html">2016-17</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2015-16.html">2015-16</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2014-15.html">2014-15</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2013-14.html">2013-14</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2012-13.html">2012-13</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2011-12.html">2011-12</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2010-11.html">2010-11</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2009-10.html">2009-10</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2008-09.html">2008-09</a></li>
                        <li><a class="dropdown-item" href="/top10/{gender}-2007-08.html">2007-08</a></li>
                    </ul>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" title="Season Summary">📈</a>
                    <ul class="dropdown-menu dropdown-menu-scroll dropdown-menu-end">
                        <li><a class="dropdown-item" href="/annual/2025-26.html">2025-26</a></li>
                        <li><a class="dropdown-item" href="/annual/2024-25.html">2024-25</a></li>
                        <li><a class="dropdown-item" href="/annual/2023-24.html">2023-24</a></li>
                        <li><a class="dropdown-item" href="/annual/2022-23.html">2022-23</a></li>
                        <li><a class="dropdown-item" href="/annual/2021-22.html">2021-22</a></li>
                        <li><a class="dropdown-item" href="/annual/2020-21.html">2020-21</a></li>
                        <li><a class="dropdown-item" href="/annual/2019-20.html">2019-20</a></li>
                        <li><a class="dropdown-item" href="/annual/2018-19.html">2018-19</a></li>
                        <li><a class="dropdown-item" href="/annual/2017-18.html">2017-18</a></li>
                        <li><a class="dropdown-item" href="/annual/2016-17.html">2016-17</a></li>
                        <li><a class="dropdown-item" href="/annual/2015-16.html">2015-16</a></li>
                        <li><a class="dropdown-item" href="/annual/2014-15.html">2014-15</a></li>
                        <li><a class="dropdown-item" href="/annual/2013-14.html">2013-14</a></li>
                        <li><a class="dropdown-item" href="/annual/2012-13.html">2012-13</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </nav>
    
    <!-- Page Header -->
    <div class="page-header">
        <div class="container d-flex align-items-center justify-content-between flex-wrap">
            <h1 class="mb-0">{gender_title} Relay Records</h1>
            <div id="jump-to-container">
                <div class="jump-to-dropdown dropdown">
                    <button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">Jump To</button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="#200-medley-relay">200 Medley Relay</a></li>
                        <li><a class="dropdown-item" href="#200-free-relay">200 Free Relay</a></li>
                        <li><a class="dropdown-item" href="#400-free-relay">400 Free Relay</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <main class="container py-4">
        {sections_html}
    </main>
    
    <!-- Footer -->
    <footer class="footer mt-auto py-3 bg-light">
        <div class="container text-center">
            <p class="text-muted small mb-1">
                Results compiled from meets published on AZPreps365 and MaxPreps with limited data availability — 
                not necessarily a complete compilation of all records. Contact aaryno@gmail.com with additional sources, errors, or corrections.
            </p>
            <p class="text-muted small mb-0">
                &copy; 2025 Tanque Verde High School Swimming
            </p>
        </div>
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        // Gender toggle
        let currentGender = '{gender}';
        
        document.querySelectorAll('.btn-gender').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const newGender = this.dataset.gender;
                if (newGender === currentGender) return;
                
                localStorage.setItem('tvhs-gender', newGender);
                window.location.href = '/records/' + newGender + '-relays.html';
            }});
        }});
    }});
    </script>
</body>
</html>'''
    
    return html

def main():
    print("Rebuilding relay pages with expandable cards...")
    
    splits_data = load_splits()
    print(f"  Loaded {len(splits_data.get('boys', []))} boys splits, {len(splits_data.get('girls', []))} girls splits")
    
    for gender in ['boys', 'girls']:
        md_path = f'records/relay-records-{gender}.md'
        html_path = f'docs/records/{gender}-relays.html'
        
        print(f"\nProcessing {gender}...")
        
        events = parse_relay_markdown(md_path)
        for event, relays in events.items():
            print(f"  {event}: {len(relays)} relays (showing top 10)")
        
        html = generate_full_page_html(gender, events, splits_data)
        
        with open(html_path, 'w') as f:
            f.write(html)
        
        print(f"  ✓ Generated {html_path}")
    
    print("\n✅ Relay pages rebuilt with expandable card pattern!")

if __name__ == '__main__':
    main()

