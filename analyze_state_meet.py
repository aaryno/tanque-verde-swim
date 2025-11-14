#!/usr/bin/env python3
"""
Analyze 2025 AIA D3 State Championship results for Tanque Verde
Extract highlights, top finishers, and improvements
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from time_formatter import format_time_display


def parse_time_to_seconds(time_str):
    """Convert time string to seconds"""
    if pd.isna(time_str) or time_str == '':
        return None
    
    parts = time_str.split(':')
    if len(parts) == 2:
        # MM:SS.mm format
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    else:
        # SS.mm format
        return float(parts[0])


def main():
    # Load state meet data
    state_file = Path('data/raw/aia-state/tvhs-state-2025.csv')
    df = pd.read_csv(state_file)
    
    # Convert times to seconds for comparison
    df['time_seconds'] = df['SwimTime'].apply(parse_time_to_seconds)
    
    # Identify prelims (has 'q' in splits) vs finals (has numeric place or empty splits)
    df['is_prelim'] = df['splits'].fillna('').str.contains('q', case=False, na=False)
    df['is_final'] = ~df['is_prelim']
    
    # Parse place as integer
    df['place_int'] = pd.to_numeric(df['place'], errors='coerce')
    
    print("=" * 80)
    print("2025 AIA D3 STATE CHAMPIONSHIP HIGHLIGHTS")
    print("Tanque Verde High School")
    print("=" * 80)
    print()
    
    # Top 10 finishers
    print("TOP 10 FINISHERS:")
    print("=" * 80)
    top10 = df[df['place_int'] <= 10].sort_values(['place_int', 'Gender', 'Event'])
    
    for _, row in top10.iterrows():
        gender_label = "Boys" if row['Gender'] == 'M' else "Girls"
        time_display = format_time_display(row['SwimTime'])
        final_label = "Finals" if row['is_final'] else "Prelims"
        print(f"{row['place_int']:2.0f}. {row['Name']:20s} | {gender_label} {row['Event']:20s} | {time_display:>8s} ({final_label})")
    
    print()
    print("=" * 80)
    print("TIME IMPROVEMENTS (Prelims to Finals):")
    print("=" * 80)
    
    # Find swimmers who swam both prelims and finals
    swimmers_with_both = df.groupby(['Name', 'Event']).filter(lambda x: len(x) == 2)
    
    if not swimmers_with_both.empty:
        improvements = []
        
        for (name, event), group in swimmers_with_both.groupby(['Name', 'Event']):
            prelim = group[group['is_prelim']]
            final = group[group['is_final']]
            
            if not prelim.empty and not final.empty:
                prelim_time = prelim.iloc[0]['time_seconds']
                final_time = final.iloc[0]['time_seconds']
                improvement = prelim_time - final_time
                
                if improvement > 0:  # Only show improvements (drops in time)
                    improvements.append({
                        'name': name,
                        'event': event,
                        'prelim_time': prelim.iloc[0]['SwimTime'],
                        'final_time': final.iloc[0]['SwimTime'],
                        'improvement': improvement,
                        'place': final.iloc[0]['place_int']
                    })
        
        # Sort by improvement
        improvements.sort(key=lambda x: x['improvement'], reverse=True)
        
        for imp in improvements:
            prelim_display = format_time_display(imp['prelim_time'])
            final_display = format_time_display(imp['final_time'])
            improvement_display = f"{imp['improvement']:.2f}s"
            print(f"{imp['name']:20s} | {imp['event']:20s} | {prelim_display:>8s} → {final_display:>8s} | -{improvement_display:>6s} | Place: {imp['place']:.0f}")
    
    print()
    print("=" * 80)
    print("ALL FINISHERS:")
    print("=" * 80)
    
    # Get best result for each swimmer/event combo (finals if available, else prelims)
    best_results = []
    for (name, event), group in df.groupby(['Name', 'Event']):
        finals = group[group['is_final']]
        if not finals.empty:
            best = finals.iloc[0]
        else:
            best = group.iloc[0]
        best_results.append(best)
    
    df_best = pd.DataFrame(best_results).sort_values(['Gender', 'Event', 'place_int'])
    
    for _, row in df_best.iterrows():
        gender_label = "Boys" if row['Gender'] == 'M' else "Girls"
        time_display = format_time_display(row['SwimTime'])
        place_str = f"{row['place_int']:.0f}" if not pd.isna(row['place_int']) else "–"
        print(f"{place_str:>3s}. {row['Name']:20s} | {gender_label} {row['Event']:20s} | {time_display:>8s}")
    
    print()
    print("=" * 80)
    print(f"SUMMARY: {len(df_best)} swims from {df_best['Name'].nunique()} swimmers")
    print(f"Top 10 Finishes: {len(df[df['place_int'] <= 10])}")
    print("=" * 80)


if __name__ == '__main__':
    main()

