#!/bin/bash

# Test script for DesiLanguage API using curl
# This will generate lessons for all topics in Telugu and store them in the database

API_BASE="http://localhost:8000"
LANGUAGE="Telugu"
OUTPUT_DIR="./api_test_results"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "==================================================="
echo "DesiLanguage API Test - Telugu Lessons Generation"
echo "==================================================="
echo "Base URL: $API_BASE"
echo "Target Language: $LANGUAGE"
echo "Output Directory: $OUTPUT_DIR"
echo ""

# Test 1: Check API health
echo "1. Testing API health..."
curl -s "$API_BASE/" | jq '.' > "$OUTPUT_DIR/api_health.json"
if [ $? -eq 0 ]; then
    echo "   ✅ API is responding"
else
    echo "   ❌ API is not responding"
    exit 1
fi

# Test 2: Get available lesson topics
echo "2. Getting lesson topics..."
curl -s "$API_BASE/desi-lesson-topics" | jq '.' > "$OUTPUT_DIR/lesson_topics.json"
TOPICS=$(curl -s "$API_BASE/desi-lesson-topics" | jq -r '.[]')
TOPIC_COUNT=$(echo "$TOPICS" | wc -l)
echo "   Found $TOPIC_COUNT lesson topics"

# Test 3: Generate lessons for each topic
echo "3. Generating lessons for all topics..."
echo ""

COUNTER=1
SUCCESS_COUNT=0
FAILED_COUNT=0

# Store results summary
echo "{" > "$OUTPUT_DIR/test_summary.json"
echo "  \"test_info\": {" >> "$OUTPUT_DIR/test_summary.json"
echo "    \"start_time\": \"$(date -Iseconds)\"," >> "$OUTPUT_DIR/test_summary.json"
echo "    \"target_language\": \"$LANGUAGE\"," >> "$OUTPUT_DIR/test_summary.json"
echo "    \"total_topics\": $TOPIC_COUNT" >> "$OUTPUT_DIR/test_summary.json"
echo "  }," >> "$OUTPUT_DIR/test_summary.json"
echo "  \"results\": [" >> "$OUTPUT_DIR/test_summary.json"

while IFS= read -r topic; do
    if [ -n "$topic" ]; then
        echo "Lesson $COUNTER: $topic"
        
        # Create JSON payload
        PAYLOAD=$(jq -n --arg lang "$LANGUAGE" --arg topic "$topic" '{
            target_language: $lang,
            lesson_topic: $topic
        }')
        
        # Make API call with timeout
        START_TIME=$(date +%s)
        HTTP_CODE=$(curl -s -w "%{http_code}" \
            -X POST \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD" \
            --max-time 60 \
            "$API_BASE/generate-desi-lesson?save_to_db=true" \
            -o "$OUTPUT_DIR/lesson_${COUNTER}_response.json")
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        
        # Clean filename for lesson
        CLEAN_TOPIC=$(echo "$topic" | sed 's/[^a-zA-Z0-9]/_/g' | sed 's/__*/_/g' | sed 's/_$//')
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo "   ✅ Success (${DURATION}s) - Stored in database"
            mv "$OUTPUT_DIR/lesson_${COUNTER}_response.json" "$OUTPUT_DIR/lesson_${COUNTER}_${CLEAN_TOPIC}_SUCCESS.json"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            STATUS="success"
            ERROR_MSG=""
        else
            echo "   ❌ Failed (HTTP $HTTP_CODE) after ${DURATION}s"
            if [ -f "$OUTPUT_DIR/lesson_${COUNTER}_response.json" ]; then
                ERROR_MSG=$(jq -r '.detail // "Unknown error"' "$OUTPUT_DIR/lesson_${COUNTER}_response.json" 2>/dev/null || echo "Parse error")
                mv "$OUTPUT_DIR/lesson_${COUNTER}_response.json" "$OUTPUT_DIR/lesson_${COUNTER}_${CLEAN_TOPIC}_FAILED.json"
            else
                ERROR_MSG="No response received"
                echo "{\"error\": \"No response received\", \"http_code\": $HTTP_CODE}" > "$OUTPUT_DIR/lesson_${COUNTER}_${CLEAN_TOPIC}_FAILED.json"
            fi
            FAILED_COUNT=$((FAILED_COUNT + 1))
            STATUS="failed"
        fi
        
        # Add to summary (handle JSON comma separation)
        if [ $COUNTER -gt 1 ]; then
            echo "    ," >> "$OUTPUT_DIR/test_summary.json"
        fi
        echo "    {" >> "$OUTPUT_DIR/test_summary.json"
        echo "      \"lesson_number\": $COUNTER," >> "$OUTPUT_DIR/test_summary.json"
        echo "      \"topic\": \"$topic\"," >> "$OUTPUT_DIR/test_summary.json"
        echo "      \"status\": \"$STATUS\"," >> "$OUTPUT_DIR/test_summary.json"
        echo "      \"http_code\": $HTTP_CODE," >> "$OUTPUT_DIR/test_summary.json"
        echo "      \"duration_seconds\": $DURATION," >> "$OUTPUT_DIR/test_summary.json"
        echo "      \"error_message\": \"$ERROR_MSG\"" >> "$OUTPUT_DIR/test_summary.json"
        echo "    }" >> "$OUTPUT_DIR/test_summary.json"
        
        COUNTER=$((COUNTER + 1))
        echo ""
    fi
done <<< "$TOPICS"

# Close summary JSON
echo "  ]," >> "$OUTPUT_DIR/test_summary.json"
echo "  \"summary\": {" >> "$OUTPUT_DIR/test_summary.json"
echo "    \"end_time\": \"$(date -Iseconds)\"," >> "$OUTPUT_DIR/test_summary.json"
echo "    \"total_processed\": $((COUNTER - 1))," >> "$OUTPUT_DIR/test_summary.json"
echo "    \"successful\": $SUCCESS_COUNT," >> "$OUTPUT_DIR/test_summary.json"
echo "    \"failed\": $FAILED_COUNT," >> "$OUTPUT_DIR/test_summary.json"
echo "    \"success_rate\": $(echo "scale=2; $SUCCESS_COUNT * 100 / (($SUCCESS_COUNT + $FAILED_COUNT))" | bc -l)%" >> "$OUTPUT_DIR/test_summary.json"
echo "  }" >> "$OUTPUT_DIR/test_summary.json"
echo "}" >> "$OUTPUT_DIR/test_summary.json"

# Test 4: Verify database storage
echo "4. Verifying database storage..."
DB_LESSONS=$(curl -s "$API_BASE/desi-lessons" | jq '. | length')
echo "   Total lessons in database: $DB_LESSONS"

# Final summary
echo ""
echo "==================================================="
echo "TEST SUMMARY"
echo "==================================================="
echo "Total topics processed: $((COUNTER - 1))"
echo "Successful generations: $SUCCESS_COUNT"
echo "Failed generations: $FAILED_COUNT"
if [ $((SUCCESS_COUNT + FAILED_COUNT)) -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $SUCCESS_COUNT * 100 / (($SUCCESS_COUNT + $FAILED_COUNT))" | bc -l)
    echo "Success rate: ${SUCCESS_RATE}%"
fi
echo "Lessons stored in database: $DB_LESSONS"
echo ""
echo "Results saved to: $OUTPUT_DIR/"
echo "Summary file: $OUTPUT_DIR/test_summary.json"
echo "==================================================="