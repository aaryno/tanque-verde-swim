#!/usr/bin/env python3
"""
Analyze senior swimmers' careers for the Class of 2026
Generate career retrospectives with best times, state appearances, and progression
"""

import pandas as pd
from pathlib import Path
import sys
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from time_formatter import format_time_display


# Seniors for 2025-26
SENIORS = [
    "Adrianna Witte",
    "Brooklyn Johnson",
    "Carter Caballero",
    "Grayson The",
    "Logan Sulger",
    "Madeline Barnard",
    "Zachary Duerkop"
]


def find_swimmer_file(name):
    """Find the CSV file for a swimmer"""
    data_dir = Path('data/raw/swimmers')
    for file in data_dir.glob('*.csv'):
        # Check if name matches (case insensitive, handle variations)
        if name.lower().replace(' ', '-') in file.stem.lower():
            return file
    return None


def parse_time_to_seconds(time_str):
    """Convert time string to seconds"""
    if pd.isna(time_str) or time_str == '':
        return None
    
    parts = str(time_str).split(':')
    if len(parts) == 2:
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    else:
        return float(parts[0])


def analyze_swimmer(name):
    """Analyze a single swimmer's career"""
    file_path = find_swimmer_file(name)
    
    if not file_path:
        print(f"⚠️  No data file found for {name}")
        return None
    
    df = pd.read_csv(file_path)
    
    # Filter out relays
    df = df[~df['Event'].str.contains('RELAY', case=False, na=False)].copy()
    
    # Convert times
    df['time_seconds'] = df['SwimTime'].apply(parse_time_to_seconds)
    
    # Parse dates
    df['SwimDate'] = pd.to_datetime(df['SwimDate'], errors='coerce')
    df['year'] = df['SwimDate'].dt.year
    
    # Identify state meets
    df['is_state'] = df['MeetName'].str.contains('State|AIA', case=False, na=False)
    
    return {
        'name': name,
        'file': file_path.name,
        'df': df,
        'total_swims': len(df),
        'state_swims': len(df[df['is_state']]),
        'years_active': sorted(df['year'].dropna().unique().tolist())
    }


def get_best_times(swimmer_data):
    """Get best times by event"""
    df = swimmer_data['df']
    
    best_times = {}
    for event in df['Event'].unique():
        event_df = df[df['Event'] == event]
        if not event_df.empty:
            best = event_df.nsmallest(1, 'time_seconds').iloc[0]
            best_times[event] = {
                'time': best['SwimTime'],
                'time_seconds': best['time_seconds'],
                'date': best['SwimDate'],
                'meet': best['MeetName'],
                'year': best['year']
            }
    
    return best_times


def get_state_history(swimmer_data):
    """Get state meet history"""
    df = swimmer_data['df']
    state_df = df[df['is_state']].copy()
    
    if state_df.empty:
        return []
    
    # Group by year and event
    state_meets = []
    for year in sorted(state_df['year'].unique()):
        year_df = state_df[state_df['year'] == year]
        events = []
        for _, swim in year_df.iterrows():
            events.append({
                'event': swim['Event'],
                'time': swim['SwimTime'],
                'meet': swim['MeetName']
            })
        state_meets.append({
            'year': int(year),
            'events': events,
            'count': len(events)
        })
    
    return state_meets


def get_progression(swimmer_data, event):
    """Get year-by-year progression for an event"""
    df = swimmer_data['df']
    event_df = df[df['Event'] == event].copy()
    
    if event_df.empty:
        return []
    
    # Get best time by year
    progression = []
    for year in sorted(event_df['year'].dropna().unique()):
        year_df = event_df[event_df['year'] == year]
        best = year_df.nsmallest(1, 'time_seconds').iloc[0]
        progression.append({
            'year': int(year),
            'time': best['SwimTime'],
            'time_seconds': best['time_seconds'],
            'meet': best['MeetName']
        })
    
    return progression


def main():
    print("=" * 80)
    print("CLASS OF 2026 - SENIOR CAREER HIGHLIGHTS")
    print("Tanque Verde High School")
    print("=" * 80)
    print()
    
    all_seniors = []
    
    for senior_name in SENIORS:
        print(f"\n{'=' * 80}")
        print(f"{'=' * 80}")
        print(f"{senior_name.upper()}")
        print(f"{'=' * 80}")
        print(f"{'=' * 80}")
        
        data = analyze_swimmer(senior_name)
        
        if not data:
            continue
        
        all_seniors.append(data)
        
        print(f"\nCareer Overview:")
        print(f"  Total Individual Swims: {data['total_swims']}")
        print(f"  State Meet Appearances: {data['state_swims']} swims")
        print(f"  Years Active: {', '.join(map(str, data['years_active']))}")
        
        # Best times
        print(f"\nPersonal Best Times:")
        print("-" * 80)
        best_times = get_best_times(data)
        
        # Sort events by type
        event_order = ['50 FR', '100 FR', '200 FR', '500 FR', '100 BK', '100 BR', '100 FL', '200 IM']
        sorted_events = []
        for event_prefix in event_order:
            for event, times in best_times.items():
                if event.startswith(event_prefix):
                    sorted_events.append((event, times))
                    break
        
        for event, times in sorted_events:
            time_display = format_time_display(times['time'])
            date_str = times['date'].strftime('%b %d, %Y') if pd.notna(times['date']) else 'Unknown'
            print(f"  {event:20s} | {time_display:>8s} | {date_str} | {times['meet'][:40]}")
        
        # State meet history
        state_history = get_state_history(data)
        if state_history:
            print(f"\nState Meet History:")
            print("-" * 80)
            for year_data in state_history:
                print(f"  {year_data['year']} ({year_data['count']} events):")
                for event in year_data['events']:
                    time_display = format_time_display(event['time'])
                    print(f"    - {event['event']:20s} | {time_display:>8s}")
        
        # Show progression in signature events (events with 3+ years)
        print(f"\nCareer Progression (Signature Events):")
        print("-" * 80)
        
        # Find events with multiple years
        df = data['df']
        event_years = {}
        for event in df['Event'].unique():
            years = df[df['Event'] == event]['year'].dropna().nunique()
            if years >= 3:
                event_years[event] = years
        
        if event_years:
            for event in sorted(event_years.keys()):
                progression = get_progression(data, event)
                if len(progression) >= 3:
                    print(f"  {event}:")
                    for prog in progression:
                        time_display = format_time_display(prog['time'])
                        print(f"    {prog['year']}: {time_display:>8s}")
                    
                    # Calculate improvement
                    if len(progression) >= 2:
                        first_time = progression[0]['time_seconds']
                        last_time = progression[-1]['time_seconds']
                        improvement = first_time - last_time
                        if improvement > 0:
                            print(f"    Improvement: -{improvement:.2f}s ({progression[0]['year']}-{progression[-1]['year']})")
        else:
            print("  (Less than 3 years of data for any single event)")
    
    print(f"\n\n{'=' * 80}")
    print(f"SENIOR CLASS SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Seniors: {len(all_seniors)}")
    print(f"Total Combined Swims: {sum(s['total_swims'] for s in all_seniors)}")
    print(f"Total State Meet Swims: {sum(s['state_swims'] for s in all_seniors)}")
    print("=" * 80)


if __name__ == '__main__':
    main()

