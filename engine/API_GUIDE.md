# RAG Engine API Usage Guide

Complete guide for using the DeepContext RAG Engine REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (local development).

---

## Endpoints

### 1. Health Check

Check if the server is running and get basic statistics.

**Endpoint:** `GET /health`

**Example Request:**
```bash
curl http://localhost:8000/health
```

**Example Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "document_count": 42
}
```

---

### 2. Hello World

Simple test endpoint.

**Endpoint:** `GET /api/hello`

**Example Request:**
```bash
curl http://localhost:8000/api/hello
```

**Example Response:**
```json
{
  "message": "Hello from Python Engine"
}
```

---

### 3. Index Documents

Index a directory of documents into the vector database.

**Endpoint:** `POST /api/index`

**Request Body:**
- `path` (string, required): Absolute or relative path to directory
- `recursive` (boolean, optional, default: true): Scan subdirectories
- `force_reindex` (boolean, optional, default: false): Reindex all files

**Supported File Types:** `.md`, `.txt`, `.markdown`

**Example Request (Basic):**
```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/username/Documents/notes"
  }'
```

**Example Request (Full Options):**
```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/username/Documents/notes",
    "recursive": true,
    "force_reindex": false
  }'
```

**Example Request (Force Reindex):**
```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/username/Documents/notes",
    "force_reindex": true
  }'
```

**Example Response:**
```json
{
  "success": true,
  "message": "Indexed 25 files (20 new, 3 updated, 2 skipped). Created 156 chunks.",
  "stats": {
    "total_files": 25,
    "new_files": 20,
    "updated_files": 3,
    "skipped_files": 2,
    "total_chunks": 156
  }
}
```

**Error Response (Path not found):**
```json
{
  "detail": "Path does not exist: /invalid/path"
}
```

---

### 4. Search Documents

Search for documents using semantic similarity.

**Endpoint:** `GET /api/search`

**Query Parameters:**
- `q` (string, required): Search query text
- `limit` (integer, optional, default: 10, range: 1-100): Max results

**Example Request (Basic):**
```bash
curl "http://localhost:8000/api/search?q=How+to+use+vector+databases"
```

**Example Request (With Limit):**
```bash
curl "http://localhost:8000/api/search?q=machine+learning&limit=5"
```

**Example Request (URL Encoded):**
```bash
curl "http://localhost:8000/api/search?q=$(python3 -c 'import urllib.parse; print(urllib.parse.quote("What is RAG?"))')&limit=3"
```

**Example Response:**
```json
{
  "query": "How to use vector databases",
  "results": [
    {
      "id": "docs/vector_db.md#0_a1b2c3d4",
      "content": "# Vector Databases\n\nVector databases store high-dimensional vectors...",
      "file_name": "vector_db.md",
      "file_path": "/Users/username/Documents/notes/vector_db.md",
      "heading": "Vector Databases",
      "score": 0.8542
    },
    {
      "id": "docs/embeddings.md#2_e5f6g7h8",
      "content": "## Using Vector Stores\n\nTo use a vector database effectively...",
      "file_name": "embeddings.md",
      "file_path": "/Users/username/Documents/notes/embeddings.md",
      "heading": "Using Vector Stores",
      "score": 0.7891
    }
  ],
  "total": 2
}
```

**Empty Results Response:**
```json
{
  "query": "nonexistent topic",
  "results": [],
  "total": 0
}
```

**Error Response (Empty Query):**
```json
{
  "detail": "Query parameter 'q' cannot be empty"
}
```

---

### 5. Get Statistics

Get database and system statistics.

**Endpoint:** `GET /api/stats`

**Example Request:**
```bash
curl http://localhost:8000/api/stats
```

**Example Response:**
```json
{
  "document_count": 156,
  "model_name": "all-MiniLM-L6-v2",
  "db_path": "/Users/username/projects/deepcontext/engine/data/lancedb"
}
```

---

## Complete Workflow Example

### Step 1: Check Server Health
```bash
curl http://localhost:8000/health
```

### Step 2: Index Your Documents
```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/username/Documents/knowledge-base",
    "recursive": true
  }'
```

### Step 3: Search for Information
```bash
curl "http://localhost:8000/api/search?q=python+best+practices&limit=5"
```

### Step 4: Check Statistics
```bash
curl http://localhost:8000/api/stats
```

---

## Using with JavaScript/TypeScript

### Fetch API Example

```javascript
// Index documents
async function indexDocuments(path) {
  const response = await fetch('http://localhost:8000/api/index', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      path: path,
      recursive: true,
      force_reindex: false
    })
  });
  
  const data = await response.json();
  console.log('Indexing complete:', data);
  return data;
}

// Search documents
async function searchDocuments(query, limit = 10) {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString()
  });
  
  const response = await fetch(`http://localhost:8000/api/search?${params}`);
  const data = await response.json();
  console.log('Search results:', data);
  return data;
}

// Usage
await indexDocuments('/Users/username/Documents/notes');
await searchDocuments('vector databases', 5);
```

### Axios Example

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// Index documents
async function indexDocuments(path) {
  const { data } = await axios.post(`${API_BASE}/api/index`, {
    path,
    recursive: true,
    force_reindex: false
  });
  return data;
}

// Search documents
async function searchDocuments(query, limit = 10) {
  const { data } = await axios.get(`${API_BASE}/api/search`, {
    params: { q: query, limit }
  });
  return data;
}

// Get stats
async function getStats() {
  const { data } = await axios.get(`${API_BASE}/api/stats`);
  return data;
}
```

---

## Using with Python

### Requests Library Example

```python
import requests

API_BASE = "http://localhost:8000"

# Index documents
def index_documents(path, recursive=True, force_reindex=False):
    response = requests.post(
        f"{API_BASE}/api/index",
        json={
            "path": path,
            "recursive": recursive,
            "force_reindex": force_reindex
        }
    )
    return response.json()

# Search documents
def search_documents(query, limit=10):
    response = requests.get(
        f"{API_BASE}/api/search",
        params={"q": query, "limit": limit}
    )
    return response.json()

# Get stats
def get_stats():
    response = requests.get(f"{API_BASE}/api/stats")
    return response.json()

# Usage
result = index_documents("/Users/username/Documents/notes")
print(f"Indexed {result['stats']['total_chunks']} chunks")

results = search_documents("vector databases", limit=5)
for r in results['results']:
    print(f"- {r['file_name']}: {r['content'][:100]}...")
```

### HTTPX Library Example (Async)

```python
import httpx
import asyncio

API_BASE = "http://localhost:8000"

async def index_documents(path, recursive=True):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/api/index",
            json={"path": path, "recursive": recursive}
        )
        return response.json()

async def search_documents(query, limit=10):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/api/search",
            params={"q": query, "limit": limit}
        )
        return response.json()

# Usage
async def main():
    result = await index_documents("/path/to/docs")
    print(result)
    
    search_result = await search_documents("RAG systems")
    print(search_result)

asyncio.run(main())
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters (e.g., empty query, invalid path)
- `500 Internal Server Error`: Server error (check logs)

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**1. Path Not Found**
```json
{
  "detail": "Path does not exist: /invalid/path"
}
```

**2. Empty Query**
```json
{
  "detail": "Query parameter 'q' cannot be empty"
}
```

**3. Invalid Limit**
```json
{
  "detail": "Limit must be between 1 and 100"
}
```

---

## Best Practices

### 1. Incremental Indexing

Don't use `force_reindex=true` unless necessary. The system automatically tracks file changes:

```bash
# First run: indexes everything
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/docs"}'

# Subsequent runs: only indexes new/modified files
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/docs"}'
```

### 2. Optimal Search Limits

Use smaller limits for faster responses:
- UI previews: `limit=5`
- Detailed results: `limit=10`
- Comprehensive search: `limit=20`

### 3. Query Formatting

Write natural language queries for better results:
- ✅ Good: "How do I implement authentication in FastAPI?"
- ❌ Bad: "auth fastapi"

### 4. Batch Indexing

For large document sets, index in batches:

```bash
# Index subdirectories separately
curl -X POST http://localhost:8000/api/index \
  -d '{"path": "/docs/backend", "recursive": false}'

curl -X POST http://localhost:8000/api/index \
  -d '{"path": "/docs/frontend", "recursive": false}'
```

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

**Swagger UI:**
```
http://localhost:8000/docs
```

**ReDoc:**
```
http://localhost:8000/redoc
```

These interfaces allow you to:
- Test all endpoints interactively
- See request/response schemas
- Try different parameters
- View error responses

---

## Troubleshooting

### Server Not Running

```bash
# Check if server is running
curl http://localhost:8000/health

# If not, start it
cd engine
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### No Search Results

1. Check if documents are indexed:
```bash
curl http://localhost:8000/api/stats
```

2. If document_count is 0, index your documents:
```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/your/docs/path"}'
```

### CORS Issues (Frontend)

If calling from a web frontend, ensure CORS is configured in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Metrics

Typical response times (MacBook Pro M1):

- Health check: ~5ms
- Index 100 files: ~30 seconds
- Search (limit=10): ~50ms
- Stats: ~5ms

Memory usage:
- Base: ~200MB (model loaded)
- Per 1000 documents: +50MB

---

## Next Steps

1. **Production Deployment**: Add authentication, rate limiting
2. **Monitoring**: Add logging and metrics
3. **Caching**: Cache frequently searched queries
4. **File Types**: Add PDF, DOCX support
5. **Filtering**: Add metadata filtering to search

---

## Support

For issues or questions:
- Check server logs: Look for `[Engine]`, `[DBManager]`, `[Scanner]` prefixes
- Enable verbose logging: Set `log_level="debug"` in uvicorn
- Run tests: `python test_rag.py`
