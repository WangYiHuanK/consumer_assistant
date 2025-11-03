# Controllers package for handling business logic and routes
from app import app
from fastapi import APIRouter

# Create router
router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint for the Consumer Assistant API"""
    return {"message": "Welcome to Consumer Assistant API"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Register routes with main app
app.include_router(router)