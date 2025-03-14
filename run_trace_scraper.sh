#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Define the Python script path
PYTHON_SCRIPT="$SCRIPT_DIR/trace_scraper.py"

# Run indefinitely until manually stopped
while true; do
    echo "[LOG] Running Python script at $(date)"
    
    # Execute the Python script
    python3 "$PYTHON_SCRIPT"
    
    echo "[LOG] Sleeping for 15 minutes..."
    
    # Wait for 15 minutes (900 seconds)
    sleep 900
done
