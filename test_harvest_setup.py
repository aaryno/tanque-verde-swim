#!/usr/bin/env python3
"""
Test Harvest Setup

Quick verification that all harvest components are in place.
"""

from pathlib import Path
import sys

def check_file(filepath: Path, description: str) -> bool:
    """Check if a file exists and report."""
    if filepath.exists():
        print(f"✅ {description}: {filepath.name}")
        return True
    else:
        print(f"❌ Missing {description}: {filepath.name}")
        return False

def main():
    print("\n" + "="*70)
    print(" Harvest System Setup Check")
    print("="*70)
    
    base_dir = Path(__file__).parent
    
    # Check harvest scripts
    print("\n📝 Checking harvest scripts:")
    all_good = True
    
    all_good &= check_file(base_dir / "harvest_azpreps365.py", "Leaderboard scraper")
    all_good &= check_file(base_dir / "harvest_relays.py", "Relay collector")
    all_good &= check_file(base_dir / "harvest_all.sh", "Master harvest script")
    all_good &= check_file(base_dir / "parse_azpreps365_html.py", "HTML parser")
    all_good &= check_file(base_dir / "README_HARVEST.md", "Harvest documentation")
    
    # Check dependencies
    print("\n📦 Checking dependencies:")
    
    try:
        import requests
        print("✅ requests library")
    except ImportError:
        print("❌ requests library (install with: pip install requests)")
        all_good = False
    
    try:
        import bs4
        print("✅ beautifulsoup4 library")
    except ImportError:
        print("❌ beautifulsoup4 library (install with: pip install beautifulsoup4)")
        all_good = False
    
    try:
        import playwright
        print("✅ playwright library")
    except ImportError:
        print("⚠️  playwright library (optional, install with: pip install playwright)")
        print("   (Only needed for JavaScript-heavy pages)")
    
    try:
        import pandas
        print("✅ pandas library")
    except ImportError:
        print("❌ pandas library (install with: pip install pandas)")
        all_good = False
    
    # Check directory structure
    print("\n📁 Checking directory structure:")
    
    data_dir = base_dir / "data" / "raw"
    if data_dir.exists():
        print(f"✅ Data directory: {data_dir}")
    else:
        print(f"⚠️  Data directory will be created on first harvest: {data_dir}")
    
    # Check for existing relay data
    relays_file = data_dir / "team-relays.csv"
    if relays_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(relays_file)
            print(f"✅ Existing relay data: {len(df)} relay results")
        except ImportError:
            print(f"⚠️  Relay data exists but pandas not available: {relays_file.name}")
    else:
        print("⚠️  No existing relay data found (will be created)")
    
    # Check for swim-data-tool
    print("\n🔧 Checking swim-data-tool:")
    
    tool_dir = base_dir.parent / "swim-data-tool"
    if tool_dir.exists():
        print(f"✅ swim-data-tool found: {tool_dir}")
        
        venv_dir = tool_dir / ".venv"
        if venv_dir.exists():
            print(f"✅ Virtual environment: {venv_dir}")
        else:
            print(f"⚠️  No virtual environment in swim-data-tool")
    else:
        print(f"⚠️  swim-data-tool not found at: {tool_dir}")
    
    # Check .env
    env_file = base_dir / ".env"
    if env_file.exists():
        print("✅ Environment configuration (.env)")
    else:
        print("⚠️  No .env file (MaxPreps settings may be needed)")
    
    # Summary
    print("\n" + "="*70)
    if all_good:
        print(" ✅ Setup Complete - Ready to Harvest!")
    else:
        print(" ⚠️  Setup Incomplete - Install missing dependencies")
    print("="*70)
    
    print("\n💡 To start harvesting:")
    print("   ./harvest_all.sh")
    print()
    print("📖 For more info:")
    print("   cat README_HARVEST.md")
    print()
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())

