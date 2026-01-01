import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";
import path from "path";
import { startPython, killPython } from "./py-process";
import http from "http";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

let mainWindow: BrowserWindow | null = null;
let healthCheckInterval: NodeJS.Timeout | null = null;

// Global error handlers to prevent uncaught exceptions from crashing the app
process.on("uncaughtException", (error) => {
  // Ignore EPIPE errors during shutdown
  if (
    error.message.includes("EPIPE") ||
    error.message.includes("write after end")
  ) {
    return;
  }
  safeLog("error", `Uncaught Exception: ${error.message}`);
  console.error(error.stack);
});

process.on("unhandledRejection", (reason, promise) => {
  safeLog("error", `Unhandled Rejection at: ${promise}, reason: ${reason}`);
});

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const isDev = !app.isPackaged;

  if (isDev) {
    mainWindow.loadURL("http://localhost:3000");
    mainWindow.webContents.openDevTools();

    // 开发模式下监控 Next.js 健康状态
    startHealthCheck();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../app/out/index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function startHealthCheck(): void {
  healthCheckInterval = setInterval(() => {
    // Skip health check if window is closed
    if (!mainWindow) {
      if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
        healthCheckInterval = null;
      }
      return;
    }

    const req = http.get("http://localhost:3000", (res) => {
      // Consume response data to properly close the connection
      res.on("data", () => {});
      res.on("end", () => {
        if (res.statusCode !== 200) {
          safeLog("error", "[Electron] Next.js unhealthy, quitting...");
          shutdown();
        }
      });
    });

    req.on("error", (err) => {
      // Ignore EPIPE and connection errors during shutdown
      if (
        err.message.includes("EPIPE") ||
        err.message.includes("ECONNREFUSED")
      ) {
        return;
      }
      safeLog("error", "[Electron] Next.js not reachable, quitting...");
      shutdown();
    });

    // Prevent hanging requests
    req.setTimeout(3000, () => {
      req.destroy();
    });
  }, 5000); // 每5秒检查一次
}

function safeLog(level: "info" | "error" | "warn", message: string): void {
  try {
    if (level === "error") {
      console.error(message);
    } else if (level === "warn") {
      console.warn(message);
    } else {
      console.log(message);
    }
  } catch (err) {
    // Ignore write errors during shutdown
  }
}

function shutdown(): void {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
    healthCheckInterval = null;
  }
  killPython();
  app.quit();
}

app.whenReady().then(() => {
  startPython();
  createWindow();

  // IPC: python:status - 检查 Python 后端状态
  ipcMain.handle("python:status", async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/hello");
      return { running: res.ok };
    } catch {
      return { running: false };
    }
  });

  // IPC: select-folder - 打开文件夹选择对话框
  ipcMain.handle("select-folder", async () => {
    if (!mainWindow) return { canceled: true, path: null };

    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory"],
      title: "选择文档库文件夹",
    });

    if (result.canceled || result.filePaths.length === 0) {
      return { canceled: true, path: null };
    }

    return { canceled: false, path: result.filePaths[0] };
  });

  // IPC: open-file - 使用系统默认应用打开文件
  ipcMain.handle("open-file", async (_, filePath: string) => {
    try {
      const result = await shell.openPath(filePath);
      if (result) {
        return { success: false, error: result };
      }
      return { success: true };
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";
      return { success: false, error: errorMsg };
    }
  });

  // IPC: open-file-at-line - 在外部编辑器中打开文件并定位到指定行
  ipcMain.handle(
    "open-file-at-line",
    async (_, filePath: string, line: number) => {
      try {
        // Try VS Code first with --goto flag for precise line navigation
        try {
          await execAsync(`code --goto "${filePath}:${line}"`);
          return { success: true, editor: "vscode" };
        } catch {
          // VS Code not available, fall back to system default
          const result = await shell.openPath(path.dirname(filePath));
          if (result) {
            return { success: false, error: result };
          }
          return { success: true, editor: "default" };
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        return { success: false, error: errorMsg };
      }
    }
  );

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("will-quit", () => {
  killPython();
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
  }
});

process.on("SIGTERM", () => {
  safeLog("info", "[Electron] Received SIGTERM, shutting down...");
  shutdown();
});

process.on("SIGINT", () => {
  safeLog("info", "[Electron] Received SIGINT, shutting down...");
  shutdown();
});
