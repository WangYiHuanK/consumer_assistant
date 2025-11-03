# FastAPI application initialization for MVC architecture
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI application
app = FastAPI(
    title="Consumer Assistant API",
    description="Consumer Assistant application using FastAPI and MVC architecture",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import controllers to register routes
from app.controllers import *

# Import models for database operations
from app.models import *