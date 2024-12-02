from fastapi import APIRouter
from typing import Optional
from fastapi import Query
from app.services.graph_processor import (get_graph_data_as_json)
from app.services.coupling_metrics_calculator import (
    calculate_ais, calculate_all_ais, calculate_ads, calculate_all_ads, calculate_adcs, calculate_scf)

router = APIRouter()

@router.get("/")
async def coupling_health():
    """
    Endpoint to fetch the dependency graph as JSON data.
    """
    try:
        graph_data = get_graph_data_as_json()
        return {"status": "success", "graph": graph_data}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}

@router.get("/absolute-importance-of")
async def get_absolute_importance_of_a_service(service: Optional[str] = Query(None)):
    """
    Endpoint to process the absolute importance of a service.
    """
    try:
        graph_data = get_graph_data_as_json()
        if service is not None:
            ais = calculate_ais(service, graph_data)
            return {"status": "success", "data": ais}
        else:
            all_ais = calculate_all_ais(graph_data)
            return {"status": "success", "data": all_ais}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}

@router.get("/absolute-dependence-of")
async def get_absolute_dependence_of_a_service(service: Optional[str] = Query(None)):
    """
    Endpoint to process the absolute dependence of a service.
    """
    try:
        graph_data = get_graph_data_as_json()
        if service is not None:
            ads = calculate_ads(service, graph_data)
            return {"status": "success", "data": ads}
        else:
            all_ads = calculate_all_ads(graph_data)
            return {"status": "success", "data": all_ads}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}

@router.get("/average-direct_connections")
async def get_average_directly_connected_services():
    """
    Endpoint to process the average absolute dependence of all services.
    """
    try:
        graph_data = get_graph_data_as_json()
        avg_ads = calculate_adcs(graph_data)
        return {"status": "success", "data": avg_ads}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}
    
@router.get("/overall-coupling-percentage")
async def get_overall_coupling_percentage():
    """
    Endpoint to process the overall coupling factor of the system.
    """
    try:
        graph_data = get_graph_data_as_json()
        coupling_factor = calculate_scf(graph_data) * 100
        return {"status": "success", "data": coupling_factor}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}