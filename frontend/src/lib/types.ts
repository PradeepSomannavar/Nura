export interface SourceDoc {
  content: string;
  metadata: Record<string, unknown>;
}

export interface ChatEvent {
  type: "token" | "sources" | "done" | "error" | "meta";
  content?: string;
  provider?: string | null;
  sources?: SourceDoc[];
}

export interface HistoryMessage {
  role: "user" | "assistant";
  content: string;
}

export interface StoredMessage extends HistoryMessage {
  id: number;
  sources: SourceDoc[];
}