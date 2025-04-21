"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import "./messages.css";

interface Message {
  id: number;
  text: string;
  date: string;
  from_id: number | null;
}

export default function MessagesPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState("");
  const router = useRouter();
  const searchParams = useSearchParams();

  const chatId = searchParams.get("chat_id");
  const username = searchParams.get("username");
  const chatTitle = decodeURIComponent(searchParams.get("title") || "");

  const isFetchingRef = useRef(false);

  const fetchMessages = async () => {
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;
  
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
  
    const query = username
      ? `username=${encodeURIComponent(username)}`
      : `chat_id=${chatId}`;
  
    try {
      const res = await fetch(`http://localhost:8000/messages?${query}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw await res.json();
      const data = await res.json();
      setMessages(data);
    } catch (err: any) {
      setError(err.detail || "Failed to load messages");
    } finally {
      isFetchingRef.current = false;
    }
  };

  useEffect(() => {
    if (!chatId && !username) {
      router.push("/chats");
      return;
    }
    fetchMessages();
  }, []);

  return (
    <div className="messages-page">
      <div className="messages-header">
        <h1 className="messages-title">
          Message {chatTitle && `• ${chatTitle}`}
        </h1>
        <div className="messages-controls">
          <button onClick={fetchMessages}>Refresh</button>
          <button onClick={() => router.push("/chats")}>Back</button>
        </div>
      </div>

      {error && <p className="messages-error">{error}</p>}

      <ul className="messages-list">
        {messages.map((msg) => (
          <li key={msg.id} className="message-item">
            <p className="message-from">{msg.from_id}</p>
            <p>{msg.text || <i className="message-empty">[without text]</i>}</p>
            <p className="message-date">{msg.date}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
