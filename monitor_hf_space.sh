#!/bin/bash
# Monitor Hugging Face Space deployment status

echo "🔍 Monitoring HF Space: https://udaypratap-quiz-solver.hf.space/"
echo "Started at: $(date)"
echo ""

check_count=0
max_checks=60  # 10 minutes (10 sec intervals)

while [ $check_count -lt $max_checks ]; do
    echo -n "[$check_count/$max_checks] "
    
    # Check HTTP status
    status=$(curl -s -o /dev/null -w "%{http_code}" "https://udaypratap-quiz-solver.hf.space/" 2>&1)
    
    if [ "$status" = "200" ]; then
        echo "✅ SUCCESS! Space is live (HTTP 200)"
        echo ""
        echo "Testing health endpoint..."
        curl -s "https://udaypratap-quiz-solver.hf.space/" | python3 -m json.tool
        echo ""
        echo "🎉 Space is ready! You can now submit to examiner:"
        echo "   URL: https://udaypratap-quiz-solver.hf.space/solve"
        exit 0
    elif [ "$status" = "503" ]; then
        echo "⏳ Building... (HTTP 503)"
    else
        echo "⚠️  Status: HTTP $status"
    fi
    
    sleep 10
    check_count=$((check_count + 1))
done

echo ""
echo "⏰ Timeout: Space still not ready after 10 minutes"
echo "Check logs: https://huggingface.co/spaces/udaypratap/quiz-solver/logs"
