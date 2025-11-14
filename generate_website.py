#!/usr/bin/env python3
"""
Generate GitHub Pages website from markdown records
Converts all markdown files to HTML with Bootstrap styling and navigation
"""

import re
from pathlib import Path
from datetime import datetime


def create_nav_html():
    """Create the 2-row navigation header"""
    return '''
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/tanque-verde-swim/index.html">
                🏊 Tanque Verde Swimming
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
        </div>
    </nav>
    
    <!-- Girls Navigation Row (Silver/Grey) -->
    <nav class="navbar navbar-expand-lg navbar-dark girls-nav">
        <div class="container-fluid">
            <span class="navbar-text text-white me-3"><strong>GIRLS</strong></span>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#girlsNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="girlsNav">
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            Team Records
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/tanque-verde-swim/records/girls-overall.html">Overall Records</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/records/girls-relays.html">Relay Records</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            Top 10 Lists
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/girls-alltime.html">All-Time</a></li>
                            <li><hr class="dropdown-divider" style="border-color: rgba(255,255,255,0.2);"></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/girls-2024-25.html">2024-25</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/girls-2023-24.html">2023-24</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/girls-2022-23.html">2022-23</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            Annual Summaries
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2025-26.html">2025-26</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2024-25.html">2024-25</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2023-24.html">2023-24</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2022-23.html">2022-23</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- Boys Navigation Row (Forest Green) -->
    <nav class="navbar navbar-expand-lg navbar-dark boys-nav">
        <div class="container-fluid">
            <span class="navbar-text text-white me-3"><strong>BOYS</strong></span>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#boysNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="boysNav">
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            Team Records
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/tanque-verde-swim/records/boys-overall.html">Overall Records</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/records/boys-relays.html">Relay Records</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            Top 10 Lists
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/boys-alltime.html">All-Time</a></li>
                            <li><hr class="dropdown-divider" style="border-color: rgba(255,255,255,0.2);"></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/boys-2024-25.html">2024-25</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/boys-2023-24.html">2023-24</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/top10/boys-2022-23.html">2022-23</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            Annual Summaries
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2025-26.html">2025-26</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2024-25.html">2024-25</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2023-24.html">2023-24</a></li>
                            <li><a class="dropdown-item" href="/tanque-verde-swim/annual/2022-23.html">2022-23</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Tanque Verde Swimming</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/tanque-verde-swim/css/style.css">
    
    <!-- Favicon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏊</text></svg>">
</head>
<body>
    {nav_html}
    
    <!-- Page Header -->
    <div class="page-header">
        <div class="container">
            <h1>{title}</h1>
            <div class="subtitle">Tanque Verde High School Swimming & Diving</div>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="container my-4">
        {content}
    </div>
    
    <!-- Footer -->
    <footer class="mt-5">
        <div class="container text-center">
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
        
        # Parse header
        headers = [h.strip() for h in header_row.split('|') if h.strip()]
        
        # Parse data rows
        rows = []
        for row in data_rows.strip().split('\n'):
            if row.strip():
                cells = [c.strip() for c in row.split('|') if c.strip()]
                if cells:
                    rows.append(cells)
        
        # Build HTML table
        html = '<div class="table-responsive record-table">\n'
        html += '<table class="table table-striped table-hover">\n'
        html += '<thead>\n<tr>\n'
        for header in headers:
            html += f'<th>{header}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for row in rows:
            html += '<tr>\n'
            for i, cell in enumerate(row):
                # Check if this is a record holder (bold text)
                if '**' in cell:
                    cell = cell.replace('**', '')
                    html += f'<td class="record-holder">{cell}</td>\n'
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

