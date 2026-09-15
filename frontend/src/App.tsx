import { useState } from "react";
import { Chat } from "./components/Chat";
import { Landing } from "./components/Landing";

export default function App() {
  const [page, setPage] = useState<"landing" | "chat">("landing");

  return page === "chat" ? (
    <Chat onHome={() => setPage("landing")} />
  ) : (
    <Landing onOpenChat={() => setPage("chat")} />
  );
}