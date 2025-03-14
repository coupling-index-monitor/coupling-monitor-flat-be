from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import db_manager
# from app.core.scheduler import start_scheduler, stop_scheduler
from app.routers import traces_router, graphs_router, services_router, coupling_router

app = FastAPI(title="Graph Generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(traces_router, prefix="/api/traces", tags=["Traces"])
app.include_router(graphs_router, prefix="/api/graphs", tags=["Graphs"])
app.include_router(services_router, prefix="/api/services", tags=["Graphs"])
app.include_router(coupling_router, prefix="/api/coupling", tags=["Coupling"])


@app.on_event("startup")
async def startup():
    print("Starting up: Initializing database connection...")
    await db_manager.initialize_mongo()
    db_manager.initialize_neo4j()
    # start_scheduler()


# @app.on_event("shutdown")
# async def shutdown():
#     print("Shutting down: Closing database connection...")
#     await db_manager.close_mongo()
#     db_manager.close_neo4j()
#     # stop_scheduler()


@app.get("/")
async def root():
    return {"message": "Graph Generator API is running"}
