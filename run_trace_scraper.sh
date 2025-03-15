#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Define the Python script path
PYTHON_SCRIPT="$SCRIPT_DIR/trace_scraper.py"

# Check if the sleep time argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <sleep_time_in_minutes>"
    exit 1
fi

# Convert sleep time to seconds
SLEEP_TIME=$(($1 * 60))

# Run indefinitely until manually stopped
while true; do
    echo -e "\n"
    echo "[LOG] Running Python script at $(date)"
    
    # Execute the Python script
    python3 "$PYTHON_SCRIPT"
    
    echo "[LOG] Sleeping for $1 minutes..."
    
    # Wait for the specified time
    sleep $SLEEP_TIME
done
