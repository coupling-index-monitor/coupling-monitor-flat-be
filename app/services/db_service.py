from pymongo.collection import Collection
from app.core.database import db_manager
from app.services import fetch_services


def get_all_traces_from_mongo():
    """
    Retrieve all traces from the 'trace' collection.
    Returns:
        list: A list of all trace documents.
    """
    try:
        trace_collection: Collection = db_manager.get_trace_collection()
        traces = list(trace_collection.find({}, {"_id": 0}))  # Exclude MongoDB's `_id` field
        print(f"Retrieved {len(traces)} traces.")
        return traces
    except Exception as e:
        print(f"Error fetching all traces: {e}")
        return []


def get_traces_by_parent_service(parent_service_name):
    """
    Retrieve traces where the parent service matches the given name.
    Args:
        parent_service_name (str): The name of the parent service.
    Returns:
        list: A list of traces matching the criteria.
    """
    try:
        trace_collection: Collection = db_manager.get_trace_collection()
        matching_traces = []

        # Iterate over traces to find those with the given parent service
        traces = trace_collection.find({}, {"_id": 0})  # Fetch all traces without `_id`
        for trace in traces:
            processes = trace.get("processes", {})
            spans = trace.get("spans", [])

            # Map process IDs to service names
            process_to_service = {pid: details["serviceName"] for pid, details in processes.items()}

            for span in spans:
                # Check for parent span references (CHILD_OF)
                parent_span_id = None
                for ref in span.get("references", []):
                    if ref["refType"] == "CHILD_OF":
                        parent_span_id = ref["spanID"]
                        break

                # If a parent span exists, find its service name
                if parent_span_id:
                    parent_span = next((s for s in spans if s["spanID"] == parent_span_id), None)
                    if parent_span and parent_span.get("processID") in process_to_service:
                        parent_service = process_to_service[parent_span["processID"]]
                        if parent_service == parent_service_name:
                            matching_traces.append(trace)
                            break  # No need to check further spans for this trace

        print(f"Found {len(matching_traces)} traces with parent service '{parent_service_name}'.")
        return matching_traces
    except Exception as e:
        print(f"Error fetching traces by parent service '{parent_service_name}': {e}")
        return []


def get_active_services_of_jaeger():
    return fetch_services()
