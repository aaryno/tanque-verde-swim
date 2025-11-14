#!/bin/bash
#
# Complete AzPreps365 Harvest Pipeline
#
# Runs all harvest scripts in sequence:
# 1. D3 leaderboards (boys and girls)
# 2. New relay results (October 20+)
#
# Usage: ./harvest_all.sh

set -e  # Exit on error

echo ""
echo "========================================================================"
echo " AzPreps365 Complete Harvest Pipeline"
echo "========================================================================"
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if needed
if [ -d "../swim-data-tool/.venv" ]; then
    echo "🔧 Activating swim-data-tool virtual environment..."
    source ../swim-data-tool/.venv/bin/activate
fi

# Step 1: Harvest D3 Leaderboards
echo ""
echo "========================================================================"
echo " Step 1: Harvesting D3 Leaderboards"
echo "========================================================================"
python3 harvest_azpreps365.py

# Step 2: Harvest New Relays
echo ""
echo "========================================================================"
echo " Step 2: Harvesting New Relay Results"
echo "========================================================================"
python3 harvest_relays.py

# Summary
echo ""
echo "========================================================================"
echo " ✅ Complete Harvest Finished!"
echo "========================================================================"
echo ""
echo "📁 Results are in: data/raw/azpreps365_harvest/$(date +%Y-%m-%d)/"
echo ""
echo "💡 Next steps:"
echo "   1. Review harvested data"
echo "   2. Process and integrate with existing records"
echo "   3. Generate updated leaderboards"
echo ""

