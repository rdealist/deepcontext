# CLAUDE.md - Development Guide

## Build & Run Commands
- Install All: `npm install && cd engine && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Run Electron (Dev): `npm run dev` (Need to configure package.json)
- Run Backend (Dev): `cd engine && uvicorn main:app --reload`
- Type Check: `npm run type-check`

## Code Style & Implementation Details
- **Backend (Python)**: Use FastAPI, Pydantic v2, and LanceDB. Follow PEP8.
- **Frontend (TS/React)**: Use Functional Components, Tailwind CSS, and Shadcn UI.
- **IPC Pattern**: All system-level file access must go through Electron Main (`electron/main.ts`) via `ipcMain`/`ipcRenderer`.
- **RAG Logic**: Use LangChain or LlamaIndex logic simplified for local use.
- **Error Handling**: Always wrap Python child process spawns in try-catch and log stderr for debugging.

## Project Structure Notes
- `/app`: Next.js (App Router)
- `/electron`: Electron Shell
- `/engine`: Python RAG Engine
- `/shared`: Shared Types
