#!/usr/bin/env python3
"""
Automated Season Update Workflow
=================================
Run this script at the end of each season to:
1. Harvest all data (MaxPreps, AIA State)
2. Generate all records
3. Analyze records broken, state meet performance, senior highlights
4. Update annual summary with formatted content
5. Regenerate website

Usage:
    python run_season_update.py --season 2025-26 --state-pdf path/to/state.pdf
    
For next year:
    python run_season_update.py --season 2026-27 --state-pdf ~/Downloads/d3-state-2026.pdf
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*70}")
    print(f"🔄 {description}")
    print(f"{'='*70}")
    print(f"Running: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    
    print(result.stdout)
    print(f"✅ {description} - COMPLETE")
    return True

def main():
    parser = argparse.ArgumentParser(description='Automated season update workflow')
    parser.add_argument('--season', required=True, help='Season in YY-YY format (e.g., 25-26)')
    parser.add_argument('--state-pdf', required=True, help='Path to AIA State Championship PDF')
    parser.add_argument('--senior-class', help='Graduation year for senior highlights (e.g., 2026)')
    
    args = parser.parse_args()
    
    season = args.season
    year = int("20" + season.split('-')[0])  # e.g., "25-26" -> 2025
    
    print(f"""
{'='*70}
🏊 TANQUE VERDE SWIMMING - AUTOMATED SEASON UPDATE
{'='*70}
Season: {season}
Year: {year}
State PDF: {args.state_pdf}
Senior Class: {args.senior_class or 'Not specified'}
{'='*70}
    """)
    
    # Step 1: Update roster and harvest MaxPreps data
    if not run_command(
        f'cd /Users/aaryn/swimming/teams/tanque-verde && '
        f'swim-data-tool roster --seasons={season}',
        f"Step 1: Generate roster for {season} season"
    ):
        sys.exit(1)
    
    if not run_command(
        f'cd /Users/aaryn/swimming/teams/tanque-verde && '
        f'swim-data-tool import swimmers --source=maxpreps',
        f"Step 2: Import swimmer data from MaxPreps"
    ):
        sys.exit(1)
    
    # Step 2: Process State Championship PDF
    state_pdf = Path(args.state_pdf).expanduser()
    if not state_pdf.exists():
        print(f"❌ State PDF not found: {state_pdf}")
        sys.exit(1)
    
    target_pdf = Path("data/raw/aia-state/aia-state-{year}.pdf")
    if not run_command(
        f'cp "{state_pdf}" {target_pdf}',
        f"Step 3: Copy State Championship PDF"
    ):
        sys.exit(1)
    
    # Update parse_aia_state_meets.py to include new year
    if not run_command(
        f'python update_state_parser.py --year {year}',
        f"Step 4: Update AIA State parser for {year}"
    ):
        sys.exit(1)
    
    if not run_command(
        'python parse_aia_state_meets.py',
        f"Step 5: Parse AIA State Championship results"
    ):
        sys.exit(1)
    
    if not run_command(
        'python merge_aia_state_data.py',
        f"Step 6: Merge state data into swimmer files"
    ):
        sys.exit(1)
    
    # Step 3: Generate all records
    if not run_command(
        'python generate_hs_records.py',
        f"Step 7: Generate individual records"
    ):
        sys.exit(1)
    
    if not run_command(
        'python generate_relay_records.py',
        f"Step 8: Generate relay records"
    ):
        sys.exit(1)
    
    if not run_command(
        'python generate_all_season_top10.py',
        f"Step 9: Generate all season top 10 lists"
    ):
        sys.exit(1)
    
    # Step 4: Analyze season highlights
    if not run_command(
        f'python analyze_season.py --season {season} --year {year}',
        f"Step 10: Analyze season for records broken and highlights"
    ):
        sys.exit(1)
    
    if not run_command(
        f'python analyze_state_meet.py --year {year}',
        f"Step 11: Analyze state meet performance"
    ):
        sys.exit(1)
    
    # Step 5: Generate formatted annual summary
    if not run_command(
        f'python generate_annual_summary.py --season {season} --formatted',
        f"Step 12: Generate formatted annual summary"
    ):
        sys.exit(1)
    
    # Step 6: Generate senior highlights if specified
    if args.senior_class:
        if not run_command(
            f'python analyze_seniors.py --class-year {args.senior_class}',
            f"Step 13: Generate senior class highlights"
        ):
            sys.exit(1)
    
    # Step 7: Regenerate website
    if not run_command(
        'python generate_website.py',
        f"Step 14: Regenerate website"
    ):
        sys.exit(1)
    
    print(f"""
{'='*70}
✅ SEASON UPDATE COMPLETE!
{'='*70}

Next steps:
1. Review the generated content in:
   - data/records/annual-summary-{season}.md
   - docs/index.html (landing page)

2. Commit and push to GitHub:
   git add -A
   git commit -m "Season {season} update - records, highlights, and website"
   git push origin main

3. GitHub Pages will automatically rebuild in 1-3 minutes

{'='*70}
    """)

if __name__ == "__main__":
    main()

