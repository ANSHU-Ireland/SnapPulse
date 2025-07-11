#!/bin/bash
set -e

echo "🧪 SnapPulse Smoke Test Suite"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass_test() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

fail_test() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

warn_test() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Get service IPs
echo "🔍 Detecting service endpoints..."

if command -v juju &> /dev/null; then
    API_IP=$(juju status api --format=yaml 2>/dev/null | grep public-address | awk '{print $2}' || echo "")
    DASHBOARD_IP=$(juju status dashboard --format=yaml 2>/dev/null | grep public-address | awk '{print $2}' || echo "")
    COPILOT_IP=$(juju status copilot --format=yaml 2>/dev/null | grep public-address | awk '{print $2}' || echo "")
else
    warn_test "Juju not available, using localhost"
    API_IP="localhost"
    DASHBOARD_IP="localhost"
    COPILOT_IP="localhost"
fi

echo "   API: $API_IP:8000"
echo "   Dashboard: $DASHBOARD_IP:3000"
echo "   Copilot: $COPILOT_IP:8001"
echo ""

# Test 1: API Health Check
echo "🔬 Test 1: API Health Check"
if curl -sf "http://${API_IP}:8000/health" > /dev/null 2>&1; then
    pass_test "API health endpoint responds"
else
    fail_test "API health endpoint not responding"
fi

# Test 2: API Stats Endpoint
echo "🔬 Test 2: API Stats Endpoint"
if curl -sf "http://${API_IP}:8000/stats/firefox/stable" | grep -q "snap_name"; then
    pass_test "API stats endpoint returns valid JSON"
else
    fail_test "API stats endpoint not working"
fi

# Test 3: API Trending Endpoint
echo "🔬 Test 3: API Trending Endpoint"
if curl -sf "http://${API_IP}:8000/trending" | grep -q "trending"; then
    pass_test "API trending endpoint returns data"
else
    fail_test "API trending endpoint not working"
fi

# Test 4: Dashboard Accessibility
echo "🔬 Test 4: Dashboard Accessibility"
if curl -sf "http://${DASHBOARD_IP}:3000" > /dev/null 2>&1; then
    pass_test "Dashboard loads successfully"
else
    fail_test "Dashboard not accessible"
fi

# Test 5: Copilot Health Check
echo "🔬 Test 5: Copilot Health Check"
if curl -sf "http://${COPILOT_IP}:8001/health" > /dev/null 2>&1; then
    pass_test "Copilot health endpoint responds"
else
    fail_test "Copilot health endpoint not responding"
fi

# Test 6: Juju Status Check
echo "🔬 Test 6: Juju Deployment Status"
if command -v juju &> /dev/null; then
    ACTIVE_UNITS=$(juju status --format=tabular 2>/dev/null | grep -c "active/idle" || echo "0")
    if [ "$ACTIVE_UNITS" -ge 4 ]; then
        pass_test "All services are active in Juju ($ACTIVE_UNITS/4)"
    elif [ "$ACTIVE_UNITS" -gt 0 ]; then
        warn_test "Some services active in Juju ($ACTIVE_UNITS/4)"
    else
        fail_test "No services active in Juju"
    fi
else
    warn_test "Juju not available for status check"
fi

# Test 7: File Structure Check
echo "🔬 Test 7: Project Structure"
REQUIRED_FILES=(
    "services/collector/app.py"
    "services/api/main.py"
    "services/dashboard/package.json"
    "services/copilot/main.py"
    "kubernetes/bundle.yaml"
    "scripts/deploy.sh"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file (missing)"
        ((MISSING_FILES++))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    pass_test "All required files present"
else
    fail_test "$MISSING_FILES required files missing"
fi

# Test 8: Demo Data Generation
echo "🔬 Test 8: Demo Data Generation"
if python3 scripts/seed_demo.py > /dev/null 2>&1; then
    pass_test "Demo data generation works"
else
    fail_test "Demo data generation failed"
fi

# Test 9: Charm Build Test (if charmcraft available)
echo "🔬 Test 9: Charm Build Capability"
if command -v charmcraft &> /dev/null; then
    if cd charms/collector && charmcraft pack --dry-run > /dev/null 2>&1; then
        pass_test "Charms can be built"
    else
        fail_test "Charm build check failed"
    fi
    cd - > /dev/null
else
    warn_test "Charmcraft not available for build test"
fi

# Test 10: API CORS Check
echo "🔬 Test 10: API CORS Configuration"
CORS_HEADERS=$(curl -sI "http://${API_IP}:8000/health" | grep -i "access-control-allow-origin" || echo "")
if [ -n "$CORS_HEADERS" ]; then
    pass_test "API has CORS headers configured"
else
    warn_test "API CORS headers not detected (might be request-dependent)"
fi

echo ""
echo "📊 Test Results Summary"
echo "======================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All critical tests passed!${NC}"
    echo -e "${GREEN}SnapPulse is ready for demonstration.${NC}"
    echo ""
    echo "📋 Quick Demo Checklist:"
    echo "   ✅ curl http://$API_IP:8000/stats/firefox/stable"
    echo "   ✅ Open http://$DASHBOARD_IP:3000 in browser"
    echo "   ✅ Check juju status shows all services active"
    echo "   ✅ Demo data available via scripts/seed_demo.py"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some tests failed. Please check the issues above.${NC}"
    echo ""
    echo "🔧 Common fixes:"
    echo "   • Run: ./scripts/deploy.sh"
    echo "   • Check: juju status"
    echo "   • Debug: juju debug-log"
    exit 1
fi
