

def calculate_ais(service_name, graph_data):
    """
    Calculate the Absolute Importance of a Service (AIS).
    
    :param service_name: Name of the target service (string).
    :param graph_data: Graph data in the described format (dict).
    :return: AIS value (integer).
    """
    if "graph" == None or "links" not in graph_data:
        raise ValueError("Invalid graph data format.")
    
    links = graph_data["links"]
    
    # Find all unique consumers (services that invoke the target service)
    consumers = set()
    for link in links:
        if link["target"] == service_name:
            consumers.add(link["source"])
    
    # Return the count of unique consumers
    return len(consumers)


def calculate_all_ais(graph_data):
    """
    Calculate the AIS for all services listed under the nodes object array.
    
    :param graph_data: Graph data in the described format (dict).
    :return: Dictionary with service names as keys and their AIS values as values.
    """
    if "nodes" not in graph_data:
        raise ValueError("Invalid graph data format.")
    
    all_ais = {}
    for node in graph_data["nodes"]:
        service_name = node["id"]
        all_ais[service_name] = calculate_ais(service_name, graph_data)
    
    return all_ais