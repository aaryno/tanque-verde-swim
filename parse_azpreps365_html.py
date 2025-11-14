#!/usr/bin/env python3
"""
Parse AzPreps365 HTML for Leaderboard Data

This script helps inspect and parse the actual HTML structure from azpreps365.com
to extract leaderboard data. Run this after saving raw HTML files.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import re


def parse_leaderboard_html(html_file: Path) -> pd.DataFrame:
    """
    Parse saved HTML file to extract leaderboard data.
    
    Args:
        html_file: Path to saved HTML file
        
    Returns:
        DataFrame with parsed leaderboard data
    """
    print(f"\n📄 Parsing: {html_file.name}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # The structure from the web search shows athlete names, schools, and times
    # Look for these patterns
    
    # Find all text content for inspection
    text = soup.get_text()
    
    # Look for known athletes from the search results
    known_athletes = [
        "Wade Olsson",
        "Zachary Duerkop", 
        "Jackson Eftekhar",
        "Austin Hargreaves",
        "Kadyn Hysong"
    ]
    
    found_athletes = []
    for athlete in known_athletes:
        if athlete in text:
            found_athletes.append(athlete)
    
    print(f"   Found {len(found_athletes)} known athletes: {found_athletes}")
    
    # Try to find structured data
    # Look for tables
    tables = soup.find_all('table')
    print(f"   Found {len(tables)} tables")
    
    # Look for divs with class containing "leader" or "stat"
    leader_divs = soup.find_all('div', class_=re.compile(r'lead|stat', re.I))
    print(f"   Found {len(leader_divs)} potential leader divs")
    
    # Extract event sections
    # Based on search results, events are organized by type
    # (200 Medley IM, 100 Fly, etc.)
    
    all_results = []
    
    # Try parsing table format
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:  # Need at least name, school, time
                result = {
                    'athlete': cells[0].get_text(strip=True),
                    'school': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                    'time': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                }
                if result['athlete'] and result['time']:
                    all_results.append(result)
    
    if all_results:
        df = pd.DataFrame(all_results)
        print(f"   ✓ Extracted {len(df)} results from tables")
        return df
    
    # If no table structure, try text parsing
    print("   ⚠️  No table structure found, attempting text parsing...")
    
    # Save a snippet for manual inspection
    snippet_file = html_file.parent / f"{html_file.stem}_snippet.txt"
    with open(snippet_file, 'w', encoding='utf-8') as f:
        # Save first 5000 chars for inspection
        f.write(text[:5000])
    print(f"   💾 Saved text snippet to: {snippet_file}")
    
    return pd.DataFrame()


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print(" AzPreps365 HTML Parser")
    print("="*70)
    
    # Find all saved HTML files
    harvest_dirs = list(Path("data/raw/azpreps365_harvest").glob("*/"))
    
    if not harvest_dirs:
        print("\n⚠️  No harvest directories found!")
        print("   Run harvest_azpreps365.py first to download HTML files")
        return
    
    # Use the most recent harvest
    latest_dir = sorted(harvest_dirs)[-1]
    print(f"\n📁 Processing harvest: {latest_dir.name}")
    
    html_files = list(latest_dir.glob("raw_html_*.html"))
    
    if not html_files:
        print("\n⚠️  No HTML files found!")
        return
    
    print(f"   Found {len(html_files)} HTML files")
    
    # Parse each file
    all_dataframes = []
    for html_file in html_files:
        df = parse_leaderboard_html(html_file)
        if not df.empty:
            # Extract metadata from filename
            # Format: raw_html_{gender}_{division}_{timestamp}.html
            parts = html_file.stem.split('_')
            if len(parts) >= 4:
                df['gender'] = parts[2]
                df['division'] = parts[3]
            all_dataframes.append(df)
    
    # Combine all results
    if all_dataframes:
        df_combined = pd.concat(all_dataframes, ignore_index=True)
        
        # Save combined results
        output_file = latest_dir / f"parsed_leaderboards_{latest_dir.name}.csv"
        df_combined.to_csv(output_file, index=False)
        
        print(f"\n✅ Saved {len(df_combined)} total results to: {output_file}")
    else:
        print("\n⚠️  No data could be parsed")
        print("   Manual inspection of HTML structure may be needed")
    
    print("\n" + "="*70)
    print(" Parsing Complete!")
    print("="*70)
    print()


if __name__ == "__main__":
    main()

