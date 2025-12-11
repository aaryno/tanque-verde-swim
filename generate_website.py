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
                <img src="/images/hawk-logo.svg" alt="Tanque Verde Hawks" class="navbar-logo">
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
                    <a class="nav-link" href="#" id="nav-records" title="Overall Records">📊</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" id="nav-top10" title="All-Time Top 10">🔟</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" id="nav-relays" title="Relay Records">🤝</a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" id="nav-season-top10" title="Season Top 10">📅</a>
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
                    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" id="nav-summary" title="Season Summary">📈</a>
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
    <link rel="icon" type="image/svg+xml" href="/images/favicon.svg">
    <link rel="apple-touch-icon" href="/images/hawk-logo.svg">
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
            document.getElementById('nav-records').href = '/records/' + g + '-overall.html';
            document.getElementById('nav-top10').href = '/top10/' + g + '-alltime.html';
            document.getElementById('nav-relays').href = '/records/' + g + '-relays.html';
            
            // Update season links
            document.querySelectorAll('.season-link').forEach(link => {{
                const season = link.textContent;
                link.href = '/top10/' + g + '-' + season + '.html';
            }});
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
        
        # Determine table type based on column count
        num_cols = len(headers)
        table_class = 'table-5col' if num_cols == 5 else 'table-6col' if num_cols == 6 else ''
        
        # Build HTML table
        html = '<div class="table-responsive record-table">\n'
        html += f'<table class="table table-striped table-hover {table_class}">\n'
        html += '<thead>\n<tr>\n'
        for header in headers:
            html += f'<th>{header}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        # Grade abbreviation mapping
        grade_abbrev = {
            'Freshman': 'FR',
            'Sophomore': 'SO',
            'Junior': 'JR',
            'Senior': 'SR',
            'Open': 'OPEN'
        }
        
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
    
    # Wrap in sections for better styling
    html_content = f'<div class="content">\n{html_content}\n</div>'
    
    # Create full HTML page
    full_html = create_html_page(title, html_content)
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(full_html)


def main():
    print("=" * 80)
    print("GENERATING TANQUE VERDE SWIM WEBSITE")
    print("=" * 80)
    print()
    
    records_dir = Path('records')
    docs_dir = Path('docs')
    
    # Convert team records
    print("📊 Converting Team Records...")
    for record_file in records_dir.glob('records-*.md'):
        if 'boys' in record_file.name:
            output = docs_dir / 'records' / 'boys-overall.html'
            title = "Boys Team Records"
        elif 'girls' in record_file.name:
            output = docs_dir / 'records' / 'girls-overall.html'
            title = "Girls Team Records"
        else:
            continue
        convert_markdown_file(record_file, output, title)
    
    # Convert relay records
    print("\n🏃 Converting Relay Records...")
    for relay_file in records_dir.glob('relay-records-*.md'):
        if 'boys' in relay_file.name:
            output = docs_dir / 'records' / 'boys-relays.html'
            title = "Boys Relay Records"
        elif 'girls' in relay_file.name:
            output = docs_dir / 'records' / 'girls-relays.html'
            title = "Girls Relay Records"
        else:
            continue
        convert_markdown_file(relay_file, output, title)
    
    # Convert top 10 lists
    print("\n🔟 Converting Top 10 Lists...")
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
        convert_markdown_file(top10_file, output, title)
    
    # Convert annual summaries
    print("\n📅 Converting Annual Summaries...")
    for annual_file in records_dir.glob('annual-summary-*.md'):
        season = annual_file.stem.replace('annual-summary-', '')
        title = f"{season} Season Summary"
        output = docs_dir / 'annual' / f"{season}.html"
        convert_markdown_file(annual_file, output, title)
    
    print("\n" + "=" * 80)
    print("✅ Website generation complete!")
    print(f"📁 Output directory: {docs_dir.absolute()}")
    print("=" * 80)


if __name__ == '__main__':
    main()

