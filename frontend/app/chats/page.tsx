"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { fetchWithAuth } from "@/lib/fetchWithAuth";
import "./chats.css";

interface Chat {
  id: number;
  title: string;
  username?: string;
  type: string;
}

export default function ChatsPage() {
  const [adminUser, setAdminUser] = useState<{ username: string } | null>(null);
  const [telegramUser, setTelegramUser] = useState<{ username?: string; phone?: string } | null>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [error, setError] = useState("");
  const [telegramNotConnected, setTelegramNotConnected] = useState(false);
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const chatsLoadedRef = useRef(false);
  const profileLoadedRef = useRef(false);

  const getToken = () =>
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const loadAdminInfo = async () => {
    try {
      const data = await fetchWithAuth(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`);
      setAdminUser(data);
    } catch (e) {
      console.error("Failed to load admin info", e);
    }
  };

  const loadTelegramInfo = async () => {
    try {
      const data = await fetchWithAuth(`${process.env.NEXT_PUBLIC_API_URL}/me`);
      setTelegramUser(data);
    } catch (e: any) {
      if (e.detail?.toLowerCase().includes("telegram")) {
        setTelegramNotConnected(true);
      } else {
        console.error("Failed to load Telegram info", e);
      }
    }
  };

  const loadChats = async () => {
    try {
      const data = await fetchWithAuth(`${process.env.NEXT_PUBLIC_API_URL}/chats`);
      setChats(data);
    } catch (err: any) {
      if (err.detail?.toLowerCase().includes("telegram")) {
        setTelegramNotConnected(true);
      } else if (err.detail?.toLowerCase().includes("token")) {
        setError("Token is invalid. Update token");
      } else {
        setError(err.detail || "Failed to load chats");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!profileLoadedRef.current) {
      loadAdminInfo();
      profileLoadedRef.current = true;
    }

    if (!telegramNotConnected && !chatsLoadedRef.current) {
      loadTelegramInfo();
      loadChats();
      chatsLoadedRef.current = true;
    }
  }, [telegramNotConnected]);

  const handleAdminLogout = async () => {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    localStorage.removeItem("access_token");
    router.push("/login");
  };

  const handleConnectTelegram = async () => {
    const token = getToken();
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/connect`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    alert(data.message);
  };

  const handleSubmitCode = async () => {
    const token = getToken();
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login?code=${code}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    alert(data.message);
    setTelegramNotConnected(false);
    await loadTelegramInfo();
    await loadChats();
  };

  const handleTelegramLogout = async () => {
    const token = getToken();
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    alert(data.message);
    setTelegramNotConnected(true);
    setChats([]);
  };

  return (
    <div className="chats-page">
      <div className="chats-header">
        <h1 className="chats-title">Система перегляду повідомлень соціальних мереж</h1>
        <div style={{ display: "flex", gap: "10px" }}>
          {!loading && !telegramNotConnected && (
            <button onClick={handleTelegramLogout} className="chats-logout">
              Disconnect Telegram
            </button>
          )}
          <button onClick={handleAdminLogout} className="chats-logout">
            Sign out
          </button>
        </div>
        <div style={{ marginLeft: "auto", textAlign: "right" }}>
          {adminUser && (
            <p style={{ fontSize: "14px", margin: "0 0 8px 0" }}>
              Admin: <strong>{adminUser.username}</strong>
            </p>
          )}
          {telegramUser && (
            <p style={{ fontSize: "14px", margin: "0 0 8px 0" }}>
              Telegram: <strong>{telegramUser.username || telegramUser.phone}</strong>
            </p>
          )}
        </div>
      </div>

      {telegramNotConnected ? (
        <div className="chats-telegram-connect">
          <p>Telegram is not connected</p>
          <button onClick={handleConnectTelegram}>Send the code to Telegram</button>
          <div className="chats-code-submit">
            <input
              type="text"
              placeholder="Enter the code from Telegram"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
            <button onClick={handleSubmitCode}>Confirm the code</button>
          </div>
        </div>
      ) : error ? (
        <div className="chats-error-block">
          <p className="chats-error">{error}</p>
        </div>
      ) : (
        <ul className="chats-list">
          {chats.map((chat) => (
            <li
              key={chat.id}
              className="chat-item"
              onClick={() =>
                router.push(`/messages?chat_id=${chat.id}&username=${chat.username || ""}&title=${encodeURIComponent(chat.title)}`)
              }
            >
              <p className="chat-title">{chat.title}</p>
              <p className="chat-subtitle">
                {chat.username || `#${chat.id}`} • {chat.type}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
