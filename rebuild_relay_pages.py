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
        # Check event type
        entry_type = split_entry.get('type', '')
        if event_type == '200 Medley Relay' and entry_type != 'medley':
            continue
        if event_type == '200 Free Relay' and (entry_type != 'free' or len(split_entry.get('splits', [])) != 4):
            continue
        if event_type == '400 Free Relay' and (entry_type != 'free' or len(split_entry.get('splits', [])) != 8):
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

def generate_relay_card_html(relay, gender, splits_data, event_type):
    """Generate HTML for a single relay card"""
    rank = relay['rank']
    time = strip_leading_zero(relay['time'])  # Remove leading zero
    participants = relay['participants']
    date = relay['date']
    meet = relay['meet']
    
    # Get last names
    swimmers = [s.strip() for s in participants.split(',')]
    last_names = ', '.join(get_last_name(s) for s in swimmers)
    
    # Find splits
    splits_match = find_splits_for_relay(splits_data, gender, event_type, participants, time)
    
    # Build swimmer lines with splits (matching splash page style)
    swimmer_html = ''
    for i, swimmer in enumerate(swimmers):
        split_time = ''
        stroke = get_stroke_for_position(event_type, i)
        
        if splits_match:
            splits = splits_match.get('splits', [])
            if event_type == '400 Free Relay' and len(splits) == 8:
                # Sum two splits for 100 Free legs
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
        
        # Match splash page format: name | stroke (italic) | time (bold, right)
        swimmer_html += f'''
                                        <div class="swimmer-entry">
                                            <span class="swimmer-name">{swimmer}</span>
                                            <span class="swimmer-stroke">{stroke}</span>
                                            <span class="swimmer-time">{split_time}</span>
                                        </div>'''
    
    # Parse meet name and location
    meet_match = re.match(r'^(.+?)(\s*\([^)]+\))?$', meet)
    meet_name = meet_match.group(1).strip() if meet_match else meet
    meet_location = meet_match.group(2).strip() if meet_match and meet_match.group(2) else ''
    
    # Rank badge class
    rank_class = 'rank-1' if rank == 1 else ('rank-2' if rank == 2 else ('rank-3' if rank == 3 else ''))
    
    html = f'''
        <div class="relay-card" data-rank="{rank}">
            <div class="relay-compact-wrapper">
                <div class="relay-line-1">
                    <span class="relay-rank {rank_class}">{rank}</span>
                    <span class="relay-time">{time}</span>
                    <span class="relay-date">{date}</span>
                </div>
                <div class="relay-line-2" onclick="this.closest('.relay-compact-wrapper').classList.toggle('expanded')">
                    <span class="relay-names-short">{last_names} <span class="relay-arrow">▼</span></span>
                </div>
                <div class="relay-expanded-content">
                    <div class="relay-swimmers">{swimmer_html}
                    </div>
                    <div class="relay-meet">
                        <span class="meet-name">{meet_name}</span>
                        {f'<span class="meet-location">{meet_location}</span>' if meet_location else ''}
                    </div>
                </div>
            </div>
        </div>'''
    
    return html

def generate_relay_section_html(event_name, relays, gender, splits_data):
    """Generate HTML for an event section"""
    cards_html = ''
    for relay in relays[:10]:  # Only Top 10
        cards_html += generate_relay_card_html(relay, gender, splits_data, event_name)
    
    event_id = event_name.lower().replace(' ', '-')
    
    return f'''
    <h2 id="{event_id}" class="event-heading">{event_name}</h2>
    <div class="relay-cards-container">
        {cards_html}
    </div>
    '''

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
        /* Relay Card Styles - matching splash page */
        .relay-cards-container {{
            max-width: 800px;
            margin: 0 auto 2rem;
        }}
        
        .relay-card {{
            background-color: #E8F5E9; /* Pale green like splash page */
            border-left: 4px solid var(--tvhs-primary, #0a3622);
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .relay-compact-wrapper {{
            padding: 0.75rem 1rem;
        }}
        
        .relay-line-1 {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1rem;
        }}
        
        .relay-rank {{
            font-weight: bold;
            min-width: 1.5rem;
            text-align: center;
            color: #666;
        }}
        
        .relay-rank.rank-1 {{
            color: #d4af37;
            font-size: 1.2rem;
        }}
        
        .relay-rank.rank-2 {{
            color: #a8a8a8;
        }}
        
        .relay-rank.rank-3 {{
            color: #cd7f32;
        }}
        
        .relay-time {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: var(--tvhs-primary, #0a3622);
            flex-shrink: 0;
        }}
        
        .relay-date {{
            margin-left: auto;
            font-size: 0.85rem;
            color: #666;
            white-space: nowrap;
        }}
        
        .relay-line-2 {{
            cursor: pointer;
            padding: 0.5rem 0 0;
            user-select: none;
        }}
        
        .relay-names-short {{
            color: #333;
            font-size: 0.95rem;
        }}
        
        .relay-arrow {{
            font-size: 0.7rem;
            display: inline-block;
            transition: transform 0.2s ease;
            color: #999;
            margin-left: 0.25rem;
        }}
        
        .relay-compact-wrapper.expanded .relay-arrow {{
            transform: rotate(180deg);
        }}
        
        .relay-expanded-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        
        .relay-compact-wrapper.expanded .relay-expanded-content {{
            max-height: 400px;
        }}
        
        .relay-swimmers {{
            padding: 0.75rem 0 0.5rem 0;
            border-top: 1px solid rgba(0,0,0,0.1);
            margin-top: 0.5rem;
        }}
        
        /* Swimmer entry - matching splash page style */
        .relay-swimmers .swimmer-entry {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.25rem 0;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }}
        
        .relay-swimmers .swimmer-entry:last-child {{
            border-bottom: none;
        }}
        
        .relay-swimmers .swimmer-name {{
            flex: 1;
            font-weight: 500;
            color: #333;
        }}
        
        .relay-swimmers .swimmer-stroke {{
            font-size: 0.85rem;
            color: #666;
            font-style: italic;
        }}
        
        .relay-swimmers .swimmer-time {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 1rem;
            color: var(--tvhs-primary, #0a3622);
            min-width: 3.5rem;
            text-align: right;
        }}
        
        .relay-meet {{
            padding: 0.5rem 0;
            border-top: 1px solid rgba(0,0,0,0.1);
            font-size: 0.85rem;
            color: #555;
        }}
        
        .meet-name {{
            display: block;
        }}
        
        .meet-location {{
            display: block;
            color: #888;
            font-size: 0.8rem;
        }}
        
        /* Mobile: stack name/stroke on one line, time on right */
        @media (max-width: 575px) {{
            .relay-swimmers .swimmer-entry {{
                display: grid;
                grid-template-columns: 1fr auto;
                grid-template-areas: 
                    "name time"
                    "stroke stroke";
                gap: 0.25rem;
            }}
            
            .relay-swimmers .swimmer-name {{
                grid-area: name;
            }}
            
            .relay-swimmers .swimmer-stroke {{
                grid-area: stroke;
                font-size: 0.8rem;
            }}
            
            .relay-swimmers .swimmer-time {{
                grid-area: time;
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

