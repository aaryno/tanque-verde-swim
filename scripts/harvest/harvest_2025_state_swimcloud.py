#!/usr/bin/env python3
"""
Harvest 2025 AIA D3 State Championship results from SwimCloud

Scrapes meet results from SwimCloud and filters for Tanque Verde swimmers.

Usage:
    python3 harvest_2025_state_swimcloud.py
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import time
import re

# Add swim-data-tool to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'swim-data-tool' / 'src'))


class SwimCloudStateScraper:
    """Scraper for SwimCloud state meet results."""
    
    MEET_URL = "https://www.swimcloud.com/results/350442/"
    MEET_NAME = "2025 D3 State Championship (Paradise Valley, AZ)"
    MEET_DATE = "11/8/2025"
    
    # Event IDs: 301-324 plus 408
    # EVENT_IDS = list(range(301, 325)) + [408]
    EVENT_IDS = [303]  # Test with one event first
    
    def __init__(self, output_dir: Path):
        """Initialize scraper with output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def scrape_event(self, event_id: int, browser, page) -> list:
        """
        Scrape results for a single event.
        
        Args:
            event_id: Event ID number
            browser: Playwright browser instance
            page: Playwright page instance
            
        Returns:
            List of swim dictionaries
        """
        url = f"{self.MEET_URL}event/{event_id}/"
        swims = []
        
        try:
            # Navigate to event page
            print(f"   Loading {url}...")
            page.goto(url, wait_until="networkidle", timeout=15000)
            time.sleep(1)
            
            # Get event name
            event_header = page.query_selector('.c-result-event__header, h1.u-section-title, h1')
            if not event_header:
                print(f"      ⚠ No event header found")
                return swims
            
            event_name = event_header.inner_text().strip()
            print(f"   Found event: {event_name}")
            
            # Determine gender from event name
            gender = "M" if "Boys" in event_name else "F"
            
            # Determine round
            round_type = "Preliminary" if "Prelim" in event_name else "Final"
            
            # Clean event name
            clean_event = event_name.replace("Boys ", "").replace("Girls ", "")
            clean_event = clean_event.replace(" - Prelims", "").replace(" - Finals", "")
            clean_event = clean_event.replace(" - A", "").replace(" - B", "")
            
            # Get all result rows (only tbody rows, not headers)
            result_rows = page.query_selector_all('tbody tr')
            
            if not result_rows:
                return swims
            
            print(f"   Event {event_id}: {event_name} ({len(result_rows)} rows)")
            
            for row in result_rows:
                # Get all td elements in row
                cells = row.query_selector_all('td')
                if len(cells) < 4:
                    continue
                
                # Get swimmer name (first column with swimmer link)
                name_el = row.query_selector('a[href*="/swimmer/"]')
                if not name_el:
                    continue
                swimmer_name = name_el.inner_text().strip()
                
                # Check if this row has Tanque Verde (look in the row text)
                row_text = row.inner_text()
                if "Tanque Verde" not in row_text and "TVHS" not in row_text:
                    continue
                
                # Get grade/year (column before time, usually 3rd or 4th column)
                grade = ""
                for cell in cells:
                    cell_text = cell.inner_text().strip()
                    if cell_text in ['FR', 'SO', 'JR', 'SR', '9', '10', '11', '12']:
                        grade = cell_text
                        break
                
                # Get time (last numeric column with time format)
                swim_time = ""
                for cell in cells:
                    # Look for time links or time divs
                    time_link = cell.query_selector('a[href*="/times/"], div[id^="time"]')
                    if time_link:
                        swim_time = time_link.inner_text().strip()
                        break
                
                # Skip if not a valid time
                if not swim_time or swim_time in ['DQ', 'NS', 'SCR', 'DNF', '--']:
                    continue
                
                swim = {
                    'Name': swimmer_name,
                    'Gender': gender,
                    'grade': grade,
                    'Event': clean_event + " SCY",
                    'SwimTime': swim_time,
                    'SwimDate': self.MEET_DATE,
                    'MeetName': self.MEET_NAME,
                    'round': round_type,
                    'Team': "Tanque Verde (Tucson, AZ)",
                    'source': 'swimcloud_state'
                }
                swims.append(swim)
                print(f"      ✓ {swimmer_name} - {clean_event}: {swim_time} ({round_type})")
        
        except Exception as e:
            print(f"      ⚠ Error on event {event_id}: {e}")
        
        return swims
    
    def scrape_all_events(self) -> list:
        """
        Scrape all events from the meet.
        
        Returns:
            List of all swim dictionaries
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("❌ Playwright not installed. Install with: pip install playwright && playwright install")
            sys.exit(1)
        
        print(f"\n📊 Scraping 2025 State Championship from SwimCloud...")
        print(f"   Events: {len(self.EVENT_IDS)} total")
        
        all_swims = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Non-headless to avoid 403
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            try:
                for event_id in self.EVENT_IDS:
                    swims = self.scrape_event(event_id, browser, page)
                    all_swims.extend(swims)
                    time.sleep(1)  # Be polite to the server
                
            finally:
                browser.close()
        
        return all_swims
    
    def scrape_all(self) -> pd.DataFrame:
        """Scrape all events and save results."""
        # Scrape all events
        all_swims = self.scrape_all_events()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_swims)
        
        if df.empty:
            print("\n⚠ No swims found!")
            return df
        
        # Save to CSV
        output_file = self.output_dir / f'tvhs-state-2025-swimcloud.csv'
        df.to_csv(output_file, index=False)
        print(f"\n✓ Saved {len(df)} swims to: {output_file}")
        
        return df


def main():
    """Main entry point."""
    output_dir = Path('data/raw/aia-state')
    
    print("=" * 80)
    print("🏊 2025 AIA D3 State Championship - SwimCloud Harvester")
    print("=" * 80)
    
    scraper = SwimCloudStateScraper(output_dir)
    df = scraper.scrape_all()
    
    # Print summary
    print(f"\n📊 Summary:")
    if not df.empty:
        print(f"   Total swims: {len(df)}")
        print(f"   Boys: {len(df[df['Gender'] == 'M'])}")
        print(f"   Girls: {len(df[df['Gender'] == 'F'])}")
        print(f"   Unique swimmers: {df['Name'].nunique()}")
        print(f"\n✓ Harvest complete!")
    else:
        print(f"   No swims found!")
        print(f"\n⚠ Check if Tanque Verde competed at this meet.")


if __name__ == '__main__':
    main()

