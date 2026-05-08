from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.nlp.ingestion.content_ingestion import ContentIngestion
from src.storage.document_store import DocumentStore

class URLItem(BaseModel):
    url: str

class Text(BaseModel):
    text: str
    query: str | None = None

app = FastAPI()
document_store = DocumentStore()

@app.post("/search")
async def search_info(t: Text):
    if not t.query:
        raise HTTPException(status_code=400, detail="Query is required")

    result = document_store.search(t.query)

    return {
        "results": result
    }

@app.post("/text")
async def upload_text(t: Text):
    if not t.text or not t.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")

    document_store.save(t.text)

    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    extractor = ContentIngestion(file=file)

    text = extractor.read()

    if not text:
        raise HTTPException(status_code=400, detail="Failed to extract text")

    document_store.save(text)

    return {"status": "ok"}

@app.post("/url")
async def upload_url(item: URLItem):
    extractor = ContentIngestion(url=item.url)

    text = extractor.read()

    if not text:
        raise HTTPException(status_code=400, detail="Invalid or blocked URL")

    document_store.save(text)

    return {"status": "ok"}