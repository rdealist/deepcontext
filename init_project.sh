#!/bin/bash

# --- 1. 基础结构创建 ---
echo "🚀 开始初始化 DeepContext 项目结构..."

mkdir -p .ai_docs
mkdir -p electron
mkdir -p engine/core engine/db engine/api
mkdir -p shared

# --- 2. 写入 AI 上下文文档 ---

echo "📝 正在生成 AI 上下文工程文档..."

cat << 'INNER_EOF' > .ai_docs/Project_Blueprint.md
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
INNER_EOF

cat << 'INNER_EOF' > .ai_docs/System_Architecture.md
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
INNER_EOF

cat << 'INNER_EOF' > .ai_docs/AI_Guidelines.md
# AI Coding Guidelines for DeepContext

- Always use **TypeScript** for frontend and electron code.
- Use **Pydantic** for all Python data models.
- **Critical**: Hande SIGTERM in Electron for Python process.
- **Critical**: Use app.getPath('userData') for local DB storage.
INNER_EOF

# --- 3. 初始化 Frontend (Next.js) ---
echo "📦 正在初始化前端 (Next.js)..."
npx create-next-app@latest app --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm < /dev/null

# --- 4. 初始化 Backend (Python) ---
echo "🐍 正在初始化后端 (Python)..."
cd engine
python3 -m venv venv
source venv/bin/activate || source venv/Scripts/activate
pip install fastapi uvicorn lancedb pydantic python-multipart langchain unstructured sentence-transformers
pip freeze > requirements.txt
touch main.py
cd ..

# --- 5. 初始化 Electron ---
echo "⚡ 正在配置 Electron..."
npm init -y
npm install electron --save-dev
npm install typescript ts-node @types/node --save-dev
touch electron/main.ts electron/preload.ts electron/py-process.ts

# --- 6. 完成 ---
echo "✅ 项目初始化完成！"
echo "下一步建议："
echo "1. 用 Cursor 打开本项目"
echo "2. 引用 @.ai_docs 里的文档，开始编写 electron/main.ts"
