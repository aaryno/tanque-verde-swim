#!/usr/bin/env python3
"""
Import historical state championship data (2007-2011) from AZPreps365 PDFs.

Downloads PDFs, extracts Tanque Verde results, and creates season files.
"""

import subprocess
import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import urllib.request


@dataclass
class SwimResult:
    """A single swim result."""
    event: str
    swimmer_name: str
    grade: str  # FR, SO, JR, SR, or empty
    time: str
    year: int
    gender: str  # M or F
    meet: str = ""
    
    def to_markdown_row(self, rank: int) -> str:
        grade = self.grade if self.grade else ""
        return f"| {rank} | {self.time} | {self.swimmer_name} | {grade} | Nov {self.year} | {self.meet} |"


# AZPreps365 archive meet IDs
MEET_IDS = {
    2007: 7844,
    2008: 9361,
    2009: 10504,
    2010: 11757,
    2011: 12611,
}

# Event name mappings
EVENT_NAMES = {
    "50 Yard Freestyle": "50 Freestyle",
    "100 Yard Freestyle": "100 Freestyle",
    "200 Yard Freestyle": "200 Freestyle",
    "500 Yard Freestyle": "500 Freestyle",
    "100 Yard Backstroke": "100 Backstroke",
    "100 Yard Breaststroke": "100 Breaststroke",
    "100 Yard Butterfly": "100 Butterfly",
    "200 Yard IM": "200 Individual Medley",
    "200 Yard Individual Medley": "200 Individual Medley",
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
    
    # Build URL based on year patterns
    if year <= 2006:
        suffix = "4a-5a-state-championships"
    elif year <= 2009:
        suffix = "1a-5a-state-championships"
    else:
        suffix = "divisions-i-ii-state-championships"
    
    url = f"https://aiaonline.org/files/{meet_id}/{year}-swimming-and-diving-{suffix}.pdf"
    
    print(f"  Downloading {year} from {url}")
    try:
        urllib.request.urlretrieve(url, output_path)
        return output_path
    except Exception as e:
        print(f"  Failed to download {year}: {e}")
        return None


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
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
    
    # Patterns
    event_pattern = re.compile(r'Event\s+\d+\s+(Boys|Girls)\s+(.+)', re.IGNORECASE)
    
    # Pattern for individual result lines:
    # "22  Matsunaga, Kurt                      SO Tanque Verde High School             2:48.05          2:31.75"
    # Name pattern: "Last, First" followed by grade and school
    result_pattern = re.compile(
        r'([A-Z][a-z]+(?:-[A-Z][a-z]+)?),\s*([A-Z][a-z]+)\s+'
        r'(FR|SO|JR|SR)\s+Tanque Verde'
    )
    
    # Time pattern - capture all times on a line
    time_pattern = re.compile(r'\b(\d{1,2}:\d{2}\.\d{2}|\d{2}\.\d{2})\b')
    
    # Process line by line
    for i, line in enumerate(lines):
        # Track current event
        event_match = event_pattern.search(line)
        if event_match:
            current_gender = 'M' if event_match.group(1).lower() == 'boys' else 'F'
            raw_event = event_match.group(2).strip()
            # Normalize event name
            current_event = EVENT_NAMES.get(raw_event, raw_event)
            # Skip relay events
            if 'relay' in current_event.lower():
                current_event = None
            continue
        
        # Skip if no current event or relay event
        if not current_event:
            continue
        
        # Look for Tanque Verde individual results
        if 'Tanque Verde' in line:
            result_match = result_pattern.search(line)
            if result_match:
                last_name = result_match.group(1)
                first_name = result_match.group(2)
                grade = result_match.group(3)
                swimmer_name = f"{first_name} {last_name}"
                
                # Find times on this line
                times = time_pattern.findall(line)
                if times:
                    # Use the last time (usually final time) or first if only one
                    time_str = times[-1] if len(times) > 1 else times[0]
                    
                    # Skip disqualified or scratch
                    if 'DQ' in line or 'DFS' in line or 'NS' in line:
                        continue
                    
                    # Determine meet name based on year
                    if year <= 2009:
                        meet = f"{year} AIA 1A-5A State Championships"
                    else:
                        meet = f"{year} AIA Division I-II State Championships"
                    
                    results.append(SwimResult(
                        event=current_event,
                        swimmer_name=swimmer_name,
                        grade=grade,
                        time=time_str,
                        year=year,
                        gender=current_gender,
                        meet=meet
                    ))
    
    # Remove duplicates (keep best time per swimmer per event)
    unique_results = {}
    for r in results:
        key = (r.event, r.swimmer_name, r.gender)
        if key not in unique_results or parse_time(r.time) < parse_time(unique_results[key].time):
            unique_results[key] = r
    
    return list(unique_results.values())


def generate_season_file(results: list[SwimResult], year: int, gender: str, output_dir: Path):
    """Generate a season top10 file from results."""
    gender_label = "Boys" if gender == "M" else "Girls"
    gender_file = "boys" if gender == "M" else "girls"
    
    # Convert year to season format (e.g., 2007 -> 2007-08)
    season = f"{year}-{str(year+1)[-2:]}"
    
    # Group by event
    events = {}
    for r in results:
        if r.event not in events:
            events[r.event] = []
        events[r.event].append(r)
    
    # Sort each event by time
    for event in events:
        events[event].sort(key=lambda r: parse_time(r.time))
    
    # Generate markdown
    lines = [
        f"# {gender_label} Top 10 - {season} Season",
        "## Tanque Verde High School Swimming",
        "",
        f"**Source:** AIA State Championships Only",
        f"**Note:** Invitational meet data not available for this season.",
        "",
        "---",
        ""
    ]
    
    # Standard event order
    event_order = [
        "50 Freestyle", "100 Freestyle", "200 Freestyle", "500 Freestyle",
        "100 Backstroke", "100 Breaststroke", "100 Butterfly", "200 Individual Medley"
    ]
    
    for event in event_order:
        lines.append(f"## {event}")
        lines.append("")
        lines.append("| Rank | Time | Athlete | Year | Date | Meet |")
        lines.append("|-----:|-----:|---------|------|------|------|")
        
        if event in events:
            for rank, result in enumerate(events[event][:10], 1):
                lines.append(result.to_markdown_row(rank))
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Write file
    output_path = output_dir / f"top10-{gender_file}-{season}.md"
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"  ✓ Generated: {output_path.name}")


def parse_time(time_str: str) -> float:
    """Parse swim time to seconds for sorting."""
    if ':' in time_str:
        parts = time_str.split(':')
        return float(parts[0]) * 60 + float(parts[1])
    return float(time_str)


def main():
    base_dir = Path(__file__).parent
    data_dir = base_dir / "historical_data"
    records_dir = base_dir / "records"
    
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("IMPORTING HISTORICAL STATE CHAMPIONSHIP DATA (2007-2011)")
    print("=" * 70)
    
    all_results = []
    
    for year in range(2007, 2012):
        print(f"\n📅 Processing {year}...")
        
        # Download PDF if needed
        pdf_path = download_pdf(year, data_dir)
        if not pdf_path or not pdf_path.exists():
            print(f"  Skipping {year} - PDF not available")
            continue
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print(f"  Skipping {year} - could not extract text")
            continue
        
        # Count mentions
        tv_count = text.lower().count('tanque verde')
        print(f"  Found {tv_count} Tanque Verde mentions")
        
        # Parse results
        results = parse_tanque_verde_results(text, year)
        print(f"  Parsed {len(results)} individual results")
        
        # Show sample
        for r in results[:3]:
            print(f"    - {r.event}: {r.swimmer_name} ({r.grade}) - {r.time}")
        if len(results) > 3:
            print(f"    ... and {len(results) - 3} more")
        
        all_results.extend(results)
        
        # Generate season files
        boys = [r for r in results if r.gender == 'M']
        girls = [r for r in results if r.gender == 'F']
        
        if boys:
            generate_season_file(boys, year, 'M', records_dir)
        if girls:
            generate_season_file(girls, year, 'F', records_dir)
    
    print("\n" + "=" * 70)
    print(f"TOTAL: {len(all_results)} results imported")
    print("=" * 70)
    
    # Summary by gender
    boys = [r for r in all_results if r.gender == 'M']
    girls = [r for r in all_results if r.gender == 'F']
    
    print(f"\nBoys: {len(boys)} results")
    print(f"Girls: {len(girls)} results")
    
    # Clean up PDFs to keep repo clean
    print("\n🧹 Cleaning up PDFs...")
    for pdf in data_dir.glob("*.pdf"):
        pdf.unlink()
    if data_dir.exists() and not any(data_dir.iterdir()):
        data_dir.rmdir()
    
    print("\n✅ Import complete! Run build_alltime_top10.py to update all-time records.")


if __name__ == "__main__":
    main()

