#!/usr/bin/env python3
"""
Parse AIA State Championship PDFs for Tanque Verde High School swimmers

Extracts swimmer results from Arizona Interscholastic Association (AIA)
state championship PDFs and saves them to CSV files.
"""

import pdfplumber
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

# AIA State Championship PDFs (2001-2025)
AIA_STATE_MEETS = [
    {"year": 2025, "file_id": None, "date": "11/8/2025"},
    {"year": 2024, "file_id": 18411, "date": "11/9/2024"},
    {"year": 2023, "file_id": 18187, "date": "11/4/2023"},
    {"year": 2022, "file_id": 17935, "date": "11/5/2022"},
    {"year": 2021, "file_id": 17672, "date": "10/23/2021"},
    {"year": 2020, "file_id": 17252, "date": "2/21/2020"},  # Pre-COVID
    {"year": 2019, "file_id": 16845, "date": "11/9/2019"},
    {"year": 2018, "file_id": 16553, "date": "11/3/2018"},
    {"year": 2017, "file_id": 16054, "date": "11/4/2017"},
    {"year": 2016, "file_id": 15661, "date": "11/5/2016"},
    {"year": 2015, "file_id": 15247, "date": "11/7/2015"},
    {"year": 2014, "file_id": 14651, "date": "11/8/2014"},
    {"year": 2013, "file_id": 14249, "date": "11/9/2013"},
    {"year": 2012, "file_id": 13462, "date": "11/3/2012"},
    {"year": 2011, "file_id": 12611, "date": "11/5/2011"},
    {"year": 2010, "file_id": 11757, "date": "11/6/2010"},
    {"year": 2009, "file_id": 10504, "date": "11/7/2009"},
    {"year": 2008, "file_id": 9361, "date": "11/8/2008"},
    {"year": 2007, "file_id": 7844, "date": "11/10/2007"},
    {"year": 2006, "file_id": 6039, "date": "11/4/2006"},
    {"year": 2005, "file_id": 4023, "date": "11/5/2005"},
    {"year": 2004, "file_id": 722, "date": "11/6/2004"},
    {"year": 2003, "file_id": 3826, "date": "11/8/2003"},
    {"year": 2002, "file_id": 7268, "date": "11/9/2002"},
    {"year": 2001, "file_id": 7171, "date": "11/10/2001"},
]


def normalize_event_name(event: str) -> str:
    """Convert AIA event name to standard format"""
    event_map = {
        "200 Medley Relay": "200 MR SCY",
        "200 Free": "200 FR SCY",
        "200 IM": "200 IM SCY",
        "50 Free": "50 FR SCY",
        "100 Fly": "100 FL SCY",
        "100 Free": "100 FR SCY",
        "500 Free": "500 FR SCY",
        "200 Free Relay": "200 FR RELAY SCY",
        "100 Back": "100 BK SCY",
        "100 Breast": "100 BR SCY",
        "400 Free Relay": "400 FR RELAY SCY",
    }
    return event_map.get(event, event)


def parse_swimmer_line(line: str) -> Optional[Dict]:
    """
    Parse a results line like:
    12 Olsson, Wade 09 Tanque Verde High School 5:24.27 5:17.84
    
    Returns dict with place, name, grade, school, prelim_time, finals_time
    """
    # Pattern: place lastname, firstname grade school prelim finals [splits]
    # Grade is 09-12 (with leading zero)
    pattern = r'^\s*(\d+)\s+([A-Za-z\-]+),\s+([A-Za-z\s]+?)\s+(\d{2})\s+(.*?)\s+([\d:\.]+)\s+([\d:\.]+|DQ|DNF|SCR)'
    
    match = re.match(pattern, line)
    if match:
        place, last_name, first_name, grade, school, prelim, finals = match.groups()
        
        # Extract splits if present (remaining part of line after finals time)
        splits_text = line[match.end():].strip()
        
        return {
            'place': int(place),
            'name': f"{first_name.strip()} {last_name.strip()}",
            'grade': int(grade),
            'school': school.strip(),
            'prelim_time': prelim if prelim not in ['DQ', 'DNF', 'SCR'] else None,
            'finals_time': finals if finals not in ['DQ', 'DNF', 'SCR'] else None,
            'splits': splits_text if splits_text else None,
        }
    return None


def determine_gender_from_context(lines: List[str], line_idx: int) -> str:
    """Determine gender by looking at nearby event headers"""
    # Look backwards up to 50 lines for event header
    for i in range(max(0, line_idx - 50), line_idx):
        line = lines[i].lower()
        if 'boys' in line or '#boys' in line:
            return 'M'
        if 'girls' in line or '#girls' in line:
            return 'F'
    return 'U'  # Unknown


def parse_aia_pdf(pdf_path: str, school_name: str = "Tanque Verde") -> List[Dict]:
    """
    Extract all swims for a specific school from an AIA state championship PDF
    
    Args:
        pdf_path: Path to PDF file
        school_name: School name to search for (default: "Tanque Verde")
    
    Returns:
        List of swim dictionaries with extracted data
    """
    swims = []
    current_event = None
    current_gender = None
    
    print(f"  📖 Parsing {Path(pdf_path).name}...")
    
    with pdfplumber.open(pdf_path) as pdf:
        all_lines = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_lines.extend(text.split('\n'))
        
        for i, line in enumerate(all_lines):
            # Check for event headers
            if "Yard" in line:
                # Boys/Girls event detection
                if "Boys" in line or "#Boys" in line:
                    current_gender = 'M'
                elif "Girls" in line or "#Girls" in line:
                    current_gender = 'F'
                
                # Event detection
                if "200 Yard Medley Relay" in line:
                    current_event = "200 Medley Relay"
                elif "200 Yard Free" in line and "Relay" not in line:
                    current_event = "200 Free"
                elif "200 Yard IM" in line:
                    current_event = "200 IM"
                elif "50 Yard Free" in line:
                    current_event = "50 Free"
                elif "100 Yard Fly" in line or "100 Yard Butterfly" in line:
                    current_event = "100 Fly"
                elif "100 Yard Free" in line and "Relay" not in line:
                    current_event = "100 Free"
                elif "500 Yard Free" in line:
                    current_event = "500 Free"
                elif "200 Yard Free Relay" in line:
                    current_event = "200 Free Relay"
                elif "100 Yard Back" in line:
                    current_event = "100 Back"
                elif "100 Yard Breast" in line:
                    current_event = "100 Breast"
                elif "400 Yard Free Relay" in line:
                    current_event = "400 Free Relay"
            
            # Look for school name
            if school_name in line and current_event:
                # Try to parse as swimmer result
                result = parse_swimmer_line(line)
                if result:
                    # Determine gender if not set
                    if not current_gender:
                        current_gender = determine_gender_from_context(all_lines, i)
                    
                    result['event'] = current_event
                    result['gender'] = current_gender
                    swims.append(result)
    
    return swims


def download_aia_pdf(year: int, file_id: int, output_dir: Path) -> Path:
    """Download AIA state championship PDF for a specific year"""
    import urllib.request
    
    url = f"https://aiaonline.org/files/{file_id}/{year}-swimming-and-diving-divisions-i-iii-state-championships.pdf"
    output_path = output_dir / f"aia-state-{year}.pdf"
    
    if output_path.exists():
        print(f"  ✓ Already downloaded: {year}")
        return output_path
    
    print(f"  ⬇ Downloading {year} state meet PDF...")
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"  ✓ Downloaded: {year}")
        return output_path
    except Exception as e:
        print(f"  ✗ Failed to download {year}: {e}")
        return None


def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    output_dir = script_dir / "data" / "raw" / "aia-state"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🏊 AIA State Championship Parser for Tanque Verde High School\n")
    print("=" * 80)
    
    all_swims = []
    
    # Download and parse each year
    for meet in AIA_STATE_MEETS:
        year = meet["year"]
        file_id = meet["file_id"]
        meet_date = meet["date"]
        
        print(f"\n📅 {year} State Championships")
        
        # Download PDF
        pdf_path = download_aia_pdf(year, file_id, output_dir)
        if not pdf_path:
            continue
        
        # Parse PDF for Tanque Verde swimmers
        try:
            swims = parse_aia_pdf(pdf_path, school_name="Tanque Verde")
            
            # Add year and date to each swim
            for swim in swims:
                swim['year'] = year
                swim['meet_date'] = meet_date
                swim['meet_name'] = f"{year} D-3 AIA State Championships (AZ)"
            
            print(f"  ✓ Found {len(swims)} Tanque Verde swims")
            all_swims.extend(swims)
            
        except Exception as e:
            print(f"  ✗ Error parsing {year}: {e}")
            continue
    
    print("\n" + "=" * 80)
    print(f"\n📊 Total: {len(all_swims)} swims extracted from {len(AIA_STATE_MEETS)} years")
    
    if all_swims:
        # Save to CSV
        df = pd.DataFrame(all_swims)
        
        # Normalize event names
        df['Event'] = df['event'].apply(normalize_event_name)
        
        # Use finals time, fallback to prelim if no finals
        df['SwimTime'] = df['finals_time'].fillna(df['prelim_time'])
        
        # Rename columns to match swimmer CSV format
        df = df.rename(columns={
            'name': 'Name',
            'gender': 'Gender',
            'meet_date': 'SwimDate',
            'meet_name': 'MeetName',
        })
        
        # Select and order columns
        output_df = df[[
            'Name', 'Gender', 'grade', 'Event', 'SwimTime', 
            'SwimDate', 'MeetName', 'place', 'splits', 'year'
        ]]
        
        # Save complete dataset
        output_file = output_dir / "tvhs-all-state-meets.csv"
        output_df.to_csv(output_file, index=False)
        print(f"\n✓ Saved to: {output_file}")
        
        # Save by year
        for year, year_df in output_df.groupby('year'):
            year_file = output_dir / f"tvhs-state-{year}.csv"
            year_df.to_csv(year_file, index=False)
        print(f"✓ Saved individual year files")
        
        # Show summary
        print(f"\n📈 Summary by year:")
        print(output_df.groupby('year').size().to_string())
        
        print(f"\n📈 Summary by swimmer:")
        print(output_df['Name'].value_counts().head(20).to_string())
    
    print("\n✓ Complete!")


if __name__ == "__main__":
    main()

