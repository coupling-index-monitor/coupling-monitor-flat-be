def calculate_for_all_services(graph_data, calculate_func):
    """
    Calculate the AIS for all services listed under the nodes object array.
    
    :param graph_data: Graph data in the described format (dict).
    :param calculate_func: Function to calculate any configured metric for a given service.
    :return: Dictionary with service names as keys and their AIS values as values.
    """
    if "nodes" not in graph_data:
        raise ValueError("Invalid graph data format.")
    
    result = {}
    for node in graph_data["nodes"]:
        service_name = node["id"]
        result[service_name] = calculate_func(service_name, graph_data)
    
    return result

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
    ais = len(consumers)


def calculate_all_ais(graph_data):
    """
    Calculate the AIS for all services listed under the nodes object array.
    
    :param graph_data: Graph data in the described format (dict).
    :return: Dictionary with service names as keys and their AIS values as values.
    """
    return calculate_for_all_services(graph_data, calculate_ais)


def calculate_ads(service_name, graph_data):
    """
    Calculate the Absolute Dependence of a Service (ADS).
    
    :param service_name: Name of the target service (string).
    :param graph_data: Graph data in the described format (dict).
    :return: ADS value (integer).
    """
    if "graph" == None or "links" not in graph_data:
        raise ValueError("Invalid graph data format.")
    
    links = graph_data["links"]
    
    # Find all unique dependencies (services that the target service invokes)
    dependencies = set()
    for link in links:
        if link["source"] == service_name:
            dependencies.add(link["target"])
    
    # Return the count of unique dependencies
    return len(dependencies)

def calculate_all_ads(graph_data):
    """
    Calculate the ADS for all services listed under the nodes object array.
    
    :param graph_data: Graph data in the described format (dict).
    :return: Dictionary with service names as keys and their ADS values as values.
    """
    return calculate_for_all_services(graph_data, calculate_ads)

def calculate_adcs(graph_data):
    """
    Calculate the Average Number of Directly Connected Services (ADCS).
    
    :param graph_data: Graph data in the described format (dict).
    :return: ADCS value (float).
    """
    if "graph" == None or "nodes" not in graph_data:
        raise ValueError("Invalid graph data format.")
        
    nodes = graph_data["nodes"]
    services = [node["id"] for node in nodes]

    # Compute ADS for all services
    total_ads = 0
    for service in services:
        total_ads += calculate_ads(service, graph_data)

    # Compute the average ADS (ADCS)
    adcs = total_ads / len(services) if services else 0
    return adcs

def calculate_scf(graph_data):
    """
    Calculate the Service Coupling Factor (SCF).
    
    :param graph_data: Graph data in the described format (dict).
    :return: SCF value (float).
    """
    if "graph" not in graph_data or "nodes" not in graph_data or "links" not in graph_data:
        raise ValueError("Invalid graph data format.")
    
    nodes = graph_data["nodes"]
    links = graph_data["links"]
    
    # Total number of services (nodes)
    num_services = len(nodes)
    
    # Sum of all dependencies (edges in the graph)
    sc = len(links)  # Each link represents a dependency
    
    # Maximum possible directed edges (N^2 - N)
    max_edges = num_services ** 2 - num_services
    
    # Calculate SCF
    scf = sc / max_edges if max_edges > 0 else 0
    return scf
