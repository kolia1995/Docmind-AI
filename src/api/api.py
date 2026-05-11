from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.nlp.ingestion.content_ingestion import ContentIngestion
from src.storage.document_store import DocumentStore

app = FastAPI()
document_store = DocumentStore()

class TextRequest(BaseModel):
    text: str

class SearchRequest(BaseModel):
    query: str

class URLItem(BaseModel):
    url: str

@app.post("/search")
async def search_info(t: SearchRequest):

    if not t.query or not t.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")

    result = document_store.search(t.query.strip())

    return {"results": result}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    extractor = ContentIngestion(file=file)
    text = extractor.read()

    if not text or not str(text).strip():
        raise HTTPException(status_code=400, detail="Failed to extract text")

    document_store.save(text.strip())

    return {"status": "ok"}

@app.post("/url")
async def upload_url(item: URLItem):

    extractor = ContentIngestion(url=item.url)
    text = extractor.read()

    if not text or not str(text).strip():
        raise HTTPException(status_code=400, detail="Invalid or blocked URL")

    document_store.save(text.strip())

    return {"status": "ok"}

@app.post("/text")
async def upload_text(t: TextRequest):

    if not t.text or not t.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")

    document_store.save(t.text.strip())

    return {"status": "ok"}