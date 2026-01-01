import json
import os
from typing import List, Optional

import requests
import uvicorn
from core.ingest import FileScanner
from core.llm import get_llm_service
from database.chat_history import get_chat_history
from db.manager import get_db_manager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from core.watcher import DirectoryWatcher

app = FastAPI(title="DeepContext Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_manager = None
file_scanner = None
llm_service = None
chat_history = None
watcher = None
chat_settings = {"model": None, "top_k": 5}

# ... (initialize_services stays same) ...

@app.post("/api/index", response_model=IndexResponse)
async def index_directory(request: IndexRequest):
    """
    Index a directory of documents into the vector database.
    
    This endpoint:
    1. Scans the specified directory for supported files
    2. Chunks the content intelligently
    3. Generates embeddings using sentence-transformers
    4. Stores in LanceDB for vector similarity search
    5. Starts a background watcher for auto-indexing new files
    """
    initialize_services()
    global watcher

    # Validate path
    if not os.path.exists(request.path):
        raise HTTPException(
            status_code=400, detail=f"Path does not exist: {request.path}"
        )

    if not os.path.isdir(request.path):
        raise HTTPException(
            status_code=400, detail=f"Path is not a directory: {request.path}"
        )

    try:
        # Ingest directory
        stats = file_scanner.ingest_directory(
            root_path=request.path,
            recursive=request.recursive,
            force_reindex=request.force_reindex,
        )

        # Start watcher
        if watcher:
            watcher.stop()
        
        watcher = DirectoryWatcher(request.path, lambda f: file_scanner.ingest_file(f))
        watcher.start()

        # Build response message
        message = (
            f"Indexed {stats['total_files']} files "
            f"({stats['new_files']} new, {stats['updated_files']} updated, "
            f"{stats['skipped_files']} skipped). "
            f"Created {stats['total_chunks']} chunks. "
            f"Auto-indexing started."
        )

        return IndexResponse(success=True, message=message, stats=stats)

    except Exception as e:
        print(f"[Index] Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Error during indexing: {str(e)}")


def initialize_services():
    """Initialize database and scanner services."""
    global db_manager, file_scanner, llm_service, chat_history, chat_settings

    if db_manager is None:
        # Get database path from environment or use default
        db_path = os.environ.get("DB_PATH", None)
        db_manager = get_db_manager(db_path=db_path)
        print("[Engine] DBManager initialized")

    if file_scanner is None:
        file_scanner = FileScanner(db_manager)
        print("[Engine] FileScanner initialized")

    if llm_service is None:
        llm_service = get_llm_service()
        print("[Engine] LLMService initialized")

    if chat_history is None:
        chat_history = get_chat_history()
        print("[Engine] Chat history storage initialized")

    if chat_settings["model"] is None:
        chat_settings["model"] = llm_service.config.model


# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    initialize_services()
    print("[Engine] Application started successfully")


class HealthResponse(BaseModel):
    status: str
    version: str
    document_count: Optional[int] = None


class HelloResponse(BaseModel):
    message: str


class IndexRequest(BaseModel):
    path: str = Field(..., description="Directory path to index")
    recursive: bool = Field(default=True, description="Recursively scan subdirectories")
    force_reindex: bool = Field(default=False, description="Force reindex all files")


class IndexResponse(BaseModel):
    success: bool
    message: str
    stats: dict


class SearchResult(BaseModel):
    id: str
    content: str
    file_name: str
    file_path: str
    heading: Optional[str] = None
    score: Optional[float] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


class SourceReference(BaseModel):
    file_name: str
    file_path: str
    heading: Optional[str] = None
    score: Optional[float] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's question")
    session_id: str = Field(..., description="Session ID for chat history")
    top_k: Optional[int] = Field(
        default=None, ge=1, le=20, description="Number of context chunks"
    )


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]
    query: str


class SessionInfo(BaseModel):
    id: str
    title: str
    created_at: str


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None


class MessageInfo(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List[SourceReference]] = None
    created_at: str


class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: List[MessageInfo]


class ModelsResponse(BaseModel):
    models: List[str]
    current_model: str
    top_k: int


class SettingsUpdateRequest(BaseModel):
    model: Optional[str] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=20)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with database status."""
    initialize_services()

    doc_count = None
    try:
        doc_count = db_manager.get_document_count()
    except Exception as e:
        print(f"[Health] Error getting document count: {e}")

    return HealthResponse(status="ok", version="0.1.0", document_count=doc_count)


@app.get("/api/hello", response_model=HelloResponse)
async def hello():
    """Simple hello endpoint."""
    return HelloResponse(message="Hello from Python Engine")


@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """List all chat sessions."""
    initialize_services()
    sessions = chat_history.list_sessions()
    return [SessionInfo(**session.__dict__) for session in sessions]


@app.post("/sessions", response_model=SessionInfo)
async def create_session(request: SessionCreateRequest):
    """Create a new chat session."""
    initialize_services()
    session = chat_history.create_session(title=request.title)
    return SessionInfo(**session.__dict__)


@app.get("/sessions/{session_id}", response_model=SessionMessagesResponse)
async def get_session_messages(session_id: str):
    """Get chat messages for a session."""
    initialize_services()
    session = chat_history.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = chat_history.list_messages(session_id)
    return SessionMessagesResponse(
        session_id=session_id,
        messages=[
            MessageInfo(
                id=message.id,
                role=message.role,
                content=message.content,
                sources=message.sources,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session and its messages."""
    initialize_services()
    deleted = chat_history.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    """List available Ollama models."""
    initialize_services()
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503, detail=f"Ollama API not available: {exc}"
        )

    payload = response.json()
    models = [
        model.get("name")
        for model in payload.get("models", [])
        if model.get("name")
    ]
    return ModelsResponse(
        models=models,
        current_model=chat_settings["model"],
        top_k=chat_settings["top_k"],
    )


@app.post("/settings")
async def update_settings(request: SettingsUpdateRequest):
    """Update current model and top_k settings."""
    initialize_services()

    if request.model:
        llm_service.config.model = request.model
        chat_settings["model"] = request.model

    if request.top_k is not None:
        chat_settings["top_k"] = request.top_k

    return {"model": chat_settings["model"], "top_k": chat_settings["top_k"]}


@app.post("/api/index", response_model=IndexResponse)
async def index_directory(request: IndexRequest):
    """
    Index a directory of documents into the vector database.

    This endpoint:
    1. Scans the specified directory for .md and .txt files
    2. Chunks the content intelligently (by headings or size)
    3. Generates embeddings using sentence-transformers
    4. Stores in LanceDB for vector similarity search
    5. Only reindexes changed or new files (unless force_reindex=True)

    Args:
        request: IndexRequest with path, recursive, and force_reindex options

    Returns:
        IndexResponse with statistics about the indexing operation
    """
    initialize_services()

    # Validate path
    if not os.path.exists(request.path):
        raise HTTPException(
            status_code=400, detail=f"Path does not exist: {request.path}"
        )

    if not os.path.isdir(request.path):
        raise HTTPException(
            status_code=400, detail=f"Path is not a directory: {request.path}"
        )

    try:
        # Ingest directory
        stats = file_scanner.ingest_directory(
            root_path=request.path,
            recursive=request.recursive,
            force_reindex=request.force_reindex,
        )

        # Build response message
        message = (
            f"Indexed {stats['total_files']} files "
            f"({stats['new_files']} new, {stats['updated_files']} updated, "
            f"{stats['skipped_files']} skipped). "
            f"Created {stats['total_chunks']} chunks."
        )

        return IndexResponse(success=True, message=message, stats=stats)

    except Exception as e:
        print(f"[Index] Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=f"Error during indexing: {str(e)}")


@app.get("/api/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., description="Search query"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Maximum results to return"
    ),
):
    """
    Search for documents using semantic vector similarity.

    This endpoint:
    1. Generates an embedding for the query text
    2. Performs vector similarity search in LanceDB
    3. Returns the most relevant document chunks

    Args:
        q: The search query (user's question or keywords)
        limit: Maximum number of results (1-100)

    Returns:
        SearchResponse with matching document chunks and metadata
    """
    initialize_services()

    if not q or not q.strip():
        raise HTTPException(
            status_code=400, detail="Query parameter 'q' cannot be empty"
        )

    try:
        # Check if database has any documents
        doc_count = db_manager.get_document_count()

        if doc_count == 0:
            return SearchResponse(query=q, results=[], total=0)

        # Perform vector search
        raw_results = db_manager.search(query=q, limit=limit)

        # Format results
        search_results = []
        for result in raw_results:
            metadata = result.get("metadata", {})

            search_results.append(
                SearchResult(
                    id=result["id"],
                    content=result["content"],
                    file_name=metadata.get("file_name", "Unknown"),
                    file_path=metadata.get("file_path", ""),
                    heading=metadata.get("heading"),
                    score=result.get("score"),
                    start_line=metadata.get("start_line"),
                    end_line=metadata.get("end_line"),
                )
            )

        return SearchResponse(
            query=q, results=search_results, total=len(search_results)
        )

    except Exception as e:
        print(f"[Search] Error during search: {e}")
        raise HTTPException(status_code=500, detail=f"Error during search: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Get database statistics."""
    initialize_services()

    try:
        doc_count = db_manager.get_document_count()

        return {
            "document_count": doc_count,
            "model_name": db_manager.model_name,
            "db_path": str(db_manager.db_path),
        }
    except Exception as e:
        print(f"[Stats] Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint.

    This endpoint:
    1. Searches for relevant document chunks using vector similarity
    2. Builds context from top_k results
    3. Sends context + question to local LLM (Ollama)
    4. Returns LLM answer with source references

    Args:
        request: ChatRequest with message and top_k

    Returns:
        ChatResponse with answer and source references
    """
    initialize_services()

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        session = chat_history.get_session(request.session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

        chat_history.add_message(
            request.session_id, "user", request.message.strip(), None
        )

        # Step 1: Search for relevant contexts
        doc_count = db_manager.get_document_count()
        top_k = request.top_k or chat_settings["top_k"]

        if doc_count == 0:
            answer = "知识库为空，请先导入文档后再提问。"
            chat_history.add_message(request.session_id, "assistant", answer, [])
            return ChatResponse(
                answer="知识库为空，请先导入文档后再提问。",
                sources=[],
                query=request.message,
            )

        raw_results = db_manager.search(query=request.message, limit=top_k)

        if not raw_results:
            answer = "没有找到与问题相关的内容，请尝试其他问题。"
            chat_history.add_message(request.session_id, "assistant", answer, [])
            return ChatResponse(
                answer="没有找到与问题相关的内容，请尝试其他问题。",
                sources=[],
                query=request.message,
            )

        # Step 2: Extract contexts and sources
        contexts = [r["content"] for r in raw_results]
        sources = []

        for result in raw_results:
            metadata = result.get("metadata", {})
            score = result.get("score")
            if score is not None:
                score = float(score)
            sources.append(
                {
                    "file_name": metadata.get("file_name", "Unknown"),
                    "file_path": metadata.get("file_path", ""),
                    "heading": metadata.get("heading"),
                    "score": score,
                    "start_line": metadata.get("start_line"),
                    "end_line": metadata.get("end_line"),
                }
            )

        # Step 3: Generate answer using LLM
        print(f"[Chat] Generating answer for: {request.message[:50]}...")
        answer = llm_service.generate_answer(
            query=request.message,
            contexts=contexts,
        )

        print(f"[Chat] Answer generated successfully")

        chat_history.add_message(
            request.session_id, "assistant", answer, sources
        )

        return ChatResponse(
            answer=answer,
            sources=sources,
            query=request.message,
        )

    except RuntimeError as e:
        print(f"[Chat] LLM error: {e}")
        raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")

    except Exception as e:
        print(f"[Chat] Error during chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error during chat: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    RAG-powered chat endpoint with Server-Sent Events (SSE) streaming.

    This endpoint:
    1. Searches for relevant document chunks using vector similarity
    2. Builds context from top_k results
    3. Streams LLM response in real-time using SSE format
    4. Sends sources metadata at the end

    SSE Event Types:
    - event: token  -> Individual token from LLM
    - event: sources -> Source references (sent once at end)
    - event: done   -> Stream completion signal
    - event: error  -> Error message

    Args:
        request: ChatRequest with message and top_k

    Returns:
        StreamingResponse with SSE formatted events
    """
    initialize_services()

    if not request.message or not request.message.strip():

        async def error_stream():
            yield f"event: error\ndata: {json.dumps({'error': 'Message cannot be empty'})}\n\n"

        return StreamingResponse(error_stream(), media_type="text/event-stream")

    session = chat_history.get_session(request.session_id)
    if session is None:

        async def session_error_stream():
            yield f"event: error\ndata: {json.dumps({'error': 'Session not found'})}\n\n"

        return StreamingResponse(
            session_error_stream(), media_type="text/event-stream"
        )

    async def generate_sse():
        try:
            chat_history.add_message(
                request.session_id, "user", request.message.strip(), None
            )

            # Step 1: Search for relevant contexts
            doc_count = db_manager.get_document_count()
            top_k = request.top_k or chat_settings["top_k"]

            if doc_count == 0:
                answer = "知识库为空，请先导入文档后再提问。"
                yield f"event: token\ndata: {json.dumps({'content': answer})}\n\n"
                yield f"event: sources\ndata: {json.dumps({'sources': []})}\n\n"
                yield "event: done\ndata: {}\n\n"
                chat_history.add_message(
                    request.session_id, "assistant", answer, []
                )
                return

            raw_results = db_manager.search(query=request.message, limit=top_k)

            if not raw_results:
                answer = "没有找到与问题相关的内容，请尝试其他问题。"
                yield f"event: token\ndata: {json.dumps({'content': answer})}\n\n"
                yield f"event: sources\ndata: {json.dumps({'sources': []})}\n\n"
                yield "event: done\ndata: {}\n\n"
                chat_history.add_message(
                    request.session_id, "assistant", answer, []
                )
                return

            # Step 2: Extract contexts and sources
            contexts = [r["content"] for r in raw_results]
            sources = []

            for result in raw_results:
                metadata = result.get("metadata", {})
                score = result.get("score")
                if score is not None:
                    score = float(score)
                sources.append(
                    {
                        "file_name": metadata.get("file_name", "Unknown"),
                        "file_path": metadata.get("file_path", ""),
                        "heading": metadata.get("heading"),
                        "score": score,
                        "start_line": metadata.get("start_line"),
                        "end_line": metadata.get("end_line"),
                    }
                )

            # Step 3: Stream answer using LLM
            print(f"[ChatStream] Generating answer for: {request.message[:50]}...")
            full_content = ""

            for chunk in llm_service.generate_answer_stream(
                query=request.message,
                contexts=contexts,
            ):
                full_content += chunk
                yield f"event: token\ndata: {json.dumps({'content': chunk})}\n\n"

            # Step 4: Send sources at the end
            yield f"event: sources\ndata: {json.dumps({'sources': sources})}\n\n"
            yield "event: done\ndata: {}\n\n"
            chat_history.add_message(
                request.session_id, "assistant", full_content, sources
            )

            print(f"[ChatStream] Stream completed successfully")

        except RuntimeError as e:
            print(f"[ChatStream] LLM error: {e}")
            yield f"event: error\ndata: {json.dumps({'error': f'LLM service error: {str(e)}'})}\n\n"

        except Exception as e:
            print(f"[ChatStream] Error during streaming: {e}")
            yield f"event: error\ndata: {json.dumps({'error': f'Streaming error: {str(e)}'})}\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
