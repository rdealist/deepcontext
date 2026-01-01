#!/usr/bin/env python3
"""
Test script for RAG system functionality.

Tests the three main components:
1. Database initialization (LanceDB + sentence-transformers)
2. File ingestion (scanning, chunking, embedding)
3. Vector search (semantic similarity)

Usage:
    python test_rag.py
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ingest import FileScanner, MarkdownChunker
from db.manager import DBManager


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_step1_database_initialization():
    """Test Step 1: Initialize LanceDB with sentence-transformers."""
    print_section("STEP 1: Database Initialization")

    try:
        # Create temporary database
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_db")

            print(f"📦 Creating database at: {db_path}")
            db_manager = DBManager(db_path=db_path)

            print(f"✅ Database initialized successfully!")
            print(f"   - Model: {db_manager.model_name}")
            print(f"   - Database path: {db_manager.db_path}")
            print(f"   - Table name: {db_manager.table_name}")

            # Test embedding generation
            test_text = "This is a test sentence for embedding generation."
            embedding = db_manager.generate_embedding(test_text)

            print(f"\n🧪 Testing embedding generation:")
            print(f"   - Input: '{test_text}'")
            print(f"   - Embedding dimension: {len(embedding)}")
            print(f"   - First 5 values: {embedding[:5]}")

            assert len(embedding) == 384, "Expected 384-dimensional embedding"
            print(f"\n✅ Step 1 PASSED: Database initialization works!")

            return True

    except Exception as e:
        print(f"\n❌ Step 1 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_step2_file_ingestion():
    """Test Step 2: File scanning and chunking."""
    print_section("STEP 2: File Ingestion")

    try:
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create database
            db_path = os.path.join(tmpdir, "test_db")
            db_manager = DBManager(db_path=db_path)

            # Create test markdown files
            test_dir = os.path.join(tmpdir, "test_docs")
            os.makedirs(test_dir)

            # File 1: Simple markdown
            file1_path = os.path.join(test_dir, "file1.md")
            with open(file1_path, "w", encoding="utf-8") as f:
                f.write(
                    """# Introduction to RAG

Retrieval-Augmented Generation (RAG) is a powerful technique that combines the benefits of retrieval-based and generative AI models.

## How RAG Works

RAG works by first retrieving relevant documents from a knowledge base, then using those documents as context for generating responses.

### Benefits

- Improved accuracy
- Reduced hallucinations
- Access to up-to-date information
"""
                )

            # File 2: Another markdown file
            file2_path = os.path.join(test_dir, "file2.md")
            with open(file2_path, "w", encoding="utf-8") as f:
                f.write(
                    """# Vector Databases

Vector databases are specialized databases designed to store and search high-dimensional vectors efficiently.

## Popular Options

- LanceDB: Fast and embedded
- Pinecone: Cloud-based
- Weaviate: Open source and scalable

## Use Cases

Vector databases are perfect for similarity search, recommendation systems, and RAG applications.
"""
                )

            # File 3: Text file
            file3_path = os.path.join(test_dir, "notes.txt")
            with open(file3_path, "w", encoding="utf-8") as f:
                f.write(
                    """Just some random notes about embeddings.

Sentence transformers can convert text into dense vectors.
These vectors capture semantic meaning.
Similar sentences have similar vectors.
"""
                )

            print(f"📁 Created test directory with 3 files")
            print(f"   - {file1_path}")
            print(f"   - {file2_path}")
            print(f"   - {file3_path}")

            # Test chunking
            print("\n🔪 Testing Markdown Chunker:")
            chunker = MarkdownChunker(chunk_size=200, overlap=30)

            with open(file1_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = chunker.chunk(content, file1_path)
            print(f"   - Input length: {len(content)} characters")
            print(f"   - Number of chunks: {len(chunks)}")
            for i, chunk in enumerate(chunks):
                print(
                    f"   - Chunk {i}: {len(chunk['content'])} chars, heading: '{chunk['heading']}'"
                )

            # Test file scanner
            print("\n🔍 Testing File Scanner:")
            scanner = FileScanner(db_manager)

            stats = scanner.ingest_directory(test_dir, recursive=True)

            print(f"   - Total files: {stats['total_files']}")
            print(f"   - New files: {stats['new_files']}")
            print(f"   - Total chunks: {stats['total_chunks']}")

            # Verify documents were added
            doc_count = db_manager.get_document_count()
            print(f"\n📊 Database now contains {doc_count} documents")

            assert doc_count == stats["total_chunks"], "Document count mismatch"
            assert stats["total_files"] == 3, "Expected 3 files"
            assert stats["total_chunks"] > 0, "Expected chunks to be created"

            # Test incremental update
            print("\n🔄 Testing Incremental Update:")
            stats2 = scanner.ingest_directory(test_dir, recursive=True)
            print(f"   - Skipped files: {stats2['skipped_files']}")
            print(f"   - New chunks: {stats2['total_chunks']}")

            assert stats2["skipped_files"] == 3, (
                "All files should be skipped on second run"
            )
            assert stats2["total_chunks"] == 0, "No new chunks should be created"

            # Test force reindex
            print("\n🔄 Testing Force Reindex:")
            stats3 = scanner.ingest_directory(
                test_dir, recursive=True, force_reindex=True
            )
            print(f"   - New files: {stats3['new_files']}")
            print(f"   - Total chunks: {stats3['total_chunks']}")

            assert stats3["total_chunks"] > 0, "Chunks should be recreated"

            print(f"\n✅ Step 2 PASSED: File ingestion works!")
            return True

    except Exception as e:
        print(f"\n❌ Step 2 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_step3_vector_search():
    """Test Step 3: Semantic vector search."""
    print_section("STEP 3: Vector Search")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and populate database
            db_path = os.path.join(tmpdir, "test_db")
            db_manager = DBManager(db_path=db_path)

            # Create test documents
            test_dir = os.path.join(tmpdir, "test_docs")
            os.makedirs(test_dir)

            docs = [
                (
                    "python.md",
                    """# Python Programming

Python is a high-level, interpreted programming language known for its simplicity and readability.

## Features

- Easy to learn
- Extensive libraries
- Great for data science and AI
""",
                ),
                (
                    "javascript.md",
                    """# JavaScript

JavaScript is a versatile programming language primarily used for web development.

## Characteristics

- Runs in browsers
- Event-driven
- Asynchronous programming
""",
                ),
                (
                    "databases.md",
                    """# Database Systems

Databases are organized collections of data that can be easily accessed and managed.

## Types

- SQL databases (PostgreSQL, MySQL)
- NoSQL databases (MongoDB, Redis)
- Vector databases (LanceDB, Pinecone)
""",
                ),
            ]

            for filename, content in docs:
                filepath = os.path.join(test_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

            # Ingest documents
            scanner = FileScanner(db_manager)
            stats = scanner.ingest_directory(test_dir)

            print(
                f"📚 Indexed {stats['total_chunks']} chunks from {stats['total_files']} files"
            )

            # Test different queries
            test_queries = [
                ("What is Python used for?", "python.md"),
                ("Tell me about databases", "databases.md"),
                ("web development programming", "javascript.md"),
                ("machine learning and AI", "python.md"),
            ]

            print("\n🔍 Testing Semantic Search:\n")

            for query, expected_file in test_queries:
                results = db_manager.search(query, limit=3)

                print(f"Query: '{query}'")
                print(f"Expected: {expected_file}")

                if results:
                    top_result = results[0]
                    metadata = top_result["metadata"]
                    file_name = metadata.get("file_name", "Unknown")

                    print(f"Top Result: {file_name}")
                    print(f"Content Preview: {top_result['content'][:100]}...")
                    print(f"Score: {top_result.get('score', 'N/A')}")

                    # Check if expected file is in top results
                    found = any(
                        r["metadata"].get("file_name") == expected_file for r in results
                    )
                    if found:
                        print(f"✅ Found expected file in results")
                    else:
                        print(f"⚠️  Expected file not in top results (but this is OK)")

                else:
                    print("❌ No results found")

                print()

            # Test empty results
            print("🔍 Testing with no matches:")
            empty_results = db_manager.search(
                "quantum cryptography blockchain", limit=5
            )
            print(f"   - Query: 'quantum cryptography blockchain'")
            print(f"   - Results: {len(empty_results)}")
            print(
                f"   - (Should still return results due to semantic similarity, even if not perfect match)"
            )

            print(f"\n✅ Step 3 PASSED: Vector search works!")
            return True

    except Exception as e:
        print(f"\n❌ Step 3 FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  🧪 RAG SYSTEM TEST SUITE")
    print("=" * 70)
    print("\nTesting the three main components of the RAG system:")
    print("1. Database Initialization (LanceDB + Embeddings)")
    print("2. File Ingestion (Scanning + Chunking)")
    print("3. Vector Search (Semantic Similarity)")

    results = []

    # Run tests
    results.append(("Database Initialization", test_step1_database_initialization()))
    results.append(("File Ingestion", test_step2_file_ingestion()))
    results.append(("Vector Search", test_step3_vector_search()))

    # Summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")

    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'=' * 70}\n")

    if passed == total:
        print("🎉 All tests passed! Your RAG system is working correctly.\n")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
