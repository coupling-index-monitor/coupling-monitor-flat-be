from fastapi import APIRouter, HTTPException

from app.services import get_all_traces_from_mongo, get_traces_by_parent_service

router = APIRouter()


@router.get("")
async def get_traces():
    traces = get_all_traces_from_mongo()
    return {"status": "success", "traces": traces}


@router.get("services/{service}")
async def get_trace(service: str):
    traces = get_traces_by_parent_service(service)
    return {"status": "success", "traces": traces}
