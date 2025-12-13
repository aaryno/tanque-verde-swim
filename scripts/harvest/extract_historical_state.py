#!/usr/bin/env python3
"""
Extract Tanque Verde swim times from historical AIA State Championship PDFs.

Downloads PDFs from AZPreps365 archives and extracts swim data.
"""

import subprocess
import re
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class SwimResult:
    """A single swim result."""
    event: str
    swimmer_name: str
    grade: str  # FR, SO, JR, SR
    time: str
    year: int
    gender: str  # M or F
    
    def to_dict(self):
        return {
            'event': self.event,
            'swimmer': self.swimmer_name,
            'grade': self.grade,
            'time': self.time,
            'year': self.year,
            'gender': self.gender
        }


# AZPreps365 archive meet IDs
MEET_IDS = {
    2001: 7171,
    2002: 7268,
    2003: 3826,
    2004: 722,
    2005: 4023,
    2006: 6039,
    2007: 7844,
    2008: 9361,
    2009: 10504,
    2010: 11757,
    2011: 12611,
}


def download_pdf(year: int, output_dir: Path) -> Optional[Path]:
    """Download state championship PDF for a given year."""
    if year not in MEET_IDS:
        print(f"No meet ID for year {year}")
        return None
    
    meet_id = MEET_IDS[year]
    output_path = output_dir / f"{year}-state.pdf"
    
    if output_path.exists():
        return output_path
    
    # Try common URL patterns
    base_url = f"https://aiaonline.org/files/{meet_id}"
    
    # Download
    import urllib.request
    try:
        # The PDFs seem to be accessible at various URLs, try the base
        url = f"{base_url}/{year}-swimming-and-diving-state-championships.pdf"
        urllib.request.urlretrieve(url, output_path)
        return output_path
    except Exception as e:
        print(f"Failed to download {year}: {e}")
        return None


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""
    except FileNotFoundError:
        print("pdftotext not found. Install with: brew install poppler")
        return ""


def parse_tanque_verde_results(text: str, year: int) -> list[SwimResult]:
    """Parse Tanque Verde results from PDF text."""
    results = []
    lines = text.split('\n')
    
    current_event = None
    current_gender = None
    
    # Event pattern
    event_pattern = re.compile(r'Event \d+ (Boys|Girls) (.+)')
    
    for i, line in enumerate(lines):
        # Track current event
        event_match = event_pattern.search(line)
        if event_match:
            current_gender = 'M' if event_match.group(1) == 'Boys' else 'F'
            current_event = event_match.group(2).strip()
            continue
        
        # Look for Tanque Verde mentions
        if 'Tanque Verde' in line:
            # Extract grade (usually on same line as school)
            grade_match = re.match(r'(FR|SO|JR|SR)\s+Tanque Verde', line)
            grade = grade_match.group(1) if grade_match else ''
            
            # Look for swimmer name in nearby lines (usually 1-5 lines before)
            swimmer_name = None
            for j in range(max(0, i-10), i):
                prev_line = lines[j].strip()
                # Names are usually "Last, First" format
                name_match = re.match(r'^([A-Z][a-z]+),\s*([A-Z][a-z]+)$', prev_line)
                if name_match:
                    swimmer_name = f"{name_match.group(2)} {name_match.group(1)}"
                    break
            
            # Look for time in nearby lines (usually 1-5 lines after)
            time_str = None
            for j in range(i, min(len(lines), i+10)):
                next_line = lines[j].strip()
                # Times are like "24.45" or "1:23.45" or "5:12.34"
                time_match = re.match(r'^(\d{1,2}:)?\d{1,2}\.\d{2}(\s*[A-Z])?$', next_line)
                if time_match:
                    time_str = next_line.split()[0]  # Remove any letter suffix
                    break
            
            if swimmer_name and time_str and current_event:
                results.append(SwimResult(
                    event=current_event,
                    swimmer_name=swimmer_name,
                    grade=grade,
                    time=time_str,
                    year=year,
                    gender=current_gender or 'M'
                ))
    
    return results


def main():
    base_dir = Path(__file__).parent
    data_dir = base_dir / "historical_data"
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("EXTRACTING HISTORICAL STATE CHAMPIONSHIP DATA")
    print("=" * 70)
    
    all_results = []
    
    for year in range(2008, 2012):  # Start with years we know have TV data
        print(f"\n📅 Processing {year}...")
        
        pdf_path = data_dir / f"{year}-state.pdf"
        if year == 2010:
            pdf_path = data_dir / "2010-state-championships.pdf"
        
        if not pdf_path.exists():
            print(f"  PDF not found: {pdf_path}")
            continue
        
        text = extract_text_from_pdf(pdf_path)
        if not text:
            continue
        
        # Count mentions
        tv_count = text.lower().count('tanque verde')
        print(f"  Found {tv_count} Tanque Verde mentions")
        
        results = parse_tanque_verde_results(text, year)
        print(f"  Parsed {len(results)} results")
        
        for r in results[:5]:  # Show first 5
            print(f"    - {r.event}: {r.swimmer_name} ({r.grade}) - {r.time}")
        
        if len(results) > 5:
            print(f"    ... and {len(results) - 5} more")
        
        all_results.extend(results)
    
    print("\n" + "=" * 70)
    print(f"TOTAL: {len(all_results)} results extracted")
    print("=" * 70)
    
    # Group by gender and event
    boys = [r for r in all_results if r.gender == 'M']
    girls = [r for r in all_results if r.gender == 'F']
    
    print(f"\nBoys: {len(boys)} results")
    print(f"Girls: {len(girls)} results")


if __name__ == "__main__":
    main()

