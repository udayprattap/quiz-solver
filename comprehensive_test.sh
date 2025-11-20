#!/bin/bash
# Comprehensive Test Suite for Quiz Solver Evaluation

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         TDS Quiz Solver - Comprehensive Test Suite          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Timestamp: $(date)"
echo "Testing: Local Server (http://localhost:8000)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local expected_status="$2"
    local response_file="$3"
    
    echo -n "Test: $test_name ... "
    
    status=$(cat "$response_file" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null || echo "error")
    
    if [[ "$status" == "$expected_status" ]]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (expected: $expected_status, got: $status)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "════════════════════════════════════════════════════════════════"
echo "TEST 1: Health Check Endpoint"
echo "════════════════════════════════════════════════════════════════"
response=$(curl -s http://localhost:8000/)
echo "$response" > /tmp/test1_response.json
echo "Response:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
run_test "Health Check" "ready" "/tmp/test1_response.json"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "TEST 2: Authentication - Invalid Secret"
echo "════════════════════════════════════════════════════════════════"
response=$(curl -s -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24ds3000019@ds.study.iitm.ac.in",
    "secret": "wrong_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }')
echo "$response" > /tmp/test2_response.json
echo "Response:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
run_test "Invalid Auth Rejection" "error" "/tmp/test2_response.json"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "TEST 3: Valid Solve Request (Background Processing)"
echo "════════════════════════════════════════════════════════════════"
response=$(curl -s -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24ds3000019@ds.study.iitm.ac.in",
    "secret": "banana",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }')
echo "$response" > /tmp/test3_response.json
echo "Response:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
run_test "Valid Request Accepted" "processing" "/tmp/test3_response.json"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "TEST 4: Environment Configuration Check"
echo "════════════════════════════════════════════════════════════════"
python3 << 'PYEOF'
from config import EMAIL, SECRET, PIPE_TOKEN, settings_summary

print(f"✓ EMAIL: {EMAIL}")
print(f"✓ SECRET: {'***' + SECRET[-3:] if SECRET else 'NOT SET'}")
print(f"✓ PIPE_TOKEN: {'Configured (' + PIPE_TOKEN[:20] + '...)' if PIPE_TOKEN else 'NOT SET'}")
print(f"\nSettings Summary:")
import json
print(json.dumps(settings_summary(redact=False), indent=2))
PYEOF
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "TEST 5: LLM Helper Availability"
echo "════════════════════════════════════════════════════════════════"
python3 << 'PYEOF'
try:
    from llm_helper import analyze_question_with_llm, parse_complex_question
    import config
    
    if config.PIPE_TOKEN:
        print("✓ LLM Helper: Available")
        print("✓ PIPE_TOKEN: Configured")
        print("✓ Integration: Ready")
        print("\nLLM will be used for:")
        print("  - Complex natural language questions")
        print("  - Multi-step reasoning")
        print("  - Ambiguous question interpretation")
        print("  - Fallback to rule-based if LLM fails")
    else:
        print("⚠ PIPE_TOKEN not configured")
        print("⚠ Will use rule-based logic only")
except Exception as e:
    print(f"✗ LLM Helper Error: {e}")
PYEOF
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "TEST 6: Dependencies Check"
echo "════════════════════════════════════════════════════════════════"
python3 << 'PYEOF'
import sys

required = {
    'fastapi': '0.104.1',
    'playwright': '1.40.0',
    'pandas': '2.1.3',
    'pdfplumber': '0.10.3',
    'openai': '1.54.0'
}

print("Checking required packages:")
for package, expected_version in required.items():
    try:
        if package == 'playwright':
            import playwright
            version = playwright.__version__
        elif package == 'fastapi':
            import fastapi
            version = fastapi.__version__
        elif package == 'pandas':
            import pandas
            version = pandas.__version__
        elif package == 'pdfplumber':
            import pdfplumber
            version = pdfplumber.__version__
        elif package == 'openai':
            import openai
            version = openai.__version__
        
        print(f"  ✓ {package}: {version}")
    except ImportError:
        print(f"  ✗ {package}: NOT INSTALLED")
    except AttributeError:
        print(f"  ✓ {package}: Installed (version check failed)")
PYEOF
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "TEST 7: Server Logs Review"
echo "════════════════════════════════════════════════════════════════"
if [ -f test_server.log ]; then
    echo "Recent server logs:"
    tail -20 test_server.log | grep -E "(INFO|ERROR|WARNING|BACKGROUND)" || echo "No relevant logs yet"
else
    echo "⚠ Server log file not found"
fi
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo "Total Tests: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ ALL TESTS PASSED - READY FOR EVALUATION           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next Steps:"
    echo "  1. Wait for HF Space rebuild (~8 minutes)"
    echo "  2. Test HF Space: curl https://udaypratap-quiz-solver.hf.space/"
    echo "  3. Submit endpoint: https://udaypratap-quiz-solver.hf.space/solve"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ SOME TESTS FAILED - REVIEW ERRORS ABOVE           ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo "Timestamp: $(date)"
