export interface SourceReference {
  file_name: string;
  file_path: string;
  heading?: string;
  score?: number;
  start_line?: number;
  end_line?: number;
}

export interface SessionInfo {
  id: string;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
  isStreaming?: boolean;
  created_at?: string;
}
