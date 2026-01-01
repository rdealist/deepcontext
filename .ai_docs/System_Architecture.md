# System Architecture & Standards

## 1. Directory Structure
- /app: Next.js frontend code. Focus on UI and API consumption.
- /electron: Electron main process and preload scripts.
- /engine: Python backend (FastAPI).
- /shared: Shared type definitions.

## 2. Development Standards
- **Inter-Process Communication (IPC)**: Use preload.ts for secure IPC.
- **Python Sidecar**: Electron Main process spawns FastAPI.
- **RAG Pipeline**: Load -> Transform (Markdown-aware) -> Embed -> Store (LanceDB).
