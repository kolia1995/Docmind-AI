import uvicorn
from src.api.api import app

if __name__ == "__main__":
    uvicorn.run("src.api.api:app", host="127.0.0.1", port=8000)