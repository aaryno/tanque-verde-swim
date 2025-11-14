#!/bin/bash
#
# Quick Test of Harvest System (with Virtual Environment)
#
# This script activates the virtual environment and runs a quick test.

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "========================================================================"
echo " Quick Harvest System Test"
echo "========================================================================"
echo ""

# Activate virtual environment
if [ -d "../swim-data-tool/.venv" ]; then
    echo "🔧 Activating swim-data-tool virtual environment..."
    source ../swim-data-tool/.venv/bin/activate
    echo ""
fi

# Run setup check
echo "📋 Running setup verification..."
python3 test_harvest_setup.py

echo ""
echo "========================================================================"
echo " Setup Check Complete!"
echo "========================================================================"
echo ""
echo "💡 To run a full harvest:"
echo "   ./harvest_all.sh"
echo ""
echo "📊 To extract D3 boys data from web search:"
echo "   source ../swim-data-tool/.venv/bin/activate"
echo "   python3 extract_leaderboard_from_webpage.py"
echo ""

