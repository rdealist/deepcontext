# 🚀 Quick Start: RAG System

Get your local RAG (Retrieval-Augmented Generation) system running in 5 minutes!

## Prerequisites

- Python 3.8+
- 2GB RAM minimum
- 500MB disk space

## Step 1: Setup (2 minutes)

```bash
# Navigate to engine directory
cd engine

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this will download ~500MB)
pip install -r requirements.txt
```

## Step 2: Start the Server (30 seconds)

```bash
# Make sure you're in the engine directory with venv activated
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
[Engine] DBManager initialized
[Engine] FileScanner initialized
[Engine] Application started successfully
```

**Keep this terminal open!** Open a new terminal for the next steps.

## Step 3: Test the System (1 minute)

### Option A: Run Automated Tests

```bash
cd engine
source venv/bin/activate
python test_rag.py
```

Expected output:
```
✅ Step 1 PASSED: Database initialization works!
✅ Step 2 PASSED: File ingestion works!
✅ Step 3 PASSED: Vector search works!
🎉 All tests passed! Your RAG system is working correctly.
```

### Option B: Run Interactive Demo

```bash
python example.py
```

This creates sample documents and demonstrates the complete workflow.

## Step 4: Index Your Documents (1 minute)

### Using curl:

```bash
# Index your notes/documents folder
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/Users/YOUR_USERNAME/Documents/notes",
    "recursive": true
  }'
```

**Replace** `/Users/YOUR_USERNAME/Documents/notes` with your actual folder path!

Supported files: `.md`, `.txt`, `.markdown`

### Expected Response:

```json
{
  "success": true,
  "message": "Indexed 25 files (25 new, 0 updated, 0 skipped). Created 128 chunks.",
  "stats": {
    "total_files": 25,
    "new_files": 25,
    "updated_files": 0,
    "skipped_files": 0,
    "total_chunks": 128
  }
}
```

## Step 5: Search Your Documents (30 seconds)

```bash
# Search for information
curl "http://localhost:8000/api/search?q=your+search+query&limit=5"
```

### Example:

```bash
curl "http://localhost:8000/api/search?q=python+best+practices&limit=3"
```

### Expected Response:

```json
{
  "query": "python best practices",
  "results": [
    {
      "id": "notes/python.md#0_abc123",
      "content": "# Python Best Practices\n\nHere are some essential Python coding guidelines...",
      "file_name": "python.md",
      "file_path": "/Users/you/Documents/notes/python.md",
      "heading": "Python Best Practices",
      "score": 0.8542
    }
  ],
  "total": 3
}
```

## 🎉 You're Done!

Your RAG system is now running and ready to use!

---

## Common Commands Cheat Sheet

### Start Server
```bash
cd engine
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Check Health
```bash
curl http://localhost:8000/health
```

### Index Documents
```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/your/documents"}'
```

### Search
```bash
curl "http://localhost:8000/api/search?q=your+query&limit=5"
```

### Get Statistics
```bash
curl http://localhost:8000/api/stats
```

### Stop Server
Press `Ctrl+C` in the server terminal

---

## Visual Workflow

```
┌─────────────────────────────────────────────────┐
│  1. Your Documents (.md, .txt files)           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  2. POST /api/index                             │
│     → Scans files                               │
│     → Chunks content                            │
│     → Generates embeddings                      │
│     → Stores in LanceDB                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  3. GET /api/search?q=your+question             │
│     → Generates query embedding                 │
│     → Finds similar chunks                      │
│     → Returns ranked results                    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  4. Results with file names & content           │
└─────────────────────────────────────────────────┘
```

---

## Interactive API Documentation

Open in your browser:

**Swagger UI** (try all endpoints):
```
http://localhost:8000/docs
```

**ReDoc** (read documentation):
```
http://localhost:8000/redoc
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'lancedb'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "Path does not exist" error
- Use absolute paths: `/Users/username/Documents/notes`
- Check the path exists: `ls /your/path`
- Use forward slashes even on Windows

### No search results
1. Check if documents are indexed:
   ```bash
   curl http://localhost:8000/api/stats
   ```
2. If `document_count` is 0, run indexing again
3. Try a different search query

### Server won't start
- Check if port 8000 is already in use
- Try a different port:
  ```bash
  uvicorn main:app --reload --host 127.0.0.1 --port 8001
  ```

### Model download is slow
- First run downloads ~80MB model
- This is normal and happens once
- Model is cached in `./data/models/`

---

## What's Happening Under the Hood?

1. **Indexing**:
   - Files are split into ~500 character chunks
   - Each chunk is converted to a 384-dimensional vector
   - Vectors are stored in LanceDB (like SQLite, but for vectors)

2. **Searching**:
   - Your query is converted to the same 384-dimensional vector
   - LanceDB finds the most similar document vectors
   - Results are ranked by similarity score

3. **Model**:
   - Uses `all-MiniLM-L6-v2` from sentence-transformers
   - Runs locally (no API calls)
   - Fast and accurate for most use cases

---

## Next Steps

1. **Read the full docs**: `engine/README.md`
2. **API reference**: `engine/API_GUIDE.md`
3. **Integration guide**: `engine/IMPLEMENTATION_SUMMARY.md`
4. **Customize chunking**: Edit `engine/core/ingest.py`
5. **Change embedding model**: Edit `engine/db/manager.py`

---

## Need Help?

- Check server logs (in the terminal running uvicorn)
- Run tests: `python test_rag.py`
- Run demo: `python example.py`
- Look for `[Engine]`, `[DBManager]`, or `[Scanner]` log prefixes

---

**🎊 Happy Searching!**

Your local knowledge base is now searchable with semantic AI.