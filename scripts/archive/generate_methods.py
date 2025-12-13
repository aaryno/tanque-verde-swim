#!/usr/bin/env python3
"""
Generate Methods/About section for published records.

Explains data sources, processing methodology, and compilation process.
"""

import json
from pathlib import Path
from datetime import datetime
import pandas as pd


def count_data_sources(swimmers_dir: Path) -> dict:
    """Count swims by data source"""
    source_counts = {}
    total_swims = 0
    
    for csv_file in swimmers_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            if 'source' in df.columns:
                counts = df['source'].value_counts().to_dict()
                for source, count in counts.items():
                    source_counts[source] = source_counts.get(source, 0) + count
                total_swims += len(df)
        except:
            continue
    
    return source_counts, total_swims


def load_aliases(aliases_file: Path) -> dict:
    """Load swimmer aliases"""
    if aliases_file.exists():
        with open(aliases_file, 'r') as f:
            return json.load(f)
    return {}


def generate_methods_markdown(output_path: Path, data_dir: Path):
    """Generate comprehensive methods section"""
    
    swimmers_dir = data_dir / "raw" / "swimmers"
    aliases_file = data_dir / "swimmer_aliases.json"
    
    # Get statistics
    source_counts, total_swims = count_data_sources(swimmers_dir)
    aliases = load_aliases(aliases_file)
    
    # Count unique aliases (not self-references)
    unique_aliases = sum(1 for k, v in aliases.items() if k != v)
    consolidated_swimmers = len(set(aliases.values()))
    
    lines = [
        "# Methods & Data Sources",
        "",
        "**Last Updated:** " + datetime.now().strftime("%B %d, %Y"),
        "",
        "---",
        "",
        "## Overview",
        "",
        "This document describes the methodology used to compile Tanque Verde High School swimming records, including data sources, collection methods, processing techniques, and quality control procedures.",
        "",
        "---",
        "",
        "## Data Sources",
        "",
        "### Primary Sources",
        "",
        "#### 1. MaxPreps (maxpreps.com)",
    ]
    
    lines.extend([
        "- **Type:** Web scraping of athlete profile pages",
        "- **Coverage:** Current and recent seasons (2023-present)",
        "- **Data Collected:**",
        "  - Swimmer names and demographics",
        "  - Event times and meet names",
        "  - Season information",
        "  - Grade levels (current)",
        "- **Access Method:** Playwright-based web scraper",
        "- **URL Pattern:** `https://www.maxpreps.com/az/tucson/tanque-verde-hawks/athletes/{name}/swimming/stats/`",
        "",
        "#### 2. Arizona Interscholastic Association (AIA) State Championships",
        "- **Type:** PDF parsing of official results",
        "- **Coverage:** 24 years (2001-2024)",
        "- **Data Collected:**",
        "  - State championship results",
        "  - Swimmer names, grades, and schools",
        "  - Final and preliminary times",
        "  - Split times (where available)",
        "  - Place finishes",
        "- **Access Method:** PDF extraction using pdfplumber",
        "- **Source:** https://aiaonline.org",
        "- **Files:** 24 PDFs containing all Division I-III state championship results",
        "",
        f"### Data Volume",
        "",
        f"- **Total Swims:** {total_swims:,}",
        f"- **Total Swimmers:** {len(list(swimmers_dir.glob('*.csv')))}",
        "",
        "**Swims by Source:**",
    ])
    
    for source, count in sorted(source_counts.items()):
        source_label = {
            'maxpreps': 'MaxPreps',
            'aia_pdf': 'AIA State Meet PDFs',
            'manual': 'Manual Entry'
        }.get(source, source)
        lines.append(f"- {source_label}: {count:,} swims ({count/total_swims*100:.1f}%)")
    
    lines.extend([
        "",
        "---",
        "",
        "## Data Processing Methodology",
        "",
        "### 1. Data Collection",
        "",
        "#### MaxPreps Import Process",
        "```bash",
        "swim-data-tool import swimmers --file=data/lookups/roster-maxpreps.csv",
        "```",
        "",
        "- Reads roster CSV with MaxPreps athlete URLs",
        "- For each athlete:",
        "  1. Navigates to swimming stats page",
        "  2. Identifies correct sport-specific URL (boys vs girls paths differ)",
        "  3. Parses season sections (Freshman, Sophomore, Junior, Senior)",
        "  4. Extracts times, meets, and dates from each season",
        "  5. Saves to individual CSV file per athlete",
        "",
        "#### AIA State Meet Processing",
        "```bash",
        "python3 parse_aia_state_meets.py",
        "```",
        "",
        "- Downloads all 24 years of state championship PDFs",
        "- For each PDF:",
        "  1. Extracts text using pdfplumber",
        "  2. Identifies event headers (200 Free, 100 Back, etc.)",
        "  3. Parses result lines with regex patterns",
        "  4. Matches school name (\"Tanque Verde\")",
        "  5. Extracts swimmer name, grade, times, splits",
        "  6. Normalizes event names to standard format",
        "",
        "### 2. Grade Assignment",
        "",
        "**Challenge:** MaxPreps initially showed all swims with athlete's current grade, not grade at time of swim.",
        "",
        "**Solution:**",
        "1. **Season-based Detection:** Parse HTML to identify season sections (e.g., \"Freshman\", \"Sophomore\")",
        "2. **Grade Inference:** Assign grade based on which season section the swim appears in",
        "3. **Date Validation:** Cross-reference swim dates with academic years",
        "4. **AIA Override:** AIA PDFs explicitly list grade at time of competition (definitive source)",
        "",
        "**Grade Calculation Logic:**",
        "```python",
        "# For each season section on MaxPreps:",
        "if \"Freshman\" in section_header:",
        "    grade = 9",
        "elif \"Sophomore\" in section_header:",
        "    grade = 10",
        "# ... etc",
        "",
        "# For graduated swimmers:",
        "# Work backward from most recent known season",
        "if most_recent_season == \"Senior\" and year == 2023:",
        "    # Previous year swims would be Junior (grade 11)",
        "    # Two years prior would be Sophomore (grade 10)",
        "```",
        "",
        "### 3. Name Consolidation & Aliases",
        "",
        f"**Duplicates Detected:** {unique_aliases} name variations",
        f"**Swimmers Consolidated:** {consolidated_swimmers}",
        "",
        "**Problem:** Swimmers appear with different name variations across data sources:",
        "- MaxPreps may use \"Nicholas\" while AIA uses \"Nick\"",
        "- Different sources may use full names vs nicknames",
        "- Historical vs current name preferences",
        "",
        "**Detection Method:**",
        "```bash",
        "python3 detect_name_duplicates.py",
        "```",
        "",
        "1. **Last Name Matching:** Group swimmers by last name",
        "2. **Nickname Recognition:** Built-in mapping of common variations:",
        "   - Nicholas/Nick/Nicolas",
        "   - Samuel/Sam/Sammy",
        "   - Zachary/Zach/Zack",
        "   - 15+ additional patterns",
        "3. **Grade Overlap:** Check if grade ranges overlap (same swimmer should have sequential grades)",
        "4. **Gender Consistency:** Ensure matched swimmers have same gender",
        "",
        "**Consolidation Process:**",
        "```bash",
        "python3 consolidate_swimmers.py",
        "```",
        "",
        "1. **Interactive Confirmation:** User confirms each potential duplicate",
        "2. **Name Selection:** User chooses preferred display name",
        "3. **File Merging:** Combine all swims into single CSV",
        "4. **Deduplication:** Remove exact duplicate swims (same event, date, time)",
        "5. **Alias Recording:** Store mapping in `swimmer_aliases.json`",
        "",
        "**Example Aliases:**",
        "```json",
        "{",
    ]
    
    # Add first 3 aliases as examples
    for i, (original, preferred) in enumerate(list(aliases.items())[:3]):
        comma = "," if i < 2 else ""
        lines.append(f'  "{original}": "{preferred}"{comma}')
    
    lines.extend([
        "}",
        "```",
        "",
        "**Auto-Application:** Future data imports automatically apply aliases.",
        "",
        "### 4. Event Normalization",
        "",
        "**Challenge:** Different sources use different event naming conventions.",
        "",
        "**Standardization:**",
        "- MaxPreps: \"100 Breast\" → \"100 BR SCY\"",
        "- AIA: \"100 Yard Breaststroke\" → \"100 BR SCY\"",
        "- Output: Canonical format for consistent records",
        "",
        "**Event Codes:**",
        "```",
        "50 FR SCY    - 50 Freestyle",
        "100 FR SCY   - 100 Freestyle",
        "200 FR SCY   - 200 Freestyle",
        "500 FR SCY   - 500 Freestyle",
        "100 BK SCY   - 100 Backstroke",
        "100 BR SCY   - 100 Breaststroke",
        "100 FL SCY   - 100 Butterfly",
        "200 IM SCY   - 200 Individual Medley",
        "```",
        "",
        "### 5. Duplicate Removal",
        "",
        "**Strategy:** Keep best time per swimmer per event per competition",
        "",
        "- Same event, date, and time → Remove duplicate",
        "- Prelims vs Finals → Keep both (marked by round)",
        "- Different meets on same date → Keep both",
        "",
        "### 6. Record Generation",
        "",
        "```bash",
        "python3 generate_hs_records.py",
        "```",
        "",
        "**High School Records Format:**",
        "- **Grade-Based Categories:** Freshman, Sophomore, Junior, Senior, Open",
        "- **8 Standard Events:** 50/100/200/500 Free, 100 Back/Breast/Fly, 200 IM",
        "- **Open Category:** Best time across all grade levels (displayed in bold)",
        "",
        "**Record Selection Logic:**",
        "1. Load all swimmer data",
        "2. Filter for Tanque Verde swimmers",
        "3. Normalize events to SCY format",
        "4. Group by event and grade level",
        "5. Select fastest time per swimmer (avoid same swimmer with multiple entries)",
        "6. Display best overall time per grade category",
        "",
        "---",
        "",
        "## Quality Control",
        "",
        "### Data Validation",
        "1. **Time Format Validation:** All times in MM:SS.SS or SS.SS format",
        "2. **Date Validation:** Dates in YYYY-MM-DD or MM/DD/YYYY format",
        "3. **Grade Range Check:** Grades 9-12 only (high school)",
        "4. **Course Consistency:** All records are SCY (short course yards)",
        "",
        "### Manual Verification",
        "- Cross-reference MaxPreps and AIA data where overlap exists",
        "- Verify state championship times against official PDFs",
        "- Confirm swimmer identities during alias consolidation",
        "",
        "### Known Limitations",
        "1. **MaxPreps Coverage:** Not all meets upload results to MaxPreps",
        "2. **State Meet Only:** AIA PDFs only include state championship qualifiers",
        "3. **Historical Gaps:** Limited data before 2015 for non-state meets",
        "4. **Relay Times:** Currently excluded from individual records",
        "",
        "---",
        "",
        "## Technical Implementation",
        "",
        "### Tools & Libraries",
        "- **Python 3.11+**",
        "- **Playwright:** Browser automation for MaxPreps scraping",
        "- **pdfplumber:** PDF text extraction for AIA results",
        "- **pandas:** Data manipulation and analysis",
        "- **swim-data-tool:** Custom CLI tool for swim data management",
        "",
        "### Data Storage",
        "```",
        "data/",
        "├── raw/",
        "│   ├── swimmers/              # Individual CSV per swimmer",
        "│   └── aia-state/            # AIA PDFs and extracted CSVs",
        "├── records/                  # Generated markdown records",
        "└── swimmer_aliases.json      # Name consolidation mapping",
        "```",
        "",
        "### Automation",
        "All processing steps are scripted and reproducible:",
        "```bash",
        "# Complete workflow",
        "swim-data-tool import swimmers",
        "python3 parse_aia_state_meets.py",
        "python3 detect_name_duplicates.py",
        "python3 consolidate_swimmers.py",
        "python3 merge_aia_state_data.py",
        "python3 generate_hs_records.py",
        "python3 generate_methods.py",
        "swim-data-tool publish",
        "```",
        "",
        "---",
        "",
        "## Updates & Maintenance",
        "",
        "### Regular Updates (After Each Meet)",
        "1. Re-import MaxPreps data",
        "2. Check for new duplicates",
        "3. Regenerate records",
        "4. Publish to GitHub",
        "",
        "### Annual Updates (After State Meet)",
        "1. Download new state championship PDF",
        "2. Re-run AIA parser",
        "3. Merge new state data",
        "4. Update methods documentation",
        "",
        "---",
        "",
        "## Contact & Issues",
        "",
        "For questions about methodology or data accuracy:",
        "- Review source code: Scripts are documented and available in repository",
        "- Check raw data: Individual swimmer CSVs contain source attribution",
        "- Report issues: Contact team administrator",
        "",
        "---",
        "",
        f"*Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*",
        "",
    ])
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Generated: {output_path}")


def main():
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    output_path = data_dir / "records" / "METHODS.md"
    
    print("\n📝 Generating Methods Documentation\n")
    
    generate_methods_markdown(output_path, data_dir)
    
    print("\n✓ Methods documentation complete!\n")


if __name__ == "__main__":
    main()

