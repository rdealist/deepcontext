#!/bin/bash

# Electron 开发启动脚本

echo "[dev-electron] Starting Electron..."

# 启动前先清理旧的 Python 进程（防止上次异常退出残留）
pkill -9 -f "python.*engine/main.py" 2>/dev/null || true

# 设置退出陷阱（处理 Ctrl+C 等正常退出）
trap 'echo "[dev-electron] Cleaning up..."; pkill -9 -f "python.*engine/main.py" 2>/dev/null || true' EXIT

# 启动 Electron
npm run build:electron && electron "."

echo "[dev-electron] Exited"
