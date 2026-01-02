# DeepContext - Local AI Knowledge Base

Privacy-first, local-only personal knowledge engine powered by AI.

## 🏗️ Project Structure (Monorepo)

```
/deepcontext                    # Project Root
├── /app                        # Next.js Frontend Project (Independent)
│   ├── /src
│   │   ├── /app               # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   ├── /components        # React Components
│   │   │   ├── /ui           # Shadcn UI Components
│   │   │   ├── ChatArea.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── ...
│   │   └── /lib              # Utility Functions
│   │       └── utils.ts
│   ├── /public               # Static Assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   └── components.json       # Shadcn UI Config
│
├── /electron                  # Electron Main Process
│   ├── main.ts
│   ├── preload.ts
│   └── tsconfig.json
│
├── /engine                    # Python RAG Backend
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── /shared                    # Cross-Project Shared Code
│   └── /types
│       ├── chat.ts           # Chat-related Types
│       ├── electron-api.ts   # Electron IPC Interface Definitions
│       └── index.ts          # Unified Exports
│
├── /docs                      # Project Documentation
│   ├── THEME_DESIGN.md
│   └── THEME_QUICK_REF.md
│
└── package.json               # Root Project Configuration
```

## 📦 Core Modules

### `/app` - Frontend Application
- **Technology**: Next.js 15 (App Router), React, TypeScript, Tailwind CSS
- **UI Framework**: Shadcn UI
- **Responsibility**: User interface, chat interaction, session management
- **Path Aliases**:
  - `@/*` → `app/src/*` (internal imports)
  - `@shared/*` → `shared/*` (shared types)

### `/electron` - Desktop Shell
- **Technology**: Electron, TypeScript
- **Responsibility**: File system access, native integrations, Python process management
- **IPC**: Communicates with frontend via type-safe interfaces defined in `shared/types/electron-api.ts`

### `/engine` - RAG Backend
- **Technology**: Python, FastAPI, LanceDB, LangChain
- **Responsibility**: Document indexing, vector search, LLM integration
- **API**: RESTful API on `http://127.0.0.1:8000`

### `/shared` - Shared Types
- **Technology**: TypeScript
- **Responsibility**: Type definitions shared across frontend and Electron
- **Key Files**:
  - `chat.ts`: Chat messages, sessions, source references
  - `electron-api.ts`: Electron IPC interface definitions

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Ollama (for local LLM)

### Installation

```bash
# Install all dependencies
npm install && cd engine && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Development

```bash
# Run Electron app (Frontend + Backend)
npm run dev

# Run frontend only (for development)
npm run dev:next

# Run backend only
cd engine && uvicorn main:app --reload

# Type check
npm run type-check
```

## 🎯 Development Guidelines

### Type Sharing Mechanism

All types shared between frontend (`/app`) and Electron (`/electron`) **must** be defined in `/shared/types/`.

**Example:**

```typescript
// ✅ Correct: Import from shared types
import { ChatMessage, ElectronAPI } from "@shared/types";

// ❌ Wrong: Don't duplicate type definitions
interface ChatMessage { ... }  // Duplication!
```

### Path Alias Conventions

- **Within `/app`**: Use `@/*` for internal imports
  ```typescript
  import { Button } from "@/components/ui/button";
  ```

- **Cross-project**: Use `@shared/*` for shared types
  ```typescript
  import { ChatMessage } from "@shared/types";
  ```

### Adding New Features

1. **Types First**: Define shared types in `/shared/types/` if needed
2. **Backend**: Implement API endpoints in `/engine`
3. **Frontend**: Build UI components in `/app/src/components`
4. **Integration**: Wire up Electron IPC if system access is required

### Project Architecture Principles

- **KISS**: Keep implementations simple and straightforward
- **YAGNI**: Only implement what's currently needed
- **DRY**: Reuse code through shared types and utilities
- **SOLID**: Follow single responsibility and interface segregation

## 📝 Code Style

- **Frontend (TypeScript/React)**: Use Functional Components, Tailwind CSS, Shadcn UI
- **Backend (Python)**: Follow PEP8, use FastAPI and Pydantic v2
- **IPC Pattern**: All system-level file access through Electron Main via `ipcMain`/`ipcRenderer`

## 📚 Documentation

- [Theme Design Guide](./docs/THEME_DESIGN.md)
- [Theme Quick Reference](./docs/THEME_QUICK_REF.md)
- [Development Guide](./CLAUDE.md)

## 🛠️ Tech Stack

### Frontend
- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS
- Shadcn UI

### Desktop
- Electron
- TypeScript

### Backend
- Python
- FastAPI
- LanceDB
- LangChain / LlamaIndex
- Ollama

## 📄 License

MIT
