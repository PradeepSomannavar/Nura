import { useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";
import { ArrowLeft, ArrowUp } from "@phosphor-icons/react";
import { createSession, fetchMessages, streamChat } from "../lib/api";
import { getSessionId, setSessionId } from "../lib/session";
import type { HistoryMessage } from "../lib/types";
import { Message, type DisplayMessage } from "./Message";

interface ChatProps {
  onHome: () => void;
}

const QUICK_PROMPTS = [
  {
    title: "Type 2 Diabetes Guidelines",
    desc: "First-line therapy & ASCVD risk add-ons",
    prompt: "What are the first-line guidelines for treating Type 2 Diabetes?",
  },
  {
    title: "Metformin & CKD Safety",
    desc: "eGFR threshold limits & dosing adjustments",
    prompt: "When is Metformin contraindicated in Chronic Kidney Disease (CKD)?",
  },
  {
    title: "Pediatric Amoxicillin Dosage",
    desc: "Weight-based mg/kg protocol",
    prompt: "What is the pediatric dosage calculation for Amoxicillin in acute otitis media?",
  },
  {
    title: "SSRI & NSAID Interactions",
    desc: "Gastrointestinal bleeding risk factors",
    prompt: "What are common drug interactions between SSRIs and NSAIDs?",
  },
];

let keyCounter = 1;
const nextKey = () => keyCounter++;

export function Chat({ onHome }: ChatProps) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [sessionId, setSid] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);

  const mainRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const scrollToBottom = useCallback(() => {
    const el = mainRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, []);

  useEffect(() => {
    const current = getSessionId();
    if (current !== null) {
      setSid(current);
      fetchMessages(current)
        .then((rows) =>
          setMessages(
            rows.map((m) => ({
              key: nextKey(),
              role: m.role,
              content: m.content,
              sources: m.sources,
            })),
          ),
        )
        .catch(() => {
          createSession().then((id) => {
            setSid(id);
            setSessionId(id);
          });
        });
    } else {
      createSession().then((id) => {
        setSid(id);
        setSessionId(id);
      });
    }
    return () => abortRef.current?.abort();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 144) + "px";
  };

  const send = useCallback(
    (raw: string) => {
      const text = raw.trim();
      if (!text || streaming) return;

      const userMessage: DisplayMessage = {
        key: nextKey(),
        role: "user",
        content: text,
      };
      const assistantMessage: DisplayMessage = {
        key: nextKey(),
        role: "assistant",
        content: "",
        pending: true,
      };
      const next = [...messages, userMessage, assistantMessage];
      setMessages(next);
      setInput("");
      if (textareaRef.current) textareaRef.current.style.height = "auto";
      setStreaming(true);

      const history: HistoryMessage[] = next
        .filter((m) => !m.pending)
        .map((m) => ({ role: m.role, content: m.content }));

      const controller = new AbortController();
      abortRef.current = controller;

      const patchLast = (patch: Partial<DisplayMessage>) =>
        setMessages((prev) => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last && last.role === "assistant" && last.pending) {
            copy[copy.length - 1] = { ...last, ...patch };
          }
          return copy;
        });

      const appendToken = (chunk: string) =>
        setMessages((prev) => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          if (last && last.role === "assistant" && last.pending) {
            copy[copy.length - 1] = { ...last, content: last.content + chunk };
          }
          return copy;
        });

      streamChat({
        message: text,
        history,
        sessionId,
        signal: controller.signal,
        onEvent: (event) => {
          switch (event.type) {
            case "token":
              appendToken(event.content ?? "");
              break;
            case "sources":
              patchLast({ sources: event.sources ?? [] });
              break;
            case "done":
              patchLast({ pending: false });
              setStreaming(false);
              break;
            case "error":
              patchLast({
                pending: false,
                content: event.content || "Something went wrong. Please try again.",
              });
              setStreaming(false);
              break;
          }
        },
      })
        .catch((err) => {
          if (err instanceof DOMException && err.name === "AbortError") return;
          patchLast({
            pending: false,
            content: "Connection issue. Please try again.",
          });
          setStreaming(false);
        })
        .finally(() => setStreaming(false));
    },
    [messages, streaming, sessionId],
  );

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    send(input);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  return (
    <div className="chat">
      <button
        type="button"
        className={`chat__back${messages.length > 0 ? " visible" : ""}`}
        onClick={onHome}
        title="Back to Home"
      >
        <ArrowLeft size={12} weight="bold" />
        <span>Home</span>
      </button>

      <div className="chat__main" ref={mainRef}>
        {messages.length === 0 ? (
          <div className="starter">
            <div>
              <h1 className="starter__title">Hi, Nura here.</h1>
              <p className="starter__sub">
                Clinical guide for symptoms, treatments, and care. Ask a question to begin.
              </p>
            </div>

            <div className="quick">
              {QUICK_PROMPTS.map((q) => (
                <button
                  key={q.title}
                  type="button"
                  className="quick__btn"
                  onClick={() => send(q.prompt)}
                  disabled={streaming}
                >
                  <p className="quick__title">{q.title}</p>
                  <p className="quick__desc">{q.desc}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((m) => (
              <Message key={m.key} message={m} />
            ))}
          </div>
        )}
      </div>

      <div className="composer">
        <div className="composer__inner">
          <form className="composer__form" onSubmit={handleSubmit}>
            <textarea
              ref={textareaRef}
              rows={1}
              className="composer__input"
              value={input}
              placeholder="Ask Nura about symptoms, treatments, or care..."
              onChange={(e) => {
                setInput(e.target.value);
                autoResize();
              }}
              onKeyDown={handleKeyDown}
            />
            <button
              type="submit"
              className="composer__send"
              disabled={streaming || input.trim() === ""}
              aria-label="Send"
            >
              <ArrowUp size={14} weight="bold" />
            </button>
          </form>
          <p className="composer__hint">
            Nura provides clinical literature references. Not a substitute for professional medical care.
          </p>
        </div>
      </div>
    </div>
  );
}