import uvicorn
from src.api.api import app
from src.core.logging import logger

if __name__ == "__main__":
    logger.info("Starting application...")
    logger.info("Starting server on http://127.0.0.1:8000")
    uvicorn.run("src.api.api:app", host="127.0.0.1", port=8000)