#!/usr/bin/env python3
"""
Detect potential duplicate swimmers with different name variations.

Identifies swimmers who might be the same person based on:
- Similar last names
- Similar first names (Sam/Samuel, Nick/Nicholas, Zach/Zachary)
- Overlapping grades/dates
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
import re


def normalize_name_for_matching(name: str) -> str:
    """Normalize name for fuzzy matching"""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)  # Remove punctuation
    return name


def get_name_variations(first_name: str) -> set[str]:
    """Get common variations of a first name"""
    name_lower = first_name.lower()
    
    variations = {name_lower}
    
    # Common nickname mappings
    nickname_map = {
        'nicholas': {'nick', 'nicolas', 'nicholas'},
        'nick': {'nick', 'nicolas', 'nicholas'},
        'nicolas': {'nick', 'nicolas', 'nicholas'},
        'samuel': {'sam', 'samuel', 'sammy'},
        'sam': {'sam', 'samuel', 'sammy'},
        'zachary': {'zach', 'zachary', 'zack'},
        'zach': {'zach', 'zachary', 'zack'},
        'zack': {'zach', 'zachary', 'zack'},
        'william': {'will', 'william', 'bill', 'billy'},
        'will': {'will', 'william', 'bill'},
        'robert': {'rob', 'robert', 'bob', 'bobby'},
        'rob': {'rob', 'robert', 'bob'},
        'benjamin': {'ben', 'benjamin', 'benji'},
        'ben': {'ben', 'benjamin', 'benji'},
        'michael': {'mike', 'michael', 'mikey'},
        'mike': {'mike', 'michael', 'mikey'},
        'christopher': {'chris', 'christopher'},
        'chris': {'chris', 'christopher'},
        'joseph': {'joe', 'joseph', 'joey'},
        'joe': {'joe', 'joseph', 'joey'},
        'jonathan': {'jon', 'jonathan', 'jonny'},
        'jon': {'jon', 'jonathan', 'jonny'},
        'daniel': {'dan', 'daniel', 'danny'},
        'dan': {'dan', 'daniel', 'danny'},
        'matthew': {'matt', 'matthew'},
        'matt': {'matt', 'matthew'},
        'alexander': {'alex', 'alexander'},
        'alex': {'alex', 'alexander'},
        'elizabeth': {'liz', 'elizabeth', 'beth', 'lizzy'},
        'liz': {'liz', 'elizabeth', 'beth'},
        'katherine': {'kate', 'katherine', 'katie', 'kathy'},
        'kate': {'kate', 'katherine', 'katie'},
        'margaret': {'maggie', 'margaret', 'meg'},
        'maggie': {'maggie', 'margaret', 'meg'},
    }
    
    if name_lower in nickname_map:
        variations.update(nickname_map[name_lower])
    
    return variations


def find_potential_duplicates(swimmers_dir: Path) -> list[dict]:
    """Find potential duplicate swimmers"""
    
    # Load all swimmer files
    swimmers = []
    for csv_file in swimmers_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            if df.empty or 'Name' not in df.columns:
                continue
            
            name = df['Name'].iloc[0]
            gender = df['Gender'].iloc[0] if 'Gender' in df.columns else 'U'
            
            # Get grade range
            grades = df['grade'].dropna().unique() if 'grade' in df.columns else []
            
            # Parse name
            parts = name.split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = ' '.join(parts[1:])
            else:
                first_name = name
                last_name = ""
            
            swimmers.append({
                'file': csv_file.name,
                'full_name': name,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'grades': sorted(grades),
                'swim_count': len(df),
            })
        except Exception as e:
            continue
    
    # Group by last name
    by_last_name = defaultdict(list)
    for swimmer in swimmers:
        if swimmer['last_name']:
            by_last_name[swimmer['last_name'].lower()].append(swimmer)
    
    # Find potential duplicates
    duplicates = []
    for last_name, swimmers_with_name in by_last_name.items():
        if len(swimmers_with_name) < 2:
            continue
        
        # Check for first name variations
        for i, s1 in enumerate(swimmers_with_name):
            for s2 in swimmers_with_name[i+1:]:
                # Same gender?
                if s1['gender'] != s2['gender'] and s1['gender'] != 'U' and s2['gender'] != 'U':
                    continue
                
                # Check if first names are variations
                variations1 = get_name_variations(s1['first_name'])
                variations2 = get_name_variations(s2['first_name'])
                
                if variations1 & variations2:  # Intersection
                    # Likely duplicate!
                    duplicates.append({
                        'swimmer1': s1,
                        'swimmer2': s2,
                        'confidence': 'high' if s1['first_name'].lower() == s2['first_name'].lower() else 'medium',
                    })
    
    return duplicates


def main():
    script_dir = Path(__file__).parent
    swimmers_dir = script_dir / "data" / "raw" / "swimmers"
    
    print("🔍 Detecting Potential Duplicate Swimmers\n")
    print("=" * 80)
    
    duplicates = find_potential_duplicates(swimmers_dir)
    
    if not duplicates:
        print("\n✓ No potential duplicates found!")
        return
    
    print(f"\n📊 Found {len(duplicates)} potential duplicate(s)\n")
    
    for i, dup in enumerate(duplicates, 1):
        s1 = dup['swimmer1']
        s2 = dup['swimmer2']
        
        print(f"\n{i}. Potential Match ({dup['confidence']} confidence)")
        print(f"   [1] {s1['full_name']}")
        print(f"       File: {s1['file']}")
        print(f"       Gender: {s1['gender']}, Grades: {s1['grades']}, Swims: {s1['swim_count']}")
        print(f"   [2] {s2['full_name']}")
        print(f"       File: {s2['file']}")
        print(f"       Gender: {s2['gender']}, Grades: {s2['grades']}, Swims: {s2['swim_count']}")
    
    print("\n" + "=" * 80)
    print("\n✓ Scan complete!")
    print("\nNext: Run consolidate_swimmers.py to merge duplicates")


if __name__ == "__main__":
    main()

