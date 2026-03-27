from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import motor.motor_asyncio
import asyncio
from contextlib import asynccontextmanager

from .config import config
from .api import pages, templates, comments
from .services.monitoring_service import MonitoringService
from .utils.logger import logger

# Global variables
db_client = None
monitoring_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_client, monitoring_service
    
    # Connect to MongoDB
    db_client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGODB_URL)
    app.db = db_client[config.DATABASE_NAME]
    
    # Start monitoring service
    monitoring_service = MonitoringService(app.db)
    asyncio.create_task(monitoring_service.start_monitoring())
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    if monitoring_service:
        await monitoring_service.stop_monitoring()
    
    if db_client:
        db_client.close()
    
    logger.info("Application shutdown")

# Create FastAPI app
app = FastAPI(
    title="Facebook Comment Assistant",
    description="Automated comment management for Facebook Pages",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pages.router)
app.include_router(templates.router)
app.include_router(comments.router)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
