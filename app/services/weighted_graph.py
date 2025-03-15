import networkx as nx
from networkx.readwrite import json_graph

from app.utils.constants import WEIGHT_TYPES

def generate_graph_with_edge_weights(traces, weight_type):
    """
    Generate a weighted dependency graph from new traces with co-execution edge weights.
    """
    graph = nx.DiGraph()
    edge_weights = {}
    execution_sets = {}

    for trace in traces:
        trace_id = trace.get("traceID")  # Use traceID as execution identifier
        processes = trace.get("processes", {})
        spans = trace.get("spans", [])

        # Map process IDs to service names
        process_to_service = {pid: details["serviceName"] for pid, details in processes.items()}

        # Track which executions include each service
        for span in spans:
            service_name = process_to_service.get(span["processID"])
            if service_name:
                if service_name not in execution_sets:
                    execution_sets[service_name] = set()
                execution_sets[service_name].add(trace_id)  # Add trace execution ID

        # Process spans to build relationships
        for span in spans:
            process_id = span.get("processID")
            duration = span.get("duration", 0) / 1_000  # Convert to milliseconds
            parent_span_id = None
            for ref in span.get("references", []):
                if ref["refType"] == "CHILD_OF":
                    parent_span_id = ref["spanID"]
                    break

            child_service = None
            parent_service = None
            if (parent_span_id) and (process_id in process_to_service):
                child_service = process_to_service[process_id]
                parent_span = next((s for s in spans if s["spanID"] == parent_span_id), None)
                if (parent_span) and (parent_span["processID"] in process_to_service):
                    parent_service = process_to_service[parent_span["processID"]]

                    # Skip self-loops
                    if parent_service != child_service:
                        if (parent_service, child_service) in edge_weights:
                            edge_weights[(parent_service, child_service)]["count"] += 1
                            edge_weights[(parent_service, child_service)]["latencies"].append(duration)
                        else:
                            edge_weights[(parent_service, child_service)] = {"count": 1, "latencies": [duration]}

    # Assign weights to graph edges based on the chosen weight_type
    for (source, destination), data in edge_weights.items():
        avg_latency = round(sum(data["latencies"]) / len(data["latencies"]), 4)
        co_execution_weight = compute_jaccard_similarity(execution_sets, source, destination)

        # Assign edge weights
        if weight_type == WEIGHT_TYPES.Frequency.value:
            graph.add_edge(source, destination, weight=data["count"])
        elif weight_type == WEIGHT_TYPES.Latency.value:
            graph.add_edge(source, destination, weight=avg_latency)
        elif weight_type == WEIGHT_TYPES.CoExecution.value:
            graph.add_edge(source, destination, weight=co_execution_weight)

        # Store additional attributes
        graph[source][destination]["latency"] = avg_latency
        graph[source][destination]["frequency"] = data["count"]
        graph[source][destination]["co_execution"] = co_execution_weight

    return json_graph.node_link_data(graph, edges="edges")

def compute_jaccard_similarity(execution_sets, source, destination):
    executions_source = execution_sets.get(source, set())
    executions_destination = execution_sets.get(destination, set())
    intersection_size = len(executions_source & executions_destination)
    union_size = len(executions_source | executions_destination)
    co_execution_weight = round(intersection_size / union_size if union_size > 0 else 0, 4)
    return co_execution_weight
