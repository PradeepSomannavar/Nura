import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { SourceDoc } from "../lib/types";

export interface DisplayMessage {
  key: number;
  role: "user" | "assistant";
  content: string;
  sources?: SourceDoc[];
  pending?: boolean;
}

interface MessageProps {
  message: DisplayMessage;
}

export function Message({ message }: MessageProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  if (message.role === "user") {
    return (
      <div className="msg--user">
        <div className="msg__text">{message.content}</div>
      </div>
    );
  }

  return (
    <div className="msg--assistant" ref={rootRef}>
      <div className={`msg__text${message.pending ? " typing-cursor" : ""}`}>
        {message.content ? (
          <div className="md">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        ) : (
          "\u00A0"
        )}
      </div>

      {message.sources && message.sources.length > 0 && (
        <div className="srcs">
          <button
            type="button"
            className="srcs__pill"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
          >
            <span>Sources</span>
          </button>

          <div className={`srcs__popover${open ? " open" : ""}`} role="group">
            <div className="srcs__head">
              <span>Referenced Sources ({message.sources.length})</span>
              <button
                type="button"
                className="srcs__close"
                onClick={() => setOpen(false)}
                aria-label="Close sources"
              >
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <path
                    d="M1 1l8 8M9 1L1 9"
                    stroke="currentColor"
                    strokeWidth="1.4"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>
            <div className="srcs__list">
              {message.sources.map((src, i) => (
                <div className="srcs__item" key={i}>
                  <strong>[{i + 1}] {String(src.metadata?.source ?? "Source")}</strong>
                  <small>{truncate(src.content, 160)}</small>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function truncate(text: string, max: number): string {
  const clean = text.replace(/\s+/g, " ").trim();
  return clean.length > max ? `${clean.slice(0, max)}…` : clean;
}