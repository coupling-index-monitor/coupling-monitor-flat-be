import networkx as nx
from networkx.readwrite import json_graph
from app.utils.constants import WEIGHT_TYPES

def generate_graph_with_edge_weights(traces, wedge_weight_type):
    """
    Generate a weighted dependency graph from new traces with co-execution edge weights.
    """
    graph = nx.DiGraph()
    edge_weights = {}
    execution_sets = {}

    for trace in traces:
        trace_id = trace.get("traceID") 
        processes = trace.get("processes", {})
        spans = trace.get("spans", [])

        # Map process IDs to service names
        process_to_service = {pid: details["serviceName"] for pid, details in processes.items()}

        # Process spans to build relationships & Track which executions include each service
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

                    add_trace_to_execution_sets(execution_sets, trace_id, parent_service)

                    if parent_service != child_service: # Skip self-loops 
                        add_trace_to_execution_sets(execution_sets, trace_id, child_service)
                        
                        if (parent_service, child_service) in edge_weights:
                            edge_weights[(parent_service, child_service)]["count"] += 1
                            edge_weights[(parent_service, child_service)]["latencies"].append(duration)
                        else:
                            edge_weights[(parent_service, child_service)] = {"count": 1, "latencies": [duration]}

    # Assign weights to graph edges based on the chosen wedge_weight_type
    graph = assign_edge_weights(wedge_weight_type, graph, edge_weights, execution_sets)

    # Calculate node weights and add nodes to the graph
    nodes = calculate_node_weights(graph)
    graph.add_nodes_from(nodes.items())

    return json_graph.node_link_data(graph, edges="edges")

def calculate_node_weights(graph):
    nodes = {}
    for service_node in graph.nodes:
        #calculates the number of nodes invoke the service_node 
        consumers = set(graph.predecessors(service_node))
        absolute_importance = len(consumers)

        #calculates the number of nodes the service_node invokes
        dependencies = set(graph.successors(service_node))
        absolute_dependence = len(dependencies)

        nodes[service_node] = {
            "absolute_importance": absolute_importance,
            "absolute_dependence": absolute_dependence
        }
    return nodes

def assign_edge_weights(wedge_weight_type, graph, edge_weights, execution_sets):
    """
    Assigns weights to the edges of a graph based on the specified weight type.

    Returns:
    networkx.Graph: The graph with updated edge weights and additional attributes:
                    - "latency(ms)": The average latency of the edge in milliseconds.
                    - "frequency": The frequency count of the edge.
                    - "co_execution": The co-execution weight of the edge.
    """
    for (source, destination), data in edge_weights.items():
        avg_latency = round(sum(data["latencies"]) / len(data["latencies"]), 4)
        co_execution_weight = compute_jaccard_similarity(execution_sets, source, destination)

        # Assign edge weights
        if wedge_weight_type == WEIGHT_TYPES.Frequency.value:
            graph.add_edge(source, destination, weight=data["count"])
        elif wedge_weight_type == WEIGHT_TYPES.Latency.value:
            graph.add_edge(source, destination, weight=avg_latency)
        elif wedge_weight_type == WEIGHT_TYPES.CoExecution.value:
            graph.add_edge(source, destination, weight=co_execution_weight)

        # Store additional attributes
        graph[source][destination]["latency(ms)"] = avg_latency
        graph[source][destination]["frequency"] = data["count"]
        graph[source][destination]["co_execution"] = co_execution_weight
    return graph

def add_trace_to_execution_sets(execution_sets, trace_id, parent_service):
    if parent_service not in execution_sets:
        execution_sets[parent_service] = set()
    execution_sets[parent_service].add(trace_id)

def compute_jaccard_similarity(execution_sets, source, destination):
    """
    Compute the Jaccard similarity between two sets of executions.

    The Jaccard similarity is defined as the size of the intersection divided by the size of the union of the sets.

    Args:
        execution_sets (dict): A dictionary where keys are nodes and values are sets of executions.
        source (str): The source node for which to compute the similarity.
        destination (str): The destination node for which to compute the similarity.

    Returns:
        float: The Jaccard similarity coefficient between the source and destination nodes, rounded to 4 decimal places.

    Example:
        execution_sets = {
            'A': {'exec1', 'exec2', 'exec3'},
            'B': {'exec2', 'exec3', 'exec4'}
        }
        similarity = compute_jaccard_similarity(execution_sets, 'A', 'B')
        print(similarity)  # Output: 0.5
    """
    executions_source = execution_sets.get(source, set())
    executions_destination = execution_sets.get(destination, set())
    intersection_size = len(executions_source & executions_destination)
    union_size = len(executions_source | executions_destination)
    co_execution_weight = round(intersection_size / union_size if union_size > 0 else 0, 4)
    return co_execution_weight
