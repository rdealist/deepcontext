# Project Blueprint: DeepContext (Local AI Knowledge Base)

## 1. Vision
A privacy-first, local-only personal knowledge engine that indexing local Markdown and PDF files using RAG (Retrieval-Augmented Generation).

## 2. Core Features (MVP)
- **Local Indexing**: Watch a local folder and index files into LanceDB.
- **Hybrid Search**: Semantic search (Embeddings) + Keyword search (BM25).
- **RAG Chat**: Chat with documents using Ollama (Llama 3/Mistral).
- **Graph Visualization**: Visual relationship map between entities in notes.
- **Reference Tracking**: Chat responses must include clickable citations to local files.

## 3. Tech Stack
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn/UI.
- **Desktop Shell**: Electron.
- **AI Backend**: FastAPI (Python 3.10+).
- **AI Models**: Ollama (Inference), Sentence-Transformers (Local Embeddings).
- **Vector DB**: LanceDB (Serverless, local storage).
