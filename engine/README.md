# DeepContext RAG Engine

A local Retrieval-Augmented Generation (RAG) engine built with FastAPI, LanceDB, and sentence-transformers.

## Features

- 🗄️ **Local Vector Database**: Uses LanceDB for persistent, file-based vector storage (like SQLite)
- 🧠 **Semantic Search**: Powered by sentence-transformers (all-MiniLM-L6-v2)
- 📄 **Smart Chunking**: Intelligent Markdown/text file chunking with overlap
- 🔄 **Incremental Indexing**: Only processes new or changed files
- 🚀 **FastAPI Backend**: RESTful API for easy integration

## Installation

1. **Create virtual environment:**
   ```bash
   cd engine
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### 1. Start the Server

```bash
cd engine
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Index Your Documents

```bash
curl -X POST "http://localhost:8000/api/index" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/your/documents",
    "recursive": true,
    "force_reindex": false
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Indexed 10 files (8 new, 2 updated, 0 skipped). Created 45 chunks.",
  "stats": {
    "total_files": 10,
    "new_files": 8,
    "updated_files": 2,
    "skipped_files": 0,
    "total_chunks": 45
  }
}
```

### 3. Search Your Documents

```bash
curl "http://localhost:8000/api/search?q=How%20does%20RAG%20work&limit=5"
```

**Response:**
```json
{
  "query": "How does RAG work",
  "results": [
    {
      "id": "docs/rag.md#0_a1b2c3d4",
      "content": "# Introduction to RAG\n\nRetrieval-Augmented Generation...",
      "file_name": "rag.md",
      "file_path": "/path/to/docs/rag.md",
      "heading": "Introduction to RAG",
      "score": 0.85
    }
  ],
  "total": 5
}
```

## API Endpoints

### Health Check
```
GET /health
```

Returns server status and document count.

### Index Documents
```
POST /api/index
```

**Request Body:**
- `path` (string, required): Directory path to index
- `recursive` (boolean, default: true): Scan subdirectories
- `force_reindex` (boolean, default: false): Reindex all files

**Supported File Types:** `.md`, `.txt`, `.markdown`

### Search Documents
```
GET /api/search?q={query}&limit={limit}
```

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (integer, default: 10, max: 100): Number of results

### Get Statistics
```
GET /api/stats
```

Returns database statistics including document count and model info.

## Testing

Run the comprehensive test suite:

```bash
cd engine
source venv/bin/activate
python test_rag.py
```

This tests:
1. ✅ Database initialization
2. ✅ File ingestion and chunking
3. ✅ Vector semantic search

## Architecture

### Components

```
engine/
├── main.py              # FastAPI application
├── db/
│   ├── __init__.py
│   └── manager.py       # DBManager class (LanceDB + embeddings)
├── core/
│   ├── __init__.py
│   └── ingest.py        # FileScanner & MarkdownChunker
├── api/                 # (Future: API routes)
└── requirements.txt
```

### How It Works

1. **Indexing Pipeline:**
   ```
   Files → Scan → Chunk → Embed → Store in LanceDB
   ```

2. **Search Pipeline:**
   ```
   Query → Embed → Vector Search → Ranked Results
   ```

### Document Schema

```python
{
  "id": str,              # Unique document ID
  "vector": List[float],  # 384-dimensional embedding
  "content": str,         # Text content
  "metadata": {
    "file_path": str,
    "file_name": str,
    "chunk_index": int,
    "heading": str,
    "file_size": int,
    "file_mtime": float
  }
}
```

## Configuration

### Environment Variables

- `DB_PATH`: Custom database path (default: `./data/lancedb`)
- `MODEL_CACHE`: Custom model cache directory (default: `./data/models`)

### Chunking Settings

Edit `core/ingest.py` to customize:

```python
MarkdownChunker(
    chunk_size=500,      # Target chunk size in characters
    overlap=50,          # Overlap between chunks
    min_chunk_size=100   # Minimum chunk size
)
```

## Advanced Usage

### Incremental Updates

The system automatically tracks file modifications:

```python
# First run: indexes all files
POST /api/index {"path": "/docs"}

# Modify a file...

# Second run: only indexes changed files
POST /api/index {"path": "/docs"}
```

### Force Reindex

To reindex everything:

```python
POST /api/index {
  "path": "/docs",
  "force_reindex": true
}
```

### Custom Embedding Model

Modify `db/manager.py`:

```python
db_manager = DBManager(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

## Troubleshooting

### Model Download Issues

On first run, the system downloads the embedding model (~80MB). If you encounter issues:

```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Out of Memory

For large document collections, adjust chunk size:

```python
# Smaller chunks = less memory per embedding
MarkdownChunker(chunk_size=300, overlap=30)
```

### Search Returns No Results

1. Check if documents are indexed:
   ```bash
   curl http://localhost:8000/api/stats
   ```

2. Verify database path is correct

3. Try force reindexing

## Performance Tips

- **Batch Indexing**: Index large directories in smaller batches
- **Chunk Size**: Balance between context (larger) and precision (smaller)
- **Search Limit**: Use smaller limits (5-10) for faster responses
- **Database Path**: Use SSD for better I/O performance

## Integration with Electron

The engine is designed to work with Electron via IPC:

```typescript
// In Electron main process
const { spawn } = require('child_process');

const python = spawn('python', ['-m', 'uvicorn', 'main:app'], {
  cwd: './engine'
});

// Then make HTTP requests from renderer
fetch('http://localhost:8000/api/search?q=example')
```

## License

Part of the DeepContext project.

## Next Steps

- [ ] Add support for more file types (PDF, DOCX)
- [ ] Implement document deletion by file path
- [ ] Add metadata filtering in search
- [ ] Support multiple embedding models
- [ ] Add batch upload endpoint
- [ ] Implement streaming search results