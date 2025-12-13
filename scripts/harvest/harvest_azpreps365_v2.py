#!/usr/bin/env python3
"""
Harvest AzPreps365 D3 Leaderboards (v2 - Configurable Output)

Scrapes Division III boys and girls swimming leaderboards from azpreps365.com.
Enhanced version with configurable output directory to avoid overwriting existing data.

Usage:
    python3 harvest_azpreps365_v2.py
    python3 harvest_azpreps365_v2.py --output-dir=data/raw/harvest_2024_11_01
    python3 harvest_azpreps365_v2.py --output-dir=../swim-data-tool/data/reports/azpreps/d3-leaderboards
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from typing import Optional

# Add swim-data-tool to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'swim-data-tool' / 'src'))


class AzPreps365Scraper:
    """Scraper for AzPreps365 leaderboards."""
    
    BASE_URL = "https://azpreps365.com"
    
    def __init__(self, output_dir: Path):
        """Initialize scraper with output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def scrape_division_leaderboard(self, division: str, gender: str) -> pd.DataFrame:
        """
        Scrape leaderboard for a specific division and gender.
        
        Args:
            division: Division code (d1, d2, d3, d4)
            gender: Gender (boys, girls)
            
        Returns:
            DataFrame with leaderboard data
        """
        url = f"{self.BASE_URL}/leaderboards/swimming-{gender}/{division}"
        print(f"\n📥 Fetching {gender.title()} {division.upper()} leaderboard...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all event sections
            all_data = []
            
            # Look for event data - this needs to be customized based on page structure
            # The page appears to use JavaScript to load leaderboard content dynamically
            # We may need to use Playwright for this
            
            print(f"⚠️  Page loaded, but dynamic content detection needed")
            print(f"   HTML length: {len(response.content)} bytes")
            
            # For now, save the raw HTML for inspection
            html_file = self.output_dir / f"raw_html_{gender}_{division}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"   Saved raw HTML to: {html_file}")
            
            return pd.DataFrame()
            
        except requests.RequestException as e:
            print(f"❌ Error fetching {gender} {division}: {e}")
            return pd.DataFrame()
    
    def scrape_with_playwright(self, division: str, gender: str) -> pd.DataFrame:
        """
        Scrape leaderboard using Playwright (handles JavaScript).
        
        Args:
            division: Division code (d1, d2, d3, d4)
            gender: Gender (boys, girls)
            
        Returns:
            DataFrame with leaderboard data
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("❌ Playwright not installed. Install with: pip install playwright && playwright install")
            return pd.DataFrame()
        
        url = f"{self.BASE_URL}/leaderboards/swimming-{gender}/{division}"
        print(f"\n🎭 Using Playwright to fetch {gender.title()} {division.upper()} leaderboard...")
        print(f"   URL: {url}")
        
        all_data = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
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
                    print(f"   📊 Scraping {event_name}...")
                    
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
                        # Results are in div.columns.is-mobile within div.box.leaderboard-top-ten
                        result_rows = page.query_selector_all('div.box.leaderboard-top-ten div.columns.is-mobile')
                        
                        for i, row in enumerate(result_rows, 1):
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
                                    'division': division,
                                    'gender': gender,
                                    'harvest_date': datetime.now().strftime("%Y-%m-%d")
                                })
                            except Exception as e:
                                # Skip rows that don't parse correctly
                                continue
                        
                        print(f"      ✓ Found {len(result_rows)} results")
                        
                    except Exception as e:
                        print(f"      ⚠️  Error scraping {event}: {e}")
                        continue
                
            except Exception as e:
                print(f"❌ Error during scraping: {e}")
            finally:
                browser.close()
        
        if all_data:
            df = pd.DataFrame(all_data)
            print(f"\n✅ Successfully scraped {len(df)} total results")
            return df
        else:
            print(f"\n⚠️  No data scraped")
            return pd.DataFrame()
    
    def save_leaderboard(self, df: pd.DataFrame, division: str, gender: str, 
                        harvest_date: str) -> Path:
        """
        Save leaderboard data to CSV.
        
        Args:
            df: DataFrame with leaderboard data
            division: Division code
            gender: Gender
            harvest_date: Date string (YYYY-MM-DD)
            
        Returns:
            Path to saved file
        """
        filename = f"azpreps365_{division}_{gender}_leaderboard_{harvest_date}.csv"
        output_path = self.output_dir / filename
        
        df.to_csv(output_path, index=False)
        print(f"\n💾 Saved {len(df)} results to: {output_path}")
        
        # Display summary by event
        if not df.empty:
            print(f"\n📊 Results by event:")
            event_counts = df.groupby('event').size()
            for event, count in event_counts.items():
                print(f"   {event}: {count} results")
        
        return output_path


def main():
    """Main execution function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Harvest AzPreps365 D3 Leaderboards with configurable output directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default directory (data/raw/azpreps365_harvest/YYYY-MM-DD/)
  python3 harvest_azpreps365_v2.py
  
  # Specify custom output directory
  python3 harvest_azpreps365_v2.py --output-dir=data/raw/harvest_2024_11_01
  
  # Output to swim-data-tool directory for lineup optimizer
  python3 harvest_azpreps365_v2.py --output-dir=../swim-data-tool/data/reports/azpreps/d3-leaderboards
        """
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for harvest data (default: data/raw/azpreps365_harvest/YYYY-MM-DD/)'
    )
    parser.add_argument(
        '--no-timestamp',
        action='store_true',
        help='Do not append timestamp to output directory'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" AzPreps365 D3 Leaderboard Harvest (v2 - Configurable)")
    print("="*70)
    
    # Determine output directory
    harvest_date = datetime.now().strftime("%Y-%m-%d")
    
    if args.output_dir:
        # Use specified directory
        if args.no_timestamp:
            harvest_dir = Path(args.output_dir)
        else:
            harvest_dir = Path(args.output_dir) / harvest_date
    else:
        # Use default directory with timestamp
        harvest_dir = Path("data/raw/azpreps365_harvest") / harvest_date
    
    print(f"\n📁 Output directory: {harvest_dir.absolute()}")
    
    # Initialize scraper
    scraper = AzPreps365Scraper(harvest_dir)
    
    # Scrape D3 Boys and Girls
    divisions = ["d3"]
    genders = ["boys", "girls"]
    
    for division in divisions:
        for gender in genders:
            # Try with Playwright first (handles JavaScript)
            df = scraper.scrape_with_playwright(division, gender)
            
            if df.empty:
                print(f"⚠️  No data retrieved for {gender} {division}")
            else:
                scraper.save_leaderboard(df, division, gender, harvest_date)
    
    print("\n" + "="*70)
    print(" Harvest Complete!")
    print("="*70)
    print(f"\n📊 Results saved to: {harvest_dir.absolute()}")
    print("\n💡 Next steps:")
    print("   1. Inspect the saved CSV files")
    print(f"   2. Run relay harvest: python3 harvest_relays_v2.py --output-dir={harvest_dir}")
    print("   3. Process and merge data")
    print()


if __name__ == "__main__":
    main()

