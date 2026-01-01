import { spawn, ChildProcess, execSync } from "child_process";
import path from "path";
import fs from "fs";
import { app } from "electron";

type ProcStatus = "stopped" | "starting" | "running" | "error";

let pyProc: ChildProcess | null = null;
let procStatus: ProcStatus = "stopped";

const LOG_PREFIX = "[PythonProcess]";

function log(level: "info" | "error" | "warn", msg: string): void {
  try {
    const timestamp = new Date().toISOString().split("T")[1].slice(0, -1);
    console[level](`${LOG_PREFIX} [${timestamp}] ${msg}`);
  } catch (err) {
    // Ignore write errors (EPIPE) during shutdown
  }
}

function getBasePath(): string {
  if (app.isPackaged) {
    return process.resourcesPath;
  }

  const devPath = path.join(process.cwd(), "engine");
  if (fs.existsSync(devPath)) {
    return process.cwd();
  }

  return app.getAppPath();
}

function getPythonPath(): string {
  const base = getBasePath();
  const venvPaths =
    process.platform === "win32"
      ? [
          path.join(base, "engine", "venv", "Scripts", "python.exe"),
          path.join(base, "engine", ".venv", "Scripts", "python.exe"),
        ]
      : [
          path.join(base, "engine", "venv", "bin", "python"),
          path.join(base, "engine", ".venv", "bin", "python"),
        ];

  for (const venv of venvPaths) {
    if (fs.existsSync(venv)) {
      log("info", `Using venv Python: ${venv}`);
      return venv;
    }
  }

  const fallback = process.platform === "win32" ? "python" : "python3";
  log("warn", `No venv found, using system Python: ${fallback}`);
  return fallback;
}

function getScriptPath(): string {
  const base = getBasePath();
  const scriptPath = path.join(base, "engine", "main.py");

  log("info", `Script path resolved: ${scriptPath}`);
  return scriptPath;
}

export function startPython(): void {
  if (pyProc) {
    log("warn", "Python process already running");
    return;
  }

  const py = getPythonPath();
  const script = getScriptPath();

  if (!fs.existsSync(script)) {
    log("error", `Script not found: ${script}`);
    procStatus = "error";
    return;
  }

  procStatus = "starting";
  log("info", `Starting: ${py} ${script}`);

  try {
    pyProc = spawn(py, [script], {
      cwd: path.dirname(script),
      detached: true,
      env: {
        ...process.env,
        PYTHONUNBUFFERED: "1",
        NODE_ENV: app.isPackaged ? "production" : "development",
        LLM_MODEL: process.env.LLM_MODEL || "qwen3:0.6b",
      },
      stdio: ["ignore", "pipe", "pipe"],
    });

    pyProc.stdout?.on("data", (data) => {
      try {
        const output = data.toString().trim();
        if (output) {
          console.log(`${LOG_PREFIX} [stdout]`, output);
        }
      } catch (err) {
        // Ignore write errors during shutdown
      }
    });

    pyProc.stderr?.on("data", (data) => {
      try {
        const output = data.toString().trim();
        if (output) {
          console.error(`${LOG_PREFIX} [stderr]`, output);
        }
      } catch (err) {
        // Ignore write errors during shutdown
      }
    });

    pyProc.on("error", (err) => {
      log("error", `Spawn error: ${err.message}`);
      procStatus = "error";
      pyProc = null;
    });

    pyProc.on("spawn", () => {
      log("info", `Process spawned successfully (PID: ${pyProc?.pid})`);
      procStatus = "running";
    });

    pyProc.on("close", (code, signal) => {
      log(
        "info",
        `Process closed (code: ${code}, signal: ${signal || "none"})`,
      );
      procStatus = "stopped";
      pyProc = null;
    });
  } catch (err) {
    log(
      "error",
      `Failed to spawn: ${err instanceof Error ? err.message : String(err)}`,
    );
    procStatus = "error";
    pyProc = null;
  }
}

export function killPython(): void {
  if (!pyProc) {
    log("warn", "No Python process to kill");
    return;
  }

  const pid = pyProc.pid;
  log("info", `Killing Python process (PID: ${pid})`);

  try {
    if (process.platform === "win32") {
      execSync(`taskkill /pid ${pid} /T /F`, { stdio: "ignore" });
    } else {
      try {
        process.kill(-pid!, "SIGTERM");
      } catch {
        process.kill(pid!, "SIGTERM");
      }
    }

    pyProc.unref();
  } catch (err) {
    log("warn", `Kill failed, forcing SIGKILL: ${err}`);
    try {
      pyProc.kill("SIGKILL");
    } catch {
      log("warn", "Process already dead");
    }
  }

  pyProc = null;
  procStatus = "stopped";
}

export function getPythonStatus(): { running: boolean; pid?: number } {
  return {
    running: pyProc !== null && procStatus === "running",
    pid: pyProc?.pid,
  };
}

export function restartPython(): void {
  log("info", "Restarting Python process");
  killPython();
  setTimeout(() => startPython(), 500);
}

function cleanup(): void {
  if (!pyProc) return;

  const pid = pyProc.pid;
  log("info", `Cleaning up Python process (PID: ${pid})`);

  try {
    if (process.platform === "win32") {
      execSync(`taskkill /pid ${pid} /T /F`, {
        stdio: "ignore",
        timeout: 5000,
      });
    } else {
      try {
        process.kill(-pid!, "SIGTERM");
      } catch {
        process.kill(pid!, "SIGTERM");
      }
    }
  } catch (err) {
    log("warn", `Cleanup error: ${err}`);
    try {
      if (process.platform === "win32") {
        execSync(`taskkill /pid ${pid} /T /F`, { stdio: "ignore" });
      } else {
        process.kill(pid!, "SIGKILL");
      }
    } catch {}
  }

  pyProc = null;
  procStatus = "stopped";
}

let isCleaningUp = false;

function doCleanup(): void {
  if (isCleaningUp) return;
  isCleaningUp = true;
  cleanup();
}

process.on("exit", () => {
  if (pyProc && !isCleaningUp) {
    const pid = pyProc.pid;
    if (pid) {
      try {
        if (process.platform !== "win32") {
          process.kill(-pid, "SIGKILL");
        } else {
          execSync(`taskkill /pid ${pid} /T /F`, {
            stdio: "ignore",
            timeout: 2000,
          });
        }
      } catch {
        // Process already dead or cannot be killed
      }
    }
  }
});

process.on("SIGTERM", () => {
  doCleanup();
  process.exit(0);
});

process.on("SIGINT", () => {
  doCleanup();
  process.exit(0);
});
