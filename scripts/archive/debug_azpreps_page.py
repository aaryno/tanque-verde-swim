#!/usr/bin/env python3
"""Debug AzPreps365 page structure."""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'swim-data-tool' / 'src'))

url = "https://azpreps365.com/leaderboards/swimming-boys/d3"

print(f"Inspecting: {url}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    try:
        # Don't wait for networkidle - just load
        print("Loading page (domcontentloaded)...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        print("✓ Page loaded\n")
        
        # Wait a bit for JavaScript
        time.sleep(5)
        
        # Save HTML
        html_file = "azpreps_debug.html"
        with open(html_file, 'w') as f:
            f.write(page.content())
        print(f"✓ Saved HTML to: {html_file}\n")
        
        # Check for select elements
        print("Looking for select elements...")
        selects = page.query_selector_all('select')
        print(f"Found {len(selects)} select elements:")
        for i, select in enumerate(selects):
            select_id = select.get_attribute('id')
            select_name = select.get_attribute('name')
            select_class = select.get_attribute('class')
            print(f"  [{i}] id='{select_id}' name='{select_name}' class='{select_class}'")
            
            # Get options
            options = select.query_selector_all('option')
            print(f"      {len(options)} options")
            if options:
                for j, opt in enumerate(options[:5]):  # First 5
                    print(f"        - {opt.inner_text()}")
                if len(options) > 5:
                    print(f"        ... and {len(options) - 5} more")
        
        print()
        
        # Look for buttons
        print("Looking for buttons...")
        buttons = page.query_selector_all('button')
        print(f"Found {len(buttons)} buttons:")
        for i, button in enumerate(buttons[:10]):  # First 10
            text = button.inner_text().strip()
            if text:
                print(f"  [{i}] {text}")
        
        print()
        
        # Look for tables
        print("Looking for tables...")
        tables = page.query_selector_all('table')
        print(f"Found {len(tables)} tables")
        
        print()
        
        # Look for leaderboard-specific elements
        print("Looking for leaderboard elements...")
        leaderboard_divs = page.query_selector_all('[class*="leaderboard"]')
        print(f"Found {len(leaderboard_divs)} elements with 'leaderboard' in class")
        
        # Look for event-related elements
        event_elements = page.query_selector_all('[class*="event"], [id*="event"]')
        print(f"Found {len(event_elements)} elements with 'event' in class/id")
        
        print("\n✓ Debug complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser.close()

print(f"\nCheck {html_file} for full page HTML")

