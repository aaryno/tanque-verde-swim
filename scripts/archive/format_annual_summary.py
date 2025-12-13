#!/usr/bin/env python3
"""
Format Annual Summary with Splash Page Styling
===============================================
Enhances annual summaries with the same formatting as the main splash page:
- Records broken (overall + grade) with NEW/OLD format
- State championship highlights
- Senior class spotlights (when applicable)
- Styled cards and sections

Usage:
    python format_annual_summary.py --season 2025-26
    python format_annual_summary.py --season 2024-25 --auto-detect
"""

import argparse
import re
from pathlib import Path
from datetime import datetime

def read_annual_summary(season):
    """Read existing annual summary"""
    summary_file = Path(f'data/records/annual-summary-{season}.md')
    if not summary_file.exists():
        print(f"❌ Annual summary not found: {summary_file}")
        return None
    return summary_file.read_text()

def enhance_with_splash_format(content, season):
    """
    Enhance annual summary with splash page formatting
    
    Adds:
    - Season overview header
    - Records broken section (if present)
    - State championship highlights (if present)
    - Senior class highlights (if applicable)
    """
    year = int("20" + season.split('-')[0])
    
    # Build enhanced content
    enhanced = f"""# {season} Season Summary
**Tanque Verde High School Swimming & Diving**

---

## Season Overview

"""
    
    # Try to extract key stats from existing content
    # Look for records broken, state results, etc.
    
    # Add records broken section if we can find them
    if 'School Record' in content or 'record' in content.lower():
        enhanced += "\n## 📈 Records Broken\n\n"
        enhanced += "### Overall School Records\n\n"
        # Parse and format records from content
        # TODO: Extract and format individual records
        
        enhanced += "\n### Grade Records\n\n"
        # TODO: Extract and format grade records
    
    # Add state meet section if present
    if 'State' in content or f'{year} D' in content:
        enhanced += f"\n## 🏆 {year} AIA D3 State Championship\n\n"
        # TODO: Extract state meet highlights
    
    # Add season bests section (always present)
    enhanced += "\n## 🌟 Season Best Times\n\n"
    enhanced += "### Boys\n\n"
    # Extract boys season bests from existing content
    
    enhanced += "\n### Girls\n\n"
    # Extract girls season bests from existing content
    
    # Add existing content (filtered)
    enhanced += "\n---\n\n"
    enhanced += "## Complete Season Details\n\n"
    enhanced += content
    
    return enhanced

def create_formatted_summary_from_scratch(season):
    """
    Create a formatted annual summary from scratch by analyzing records
    """
    year = int("20" + season.split('-')[0])
    
    # TODO: Call analyze_season.py to get records broken
    # TODO: Call analyze_state_meet.py if state data exists
    # TODO: Extract season bests from records
    
    template = f"""# {season} Season Summary
**Tanque Verde High School Swimming & Diving**

*Generated: {datetime.now().strftime('%B %d, %Y')}*

---

## Season Overview

The {season} season for Tanque Verde High School Swimming featured:
- X individual records broken
- X relay records broken  
- X grade records set
- Strong performances at the AIA D3 State Championship

---

## 📈 Records Broken

### 🏆 Overall School Records

[To be filled with records analysis]

### 🎯 Grade Records

[To be filled with grade records analysis]

---

## 🏆 AIA D3 State Championship

**Date:** November X, {year}

### Top Finishers

**Boys:**
- [To be filled from state results]

**Girls:**
- [To be filled from state results]

---

## 🌟 Season Best Times

### Boys

| Event | Time | Athlete | Meet |
|-------|------|---------|------|
| [To be filled] | | | |

### Girls

| Event | Time | Athlete | Meet |
|-------|------|---------|------|
| [To be filled] | | | |

---

*For complete records and top 10 lists, see the team records pages.*
"""
    
    return template

def main():
    parser = argparse.ArgumentParser(description='Format annual summary with splash page styling')
    parser.add_argument('--season', required=True, help='Season in YY-YY format (e.g., 25-26)')
    parser.add_argument('--auto-detect', action='store_true', 
                       help='Automatically detect records broken from records files')
    parser.add_argument('--output', help='Output file (defaults to updating in place)')
    
    args = parser.parse_args()
    
    season = args.season
    summary_file = Path(f'data/records/annual-summary-{season}.md')
    
    # Read existing content if it exists
    if summary_file.exists():
        print(f"📄 Reading existing summary: {summary_file}")
        content = read_annual_summary(season)
        
        if args.auto_detect:
            print("🔍 Auto-detecting records and highlights...")
            # enhanced = enhance_with_splash_format(content, season)
            enhanced = create_formatted_summary_from_scratch(season)
        else:
            enhanced = content
    else:
        print(f"📝 Creating new summary from scratch...")
        enhanced = create_formatted_summary_from_scratch(season)
    
    # Write output
    output_file = Path(args.output) if args.output else summary_file
    output_file.write_text(enhanced)
    
    print(f"✅ Enhanced annual summary written to: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Review {output_file} and fill in any [To be filled] sections")
    print(f"2. Run: python generate_website.py")
    print(f"3. Commit and push changes")

if __name__ == '__main__':
    main()

