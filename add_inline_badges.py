#!/usr/bin/env python3
"""
Update state highlights and Class of 2026 sections to add badges inline with times.
- School Record badges (SR)
- Class Record badges (FR/SO/JR/SR)
- Personal Best badges (PB with gradient)
- Mobile-responsive badge text
"""

import re
from pathlib import Path

# State highlight swimmers with their records and PBs
STATE_HIGHLIGHTS = [
    {
        'name': 'Zachary Duerkop',
        'grade': 'SR',
        'event': 'Boys 100 Fly',
        'time': '52.48',
        'place': '2nd',
        'school_record': True,
        'class_record': 'SR',
        'pb_drop': None  # No PB info for this one
    },
    {
        'name': 'Wade Olsson',
        'grade': 'JR',
        'event': 'Boys 200 IM',
        'time': '1:57.78',
        'place': '2nd',
        'school_record': True,
        'class_record': 'JR',
        'pb_drop': None
    },
    {
        'name': 'Wade Olsson',
        'grade': 'JR',
        'event': 'Boys 100 Breast',
        'time': '1:00.82',
        'place': '3rd',
        'school_record': False,
        'class_record': None,
        'pb_drop': None
    },
    {
        'name': 'Kent Olsson',
        'grade': 'FR',
        'event': 'Boys 500 Free',
        'time': '5:07.85',
        'place': '4th',
        'school_record': False,
        'class_record': 'FR',
        'pb_drop': 15.21  # -15.21s
    },
    {
        'name': 'Logan Sulger',
        'grade': 'SR',
        'event': 'Girls 100 Back',
        'time': '1:02.29',
        'place': '5th',
        'school_record': True,
        'class_record': 'SR',
        'pb_drop': None
    },
    {
        'name': 'Jackson Eftekhar',
        'grade': 'JR',
        'event': 'Boys 100 Fly',
        'time': '54.92',
        'place': '8th',
        'school_record': False,
        'class_record': None,
        'pb_drop': None
    },
    {
        'name': 'Adrianna Witte',
        'grade': 'SR',
        'event': 'Girls 100 Breast',
        'time': '1:14.68',
        'place': '8th',
        'school_record': False,
        'class_record': None,
        'pb_drop': None
    },
    {
        'name': 'Grayson The',
        'grade': 'SR',
        'event': 'Boys 50 Free',
        'time': '23.54',
        'place': '10th',
        'school_record': False,
        'class_record': None,
        'pb_drop': None
    },
    {
        'name': 'Hadley Cusson',
        'grade': 'JR',
        'event': 'Girls 50 Free',
        'time': '26.61',
        'place': '10th',
        'school_record': False,
        'class_record': None,
        'pb_drop': None
    },
    {
        'name': 'Kent Olsson',
        'grade': 'FR',
        'event': 'Boys 100 Back',
        'time': '1:00.15',
        'place': '10th',
        'school_record': False,
        'class_record': 'FR',
        'pb_drop': None
    },
    {
        'name': 'Madeline Barnard',
        'grade': 'SR',
        'event': 'Girls 100 Breast',
        'time': '1:15.82',
        'place': '10th',
        'school_record': False,
        'class_record': None,
        'pb_drop': None
    },
]

def get_pb_badge_class(drop_seconds, event):
    """Get PB badge class based on time drop per 50y"""
    if drop_seconds <= 0:
        return "pb-verylightgray"
    
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

def generate_badges_html(highlight):
    """Generate inline badges for a highlight"""
    badges = []
    
    # School record or class record (not both)
    if highlight['school_record']:
        # Mobile: "SR", Desktop: "Record"
        badges.append('<span class="badge badge-sr"><span class="d-none d-md-inline">Record</span><span class="d-md-none">SR</span></span>')
    elif highlight['class_record']:
        # Mobile/Desktop: "FR Record", "JR Record", etc.
        grade = highlight['class_record']
        badges.append(f'<span class="badge badge-class-record grade-{grade.lower()}"><span class="d-none d-md-inline">{grade} </span>Record</span>')
    
    # PB badge
    if highlight['pb_drop']:
        pb_class = get_pb_badge_class(highlight['pb_drop'], highlight['event'])
        pb_drop = highlight['pb_drop']
        badges.append(f'<span class="badge badge-pb {pb_class}">-{pb_drop:.2f}s</span>')
    
    return ' '.join(badges) if badges else ''

def update_state_highlights(content):
    """Update state highlights section with inline badges"""
    
    for highlight in STATE_HIGHLIGHTS:
        # Find this specific card
        # Pattern: <h6 class="card-title"><span class="place-badge ...>...</span> Name <span class="grade-badge ...>...</span></h6>
        #          <p class="card-text mb-0">Event - <span class="time">time</span></p>
        #          <div class="highlight-badges">...</div>
        
        # Escape special characters in name for regex
        name_pattern = re.escape(highlight['name'])
        event_pattern = re.escape(highlight['event'])
        time_pattern = re.escape(highlight['time'])
        
        # Find the card and replace the time line + badges section
        # Old format: <p class="card-text mb-0">Event - <span class="time">time</span></p>\n<div class="highlight-badges">...</div>
        # New format: <p class="card-text mb-0">Event - <span class="time">time</span> badges</p>
        
        old_pattern = (
            rf'(<h6 class="card-title">.*?{name_pattern}.*?</h6>\s*'
            rf'<p class="card-text mb-0">{event_pattern} - <span class="time">{time_pattern}</span>)'
            rf'(</p>)\s*(?:<div class="highlight-badges">.*?</div>)?'
        )
        
        badges_html = generate_badges_html(highlight)
        new_content = (
            r'\1'
            + (f' {badges_html}' if badges_html else '')
            + r'\2'
        )
        
        content = re.sub(old_pattern, new_content, content, flags=re.DOTALL)
    
    return content

def main():
    # Read index.html
    with open('docs/index.html', 'r') as f:
        content = f.read()
    
    # Update state highlights
    content = update_state_highlights(content)
    
    # Write back
    with open('docs/index.html', 'w') as f:
        f.write(content)
    
    print("✓ Updated state highlights with inline badges")
    print("  - School Record badges (SR / Record)")
    print("  - Class Record badges (FR/SO/JR/SR Record)")
    print("  - PB badges with gradient colors")
    print("  - Mobile-responsive badge text")

if __name__ == "__main__":
    main()

