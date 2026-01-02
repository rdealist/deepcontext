# CLAUDE.md - Development Guide

## Build & Run Commands
- Install All: `npm install && cd engine && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Run Electron (Dev): `npm run dev` (Need to configure package.json)
- Run Backend (Dev): `cd engine && uvicorn main:app --reload`
- Type Check: `npm run type-check`

## Project Structure (Monorepo Architecture)

### Directory Layout
```
/deepcontext
├── /app                    # Next.js Frontend (Independent Project)
│   ├── /src               # Source Code (IMPORTANT: All source files in src/)
│   │   ├── /app          # Next.js App Router
│   │   ├── /components   # React Components
│   │   └── /lib          # Utility Functions
│   ├── /public           # Static Assets
│   └── tsconfig.json     # TypeScript Config (with path aliases)
├── /electron              # Electron Main Process
├── /engine                # Python RAG Backend
├── /shared                # Cross-Project Shared Code
│   └── /types            # Shared TypeScript Type Definitions
└── /docs                  # Project Documentation
```

### Path Alias Configuration

**CRITICAL:** The project uses TypeScript path aliases for clean imports:

- `@/*` → `app/src/*` (for internal app imports)
- `@shared/*` → `shared/*` (for shared types across projects)

**tsconfig.json configuration:**
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@shared/*": ["../shared/*"]
    }
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "../shared/**/*.ts"
  ]
}
```

## Code Style & Implementation Details

### Backend (Python)
- Use FastAPI, Pydantic v2, and LanceDB
- Follow PEP8
- **Error Handling**: Always wrap Python child process spawns in try-catch and log stderr for debugging

### Frontend (TypeScript/React)
- Use Functional Components
- Tailwind CSS for styling
- Shadcn UI component library
- **IMPORTANT:** All source files must be in `app/src/`, not `app/` root

### IPC Pattern
- All system-level file access must go through Electron Main (`electron/main.ts`) via `ipcMain`/`ipcRenderer`
- Electron IPC interface definitions **must** be defined in `shared/types/electron-api.ts`
- Import Electron types via `@shared/types` to ensure type safety

### RAG Logic
- Use LangChain or LlamaIndex logic simplified for local use

## Type Sharing Rules (CRITICAL)

### Rule 1: All Shared Types in /shared/types/

**Any type used by both `/app` and `/electron` MUST be defined in `/shared/types/`**

```typescript
// ✅ CORRECT: Define in shared/types/chat.ts
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

// ✅ CORRECT: Import from shared
import { ChatMessage } from "@shared/types";
```

```typescript
// ❌ WRONG: Duplicating type definitions
// In app/src/types/chat.ts
interface ChatMessage { ... }

// In electron/types.ts
interface ChatMessage { ... }  // Duplication! Violates DRY!
```

### Rule 2: Use @shared/* Path Alias

**Always use `@shared/*` when importing shared types:**

```typescript
// ✅ CORRECT
import { ChatMessage, ElectronAPI } from "@shared/types";

// ❌ WRONG: Relative paths are fragile
import { ChatMessage } from "../../shared/types/chat";
```

### Rule 3: Electron API Interface Contract

**Electron IPC interfaces must be defined in `shared/types/electron-api.ts`:**

```typescript
// shared/types/electron-api.ts
export interface ElectronAPI {
  selectFolder: () => Promise<{ canceled: boolean; path: string | null }>;
  openFile: (filePath: string) => Promise<{ success: boolean }>;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
```

## Development Workflow

### Adding New Features

1. **Types First**: Define shared types in `/shared/types/` if needed
2. **Backend**: Implement API in `/engine`
3. **Frontend**: Build UI in `/app/src/components`
4. **IPC (if needed)**: Add Electron IPC handlers in `/electron/main.ts`

### File Organization Best Practices

**DO:**
- ✅ Put all app source code in `app/src/`
- ✅ Put shared types in `shared/types/`
- ✅ Put documentation in `docs/`
- ✅ Use path aliases (`@/*` and `@shared/*`)

**DON'T:**
- ❌ Put source files directly in `app/` root
- ❌ Duplicate type definitions across projects
- ❌ Use relative paths for shared types
- ❌ Mix documentation with source code

## Architecture Principles

### KISS (Keep It Simple, Stupid)
- Prefer simple, straightforward solutions
- Avoid unnecessary complexity
- Clear is better than clever

### YAGNI (You Aren't Gonna Need It)
- Only implement currently needed features
- Don't build for hypothetical future use cases
- Remove unused code and dependencies

### DRY (Don't Repeat Yourself)
- Share types via `/shared/types/`
- Extract reusable utilities to `/app/src/lib/`
- Use path aliases to avoid duplication

### SOLID Principles
- **S**: Single Responsibility - Each component does one thing well
- **O**: Open/Closed - Extend via composition, not modification
- **L**: Liskov Substitution - Subtypes are substitutable
- **I**: Interface Segregation - Small, focused interfaces (see `shared/types/`)
- **D**: Dependency Inversion - Depend on abstractions (types), not implementations

## Common Pitfalls & Solutions

### ❌ Problem: Import errors after restructuring
```typescript
// Error: Cannot find module '@/types/chat'
import { ChatMessage } from "@/types/chat";
```

### ✅ Solution: Use correct path alias
```typescript
import { ChatMessage } from "@shared/types";
```

---

### ❌ Problem: Electron types not found in frontend
```typescript
// Missing global Window.electronAPI types
window.electronAPI?.selectFolder();
```

### ✅ Solution: Import electron-api types
```typescript
import "@shared/types/electron-api";

// Now electronAPI is properly typed
window.electronAPI?.selectFolder();
```

---

### ❌ Problem: Type duplication across projects
Maintaining same type in multiple files leads to inconsistencies.

### ✅ Solution: Single source of truth in /shared/types/
Define once, import everywhere using `@shared/*`.

