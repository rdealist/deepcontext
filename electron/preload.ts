import { contextBridge, ipcRenderer } from "electron";

interface SelectFolderResult {
  canceled: boolean;
  path: string | null;
}

interface OpenFileResult {
  success: boolean;
  error?: string;
}

interface OpenFileAtLineResult {
  success: boolean;
  error?: string;
  editor?: "vscode" | "default";
}

contextBridge.exposeInMainWorld("electronAPI", {
  getPythonStatus: () => ipcRenderer.invoke("python:status"),
  selectFolder: (): Promise<SelectFolderResult> =>
    ipcRenderer.invoke("select-folder"),
  openFile: (filePath: string): Promise<OpenFileResult> =>
    ipcRenderer.invoke("open-file", filePath),
  openFileAtLine: (
    filePath: string,
    line: number
  ): Promise<OpenFileAtLineResult> =>
    ipcRenderer.invoke("open-file-at-line", filePath, line),
});

declare global {
  interface Window {
    electronAPI: {
      getPythonStatus: () => Promise<{ running: boolean }>;
      selectFolder: () => Promise<SelectFolderResult>;
      openFile: (filePath: string) => Promise<OpenFileResult>;
      openFileAtLine: (
        filePath: string,
        line: number
      ) => Promise<OpenFileAtLineResult>;
    };
  }
}
