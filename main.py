# Main entry point for running the FastAPI application
import uvicorn
from app import app
from app.configs.config import config

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )