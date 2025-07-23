#!/bin/bash

# Simple API test script for DesiLanguage API using curl
# This will generate lessons for all topics in the specified language and store them in the database

# Usage: ./test_api_simple.sh [LANGUAGE]
# Example: ./test_api_simple.sh Kannada

API_BASE="http://localhost:8000"
LANGUAGE="${1:-Telugu}"  # Use first argument or default to Telugu
OUTPUT_DIR="./api_test_results_${LANGUAGE,,}"  # Convert to lowercase for directory

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "==================================================="
echo "DesiLanguage API Test - $LANGUAGE Lessons Generation"
echo "==================================================="
echo "Base URL: $API_BASE"
echo "Target Language: $LANGUAGE"
echo "Output Directory: $OUTPUT_DIR"
echo ""

# Test 1: Check API health
echo "1. Testing API health..."
curl -s "$API_BASE/" -o "$OUTPUT_DIR/api_health.json"
if [ $? -eq 0 ]; then
    echo "   ✅ API is responding"
    cat "$OUTPUT_DIR/api_health.json"
    echo ""
else
    echo "   ❌ API is not responding"
    exit 1
fi

# Test 2: Get available lesson topics with themes
echo "2. Getting lesson topics and themes..."
curl -s "$API_BASE/desi-lesson-topics" -o "$OUTPUT_DIR/lesson_topics.json"
curl -s "$API_BASE/desi-lessons-with-themes" -o "$OUTPUT_DIR/lessons_with_themes.json"
echo "   Topics and themes retrieved and saved to lesson files"

# Parse lesson titles from Lessons_n_themes.txt file
if [ ! -f "Lessons_n_themes.txt" ]; then
    echo "Error: Lessons_n_themes.txt file not found!"
    echo "Please ensure the file exists in the current directory."
    exit 1
fi

# Extract lesson titles from the structured file
echo "   Parsing lesson titles from Lessons_n_themes.txt..."
TOPICS=()
while IFS= read -r line; do
    if [[ $line == "Lesson Title:"* ]]; then
        # Extract title after "Lesson Title: "
        title="${line#Lesson Title: }"
        TOPICS+=("$title")
    fi
done < "Lessons_n_themes.txt"

# Verify we found topics
if [ ${#TOPICS[@]} -eq 0 ]; then
    echo "Error: No lesson titles found in Lessons_n_themes.txt"
    echo "Please check the file format."
    exit 1
fi

echo "   Found ${#TOPICS[@]} lesson titles from Lessons_n_themes.txt"

# Test 3: Generate lessons for each topic
echo "3. Generating lessons for all topics..."
echo ""

COUNTER=1
SUCCESS_COUNT=0
FAILED_COUNT=0

# Start summary file
echo "Test started at: $(date)" > "$OUTPUT_DIR/test_summary.txt"
echo "Target Language: $LANGUAGE" >> "$OUTPUT_DIR/test_summary.txt"
echo "Total Topics: ${#TOPICS[@]}" >> "$OUTPUT_DIR/test_summary.txt"
echo "" >> "$OUTPUT_DIR/test_summary.txt"

for topic in "${TOPICS[@]}"; do
    echo "Lesson $COUNTER: $topic"
    
    # Clean filename
    CLEAN_TOPIC=$(echo "$topic" | sed 's/[^a-zA-Z0-9]/_/g' | sed 's/__*/_/g' | sed 's/_$//')
    
    # Create JSON payload
    cat > "$OUTPUT_DIR/payload_$COUNTER.json" << EOF
{
    "target_language": "$LANGUAGE",
    "lesson_topic": "$topic"
}
EOF
    
    # Make API call with timeout
    START_TIME=$(date +%s)
    HTTP_CODE=$(curl -s -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d @"$OUTPUT_DIR/payload_$COUNTER.json" \
        --max-time 120 \
        "$API_BASE/generate-desi-lesson?save_to_db=true" \
        -o "$OUTPUT_DIR/lesson_${COUNTER}_response.json")
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ Success (${DURATION}s) - Stored in database"
        mv "$OUTPUT_DIR/lesson_${COUNTER}_response.json" "$OUTPUT_DIR/lesson_${COUNTER}_${CLEAN_TOPIC}_SUCCESS.json"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "Lesson $COUNTER: $topic - SUCCESS (${DURATION}s)" >> "$OUTPUT_DIR/test_summary.txt"
    else
        echo "   ❌ Failed (HTTP $HTTP_CODE) after ${DURATION}s"
        mv "$OUTPUT_DIR/lesson_${COUNTER}_response.json" "$OUTPUT_DIR/lesson_${COUNTER}_${CLEAN_TOPIC}_FAILED.json"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "Lesson $COUNTER: $topic - FAILED (HTTP $HTTP_CODE, ${DURATION}s)" >> "$OUTPUT_DIR/test_summary.txt"
        
        # Show error details
        echo "   Error details:"
        cat "$OUTPUT_DIR/lesson_${COUNTER}_${CLEAN_TOPIC}_FAILED.json" | head -3
    fi
    
    # Clean up payload file
    rm -f "$OUTPUT_DIR/payload_$COUNTER.json"
    
    COUNTER=$((COUNTER + 1))
    echo ""
    
    # Small delay to not overwhelm the API
    sleep 2
done

# Test 4: Verify database storage
echo "4. Verifying database storage..."
curl -s "$API_BASE/desi-lessons" -o "$OUTPUT_DIR/database_lessons.json"
echo "   Database lessons saved to database_lessons.json"

# Check database count by language
curl -s "$API_BASE/desi-lessons/language/$LANGUAGE" -o "$OUTPUT_DIR/${LANGUAGE,,}_lessons_in_db.json"
echo "   $LANGUAGE lessons in database saved to ${LANGUAGE,,}_lessons_in_db.json"

# Final summary
TOTAL_PROCESSED=$((COUNTER - 1))
echo "" >> "$OUTPUT_DIR/test_summary.txt"
echo "=== FINAL SUMMARY ===" >> "$OUTPUT_DIR/test_summary.txt"
echo "Test completed at: $(date)" >> "$OUTPUT_DIR/test_summary.txt"
echo "Total topics processed: $TOTAL_PROCESSED" >> "$OUTPUT_DIR/test_summary.txt"
echo "Successful generations: $SUCCESS_COUNT" >> "$OUTPUT_DIR/test_summary.txt"
echo "Failed generations: $FAILED_COUNT" >> "$OUTPUT_DIR/test_summary.txt"

if [ $TOTAL_PROCESSED -gt 0 ]; then
    SUCCESS_RATE=$((SUCCESS_COUNT * 100 / TOTAL_PROCESSED))
    echo "Success rate: ${SUCCESS_RATE}%" >> "$OUTPUT_DIR/test_summary.txt"
fi

echo ""
echo "==================================================="
echo "TEST SUMMARY"
echo "==================================================="
echo "Total topics processed: $TOTAL_PROCESSED"
echo "Successful generations: $SUCCESS_COUNT"
echo "Failed generations: $FAILED_COUNT"
if [ $TOTAL_PROCESSED -gt 0 ]; then
    SUCCESS_RATE=$((SUCCESS_COUNT * 100 / TOTAL_PROCESSED))
    echo "Success rate: ${SUCCESS_RATE}%"
fi
echo ""
echo "All results saved to: $OUTPUT_DIR/"
echo "Summary: $OUTPUT_DIR/test_summary.txt"
echo "Database lessons: $OUTPUT_DIR/database_lessons.json"
echo "$LANGUAGE lessons: $OUTPUT_DIR/${LANGUAGE,,}_lessons_in_db.json"
echo ""
echo "Usage: ./test_api_simple.sh [LANGUAGE]"
echo "Examples:"
echo "  ./test_api_simple.sh Kannada"
echo "  ./test_api_simple.sh Hindi"
echo "  ./test_api_simple.sh Tamil"
echo "=================================================="