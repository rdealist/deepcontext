export interface ElectronAPI {
  getPythonStatus: () => Promise<{ running: boolean }>;
  selectFolder: () => Promise<{ canceled: boolean; path: string | null }>;
  openFile: (
    filePath: string,
  ) => Promise<{ success: boolean; error?: string }>;
  openFileAtLine: (
    filePath: string,
    line: number,
  ) => Promise<{ success: boolean; error?: string; editor?: "vscode" | "default" }>;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
