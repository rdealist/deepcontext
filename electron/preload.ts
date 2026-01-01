import { contextBridge, ipcRenderer } from "electron";

interface SelectFolderResult {
  canceled: boolean;
  path: string | null;
}

interface OpenFileResult {
  success: boolean;
  error?: string;
}

contextBridge.exposeInMainWorld("electronAPI", {
  getPythonStatus: () => ipcRenderer.invoke("python:status"),
  selectFolder: (): Promise<SelectFolderResult> =>
    ipcRenderer.invoke("select-folder"),
  openFile: (filePath: string): Promise<OpenFileResult> =>
    ipcRenderer.invoke("open-file", filePath),
});

declare global {
  interface Window {
    electronAPI: {
      getPythonStatus: () => Promise<{ running: boolean }>;
      selectFolder: () => Promise<SelectFolderResult>;
      openFile: (filePath: string) => Promise<OpenFileResult>;
    };
  }
}
