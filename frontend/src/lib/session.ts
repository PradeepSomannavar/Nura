const KEY = "nura.sessionId";

export function getSessionId(): number | null {
  const raw = localStorage.getItem(KEY);
  if (!raw) return null;
  const id = Number(raw);
  return Number.isFinite(id) && id > 0 ? id : null;
}

export function setSessionId(id: number): void {
  localStorage.setItem(KEY, String(id));
}