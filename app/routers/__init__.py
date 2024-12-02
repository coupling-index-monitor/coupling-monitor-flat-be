from app.routers.traces import router as traces_router
from app.routers.graphs import router as graphs_router
from app.routers.services import router as services_router
from app.routers.coupling import router as coupling_router

__all__ = ["traces_router", "graphs_router", "services_router", "coupling_router"]
