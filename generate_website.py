#!/usr/bin/env python3
"""
Generate GitHub Pages website from markdown records
Converts all markdown files to HTML with Bootstrap styling and navigation
"""

import re
from pathlib import Path
from datetime import datetime


def create_nav_html():
    """Create mobile-friendly navigation with Boys/Girls toggle and emoji shortcuts"""
    return '''
    <!-- Main Navigation -->
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
                    <a class="nav-link" href="#" id="nav-top10" title="All-Time Top 10">🔟<span class="d-none d-md-inline ms-1">Top 10</span></a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" id="nav-relays" title="Relay Records">🤝<span class="d-none d-md-inline ms-1">Relays</span></a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" id="nav-season-top10" title="Season Top 10">📅<span class="d-none d-md-inline ms-1">Top 10 by Year</span></a>
                    <ul class="dropdown-menu dropdown-menu-scroll">
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2024-25</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2023-24</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2022-23</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2021-22</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2020-21</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2019-20</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2018-19</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2017-18</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2016-17</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2015-16</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2014-15</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2013-14</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2012-13</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2011-12</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2010-11</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2009-10</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2008-09</a></li>
                        <li><a class="dropdown-item season-link" data-path="top10" href="#">2007-08</a></li>
                    </ul>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" id="nav-summary" title="Season Summary">📈<span class="d-none d-md-inline ms-1">Summary by Year</span></a>
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


def create_html_page(title, content, page_type="default"):
    """Create a complete HTML page with Bootstrap and navigation"""
    nav_html = create_nav_html()
    
    return f'''<!DOCTYPE html>
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
</head>
<body>
    {nav_html}
    
    <!-- Page Header -->
    <div class="page-header">
        <div class="container d-flex align-items-center justify-content-between flex-wrap">
            <h1 class="mb-0">{title}</h1>
            <div id="jump-to-container"></div>
        </div>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        // Build Jump To dropdown from event headings (h2 or h3.event-heading)
        let headings = document.querySelectorAll('h2, h3.event-heading');
        if (headings.length > 2) {{
            let options = '<div class="jump-to-dropdown dropdown"><button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">Jump To</button><ul class="dropdown-menu dropdown-menu-end dropdown-menu-scroll">';
            headings.forEach(function(h, i) {{
                const id = 'event-' + i;
                h.id = id;
                options += '<li><a class="dropdown-item" href="#' + id + '">' + h.textContent + '</a></li>';
            }});
            options += '</ul></div>';
            document.getElementById('jump-to-container').innerHTML = options;
        }}
        
        // Check if this is a relay records page
        const isRelayPage = document.title.toLowerCase().includes('relay');
        if (isRelayPage && window.innerWidth <= 576) {{
            // Transform relay tables for mobile
            document.querySelectorAll('table tbody tr').forEach(function(row) {{
                const cells = row.querySelectorAll('td');
                if (cells.length >= 5) {{
                    const participants = cells[2].textContent;
                    const date = cells[3].textContent;  // Date is column 4 (index 3)
                    const meet = cells[4].textContent;  // Meet is column 5 (index 4)
                    
                    // Extract last names
                    const names = participants.split(',').map(n => n.trim());
                    const lastNames = names.map(n => {{
                        const parts = n.split(' ');
                        return parts[parts.length - 1];
                    }}).join(', ');
                    
                    // Create expandable content
                    const shortNames = document.createElement('div');
                    shortNames.className = 'relay-names';
                    shortNames.textContent = lastNames;
                    
                    const details = document.createElement('div');
                    details.className = 'relay-details';
                    names.forEach(n => {{
                        const member = document.createElement('span');
                        member.className = 'member';
                        member.textContent = n;
                        details.appendChild(member);
                    }});
                    
                    // Split meet name from location (typically in parentheses)
                    const meetMatch = meet.match(/^(.+?)(\s*\([^)]+\))?$/);
                    const meetName = meetMatch ? meetMatch[1].trim() : meet;
                    const meetLocation = meetMatch && meetMatch[2] ? meetMatch[2].trim() : '';
                    
                    const meetDiv = document.createElement('div');
                    meetDiv.className = 'meet-full';
                    const meetNameSpan = document.createElement('span');
                    meetNameSpan.className = 'meet-name';
                    meetNameSpan.textContent = meetName;
                    meetDiv.appendChild(meetNameSpan);
                    if (meetLocation) {{
                        const meetLocSpan = document.createElement('span');
                        meetLocSpan.className = 'meet-location';
                        meetLocSpan.textContent = meetLocation;
                        meetDiv.appendChild(meetLocSpan);
                    }}
                    details.appendChild(meetDiv);
                    
                    // Replace participants cell content
                    cells[2].innerHTML = '';
                    cells[2].appendChild(shortNames);
                    cells[2].appendChild(details);
                    
                    // Put date in the date cell (hide meet cell)
                    cells[3].textContent = date;
                    cells[4].style.display = 'none';  // Hide meet column
                    
                    // Add click handler
                    shortNames.addEventListener('click', function() {{
                        this.classList.toggle('expanded');
                        details.classList.toggle('show');
                    }});
                }}
            }});
        }}
        
        // Gender toggle and navigation
        let currentGender = localStorage.getItem('tvhs-gender') || 'boys';
        
        // Detect current page gender from URL
        const currentPath = window.location.pathname;
        if (currentPath.includes('girls')) {{
            currentGender = 'girls';
        }} else if (currentPath.includes('boys')) {{
            currentGender = 'boys';
        }}
        localStorage.setItem('tvhs-gender', currentGender);
        
        function updateGenderUI() {{
            document.querySelectorAll('.btn-gender').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.gender === currentGender);
            }});
            updateNavLinks();
        }}
        
        function updateNavLinks() {{
            const g = currentGender;
            // Update nav links based on current gender
            document.getElementById('nav-top10').href = '/top10/' + g + '-alltime.html';
            document.getElementById('nav-relays').href = '/records/' + g + '-relays.html';
            
            // Update season links
            document.querySelectorAll('.season-link').forEach(link => {{
                const season = link.textContent;
                link.href = '/top10/' + g + '-' + season + '.html';
            }});
            
            // Reorder sections on Overall Records page based on gender
            const overallPage = document.querySelector('.overall-records-page');
            if (overallPage) {{
                const boysSection = document.getElementById('boys-records');
                const girlsSection = document.getElementById('girls-records');
                if (boysSection && girlsSection) {{
                    if (g === 'girls') {{
                        overallPage.insertBefore(girlsSection, boysSection);
                    }} else {{
                        overallPage.insertBefore(boysSection, girlsSection);
                    }}
                }}
            }}
        }}
        
        // Gender toggle click handlers - navigate to corresponding gender page
        document.querySelectorAll('.btn-gender').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const newGender = this.dataset.gender;
                if (newGender === currentGender) return;
                
                localStorage.setItem('tvhs-gender', newGender);
                
                // Try to navigate to the corresponding gender version of current page
                const path = window.location.pathname;
                let newPath = path;
                
                if (path.includes('boys')) {{
                    newPath = path.replace('boys', 'girls');
                }} else if (path.includes('girls')) {{
                    newPath = path.replace('girls', 'boys');
                }} else {{
                    // Not a gendered page, just update UI
                    currentGender = newGender;
                    updateGenderUI();
                    return;
                }}
                
                // Navigate to the new page
                window.location.href = newPath;
            }});
        }});
        
        // Initialize
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
    }});
    </script>
    
    <!-- Main Content -->
    <div class="container my-4">
        {content}
    </div>
    
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
            <p class="mb-2">&copy; {datetime.now().year} Tanque Verde High School Swimming</p>
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
</body>
</html>'''


def markdown_to_html_table(md_text):
    """Convert markdown tables to Bootstrap-styled HTML tables"""
    # Find all markdown tables
    table_pattern = r'\|(.+?)\|\n\|[-: |]+\|\n((?:\|.+?\|\n)+)'
    
    def replace_table(match):
        header_row = match.group(1)
        data_rows = match.group(2)
        
        # Parse header - split by | and remove leading/trailing empty parts
        header_parts = header_row.split('|')
        if header_parts and header_parts[0].strip() == '':
            header_parts = header_parts[1:]
        if header_parts and header_parts[-1].strip() == '':
            header_parts = header_parts[:-1]
        headers = [h.strip() for h in header_parts]
        
        # Parse data rows
        rows = []
        for row in data_rows.strip().split('\n'):
            if row.strip():
                # Split by | but keep empty cells (don't filter them out)
                parts = row.split('|')
                # Remove first and last empty parts (from leading/trailing |)
                if parts and parts[0].strip() == '':
                    parts = parts[1:]
                if parts and parts[-1].strip() == '':
                    parts = parts[:-1]
                cells = [c.strip() for c in parts]
                if cells:
                    rows.append(cells)
        
        # Determine table type based on column count and content
        num_cols = len(headers)
        # Check if this is a relay table (has "Participants" header)
        is_relay = any('participant' in h.lower() for h in headers)
        if is_relay:
            table_class = 'table-relay'
        elif num_cols == 5:
            table_class = 'table-5col'
        elif num_cols == 6:
            table_class = 'table-6col'
        else:
            table_class = ''
        
        # Build HTML table
        html = '<div class="table-responsive record-table">\n'
        html += f'<table class="table table-striped table-hover {table_class}">\n'
        html += '<thead>\n<tr>\n'
        for header in headers:
            html += f'<th>{header}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        # Grade abbreviation mapping (full names to abbreviations)
        grade_abbrev = {
            'Freshman': 'FR',
            'Sophomore': 'SO',
            'Junior': 'JR',
            'Senior': 'SR',
            'Open': 'OPEN'
        }
        
        # Also handle already-abbreviated grades
        abbrev_grades = {'FR', 'SO', 'JR', 'SR'}
        
        for row in rows:
            html += '<tr>\n'
            for i, cell in enumerate(row):
                # Strip bold markers for checking
                cell_clean = cell.replace('**', '').strip()
                is_bold = '**' in cell
                
                # Check if this is a grade column (first column often has grade names)
                if cell_clean in grade_abbrev:
                    abbrev = grade_abbrev[cell_clean]
                    css_class = abbrev.lower()
                    html += f'<td><span class="grade-badge grade-{css_class}">{abbrev}</span></td>\n'
                # Also check for already-abbreviated grades
                elif cell_clean.upper() in abbrev_grades:
                    abbrev = cell_clean.upper()
                    css_class = abbrev.lower()
                    html += f'<td><span class="grade-badge grade-{css_class}">{abbrev}</span></td>\n'
                # Check if this is a record holder (bold text)
                elif is_bold:
                    html += f'<td class="record-holder">{cell_clean}</td>\n'
                else:
                    html += f'<td>{cell}</td>\n'
            html += '</tr>\n'
        
        html += '</tbody>\n</table>\n</div>\n'
        return html
    
    # Replace all tables
    result = re.sub(table_pattern, replace_table, md_text, flags=re.MULTILINE)
    return result


def convert_class_year_to_badges(html_content):
    """Convert (FR), (SO), (JR), (SR) text to styled badge HTML"""
    badge_classes = {
        'FR': 'grade-fr',
        'SO': 'grade-so', 
        'JR': 'grade-jr',
        'SR': 'grade-sr'
    }
    
    def replace_grade(match):
        grade = match.group(1).upper()
        badge_class = badge_classes.get(grade, 'grade-open')
        return f'<span class="grade-badge {badge_class}">{grade}</span>'
    
    # Match (FR), (SO), (JR), (SR) - case insensitive
    result = re.sub(r'\((FR|SO|JR|SR)\)', replace_grade, html_content, flags=re.IGNORECASE)
    return result


def convert_top10_to_cards(md_file, output_file, title):
    """Convert a Top 10 markdown file to card-style HTML matching Overall Records format"""
    print(f"Converting {md_file.name} → {output_file.name} (card format)")
    
    with open(md_file, 'r') as f:
        content = f.read()
    
    # Grade badge mapping
    grade_classes = {
        'FR': 'grade-fr',
        'SO': 'grade-so',
        'JR': 'grade-jr',
        'SR': 'grade-sr'
    }
    
    # Parse events and records
    html_content = '<div class="content top10-cards">\n'
    
    # Find all event sections (### Event Name followed by table)
    event_pattern = r'### (.+?)\n\n\|.*?\|\n\|[-:\|\s]+\|\n((?:\|.*?\|\n)+)'
    
    for match in re.finditer(event_pattern, content, re.MULTILINE):
        event_name = match.group(1).strip()
        table_rows = match.group(2).strip()
        
        # Add event header with same styling as Overall Records
        html_content += f'<h3 class="event-heading top10-event-header">{event_name}</h3>\n'
        html_content += '<div class="top10-event-cards">\n'
        
        # Parse each row
        for row in table_rows.split('\n'):
            if not row.strip() or row.startswith('|--'):
                continue
            
            # Parse columns: | Rank | Time | Athlete | Year | Date | Meet |
            parts = [p.strip() for p in row.split('|')[1:-1]]
            if len(parts) < 6:
                continue
            
            rank_raw, time_raw, athlete_raw, year_raw, date_raw, meet_raw = parts[:6]
            
            # Clean bold markers and get values
            is_record = '**' in rank_raw
            rank = rank_raw.replace('**', '').strip()
            time = time_raw.replace('**', '').strip()
            athlete = athlete_raw.replace('**', '').strip()
            year = year_raw.replace('**', '').strip().upper()
            date = date_raw.replace('**', '').strip()
            meet = meet_raw.replace('**', '').strip()
            
            # Determine record holder class
            record_class = ' record-holder-row' if is_record else ''
            
            # Get grade badge class
            grade_class = grade_classes.get(year, 'grade-open')
            
            # Build card HTML
            html_content += f'''<div class="top10-card{record_class}" onclick="this.classList.toggle('expanded')">
    <div class="top10-line">
        <span class="top10-rank">{rank}</span>
        <span class="top10-time">{time}</span>
        <span class="top10-athlete">{athlete} <span class="grade-badge {grade_class}">{year}</span></span>
        <span class="top10-date">{date}</span>
        <span class="expand-arrow">▼</span>
    </div>
    <div class="top10-expanded">
        <div class="record-meet">📍 {meet}</div>
    </div>
</div>
'''
        
        html_content += '</div>\n'  # Close top10-event-cards
    
    html_content += '</div>\n'  # Close content
    
    # Create full HTML page
    full_html = create_html_page(title, html_content)
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(full_html)


def convert_markdown_file(md_file, output_file, title=None):
    """Convert a markdown file to HTML"""
    print(f"Converting {md_file.name} → {output_file.name}")
    
    # Read markdown
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    # Extract title from first heading if not provided
    if not title:
        title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        else:
            title = md_file.stem.replace('-', ' ').title()
    
    # Convert tables first
    html_content = markdown_to_html_table(md_content)
    
    # Remove duplicate subtitle (already shown in sticky header)
    html_content = re.sub(r'^## Tanque Verde High School Swimming\s*$', '', html_content, flags=re.MULTILINE)
    
    # Remove h1 title from content (it's already in the page header)
    html_content = re.sub(r'^# .+$', '', html_content, flags=re.MULTILINE)
    
    # Remove redundant "Team Records - Short Course Yards" subtitle
    html_content = re.sub(r'^## Team Records - Short Course Yards.*$', '', html_content, flags=re.MULTILINE)
    
    # Remove "Generated:" lines
    html_content = re.sub(r'^\*?\*?Generated:\*?\*?.*$', '', html_content, flags=re.MULTILINE)
    
    # Convert remaining markdown elements
    # Headings
    html_content = re.sub(r'^### (.+)$', r'<h3 class="event-heading">\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    
    # Bold text
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Italic text
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
    
    # Horizontal rules
    html_content = re.sub(r'^---$', '<hr>', html_content, flags=re.MULTILINE)
    
    # Convert unordered lists
    def convert_list_block(match):
        list_block = match.group(0)
        items = re.findall(r'^- (.+)$', list_block, re.MULTILINE)
        if items:
            html_items = '\n'.join([f'<li>{item}</li>' for item in items])
            return f'<ul>\n{html_items}\n</ul>'
        return list_block
    
    # Find consecutive lines starting with "- " and convert to <ul>
    html_content = re.sub(r'(^- .+$\n?)+', convert_list_block, html_content, flags=re.MULTILINE)
    
    # Paragraphs (lines separated by blank lines)
    paragraphs = html_content.split('\n\n')
    formatted_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<'):
            para = f'<p>{para}</p>'
        formatted_paragraphs.append(para)
    html_content = '\n'.join(formatted_paragraphs)
    
    # Convert class year text (FR), (SO), (JR), (SR) to styled badges
    html_content = convert_class_year_to_badges(html_content)
    
    # Wrap in sections for better styling
    html_content = f'<div class="content">\n{html_content}\n</div>'
    
    # Create full HTML page
    full_html = create_html_page(title, html_content)
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(full_html)


def extract_open_records(md_file):
    """Extract only OPEN records from a records markdown file, with class year"""
    with open(md_file, 'r') as f:
        content = f.read()
    
    # Grade abbreviation mapping
    grade_abbrev = {
        'Freshman': 'FR',
        'Sophomore': 'SO',
        'Junior': 'JR',
        'Senior': 'SR'
    }
    
    records = []
    current_event = None
    current_event_records = []  # Store grade records for current event
    
    for line in content.split('\n'):
        # Match event headings
        event_match = re.match(r'^### (.+)$', line)
        if event_match:
            current_event = event_match.group(1)
            current_event_records = []
            continue
        
        # Parse grade record rows (non-bold, before OPEN)
        if current_event and line.startswith('|') and '**' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 5 and parts[0] in grade_abbrev:
                current_event_records.append({
                    'grade': parts[0],
                    'time': parts[1],
                    'name': parts[2],
                    'date': parts[3],
                    'meet': parts[4]
                })
        
        # Match OPEN record rows (bold)
        if current_event and '**Open**' in line:
            # Parse the table row: | **Open** | **Time** | **Name** | **Date** | **Meet** |
            parts = [p.strip().replace('**', '') for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                open_time = parts[1]
                open_name = parts[2]
                
                # Find which grade record matches the OPEN record
                class_year = ''
                for grade_rec in current_event_records:
                    # Match by time and name
                    if grade_rec['time'] == open_time and grade_rec['name'] == open_name:
                        class_year = grade_abbrev.get(grade_rec['grade'], '')
                        break
                
                records.append({
                    'event': current_event,
                    'time': parts[1],
                    'name': parts[2],
                    'class_year': class_year,
                    'date': parts[3],
                    'meet': parts[4]
                })
    
    return records


def extract_top_relay_records(md_file):
    """Extract the #1 relay for each event from a relay records markdown file"""
    with open(md_file, 'r') as f:
        content = f.read()
    
    records = []
    current_event = None
    
    for line in content.split('\n'):
        # Match event headings (## 200 Medley Relay, etc.)
        event_match = re.match(r'^## (.+ Relay)$', line)
        if event_match:
            current_event = event_match.group(1)
            continue
        
        # Match #1 record rows (bold with rank 1)
        if current_event and line.startswith('| **1**'):
            # Parse: | **1** | **Time** | **Participants** | **Date** | **Meet** |
            parts = [p.strip().replace('**', '') for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                # Strip leading zero from time
                time = parts[1]
                if time.startswith('0'):
                    time = time[1:]
                records.append({
                    'event': current_event,
                    'time': time,
                    'participants': parts[2],
                    'date': parts[3],
                    'meet': parts[4]
                })
                current_event = None  # Only get #1 for each event
    
    return records


def generate_overall_records_page(records_dir, docs_dir):
    """Generate the Overall Records page with both boys and girls OPEN records"""
    print("🏆 Generating Overall Records page...")
    
    # Extract OPEN records from both boys and girls
    boys_records = extract_open_records(records_dir / 'records-boys.md')
    girls_records = extract_open_records(records_dir / 'records-girls.md')
    
    # Extract top relay records
    boys_relays = extract_top_relay_records(records_dir / 'relay-records-boys.md')
    girls_relays = extract_top_relay_records(records_dir / 'relay-records-girls.md')
    
    # Load relay splits
    splits_data = {}
    splits_file = Path('data/historical_splits/all_relay_splits.json')
    if splits_file.exists():
        import json
        with open(splits_file, 'r') as f:
            splits_data = json.load(f)
    
    def get_last_names(participants):
        """Extract last names from participants string"""
        names = [n.strip() for n in participants.split(',')]
        return ', '.join(n.split()[-1] for n in names)
    
    def find_relay_splits(relay, gender, event):
        """Find splits for a relay from the splits data"""
        swimmers = [s.strip() for s in relay['participants'].split(',')]
        relay_set = set(s.lower() for s in swimmers)
        
        for split_entry in splits_data.get(gender, []):
            entry_type = split_entry.get('type', '')
            if entry_type != event:
                continue
            
            entry_swimmers = []
            for s in split_entry.get('swimmers', []):
                import re
                name = re.sub(r'\s*-\s*(Fr|So|Jr|Sr)\.$', '', s, flags=re.IGNORECASE)
                entry_swimmers.append(name.strip())
            
            entry_set = set(s.lower() for s in entry_swimmers)
            if len(relay_set & entry_set) >= 3:
                return split_entry.get('splits', [])
        return []
    
    def get_stroke_for_position(event, pos):
        if 'Medley' in event:
            strokes = ['Backstroke', 'Breaststroke', 'Butterfly', 'Freestyle']
            return strokes[pos] if pos < 4 else 'Freestyle'
        return 'Freestyle'
    
    # Build HTML content for overall records with special layout
    def build_records_html(records, relays, gender):
        section_id = f"{gender}-content"
        html = f'''<div class="overall-records-section" id="{gender}-records">
<div class="section-header" data-section="{gender}">
    <h2 class="mb-0">{gender.title()} Team Records</h2>
    <button class="section-toggle" data-target="{section_id}">
        <span class="toggle-icon">▼</span>
    </button>
</div>
<div class="section-content" id="{section_id}">
'''
        
        # Individual records - single line with expandable location
        for record in records:
            # Build class year badge if available
            class_year = record.get('class_year', '')
            if class_year:
                grade_class = f"grade-{class_year.lower()}"
                class_badge = f' <span class="grade-badge {grade_class}">{class_year}</span>'
            else:
                class_badge = ''
            
            html += f'''<div class="overall-record-card" onclick="this.classList.toggle('expanded')">
    <div class="record-line">
        <span class="event-name">{record['event']}</span>
        <span class="record-time">{record['time']}</span>
        <span class="record-athlete">{record['name']}{class_badge}</span>
        <span class="record-date">{record['date']}</span>
        <span class="expand-arrow">▼</span>
    </div>
    <div class="record-expanded">
        <div class="record-meet">📍 {record['meet']}</div>
    </div>
</div>\n'''
        
        # Relay records section with expandable splits
        if relays:
            html += f'<h3 class="relay-header">{gender.title()} Relay Records</h3>\n'
            for relay in relays:
                last_names = get_last_names(relay['participants'])
                swimmers = [s.strip() for s in relay['participants'].split(',')]
                splits = find_relay_splits(relay, gender, relay['event'])
                
                # Build splits HTML
                splits_html = ''
                for i, swimmer in enumerate(swimmers):
                    stroke = get_stroke_for_position(relay['event'], i)
                    split_time = ''
                    if splits:
                        if relay['event'] == '400 Free Relay' and len(splits) == 8:
                            idx = i * 2
                            if idx + 1 < len(splits):
                                try:
                                    t1 = float(splits[idx].replace('00:', ''))
                                    t2 = float(splits[idx + 1].replace('00:', ''))
                                    split_time = f"{t1 + t2:.2f}"
                                except:
                                    pass
                        elif i < len(splits):
                            split_time = splits[i].replace('00:', '')
                    
                    splits_html += f'''<div class="relay-split-row">
    <span class="split-stroke">{stroke}</span>
    <span class="split-swimmer">{swimmer}</span>
    <span class="split-time">{split_time}</span>
</div>'''
                
                html += f'''<div class="overall-record-card relay-record-card" onclick="this.classList.toggle('expanded')">
    <div class="record-line">
        <span class="event-name">{relay['event']}</span>
        <span class="record-time">{relay['time']}</span>
        <span class="record-athlete relay-names">{last_names}</span>
        <span class="record-date">{relay['date']}</span>
        <span class="expand-arrow">▼</span>
    </div>
    <div class="record-expanded">
        <div class="relay-splits">{splits_html}</div>
        <div class="record-meet">📍 {relay['meet']}</div>
    </div>
</div>\n'''
        
        html += '</div>\n'  # Close section-content
        html += '</div>\n'  # Close overall-records-section
        return html
    
    boys_html = build_records_html(boys_records, boys_relays, 'boys')
    girls_html = build_records_html(girls_records, girls_relays, 'girls')
    
    # Combine with boys first (JavaScript will reorder based on gender toggle)
    content = f'''<div class="content overall-records-page">
{boys_html}
{girls_html}
</div>'''
    
    # Create full HTML page
    full_html = create_html_page("Overall Team Records", content)
    
    # Write output
    output_file = docs_dir / 'records' / 'overall.html'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(full_html)
    
    print(f"  Created: {output_file}")


def filter_out_open_records(md_content):
    """Remove OPEN records from markdown content for By Grade page"""
    lines = md_content.split('\n')
    filtered_lines = []
    for line in lines:
        # Skip lines that contain **Open**
        if '**Open**' not in line and '| Open |' not in line:
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)


def main():
    print("=" * 80)
    print("GENERATING TANQUE VERDE SWIM WEBSITE")
    print("=" * 80)
    print()
    
    records_dir = Path('records')
    docs_dir = Path('docs')
    
    # Generate Overall Records page (OPEN records only)
    generate_overall_records_page(records_dir, docs_dir)
    
    # Convert team records (By Grade - excludes OPEN)
    print("\n📊 Converting By Grade Records...")
    for record_file in records_dir.glob('records-*.md'):
        if 'boys' in record_file.name:
            output = docs_dir / 'records' / 'boys-bygrade.html'
            title = "Boys Records by Grade"
        elif 'girls' in record_file.name:
            output = docs_dir / 'records' / 'girls-bygrade.html'
            title = "Girls Records by Grade"
        else:
            continue
        
        # Read and filter out OPEN records
        with open(record_file, 'r') as f:
            md_content = f.read()
        filtered_content = filter_out_open_records(md_content)
        
        # Write to temp file and convert
        temp_file = record_file.with_suffix('.filtered.md')
        with open(temp_file, 'w') as f:
            f.write(filtered_content)
        
        convert_markdown_file(temp_file, output, title)
        temp_file.unlink()  # Clean up temp file
    
    # Relay pages are generated by rebuild_relay_pages.py (not from markdown)
    # This provides expandable cards with splits data
    print("\n🏃 Generating Relay Records (via rebuild_relay_pages.py)...")
    import subprocess
    result = subprocess.run(['python3', 'rebuild_relay_pages.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️ Warning: rebuild_relay_pages.py failed: {result.stderr}")
    else:
        print("  ✓ Relay pages generated with expandable cards")
    
    # Convert top 10 lists (card format matching Overall Records)
    print("\n🔟 Converting Top 10 Lists (Card Format)...")
    for top10_file in records_dir.glob('top10-*.md'):
        gender = 'boys' if 'boys' in top10_file.name else 'girls'
        season = top10_file.stem.replace(f'top10-{gender}-', '')
        
        if season == 'alltime':
            title = f"{gender.title()} All-Time Top 10"
            output_name = f"{gender}-alltime.html"
        else:
            title = f"{gender.title()} Top 10 - {season}"
            output_name = f"{gender}-{season}.html"
        
        output = docs_dir / 'top10' / output_name
        convert_top10_to_cards(top10_file, output, title)
    
    # Generate annual summaries using dedicated script (maintains styled format)
    print("\n📅 Generating Annual Summaries (via generate_annual_pages.py)...")
    import subprocess
    result = subprocess.run(['python3', 'generate_annual_pages.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️ Warning: generate_annual_pages.py failed: {result.stderr}")
    else:
        print("  ✓ Annual pages generated with styled format")
    
    print("\n" + "=" * 80)
    print("✅ Website generation complete!")
    print(f"📁 Output directory: {docs_dir.absolute()}")
    print("=" * 80)


if __name__ == '__main__':
    main()

