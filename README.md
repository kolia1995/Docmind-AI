# AI Document Search System

FastAPI service for indexing documents and searching by vector similarity.

## Features

- Index raw text through `/text`
- Upload and index files through `/upload`
- Fetch and index document URLs through `/url`
- Search indexed documents through `/search`
- Extract text from PDF, DOC/DOCX, TXT, and HTML files
- Classify text into 16 categories with `facebook/bart-large-mnli`
- Create 384D embeddings with `sentence-transformers/all-MiniLM-L6-v2`
- Store text, category, and embedding in PostgreSQL with `pgvector`

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Enable `pgvector` in PostgreSQL:

```bash
psql -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Current database connection is configured in `database/db.py`:

```text
dbname=postgres
user=postgres
password=postgres
host=localhost
port=5332
```

Start the server:

```bash
python main.py
```

API runs at:

```text
http://127.0.0.1:8000
```

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/text` | Index text |
| POST | `/upload` | Upload and index a file |
| POST | `/url` | Fetch and index URL content |
| POST | `/search` | Search indexed documents |

## Examples

Index text:

```bash
curl -X POST "http://127.0.0.1:8000/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text"}'
```

Search:

```bash
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query"}'
```

## Project Structure

```text
main.py                  App entry point
database/                Database connection, queries, schema
src/api/                 FastAPI routes
src/core/                Settings, logging, model loading
src/llm/                 Groq provider
src/nlp/                 Classification and content ingestion
src/storage/             Document storage and search
models/                  Model placeholder directory
```

## Notes

- The `documents` table is created from `database/schema.sql`.
- Models are loaded from HuggingFace when first used.
- Uploaded files are limited to 5MB in `ContentIngestion`.
- OCR for scanned PDFs uses `pytesseract`.
- Search returns the best matching stored text.

## License

Open source for research and development.
