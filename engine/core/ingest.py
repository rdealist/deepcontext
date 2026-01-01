"""
File ingestion module for scanning and chunking local documents.

Supports:
- Recursive directory scanning
- Markdown and text file parsing
- Intelligent chunking with overlap
- Incremental updates based on file modification time
"""

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from db.manager import DBManager


@dataclass
class FileInfo:
    """Information about a scanned file."""

    path: str
    size: int
    mtime: float
    hash: str


class MarkdownChunker:
    """
    Intelligently chunk Markdown files while preserving structure.

    Strategies:
    1. Split by headings (##, ###)
    2. Split by paragraphs if chunks are too large
    3. Maintain overlap for context preservation
    """

    def __init__(
        self, chunk_size: int = 500, overlap: int = 50, min_chunk_size: int = 100
    ):
        """
        Initialize chunker.

        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
            min_chunk_size: Minimum chunk size to avoid tiny fragments
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Chunk markdown text into manageable pieces with line number tracking.

        Args:
            text: Raw markdown text
            file_path: Path to source file

        Returns:
            List of chunk dictionaries with line number information
        """
        chunks = []

        # First, try to split by headings
        heading_pattern = r"^(#{1,6})\s+.+$"
        lines = text.split("\n")

        current_chunk = []
        current_heading = "Introduction"
        chunk_index = 0
        chunk_start_line = 1  # Track starting line number (1-indexed)

        for line_idx, line in enumerate(lines, start=1):
            # Check if this is a heading
            heading_match = re.match(heading_pattern, line)

            if heading_match:
                # Save previous chunk if it's large enough
                chunk_text = "\n".join(current_chunk).strip()

                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(
                        {
                            "content": chunk_text,
                            "heading": current_heading,
                            "chunk_index": chunk_index,
                            "start_line": chunk_start_line,
                            "end_line": line_idx - 1,
                        }
                    )
                    chunk_index += 1

                # Start new chunk
                current_heading = line.strip()
                current_chunk = [line]
                chunk_start_line = line_idx
            else:
                current_chunk.append(line)

                # Check if chunk is too large, split by paragraphs
                if len("\n".join(current_chunk)) > self.chunk_size * 2:
                    chunk_text = "\n".join(current_chunk).strip()
                    sub_chunks = self._split_large_chunk(chunk_text)

                    # Calculate approximate line numbers for sub-chunks
                    lines_in_chunk = len(current_chunk)
                    lines_per_subchunk = max(1, lines_in_chunk // len(sub_chunks))

                    for i, sub_chunk in enumerate(sub_chunks):
                        sub_start = chunk_start_line + (i * lines_per_subchunk)
                        sub_end = min(chunk_start_line + ((i + 1) * lines_per_subchunk) - 1, line_idx)
                        chunks.append(
                            {
                                "content": sub_chunk,
                                "heading": current_heading,
                                "chunk_index": chunk_index + i,
                                "start_line": sub_start,
                                "end_line": sub_end,
                            }
                        )

                    chunk_index += len(sub_chunks)
                    current_chunk = []
                    chunk_start_line = line_idx + 1

        # Don't forget the last chunk
        chunk_text = "\n".join(current_chunk).strip()
        if len(chunk_text) >= self.min_chunk_size:
            chunks.append(
                {
                    "content": chunk_text,
                    "heading": current_heading,
                    "chunk_index": chunk_index,
                    "start_line": chunk_start_line,
                    "end_line": len(lines),
                }
            )

        # If no chunks were created (e.g., file too small), create one
        if not chunks and text.strip():
            chunks.append(
                {
                    "content": text.strip(),
                    "heading": "Content",
                    "chunk_index": 0,
                    "start_line": 1,
                    "end_line": len(lines),
                }
            )

        # Add overlap to chunks (except first and last)
        if len(chunks) > 1:
            for i in range(1, len(chunks)):
                prev_chunk = chunks[i - 1]["content"]
                curr_chunk = chunks[i]["content"]

                # Add overlap from previous chunk
                if len(prev_chunk) > self.overlap:
                    overlap_text = prev_chunk[-self.overlap :]
                    chunks[i]["content"] = f"{overlap_text}\n\n{curr_chunk}"

        return chunks

    def _split_large_chunk(self, text: str) -> List[str]:
        """
        Split a large chunk by paragraphs.

        Args:
            text: Large text chunk

        Returns:
            List of smaller chunks
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Add overlap
                if len(current_chunk) > self.overlap:
                    current_chunk = current_chunk[-self.overlap :] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks


class FileScanner:
    """
    Scans local directories for supported files and tracks changes.
    """

    SUPPORTED_EXTENSIONS = {".md", ".txt", ".markdown"}

    def __init__(self, db_manager: DBManager):
        """
        Initialize scanner.

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.index_state: Dict[str, FileInfo] = {}

    def scan_directory(self, root_path: str, recursive: bool = True) -> List[str]:
        """
        Scan directory for supported files.

        Args:
            root_path: Root directory to scan
            recursive: Whether to scan recursively

        Returns:
            List of file paths
        """
        root = Path(root_path)

        if not root.exists():
            print(f"[Scanner] Path does not exist: {root_path}")
            return []

        if not root.is_dir():
            print(f"[Scanner] Path is not a directory: {root_path}")
            return []

        files = []

        if recursive:
            for ext in self.SUPPORTED_EXTENSIONS:
                files.extend(root.rglob(f"*{ext}"))
        else:
            for ext in self.SUPPORTED_EXTENSIONS:
                files.extend(root.glob(f"*{ext}"))

        file_paths = [str(f) for f in files]
        print(f"[Scanner] Found {len(file_paths)} supported files")

        return file_paths

    def get_file_info(self, file_path: str) -> FileInfo:
        """
        Get file information including hash.

        Args:
            file_path: Path to file

        Returns:
            FileInfo object
        """
        path = Path(file_path)
        stat = path.stat()

        # Calculate file hash
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        return FileInfo(
            path=file_path,
            size=stat.st_size,
            mtime=stat.st_mtime,
            hash=hash_md5.hexdigest(),
        )

    def read_file(self, file_path: str) -> str:
        """
        Read file content with proper encoding detection.

        Args:
            file_path: Path to file

        Returns:
            File content as string
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with alternative encoding
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                print(f"[Scanner] Error reading file {file_path}: {e}")
                return ""

    def ingest_directory(
        self, root_path: str, recursive: bool = True, force_reindex: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest all files from a directory into the database.

        Args:
            root_path: Root directory to ingest
            recursive: Whether to scan recursively
            force_reindex: Force reindexing all files

        Returns:
            Statistics about the ingestion
        """
        print(f"[Scanner] Starting ingestion of: {root_path}")

        # Scan for files
        file_paths = self.scan_directory(root_path, recursive)

        if not file_paths:
            return {
                "total_files": 0,
                "new_files": 0,
                "updated_files": 0,
                "skipped_files": 0,
                "total_chunks": 0,
            }

        # Check which files need updating
        files_to_process = []
        new_count = 0
        updated_count = 0
        skipped_count = 0

        for file_path in file_paths:
            file_info = self.get_file_info(file_path)

            # Check if file needs updating
            if force_reindex:
                files_to_process.append(file_info)
                new_count += 1
            elif file_path not in self.index_state:
                files_to_process.append(file_info)
                new_count += 1
            else:
                old_info = self.index_state[file_path]
                if file_info.mtime > old_info.mtime or file_info.hash != old_info.hash:
                    files_to_process.append(file_info)
                    updated_count += 1
                else:
                    skipped_count += 1

        print(
            f"[Scanner] New: {new_count}, Updated: {updated_count}, Skipped: {skipped_count}"
        )

        if not files_to_process:
            print("[Scanner] No files to process")
            return {
                "total_files": len(file_paths),
                "new_files": new_count,
                "updated_files": updated_count,
                "skipped_files": skipped_count,
                "total_chunks": 0,
            }

        # Process files
        chunker = MarkdownChunker()
        all_chunks = []

        for file_info in files_to_process:
            print(f"[Scanner] Processing: {file_info.path}")

            # Read file
            content = self.read_file(file_info.path)

            if not content:
                print(f"[Scanner] Skipping empty file: {file_info.path}")
                continue

            # Chunk content
            chunks = chunker.chunk(content, file_info.path)

            # Prepare documents
            for chunk in chunks:
                all_chunks.append(
                    {
                        "content": chunk["content"],
                        "file_path": file_info.path,
                        "chunk_index": chunk["chunk_index"],
                        "metadata": {
                            "heading": chunk.get("heading", ""),
                            "file_size": file_info.size,
                            "file_mtime": file_info.mtime,
                            "start_line": chunk.get("start_line", 1),
                            "end_line": chunk.get("end_line", 1),
                        },
                    }
                )

            # Update index state
            self.index_state[file_info.path] = file_info

        # Add to database
        if all_chunks:
            self.db_manager.add_documents(all_chunks)

        return {
            "total_files": len(file_paths),
            "new_files": new_count,
            "updated_files": updated_count,
            "skipped_files": skipped_count,
            "total_chunks": len(all_chunks),
        }
