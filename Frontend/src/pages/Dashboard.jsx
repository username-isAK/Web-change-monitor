import React, { useState, useEffect } from "react";
import UrlCard from "../components/UrlCard";
import axios from "axios";

export default function App() {
  const [urlsInput, setUrlsInput] = useState("");
  const [urls, setUrls] = useState([]);
  const [results, setResults] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  const userEmail = "user@example.com";
  const API_BASE = "/api";

  const fetchUrls = async () => {
    try {
      const res = await axios.get(`${API_BASE}/urls`, {
        headers: { "user-email": userEmail },
      });
      setUrls(res.data);
    } catch (err) {
      console.error("Failed to fetch URLs:", err);
    }
  };

  const fetchSummaries = async () => {
    try {
      const res = await axios.get(`${API_BASE}/summaries`, {
        headers: { "user-email": userEmail },
      });
      setResults(res.data ?? []);
    } catch (err) {
      console.error("Failed to fetch summaries:", err);
    }
  };

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(`${API_BASE}/notifications`, {
        headers: { "user-email": userEmail },
      });
      setNotifications(res.data);
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    }
  };

  const markNotificationRead = async (id) => {
    try {
      await axios.post(
        `${API_BASE}/notifications/${id}/read`,
        {},
        { headers: { "user-email": userEmail } }
      );
      fetchNotifications();
    } catch (err) {
      console.error("Failed to mark notification read:", err);
    }
  };

  const handleDelete = async (urlId) => {
    try {
      await axios.delete(`${API_BASE}/urls/${urlId}`, {
        headers: { "user-email": userEmail },
      });
      fetchUrls();
      fetchSummaries();
    } catch (err) {
      console.error("Failed to delete URL:", err);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const newUrls = urlsInput
        .split("\n")
        .map((u) => u.trim())
        .filter(Boolean);

      for (const url of newUrls) {
        try {
          await axios.post(
            `${API_BASE}/urls`,
            { url },
            { headers: { "user-email": userEmail } }
          );
        } catch (err) {
          console.error("Failed to register URL:", url, err);
        }
      }

      setUrlsInput("");
      fetchUrls();
      fetchSummaries();
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    fetchUrls();
    fetchSummaries();
    fetchNotifications();

    const interval = setInterval(() => {
      fetchUrls();
      fetchSummaries();
      fetchNotifications();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div style={{ padding: "20px" }}>
      <h2>Web Change Monitor</h2>

      <div style={{ marginBottom: "20px" }}>
        <h3>
          Notifications{" "}
          {unreadCount > 0 && (
            <span style={{ color: "red" }}>({unreadCount})</span>
          )}
        </h3>

        {notifications.length === 0 && <p>No notifications yet.</p>}

        {notifications.map((n) => (
          <div
            key={n.id}
            onClick={() => markNotificationRead(n.id)}
            style={{
              border: "1px solid #ddd",
              padding: "10px",
              marginBottom: "8px",
              backgroundColor: n.read ? "#f9f9f9" : "#fff3cd",
              cursor: "pointer",
            }}
          >
            <strong>{n.importance.toUpperCase()}</strong>
            <p>{n.message}</p>
            <small>{n.url}</small>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: "20px" }}>
        <h3>Register new URLs</h3>
        <textarea
          rows={5}
          value={urlsInput}
          onChange={(e) => setUrlsInput(e.target.value)}
          placeholder="Enter one URL per line"
          style={{ width: "100%", marginBottom: "12px" }}
        />
        <button onClick={handleSubmit}>Register URLs</button>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <h3>Registered URLs</h3>
        {urls.length === 0 && <p>No URLs registered yet.</p>}
        {urls.map((u) => (
          <div
            key={u.id}
            style={{
              border: "1px solid #ccc",
              padding: "12px",
              marginBottom: "12px",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>{u.url}</span>
            <button onClick={() => handleDelete(u.id)}>Delete</button>
          </div>
        ))}
      </div>

      <div>
        <h3>Summaries</h3>
        {loading && <p>Loading summaries...</p>}
        {results.map((r) => (
          <UrlCard
            key={r.url}
            url={r.url}
            summary={r.summary}
            importance={r.importance}
            reasoning={r.reasoning}
          />
        ))}
      </div>
    </div>
  );
}
