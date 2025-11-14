#!/usr/bin/env python3
"""
Harvest AzPreps365 D3 Leaderboards

Scrapes Division III boys and girls swimming leaderboards from azpreps365.com.
This is the main orchestration script for data collection.
"""

import sys
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
        Scrape leaderboard using Playwright for JavaScript rendering.
        
        Args:
            division: Division code (d1, d2, d3, d4)
            gender: Gender (boys, girls)
            
        Returns:
            DataFrame with leaderboard data
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("❌ Playwright not installed. Install with: pip install playwright && playwright install chromium")
            return pd.DataFrame()
        
        url = f"{self.BASE_URL}/leaderboards/swimming-{gender}/{division}"
        print(f"\n📥 Fetching {gender.title()} {division.upper()} leaderboard (Playwright)...")
        print(f"   URL: {url}")
        
        all_events = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to the page
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Wait for content to load
                page.wait_for_timeout(5000)
                
                # Find all event categories in the dropdown
                categories = page.query_selector_all('select option')
                print(f"   Found {len(categories)} event categories")
                
                for category in categories:
                    category_name = category.inner_text()
                    if not category_name or category_name == "Select Category":
                        continue
                    
                    print(f"   Processing: {category_name}")
                    
                    # Select the category
                    page.select_option('select', label=category_name)
                    
                    # Click "Load Leaderboard" button
                    load_button = page.query_selector('button:has-text("Load Leaderboard")')
                    if load_button:
                        load_button.click()
                        page.wait_for_timeout(3000)  # Wait for results to load
                        
                        # Parse the results
                        html = page.content()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find the results table/section
                        # The structure varies by event type
                        results = self._parse_event_results(soup, category_name, division, gender)
                        all_events.extend(results)
                        
                        print(f"      → Found {len(results)} results")
                    
                    time.sleep(1)  # Be polite to the server
                    
            finally:
                browser.close()
        
        if all_events:
            df = pd.DataFrame(all_events)
            return df
        else:
            print("⚠️  No events found")
            return pd.DataFrame()
    
    def _parse_event_results(self, soup: BeautifulSoup, event_name: str, 
                            division: str, gender: str) -> list[dict]:
        """
        Parse results for a specific event from the page HTML.
        
        Args:
            soup: BeautifulSoup object with page content
            event_name: Name of the event
            division: Division code
            gender: Gender
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        # Look for result entries
        # Based on the web search, results appear in a structured format with:
        # - Athlete name
        # - School name
        # - Time
        
        # Find all result entries (need to inspect actual HTML structure)
        result_divs = soup.find_all('div', class_='leaderboard-entry')  # This class name is a guess
        
        # If we can't find specific divs, look for the athlete names mentioned in the search results
        if not result_divs:
            # Try parsing based on the known athletes from the search results
            # Look for Wade Olsson, Zachary Duerkop, etc.
            content = soup.get_text()
            
            # For now, return empty - we need to see the actual HTML structure
            pass
        
        return results
    
    def save_leaderboard(self, df: pd.DataFrame, division: str, gender: str, 
                        harvest_date: str) -> Path:
        """
        Save leaderboard data to CSV.
        
        Args:
            df: DataFrame with leaderboard data
            division: Division code
            gender: Gender
            harvest_date: Date string for filename
            
        Returns:
            Path to saved file
        """
        if df.empty:
            print(f"⚠️  No data to save for {gender} {division}")
            return None
        
        filename = f"azpreps365_{division}_{gender}_leaderboard_{harvest_date}.csv"
        output_path = self.output_dir / filename
        
        df.to_csv(output_path, index=False)
        print(f"✅ Saved {len(df)} entries to: {output_path}")
        
        return output_path


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print(" AzPreps365 D3 Leaderboard Harvest")
    print("="*70)
    
    # Create harvest directory with timestamp
    harvest_date = datetime.now().strftime("%Y-%m-%d")
    harvest_dir = Path("data/raw/azpreps365_harvest") / harvest_date
    
    print(f"\n📁 Output directory: {harvest_dir}")
    
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
    print(f"\n📊 Results saved to: {harvest_dir}")
    print("\n💡 Next steps:")
    print("   1. Inspect the saved CSV files")
    print("   2. Run relay harvest: python3 harvest_relays.py")
    print("   3. Process and merge data")
    print()


if __name__ == "__main__":
    main()

