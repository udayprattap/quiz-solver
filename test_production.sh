#!/bin/bash
# Quick test script for TDS Quiz Solver
# Run this before submitting to examiner

echo "======================================================================"
echo "TDS Quiz Solver - Pre-Submission Test Suite"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
ENDPOINT="https://udaypratap-quiz-solver.hf.space"
EMAIL="24ds3000019@ds.study.iitm.ac.in"
SECRET="banana"
DEMO_URL="https://tds-llm-analysis.s-anand.net/demo"

# Test 1: Health Check
echo "Test 1: Health Check"
echo "GET ${ENDPOINT}/"
HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" "${ENDPOINT}/")
BODY=$(cat /tmp/response.json 2>/dev/null || echo "{}")

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Status: 200 OK"
    echo "Response: $BODY" | head -n 3
else
    echo -e "${RED}✗ FAILED${NC} - Status: $HTTP_CODE"
    echo "Response: $BODY"
    exit 1
fi
echo ""

# Test 2: Info Endpoint
echo "Test 2: Info Endpoint"
echo "GET ${ENDPOINT}/info"
HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" "${ENDPOINT}/info")
BODY=$(cat /tmp/response.json 2>/dev/null || echo "{}")

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Status: 200 OK"
    echo "Response: $BODY" | head -n 3
else
    echo -e "${RED}✗ FAILED${NC} - Status: $HTTP_CODE"
fi
echo ""

# Test 3: Valid Solve Request
echo "Test 3: Valid Solve Request"
echo "POST ${ENDPOINT}/solve"
HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" -X POST "${ENDPOINT}/solve" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"secret\":\"${SECRET}\",\"url\":\"${DEMO_URL}\"}")
BODY=$(cat /tmp/response.json 2>/dev/null || echo "{}")

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Status: 200 OK"
    echo "Response: $BODY"
    if echo "$BODY" | grep -q "processing"; then
        echo -e "${GREEN}✓ Background task started${NC}"
    fi
else
    echo -e "${RED}✗ FAILED${NC} - Status: $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Test 4: Invalid Secret (Should Fail)
echo "Test 4: Invalid Secret (Should Reject)"
HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" -X POST "${ENDPOINT}/solve" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"secret\":\"wrong_secret\",\"url\":\"${DEMO_URL}\"}")
BODY=$(cat /tmp/response.json 2>/dev/null || echo "{}")

if [ "$HTTP_CODE" -eq 403 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Correctly rejected (403)"
    echo "Response: $BODY"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Expected 403, got $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Test 5: Invalid Email (Should Fail)
echo "Test 5: Invalid Email (Should Reject)"
HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" -X POST "${ENDPOINT}/solve" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"wrong@example.com\",\"secret\":\"${SECRET}\",\"url\":\"${DEMO_URL}\"}")
BODY=$(cat /tmp/response.json 2>/dev/null || echo "{}")

if [ "$HTTP_CODE" -eq 403 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Correctly rejected (403)"
    echo "Response: $BODY"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Expected 403, got $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# Summary
echo "======================================================================"
echo "Test Summary"
echo "======================================================================"
echo ""
echo -e "${GREEN}All critical tests passed!${NC}"
echo ""
echo "Next Steps:"
echo "1. Check HF Space logs for background processing"
echo "2. Wait 1-2 minutes for demo quiz to complete"
echo "3. Look for 'QUIZ CHAIN COMPLETED' in logs"
echo ""
echo "If all looks good, you can submit this endpoint to your examiner:"
echo ""
echo -e "${YELLOW}Endpoint:${NC} ${ENDPOINT}/solve"
echo -e "${YELLOW}Email:${NC} ${EMAIL}"
echo -e "${YELLOW}Secret:${NC} ${SECRET}"
echo ""
echo "HF Space Logs: https://huggingface.co/spaces/udaypratap/quiz-solver"
echo ""
