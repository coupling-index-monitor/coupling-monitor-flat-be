from fastapi import APIRouter, HTTPException

from app.services.db_service import get_all_services

router = APIRouter()


@router.get("")
async def get_services():
    services = get_all_services()
    return {"status": "success", "services": services}
