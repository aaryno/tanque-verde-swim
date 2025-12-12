#!/usr/bin/env python3
"""
Generate enhanced annual pages with:
- Season bests with badges (trophy for overall, star for class records)
- Relay section with expandable splits
- Class records broken section
- Seniors section with cards
- State championship summary
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Load data
def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def load_class_records_at_season(target_season, history):
    """Get class records as they stood at the END of a given season"""
    records = {'boys': {}, 'girls': {}}
    
    for record in history:
        if record['season'] <= target_season:
            gender = record['gender']
            event = record['event']
            grade = record['grade']
            
            if event not in records[gender]:
                records[gender][event] = {}
            
            records[gender][event][grade] = {
                'time': record['time'],
                'name': record['name'],
                'date': record['date'],
                'meet': record['meet'],
                'season': record['season']
            }
    
    return records

def load_overall_records():
    """Load overall (Open) records from records-boys.md and records-girls.md"""
    records = {'boys': {}, 'girls': {}}
    
    for gender in ['boys', 'girls']:
        filepath = Path('records') / f'records-{gender}.md'
        if not filepath.exists():
            continue
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        current_event = None
        for line in content.split('\n'):
            event_match = re.match(r'^### (.+)$', line)
            if event_match:
                current_event = event_match.group(1).strip()
                continue
            
            if current_event and '**Open**' in line:
                parts = [p.strip().replace('**', '') for p in line.split('|') if p.strip()]
                if len(parts) >= 5:
                    records[gender][current_event] = {
                        'time': parts[1],
                        'name': parts[2],
                        'date': parts[3],
                        'meet': parts[4]
                    }
    
    return records

def parse_time_to_seconds(time_str):
    """Convert time string to seconds"""
    time_str = time_str.strip().replace('**', '').replace('(r)', '')
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            return float(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    except:
        return float('inf')

def parse_top10_file(filepath):
    """Parse Top 10 markdown file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    entries = []
    current_event = None
    
    for line in content.split('\n'):
        event_match = re.match(r'^###?\s+(.+)$', line)
        if event_match:
            current_event = event_match.group(1).strip()
            continue
        
        if current_event and line.startswith('|') and not line.startswith('| Rank') and not line.startswith('|--'):
            parts = [p.strip().replace('**', '') for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                try:
                    time = parts[1].replace('(r)', '').strip()
                    entries.append({
                        'event': current_event,
                        'time': time,
                        'time_seconds': parse_time_to_seconds(time),
                        'name': parts[2],
                        'year': parts[3].upper(),
                        'date': parts[4],
                        'meet': parts[5] if len(parts) > 5 else ''
                    })
                except:
                    pass
    
    return entries

def get_season_bests(entries):
    """Get the best time per event"""
    bests = {}
    for entry in entries:
        event = entry['event']
        if event not in bests or entry['time_seconds'] < bests[event]['time_seconds']:
            bests[event] = entry
    return bests

def parse_relay_file(filepath):
    """Parse relay records markdown file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    relays = []
    current_event = None
    
    for line in content.split('\n'):
        event_match = re.match(r'^## (.+ Relay)$', line)
        if event_match:
            current_event = event_match.group(1)
            continue
        
        if current_event and line.startswith('|') and not line.startswith('| Rank') and not line.startswith('|--'):
            parts = [p.strip().replace('**', '') for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                try:
                    rank = int(parts[0])
                    relays.append({
                        'event': current_event,
                        'rank': rank,
                        'time': parts[1],
                        'participants': parts[2],
                        'date': parts[3],
                        'meet': parts[4]
                    })
                except:
                    pass
    
    return relays

def get_season_relay_bests(season, all_relays):
    """Get the best relay for each event in a given season"""
    # Extract year from season (e.g., "2023-24" -> look for dates in late 2023 or early 2024)
    year_start = int(season.split('-')[0])
    
    bests = {}
    for relay in all_relays:
        date = relay['date']
        # Try to parse year from date
        match = re.search(r'(\d{4})', date)
        if match:
            relay_year = int(match.group(1))
            # Check if in season range
            if relay_year == year_start or relay_year == year_start + 1:
                event = relay['event']
                if event not in bests or relay['rank'] < bests[event]['rank']:
                    bests[event] = relay
    
    return bests

def get_seniors_in_season(entries):
    """Get list of seniors who swam in the season"""
    seniors = {}
    for entry in entries:
        if entry['year'] == 'SR':
            name = entry['name']
            if name not in seniors:
                seniors[name] = {'events': [], 'best_times': {}}
            if entry['event'] not in [e['event'] for e in seniors[name]['events']]:
                seniors[name]['events'].append(entry)
                seniors[name]['best_times'][entry['event']] = entry
    return seniors

def grade_badge(year):
    """Generate grade badge HTML"""
    year = year.upper()
    badge_class = {
        'FR': 'grade-fr',
        'SO': 'grade-so',
        'JR': 'grade-jr',
        'SR': 'grade-sr'
    }.get(year, 'grade-open')
    return f'<span class="grade-badge {badge_class}">{year}</span>'

def get_class_records_broken_in_season(season, history):
    """Get class records that were broken in a specific season"""
    return [r for r in history if r['season'] == season]

def generate_season_bests_html(boys_bests, girls_bests, overall_records, class_records, gender_label):
    """Generate HTML for season bests tables"""
    events_order = ['50 Freestyle', '100 Freestyle', '200 Freestyle', '500 Freestyle',
                    '100 Backstroke', '100 Breaststroke', '100 Butterfly', '200 Individual Medley']
    
    html = ''
    for gender, bests in [('boys', boys_bests), ('girls', girls_bests)]:
        if not bests:
            continue
        
        html += f'<h3 class="event-heading">{gender.title()} Season Bests</h3>\n'
        html += '<div class="records-table-container">\n'
        html += '<table class="table table-striped table-hover table-records">\n'
        html += '<thead><tr><th>Event</th><th>Time</th><th>Swimmer</th><th>Date</th><th>Meet</th></tr></thead>\n'
        html += '<tbody>\n'
        
        for event in events_order:
            if event not in bests:
                continue
            
            entry = bests[event]
            time = entry['time']
            name = entry['name']
            year = entry['year']
            date = entry['date']
            meet = entry['meet']
            
            # Check for overall record
            is_overall_record = False
            overall = overall_records.get(gender, {}).get(event)
            if overall and parse_time_to_seconds(time) <= parse_time_to_seconds(overall['time']):
                is_overall_record = True
            
            # Check for class record
            is_class_record = False
            class_rec = class_records.get(gender, {}).get(event, {}).get(year)
            if class_rec and parse_time_to_seconds(time) <= parse_time_to_seconds(class_rec['time']):
                is_class_record = True
            
            # Build badges
            badges = ''
            if is_overall_record:
                badges += ' 🏆'
            elif is_class_record:
                badges += ' ⭐'
            
            html += f'<tr>'
            html += f'<td class="event-cell">{event}</td>'
            html += f'<td class="time-cell"><strong>{time}</strong>{badges}</td>'
            html += f'<td class="name-cell">{name} {grade_badge(year)}</td>'
            html += f'<td class="date-cell">{date}</td>'
            html += f'<td class="meet-cell">{meet}</td>'
            html += f'</tr>\n'
        
        html += '</tbody></table>\n'
        html += '</div>\n'
    
    # Add legend
    html += '<p class="text-muted small mt-2">🏆 = Overall School Record · ⭐ = Class Record</p>\n'
    
    return html

def generate_relay_section_html(relays, splits_data, gender):
    """Generate relay cards HTML"""
    if not relays:
        return ''
    
    html = f'<h3 class="event-heading">{gender.title()} Relays</h3>\n'
    html += '<div class="relay-cards-container">\n'
    
    for event in ['200 Medley Relay', '200 Free Relay', '400 Free Relay']:
        if event not in relays:
            continue
        
        relay = relays[event]
        time = relay['time']
        if time.startswith('0'):
            time = time[1:]
        
        participants = relay['participants']
        swimmers = [s.strip() for s in participants.split(',')]
        last_names = ', '.join(s.split()[-1] for s in swimmers)
        date = relay['date']
        meet = relay['meet']
        
        # Parse meet name and location
        meet_match = re.match(r'^(.+?)(\s*\([^)]+\))?$', meet)
        meet_name = meet_match.group(1).strip() if meet_match else meet
        meet_location = meet_match.group(2).strip() if meet_match and meet_match.group(2) else ''
        
        # Build swimmer HTML (simplified - no splits for now)
        swimmer_html = ''
        strokes = ['Backstroke', 'Breaststroke', 'Butterfly', 'Freestyle'] if 'Medley' in event else ['Freestyle'] * 4
        for i, swimmer in enumerate(swimmers):
            stroke = strokes[i] if i < len(strokes) else 'Freestyle'
            swimmer_html += f'''
                <div class="swimmer-entry">
                    <span class="swimmer-name">{swimmer}</span>
                    <span class="swimmer-stroke">{stroke}</span>
                    <span class="swimmer-time"></span>
                </div>'''
        
        html += f'''
        <div class="relay-card">
            <div class="relay-compact-wrapper" onclick="this.classList.toggle('expanded')">
                <div class="relay-header">
                    <span class="relay-event">{event}</span>
                    <span class="relay-time">{time}</span>
                    <span class="relay-names-short">{last_names}</span>
                    <span class="relay-date">{date}</span>
                    <span class="relay-arrow">▼</span>
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
    
    html += '</div>\n'
    return html

def generate_class_records_broken_html(records_broken):
    """Generate class records broken section"""
    if not records_broken:
        return ''
    
    html = '<div class="section-header" data-section="class-records">\n'
    html += '<h2>⭐ Class Records Broken</h2>\n'
    html += '</div>\n'
    html += '<div class="class-records-container">\n'
    
    # Group by gender
    for gender in ['boys', 'girls']:
        gender_records = [r for r in records_broken if r['gender'] == gender]
        if not gender_records:
            continue
        
        html += f'<h3>{gender.title()}</h3>\n'
        html += '<div class="row g-3">\n'
        
        for record in gender_records:
            prev = record.get('previous')
            time_drop = ''
            if prev:
                drop = parse_time_to_seconds(prev['time']) - parse_time_to_seconds(record['time'])
                if drop > 0:
                    time_drop = f'<span class="badge badge-pb pb-mediumgray">-{drop:.2f}s</span>'
            
            html += f'''
            <div class="col-md-6">
                <div class="card class-record-card">
                    <div class="card-body">
                        <h6 class="card-title">{record['grade']} {record['event']}</h6>
                        <p class="mb-1"><strong>{record['time']}</strong> - {record['name']} {time_drop}</p>
                        <p class="text-muted small mb-0">{record['date']} at {record['meet']}</p>
                        {'<p class="text-muted small mb-0">Previous: ' + prev['time'] + ' by ' + prev['name'] + '</p>' if prev else '<p class="text-muted small mb-0 fst-italic">First-Ever ' + record['grade'] + ' Record!</p>'}
                    </div>
                </div>
            </div>'''
        
        html += '</div>\n'
    
    html += '</div>\n'
    return html

def generate_seniors_section_html(seniors):
    """Generate seniors section with cards"""
    if not seniors:
        return ''
    
    html = '<div class="section-header" data-section="seniors">\n'
    html += '<h2>🎓 Seniors</h2>\n'
    html += '</div>\n'
    html += '<div class="row g-4">\n'
    
    for name in sorted(seniors.keys()):
        data = seniors[name]
        events = data['events']
        
        html += f'''
        <div class="col-md-4">
            <div class="card h-100 senior-card">
                <div class="card-body">
                    <h5 class="card-title">{name}</h5>
                    <p class="mb-2"><strong>{len(events)} events</strong></p>
                    <div class="events-section">'''
        
        for entry in sorted(events, key=lambda x: x['event']):
            html += f'<p class="mb-1"><small>{entry["event"]}: <span class="time">{entry["time"]}</span></small></p>\n'
        
        html += '''
                    </div>
                </div>
            </div>
        </div>'''
    
    html += '</div>\n'
    return html

def generate_annual_page(season):
    """Generate a complete enhanced annual page for a season"""
    print(f"  Generating {season}...")
    
    # Load data
    class_history = load_json('data/class_records_history.json')
    overall_records = load_overall_records()
    splits_data = load_json('data/historical_splits/all_relay_splits.json')
    
    # Get class records as they stood before this season
    prev_season_parts = season.split('-')
    prev_year = int(prev_season_parts[0]) - 1
    prev_season = f"{prev_year}-{str(prev_year + 1)[-2:]}"
    class_records_before = load_class_records_at_season(prev_season, class_history)
    
    # Load season data
    boys_entries = []
    girls_entries = []
    
    boys_path = Path('records') / f'top10-boys-{season}.md'
    girls_path = Path('records') / f'top10-girls-{season}.md'
    
    if boys_path.exists():
        boys_entries = parse_top10_file(boys_path)
    if girls_path.exists():
        girls_entries = parse_top10_file(girls_path)
    
    # Get season bests
    boys_bests = get_season_bests(boys_entries)
    girls_bests = get_season_bests(girls_entries)
    
    # Get relays
    boys_relays = {}
    girls_relays = {}
    boys_relay_path = Path('records') / 'relay-records-boys.md'
    girls_relay_path = Path('records') / 'relay-records-girls.md'
    
    if boys_relay_path.exists():
        all_boys_relays = parse_relay_file(boys_relay_path)
        boys_relays = get_season_relay_bests(season, all_boys_relays)
    if girls_relay_path.exists():
        all_girls_relays = parse_relay_file(girls_relay_path)
        girls_relays = get_season_relay_bests(season, all_girls_relays)
    
    # Get class records broken in this season
    records_broken = get_class_records_broken_in_season(season, class_history)
    
    # Get seniors
    boys_seniors = get_seniors_in_season(boys_entries)
    girls_seniors = get_seniors_in_season(girls_entries)
    all_seniors = {**boys_seniors, **girls_seniors}
    
    # Build page content
    content_parts = []
    
    # Season Bests section
    content_parts.append('<div class="section-header" data-section="season-bests">')
    content_parts.append('<h2>📊 Season Bests</h2>')
    content_parts.append('</div>')
    content_parts.append(generate_season_bests_html(boys_bests, girls_bests, overall_records, class_records_before, season))
    
    # Relays section
    if boys_relays or girls_relays:
        content_parts.append('<div class="section-header" data-section="relays">')
        content_parts.append('<h2>🤝 Relay Records</h2>')
        content_parts.append('</div>')
        if boys_relays:
            content_parts.append(generate_relay_section_html(boys_relays, splits_data, 'boys'))
        if girls_relays:
            content_parts.append(generate_relay_section_html(girls_relays, splits_data, 'girls'))
    
    # Class Records Broken section
    if records_broken:
        content_parts.append(generate_class_records_broken_html(records_broken))
    
    # Seniors section
    if all_seniors:
        content_parts.append(generate_seniors_section_html(all_seniors))
    
    return '\n'.join(content_parts)

def create_html_page(title, content, season):
    """Create a complete HTML page with navigation"""
    
    # Read the template from an existing page for consistency
    nav_html = '''
    <!-- Main Navigation -->
    <nav class="navbar navbar-dark" id="main-nav">
        <div class="container-fluid">
            <a class="navbar-brand" href="/index.html">
                <img src="/images/hawk-logo.png" alt="Tanque Verde Hawks" class="navbar-logo">
                <span class="navbar-brand-text">TVHS</span>
            </a>
            <!-- Gender Toggle -->
            <div class="gender-toggle" id="gender-toggle">
                <button class="btn btn-gender active" data-gender="boys">Boys</button>
                <button class="btn btn-gender" data-gender="girls">Girls</button>
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
                    <a class="nav-link" href="/records/boys-bygrade.html" id="nav-bygrade" title="Records by Grade">📊</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/top10/boys-alltime.html" id="nav-top10" title="All-Time Top 10">🔟</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/records/boys-relays.html" id="nav-relays" title="Relay Records">🤝</a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" title="Season Top 10">📅</a>
                    <ul class="dropdown-menu dropdown-menu-scroll">
                        <li><a class="dropdown-item" href="/top10/boys-2024-25.html">2024-25</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2023-24.html">2023-24</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2022-23.html">2022-23</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2021-22.html">2021-22</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2020-21.html">2020-21</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2019-20.html">2019-20</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2018-19.html">2018-19</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2017-18.html">2017-18</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2016-17.html">2016-17</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2015-16.html">2015-16</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2014-15.html">2014-15</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2013-14.html">2013-14</a></li>
                        <li><a class="dropdown-item" href="/top10/boys-2012-13.html">2012-13</a></li>
                    </ul>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle active" href="#" data-bs-toggle="dropdown" title="Season Summary">📈</a>
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
    '''
    
    styles = '''
    <style>
        /* Enhanced Annual Page Styles */
        .section-header {
            background: var(--tvhs-primary, #0a3622);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px 8px 0 0;
            margin-top: 2rem;
            margin-bottom: 0;
        }
        
        .section-header h2 {
            margin: 0;
            font-size: 1.25rem;
        }
        
        .table-records {
            margin-bottom: 1.5rem;
        }
        
        .table-records th {
            background: var(--tvhs-primary, #0a3622);
            color: white;
            font-weight: 500;
        }
        
        .time-cell {
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }
        
        .event-cell {
            font-weight: 500;
        }
        
        .date-cell, .meet-cell {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* Relay cards for annual pages */
        .relay-cards-container {
            max-width: 900px;
            margin: 0 auto 2rem;
        }
        
        .relay-card {
            background-color: #E8F5E9;
            border-left: 4px solid var(--tvhs-primary, #0a3622);
            border-radius: 8px;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .relay-compact-wrapper {
            padding: 0.75rem 1rem;
            cursor: pointer;
            user-select: none;
        }
        
        .relay-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }
        
        .relay-event {
            font-weight: bold;
            color: var(--tvhs-primary, #0a3622);
            min-width: 140px;
        }
        
        .relay-time {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: var(--tvhs-primary, #0a3622);
        }
        
        .relay-names-short {
            flex: 1;
            color: #333;
        }
        
        .relay-date {
            font-size: 0.85rem;
            color: #666;
        }
        
        .relay-arrow {
            font-size: 0.7rem;
            transition: transform 0.2s ease;
            color: #999;
        }
        
        .relay-compact-wrapper.expanded .relay-arrow {
            transform: rotate(180deg);
        }
        
        .relay-expanded-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        .relay-compact-wrapper.expanded .relay-expanded-content {
            max-height: 400px;
        }
        
        .relay-swimmers {
            padding: 0.75rem 0 0.5rem;
            border-top: 1px solid rgba(0,0,0,0.1);
            margin-top: 0.5rem;
        }
        
        .swimmer-entry {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.25rem 0;
        }
        
        .swimmer-name {
            flex: 1;
            font-weight: 500;
        }
        
        .swimmer-stroke {
            font-size: 0.85rem;
            color: #666;
            font-style: italic;
        }
        
        .swimmer-time {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            min-width: 3.5rem;
            text-align: right;
        }
        
        .relay-meet {
            padding: 0.5rem 0;
            border-top: 1px solid rgba(0,0,0,0.1);
            font-size: 0.85rem;
            color: #555;
        }
        
        /* Class record cards */
        .class-record-card {
            background: #fff;
            border-left: 4px solid #ffc107;
        }
        
        /* Senior cards */
        .senior-card {
            border-left: 4px solid var(--tvhs-primary, #0a3622);
        }
        
        .senior-card .card-title {
            color: var(--tvhs-primary, #0a3622);
            font-weight: bold;
        }
        
        .time {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: var(--tvhs-primary, #0a3622);
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .table-records td:nth-child(4),
            .table-records th:nth-child(4),
            .table-records td:nth-child(5),
            .table-records th:nth-child(5) {
                display: none;
            }
            
            .relay-header {
                flex-wrap: wrap;
            }
            
            .relay-names-short {
                width: 100%;
                order: 10;
                padding-top: 0.25rem;
            }
        }
    </style>
    '''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title} | Tanque Verde Swimming</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/css/style.css">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/images/favicon.png">
    <link rel="apple-touch-icon" href="/images/hawk-logo.png">
    
    {styles}
</head>
<body>
    {nav_html}
    
    <!-- Page Header -->
    <div class="page-header">
        <div class="container d-flex align-items-center justify-content-between flex-wrap">
            <h1 class="mb-0">{title}</h1>
        </div>
    </div>
    
    <main class="container py-4">
        {content}
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
        let currentGender = localStorage.getItem('tvhs-gender') || 'boys';
        
        function updateGenderUI() {{
            document.querySelectorAll('.btn-gender').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.gender === currentGender);
            }});
        }}
        
        document.querySelectorAll('.btn-gender').forEach(btn => {{
            btn.addEventListener('click', function() {{
                currentGender = this.dataset.gender;
                localStorage.setItem('tvhs-gender', currentGender);
                updateGenderUI();
            }});
        }});
        
        updateGenderUI();
    }});
    </script>
</body>
</html>'''
    
    return html

def main():
    print("Generating enhanced annual pages...")
    print("=" * 60)
    
    seasons = sorted([
        f.stem.replace('annual-summary-', '') 
        for f in Path('records').glob('annual-summary-*.md')
    ])
    
    output_dir = Path('docs/annual')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for season in seasons:
        content = generate_annual_page(season)
        title = f"{season} Season Summary"
        
        html = create_html_page(title, content, season)
        
        output_path = output_dir / f"{season}.html"
        with open(output_path, 'w') as f:
            f.write(html)
        
        print(f"  ✓ {output_path}")
    
    print(f"\n{'=' * 60}")
    print(f"✅ Generated {len(seasons)} enhanced annual pages")

if __name__ == '__main__':
    main()

