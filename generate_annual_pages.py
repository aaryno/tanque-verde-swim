#!/usr/bin/env python3
"""
Generate enhanced annual summary pages with index.html-style formatting.
Generates pages oldest to newest to properly track class records.
"""

import json
import re
from pathlib import Path
from datetime import datetime


# Seasons in order (oldest to newest)
SEASONS = [
    "2007-08", "2008-09", "2009-10", "2010-11", "2011-12",
    "2012-13", "2013-14", "2014-15", "2015-16", "2016-17",
    "2017-18", "2018-19", "2019-20", "2020-21", "2021-22",
    "2022-23", "2023-24", "2024-25", "2025-26"
]

# Years with incomplete data (only state meet results available)
INCOMPLETE_DATA_YEARS = ["2007-08", "2008-09", "2009-10", "2010-11", "2011-12"]


def grade_to_badge(grade_text):
    """Convert (FR), (SO), etc to badge HTML"""
    grade_map = {
        'FR': 'fr', 'SO': 'so', 'JR': 'jr', 'SR': 'sr',
        'Freshman': 'fr', 'Sophomore': 'so', 'Junior': 'jr', 'Senior': 'sr'
    }
    grade = grade_text.strip('()').upper()
    if grade in grade_map:
        return f'<span class="grade-badge grade-{grade_map[grade]}">{grade}</span>'
    return grade_text


def parse_annual_summary(md_file):
    """Parse the annual summary markdown file"""
    with open(md_file, 'r') as f:
        content = f.read()
    
    data = {
        'season': '',
        'total_swims': 0,
        'swimmers': 0,
        'meets': 0,
        'boys_swims': 0,
        'girls_swims': 0,
        'grade_swims': {},
        'meets_list': [],
        'records_broken': [],
        'best_times': [],
        'active_swimmers': {'boys': {}, 'girls': {}}
    }
    
    # Extract season from filename
    match = re.search(r'annual-summary-(\d{4}-\d{2})', md_file.name)
    if match:
        data['season'] = match.group(1)
    
    # Extract stats
    stats_match = re.search(r'\*\*Total Swims:\*\*\s*(\d+)', content)
    if stats_match:
        data['total_swims'] = int(stats_match.group(1))
    
    swimmers_match = re.search(r'\*\*Swimmers:\*\*\s*(\d+)', content)
    if swimmers_match:
        data['swimmers'] = int(swimmers_match.group(1))
    
    meets_match = re.search(r'\*\*Meets Attended:\*\*\s*(\d+)', content)
    if meets_match:
        data['meets'] = int(meets_match.group(1))
    
    # Gender swims
    boys_match = re.search(r'\*\*Boys:\*\*\s*(\d+)\s*swims', content)
    if boys_match:
        data['boys_swims'] = int(boys_match.group(1))
    
    girls_match = re.search(r'\*\*Girls:\*\*\s*(\d+)\s*swims', content)
    if girls_match:
        data['girls_swims'] = int(girls_match.group(1))
    
    # Grade swims
    for grade in ['Freshman', 'Sophomore', 'Junior', 'Senior']:
        grade_match = re.search(rf'\*\*{grade}:\*\*\s*(\d+)\s*swims', content)
        if grade_match:
            data['grade_swims'][grade] = int(grade_match.group(1))
    
    # Extract meets
    meets_section = re.search(r'## Meet Schedule.*?\n\|(.*?)\n---', content, re.DOTALL)
    if meets_section:
        for line in meets_section.group(1).split('\n'):
            if '|' in line and 'Date' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 2:
                    data['meets_list'].append({'date': parts[0], 'meet': parts[1]})
    
    # Extract records broken
    records_section = re.search(r'## 🏆 Records Broken\n\n(.*?)(?=\n---|\n## |$)', content, re.DOTALL)
    if records_section:
        records_text = records_section.group(1)
        current_record = {}
        for line in records_text.split('\n'):
            if line.startswith('**') and 'SCY' in line:
                if current_record:
                    data['records_broken'].append(current_record)
                event = line.strip('*').strip()
                current_record = {'event': event, 'new': '', 'previous': '', 'date': ''}
            elif line.startswith('- **NEW:**'):
                match = re.search(r'\*\*NEW:\*\*\s*([\d:.]+)\s*-\s*(.+)', line)
                if match:
                    current_record['new_time'] = match.group(1)
                    current_record['new_swimmer'] = match.group(2).strip()
            elif line.startswith('- *Previous:*'):
                match = re.search(r'\*Previous:\*\s*([\d:.]+|None)(?:\s*-\s*(.+))?', line)
                if match:
                    current_record['prev_time'] = match.group(1)
                    current_record['prev_swimmer'] = match.group(2).strip() if match.group(2) else ''
            elif line.startswith('- *Date:*'):
                match = re.search(r'\*Date:\*\s*(.+)', line)
                if match:
                    date_str = match.group(1).strip()
                    # Split date and meet location
                    if ' at ' in date_str:
                        parts = date_str.split(' at ', 1)
                        current_record['date'] = parts[0].strip()
                        current_record['meet'] = parts[1].strip()
                    else:
                        current_record['date'] = date_str
                        current_record['meet'] = ''
        if current_record:
            data['records_broken'].append(current_record)
    
    # Extract best times
    best_section = re.search(r'## Season Best Times\n\n\|(.*?)\n---', content, re.DOTALL)
    if best_section:
        for line in best_section.group(1).split('\n'):
            if '|' in line and 'Event' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 5:
                    data['best_times'].append({
                        'event': parts[0],
                        'boys_time': parts[1],
                        'boys_swimmer': parts[2],
                        'girls_time': parts[3],
                        'girls_swimmer': parts[4]
                    })
    
    return data


def load_class_records_for_season(class_records, season):
    """Get class records broken in a specific season"""
    return [r for r in class_records if r.get('season') == season]


def generate_nav_html():
    """Generate the navigation HTML"""
    return '''    <!-- Main Navigation -->
    <nav class="navbar navbar-dark" id="main-nav">
        <div class="container-fluid">
            <a class="navbar-brand" href="/index.html">
                <img src="/images/hawk-logo.png" alt="Tanque Verde Hawks" class="navbar-logo">
                <span class="navbar-brand-text d-md-none">TVHS</span>
                <span class="navbar-brand-text d-none d-md-inline">Tanque Verde Swimming Records</span>
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
        <div class="container-fluid justify-content-start">
            <ul class="nav">
                <li class="nav-item">
                    <a class="nav-link nav-home" href="/index.html" title="Home">
                        <img src="/images/hawk-logo.png" alt="Home" class="nav-logo">
                        <span class="d-none d-md-inline">Home</span>
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/records/overall.html" id="nav-overall" title="Overall Records">🏆<span class="d-none d-md-inline ms-1">Records</span></a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/top10/boys-alltime.html" id="nav-top10" title="All-Time Top 10">🔟<span class="d-none d-md-inline ms-1">Top 10</span></a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/records/boys-relays.html" id="nav-relays" title="Relay Records">🤝<span class="d-none d-md-inline ms-1">Relays</span></a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" id="nav-season-top10" title="Season Top 10">📅<span class="d-none d-md-inline ms-1">Top 10 by Year</span></a>
                    <ul class="dropdown-menu dropdown-menu-scroll">
''' + '\n'.join([f'                        <li><a class="dropdown-item season-link" data-path="top10" href="/top10/boys-{s}.html">{s}</a></li>' for s in reversed(SEASONS) if s >= "2007-08"]) + '''
                    </ul>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" id="nav-summary" title="Season Summary">📈<span class="d-none d-md-inline ms-1">Summary by Year</span></a>
                    <ul class="dropdown-menu dropdown-menu-scroll dropdown-menu-end">
''' + '\n'.join([f'                        <li><a class="dropdown-item" href="/annual/{s}.html">{s}</a></li>' for s in reversed(SEASONS) if s >= "2012-13"]) + '''
                    </ul>
                </li>
            </ul>
        </div>
    </nav>'''


def generate_season_overview_html(data, class_records_count):
    """Generate the Season Overview section"""
    records_count = len(data['records_broken'])
    
    html = f'''
    <!-- Season Overview -->
    <div class="container my-5" id="season-overview">
        <div class="section-header" data-section="overview">
            <h2 class="mb-0">📊 {data['season']} Season Overview</h2>
            <button class="section-toggle" data-target="overview-content">
                <span class="toggle-icon">▼</span>
            </button>
        </div>
        <div class="section-content" id="overview-content">
            <div class="row g-4 mt-3">
                <div class="col-6 col-md-3">
                    <div class="card text-center h-100">
                        <div class="card-body">
                            <h3 class="display-5 text-primary mb-1">{data['total_swims']}</h3>
                            <p class="mb-0 small">Total Swims</p>
                        </div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card text-center h-100">
                        <div class="card-body">
                            <h3 class="display-5 text-primary mb-1">{data['swimmers']}</h3>
                            <p class="mb-0 small">Swimmers</p>
                        </div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card text-center h-100">
                        <div class="card-body">
                            <h3 class="display-5 text-primary mb-1">{data['meets']}</h3>
                            <p class="mb-0 small">Meets</p>
                        </div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="card text-center h-100">
                        <div class="card-body">
                            <h3 class="display-5 text-success mb-1">{records_count}</h3>
                            <p class="mb-0 small">Records Broken</p>
                        </div>
                    </div>
                </div>
            </div>'''
    
    # Add incomplete data notice if applicable
    if data['season'] in INCOMPLETE_DATA_YEARS:
        html += '''
            <div class="alert alert-info mt-4">
                <small>⚠️ <strong>Note:</strong> Complete meet results are not available for this season. 
                Records shown are based on available data from state meets and select invitationals.</small>
            </div>'''
    
    # Add best times table
    if data['best_times']:
        html += '''
            
            <h4 class="mt-5 mb-3">Season Best Times</h4>
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Event</th>
                            <th>Boys</th>
                            <th>Girls</th>
                        </tr>
                    </thead>
                    <tbody>'''
        
        for bt in data['best_times']:
            boys_swimmer = re.sub(r'\((\w+)\)', lambda m: grade_to_badge(m.group(1)), bt['boys_swimmer'])
            girls_swimmer = re.sub(r'\((\w+)\)', lambda m: grade_to_badge(m.group(1)), bt['girls_swimmer'])
            
            html += f'''
                        <tr>
                            <td>{bt['event']}</td>
                            <td><span class="time">{bt['boys_time']}</span> - {boys_swimmer}</td>
                            <td><span class="time">{bt['girls_time']}</span> - {girls_swimmer}</td>
                        </tr>'''
        
        html += '''
                    </tbody>
                </table>
            </div>'''
    
    html += '''
        </div>
    </div>'''
    
    return html


def generate_records_broken_html(data):
    """Generate the Records Broken section with compact expandable format"""
    if not data['records_broken']:
        return ''
    
    html = f'''
    <!-- Records Broken -->
    <div class="container my-5" id="records-broken">
        <div class="section-header" data-section="records">
            <h2 class="mb-0">📈 {data['season']} Records Broken</h2>
            <button class="section-toggle" data-target="records-content">
                <span class="toggle-icon">▼</span>
            </button>
        </div>
        <div class="section-content" id="records-content">
            <h3 class="mt-4 mb-3">🏆 Overall School Records</h3>
            <div class="row g-4">'''
    
    for idx, record in enumerate(data['records_broken']):
        event = record.get('event', '').replace(' SCY', '')
        new_time = record.get('new_time', '')
        new_swimmer = record.get('new_swimmer', '')
        prev_time = record.get('prev_time', '')
        prev_swimmer = record.get('prev_swimmer', '')
        date = record.get('date', '')
        meet = record.get('meet', '')
        
        # Convert grade notations to badges
        new_swimmer_html = re.sub(r'\((\w+)\)', lambda m: grade_to_badge(m.group(1)), new_swimmer)
        prev_swimmer_html = re.sub(r'\((\w+)\)', lambda m: grade_to_badge(m.group(1)), prev_swimmer) if prev_swimmer else ''
        
        # Calculate improvement if possible
        improvement_html = ''
        if prev_time and prev_time != 'None' and new_time:
            try:
                def time_to_seconds(t):
                    if ':' in t:
                        parts = t.split(':')
                        return float(parts[0]) * 60 + float(parts[1])
                    return float(t)
                diff = time_to_seconds(prev_time) - time_to_seconds(new_time)
                if diff > 0:
                    improvement_html = f'''
                            <div class="record-improvement">
                                <span class="text-success"><strong>⬆ Improvement: {diff:.2f} seconds</strong></span>
                            </div>'''
            except:
                pass
        
        # Build previous record section
        prev_section = ''
        if prev_time and prev_time != 'None':
            prev_section = f'''
                            <div class="record-prev-section">
                                <div class="record-row">
                                    <span class="record-label-small">Previous:</span>
                                    <span class="time-value-small">{prev_time}</span>
                                </div>
                                <div class="record-row clickable-row" onclick="this.nextElementSibling.classList.toggle('show')">
                                    <span class="swimmer-name">{prev_swimmer_html}</span>
                                    <span class="date-value">—</span>
                                </div>
                                <div class="record-location-hidden">📍 —</div>
                            </div>'''
        else:
            prev_section = '''
                            <div class="record-prev-section">
                                <div class="record-row">
                                    <span class="text-muted small">First record in this event</span>
                                </div>
                            </div>'''
        
        html += f'''
                <div class="col-md-6">
                    <div class="card record-card-compact">
                        <div class="card-body">
                            <div class="record-row record-header-row">
                                <span class="event-name">{event}</span>
                                <span class="time-value">{new_time}</span>
                            </div>
                            <div class="record-row clickable-row" onclick="this.nextElementSibling.classList.toggle('show')">
                                <span class="swimmer-name"><strong>{new_swimmer_html}</strong></span>
                                <span class="date-value">{date}</span>
                            </div>
                            <div class="record-location-hidden">📍 {meet}</div>
                            {prev_section}
                            {improvement_html}
                        </div>
                    </div>
                </div>'''
    
    html += '''
            </div>
        </div>
    </div>'''
    
    return html


def generate_class_records_html(class_records, season):
    """Generate the Class Records Broken section with compact expandable format"""
    season_records = [r for r in class_records if r.get('season') == season]
    if not season_records:
        return ''
    
    # Group by grade
    by_grade = {}
    for r in season_records:
        grade = r.get('grade', 'Unknown')
        if grade not in by_grade:
            by_grade[grade] = []
        by_grade[grade].append(r)
    
    grade_order = ['FR', 'SO', 'JR', 'SR']
    grade_names = {'FR': 'Freshman', 'SO': 'Sophomore', 'JR': 'Junior', 'SR': 'Senior'}
    grade_badges = {'FR': 'grade-fr', 'SO': 'grade-so', 'JR': 'grade-jr', 'SR': 'grade-sr'}
    
    html = f'''
    <!-- Class Records Broken -->
    <div class="container my-5" id="class-records">
        <div class="section-header" data-section="class-records">
            <h2 class="mb-0">🎯 {season} Class Records Broken</h2>
            <button class="section-toggle" data-target="class-records-content">
                <span class="toggle-icon">▼</span>
            </button>
        </div>
        <div class="section-content" id="class-records-content">'''
    
    for grade in grade_order:
        if grade not in by_grade:
            continue
        
        records = by_grade[grade]
        html += f'''
            <h3 class="mt-4 mb-3">{grade_names.get(grade, grade)} Records</h3>
            <div class="row g-4">'''
        
        for record in records:
            gender = record.get('gender', 'boys')
            event = record.get('event', '')
            time = record.get('time', '')
            name = record.get('name', '')
            date = record.get('date', '')
            meet = record.get('meet', '')
            prev = record.get('previous')
            
            # Color based on gender
            border_color = '#2C5F2D' if gender == 'boys' else '#666'
            gender_label = 'BOYS' if gender == 'boys' else 'GIRLS'
            badge_class = grade_badges.get(grade, '')
            
            # Build previous record section
            prev_section = ''
            if prev:
                prev_name = prev.get('name', '')
                prev_time = prev.get('time', '')
                prev_season = prev.get('season', '')
                prev_section = f'''
                            <div class="record-prev-section">
                                <div class="record-row">
                                    <span class="record-label-small">Previous:</span>
                                    <span class="time-value-small">{prev_time}</span>
                                </div>
                                <div class="record-row">
                                    <span class="swimmer-name text-muted">{prev_name}</span>
                                    <span class="date-value text-muted small">{prev_season}</span>
                                </div>
                            </div>'''
            else:
                prev_section = '''
                            <div class="record-prev-section">
                                <div class="record-row">
                                    <span class="text-muted small">First record in this event/class</span>
                                </div>
                            </div>'''
            
            html += f'''
                <div class="col-md-6">
                    <div class="card record-card-compact" style="border-left: 4px solid {border_color};">
                        <div class="card-body">
                            <div class="record-row record-header-row">
                                <span class="event-name">{gender_label} {event} <span class="grade-badge {badge_class}">{grade}</span></span>
                                <span class="time-value">{time}</span>
                            </div>
                            <div class="record-row clickable-row" onclick="this.nextElementSibling.classList.toggle('show')">
                                <span class="swimmer-name"><strong>{name}</strong></span>
                                <span class="date-value">{date}</span>
                            </div>
                            <div class="record-location-hidden">📍 {meet}</div>
                            {prev_section}
                        </div>
                    </div>
                </div>'''
        
        html += '''
            </div>'''
    
    html += '''
        </div>
    </div>'''
    
    return html


def generate_page_html(data, class_records):
    """Generate the complete page HTML"""
    season = data['season']
    class_records_count = len([r for r in class_records if r.get('season') == season])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{season} Season Summary | Tanque Verde Swimming</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/css/style.css">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/images/favicon.png">
    <link rel="apple-touch-icon" href="/images/hawk-logo.png">
</head>
<body>
{generate_nav_html()}
    
    <!-- Page Header -->
    <div class="page-header">
        <div class="container d-flex align-items-center justify-content-between flex-wrap">
            <h1 class="mb-0">{season} Season Summary</h1>
            <div class="dropdown">
                <button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    Jump To
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item jump-to-link" href="#season-overview">📊 Season Overview</a></li>
                    <li><a class="dropdown-item jump-to-link" href="#records-broken">📈 Records Broken</a></li>
                    <li><a class="dropdown-item jump-to-link" href="#class-records">🎯 Class Records</a></li>
                </ul>
            </div>
        </div>
    </div>
{generate_season_overview_html(data, class_records_count)}
{generate_records_broken_html(data)}
{generate_class_records_html(class_records, season)}
    
    <!-- Footer -->
    <footer class="mt-5">
        <div class="container text-center">
            <div class="disclaimer mb-3">
                <small class="text-muted">
                    Results compiled from meets published on <a href="https://azpreps365.com" target="_blank">AZPreps365</a> 
                    and <a href="https://maxpreps.com" target="_blank">MaxPreps</a> with limited data availability — 
                    not necessarily a complete compilation of all records. 
                    Contact <a href="mailto:aaryno@gmail.com">aaryno@gmail.com</a> with additional sources, errors, or corrections.
                </small>
            </div>
            <p class="mb-2">&copy; 2025 Tanque Verde High School Swimming</p>
            <p class="mb-0">
                <small>
                    Generated on {datetime.now().strftime('%B %d, %Y')} | 
                    <a href="https://github.com/aaryno/tanque-verde-swim">View on GitHub</a>
                </small>
            </p>
        </div>
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        // Gender toggle and navigation
        let currentGender = localStorage.getItem('tvhs-gender') || 'boys';
        
        function updateGenderUI() {{
            document.querySelectorAll('.btn-gender').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.gender === currentGender);
            }});
            updateNavLinks();
        }}
        
        function updateNavLinks() {{
            const g = currentGender;
            document.getElementById('nav-bygrade').href = '/records/' + g + '-bygrade.html';
            document.getElementById('nav-top10').href = '/top10/' + g + '-alltime.html';
            document.getElementById('nav-relays').href = '/records/' + g + '-relays.html';
            
            document.querySelectorAll('.season-link').forEach(link => {{
                const season = link.textContent;
                link.href = '/top10/' + g + '-' + season + '.html';
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
        
        // Collapsible sections
        document.querySelectorAll('.section-header').forEach(header => {{
            header.addEventListener('click', function(e) {{
                e.preventDefault();
                const toggleBtn = this.querySelector('.section-toggle');
                if (!toggleBtn) return;
                
                const targetId = toggleBtn.dataset.target;
                const content = document.getElementById(targetId);
                
                if (content) {{
                    this.classList.toggle('collapsed');
                    content.classList.toggle('collapsed');
                }}
            }});
        }});
        
        // Smooth scroll for Jump To links
        document.querySelectorAll('.jump-to-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {{
                    const sectionHeader = targetElement.querySelector('.section-header');
                    const sectionContent = targetElement.querySelector('.section-content');
                    if (sectionHeader && sectionHeader.classList.contains('collapsed')) {{
                        sectionHeader.classList.remove('collapsed');
                        if (sectionContent) sectionContent.classList.remove('collapsed');
                    }}
                    
                    const yOffset = -120;
                    const y = targetElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
                    window.scrollTo({{top: y, behavior: 'smooth'}});
                }}
            }});
        }});
    }});
    </script>
</body>
</html>'''
    
    return html


def main():
    base_dir = Path(__file__).parent
    records_dir = base_dir / 'records'
    docs_dir = base_dir / 'docs'
    data_dir = base_dir / 'data'
    annual_dir = docs_dir / 'annual'
    
    # Load class records history
    class_records = []
    class_records_file = data_dir / 'class_records_history.json'
    if class_records_file.exists():
        with open(class_records_file, 'r') as f:
            class_records = json.load(f)
    
    print("🏊 Generating Enhanced Annual Summary Pages")
    print("=" * 50)
    
    # Generate pages oldest to newest
    generated = 0
    for season in SEASONS:
        # Skip 2025-26 - it's a manually maintained prototype with Seniors/State sections
        if season == "2025-26":
            print(f"  ⏭️  {season}: Skipping (manually maintained prototype)")
            continue
        
        md_file = records_dir / f'annual-summary-{season}.md'
        if not md_file.exists():
            print(f"  ⚠️  {season}: No markdown file found, skipping")
            continue
        
        print(f"  📄 {season}...", end=' ')
        
        # Parse the markdown
        data = parse_annual_summary(md_file)
        
        # Generate HTML
        html = generate_page_html(data, class_records)
        
        # Write output
        output_file = annual_dir / f'{season}.html'
        with open(output_file, 'w') as f:
            f.write(html)
        
        records_count = len(data['records_broken'])
        class_count = len([r for r in class_records if r.get('season') == season])
        print(f"✓ ({records_count} records, {class_count} class records)")
        generated += 1
    
    print("=" * 50)
    print(f"✅ Generated {generated} annual summary pages")


if __name__ == '__main__':
    main()
