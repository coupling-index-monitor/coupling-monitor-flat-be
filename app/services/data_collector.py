import json
import os

import requests
from datetime import datetime, timezone, timedelta
from pymongo import errors
from app.core.database import db_manager
from app.core.config import settings

JAEGER_BASE_URL = settings.JAEGER_URL


def setup_indexes():
    """
    Ensure the required indexes are set up on the collections.
    """
    try:
        trace_collection = db_manager.get_trace_collection()
        trace_collection.create_index("traceID", unique=True)  # Enforce unique traceIDs
        trace_updates = db_manager.get_trace_updates_collection()
        trace_updates.create_index("service_name", unique=True)  # Enforce unique services
        print("Indexes created successfully.")
    except errors.PyMongoError as e:
        print(f"Error setting up indexes: {e}")


def fetch_services():
    """
    Fetch all available services from Jaeger.
    Returns:
        List of service names.
    """
    url = f"{JAEGER_BASE_URL}/services"
    try:
        response = requests.get(url)
        response.raise_for_status()
        services = response.json().get("data", [])
        return sorted([service for service in services if service != "jaeger-all-in-one"])
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch services: {e}")
        return []


def fetch_traces(service_name, start_us, end_us, limit=100):
    """
    Fetch traces for a specific service within a time range.
    """
    url = f"{JAEGER_BASE_URL}/traces"
    params = {
        "service": service_name,
        "start": int(start_us),  # Ensure integer timestamps
        "end": int(end_us),      # Ensure integer timestamps
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        if not isinstance(data, list):
            print(f"Unexpected API response for {service_name}: {data}")
            return []
        return data
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch traces for service '{service_name}': {e}")
        return []


def initialize_trace_updates(services):
    """
    Ensure every service has an entry in the trace_updates collection.
    """
    try:
        trace_updates = db_manager.get_trace_updates_collection()
        if trace_updates is None:
            raise RuntimeError("trace_updates collection is not initialized.")

        for service in services:
            trace_updates.update_one(
                {"service_name": service},
                {"$setOnInsert": {
                    "last_fetched_end_time_us": None
                }},
                upsert=True
            )
    except RuntimeError as e:
        print(f"Failed to initialize trace updates: {e}")


def fetch_and_store_traces(service_name):
    """
    Fetch and store traces for a specific service, handling sparse data and deduplication.
    """
    try:
        trace_collection = db_manager.get_trace_collection()
        trace_updates = db_manager.get_trace_updates_collection()

        # Retrieve last fetched end time in microseconds
        update_record = trace_updates.find_one({"service_name": service_name})
        last_end_time_us = update_record.get("last_fetched_end_time_us", None)

        # Default: Start from the last 5 minutes if no records exist
        if last_end_time_us is None:
            last_end_time_us = int((datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp() * 1e6)

        current_time_us = int(datetime.now(timezone.utc).timestamp() * 1e6)
        total_stored = 0
        total_skipped = 0
        consecutive_no_trace_batches = 0  # Counter for consecutive empty batches

        while last_end_time_us < current_time_us:
            next_end_time_us = min(last_end_time_us + (5 * 60 * 1e6), current_time_us)  # 5-minute batch
            traces = fetch_traces(service_name, start_us=last_end_time_us, end_us=next_end_time_us)

            if not traces:
                consecutive_no_trace_batches += 1
                print(f"No traces found for {service_name} in range {int(last_end_time_us)} - {int(next_end_time_us)}")
                if consecutive_no_trace_batches > 10:  # Allow 10 consecutive empty batches before stopping
                    print(f"Stopping early for {service_name}, no traces found in 10 consecutive ranges.")
                    break
                last_end_time_us = next_end_time_us + 1
                continue

            consecutive_no_trace_batches = 0  # Reset counter upon finding data
            for trace in traces:
                if "traceID" in trace:
                    try:
                        # Use upsert to avoid duplicates
                        result = trace_collection.update_one(
                            {"traceID": trace["traceID"]}, {"$set": trace}, upsert=True
                        )
                        if result.upserted_id:
                            total_stored += 1  # Trace inserted
                        else:
                            total_skipped += 1  # Trace already exists
                    except errors.PyMongoError as e:
                        print(f"Error inserting/updating trace {trace['traceID']} for {service_name}: {e}")

            # Update last_end_time_us for the next batch
            last_end_time_us = next_end_time_us + 1

            # Update progress in the trace_updates collection
            trace_updates.update_one(
                {"service_name": service_name},
                {"$set": {"last_fetched_end_time_us": last_end_time_us}}
            )

        print(
            f"Processed {total_stored + total_skipped} traces for service: {service_name}. "
            f"Inserted: {total_stored}, Skipped (duplicates): {total_skipped}."
        )
        return total_stored
    except Exception as e:
        print(f"Error fetching and storing traces for {service_name}: {e}")
        return 0


def fetch_and_store_traces_for_all_services():
    """
    Fetch and store traces for all services, updating the trace_updates collection.
    """
    services = fetch_services()
    if not services:
        print("No services available.")
        return

    # Initialize the trace_updates collection
    initialize_trace_updates(services)

    for service in services:
        print(f"Processing service: {service}")
        total_traces = fetch_and_store_traces(service)
        if total_traces == 0:
            print(f"No new traces for service: {service}. Moving to the next service.")


def get_traces_within_timerange(start_us, end_us, batch_size=100, page=1):
    """
    Retrieve traces from the MongoDB traces collection within a given time range and with pagination.
    Args:
        start_us (int): Start time in microseconds.
        end_us (int): End time in microseconds.
        batch_size (int): Number of traces to fetch per batch to avoid memory issues.
        page (int): Page number for pagination.
    Returns:
        list: List of trace documents within the specified time range.
    """
    print(f"Retrieving traces from {start_us} to {end_us}, page {page}")
    try:
        traces_collection = db_manager.get_trace_collection()
        skip_count = (page - 1) * batch_size

        # Query to fetch traces within the specified time range
        query = {
            "spans": {
                "$elemMatch": {
                    "startTime": {
                    "$gte": int(start_us),
                    "$lte": int(end_us)
                    }
                }
            }
        }

        # Fetch the total count of documents matching the query
        total_count = traces_collection.count_documents(query)
        total_pages = (total_count + batch_size - 1) // batch_size 
        print(f"Total traces: {total_count}, Total pages: {total_pages}")

        # Fetch the traces with pagination
        traces = list(traces_collection.find(query).skip(skip_count).limit(batch_size))
        print(f"Retrieved {len(traces)} traces from the database.")

        # Prepare the paginated response
        response = {
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": batch_size,
            "traces": traces
        }
        return response
    except Exception as e:
        print(f"Error fetching traces: {e}")
        return None

def get_traces_from_files_within_timerange(start_us, end_us):
    """
    Retrieve traces from the MongoDB traces collection within a given time range and with pagination.
    Args:
        start_us (int): Start time in microseconds.
        end_us (int): End time in microseconds.
    Returns:
        list: List of trace documents within the specified time range.
    """
    print(f"Retrieving traces from {start_us} to {end_us}")
    try:
        trace_files = [f for f in os.listdir(settings.TRACES_DIR) if f.endswith('.json') and f != 'offset.json']

        # Filter files within the specified time range based on their names
        filtered_files = [
            f for f in trace_files
            if int(f.split('_')[0]) >= int(start_us) and int(f.split('_')[1].split('.')[0]) <= int(end_us)
        ]

        # Initialize an empty list to store all traces
        all_traces = []

        for trace_file in filtered_files:
            with open(os.path.join(settings.TRACES_DIR, trace_file), 'r') as file:
                traces = json.load(file)
                all_traces.extend(traces)

        # Filter traces within the specified time range
        filtered_traces = [
            trace for trace in all_traces
            if any(int(start_us) <= span["startTime"] <= int(end_us) for span in trace["spans"])
        ]
        print(f"Retrieved {len(filtered_traces)} traces from the JSON files.")

        return filtered_traces
    except Exception as e:
        print(f"Error fetching traces: {e}")
        return None