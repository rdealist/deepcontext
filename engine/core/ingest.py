"""
File ingestion module for scanning and chunking local documents.

Supports:
- Recursive directory scanning
- PDF, DOCX, Markdown, and text file parsing
- Intelligent chunking with overlap
- Incremental updates based on file modification time
"""

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pypdf
import docx
from db.manager import DBManager


@dataclass
class FileInfo:
    """Information about a scanned file."""

    path: str
    size: int
    mtime: float
    hash: str


class TextProcessor:
    """
    Intelligently chunk text while preserving structure and metadata.
    """

    def __init__(
        self, chunk_size: int = 500, overlap: int = 50, min_chunk_size: int = 100
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

    def chunk_content(
        self, content: str, metadata: Dict[str, Any], file_type: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk content based on file type.
        """
        if file_type in [".md", ".markdown"]:
            return self._chunk_markdown(content)
        else:
            return self._chunk_generic(content)

    def _chunk_markdown(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk markdown text into manageable pieces with line number tracking.
        """
        chunks = []
        heading_pattern = r"^(#{1,6})\s+.+$"
        lines = text.split("\n")

        current_chunk = []
        current_heading = "Introduction"
        chunk_index = 0
        chunk_start_line = 1

        for line_idx, line in enumerate(lines, start=1):
            heading_match = re.match(heading_pattern, line)

            if heading_match:
                chunk_text = "\n".join(current_chunk).strip()
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(
                        {
                            "content": chunk_text,
                            "chunk_index": chunk_index,
                            "metadata": {
                                "heading": current_heading,
                                "start_line": chunk_start_line,
                                "end_line": line_idx - 1,
                            },
                        }
                    )
                    chunk_index += 1

                current_heading = line.strip()
                current_chunk = [line]
                chunk_start_line = line_idx
            else:
                current_chunk.append(line)
                if len("\n".join(current_chunk)) > self.chunk_size * 2:
                    chunk_text = "\n".join(current_chunk).strip()
                    sub_chunks = self._split_large_chunk(chunk_text)
                    
                    lines_in_chunk = len(current_chunk)
                    lines_per_subchunk = max(1, lines_in_chunk // len(sub_chunks))

                    for i, sub_chunk in enumerate(sub_chunks):
                        sub_start = chunk_start_line + (i * lines_per_subchunk)
                        sub_end = min(chunk_start_line + ((i + 1) * lines_per_subchunk) - 1, line_idx)
                        chunks.append(
                            {
                                "content": sub_chunk,
                                "chunk_index": chunk_index + i,
                                "metadata": {
                                    "heading": current_heading,
                                    "start_line": sub_start,
                                    "end_line": sub_end,
                                },
                            }
                        )
                    chunk_index += len(sub_chunks)
                    current_chunk = []
                    chunk_start_line = line_idx + 1

        chunk_text = "\n".join(current_chunk).strip()
        if len(chunk_text) >= self.min_chunk_size:
            chunks.append(
                {
                    "content": chunk_text,
                    "chunk_index": chunk_index,
                    "metadata": {
                        "heading": current_heading,
                        "start_line": chunk_start_line,
                        "end_line": len(lines),
                    },
                }
            )
        
        # Add overlap
        self._add_overlap(chunks)
        return chunks

    def _chunk_generic(self, text: str) -> List[Dict[str, Any]]:
        """Generic text chunking."""
        chunks = []
        if not text.strip():
            return chunks
            
        sub_chunks = self._split_large_chunk(text)
        for i, sub_chunk in enumerate(sub_chunks):
            chunks.append({
                "content": sub_chunk,
                "chunk_index": i,
                "metadata": {}
            })
        
        self._add_overlap(chunks)
        return chunks

    def _split_large_chunk(self, text: str) -> List[str]:
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                if len(current_chunk) > self.overlap:
                    current_chunk = current_chunk[-self.overlap :] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _add_overlap(self, chunks: List[Dict[str, Any]]):
        if len(chunks) > 1:
            for i in range(1, len(chunks)):
                prev_chunk = chunks[i - 1]["content"]
                curr_chunk = chunks[i]["content"]
                if len(prev_chunk) > self.overlap:
                    overlap_text = prev_chunk[-self.overlap :]
                    chunks[i]["content"] = f"{overlap_text}\n\n{curr_chunk}"


class FileScanner:
    """
    Scans local directories for supported files and tracks changes.
    """

    SUPPORTED_EXTENSIONS = {".md", ".txt", ".markdown", ".pdf", ".docx"}

    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self.index_state: Dict[str, FileInfo] = {}
        self.processor = TextProcessor()

    def scan_directory(self, root_path: str, recursive: bool = True) -> List[str]:
        root = Path(root_path)
        if not root.exists() or not root.is_dir():
            return []

        files = []
        if recursive:
            for ext in self.SUPPORTED_EXTENSIONS:
                files.extend(root.rglob(f"*{ext}"))
        else:
            for ext in self.SUPPORTED_EXTENSIONS:
                files.extend(root.glob(f"*{ext}"))

        return [str(f) for f in files]

    def get_file_info(self, file_path: str) -> FileInfo:
        path = Path(file_path)
        stat = path.stat()
        hash_md5 = hashlib.md5()
        
        # For large files, maybe only hash parts, but for simplicity hash all for now
        # Note: PDF/Docx might be binary, need to handle updating hash carefully
        try:
            with open(file_path, "rb") as f:
                 for chunk in iter(lambda: f.read(4096), b""):
                     hash_md5.update(chunk)
        except Exception:
             pass

        return FileInfo(
            path=file_path,
            size=stat.st_size,
            mtime=stat.st_mtime,
            hash=hash_md5.hexdigest(),
        )

    def load_file_content(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load content from file returning list of raw chunks (e.g. per page for PDF).
        Each item has 'content' and 'metadata'.
        """
        ext = Path(file_path).suffix.lower()
        results = []

        try:
            if ext == ".pdf":
                reader = pypdf.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        results.append({
                            "content": text,
                            "metadata": {"page_label": i + 1}
                        })
            elif ext == ".docx":
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                if text:
                    results.append({"content": text, "metadata": {}})
            else:
                # Text files
                text = ""
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                except UnicodeDecodeError:
                    with open(file_path, "r", encoding="latin-1") as f:
                        text = f.read()
                if text:
                    results.append({"content": text, "metadata": {}})
        except Exception as e:
            print(f"[Scanner] Error loading {file_path}: {e}")
            
        return results

    def ingest_file(self, file_path: str) -> None:
        """Ingest a single file."""
        try:
            file_info = self.get_file_info(file_path)
            print(f"[Scanner] Processing single file: {file_path}")
            
            raw_contents = self.load_file_content(file_path)
            if not raw_contents:
                return

            file_ext = Path(file_path).suffix.lower()
            file_chunks = []
            
            for raw in raw_contents:
                raw_text = raw["content"]
                base_metadata = raw["metadata"]

                processed_chunks = self.processor.chunk_content(raw_text, base_metadata, file_ext)

                for chunk in processed_chunks:
                    final_metadata = {
                        "file_size": file_info.size,
                        "file_mtime": file_info.mtime,
                        **base_metadata,
                        **chunk["metadata"]
                    }
                    
                    file_chunks.append({
                        "content": chunk["content"],
                        "file_path": file_info.path,
                        "chunk_index": len(file_chunks), # Local index
                        "metadata": final_metadata
                    })
            
            if file_chunks:
                # First delete existing docs for this file? 
                # DBManager doesn't support delete well yet, but we should try to avoid duplicates.
                # For now just add.
                self.db_manager.add_documents(file_chunks)
                self.index_state[file_info.path] = file_info
                print(f"[Scanner] Ingested {len(file_chunks)} chunks from {file_path}")

        except Exception as e:
            print(f"[Scanner] Error ingesting file {file_path}: {e}")

    def ingest_directory(
        self, root_path: str, recursive: bool = True, force_reindex: bool = False
    ) -> Dict[str, Any]:
        print(f"[Scanner] Starting ingestion of: {root_path}")
        file_paths = self.scan_directory(root_path, recursive)

        if not file_paths:
            return {"total_files": 0, "new_files": 0, "updated_files": 0, "skipped_files": 0, "total_chunks": 0}

        files_to_process = []
        new_count = 0
        updated_count = 0
        skipped_count = 0

        for file_path in file_paths:
            try:
                file_info = self.get_file_info(file_path)
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
            except Exception as e:
                print(f"[Scanner] Error checking file {file_path}: {e}")

        print(f"[Scanner] New: {new_count}, Updated: {updated_count}, Skipped: {skipped_count}")

        if not files_to_process:
            return {"total_files": len(file_paths), "new_files": new_count, "updated_files": updated_count, "skipped_files": skipped_count, "total_chunks": 0}

        all_chunks = []
        for file_info in files_to_process:
            print(f"[Scanner] Processing: {file_info.path}")
            
            raw_contents = self.load_file_content(file_info.path)
            if not raw_contents:
                continue

            file_ext = Path(file_info.path).suffix.lower()
            
            # Process each raw content part (e.g. PDF page)
            for raw in raw_contents:
                raw_text = raw["content"]
                base_metadata = raw["metadata"] # e.g. {page_label: 1}

                # Chunk further if needed
                processed_chunks = self.processor.chunk_content(raw_text, base_metadata, file_ext)

                for chunk in processed_chunks:
                    # Merge metadata
                    final_metadata = {
                        "file_size": file_info.size,
                        "file_mtime": file_info.mtime,
                        **base_metadata,
                        **chunk["metadata"]
                    }
                    
                    all_chunks.append({
                        "content": chunk["content"],
                        "file_path": file_info.path,
                        "chunk_index": len(all_chunks), # Global index or local? Manager handles doc_id.
                        "metadata": final_metadata
                    })
            
            self.index_state[file_info.path] = file_info

        if all_chunks:
            self.db_manager.add_documents(all_chunks)

        return {
            "total_files": len(file_paths),
            "new_files": new_count,
            "updated_files": updated_count,
            "skipped_files": skipped_count,
            "total_chunks": len(all_chunks),
        }
