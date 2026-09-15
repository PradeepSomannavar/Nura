const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ??
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

const BASE = `${API_BASE}/api`;

export async function createSession(): Promise<number> {
  const res = await fetch(`${BASE}/sessions`, { method: "POST" });
  if (!res.ok) throw new Error(`Failed to create session (${res.status})`);
  const body = (await res.json()) as { session_id: number };
  return body.session_id;
}

export async function fetchMessages(sessionId: number): Promise<import("./types").StoredMessage[]> {
  const res = await fetch(`${BASE}/sessions/${sessionId}/messages`);
  if (!res.ok) throw new Error(`Failed to load messages (${res.status})`);
  return (await res.json()) as import("./types").StoredMessage[];
}

export interface StreamRequest {
  message: string;
  history: import("./types").HistoryMessage[];
  sessionId: number | null;
  signal?: AbortSignal;
  onEvent: (event: import("./types").ChatEvent) => void;
}

export async function streamChat(req: StreamRequest): Promise<void> {
  const res = await fetch(`${BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: req.sessionId,
      message: req.message,
      history: req.history,
    }),
    signal: req.signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const dispatch = (block: string) => {
    const lines = block.split(/\r?\n/);
    let eventType = "message";
    const data: string[] = [];
    for (const line of lines) {
      if (line.startsWith("event:")) eventType = line.slice(6).trim();
      else if (line.startsWith("data:")) data.push(line.slice(5).trim());
    }
    if (data.length === 0) return;
    const parsed = JSON.parse(data.join("\n")) as import("./types").ChatEvent;
    req.onEvent({ ...parsed, type: (eventType || parsed.type) as import("./types").ChatEvent["type"] });
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";
    for (const block of blocks) {
      if (block.trim()) dispatch(block);
    }
  }
  if (buffer.trim()) dispatch(buffer);
}