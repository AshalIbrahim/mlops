import React, { useEffect, useRef, useState } from "react";
import {
  Box,
  Paper,
  IconButton,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Typography,
  Avatar,
  Fab,
  CircularProgress,
} from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import CloseIcon from "@mui/icons-material/Close";

const STORAGE_KEY = "zameen_chat_history_v2";
const OPEN_KEY = "zameen_chat_open_v2";
const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function getBotReply(messages) {
  const payload = {
    messages: messages.map((m) => ({
      role: m.from === "user" ? "user" : "assistant",
      content: m.text,
    })),
  };

  try {
    const resp = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await resp.json();
    return data.response || "Sorry, I couldn't generate a response.";
  } catch (e) {
    return "Connection error: unable to reach assistant.";
  }
}

export default function Chatbot({ fullPage = false }) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [llmLoaded, setLlmLoaded] = useState(false);
  const [llmChecking, setLlmChecking] = useState(true);
  const listRef = useRef(null);
  const sendDebounceRef = useRef(false);

  // Load saved chat + open state
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setMessages(JSON.parse(raw));
    } catch (e) {}

    try {
      if (localStorage.getItem(OPEN_KEY) === "1") setOpen(true);
    } catch (e) {}
  }, []);

  // Check backend/LLM readiness (poll until healthy)
  useEffect(() => {
    let mounted = true;

    async function check() {
      try {
        const resp = await fetch(`${API}/health`);
        if (resp.ok) {
          const data = await resp.json();
          if (data && data.status === "ok") {
            if (!mounted) return;
            setLlmLoaded(true);
            setLlmChecking(false);
            return;
          }
        }
      } catch (e) {
        // ignore and retry
      }

      if (!mounted) return;
      setTimeout(check, 2000);
    }

    check();

    return () => {
      mounted = false;
    };
  }, []);

  // Persist messages
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {}
  }, [messages]);

  // Persist open state
  useEffect(() => {
    try {
      localStorage.setItem(OPEN_KEY, open ? "1" : "0");
    } catch (e) {}
  }, [open]);

  // Auto-scroll when messages change
  useEffect(() => {
    try {
      setTimeout(() => {
        if (listRef.current) {
          listRef.current.scrollTop = listRef.current.scrollHeight;
        }
      }, 60);
    } catch (e) {}
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    if (!llmLoaded) return;

    // Quick debounce to avoid double-click / double-enter
    if (sendDebounceRef.current) return;
    sendDebounceRef.current = true;
    setTimeout(() => (sendDebounceRef.current = false), 600);

    // prevent sending exact duplicate of last user message
    const lastUser = [...messages].reverse().find((m) => m.from === "user");
    if (lastUser && lastUser.text.trim() === input.trim()) {
      setInput("");
      return;
    }

    const userMsg = {
      from: "user",
      text: input.trim(),
      time: Date.now(),
    };

    setInput("");

    // set loading early to prevent fast additional sends
    setLoading(true);

    // Add user message instantly
    setMessages((prev) => {
      const updated = [...prev, userMsg];
      botReply(updated);
      return updated;
    });
  }

  async function botReply(history) {
    let botText = "";
    try {
      botText = await getBotReply(history);
    } catch (e) {
      botText = "Connection error: unable to reach assistant.";
    }

    const botMsg = {
      from: "bot",
      text: botText,
      time: Date.now(),
    };

    // Prevent adding duplicate assistant messages
    setMessages((prev) => {
      const lastAssistant = [...prev].reverse().find((m) => m.from === "bot");
      if (lastAssistant && lastAssistant.text && lastAssistant.text.trim() === botText.trim()) {
        return prev;
      }
      return [...prev, botMsg];
    });

    setLoading(false);
  }

  return (
    <Box className="chatbot-root">
      {/* Chat Panel (floating or full page) */}
      {open && !fullPage && (
        <Paper
          elevation={10}
          sx={{
            position: "fixed",
            bottom: "90px",
            right: "20px",
            width: "360px",
            height: "520px",
            display: "flex",
            flexDirection: "column",
            borderRadius: "16px",
            overflow: "hidden",
            zIndex: 10000,
          }}
        >
          <Box sx={{ px: 2, py: 1.5, display: "flex", alignItems: "center", bgcolor: "#1976d2" }}>
            <Typography sx={{ flex: 1, color: "white", fontWeight: 600 }}>Zameen Assistant</Typography>
            <IconButton size="small" onClick={() => setOpen(false)}>
              <CloseIcon sx={{ color: "white" }} />
            </IconButton>
          </Box>

          <List ref={listRef} sx={{ flex: 1, overflowY: "auto", px: 1.5, py: 1 }}>
            {messages.length === 0 && (
              <ListItem>
                <ListItemText primary="Ask me about prices, listings, or locations." secondary="(Powered by RAG + Gemini)" />
              </ListItem>
            )}

            {messages.map((m, idx) => (
              <ListItem key={idx} sx={{ display: "flex", flexDirection: m.from === "user" ? "row-reverse" : "row" }}>
                <Avatar sx={{ mx: 1 }}>{m.from === "user" ? "U" : "B"}</Avatar>
                <Box sx={{ maxWidth: "70%", bgcolor: m.from === "user" ? "#1976d2" : "#f0f0f0", color: m.from === "user" ? "white" : "black", px: 2, py: 1, borderRadius: 3 }}>
                  <Typography sx={{ fontSize: "0.9rem", whiteSpace: "pre-line" }}>{m.text}</Typography>
                </Box>
              </ListItem>
            ))}

            {loading && (
              <ListItem sx={{ display: "flex", alignItems: "center" }}>
                <Avatar sx={{ mx: 1 }}>B</Avatar>
                <Box sx={{ bgcolor: "#f0f0f0", px: 2, py: 1.2, borderRadius: 3, display: "flex", gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography sx={{ fontSize: "0.85rem" }}>Typing…</Typography>
                </Box>
              </ListItem>
            )}
          </List>

          <Box sx={{ display: "flex", gap: 1, p: 2, borderTop: "1px solid #eee" }}>
            <TextField size="small" fullWidth placeholder={llmLoaded ? "Type a message..." : "Loading assistant..."} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") sendMessage(); }} disabled={!llmLoaded} />
            <Button variant="contained" onClick={sendMessage} disabled={loading || !llmLoaded}>Send</Button>
          </Box>
        </Paper>
      )}

      {/* Full page mode */}
      {fullPage && (
        <Paper elevation={2} sx={{ width: "100%", minHeight: "70vh", display: "flex", flexDirection: "column", borderRadius: 2, overflow: "hidden" }}>
          <Box sx={{ px: 3, py: 2, display: "flex", alignItems: "center", bgcolor: "#1976d2" }}>
            <Typography sx={{ flex: 1, color: "white", fontWeight: 700, fontSize: "1.1rem" }}>Zameen Assistant</Typography>
            <Button color="inherit" onClick={() => { setMessages([]); try { localStorage.removeItem(STORAGE_KEY); } catch (e) {} }}>Clear</Button>
          </Box>

          <List ref={listRef} sx={{ flex: 1, overflowY: "auto", px: 2, py: 2 }}>
            {messages.length === 0 && (
              <ListItem>
                <ListItemText primary="Ask me about prices, listings, or locations." secondary="(Powered by RAG + Gemini)" />
              </ListItem>
            )}

            {messages.map((m, idx) => (
              <ListItem key={idx} sx={{ display: "flex", flexDirection: m.from === "user" ? "row-reverse" : "row" }}>
                <Avatar sx={{ mx: 1 }}>{m.from === "user" ? "U" : "B"}</Avatar>
                <Box sx={{ maxWidth: "80%", bgcolor: m.from === "user" ? "#1976d2" : "#f0f0f0", color: m.from === "user" ? "white" : "black", px: 2, py: 1, borderRadius: 3 }}>
                  <Typography sx={{ fontSize: "0.95rem", whiteSpace: "pre-line" }}>{m.text}</Typography>
                </Box>
              </ListItem>
            ))}

            {loading && (
              <ListItem sx={{ display: "flex", alignItems: "center" }}>
                <Avatar sx={{ mx: 1 }}>B</Avatar>
                <Box sx={{ bgcolor: "#f0f0f0", px: 2, py: 1.2, borderRadius: 3, display: "flex", gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography sx={{ fontSize: "0.95rem" }}>Typing…</Typography>
                </Box>
              </ListItem>
            )}
          </List>

          <Box sx={{ display: "flex", gap: 1, p: 2, borderTop: "1px solid #eee" }}>
            <TextField size="small" fullWidth placeholder={llmLoaded ? "Type a message..." : "Loading assistant..."} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") sendMessage(); }} disabled={!llmLoaded} />
            <Button variant="contained" onClick={sendMessage} disabled={loading || !llmLoaded}>Send</Button>
          </Box>

          {/* Loading overlay when assistant not ready */}
          {(!llmLoaded || llmChecking) && (
            <Box sx={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", bgcolor: "rgba(255,255,255,0.8)", zIndex: 1200 }}>
              <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 1 }}>
                <CircularProgress />
                <Typography>Loading assistant — please wait</Typography>
              </Box>
            </Box>
          )}
        </Paper>
      )}

      {/* Floating Action Button (only when not fullPage) */}
      {!fullPage && (
        <Fab color="primary" aria-label="chat" sx={{ position: "fixed", bottom: "20px", right: "20px", zIndex: 9999 }} onClick={() => setOpen((o) => !o)}>
          <ChatIcon />
        </Fab>
      )}
    </Box>
  );
}
