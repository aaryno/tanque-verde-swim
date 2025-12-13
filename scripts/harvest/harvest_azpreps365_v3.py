#!/usr/bin/env python3
"""
Harvest AzPreps365 D3 Leaderboards (v3 - Direct URL Method)

Scrapes Division III boys and girls swimming leaderboards from azpreps365.com.
Uses direct event URLs (top 50 results already loaded on each page).

Usage:
    python3 harvest_azpreps365_v3.py
    python3 harvest_azpreps365_v3.py --output-dir=data/raw/harvest_2024_11_01
    python3 harvest_azpreps365_v3.py --division=d3 --top-n=50
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import time

# Add swim-data-tool to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'swim-data-tool' / 'src'))


class AzPreps365ScraperV3:
    """Scraper for AzPreps365 leaderboards using direct event URLs."""
    
    BASE_URL = "https://azpreps365.com"
    
    def __init__(self, output_dir: Path, top_n: int = 50):
        """Initialize scraper with output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.top_n = top_n
        
    def scrape_division_leaderboard(self, division: str, gender: str) -> pd.DataFrame:
        """
        Scrape leaderboard for a specific division and gender.
        
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
        
        print(f"\n🎭 Scraping {gender.title()} {division.upper()} leaderboard (top {self.top_n})...")
        
        all_data = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Define events to scrape (URL slug format)
                # Each event has its own page: /leaderboards/swimming-{gender}/{division}/{event_slug}
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
                
                for event_slug, event_name in events:
                    # Go directly to the event page (top 50 already loaded!)
                    url = f"{self.BASE_URL}/leaderboards/swimming-{gender}/{division}/{event_slug}"
                    print(f"   📊 Scraping {event_name}...")
                    
                    try:
                        # Navigate to event page
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(2)  # Wait for content to render
                        
                        # Extract results from table
                        # Results are in a table with rows
                        result_rows = page.query_selector_all('table tbody tr')
                        
                        count = 0
                        for row in result_rows:
                            if count >= self.top_n:
                                break
                                
                            try:
                                cols = row.query_selector_all('td')
                                if len(cols) < 4:
                                    continue
                                
                                # Column 0: Rank
                                rank_text = cols[0].inner_text().strip()
                                try:
                                    rank = int(rank_text)
                                except:
                                    continue
                                
                                # Column 1: Athlete name (with link)
                                athlete_link = cols[1].query_selector('a')
                                if athlete_link:
                                    athlete = athlete_link.inner_text().strip()
                                else:
                                    continue
                                
                                # School is also in column 1 (as a separate link)
                                school_links = cols[1].query_selector_all('a')
                                if len(school_links) >= 2:
                                    school = school_links[1].inner_text().strip()
                                else:
                                    school = "Unknown"
                                
                                # Column 3: Time
                                time_str = cols[3].inner_text().strip()
                                
                                all_data.append({
                                    'event': event_name,
                                    'athlete': athlete,
                                    'school': school,
                                    'time': time_str,
                                    'rank': rank,
                                    'division': division,
                                    'gender': gender,
                                    'harvest_date': datetime.now().strftime("%Y-%m-%d")
                                })
                                count += 1
                            except Exception as e:
                                # Skip rows that don't parse correctly
                                continue
                        
                        print(f"      ✓ Found {count} results")
                        
                    except Exception as e:
                        print(f"      ⚠️  Error scraping {event_name}: {e}")
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
        filename = f"azpreps365_{division}_{gender}_leaderboard_top{self.top_n}_{harvest_date}.csv"
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
        description='Harvest AzPreps365 D3 Leaderboards (v3 - Direct URL method)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default directory (data/raw/azpreps365_harvest/YYYY-MM-DD/)
  python3 harvest_azpreps365_v3.py
  
  # Specify custom output directory
  python3 harvest_azpreps365_v3.py --output-dir=data/raw/harvest_2024_11_01
  
  # Top 25 instead of 50
  python3 harvest_azpreps365_v3.py --top-n=25
  
  # Different division
  python3 harvest_azpreps365_v3.py --division=d2 --top-n=50
        """
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for harvest data (default: data/raw/azpreps365_harvest/YYYY-MM-DD/)'
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
        help='Number of top results to harvest per event (default: 50)'
    )
    parser.add_argument(
        '--no-timestamp',
        action='store_true',
        help='Do not append timestamp to output directory'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(f" AzPreps365 {args.division.upper()} Leaderboard Harvest (v3)")
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
    print(f"🎯 Division: {args.division.upper()}")
    print(f"🔢 Top N per event: {args.top_n}")
    
    # Initialize scraper
    scraper = AzPreps365ScraperV3(harvest_dir, args.top_n)
    
    # Scrape Boys and Girls
    genders = ["boys", "girls"]
    
    for gender in genders:
        df = scraper.scrape_division_leaderboard(args.division, gender)
        
        if df.empty:
            print(f"⚠️  No data retrieved for {gender} {args.division}")
        else:
            scraper.save_leaderboard(df, args.division, gender, harvest_date)
    
    print("\n" + "="*70)
    print(" Harvest Complete!")
    print("="*70)
    print(f"\n📊 Results saved to: {harvest_dir.absolute()}")
    print("\n💡 Next steps:")
    print("   1. Inspect the saved CSV files")
    print(f"   2. Run relay harvest: python3 harvest_relays_v2.py --output-dir={harvest_dir}")
    print("   3. Use for lineup optimizer")
    print()


if __name__ == "__main__":
    main()

