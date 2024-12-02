import networkx as nx
from networkx.readwrite import json_graph
from app.core.database import db_manager


def generate_weighted_graph_from_traces(traces):
    """
    Generate a weighted dependency graph from new traces.
    """
    graph = nx.DiGraph()

    for trace in traces:
        processes = trace.get("processes", {})
        spans = trace.get("spans", [])

        # Map process IDs to service names
        process_to_service = {pid: details["serviceName"] for pid, details in processes.items()}

        # Process spans to build relationships
        for span in spans:
            process_id = span.get("processID")
            parent_span_id = None
            for ref in span.get("references", []):
                if ref["refType"] == "CHILD_OF":
                    parent_span_id = ref["spanID"]
                    break

            if parent_span_id and process_id in process_to_service:
                child_service = process_to_service[process_id]
                parent_span = next((s for s in spans if s["spanID"] == parent_span_id), None)
                if parent_span and parent_span["processID"] in process_to_service:
                    parent_service = process_to_service[parent_span["processID"]]

                    # Skip self-loops
                    if parent_service != child_service:
                        # Update graph with weight
                        if graph.has_edge(parent_service, child_service):
                            graph[parent_service][child_service]["weight"] += 1
                        else:
                            graph.add_edge(parent_service, child_service, weight=1)

    return graph


def update_graph_in_neo4j(graph):
    """
    Update the dependency graph in Neo4j using the provided NetworkX graph.
    """
    with db_manager.neo4j_driver.session() as session:
        for edge in graph.edges(data=True):
            parent, child, attributes = edge
            weight = attributes.get("weight", 1)

            # Create or update nodes and relationships in Neo4j
            session.run("""
                MERGE (a:Service {name: $parent})
                MERGE (b:Service {name: $child})
                MERGE (a)-[r:CALLS]->(b)
                ON CREATE SET r.weight = $weight
                ON MATCH SET r.weight = r.weight + $weight
            """, parent=parent, child=child, weight=weight)


def fetch_graph_from_neo4j():
    """
    Fetch the dependency graph from Neo4j and return it as a NetworkX graph object.
    """
    graph = nx.DiGraph()

    try:
        with db_manager.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (a:Service)-[r:CALLS]->(b:Service)
                RETURN a.name AS parent, b.name AS child, r.weight AS weight
            """)

            for record in result:
                parent = record["parent"]
                child = record["child"]
                weight = record["weight"]
                graph.add_edge(parent, child, weight=weight)

    except Exception as e:
        print(f"Error fetching graph from Neo4j: {e}")

    return graph


def get_graph_data_as_json():
    """
    Retrieve the dependency graph as JSON-compatible data for API or frontend consumption.
    """
    graph = fetch_graph_from_neo4j()
    return json_graph.node_link_data(graph)
