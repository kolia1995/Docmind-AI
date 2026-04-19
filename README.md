# AI Document Search System

Enterprise-grade document intelligence platform with semantic search and AI-powered response generation.

## Core Features

- **Document Processing**: PDF, DOCX, TXT, HTML, URLs
- **Semantic Search**: Vector embeddings (MiniLM - 384D)
- **Classification**: 16-category text classifier (BART-MNLI)
- **Keyword Extraction**: Automated keyphrase detection (KeyBERT)
- **AI Responses**: Powered by Groq LLM with caching
- **Vector Database**: PostgreSQL with pgvector extension
- **Logging**: Auto-rotating file logs with monitoring

## Tech Stack

- **Backend**: FastAPI 0.104.1, Python 3.8+
- **Database**: PostgreSQL 12+ (pgvector extension)
- **ML Models**: Sentence-Transformers, HuggingFace Transformers
- **API**: Groq LLM for response generation
- **Infrastructure**: Connection pooling, async processing, auto-scaling logs

## Installation & Setup

### Requirements
- Python 3.8+, PostgreSQL 12+, 2GB disk space (models), Internet connection

### Quick Start (5 Steps)

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Configure environment:**
```bash
cp .env.example .env
# Edit .env: Add LLM_GROQ_KEY and database credentials
```

**3. Download ML models:**
```bash
python setup_models.py
# Downloads: miniLM (~130MB) + bart-mnli (~1.6GB)
# Or skip this - models auto-download on first run
```

**4. Initialize database:**
```bash
createdb document_db
psql -U postgres -d document_db -f database/schema.sql
psql -U postgres -d document_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**5. Start server:**
```bash
python main.py
```
API available at: **http://127.0.0.1:8000**

## API Reference

### Endpoints

| POST | `/text` | Index text document |
| POST | `/upload` | Upload file (PDF/DOCX/TXT/HTML) |
| POST | `/url` | Process URL content |
| POST | `/search` | Semantic search with filters |

### Examples

```bash
# Index text
curl -X POST "http://127.0.0.1:8000/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text"}'

# Search
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query"}'
```

## Project Organization

```
src/api/         → FastAPI endpoints
src/core/        → Logging, settings, model loader
src/nlp/         → Text processing (classifier, keyphrase)
src/llm/         → Groq LLM integration
src/storage/     → Document store (PostgreSQL + vectors)
database/        → Schema (SQL)
models/          → ML models (auto-downloaded)
logs/            → Application logs (logs/app.log)
```

## Configuration

- **Environment**: `.env` (copy from `.env.example`)
- **Logging**: `logs/app.log` (auto-rotating, 5MB per file)
- **Models**: Auto-download on first run or via `python setup_models.py`
- **Settings**: `src/core/settings.py` (load from .env)

## Architecture

**Document Pipeline:**
Text → Extract → Embeddings → Keywords → Classification → Store → Search

**Key Components:**
1. **API Layer**: FastAPI endpoints for document operations
2. **NLP Pipeline**: Text extraction, embedding generation, classification
3. **Vector Store**: PostgreSQL with pgvector for semantic search
4. **LLM Integration**: Groq API with response caching
5. **Logging**: Auto-rotating logs for monitoring and debugging

## Strengths

✓ **Semantic Search** - Not just keyword matching, true meaning-based search  
✓ **Multi-Format** - Handles PDF, DOCX, TXT, HTML, URLs  
✓ **Production-Ready** - Error handling, logging, connection pooling  
✓ **Scalable** - Vector DB enables fast similarity search  
✓ **Modular** - Clean separation of concerns (API, NLP, Storage, LLM)  

## � Models & Repository Size

### Why Models Are Not Committed
Models are **NOT included in the Git repository** (see `.gitignore`):
- **miniLM** model: ~130MB
- **bart-mnli** model: ~1.6GB
- **Total:** ~1.7GB of large files

Including them would make the repository huge and slow to clone.

### How Models Work

**Option 1: Pre-download (Recommended for production)**
```bash
python setup_models.py
```
- Downloads models once
- Stores in `./models/` directory
- Fast startup (~1 second)

**Option 2: Auto-download on first run**
- Models auto-download when first needed
- First startup takes 1-2 minutes
- Subsequent startups are fast (<1 second)
- Stored in `./models/` directory

The system uses `src/core/model_loader.py` which:
1. Checks if model exists locally
2. Uses local model if available
3. Auto-downloads from HuggingFace if not found
4. Caches loaded models in memory for performance

### Repository Size
- **With pre-downloaded models:** ~1.7GB
- **Without models (Git clone):** ~2MB
- **Models auto-download:** ~2MB + downloads as needed

**Recommended:** Use `python setup_models.py` before production deployment.

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| **ModuleNotFoundError** | Run `pip install -r requirements.txt` |
| **PostgreSQL Connection Error** | Check PostgreSQL is running and `.env` credentials. See `logs/app.log` for details |
| **Models Not Found** | Run `python setup_models.py` or wait for auto-download |
| **Tesseract Not Found** | `choco install tesseract` (Windows) or install via package manager |
| **Groq API Error** | Verify `LLM_GROQ_KEY` in `.env` is correct. Check `logs/app.log` for error details |
| **First run is slow** | Models downloading (1-2 min), only happens first time. Check `logs/app.log` for progress |
| **Server won't start** | Check `logs/app.log` for error messages. Ensure port 8000 is available |
| **Can't find logs** | Logs stored in `logs/app.log` (created automatically on first run) |

### How to Debug Using Logs

**Location:** `logs/app.log`

1. **Check for errors:**
   ```bash
   # Find all errors
   Get-Content logs/app.log | Select-String "ERROR"
   
   # Find warnings
   Get-Content logs/app.log | Select-String "WARNING"
   ```

2. **Follow live updates:**
   ```bash
   Get-Content logs/app.log -Wait
   ```

3. **Check recent activity:**
   ```bash
   Get-Content logs/app.log -Tail 100
   ```

## 📄 License

Open source for research and development.

---

**Ready to process documents intelligently!** 🚀
