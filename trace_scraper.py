#!/usr/bin/env python

import os
import json
import requests
import time

JAEGER_TRACES_ENDPOINT = "http://localhost:16686/jaeger/api/traces"

# Ensure traces and offset.json are stored inside the traces directory
TRACES_DIR = os.path.join(os.getcwd(), "traces")
OFFSET_FILE = os.path.join(TRACES_DIR, "offset.json")
TRACE_LIMIT = 20000  # Max limit per Jaeger request


def log(message):
    """ Simple logging function for better visibility. """
    print(f"[LOG] {message}")


def get_traces(start_time, end_time):
    """ Retrieves all traces within the given time range using pagination. """
    all_traces = []
    current_start_time = start_time

    log(f"Fetching traces from {start_time} to {end_time}...")

    while True:
        params = {
            "start": current_start_time,
            "end": end_time,
            "limit": TRACE_LIMIT
        }

        try:
            response = requests.get(JAEGER_TRACES_ENDPOINT, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            log(f"Error fetching traces: {err}")
            return all_traces

        response_data = json.loads(response.text)
        traces = response_data.get("data", [])

        if not traces:
            log("No more traces found within the specified range.")
            break  # Stop if no more traces are returned

        all_traces.extend(traces)

        # Sort traces by startTime in ascending order
        traces.sort(key=lambda trace: trace["spans"][0]["startTime"])

        # Update the new start time to the last retrieved trace's startTime
        current_start_time = traces[-1]["spans"][0]["startTime"]

        log(f"Fetched {len(traces)} traces. Continuing from {current_start_time}...")

        if len(traces) < TRACE_LIMIT:
            break  # Stop if we received less than the limit (i.e., no more traces left)

    log(f"Total traces retrieved: {len(all_traces)}")
    return all_traces


def write_traces(traces):
    """ Write traces to a JSON file inside the 'traces' directory. """
    if not traces:
        log("No traces received. Nothing to write.")
        return

    # Ensure traces directory exists
    if not os.path.exists(TRACES_DIR):
        os.makedirs(TRACES_DIR)

    # Sort traces by startTime in ascending order
    traces.sort(key=lambda trace: trace["spans"][0]["startTime"])

    # Get the last trace's startTime and traceID
    last_trace = traces[-1]
    last_start_time = last_trace["spans"][0]["startTime"]
    last_trace_id = last_trace["traceID"]

    # Save traces in a file named after the last trace's startTime
    trace_file_path = os.path.join(TRACES_DIR, f"{last_start_time}.json")
    with open(trace_file_path, 'w') as trace_file:
        json.dump(traces, trace_file, indent=4)

    log(f"Traces saved in {trace_file_path}")

    # Update offset.json inside the traces directory
    offset_data = {}
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, 'r') as offset_file:
            offset_data = json.load(offset_file)

    offset_data[str(last_start_time)] = last_trace_id

    with open(OFFSET_FILE, 'w') as offset_file:
        json.dump(offset_data, offset_file, indent=4)

    log(f"Updated offset.json in {OFFSET_FILE} with last trace ID: {last_trace_id}")


def main():
    """ Fetches traces from the last recorded timestamp or the last 15 minutes. """
    log("Starting trace fetch process...")

    # Get the current time in microseconds
    end_time = int(time.time() * 1_000_000)

    # Ensure traces directory exists before reading/writing offset.json
    if not os.path.exists(TRACES_DIR):
        os.makedirs(TRACES_DIR)

    # Get last recorded start time from offset.json
    last_start_time = None
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, 'r') as offset_file:
            offset_data = json.load(offset_file)
            if offset_data:
                last_start_time = max(map(int, offset_data.keys()))  # Get latest start time

    # If we have a last recorded start time, use it; otherwise, get last 15 minutes
    if last_start_time:
        start_time = last_start_time
        log(f"Resuming from last recorded start time: {start_time}")
    else:
        start_time = end_time - (15 * 60 * 1_000_000)  # 15 minutes earlier
        log("No previous records found. Fetching last 15 minutes of traces.")

    log(f"Fetching traces from {start_time} to {end_time}")

    traces = get_traces(start_time, end_time)
    write_traces(traces)

if __name__ == "__main__":
    main()