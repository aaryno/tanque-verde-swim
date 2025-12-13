#!/usr/bin/env python3
"""Debug script to inspect SwimCloud page structure"""

from playwright.sync_api import sync_playwright
import time

url = "https://www.swimcloud.com/results/350442/event/303/"  # Try individual event

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Non-headless to see what's happening
    page = browser.new_page()
    
    print(f"Loading: {url}")
    page.goto(url, wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    # Save HTML
    html = page.content()
    with open('/tmp/swimcloud_debug.html', 'w') as f:
        f.write(html)
    print("Saved HTML to /tmp/swimcloud_debug.html")
    
    # Try to find elements
    print("\nLooking for elements...")
    
    # Try different selectors for event title
    title_selectors = ['h1', '.c-result-event__header', '.u-section-title', 'title']
    for selector in title_selectors:
        el = page.query_selector(selector)
        if el:
            print(f"  Title ({selector}): {el.inner_text().strip()[:100]}")
    
    # Try different selectors for result rows
    row_selectors = ['.c-result__row', 'tr', 'table tr', '.c-table-clean__row']
    for selector in row_selectors:
        rows = page.query_selector_all(selector)
        if rows:
            print(f"  Found {len(rows)} rows with: {selector}")
    
    # Look for Tanque Verde
    tanque_els = page.query_selector_all('text=Tanque Verde')
    print(f"\n  Found {len(tanque_els)} instances of 'Tanque Verde'")
    
    time.sleep(2)
    browser.close()

