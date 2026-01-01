"""
LanceDB Database Manager for DeepContext.

Manages vector storage and retrieval using LanceDB and sentence-transformers.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import lancedb
from lancedb.pydantic import LanceModel, Vector
from pydantic import Field
from sentence_transformers import SentenceTransformer


class Document(LanceModel):
    """Document schema for LanceDB."""

    id: str = Field(default="")
    vector: Vector(384)  # all-MiniLM-L6-v2 produces 384-dimensional vectors
    content: str
    metadata: str  # JSON string containing file info


class DBManager:
    """
    Manages LanceDB database operations for document storage and retrieval.

    Features:
    - Persistent local storage (like SQLite)
    - Automatic embedding generation using sentence-transformers
    - Efficient vector similarity search
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize DBManager.

        Args:
            db_path: Path to store database. Defaults to ./data/lancedb
            model_name: HuggingFace model name for embeddings
            cache_dir: Custom cache directory for models
        """
        # Set database path
        if db_path is None:
            db_path = os.path.join(os.getcwd(), "data", "lancedb")

        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Initialize LanceDB connection
        self.db = lancedb.connect(str(self.db_path))

        # Initialize embedding model
        self.model_name = model_name
        cache_dir = cache_dir or os.path.join(os.getcwd(), "data", "models")
        os.makedirs(cache_dir, exist_ok=True)

        print(f"[DBManager] Loading embedding model: {model_name}")
        print(f"[DBManager] Cache directory: {cache_dir}")

        self.embedding_model = SentenceTransformer(model_name, cache_folder=cache_dir)

        self.table_name = "documents"
        self._table = None

    @property
    def table(self):
        """Lazy-load table."""
        if self._table is None:
            self._initialize_table()
        return self._table

    def _initialize_table(self):
        """Initialize or load the documents table."""
        if self.table_name in self.db.table_names():
            self._table = self.db.open_table(self.table_name)
            print(f"[DBManager] Loaded existing table: {self.table_name}")
            print(f"[DBManager] Current document count: {self._table.count_rows()}")
        else:
            self._table = self.db.create_table(
                self.table_name, schema=Document, mode="overwrite"
            )
            print(f"[DBManager] Created new table: {self.table_name}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using sentence-transformers.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector
        """
        return self.embedding_model.encode(text).tolist()

    def generate_doc_id(self, file_path: str, chunk_index: int, content: str) -> str:
        """
        Generate unique document ID based on file path and content.

        Args:
            file_path: Path to source file
            chunk_index: Index of the chunk in the file
            content: Chunk content

        Returns:
            Unique document ID
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{file_path}#{chunk_index}_{content_hash}"

    def add_documents(
        self, documents: List[Dict[str, Any]], overwrite: bool = True
    ) -> int:
        """
        Add documents to the database.

        Args:
            documents: List of document dicts with keys:
                - content: Text content
                - file_path: Source file path
                - chunk_index: Chunk index in file
                - metadata: Additional metadata dict
            overwrite: Whether to overwrite existing documents

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        doc_records = []

        for doc in documents:
            # Generate embedding
            embedding = self.generate_embedding(doc["content"])

            # Generate unique ID
            doc_id = self.generate_doc_id(
                doc["file_path"], doc["chunk_index"], doc["content"]
            )

            # Prepare metadata
            metadata = {
                "file_path": doc["file_path"],
                "file_name": os.path.basename(doc["file_path"]),
                "chunk_index": doc["chunk_index"],
                **doc.get("metadata", {}),
            }

            doc_records.append(
                {
                    "id": doc_id,
                    "vector": embedding,
                    "content": doc["content"],
                    "metadata": json.dumps(metadata, ensure_ascii=False),
                }
            )

        # Add to table
        mode = "overwrite" if overwrite else "append"
        self.table.add(doc_records, mode=mode)

        print(f"[DBManager] Added {len(doc_records)} documents to database")
        return len(doc_records)

    def search(
        self, query: str, limit: int = 10, metric: str = "cosine"
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            metric: Distance metric ("cosine", "l2", "dot")

        Returns:
            List of search results with content, metadata, and scores
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Search
        results = (
            self.table.search(query_embedding)
            .limit(limit)
            .metric(metric)
            .to_pydantic(Document)
        )

        # Format results
        formatted_results = []
        for result in results:
            metadata = json.loads(result.metadata)
            formatted_results.append(
                {
                    "id": result.id,
                    "content": result.content,
                    "metadata": metadata,
                    "score": getattr(result, "_score", None),
                }
            )

        return formatted_results

    def get_document_count(self) -> int:
        """Get total number of documents in database."""
        return self.table.count_rows()

    def delete_by_file(self, file_path: str) -> int:
        """
        Delete all documents from a specific file.

        Args:
            file_path: Path to file whose documents should be deleted

        Returns:
            Number of documents deleted
        """
        # This is a simplified version - LanceDB doesn't have direct delete by SQL
        # For now, we'll need to filter and rebuild
        # TODO: Implement proper deletion when LanceDB adds better support
        print(f"[DBManager] Delete by file not fully implemented: {file_path}")
        return 0

    def close(self):
        """Close database connection."""
        if self._table is not None:
            del self._table
            self._table = None
        print("[DBManager] Database connection closed")


# Global instance
_db_manager: Optional[DBManager] = None


def get_db_manager(
    db_path: Optional[str] = None, model_name: str = "all-MiniLM-L6-v2"
) -> DBManager:
    """
    Get or create global DBManager instance.

    Args:
        db_path: Path to database directory
        model_name: Name of embedding model

    Returns:
        DBManager instance
    """
    global _db_manager

    if _db_manager is None:
        _db_manager = DBManager(db_path=db_path, model_name=model_name)

    return _db_manager
