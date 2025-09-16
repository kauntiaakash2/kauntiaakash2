"""
Main FastAPI application for Smart Classroom Timetable Scheduler
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.utils.database import connect_to_mongo, close_mongo_connection
from app.routes import teachers, classrooms, subjects, batches, timetable, auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up Smart Classroom Timetable Scheduler...")
    try:
        await connect_to_mongo()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="A comprehensive backend API for managing smart classroom timetable scheduling",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Smart Classroom Timetable Scheduler API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "classroom-scheduler-api"}


# Include routers with API prefix
api_prefix = settings.api_v1_str

# Authentication routes (no prefix for login)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# API routes with authentication
app.include_router(teachers.router, prefix=f"{api_prefix}/teachers", tags=["Teachers"])
app.include_router(classrooms.router, prefix=f"{api_prefix}/classrooms", tags=["Classrooms"])
app.include_router(subjects.router, prefix=f"{api_prefix}/subjects", tags=["Subjects"])
app.include_router(batches.router, prefix=f"{api_prefix}/batches", tags=["Batches"])
app.include_router(timetable.router, prefix=f"{api_prefix}/timetable", tags=["Timetable"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )