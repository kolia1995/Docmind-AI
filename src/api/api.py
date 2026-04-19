from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.nlp.processing import FileTextExtractor
from src.storage.document_store import DocumentStore
from src.core.logging import logger

class URLItem(BaseModel):
    url: str

class Text(BaseModel):
    text: str
    query: str | None = None

app = FastAPI()
document_store = DocumentStore()

@app.post("/search")
async def search_info(t: Text):
    logger.info(f"Search request received: {t.query}")
    if not t.query:
        logger.warning("Search query is empty")
        raise HTTPException(status_code=400, detail="Query is required")

    result = document_store.search(t.query)
    logger.info(f"Search completed for query: {t.query}")

    return {
        "results": result
    }

@app.post("/text")
async def upload_text(t: Text):
    logger.info("Text upload request received")
    if not t.text or not t.text.strip():
        logger.warning("Empty text received")
        raise HTTPException(status_code=400, detail="Empty text")

    document_store.save(t.text)
    logger.info("Text saved successfully")

    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"File upload request: {file.filename}")
    extractor = FileTextExtractor(file=file)

    text = extractor.read()

    if not text:
        logger.warning(f"Failed to extract text from file: {file.filename}")
        raise HTTPException(status_code=400, detail="Failed to extract text")

    document_store.save(text)
    logger.info(f"File processed and saved: {file.filename}")

    return {"status": "ok"}

@app.post("/url")
async def upload_url(item: URLItem):
    logger.info(f"URL upload request: {item.url}")
    extractor = FileTextExtractor(url=item.url)

    text = extractor.read()

    if not text:
        logger.warning(f"Failed to extract text from URL: {item.url}")
        raise HTTPException(status_code=400, detail="Invalid or blocked URL")

    document_store.save(text)
    logger.info(f"Content from URL saved: {item.url}")

    return {"status": "ok"}