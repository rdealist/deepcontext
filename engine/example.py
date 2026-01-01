#!/usr/bin/env python3
"""
Example script demonstrating the complete RAG workflow.

This script shows how to:
1. Initialize the database
2. Index documents
3. Perform semantic search

Run this script to see the RAG system in action!
"""

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ingest import FileScanner
from db.manager import DBManager


def create_sample_documents(base_dir: str) -> str:
    """
    Create sample markdown documents for demonstration.

    Args:
        base_dir: Base directory to create documents in

    Returns:
        Path to the created documents directory
    """
    docs_dir = os.path.join(base_dir, "sample_docs")
    os.makedirs(docs_dir, exist_ok=True)

    # Document 1: About RAG
    with open(os.path.join(docs_dir, "rag_intro.md"), "w", encoding="utf-8") as f:
        f.write("""# What is RAG?

Retrieval-Augmented Generation (RAG) is an AI framework that combines information retrieval with text generation.

## How It Works

RAG systems work in two main phases:

### 1. Indexing Phase
- Documents are broken into chunks
- Each chunk is converted to a vector embedding
- Embeddings are stored in a vector database

### 2. Query Phase
- User query is converted to an embedding
- Similar document chunks are retrieved
- Retrieved context is used to generate responses

## Benefits

- **Reduced Hallucinations**: Grounded in real data
- **Up-to-date Information**: Easy to update knowledge base
- **Transparent**: Can show source documents
- **Cost-effective**: No need to retrain models

## Use Cases

RAG is perfect for:
- Question answering systems
- Chatbots with domain knowledge
- Document search and summarization
- Customer support automation
""")

    # Document 2: About Vector Databases
    with open(
        os.path.join(docs_dir, "vector_databases.md"), "w", encoding="utf-8"
    ) as f:
        f.write("""# Vector Databases Explained

Vector databases are specialized database systems optimized for storing and querying high-dimensional vectors.

## What are Vectors?

Vectors are arrays of numbers that represent semantic meaning. For example:
- "cat" might be [0.2, 0.8, 0.1, ...]
- "dog" might be [0.3, 0.7, 0.15, ...]

Similar concepts have similar vectors!

## Popular Vector Databases

### LanceDB
- **Type**: Embedded (file-based)
- **Best for**: Local applications, Electron apps
- **Advantages**: No server needed, like SQLite

### Pinecone
- **Type**: Cloud-hosted
- **Best for**: Production applications
- **Advantages**: Fully managed, scalable

### Weaviate
- **Type**: Self-hosted or cloud
- **Best for**: Open-source projects
- **Advantages**: Feature-rich, GraphQL API

### Chroma
- **Type**: Embedded
- **Best for**: Prototyping, small projects
- **Advantages**: Simple API, Python-first

## Why Vector Databases?

Traditional databases search for exact matches. Vector databases find semantic similarity:
- "automobile" matches "car"
- "happy" matches "joyful"
- "python programming" matches "coding in Python"
""")

    # Document 3: About Embeddings
    with open(os.path.join(docs_dir, "embeddings.md"), "w", encoding="utf-8") as f:
        f.write("""# Understanding Embeddings

Embeddings are dense vector representations of text that capture semantic meaning.

## How Embeddings Work

Embedding models are neural networks trained to convert text into vectors:

1. **Input**: "The cat sat on the mat"
2. **Processing**: Neural network layers
3. **Output**: [0.1, -0.3, 0.8, ..., 0.2] (384 dimensions)

## Sentence Transformers

Sentence Transformers is a popular Python library for generating embeddings:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Hello world")
```

## Popular Models

### all-MiniLM-L6-v2
- **Size**: 80MB
- **Dimensions**: 384
- **Speed**: Very fast
- **Use case**: General purpose

### all-mpnet-base-v2
- **Size**: 420MB
- **Dimensions**: 768
- **Speed**: Moderate
- **Use case**: Higher quality

### paraphrase-multilingual
- **Dimensions**: 768
- **Speed**: Moderate
- **Use case**: Multiple languages

## Vector Similarity

To find similar texts, we compare their vectors:

- **Cosine Similarity**: Measures angle between vectors
- **Euclidean Distance**: Measures straight-line distance
- **Dot Product**: Measures alignment

Similar meanings → Similar vectors → High similarity score!
""")

    # Document 4: About FastAPI
    with open(os.path.join(docs_dir, "fastapi.md"), "w", encoding="utf-8") as f:
        f.write("""# FastAPI for RAG Systems

FastAPI is a modern, fast web framework perfect for building RAG APIs.

## Why FastAPI?

- **Fast**: Built on Starlette and Pydantic
- **Async**: Native async/await support
- **Type Safety**: Automatic validation with Pydantic
- **Documentation**: Auto-generated OpenAPI docs

## Example RAG Endpoint

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100)
):
    results = db_manager.search(q, limit)
    return {"results": results}
```

## Best Practices

1. **Use Pydantic Models**: Type-safe request/response
2. **Add CORS**: Enable frontend access
3. **Handle Errors**: Proper exception handling
4. **Add Logging**: Track performance
5. **Use Async**: For I/O operations
""")

    print(f"✅ Created 4 sample documents in: {docs_dir}")
    return docs_dir


def main():
    """Main demonstration function."""
    print("\n" + "=" * 70)
    print("  🚀 RAG System Complete Workflow Demo")
    print("=" * 70 + "\n")

    # Use temporary directory for this demo
    with tempfile.TemporaryDirectory() as tmpdir:
        print("📁 Step 1: Creating sample documents...")
        docs_dir = create_sample_documents(tmpdir)
        print()

        # Initialize database
        print("🗄️  Step 2: Initializing LanceDB...")
        db_path = os.path.join(tmpdir, "demo_db")
        db_manager = DBManager(db_path=db_path)
        print(f"   ✓ Database initialized at: {db_path}")
        print(f"   ✓ Using model: {db_manager.model_name}")
        print()

        # Index documents
        print("📚 Step 3: Indexing documents...")
        scanner = FileScanner(db_manager)
        stats = scanner.ingest_directory(docs_dir, recursive=True)

        print(f"   ✓ Files indexed: {stats['total_files']}")
        print(f"   ✓ Chunks created: {stats['total_chunks']}")
        print(f"   ✓ Database size: {db_manager.get_document_count()} documents")
        print()

        # Perform searches
        print("🔍 Step 4: Performing semantic searches...")
        print()

        test_queries = [
            "What is RAG and how does it work?",
            "Tell me about vector databases",
            "How do embeddings capture meaning?",
            "Which database should I use for local development?",
            "What are the benefits of using RAG?",
        ]

        for i, query in enumerate(test_queries, 1):
            print(f'Query {i}: "{query}"')
            print("-" * 70)

            results = db_manager.search(query, limit=3)

            if results:
                for j, result in enumerate(results[:2], 1):  # Show top 2 results
                    metadata = result["metadata"]
                    content = result["content"]

                    # Truncate content for display
                    preview = content[:200] + "..." if len(content) > 200 else content

                    print(f"\n   Result {j}:")
                    print(f"   📄 File: {metadata.get('file_name', 'Unknown')}")
                    print(f"   📍 Section: {metadata.get('heading', 'N/A')}")
                    print(f"   📊 Score: {result.get('score', 'N/A')}")
                    print(f"   📝 Preview: {preview}")
            else:
                print("   ❌ No results found")

            print()

        # Test incremental update
        print("=" * 70)
        print("🔄 Step 5: Testing incremental update...")
        print()

        # Run indexing again without changes
        stats2 = scanner.ingest_directory(docs_dir, recursive=True)
        print(f"   ✓ Second run: {stats2['skipped_files']} files skipped (no changes)")
        print(f"   ✓ New chunks: {stats2['total_chunks']}")
        print()

        # Modify a file
        print("   📝 Modifying a document...")
        modified_file = os.path.join(docs_dir, "rag_intro.md")
        with open(modified_file, "a", encoding="utf-8") as f:
            f.write(
                "\n\n## Latest Update\n\nRAG systems are becoming increasingly popular!\n"
            )

        # Run indexing again
        stats3 = scanner.ingest_directory(docs_dir, recursive=True)
        print(f"   ✓ Third run: {stats3['updated_files']} file updated")
        print(f"   ✓ New chunks: {stats3['total_chunks']}")
        print()

        # Final statistics
        print("=" * 70)
        print("📊 Final Statistics")
        print("=" * 70)
        print(f"   Total documents in database: {db_manager.get_document_count()}")
        print(f"   Database path: {db_path}")
        print(f"   Embedding model: {db_manager.model_name}")
        print(f"   Vector dimensions: 384")
        print()

        print("=" * 70)
        print("  ✅ Demo Complete!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Start the FastAPI server: uvicorn main:app --reload")
        print("  2. Try the API at: http://localhost:8000/docs")
        print("  3. Index your own documents using POST /api/index")
        print("  4. Search using GET /api/search?q=your+query")
        print()


if __name__ == "__main__":
    main()
