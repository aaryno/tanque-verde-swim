#!/bin/bash
# Test script for season range functionality

set -e  # Exit on error

echo "🧪 Testing Season Range Functionality"
echo "======================================"
echo ""

# Test 1: Single explicit season
echo "Test 1: Single explicit season (25-26)"
echo "Command: uv run swim-data-tool roster --source=maxpreps --seasons=25-26"
echo ""
uv run swim-data-tool roster --source=maxpreps --seasons=25-26
echo ""
echo "✅ Test 1 passed"
echo ""
sleep 2

# Test 2: Season range
echo "Test 2: Season range (22-23 to 24-25)"
echo "Command: uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25"
echo ""
uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25
echo ""
echo "✅ Test 2 passed"
echo ""
sleep 2

# Test 3: Error handling (only start-season)
echo "Test 3: Error handling (only start-season provided)"
echo "Command: uv run swim-data-tool roster --source=maxpreps --start-season=22-23"
echo ""
if uv run swim-data-tool roster --source=maxpreps --start-season=22-23 2>&1 | grep -q "Both --start-season and --end-season must be provided together"; then
    echo "✅ Test 3 passed (error message shown correctly)"
else
    echo "❌ Test 3 failed (expected error message not shown)"
    exit 1
fi
echo ""

# Test 4: Error handling (only end-season)
echo "Test 4: Error handling (only end-season provided)"
echo "Command: uv run swim-data-tool roster --source=maxpreps --end-season=24-25"
echo ""
if uv run swim-data-tool roster --source=maxpreps --end-season=24-25 2>&1 | grep -q "Both --start-season and --end-season must be provided together"; then
    echo "✅ Test 4 passed (error message shown correctly)"
else
    echo "❌ Test 4 failed (expected error message not shown)"
    exit 1
fi
echo ""

echo "🎉 All tests passed!"
echo ""
echo "📊 Check the roster CSV:"
echo "  cat data/lookups/roster-maxpreps.csv | head -20"

