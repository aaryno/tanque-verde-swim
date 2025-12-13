#!/usr/bin/env python3
"""
Complete Division Harvest - Leaderboards + All Team Relays

Harvests:
1. Top N swimmers from D3 boys/girls leaderboards (default: 50)
2. Extracts all unique schools from leaderboards
3. Visits each school's MaxPreps page and harvests relay results

This provides complete division data for lineup optimization and competitive analysis.

Usage:
    python3 harvest_division_complete.py
    python3 harvest_division_complete.py --output-dir=data/raw/d3_complete --top-n=100
    python3 harvest_division_complete.py --division=d3 --top-n=50 --cutoff-date=2024-09-01
"""

import sys
import argparse
import re
from pathlib import Path
from datetime import datetime, date
from typing import Optional
import pandas as pd
from bs4 import BeautifulSoup
import time

# Add swim-data-tool to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'swim-data-tool' / 'src'))


class DivisionHarvester:
    """Complete division data harvester."""
    
    BASE_URL = "https://azpreps365.com"
    MAXPREPS_URL = "https://www.maxpreps.com"
    
    def __init__(self, output_dir: Path, division: str = "d3", top_n: int = 50):
        """Initialize harvester."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.division = division
        self.top_n = top_n
        self._playwright = None
        self._browser = None
        
    def _ensure_playwright(self):
        """Ensure Playwright is initialized."""
        if self._playwright is None:
            try:
                from playwright.sync_api import sync_playwright
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.launch(headless=True)
            except ImportError:
                print("❌ Playwright not installed. Install with: pip install playwright && playwright install")
                sys.exit(1)
    
    def _close_playwright(self):
        """Close Playwright resources."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
    
    def harvest_leaderboard(self, gender: str) -> pd.DataFrame:
        """
        Harvest top N from division leaderboard.
        
        Args:
            gender: "boys" or "girls"
            
        Returns:
            DataFrame with leaderboard data
        """
        self._ensure_playwright()
        
        url = f"{self.BASE_URL}/leaderboards/swimming-{gender}/{self.division}"
        print(f"\n🎭 Harvesting {gender.title()} {self.division.upper()} leaderboard (top {self.top_n})...")
        print(f"   URL: {url}")
        
        all_data = []
        page = self._browser.new_page()
        
        try:
            # Navigate to page (don't wait for networkidle - it times out)
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)  # Wait for JavaScript to load
            print("   ✓ Page loaded")
            
            # Define events to scrape (value format for select)
            events = [
                ("freeindividual50", "50 Free"),
                ("freeindividual100", "100 Free"),
                ("freeindividual200", "200 Free"),
                ("freeindividual500", "500 Free"),
                ("backindividual100", "100 Back"),
                ("breastindividual100", "100 Breast"),
                ("flyindividual100", "100 Fly"),
                ("medleyindividual200", "200 IM"),
                ("medleyrelay200", "200 Medley Relay"),
                ("freerelay200", "200 Free Relay"),
                ("freerelay400", "400 Free Relay")
            ]
            
            for event_value, event_name in events:
                print(f"   📊 Scraping {event_name} (top {self.top_n})...")
                
                try:
                    # Select event from dropdown (using name="category")
                    page.select_option('select[name="category"]', value=event_value)
                    time.sleep(1)
                    
                    # Click "Load Leaderboard" button
                    page.click('button:has-text("Load Leaderboard")')
                    
                    # Wait for results to load (wait for at least one result row)
                    try:
                        page.wait_for_selector('div.box.leaderboard-top-ten div.columns.is-mobile', timeout=10000)
                    except:
                        # No results for this event
                        pass
                    
                    time.sleep(2)  # Extra wait for all results to load
                    
                    # Extract results from leaderboard boxes
                    result_rows = page.query_selector_all('div.box.leaderboard-top-ten div.columns.is-mobile')
                    
                    for i, row in enumerate(result_rows[:self.top_n], 1):
                        try:
                            # Athlete name and school are in column is-9
                            name_col = row.query_selector('div.column.is-9.leaderboard-name.athlete')
                            if not name_col:
                                continue
                            
                            # Extract athlete name (in <a> tag)
                            name_link = name_col.query_selector('a.name')
                            if name_link:
                                athlete = name_link.inner_text().strip().replace('\n', ' ').replace('  ', ' ')
                            else:
                                continue
                            
                            # Extract school (in <span class="team">)
                            school_span = name_col.query_selector('span.team')
                            if school_span:
                                school = school_span.inner_text().strip()
                            else:
                                school = "Unknown"
                            
                            # Time is in column is-3
                            time_col = row.query_selector('div.column.is-3.leaderboard-value')
                            if time_col:
                                time_str = time_col.inner_text().strip()
                            else:
                                continue
                            
                            all_data.append({
                                'event': event_name,
                                'athlete': athlete,
                                'school': school,
                                'time': time_str,
                                'rank': i,
                                'division': self.division,
                                'gender': gender,
                                'harvest_date': datetime.now().strftime("%Y-%m-%d")
                            })
                        except Exception as e:
                            # Skip rows that don't parse correctly
                            continue
                    
                    print(f"      ✓ Found {min(len(result_rows), self.top_n)} results")
                
                except Exception as e:
                    print(f"      ⚠️  Error scraping {event_name}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
        finally:
            page.close()
        
        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n✅ Successfully scraped {len(df)} total results")
            return df
        else:
            print(f"\n⚠️  No data scraped")
            return pd.DataFrame()
    
    def extract_schools(self, df: pd.DataFrame) -> list[str]:
        """
        Extract unique schools from leaderboard data.
        
        Args:
            df: Leaderboard DataFrame
            
        Returns:
            List of unique school names
        """
        if df.empty:
            return []
        
        schools = df['school'].unique().tolist()
        schools = [s for s in schools if s and s.strip()]
        schools.sort()
        
        print(f"\n📋 Found {len(schools)} unique schools in leaderboard:")
        for i, school in enumerate(schools, 1):
            print(f"   {i}. {school}")
        
        return schools
    
    def school_name_to_slug(self, school_name: str) -> str:
        """
        Convert school name to MaxPreps slug format.
        
        Args:
            school_name: School name (e.g., "Tanque Verde")
            
        Returns:
            Slug (e.g., "tanque-verde-hawks")
        """
        # Convert to lowercase, replace spaces with hyphens
        slug = school_name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/hyphens with single hyphen
        slug = slug.strip('-')
        
        # Note: This is a best guess. Real slugs often include mascot names
        # e.g., "Tanque Verde" -> "tanque-verde-hawks"
        # May need manual mapping for accuracy
        
        return slug
    
    def find_maxpreps_school_url(self, school_name: str, state: str = "az") -> Optional[str]:
        """
        Search MaxPreps for school URL.
        
        Args:
            school_name: School name
            state: State abbreviation
            
        Returns:
            MaxPreps school URL or None
        """
        self._ensure_playwright()
        
        # Try direct slug first
        slug = self.school_name_to_slug(school_name)
        
        # Common Arizona high school mascots
        mascots = ["hawks", "wildcats", "eagles", "falcons", "panthers", "jaguars", 
                   "mustangs", "bulldogs", "cougars", "spartans", "warriors", "knights"]
        
        page = self._browser.new_page()
        
        try:
            for mascot in mascots:
                test_slug = f"{slug}-{mascot}"
                test_url = f"{self.MAXPREPS_URL}/high-schools/{test_slug}/swimming-winter-23-24/stats.htm"
                
                try:
                    response = page.goto(test_url, wait_until="domcontentloaded", timeout=10000)
                    if response and response.status == 200:
                        # Check if page contains school name
                        content = page.content()
                        if school_name.lower() in content.lower():
                            print(f"      ✓ Found: {test_url}")
                            page.close()
                            return test_url
                except:
                    continue
            
            print(f"      ⚠️  Could not find MaxPreps URL for {school_name}")
            page.close()
            return None
            
        except Exception as e:
            print(f"      ❌ Error searching for {school_name}: {e}")
            page.close()
            return None
    
    def harvest_school_relays(self, school_name: str, gender: str, 
                             cutoff_date: date, state: str = "az") -> pd.DataFrame:
        """
        Harvest relay results for a specific school.
        
        Args:
            school_name: School name
            gender: "boys" or "girls"
            cutoff_date: Only include relays from this date onwards
            state: State abbreviation
            
        Returns:
            DataFrame with relay results
        """
        print(f"\n   🏊 Harvesting {gender} relays for {school_name}...")
        
        # Find school URL
        school_url = self.find_maxpreps_school_url(school_name, state)
        if not school_url:
            return pd.DataFrame()
        
        # TODO: Implement relay scraping from MaxPreps school page
        # This would require:
        # 1. Navigate to school's swimming page
        # 2. Find meet results
        # 3. Extract relay times from each meet
        # 4. Filter by date
        
        # For now, return empty DataFrame
        # This is a placeholder for the full implementation
        print(f"      ⚠️  Relay scraping not yet implemented")
        return pd.DataFrame()
    
    def harvest_all_school_relays(self, schools: list[str], gender: str, 
                                  cutoff_date: date) -> pd.DataFrame:
        """
        Harvest relays for all schools.
        
        Args:
            schools: List of school names
            gender: "boys" or "girls"
            cutoff_date: Only include relays from this date onwards
            
        Returns:
            Combined DataFrame with all relay results
        """
        print(f"\n🏊 Harvesting {gender} relays for {len(schools)} schools...")
        
        all_relays = []
        
        for i, school in enumerate(schools, 1):
            print(f"\n[{i}/{len(schools)}] {school}")
            
            try:
                df = self.harvest_school_relays(school, gender, cutoff_date)
                if not df.empty:
                    all_relays.append(df)
                    print(f"      ✓ Found {len(df)} relay results")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue
        
        if all_relays:
            combined = pd.concat(all_relays, ignore_index=True)
            print(f"\n✅ Total relay results: {len(combined)}")
            return combined
        else:
            print(f"\n⚠️  No relay results found")
            return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, filename: str) -> Path:
        """Save DataFrame to CSV."""
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        print(f"\n💾 Saved to: {output_path}")
        return output_path


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Complete division harvest: leaderboards + all team relays',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: Top 50 from D3, relays from Oct 20+
  python3 harvest_division_complete.py
  
  # Top 100 from D3
  python3 harvest_division_complete.py --top-n=100
  
  # Custom output directory
  python3 harvest_division_complete.py --output-dir=data/raw/d3_complete_2024_10_26
  
  # Different cutoff date for relays
  python3 harvest_division_complete.py --cutoff-date=2024-09-01
  
  # Different division
  python3 harvest_division_complete.py --division=d2 --top-n=50
        """
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (default: data/raw/division_harvest/YYYY-MM-DD/)'
    )
    parser.add_argument(
        '--division',
        type=str,
        default='d3',
        choices=['d1', 'd2', 'd3', 'd4'],
        help='Division to harvest (default: d3)'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=50,
        help='Number of top swimmers per event (default: 50)'
    )
    parser.add_argument(
        '--cutoff-date',
        type=str,
        default='2024-10-20',
        help='Only include relays from this date onwards (format: YYYY-MM-DD)'
    )
    parser.add_argument(
        '--no-timestamp',
        action='store_true',
        help='Do not append timestamp to output directory'
    )
    parser.add_argument(
        '--leaderboard-only',
        action='store_true',
        help='Only harvest leaderboards, skip relay harvesting'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(f" Complete Division Harvest - {args.division.upper()}")
    print("="*70)
    
    # Determine output directory
    harvest_date = datetime.now().strftime("%Y-%m-%d")
    
    if args.output_dir:
        if args.no_timestamp:
            output_dir = Path(args.output_dir)
        else:
            output_dir = Path(args.output_dir) / harvest_date
    else:
        output_dir = Path("data/raw/division_harvest") / harvest_date
    
    print(f"\n📁 Output directory: {output_dir.absolute()}")
    print(f"🎯 Division: {args.division.upper()}")
    print(f"🔢 Top N per event: {args.top_n}")
    
    # Parse cutoff date
    try:
        cutoff_date = datetime.strptime(args.cutoff_date, '%Y-%m-%d').date()
        print(f"📅 Relay cutoff date: {cutoff_date}")
    except ValueError:
        print(f"❌ Invalid cutoff date format: {args.cutoff_date}")
        sys.exit(1)
    
    # Initialize harvester
    harvester = DivisionHarvester(output_dir, args.division, args.top_n)
    
    try:
        # Step 1: Harvest leaderboards
        print("\n" + "="*70)
        print(" Step 1: Harvesting Leaderboards")
        print("="*70)
        
        boys_leaderboard = harvester.harvest_leaderboard("boys")
        girls_leaderboard = harvester.harvest_leaderboard("girls")
        
        # Save leaderboards
        if not boys_leaderboard.empty:
            harvester.save_data(
                boys_leaderboard,
                f"{args.division}_boys_leaderboard_top{args.top_n}_{harvest_date}.csv"
            )
        
        if not girls_leaderboard.empty:
            harvester.save_data(
                girls_leaderboard,
                f"{args.division}_girls_leaderboard_top{args.top_n}_{harvest_date}.csv"
            )
        
        # Extract unique schools
        boys_schools = harvester.extract_schools(boys_leaderboard)
        girls_schools = harvester.extract_schools(girls_leaderboard)
        all_schools = sorted(set(boys_schools + girls_schools))
        
        print(f"\n📊 Total unique schools: {len(all_schools)}")
        
        # Save school list
        schools_df = pd.DataFrame({'school': all_schools})
        harvester.save_data(
            schools_df,
            f"{args.division}_schools_{harvest_date}.csv"
        )
        
        if args.leaderboard_only:
            print("\n⚠️  Skipping relay harvest (--leaderboard-only flag)")
        else:
            # Step 2: Harvest relays for all schools
            print("\n" + "="*70)
            print(" Step 2: Harvesting Relays for All Schools")
            print("="*70)
            print(f"\n⚠️  NOTE: Relay harvesting is not yet fully implemented")
            print(f"   This will require:")
            print(f"   1. Finding each school's MaxPreps URL")
            print(f"   2. Scraping meet results pages")
            print(f"   3. Extracting relay times")
            print(f"   4. Filtering by date")
            print(f"\n   For now, only leaderboard data has been harvested.")
            
            # boys_relays = harvester.harvest_all_school_relays(
            #     all_schools, "boys", cutoff_date
            # )
            # girls_relays = harvester.harvest_all_school_relays(
            #     all_schools, "girls", cutoff_date
            # )
            
            # if not boys_relays.empty:
            #     harvester.save_data(
            #         boys_relays,
            #         f"{args.division}_boys_relays_since_{args.cutoff_date.replace('-', '')}_{harvest_date}.csv"
            #     )
            
            # if not girls_relays.empty:
            #     harvester.save_data(
            #         girls_relays,
            #         f"{args.division}_girls_relays_since_{args.cutoff_date.replace('-', '')}_{harvest_date}.csv"
            #     )
        
    finally:
        harvester._close_playwright()
    
    print("\n" + "="*70)
    print(" Harvest Complete!")
    print("="*70)
    print(f"\n📊 Results saved to: {output_dir.absolute()}")
    print("\n💡 Files created:")
    print(f"   • {args.division}_boys_leaderboard_top{args.top_n}_{harvest_date}.csv")
    print(f"   • {args.division}_girls_leaderboard_top{args.top_n}_{harvest_date}.csv")
    print(f"   • {args.division}_schools_{harvest_date}.csv")
    if not args.leaderboard_only:
        print(f"   • (Relay files - pending full implementation)")
    print()


if __name__ == "__main__":
    main()

