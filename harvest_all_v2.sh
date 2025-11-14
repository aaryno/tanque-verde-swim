#!/bin/bash
#
# Complete AzPreps365 Harvest Pipeline (v2 - Configurable Output)
#
# Runs all harvest scripts in sequence with configurable output directory:
# 1. D3 leaderboards (boys and girls)
# 2. New relay results (configurable cutoff date)
#
# Usage:
#   ./harvest_all_v2.sh
#   ./harvest_all_v2.sh data/raw/harvest_2024_11_01
#   ./harvest_all_v2.sh ../swim-data-tool/data/reports/azpreps/d3-leaderboards
#   OUTPUT_DIR=data/raw/harvest_new CUTOFF_DATE=2024-10-01 ./harvest_all_v2.sh

set -e  # Exit on error

echo ""
echo "========================================================================"
echo " AzPreps365 Complete Harvest Pipeline (v2 - Configurable)"
echo "========================================================================"
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Parse command-line arguments
OUTPUT_DIR="${1:-${OUTPUT_DIR}}"
CUTOFF_DATE="${CUTOFF_DATE:-2024-10-20}"

# Display configuration
if [ -n "$OUTPUT_DIR" ]; then
    echo "📁 Output directory: $OUTPUT_DIR"
else
    echo "📁 Output directory: data/raw/azpreps365_harvest/$(date +%Y-%m-%d)/ (default)"
fi
echo "📅 Relay cutoff date: $CUTOFF_DATE"
echo ""

# Activate virtual environment if needed
if [ -d "../swim-data-tool/.venv" ]; then
    echo "🔧 Activating swim-data-tool virtual environment..."
    source ../swim-data-tool/.venv/bin/activate
fi

# Build command arguments
HARVEST_ARGS=""
if [ -n "$OUTPUT_DIR" ]; then
    HARVEST_ARGS="--output-dir=$OUTPUT_DIR"
fi

# Step 1: Harvest D3 Leaderboards
echo ""
echo "========================================================================"
echo " Step 1: Harvesting D3 Leaderboards"
echo "========================================================================"
python3 harvest_azpreps365_v2.py $HARVEST_ARGS

# Step 2: Harvest New Relays
echo ""
echo "========================================================================"
echo " Step 2: Harvesting New Relay Results"
echo "========================================================================"
python3 harvest_relays_v2.py $HARVEST_ARGS --cutoff-date=$CUTOFF_DATE

# Summary
echo ""
echo "========================================================================"
echo " ✅ Complete Harvest Finished!"
echo "========================================================================"
echo ""

if [ -n "$OUTPUT_DIR" ]; then
    echo "📁 Results are in: $OUTPUT_DIR/$(date +%Y-%m-%d)/"
else
    echo "📁 Results are in: data/raw/azpreps365_harvest/$(date +%Y-%m-%d)/"
fi

echo ""
echo "💡 Next steps:"
echo "   1. Review harvested data"
echo "   2. Process and integrate with existing records"
echo "   3. Generate updated leaderboards"
echo ""
echo "💡 For lineup optimizer:"
echo "   cd ../swim-data-tool"
echo "   swim-data-tool optimize lineup \\"
echo "     --roster=examples/roster_example.csv \\"
if [ -n "$OUTPUT_DIR" ]; then
    echo "     --leaderboard=$OUTPUT_DIR/$(date +%Y-%m-%d)/azpreps365_d3_boys_leaderboard_$(date +%Y-%m-%d).csv \\"
else
    echo "     --leaderboard=../tanque-verde/data/raw/azpreps365_harvest/$(date +%Y-%m-%d)/azpreps365_d3_boys_leaderboard_$(date +%Y-%m-%d).csv \\"
fi
echo "     --team-name=\"Tanque Verde\""
echo ""

