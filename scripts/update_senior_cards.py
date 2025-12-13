#!/usr/bin/env python3
"""
Update the Class of 2026 senior cards in index.html with:
1. Record badges for all records they hold (not just 2026)
2. Complete swim history with first/last times and improvement badges
"""

import json
import re
from pathlib import Path

def calculate_pb_badge_class(time_drop, distance):
    """Calculate PB badge color based on time drop per 50y distance"""
    if time_drop <= 0:
        return None
    
    # Calculate seconds per 50y
    if "50" in distance:
        s_per_50y = time_drop / 1
    elif "100" in distance:
        s_per_50y = time_drop / 2
    elif "200" in distance:
        s_per_50y = time_drop / 4
    elif "500" in distance:
        s_per_50y = time_drop / 10
    else:
        s_per_50y = time_drop / 2  # Default
    
    # Classify improvement
    if s_per_50y >= 5.0:
        return "pb-black"
    elif s_per_50y >= 4.0:
        return "pb-darkgray"
    elif s_per_50y >= 3.0:
        return "pb-gray"
    elif s_per_50y >= 2.0:
        return "pb-mediumgray"
    elif s_per_50y >= 1.0:
        return "pb-lightgray"
    elif s_per_50y >= 0.5:
        return "pb-verylightgray"
    else:
        return None

def parse_time(time_str):
    """Convert time string to seconds for comparison"""
    if not time_str:
        return None
    
    # Remove any whitespace
    time_str = time_str.strip()
    
    # Handle formats: 1:23.45 or 23.45
    if ':' in time_str:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        return float(time_str)

def get_alltime_bests(swimmer_name, gender):
    """Get best times from all-time Top 10 file"""
    bests = {}
    
    alltime_file = Path(f"records/top10-{gender}-alltime.md")
    if not alltime_file.exists():
        return bests
    
    with open(alltime_file, 'r') as f:
        content = f.read()
    
    # Find lines with this swimmer
    pattern = rf"\|\s*\d+\s*\|\s*([\d:\.]+)\s*\|\s*{re.escape(swimmer_name)}\s*\|([^|]*)\|([^|]*)\|([^|]*)\|"
    
    current_event = None
    for line in content.split('\n'):
        # Check if this is an event header (## or ###)
        if line.startswith('###'):
            current_event = line.replace('###', '').strip()
        elif line.startswith('##'):
            current_event = line.replace('##', '').strip()
        
        # Check if this line has the swimmer
        if swimmer_name in line and '|' in line:
            match = re.search(pattern, line)
            if match and current_event:
                time_str = match.group(1).strip()
                year = match.group(2).strip()
                date_str = match.group(3).strip()
                meet = match.group(4).strip()
                
                # If we don't have this event yet, or if this is a better time
                if current_event not in bests:
                    bests[current_event] = {
                        'time': time_str,
                        'time_seconds': parse_time(time_str),
                        'year': year,
                        'date': date_str,
                        'meet': meet,
                        'season': 'alltime'
                    }
    
    return bests

def generate_senior_card(name, data):
    """Generate HTML for a senior's card with complete data"""
    
    records = data['records']
    history = data['history']
    gender = data['gender']
    
    # Filter out the weird "Tanque Verde High School Swimming" event
    history = {k: v for k, v in history.items() if k != "Tanque Verde High School Swimming"}
    
    # Also get the best times from all-time records to ensure we have the absolute best
    alltime_bests = get_alltime_bests(name, gender)
    
    # Update history with all-time bests if they're better
    for event, best_time in alltime_bests.items():
        if event in history:
            # Compare times
            if best_time['time_seconds'] < history[event]['last_swim']['time_seconds']:
                # Update last swim
                old_last = history[event]['last_swim']['time_seconds']
                history[event]['last_swim'] = best_time
                # Don't recalculate time drop - keep the original from first swim
        else:
            # Add as a new event if not in history
            history[event] = {
                'first_swim': best_time,
                'last_swim': best_time,
                'total_swims': 1,
                'time_drop': 0,
                'improvement_text': "Only 1 recorded swim"
            }
    
    # Group records by event
    records_by_event = {}
    for record in records:
        event = record['event']
        if event == "Team Records - Short Course Yards (SCY)":
            # Need to match this with actual event from history
            # For now, we'll handle this manually based on the time
            continue
        if event not in records_by_event:
            records_by_event[event] = []
        records_by_event[event].append(record)
    
    # Manually map known records
    record_events = set()
    if name == "Zachary Duerkop":
        record_events = {"100 Butterfly", "100 Breaststroke"}
    elif name == "Logan Sulger":
        record_events = {"100 Backstroke"}
    
    # Start card HTML
    html = f'''                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">{name}'''
    
    # Add record badges to name
    if record_events:
        for event in sorted(record_events):
            # Abbreviate event names
            event_abbrev = event.replace("100 ", "").replace("200 ", "").replace("500 ", "")
            html += f''' <span class="badge badge-sr">{event_abbrev}</span>'''
    
    html += '''</h5>\n'''
    
    # Count state meets and total events
    state_meets = set()
    total_events = len(history)
    
    for event, event_data in history.items():
        if "State" in event_data['last_swim']['meet']:
            state_meets.add(event_data['last_swim']['season'])
    
    # Add state meet summary
    if len(state_meets) > 0:
        html += f'''                            <p class="mb-2"><strong>{len(state_meets)} State Meet{"s" if len(state_meets) != 1 else ""}</strong> ({total_events} events)</p>\n'''
    else:
        html += f'''                            <p class="mb-2"><strong>4 Years Active</strong></p>\n'''
    
    # Add event history
    for event in sorted(history.keys()):
        event_data = history[event]
        first = event_data['first_swim']
        last = event_data['last_swim']
        time_drop = event_data['time_drop']
        
        # Determine if this is a record event
        is_record = event in record_events
        
        # Show best time with record indicator
        html += f'''                            <p class="mb-1"><small>{event}: <span class="time">{last['time']}</span>'''
        if is_record:
            html += ''' <span class="badge badge-sr">SR</span>'''
        html += '''</small></p>\n'''
        
        # Show improvement if multiple swims
        if event_data['total_swims'] > 1 and time_drop != 0:
            # Add expandable details
            if time_drop > 0:
                pb_class = calculate_pb_badge_class(time_drop, event)
                pb_badge = f'<span class="badge badge-pb {pb_class} ms-1">-{time_drop:.2f}s</span>' if pb_class else ''
                
                html += f'''                            <p class="mb-0"><small class="text-muted">First: {first['time']} ({first['date'][:3]} {first['date'].split()[-1]}){pb_badge}</small></p>\n'''
    
    html += '''                        </div>
                    </div>
                </div>'''
    
    return html

def main():
    # Load analysis data
    with open('data/class_of_2026_analysis.json', 'r') as f:
        analysis = json.load(f)
    
    # Read current index.html
    with open('docs/index.html', 'r') as f:
        html_content = f.read()
    
    # Generate new cards for each senior
    senior_cards = []
    seniors_order = [
        "Zachary Duerkop",
        "Logan Sulger",
        "Madeline Barnard",
        "Grayson The",
        "Adrianna Witte",
        "Carter Caballero",
        "Brooklyn Johnson"
    ]
    
    for name in seniors_order:
        if name in analysis:
            card_html = generate_senior_card(name, analysis[name])
            senior_cards.append(card_html)
            print(f"Generated card for {name}")
    
    # Find the Class of 2026 section and replace the cards
    # Find start of cards section
    start_pattern = r'<div class="row g-4">'
    end_pattern = r'</div>\s*</div>\s*</div>\s*\n\s*<!-- Boys Records & Stats -->'
    
    # Find the specific section after "Congrats Class of 2026"
    congrats_start = html_content.find('<!-- Congrats Class of 2026 -->')
    if congrats_start == -1:
        print("Could not find Congrats Class of 2026 comment!")
        return
    
    # Search within that section
    search_content = html_content[congrats_start:congrats_start + 10000]
    match = re.search(
        f'{start_pattern}(.*?){end_pattern}',
        search_content,
        re.DOTALL
    )
    
    if not match:
        print("Could not find Class of 2026 section!")
        return
    
    # Build new cards section
    new_cards_html = "\n" + "\n".join(senior_cards) + "\n            "
    
    # Replace
    actual_match_start = congrats_start + match.start(1)
    actual_match_end = congrats_start + match.end(1)
    new_html = html_content[:actual_match_start] + new_cards_html + html_content[actual_match_end:]
    
    # Write back
    with open('docs/index.html', 'w') as f:
        f.write(new_html)
    
    print("\n✓ Updated docs/index.html with enriched senior cards")

if __name__ == "__main__":
    main()

