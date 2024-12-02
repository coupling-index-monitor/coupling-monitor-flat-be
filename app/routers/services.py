from fastapi import APIRouter, HTTPException

from app.services.db_service import get_active_services_of_jaeger
from app.services.graph_processor import fetch_unique_services_from_neo4j

router = APIRouter()


@router.get("/active")
async def get_active_services():
    services = get_active_services_of_jaeger()
    return {"status": "success", "services": services}

@router.get("/recorded")
async def get_recorded_services():
    services  = fetch_unique_services_from_neo4j()
    return {"status": "success", "services": services}